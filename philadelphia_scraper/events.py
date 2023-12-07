from pupa.scrape import Scraper
from pupa.scrape import Event
import lxml
from datetime import datetime
import logging
from philadelphia_scraper.utils import from_x, content_from_x
from typing import List

logger = logging.getLogger(__name__)

def is_event_duplicated(new_e: Event, es: List[Event]) -> bool:
    for e in es:
        if (new_e.name == e.name) and (new_e.start_date == e.start_date) and (new_e.location == e.location):
            return True
    return False

class PhiladelphiaEventScraper(Scraper):

    CALENDAR = "https://phila.legistar.com/Calendar.aspx"    

    def lxmlize(self, url):
        html = self.get(url).text
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
            agendaL = event.xpath("./td[6]/font/span/a/@href")

            name = content_from_x(nameL[0]) #.text_content().strip()
            date = content_from_x(dateL)
            date_ = datetime.strptime(date, r"%m/%d/%Y").strftime("%Y-%m-%d")
            time = content_from_x(timeL)
            location = content_from_x(locationL)
            agenda = content_from_x(agendaL)

            e = Event(
                    name=name,
                    start_date=date_,
                    location_name=location,
                    # description?
                    )
            if agenda != "":
                e.add_source(agenda)
            else:
                e.add_source(self.CALENDAR)

            if is_event_duplicated(e, events):
                continue
                logger.warn("Found duplicate event: ",e)
            else:
                events.append(e)
                yield e

