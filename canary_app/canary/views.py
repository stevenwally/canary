from processor import *

from listener import Listener
from config import keys
from django.shortcuts import render
from django.http import HttpResponseRedirect

from tweepy import OAuthHandler, API, Stream

TweetProcessor = Processor()

auth = OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = API(auth)

listener = Listener(processor=TweetProcessor)
stream = Stream(auth=api.auth, listener=listener)


def index(request):
    """
    Render landing template.
    :param request:
    :return:
    """
    template_name = 'canary/index.html'
    return render(request, template_name, {})


def start_stream(request):
    """
    Initiate connection to Twitter Streaming API.
    :param request:
    :return:
    """
    query = str(request.POST['search'])

    TweetProcessor.clear()
    TweetProcessor.set_keyword(query)
    stream.filter(track=[query], is_async=True)

    return HttpResponseRedirect('/visualization')


def stop_stream(request):
    """
    Close connection with Twitter stream.
    :param request:
    :return:
    """
    stream.disconnect()
    return HttpResponseRedirect('/results')


def visualization(request):
    """
    Render visualization template, including data stream
    :param request:
    :return:
    """

    template_name = 'canary/visualization.html'
    data = TweetProcessor.get_data()
    return render(request, template_name, data)


def results(request):
    """
    Render results template
    :param request:
    :return:
    """

    template_name = 'canary/results.html'
    data = TweetProcessor.get_data()
    return render(request, template_name, data)
