from django.db import models

class UserKeyword(models.Model):
    keyword_name = models.CharField(max_length=50, null=True)


class Tweet(models.Model):
    """
        Contains pertinent data to tweets streamed from the Twitter API.
    """
    tweet_text = models.CharField(max_length=140, default='No Tweet Data. Weird.')
    sent_rating = models.DecimalField(max_digits=19, decimal_places=10)
    origin = models.CharField(max_length=140, null=True, default='No Location data. Weird.')
    search_keyword = models.ForeignKey(UserKeyword, null=True, on_delete=models.CASCADE)
    
