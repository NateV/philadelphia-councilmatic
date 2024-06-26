from councilmatic_core.models import *
from philadelphia.models import *
from councilmatic_core.views import *
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from typing import List, Tuple, TypeVar

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


class CommitteesView(ListView):
    template_name = "philadelphia/committees.html"
    context_object_name = "committees"

    def get_queryset(self):
        return Organization.committees()


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

def expand_posts(posts: List[Post]) -> List[Tuple[Post, List[Membership]]]:
    """
    From a list of posts, expand to a list mapping posts
    to current members.
    """
    posts_ = []
    for post in posts:
        current_members = post.memberships.filter(
                start_date_dt__lt=timezone.now(),
                end_date_dt__gt=timezone.now())
        posts_.append((post, current_members))
    return posts_

A = TypeVar('A')
B = TypeVar('B')

def invert_map(dct: List[Tuple[A,List[B]]]) -> List[Tuple[B,List[A]]]:
    """
    Given a list that is a map from some type A to lists of some type B,
    invert the map to a list of tuples mapping from B to lists of A
    """
    temp_dict = dict()
    for a, bs in dct:
        for b in bs:
            if temp_dict.get(b) is None:
                temp_dict[b] = [a]
            else:
                temp_dict[b].append(a)
    return [(a, bs) for a, bs in temp_dict.items()]


class CouncilMembersView(ListView):
    template_name = "philadelphia/council_members.html"
    context_object_name = "posts"

    def map(self):
        map_geojson = {"type": "FeatureCollection", "features": []}

        get_kwarg = {"name": settings.OCD_CITY_COUNCIL_NAME}
        
        posts = Organization.objects.get(**get_kwarg).posts.all()
        for post in posts:
            if post.shape:
                council_member = "Vacant"
                detail_link = ""
                if post.current_member:
                    council_member = post.current_member.person.name
                    detail_link = post.current_member.person.slug

                feature = {
                    "type": "Feature",
                    "geometry": json.loads(post.shape.json),
                    "properties": {
                        "district": post.label,
                        "council_member": council_member,
                        "detail_link": "/person/" + detail_link,
                        "select_id": "polygon-{}".format(slugify(post.label)),
                    },
                }

                map_geojson["features"].append(feature)

        return json.dumps(map_geojson)

    def get_queryset(self):
        get_kwarg = {"name": settings.OCD_CITY_COUNCIL_NAME}

        posts = Organization.objects.get(**get_kwarg).posts.all()
        # We have posts w/ multiple members simultaneously. So 
        # instead of posts, we need to expand posts to a mapping of post:[current members]
        posts_ = expand_posts(posts)
        # TODO how do we both show VACANT Posts (which implies mapping over all posts),
        # and show leadership roles for people
        members = invert_map(posts_)
        return posts_

    def get_context_data(self, *args, **kwargs):
        context = super(CouncilMembersView, self).get_context_data(**kwargs)
        context["seo"] = self.get_seo_blob()

        if settings.MAP_CONFIG:
            context["map_geojson"] = self.map
        else:
            context["map_geojson"] = None

        return context

    def get_seo_blob(self):
        seo = {}
        seo.update(settings.SITE_META)
        return seo


class EventDetailView(DetailView):
    template_name = "philadelphia/event.html"
    model = Event
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        event = context["event"]

        event.source_url = event.sources.all()[0].url

            
        participants = [p.entity_name for p in event.participants.all()]
        context["participants"] = Organization.objects.filter(name__in=participants)

        seo = {}
        seo.update(settings.SITE_META)
        seo["site_desc"] = (
            "Public city council event on %s/%s/%s - view event participants & agenda items"
            % (event.start_time.month, event.start_time.day, event.start_time.year)
        )
        seo["title"] = "%s Event - %s" % (event.name, settings.SITE_META["site_name"])
        context["seo"] = seo

        return context


class PersonDetailView(DetailView):
    model = Person
    template_name = "philadelphia/person.html"
    context_object_name = "person"

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)

        person = context["person"]
        person.source_url = person.sources.all()[0].url
        context["sponsored_legislation"] = (
            Bill.objects.filter(sponsorships__person=person, sponsorships__primary=True)
            .annotate(last_action=Max("actions__date"))
            .order_by("-last_action")[:10]
        )

        title = ""
        if person.current_council_seat:
            title = "%s %s" % (
                person.current_council_seat,
                settings.CITY_VOCAB["COUNCIL_MEMBER"],
            )
        elif person.latest_council_seat:
            title = "Former %s, %s" % (
                settings.CITY_VOCAB["COUNCIL_MEMBER"],
                person.latest_council_seat,
            )
        elif (
            getattr(settings, "EXTRA_TITLES", None)
            and person.slug in settings.EXTRA_TITLES
        ):
            title = settings.EXTRA_TITLES[person.slug]
        context["title"] = title

        seo = {}
        seo.update(settings.SITE_META)
        if person.current_council_seat:
            short_name = re.sub(r",.*", "", person.name)
            seo[
                "site_desc"
            ] = "%s - %s representative in %s. See what %s has been up to!" % (
                person.name,
                person.current_council_seat,
                settings.CITY_COUNCIL_NAME,
                short_name,
            )
        else:
            seo["site_desc"] = "Details on %s, %s" % (
                person.name,
                settings.CITY_COUNCIL_NAME,
            )
        seo["title"] = "%s - %s" % (person.name, settings.SITE_META["site_name"])
        seo["image"] = static(person.headshot.url)
        context["seo"] = seo

        context["map_geojson"] = None

        if (
            settings.MAP_CONFIG
            and person.latest_council_membership
            and person.latest_council_membership.post
            and person.latest_council_membership.post.shape
        ):
            map_geojson = {"type": "FeatureCollection", "features": []}

            feature = {
                "type": "Feature",
                "geometry": json.loads(
                    person.latest_council_membership.post.shape.json
                ),
                "properties": {
                    "district": person.latest_council_membership.post.label,
                },
            }

            map_geojson["features"].append(feature)

            context["map_geojson"] = json.dumps(map_geojson)

        context["user_subscribed"] = False

        if settings.USING_NOTIFICATIONS:
            if self.request.user.is_authenticated:
                user = self.request.user
                context["user"] = user
                # check if person of interest is subscribed to by user

                for ps in user.personsubscriptions.all():
                    if person == ps.person:
                        context["user_subscribed"] = True
                        break

        return context



