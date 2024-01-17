from pupa.scrape import Scraper
from pupa.scrape import Person
from pupa.scrape import Organization
import lxml
import re
import logging
import json 
from datetime import date
from typing import List
from philadelphia_scraper.utils import (
        name_adjuster,
        from_x,
        get_last_name,
        pad_list
        )

logger = logging.getLogger(__name__)

class PhiladelphiaPersonScraper(Scraper):

    """
    Philadelphia's Legistar instance seems to not have pages dedicated to the legislators. This seems to be fairly common. Other sites have the info about who is on city council.

    See the municpal_scrapers for boise, denver, rialto, for examples of other scrapers that find 
    legislators from other sites.
    """

    # TODO this should not have a trailing /
    COUNCIL_ROOT = "https://phlcouncil.com/"
    COUNCIL_URL = "https://phlcouncil.com/council-members"


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

        # Ughhhh.
        at_large_counter = 1


        for card_num, card in enumerate(cards):


            
            name = from_x(card.xpath(name_xpath)).title()
            if re.search("vacant",name, flags=re.I): 
                continue
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
            #if re.search(r"Harrity", name,flags=re.I): breakpoint()
            last_name = get_last_name(name)

            # Create legislator.
            
            # BUG seems like I should't put the district here, because I add a 
            # term later...
            #person = Person(name_adjuster(name), image=pic, district=district)
            
            person = Person(name_adjuster(name), image=pic)

            # I don't know what to do for names that have family name as not last.
            # We need the family name because legislation is linked to people in legistar only by 'CouncilMember [last name]'.
            person.family_name = last_name

            # Add membership on council.
            # is this a mistake, since we're also adding roles?
            #person.add_membership(council)

            # add terms of office. I think this is where the site picks up that Joe is the Dist
            # 1 Council member. 



            match = dist_pat.match(district or "")

            if match:
                dist_num = match.group('distnum')


            else:
                logger.warn("unknown district pattern for %s: %s", name, district) 
                dist_num = None
    

            if dist_num:
                person.add_term(role="Member", 
                    org_classification="legislature",
                    label=f"District {dist_num} Councilmember", 
                    district=f"District {dist_num} Councilmember",
                    # NB end_date is REQUIRED. The councilmember querset won't find any council members
                    # if the end dates for their terms aren't set.
                    end_date = "2025-01-01")

            else:
                # at large members w/out districts.
                person.add_term(role="Member",
                    org_classification="legislature",
                    label=f"Councilmember at Large ({at_large_counter})",
                    district=f"Councilmember at Large ({at_large_counter})",
                    end_date="2025-01-01")
                at_large_counter += 1

         
            # TODO sould leadership titles be 'roles', not Posts?
            if (council_title.upper() in ["COUNCIL PRESIDENT"]):
                person.add_term(
                        role="Member",
                        org_classification="legislature",
                        label=council_title.title(),
                        district=council_title.title(),
                        end_date="2025-01-01")
                person.add_name(f"Council President {last_name}")


            if (whip_title.upper() in ["MAJORITY WHIP"]):
                person.add_term(
                        role="Member",
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

        # If there's a former member who is still listed in committees and hearings,
        # then we still need to add that person to the database, even if they're 
        # no longer listed as a council member. 
        # This extra_people.json file gives us a mechanism for just adding former 
        # members by hand.
        with open("philadelphia_scraper/extra_people.json","r") as extra_people_file:
            extra_people = json.load(extra_people_file)
            for extra_person_record in extra_people["people"]:
                extra_p = Person(
                        extra_person_record['name'],
                        image=extra_person_record['image'])
                extra_p.family_name = extra_person_record['family_name']

                extra_p.add_source(self.COUNCIL_URL)

                for term_record in extra_person_record["terms"]:
                    extra_p.add_term(
                        role=term_record["role"],
                        org_classification=term_record["org_classification"],
                        label=term_record["label"],
                        district=term_record["district"],
                        end_date=term_record["end_date"]
                        )
                yield extra_p




