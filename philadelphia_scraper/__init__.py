# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .events import PhiladelphiaEventScraper
from .people import PhiladelphiaPersonScraper
from .bills import PhiladelphiaBillScraper


class Philadelphia(Jurisdiction):
    division_id = "ocd-division/country:us/state:pa/place:philadelphia"
    classification = "legislature"
    name = "City of Philadelphia"
    url = "https://phlcouncil.com/"
    scrapers = {
        #"events": PhiladelphiaEventScraper,
        "people": PhiladelphiaPersonScraper,
        "bills": PhiladelphiaBillScraper,
    }

    legislative_sessions = [
        {
            "identifier": "2023",
            "name": "2023 Regular Session",
            "start_date": "2023-05-20",
            "end_date": "2023-12-19",
        },
    ]


    def get_organizations(self):
        #REQUIRED: define an organization using this format
        #where org_name is something like Seattle City Council
        #and classification is described here:
        org = Organization(name="Philadelphia City Council", classification="legislature")
        org.add_source(self.url)
        # OPTIONAL: add posts to your organizaion using this format,
        # where label is a human-readable description of the post (eg "Ward 8 councilmember")
        # and role is the position type (eg councilmember, alderman, mayor...)
        # skip entirely if you're not writing a people scraper.
        #org.add_post(label="position_description", role="position_type")

        #REQUIRED: yield the organization
        yield org
