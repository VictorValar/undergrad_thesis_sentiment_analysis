import mongoengine
from mongoengine.fields import IntField

class Tweets(mongoengine.Document):
    tweet_id = mongoengine.IntField()
    author_id  = mongoengine.IntField()
    created_at  = mongoengine.DateField()# 2021-09-05T18:34:04.000Z
    text  = mongoengine.StringField()
    lang  = mongoengine.StringField()
    retweet_count  = mongoengine.IntField()
    reply_count  = mongoengine.IntField()
    like_count  = mongoengine.IntField()
    quote_count  = mongoengine.IntField()

    meta = {
        'db_alias':'core',
        'collection':'tweets'
    }

class TweetsData(mongoengine.EmbeddedDocument):
    pass
     # List of tweet ids
    

class TweetsMeta(mongoengine.EmbeddedDocument):
    next_token = mongoengine.StringField()
    has_next_token = mongoengine.BooleanField(default=False)
    oldest_id = mongoengine.StringField()
    newest_id = mongoengine.StringField()
    result_count = mongoengine.IntField()


class TweetsRequests(mongoengine.Document):
    total_reply_count = mongoengine.IntField(defaut=0)
    tweets_with_replies = mongoengine.ListField(mongoengine.IntField())
    # request_data = mongoengine.EmbeddedDocumentListField(TweetsData)
    request_meta = mongoengine.EmbeddedDocumentField(TweetsMeta)
    meta = {
        'db_alias':'core',
        'collection':'tweets_requests'
    }


# class Replies(mongoengine.Document):

#     id = mongoengine.IntField()
#     conversation_id  = mongoengine.IntField()
#     in_reply_to_user_id  = mongoengine.IntField()
#     created_at  = mongoengine.DateField() # 2021-09-05T18:34:04.000Z
#     text  = mongoengine.StringField()
#     public_metrics  = mongoengine.DictField()
    
#     meta = {
#         'db_alias':'core',
#         'collection':'replies'
#     }  