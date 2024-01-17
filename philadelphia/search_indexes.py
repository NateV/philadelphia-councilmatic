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

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare_actions(self, obj):
        return [str(action) for action in obj.actions.all()]

    def prepare_sponsorships(self, obj):
        return [
            str(sponsorship.person)
            for sponsorship in obj.sponsorships.filter(primary=True)
        ]
