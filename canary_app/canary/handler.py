from sentiment import Sentiment


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
