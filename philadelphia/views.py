from councilmatic_core.models import *
from philadelphia.models import *
from councilmatic_core.views import *
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

class PhilaBillDetailView(BillDetailView):
    model = PhilaBill
    template_name = "philadelphia/legislation.html"
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


class CORSProxyView(View):
    """
    CORS Proxy so we can display pdfs of bills.
    """
    def get(self, request, *args, **kwargs):
        url = request.GET.get('url')
        if url:
            # add the legistar url here.
            full_url = "https://phila.legistar.com/View.ashx?" + url

            remote_pdf = requests.get(full_url)
            response = HttpResponse(remote_pdf.content)
            if request.GET.get('download') == 'true':
                response['Content-Disposition'] = 'attachment; filename=bill.pdf'
            return response


class CommitteeDetailView(DetailView):
    model = Organization
    template_name = "philadelphia/committee.html"
    context_object_name = "committee"

    def get_context_data(self, **kwargs):
        context = super(CommitteeDetailView, self).get_context_data(**kwargs)

        committee = context["committee"]
        context["memberships"] = committee.memberships.all()
        description = None

        if getattr(settings, "COMMITTEE_DESCRIPTIONS", None):
            description = settings.COMMITTEE_DESCRIPTIONS.get(committee.slug)
            context["committee_description"] = description

        seo = {}
        seo.update(settings.SITE_META)

        if description:
            seo["site_desc"] = description
        else:
            seo["site_desc"] = "See what %s's %s has been up to!" % (
                settings.CITY_COUNCIL_NAME,
                committee.name,
            )

        seo["title"] = "%s - %s" % (committee.name, settings.SITE_META["site_name"])
        context["seo"] = seo

        context["user_subscribed_actions"] = False
        context["user_subscribed_events"] = False
        if self.request.user.is_authenticated:
            user = self.request.user
            context["user"] = user
            # check if person of interest is subscribed to by user

            if settings.USING_NOTIFICATIONS:
                for cas in user.committeeactionsubscriptions.all():
                    if committee == cas.committee:
                        context["user_subscribed_actions"] = True
                for ces in user.committeeeventsubscriptions.all():
                    if committee == ces.committee:
                        context["user_subscribed_events"] = True
        return context



