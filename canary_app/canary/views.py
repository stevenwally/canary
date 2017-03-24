from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
import tweepy
from canary.streamer import *
from canary.config import *
from canary.models import *
from canary.processor import *

auth = tweepy.OAuthHandler(TWITTER_APP_KEY, TWITTER_APP_SECRET)
auth.set_access_token(TWITTER_KEY, TWITTER_SECRET)
api = tweepy.API(auth)
stream_listener = Listener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

def index(request):
    template_name = 'canary/index.html'
    return render(request, template_name, {})


def start_stream(request):
    '''
        initiate connection to Twitter Streaming API. takes one argument -> keyword.
    '''
    search = request.POST

    processor = Processor()
    processor.persist_keyword(search['search'])
    handler.clear_handler()
    handler.set_keyword(search['search'])
    stream.filter(track=[search['search']], async=True)

    return HttpResponseRedirect('/visualization')

def stop_stream(request):

    stream.disconnect()
    return HttpResponseRedirect('/results')

def visualization(request):

    template_name = 'canary/visualization.html'
    context = handler.get_data()
    return render(request, template_name, context)

def results(request):

    template_name = 'canary/results.html'
    context = handler.get_data()
    return render(request, template_name, context)