from django.conf.urls import url, include
from django.contrib import admin
from canary.views import *


app_name = 'canary'
urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^start_stream/', start_stream, name='start_stream'),
    url(r'^stop_stream/', stop_stream, name='stop_stream'),
    url(r'^visualization/', visualization, name='visualization'),
    url(r'^results/', results, name='results'),
]