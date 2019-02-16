class Sentiment(object):

    def __init__(self):
        self.sentiment_value = 0
        self.tweets = []
        self.origins = []
        self.percentage = None
        self.keyword = None

    def get_sentiment_value(self):
        return self.sentiment_value

    def set_sentiment_value(self, value):
        self.sentiment_value = value

    def increment_sentiment_value(self):
        self.sentiment_value += 1

    def get_tweets(self):
        return self.tweets

    def add_tweet(self, tweet):
        self.tweets.append(tweet)

    def get_origins(self):
        return self.origins

    def add_origin(self, location):
        self.origins.append(location)

    def get_percentage(self):
        return self.percentage

    def set_percentage(self, value):
        self.percentage = value

    def get_keyword(self):
        return self.keyword

    def set_keyword(self, keyword):
        self.keyword = keyword

    def clear(self):
        self.__init__()