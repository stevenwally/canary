from processor import *
from tweepy.streaming import StreamListener


class Listener(StreamListener):
    def __init__(self, processor=None, *args, **kwargs):
        super(Listener, self).__init__(*args, **kwargs)
        self.processor = processor

    def on_status(self, tweet):
        # Get/process tweets on arrival.
        if self.processor:
            self.processor.process_tweet(tweet)
        # if 'RT @' in status.text:
        #     return
        # else:
        #     processor.process_tweets(status)
        #     return True

    def on_error(self, status_code):
        # Error handling
        if status_code == 420:
            print('Error: Status Code 420')
            return False
