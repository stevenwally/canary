
class Sentiment(object):

    def __init__(self):
        self.sentiment_value = 0
        self.tweets = []
        self.location = []
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

    def get_location(self):
        return self.location

    def add_location(self, location):
        self.location.append(location)

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


class Handler(object):

    def __init__(self):
        self.positive = Sentiment()
        self.negative = Sentiment()
        self.neutral = Sentiment()

    def clear_handler(self):
        self.positive.clear()
        self.negative.clear()
        self.neutral.clear()

    def set_keyword(self, keyword):

        self.positive.set_keyword(keyword)
        self.negative.set_keyword(keyword)
        self.neutral.set_keyword(keyword)

    def set_tweet(self, text, polarity):

        if polarity > 0:
            self.positive.add_tweet(text)
        elif polarity < 0:
            self.negative.add_tweet(text)
        else:
            self.neutral.add_tweet(text)

    # def set_top_rt(self, text, count, polarity):
    #
    #     if polarity > 0:
    #         self.positive['rt_count'] = count
    #         self.positive['top_rt'] = text
    #     elif polarity < 0:
    #         self.negative['rt_count'] = count
    #         self.negative['top_rt'] = text
    #     else:
    #         self.neutral['rt_count'] = count
    #         self.neutral['top_rt'] = text

    def set_sentiment(self, polarity):

        if polarity > 0:
            self.positive.increment_sentiment_value()
        elif polarity < 0:
            self.negative.increment_sentiment_value()
        else:
            self.neutral.increment_sentiment_value()

    def set_percentage(self):

        self.positive.set_percentage(round(self.positive.get_sentiment_value() / (self.positive.get_sentiment_value() + self.negative.get_sentiment_value() + self.neutral.get_sentiment_value()) * 100, 1))
        self.negative.set_percentage(round(self.negative.get_sentiment_value() / (self.positive.get_sentiment_value() + self.negative.get_sentiment_value() + self.neutral.get_sentiment_value()) * 100, 1))
        self.neutral.set_percentage(round(self.neutral.get_sentiment_value() / (self.positive.get_sentiment_value() + self.negative.get_sentiment_value() + self.neutral.get_sentiment_value()) * 100, 1))

    def set_location(self, location, polarity):

        if polarity > 0:
            self.positive.add_location(location)
        elif polarity < 0:
            self.negative.add_location(location)
        else:
            self.neutral.add_location(location)

    def get_data(self):
        return {'positive': self.positive,
                'negative': self.negative, 
                'neutral': self.neutral}
