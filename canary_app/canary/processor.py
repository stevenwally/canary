from textblob import TextBlob
from sentiment import Sentiment


class Processor(object):
    def __init__(self):
        self.data = {
            'text': None,
            'keyword': None,
            'loc': None,
            'polarity': 0,
            'positive': Sentiment(),
            'negative': Sentiment(),
            'neutral': Sentiment()
        }

    def clear(self):
        self.__init__()

    def _increment_sentiment(self, polarity):
        if polarity > 0:
            self.data['positive'].increment_sentiment_value()
        elif polarity < 0:
            self.data['negative'].increment_sentiment_value()
        else:
            self.data['neutral'].increment_sentiment_value()

    def set_origin(self, origin, polarity):
        if polarity > 0:
            self.data['positive'].add_origin(origin)
        elif polarity < 0:
            self.data['negative'].add_origin(origin)
        else:
            self.data['neutral'].add_origin(origin)

    def set_keyword(self, keyword):
        self.data['positive'].set_keyword(keyword)
        self.data['negative'].set_keyword(keyword)
        self.data['neutral'].set_keyword(keyword)

    def _set_tweet_text(self, text, polarity):
        if polarity > 0:
            self.data['positive'].add_tweet(text)
        elif polarity < 0:
            self.data['negative'].add_tweet(text)
        else:
            self.data['neutral'].add_tweet(text)

    def _determine_set_percentage(self, sentiment):
        # TODO: This calculation should be broken out into another function. Way too messy.
        total_value = sum([self.data['positive'].get_sentiment_value(),
                           self.data['negative'].get_sentiment_value(),
                           self.data['neutral'].get_sentiment_value()])

        sentiment.set_percentage(round(sentiment.get_sentiment_value() / total_value * 100, 1))

    def get_data(self):
        return self.data

    def process_tweet(self, tweet):
        """

        :param tweet:
        :return:
        """

        # assign tweet text
        self.data['text'] = tweet.text

        # assign sentiment values
        sentiment = TextBlob(self.data['text']).sentiment
        self.data['polarity'] = sentiment.polarity

        self._increment_sentiment(self.data['polarity'])
        self._set_tweet_text(self.data['text'], self.data['polarity'])

        self._determine_set_percentage(self.data['positive'])
        self._determine_set_percentage(self.data['negative'])
        self._determine_set_percentage(self.data['neutral'])

        if tweet.place is not None:
            if tweet.place.country_code is not None:
                self.data['loc'] = tweet.place.country_code
            elif tweet.place.country is not None:
                self.data['loc'] = tweet.place.country
            else:
                self.data['loc'] = 'Unknown Origin'
        elif tweet.user.location is not None:
            self.data['loc'] = tweet.user.location
        else:
            self.data['loc'] = 'Unknown Origin'

        self.set_origin(self.data['loc'], self.data['polarity'])
