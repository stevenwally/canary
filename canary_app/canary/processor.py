from textblob import TextBlob
from canary.views import *
from canary.models import *
from canary.handler import *

handler = Handler()

class Processor(object):

    def __init__(self):

        self.tweet_text = ""
        self.keyword = ""
        self.loc = ""
        self.coords = int()
        self.polarity = 0


    def persist_keyword(self, search_keyword):

        Processor.search_keyword = search_keyword

        UserKeyword.objects.create(
                keyword_name = search_keyword
            )

    def persist_tweet(text, polarity):

        search_keyword = UserKeyword.objects.get(keyword_name = Processor.search_keyword)
        Tweet.objects.create(
                tweet_text = text,
                sent_rating = polarity,
                search_keyword = search_keyword

            )

        handler.set_sentiment(search_keyword)
 

    def process_tweets(self, tweet):

    # assign tweet text
        self.tweet_text = tweet.text

    # assign coordinates
        self.loc = tweet.user.location
        self.coords = tweet.coordinates

    # assign sentiment values
        blob = TextBlob(tweet.text)
        sent = blob.sentiment

        self.polarity = sent.polarity
        # subjectivity = sent.subjectivity

    # process sentiment based on polarity
        # Processor.process_sentiment(self)
        Processor.persist_tweet(self.tweet_text, self.polarity)
