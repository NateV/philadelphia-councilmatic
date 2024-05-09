from pupa.scrape import Scraper
from pupa.scrape import Event, Bill
import lxml
from datetime import datetime, tzinfo
import logging
from philadelphia_scraper.utils import from_x, content_from_x
from typing import List
import pytz

logger = logging.getLogger(__name__)

def is_event_duplicated(new_e: Event, es: List[Event]) -> bool:
    for e in es:
        if (new_e.name == e.name) and (new_e.start_date == e.start_date) and (new_e.location == e.location):
            return True
    return False

           

class PhiladelphiaEventScraper(Scraper):

    CALENDAR = "https://phila.legistar.com/Calendar.aspx"    

    def lxmlize(self, url):
        search_cookie = {"Setting-30-Calendar Year":"Last Month"}
        # other values for controlling how many results come back:
        # This Year, Today, This Month
        html = self.get(url, cookies=search_cookie).text
        doc = lxml.html.fromstring(html)
        doc.make_links_absolute(url)
        return doc

    def scrape(self):
        """
        Scrape the events calendar.

        NB. This request will fetch just the events in the current month. 
        It may be possible to use cookies to collect more if desired. Use the  
        site to figure out what cookies you need to set. 
        """

        doc = self.lxmlize(self.CALENDAR)
        # We'll only grab the first 100 events at most
        event_nodes = doc.xpath("//table[@id='ctl00_ContentPlaceHolder1_gridCalendar_ctl00']/tbody//tr") 
        events = []

        # and while testing, even fewer
        for idx, event in enumerate(event_nodes):
            nameL = event.xpath("./td[1]")
            dateL = event.xpath("./td[2]")
            timeL = event.xpath("./td[4]")
            locationL = event.xpath("./td[5]")
            detailsUrlL = event.xpath("./td[6]//a/@href")
            agendaL = event.xpath("./td[7]//a/@href")

            name = content_from_x(nameL[0]) #.text_content().strip()
            date = content_from_x(dateL)
            date_ = datetime.strptime(date, r"%m/%d/%Y").strftime("%Y-%m-%d")
            time = content_from_x(timeL)
            location = content_from_x(locationL)
            agenda = content_from_x(agendaL)
            details_url = content_from_x(detailsUrlL)
            e = Event(
                    name=name,
                    start_date=date_,
                    location_name=location,
                    )
            if details_url != "":
                e.add_source(url=details_url)
            else:
                e.add_source(self.CALENDAR)




            if is_event_duplicated(e, events):
                continue
                logger.warn("Found duplicate event: ",e)
            else:
                events.append(e)
                yield e
                
            """
            Now handle events to record what has happened to bills.
            """
            if (details_url is not None) and (details_url !=""):

                page = self.lxmlize(details_url)
                bill_actions = page.xpath("//table[@id='ctl00_ContentPlaceHolder1_gridMain_ctl00']/tbody/tr")

                mtg_date_string = content_from_x(page.xpath("//span[@id='ctl00_ContentPlaceHolder1_lblDate']"))
                
                eastern = pytz.timezone('US/Eastern') 
                mtg_date = datetime.strptime(mtg_date_string, "%m/%d/%Y")
                mtg_date = mtg_date.replace(tzinfo=eastern)
                legislative_session = str(mtg_date.year)
                


                for idx, bill_action in enumerate(bill_actions):
                    file_numL = bill_action.xpath("./td[1]/font/a/font")
                    file_num = content_from_x(file_numL)
                    doc_typeL = bill_action.xpath("./td[5]")
                    doc_type = content_from_x(doc_typeL)
                    doc_titleL = bill_action.xpath("./td[6]")
                    doc_title = content_from_x(doc_titleL)
                    actionL = bill_action.xpath("./td[7]")
                    action = content_from_x(actionL)

                    if (action is not None) and (action != ''): 
                        bill = Bill(
                            identifier=file_num,
                            title=doc_title,
                            legislative_session=legislative_session,
                            from_organization={"name":"Philadelphia City Council"})
                        bill.add_action(
                                description=action,
                                date=mtg_date
                                )
                        bill.add_source(details_url, note="meeting")

                        yield bill
         
