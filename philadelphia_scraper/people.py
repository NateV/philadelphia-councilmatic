from pupa.scrape import Scraper
from pupa.scrape import Person
from pupa.scrape import Organization
import lxml
import re
import logging
from datetime import date
from typing import List

logger = logging.getLogger(__name__)


def from_x(els: List["lxml.etree._Element"]) -> str:
    """
    Given an element, check its a singleton, and return its text, or ""
    """
    if len(els) != 1:
        return ""
    if isinstance(els[0], str): return els[0]
    return els[0].text

def strip_name_end(full_name):
    """
    Remove Jr, III, etc. from names, if present.
    """
    return re.sub(r"(, jr\.)|( i+ )", "", full_name, flags=re.I)

def pad_list(short, long, pad_with):
    """
    pad the short list with the pad_with until its as long as the long list
    """
    pad = [pad_with for _ in range(0, len(long)-len(short))]
    return short.extend(pad)

class PhiladelphiaPersonScraper(Scraper):

    """
    Philadelphia's Legistar instance seems to not have pages dedicated to the legislators. This seems to be fairly common. Other sites have the info about who is on city council.

    See the municpal_scrapers for boise, denver, rialto, for examples of other scrapers that find 
    legislators from other sites.
    """

    COUNCIL_ROOT = "https://phlcouncil.com/"
    COUNCIL_URL = "https://phlcouncil.com/council-members/"


    def scrape(self):


        council = Organization('Philadelphia City Council', classification="legislature")
        council.add_source(self.COUNCIL_ROOT)
        yield council

        # nb. the . at the start of each path makes the search relative.
        name_xpath = ".//h4[@class='x-face-title']/strong"
        # where the data is written on front and back of the card, pick one.
        council_title_xpath = ".//div[@class='x-face-outer front']//p[@class='x-face-text']/strong/big" # the 'Whip' or 'Leader' title, if any. 
        whip_title_xpath = ".//div[@class='x-face-outer front']//p[@class='x-face-text']/big/strong" # the 'Whip' or 'Leader' title, if any. 
        district_xpath = ".//div[@class='x-face-outer front']//p[@class='x-face-text']/strong" # district, not the 'Whip' or 
        link_xpath = ".//a[@class='x-face-button']/@href"
        pic_path = ".//div[@class='x-face-graphic']/img/@src"


        response = self.request(url=self.COUNCIL_URL, method="GET")

        html = response.text
        doc = lxml.html.fromstring(html)

 
        # philly's council site has members on 'cards'. We'll iterate over each card to make sure
        # we catch those that are vacant and keep all the data points together.
        cards_path = "//div[@class='x-card-inner']"
        cards = doc.xpath(cards_path)

        for card in cards:


            
            name = from_x(card.xpath(name_xpath))
            url = from_x(card.xpath(link_xpath))
            url = f"{self.COUNCIL_ROOT}{url}"
            district = from_x(card.xpath(district_xpath))
            whip_title = from_x(card.xpath(whip_title_xpath))
            council_title = from_x(card.xpath(council_title_xpath))
            pic = from_x(card.xpath(pic_path))
#       
#        # the urls of the council people
#        urls = [f"{self.COUNCIL_ROOT}{end_part}" for end_part in doc.xpath(link_xpath)]
#        names = [el.text for el in doc.xpath(name_xpath)]
#        districts = [el.text for el in doc.xpath(district_xpath)]
#        titles = [el.text for el in doc.xpath(title_xpath)]
#        pad_list(titles, names, "")
#
#        images = doc.xpath(pic_path)
#
            dist_pat = re.compile(r"^DISTRICT (?P<distnum>\d+)$")
#
#
#        for url, name, district, title, pic in zip(urls, names, districts, titles, images, strict=True):
#
            name_parts = strip_name_end(name).split(" ")
            last_name = name_parts[-1] 

            # Create legislator.
            person = Person(name, image=pic, district=district)
            # I don't know what to do for names that have family name as not last.
            person.family_name = last_name

            # Add membership on council.
            person.add_membership(council)

            # add terms of office. I think this is where the site picks up that Joe is the Dist
            # 1 Council member. 

    
            match = dist_pat.match(district)
            if match:
                dist_num = match.group('distnum')


            else:
                logger.warn("unknown district pattern for %s: %s", name, district) 
                dist_num = None
    

            if dist_num:
                person.add_term(role="member", 
                    org_classification="legislature",
                    label=f"District {dist_num} Councilmember", 
                    district=f"District {dist_num} Councilmember",
                    # NB end_date is REQUIRED. The councilmember querset won't find any council members
                    # if the end dates for their terms aren't set.
                    end_date = "2025-01-01")

            else:
                # at large members w/out districts.
                person.add_term(role="member",
                    org_classification="legislature",
                    label="Councilmember at Large",
                    district="Councilmember at Large",
                    end_date="2025-01-01")
    
         

            if (council_title.upper() in ["COUNCIL PRESIDENT"]):
                person.add_term(
                        role="member",
                        org_classification="legislature",
                        label=council_title.title(),
                        district=council_title.title(),
                        end_date="2025-01-01")


            if (whip_title.upper() in ["MAJORITY WHIP"]):
                person.add_term(
                        role="member",
                        org_classification="legislature",
                        label=whip_title.title(),
                        district=whip_title.title(),
                        end_date="2025-01-01")


            # TODO Phila site's contact info is a little tedious to parse

            # Add email address.
            #email_xpath = '//a[contains(@href, "mailto")]/@href'
            #email = urls.detail.xpath(email_xpath).pop()[7:]
            #memb.contact_details.append(
            #    dict(type='email', value=email, note='work'))

            # Add sources.
            person.add_source(url)

            yield person
