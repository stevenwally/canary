from processor import *
from tweepy.streaming import StreamListener

processor = Processor()


class Listener(StreamListener):

    def on_status(self, tweet):
        # Get tweets, send to processor
        print tweet
        processor.process_tweet(tweet)
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
