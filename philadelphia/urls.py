
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.views.generic.base import RedirectView
from haystack.query import SearchQuerySet
import views



urlpatterns = [
    url(r"^legislation/(?P<slug>[^/]+)/$",
        views.PhilaBillDetailView.as_view(),
        name='bill_detail',),

        ]
