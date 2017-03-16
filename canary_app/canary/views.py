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
    stream.filter(track=[search['search']], async=True)

    return HttpResponseRedirect('/visualization')

def stop_stream(request):

    stream.disconnect()

    return HttpResponseRedirect('/results')

def visualization(request):

    template_name = 'canary/visualization.html'

    sentiment = {'positive': handler.positive, 'negative': handler.negative, 'neutral': handler.neutral}

    sentiment = handler.get_data()

    context = {'sentiment': sentiment}

    return render(request, template_name, context)

def results(request):

    template_name = 'canary/results.html'

    sentiment = {
                'positive': handler.positive, 
                'negative': handler.negative, 
                'neutral': handler.neutral,
                'positive_tweets': handler.positive_tweets,
                'negative_tweets': handler.negative_tweets,
                'positive_tweets': handler.neutral_tweets
                }

    sentiment = handler.get_data()

    context = {'sentiment': sentiment}

    return render(request, template_name, context)


   

