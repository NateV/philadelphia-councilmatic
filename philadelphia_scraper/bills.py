from typing import Dict, Tuple, Iterator, List
from pupa.scrape import Scraper
from pupa.scrape import Bill, VoteEvent
from pupa.scrape.bill import Action
from legistar.bills import LegistarBillScraper
from datetime import date

class PhiladelphiaBillScraper(LegistarBillScraper, Scraper):
    
    LEGISLATION_URL = "https://phila.legistar.com/Legislation.aspx"
    BASE_URL = "https://phila.legistar.com/"
    BASE_WEB_URL = "https://phila.legistar.com/"
    TIMEZONE = "US/Eastern"

    def actions(self, matter_id: str) -> Iterator[Tuple[Dict[str, str], Tuple[dict | None, dict | None]]]:
        """
        Collect the actions on a particular bill.
        """
        breakpoint() 
        for action in self.history(matter_id):
            bill_action = {}
            votes = (None, None)
            breakpoint()
            bill_action["action_date"] = ""
            bill_action["action_description"] = ""
            bill_action["responsible_org"] = ""


            yield bill_action, votes


    def scrape(self):
        """
        
        LegistarBillsScraper.legislation() is going to yield bills as dicts.

        I need to then create Bill objects from each bill.

        """
        for bill in self.legislation(created_after=date(2023,6,16)):
        

            # so scrape needs to yield to ... what?

            if bill['Type'] != "COMMUNICATION":
                # This isn't a bill, but a note from somebody to Council.
                # TODO - do something about Resolutions?

                       
                identifier = bill['File\xa0#']
                title = bill['Title']
                classification = bill.get('Type').strip().lower()
                # Somewhere there's a list of enum valuesthat 'classification' can take.
                legislative_session = "2023" #bill['File\xa0Created']
    
                assert identifier is not None

                bill_ = Bill(identifier=identifier,
                        title=title,
                        classification=classification,
                        legislative_session=legislative_session,
                        from_organization={"name": "Philadelphia City Council"})
    
                bill_.add_source(bill['url'],note="url")
                for action, vote in self.actions(bill_.identifier):
                    act = bill_.add_action(action['action_description'],
                                          action['action_date'],
                                          organization={'name': action['responsible_org']},
                                          classification=action['classification'])

                    
                    result, votes = vote
                    if result:
                        yield self.get_vote_event(bill_, act, votes, result)

            
                yield bill_

    def get_vote_event(self, bill: Bill, act: Action, votes: List[Dict[str, str]], result: str) -> VoteEvent:
        '''Make VoteEvent object from given Bill, action, votes and result.'''
        breakpoint()
        organization = "?"
        vote_event = VoteEvent(legislative_session=bill.legislative_session,
                               motion_text=act['description'],
                               organization=organization,
                               classification=None,
                               start_date=act['date'],
                               result=result,
                               bill=bill)

        legistar_web, legistar_api = [src['url'] for src in bill.sources]

        vote_event.add_source(legistar_web)
        vote_event.add_source(legistar_api + '/histories')

        for vote in votes:
            raw_option = vote['VoteValueName'].lower()

            if raw_option == 'suspended':
                continue

            
            #clean_option = self.VOTE_OPTIONS.get(raw_option, raw_option)
            clean_option = raw_option
            vote_event.vote(clean_option, vote['VotePersonName'].strip())

        return vote_event


