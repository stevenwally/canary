from canary.models import *

class Handler(object):

    def __init__(self):

        self.positive = 0
        self.negative = 0
        self.neutral = 0

    def set_sentiment(self, keyword):

        search_keyword = UserKeyword.objects.filter(keyword_name = keyword.keyword_name)

        current_tweets = Tweet.objects.filter(search_keyword_id = keyword.pk)

        for tweet in current_tweets:

            if tweet.sent_rating > 0:
                self.positive += 1
            elif tweet.sent_rating < 0:
                self.negative += 1
            else:
                self.neutral += 1

    def get_data(self):

        return Tweet.objects.all()



