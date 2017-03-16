from canary.models import *

class Handler(object):

    def __init__(self):

        self.positive = 0
        self.negative = 0
        self.neutral = 0
        self.positive_tweets = []
        self.negative_tweets = []
        self.neutral_tweets = []
        self.location = []


    def clear_handler(self):
        self.positive = 0
        self.negative = 0
        self.neutral = 0
        self.positive_tweets = []
        self.negative_tweets = []
        self.neutral_tweets = []

    def set_tweet(self, text, polarity):

        if polarity > 0:
            self.positive_tweets.append(text)
        elif polarity < 0:
            self.negative_tweets.append(text)
        else:
            self.neutral_tweets.append(text)


    def set_sentiment(self, polarity):

        # search_keyword = UserKeyword.objects.filter(keyword_name = keyword.keyword_name)

        # current_tweets = Tweet.objects.filter(search_keyword_id = keyword.pk)

        # for tweet in current_tweets:

        if polarity > 0:
            self.positive += 1
        elif polarity < 0:
            self.negative += 1
        else:
            self.neutral += 1

    def get_data(self):

        return {'positive': self.positive,
                'negative': self.negative, 
                'neutral': self.neutral,
                'positive_tweets': self.positive_tweets,
                'negative_tweets': self.negative_tweets,
                'neutral_tweets': self.neutral_tweets
                }




