from pupa.scrape import Scraper, Organization, Membership, Person
import lxml
import logging
from datetime import date
from typing import List
import re
from philadelphia_scraper.utils import (
        name_adjuster,
        from_x,
        get_last_name,
        pad_list
        )

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
        term_end_date = date(2024,12,30)

        for el in committees:
            try:
                committee_name = el.xpath("./div/a/span")[0].text.strip()
                if committee_name is None:
                    committee_name = el.xpath("./div/a/span")[0].text_content().strip()
                if committee_name is None:
                    logger.warn("Could not figure out committee name: ", el.text_content())
                    continue
            except: 
                logger.warn("Could not figure out committee name: ", el.text_content())
                continue
            
            if "Whole Council" in committee_name: continue
    
            o = Organization(committee_name, classification="committee")
            o.add_source(self.COMMITTEES_LIST)

    
            # NB site will only show committees that have at least one member, so finding all members is def. required.

            chair_path = ".//h6[text()='Chair']/following-sibling::p[1]"
            try:
                chair = el.xpath(chair_path)[0].text
                post = o.add_post(label=f"Chair of {committee_name}", role="Chair")
                # family names are needed here, because we use them in the 
                # PeopleScraper. If they're not included, these Person objects
                # don't match the Person objects already in the db, so pupa
                # won't know they are the same people.
                #last_name = get_last_name(chair)
                #chair = Person(chair)
                #chair.family_name = last_name
                #chair.add_source(self.COMMITTEES_LIST)
                #yield chair
                o.add_member(chair, "Chair", 
                        post_id=post._id, end_date=term_end_date, label="Chair")
            except:
                logger.warn("Could not find chair for %s" % committee_name)

            vice_chair_path = ".//h6[text()='Vice Chair']/following-sibling::p[1]"
            try:
                vice_chair = el.xpath(vice_chair_path)[0].text
                #last_name = get_last_name(vice_chair)
                #vice_chair = Person(vice_chair)
                #vice_chair.family_name = last_name
                #vice_chair.add_source(self.COMMITTEES_LIST)
                #yield vice_chair
                post = o.add_post(label=f"Vice Chair of {committee_name}", role="Vice Chair")
                o.add_member(vice_chair, "Vice Chair", post_id=post._id, end_date=term_end_date, label="Vice Chair")
            except:
                logger.warn("Could not find vice chair for %s" % committee_name)

            members_path = ".//h6[contains(text(), 'Members (Consisting of ')]/following-sibling::p[1]"
            try:
                members = repair_names(
                    [m.strip() for m in el.xpath(members_path)[0].text.split(",") if m.strip() is not ""]
                    ) 

                for m in members:
                    #m_ = Person(m)
                    #m_.family_name = get_last_name(m)

                    #m_.add_source(self.COMMITTEES_LIST)
                    #yield m_
                    o.add_member(m, end_date=term_end_date, role="Member", label="Member")
            except:
                logger.warn("Could not find members for %s" % committee_name)

            yield o

        return
        

