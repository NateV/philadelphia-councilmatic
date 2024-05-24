from django.conf import settings
from django.db import models
from councilmatic_core.models import Bill, Event
from datetime import datetime
import pytz
import re
from urllib import parse

app_timezone = pytz.timezone(settings.TIME_ZONE)

class PhilaBill(Bill):
    """
    Subclass of Pupa's Bill that overrides certain methods to make nicer Philadelphia-centric bills.

    NB has to have this name, as it is imported by django-councilmatic.

    """
    
    class Meta:
        proxy = True
    def __init__(self,*args, **kwargs):
        # Huh - so CityBill gets instantiated in the search page, 
        # but not in the bill detail page??
        super().__init__(*args, **kwargs)

    @property
    def friendly_name(self):
        """
        Overriding a default non-Philly-oriented implementation in pupa models.py.
        """
        words = self.title.split(" ")
        if len(words) > 5:
            words = " ".join(words[0:5]) + "..."

        return f"{self.identifier} - {words}"

    @property
    def full_text_doc_url(self):
        """
        overriding default so we can embed pdfs of bill text.
        """
        

        # self.documents is a RelatedManager for BillDocument objs. from
        # here: https://github.com/opencivicdata/python-opencivicdata/blob/master/opencivicdata/legislative/models/bill.py
        # then the BilDocument has links,
        # and links get urls from a LinkMixin.
        # https://github.com/opencivicdata/python-opencivicdata/blob/1c352a8d246846d1bce976a8c3686ee4f35d0e69/opencivicdata/core/models/base.py#L91
         
        
        # Instead of returning the regular url, the url should be to a cors proxy.
        if len(docs := self.documents.all()) > 0:
            if len(links := docs[0].links.all()) > 0:  
                bill_url = links[0].url
                url_patt = re.compile(r'https://phila.legistar.com/View\.ashx\?(?P<bill_url_id>.*)')
                match = url_patt.match(bill_url)
                if match:
                    bill_url_id = parse.quote(match.group('bill_url_id'))
                    return f"/pdfs/?url={bill_url_id}"
                    #return bill_url_id


    @property
    def inferred_status(self):
        actions = self.actions.all().order_by("-order")
        classification_hist = [a.classification for a in actions]
        last_action_date = actions[0].date_dt if actions else None
        bill_type = self.bill_type

        if len(actions) > 0:
            return actions[0].description
        
        else:
            return "New"

class PupaUpdate(models.Model):
    update_date = models.DateField()
