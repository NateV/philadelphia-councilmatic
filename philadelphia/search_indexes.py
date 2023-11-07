from councilmatic_core.haystack_indexes import BillIndex
from haystack import indexes
from .models import PhilaBill
from datetime import datetime
from django.conf import settings
import pytz

app_timezone = pytz.timezone(settings.TIME_ZONE)

class PhilaBillIndex(BillIndex, indexes.Indexable):

    def get_model(self):
        return PhilaBill

