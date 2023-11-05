from django.conf import settings
from django.db import models
from councilmatic_core.models import Bill, Event
from datetime import datetime
import pytz

app_timezone = pytz.timezone(settings.TIME_ZONE)

class CityBill(Bill):
    """
    Subclass of Pupa's Bill that overrides certain methods to make nicer Philadelphia-centric bills.

    NB has to have this name, as it is imported by django-councilmatic.

    """
    
    class Meta:
        proxy = True
    def __init__(self,*args, **kwargs):
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


