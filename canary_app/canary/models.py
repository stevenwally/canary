from django.db import models

class UserKeyword(models.Model):
    keyword_name = models.CharField(max_length=50, null=True, unique=True)



class Tweet(models.Model):
    """
        Contains pertinent data to tweets streamed from the Twitter API.
    """
    tweet_text = models.CharField(max_length=140, default='No Tweet Data. Weird.')
    search_keyword = models.ForeignKey(UserKeyword, null=True, on_delete=models.CASCADE)
    sent_rating = models.DecimalField(max_digits=19, decimal_places=10)
