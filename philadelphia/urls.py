
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.views.generic.base import RedirectView
from haystack.query import SearchQuerySet
from philadelphia import views
from haystack.query import SearchQuerySet
from councilmatic_core.views import CouncilmaticSearchForm, CouncilmaticFacetedSearchView

sqs = (SearchQuerySet().facet('bill_type')
                      .facet('sponsorships') #, sort='index')
                      .facet('controlling_body')
                      .facet('inferred_status')
                      .facet('topics')
                      .facet('legislative_session')
                      .highlight())



urlpatterns = [
    url(r"^legislation/(?P<slug>[^/]+)/$",
        views.PhilaBillDetailView.as_view(),
        name='bill_detail',),
    url(r'^search/', CouncilmaticFacetedSearchView(searchqueryset=sqs,
                                                   form_class=CouncilmaticSearchForm)),

        ]
