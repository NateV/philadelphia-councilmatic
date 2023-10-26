from pupa.scrape import Scraper
from pupa.scrape import Person
from pupa.scrape import Organization
import lxml

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

        name_xpath = "//h4[@class='x-face-title']/strong"
        title_xpath = "//p[@class='x-face-text']/big/strong" # the 'Whip' or 'Leader' title, if any. 
        district_xpath = "//p[@class='x-face-text']/strong" # district, not the 'Whip' or 
        link_xpath = "//a[@class='x-face-button']/@href"
        pic_path = "//div[@class='x-face-graphic']/img/@src"


        response = self.request(url=self.COUNCIL_URL, method="GET")

        html = response.text
        doc = lxml.html.fromstring(html)

        
        # the urls of the council people
        urls = [f"{self.COUNCIL_ROOT}{end_part}" for end_part in doc.xpath(link_xpath)]
        names = [el.text for el in doc.xpath(name_xpath)]
        districts = [el.text for el in doc.xpath(district_xpath)]
        titles = [el.text for el in doc.xpath(title_xpath)]
        images = doc.xpath(pic_path)

        for url, name, district, title, pic in zip(urls, names, districts, titles, images):

            # Create legislator.
            person = Person(name, image=pic, district=district)

            # Add membership on council.
            person.add_membership(council, role=title)

            # TODO Phila site's contact info is a little tedious to parse

            # Add email address.
            #email_xpath = '//a[contains(@href, "mailto")]/@href'
            #email = urls.detail.xpath(email_xpath).pop()[7:]
            #memb.contact_details.append(
            #    dict(type='email', value=email, note='work'))

            # Add sources.
            person.add_source(url)

            yield person
