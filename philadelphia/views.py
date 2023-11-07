from councilmatic_core.models import *
from models import *
from councilmatic_core.views import *
from django.conf import settings
from django.shortcuts import render




class PhilaBillDetailView(BillDetailView):
    model = PhilaBill
    template_name = "councilmatic_core/legislation.html"
    context_object_name = "legislation"

    def get_context_data(self, **kwargs):
        context = super(BillDetailView, self).get_context_data(**kwargs)

        context["actions"] = self.get_object().actions.all().order_by("-order")
        bill = context["legislation"]

        seo = {}
        seo.update(settings.SITE_META)
        seo["site_desc"] = bill.listing_description
        seo["title"] = "%s - %s" % (bill.friendly_name, settings.SITE_META["site_name"])
        context["seo"] = seo

        context["user_subscribed"] = False
        if self.request.user.is_authenticated:
            user = self.request.user
            context["user"] = user
            # check if person of interest is subscribed to by user

            if settings.USING_NOTIFICATIONS:
                for bas in user.billactionsubscriptions.all():
                    if bill == bas.bill:
                        context["user_subscribed"] = True
                        break

        return context





