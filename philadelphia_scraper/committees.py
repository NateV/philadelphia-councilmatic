from pupa.scrape import Scraper, Organization, Membership, Person
import lxml
import logging
from datetime import date
from typing import List
import re
from philadelphia_scraper.utils import name_adjuster

logger = logging.getLogger(__name__)

def repair_names(names: List[str]) -> List[str]:
    """
    A committee might have names like "Joe James, Sally Smith" which can be split
    into members by splitting on a comma. 

    But if the names are "Joe James, Jr., Sally Smith", then "Jr" will end up as its own name, which is wrong.

    This will take a list of names, and for certain suffixes like "Jr", re-apppend them to the 
    """
    new_names = []
    for name in names:
        if re.match(r"Jr\.", name, flags=re.I) and (len(new_names) > 0):
            new_names[-1] = new_names[-1] + ", " + name
        else:
            new_names.append(name)
    return [name_adjuster(n) for n in new_names]

class PhiladelphiaCommitteeScraper(Scraper):

    COMMITTEES_LIST = "https://phlcouncil.com/standing-committees/"


    def scrape(self):

        resp = self.request(url=self.COMMITTEES_LIST, method="GET")
        assert resp.status_code == 200, "Bad Request for Committees List"
        doc = lxml.html.fromstring(resp.text)

        committee_els = "//div[@class='x-accordion-group']"
        committees = doc.xpath(committee_els)
    
        # TODO set the term end date in a real way.
        term_end_date = date(2024,1,1)

        for el in committees:
            try:
                committee_name = el.xpath("./div/a")[0].text
            except: 
                continue
            
            if committee_name == "Whole Council": continue

    
            o = Organization(committee_name, classification="committee")
            o.add_source(self.COMMITTEES_LIST)

    
            # NB site will only show committees that have at least one member, so finding all members is def. required.

            chair_path = ".//h6[text()='Chair']/following-sibling::p[1]"
            try:
                chair = el.xpath(chair_path)[0].text
                post = o.add_post(label=f"Chair", role="Chair")
                o.add_member(chair, "Chair", post_id=post._id, end_date=term_end_date, label="Chair")
            except:
                logger.warn("Could not find chair for %s" % committee_name)

            vice_chair_path = ".//h6[text()='Vice Chair']/following-sibling::p[1]"
            try:
                vice_chair = el.xpath(vice_chair_path)[0].text
                post = o.add_post(label="Vice Chair", role="Vice Chair")
                o.add_member(vice_chair, "Vice Chair", post_id=post._id, end_date=term_end_date, label="Chair")
            except:
                logger.warn("Could not find vice chair for %s" % committee_name)

            members_path = ".//h6[contains(text(), 'Members (Consisting of ')]/following-sibling::p[1]"
            try:
                members = repair_names(
                    [m.strip() for m in el.xpath(members_path)[0].text.split(",")]
                    ) 
                for m in members:
                    o.add_member(m, end_date=term_end_date, role="Member", label="Chair")
            except:
                logger.warn("Could not find members for %s" % committee_name)

            yield o

        return
        

