from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from canary.processor import *

processor = Processor()

class Listener(StreamListener):

    def on_status(self, status):
        # Get tweets -> exclude retweets
        if 'RT @' in status.text:
            return
        else:
            processor.process_tweets(status)
            return True

    def on_error(self, status_code):
        # Error handling
        if status_code == 420:
            print('Error: Status Code 420')
            return True