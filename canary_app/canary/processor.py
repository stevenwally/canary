from textblob import TextBlob
from views import *
from handler import *

handler = Handler()


class Processor(object):
    def __init__(self):
        self.tweet_text = None
        self.keyword = None
        self.loc = None
        self.coords = None
        self.polarity = 0
        self.top_rt = None
        self.rt_count = 0

    def process_tweet(self, tweet):
        """

        :param tweet:
        :return:
        """

    # assign tweet text
        self.tweet_text = tweet.text

    # assign sentiment values
        sentiment = TextBlob(tweet.text).sentiment
        self.polarity = sentiment.polarity

        handler.set_sentiment(self.polarity)
        handler.set_tweet(self.tweet_text, self.polarity)
        handler.set_percentage()

        if tweet.place is not None:
            if tweet.place.country_code is not None:
                self.loc = tweet.place.country_code
            elif tweet.place.country is not None:
                self.loc = tweet.place.country
            else:
                self.loc = "Unknown Location"
        elif tweet.user.location is not None:
            self.loc = tweet.user.location
        else:
            self.loc = "Unknown Location"

        handler.set_location(self.loc, self.polarity)
