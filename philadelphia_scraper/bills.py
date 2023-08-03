from typing import Dict, Tuple, Generator, List
from pupa.scrape import Scraper
from pupa.scrape import Bill, VoteEvent
from pupa.scrape.bill import Action
from legistar.bills import LegistarBillScraper
from datetime import date
import datetime

class PhiladelphiaBillScraper(LegistarBillScraper, Scraper):
    
    LEGISLATION_URL = "https://phila.legistar.com/Legislation.aspx"
    BASE_URL = "https://phila.legistar.com/"
    BASE_WEB_URL = "https://phila.legistar.com/"
    TIMEZONE = "US/Eastern"
    VOTE_OPTIONS = {
        "Ayes":"yes",
        "Nayes":"no"
            }

    def actions(self, matter_url: str) -> Generator[Tuple[Dict[str, str], Tuple[dict | None, dict | None]], None, None]:
        """
        Collect the actions on a particular bill.

        Args:
            matter_url (str): URL of a bill.

        Yields:
            A dict with information about an action on a bill, and any votes that happened in the action (e.g. a committee hearing)
        
        """
        print("Looking at actions for ", matter_url)
        for action in self.history(matter_url):
            bill_action = {}
            votes = (None, None)
            bill_action["action_date"] =datetime.datetime.strptime(action.get('Date') or "","%m/%d/%Y").strftime("%Y-%m-%d")
            bill_action["action_description"] = action.get('Action') or 'Unknown'
            # there is an action detail url in Action\xa0Details
            # do i need that?
            bill_action["responsible_org"] = action.get('Action\xa0By','Ukn')
            result = action.get("Result")

            # TODO not sure what shows up in the Tally column.
            # Tally is a string, a count of votes, 13:1 or 11:3. It indicates there was a vote,
            # and that there are action details to extract.
            tally = action.get('Tally')
            if tally is not None and tally != "":
                action_details = action.get("Action\xa0Details")
                tally_url = action_details.get('url') if action_details is not None else None

                votes = (result, self.extractVotes(tally_url) if tally_url is not None else None)
            else:
                print("tally is ", tally)
            

            yield bill_action, votes


    def scrape(self, search_text: str='qualified electors', created_after: date | None = date(2023,1,1), created_before: date | None = date(2023,1,28) ) -> Generator[Bill | VoteEvent, None, None]:
        """
        
        LegistarBillsScraper.legislation() is going to yield bills as dicts.

        I need to then create Bill objects from each bill.

        """
        for bill in self.legislation(created_after=created_after, created_before=created_before, search_text=search_text):
        

            # so scrape needs to yield to ... what?

            if bill['Type'] not in ["COMMUNICATION", "Resolution"]:
                # This isn't a bill, but a note from somebody to Council.
                # TODO - do something about Resolutions?

                       
                identifier = bill['File\xa0#']
                title = bill['Title']
                
                classification = bill.get('Type').strip().lower()

                date_created = bill["File\xa0Created"]
                
                legislative_session =str(datetime.datetime.strptime(bill.get("File\xa0Created") or "","%m/%d/%Y").year )
                 
                assert identifier is not None

                bill_ = Bill(identifier=identifier,
                        title=title,
                        classification=classification,
                        legislative_session=legislative_session,
                        from_organization={"name": "Philadelphia City Council"})
    
                if bill.get('url') is not None:
                    bill_.add_source(bill['url'],note="web")
                    for action, vote in self.actions(bill.get('url') or ""):

                        # Classification of an action describes the type of the action, like 'filing' or 'executive-signature'
                        # TODO need a dict that maps the philly action's "Action" key to the enum values of councilmatic's classifications.
                        act = bill_.add_action(action['action_description'],
                                              action['action_date'],
                                              organization={'name': action['responsible_org']},
                                              classification="")
    
                        # DOING what is 'vote'? Need to find a bill w/ votes to see if this works.
                        # Use 220733,  	9/22/2022 passed  2/16/2023 
                        # It had a vote.

                        result, votes = vote
                        if result:
                            yield self.get_vote_event(bill_, act, votes, result)
    
                
                yield bill_

    def get_vote_event(self, bill: Bill, act: Action, votes: List[Dict[str, str]], result: str) -> VoteEvent:
        '''Make VoteEvent object from given Bill, action, votes and result.'''
        organization = "?"
        vote_event = VoteEvent(legislative_session=bill.legislative_session,
                               motion_text=act['description'],
                               organization=organization,
                               classification=None,
                               start_date=act['date'],
                               result=result,
                               bill=bill)

        legistar_web = [src['url'] for src in bill.sources]

        vote_event.add_source(legistar_web)

        for vote in votes:
            raw_option = vote['VoteValueName'].lower()

            if raw_option == 'suspended':
                continue

            
            clean_option = self.VOTE_OPTIONS.get(raw_option, raw_option)
            #clean_option = raw_option
            vote_event.vote(clean_option, vote['VotePersonName'].strip())

        return vote_event


