from models import *


class Handler(object):

    def __init__(self):

        self.positive = {
                        'keyword': "",
                        'sentiment': 0,
                        'tweets': [],
                        'location': [],
                        'percentage': 0,
                        'rt_count': 0,
                        'top_rt': ""
                        }
        self.negative = {
                        'sentiment': 0,
                        'tweets': [],
                        'location': [],
                        'percentage': 0,
                        }
        self.neutral = {
                        'sentiment': 0,
                        'tweets': [],
                        'location': [],
                        'percentage': 0,
                        }

    def clear_handler(self):
        self.positive = {
                        'sentiment': 0,
                        'tweets': [],
                        'location': [],
                        'percentage': 0,
                        }
        self.negative = {
                        'sentiment': 0,
                        'tweets': [],
                        'location': [],
                        'percentage': 0,
                        }
        self.neutral = {
                        'sentiment': 0,
                        'tweets': [],
                        'location': [],
                        'percentage': 0,
                        }

    def set_keyword(self, keyword):

        self.positive['keyword'] = keyword
        self.neutral['keyword'] = keyword
        self.negative['keyword'] = keyword

    def set_tweet(self, text, polarity):

        if polarity > 0:
            self.positive['tweets'].append(text)
        elif polarity < 0:
            self.negative['tweets'].append(text)
        else:
            self.neutral['tweets'].append(text)

    def set_top_rt(self, text, count, polarity):

        if polarity > 0:
            self.positive['rt_count'] = count
            self.positive['top_rt'] = text
        elif polarity < 0:
            self.negative['rt_count'] = count
            self.negative['top_rt'] = text
        else:
            self.neutral['rt_count'] = count
            self.neutral['top_rt'] = text

    def set_sentiment(self, polarity):

        if polarity > 0:
            self.positive['sentiment'] += 1
        elif polarity < 0:
            self.negative['sentiment'] += 1
        else:
            self.neutral['sentiment'] += 1

    def set_percentage(self):

        self.positive['percentage'] = round(self.positive['sentiment'] / (self.positive['sentiment'] + self.negative['sentiment'] + self.neutral['sentiment']) * 100, 1)
        self.negative['percentage'] = round(self.negative['sentiment'] / (self.positive['sentiment'] + self.negative['sentiment'] + self.neutral['sentiment']) * 100, 1)
        self.neutral['percentage'] = round(self.neutral['sentiment'] / (self.positive['sentiment'] + self.negative['sentiment'] + self.neutral['sentiment']) * 100, 1)

    def set_location(self, location, polarity):

        if polarity > 0:
            self.positive['location'].append(location)
        elif polarity < 0:
            self.negative['location'].append(location)
        else:
            self.neutral['location'].append(location)

    def get_data(self):

        return {'positive': self.positive,
                'negative': self.negative, 
                'neutral': self.neutral,
                }
