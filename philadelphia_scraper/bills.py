from pupa.scrape import Scraper
from pupa.scrape import Bill
from legistar.bills import LegistarBillScraper
from datetime import date

class PhiladelphiaBillScraper(LegistarBillScraper, Scraper):
    
    LEGISLATION_URL = "https://phila.legistar.com/Legislation.aspx"
    BASE_URL = "https://phila.legistar.com/"
    BASE_WEB_URL = "https://phila.legistar.com/"
    TIMEZONE = "US/Eastern"

    def scrape(self):
        """
        
        LegistarBillsScraper.legislation() is going to yield bills as dicts.

        I need to then create Bill objects from each bill.

        """
        for bill in self.legislation(created_after=date(2023,6,1)):
        

            # so scrape needs to yield to ... what?

            if bill['Type'] != "COMMUNICATION":
                # This isn't a bill, but a note from somebody to Council.
                
                       
                identifier = bill['File\xa0#']
                title = bill['Title']
                classification = bill['Type'].strip().lower()
                # Somewhere there's a list of enum valuesthat 'classification' can take.
                legislative_session = "2023" #bill['File\xa0Created']
    
    
                bill_ = Bill(identifier=identifier,
                        title=title,
                        classification=classification,
                        legislative_session=legislative_session,
                        from_organization={"name": "Philadelphia City Council"})
    
                bill_.add_source(bill['url'],note="url")


                yield bill_
