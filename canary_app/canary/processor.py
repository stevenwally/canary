from textblob import TextBlob
from views import *
from models import *
from handler import *

handler = Handler()


class Processor(object):

    def __init__(self):

        self.tweet_text = ""
        self.keyword = ""
        self.loc = ""
        self.coords = int()
        self.polarity = 0
        self.top_rt = ""
        self.rt_count = 0

    @staticmethod
    def persist_keyword(search_keyword):
        """

        :param search_keyword:
        :return:
        """
        Processor.search_keyword = search_keyword
        UserKeyword.objects.get_or_create(keyword_name=search_keyword)

    def persist_tweet(self, text, polarity, location):
        """

        :param text:
        :param polarity:
        :param location:
        :return:
        """
        search_keyword = UserKeyword.objects.get(keyword_name=self.keyword)
        Tweet.objects.create(
                tweet_text=text,
                sent_rating=polarity,
                origin=location,
                search_keyword=search_keyword
            )

    def process_tweets(self, tweet):
        """

        :param tweet:
        :return:
        """

    # assign tweet text
        self.tweet_text = tweet.text
        print self.tweet_text

    # assign sentiment values
        blob = TextBlob(tweet.text)
        sent = blob.sentiment
        self.polarity = sent.polarity

        handler.set_sentiment(self.polarity)
        handler.set_tweet(self.tweet_text, self.polarity)
        handler.set_percentage()

        print(tweet.user.followers_count)
        print(tweet.user.favourites_count)

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

        # Processor.persist_tweet(self.tweet_text, self.polarity, self.loc)
