# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .events import PhiladelphiaEventScraper
from .people import PhiladelphiaPersonScraper
from .bills import PhiladelphiaBillScraper
from .committees import PhiladelphiaCommitteeScraper

DIVISION_ID = "ocd-division/country:us/state:pa/place:philadelphia"


class Philadelphia(Jurisdiction):
    division_id = DIVISION_ID
    classification = "legislature"
    name = "City of Philadelphia"
    url = "https://phlcouncil.com/"
    scrapers = {
        "events": PhiladelphiaEventScraper,
        "people": PhiladelphiaPersonScraper,
        "bills": PhiladelphiaBillScraper,
        "committees": PhiladelphiaCommitteeScraper,
    }

    legislative_sessions = [
        {
            "identifier": "2023",
            "name": "2023 Regular Session",
            "start_date": "2023-05-20",
            "end_date": "2023-12-30",
        },
    ]


    def get_organizations(self):
        #REQUIRED: define an organization using this format
        #where org_name is something like Seattle City Council
        #and classification is described here:
        org = Organization(name="Philadelphia City Council", classification="legislature")
        org.add_source(self.url)
       
        # See https://www.popoloproject.com/specs/post.html
        org.add_post(label="Council President", role="Member")
        org.add_post(label="Majority Whip", role="Member")
        for dist in range(1,11):
            org.add_post(label=f"District {dist} Councilmember", role=f"Member")
    
        # There are 6 at-larges - 
        # TODO what is the proper way to handle multi-seat 'Posts'?
        for at_large in range(1,8):
           org.add_post(
                   label=f"Councilmember at Large ({at_large})",
                   role="Member")
   


        #REQUIRED: yield the organization
        yield org
