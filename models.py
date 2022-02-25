import mongoengine

class RepliesSentiment(mongoengine.Document):
    reply_id = mongoengine.IntField(unique=True)
    length = mongoengine.IntField()
    sentiment = mongoengine.StringField()
    negative = mongoengine.FloatField()
    positive = mongoengine.FloatField()
    neutral = mongoengine.FloatField()
    clean_text = mongoengine.StringField()

    meta = {
        'db_alias': 'core',
        'collection': 'replies_sentiment'
    }

class TweetsSentiment(mongoengine.Document):
    tweet_id = mongoengine.IntField(unique=True)
    length = mongoengine.IntField()
    sentiment = mongoengine.StringField()
    negative = mongoengine.FloatField()
    positive = mongoengine.FloatField()
    neutral = mongoengine.FloatField()
    clean_text = mongoengine.StringField()

    meta = {
        'db_alias': 'core',
        'collection': 'tweets_sentiment'
    }

class Tweets(mongoengine.Document):
    tweet_id = mongoengine.IntField(unique=True)
    author_id = mongoengine.IntField()
    created_at = mongoengine.DateTimeField()  # 2021-09-05T18:34:04.000Z
    text = mongoengine.StringField()
    lang = mongoengine.StringField()
    retweet_count = mongoengine.IntField()
    reply_count = mongoengine.IntField()
    like_count = mongoengine.IntField()
    quote_count = mongoengine.IntField()
    # request = mongoengine.LazyReferenceField('TweetsRequests',dbref=False, reverse_delete_rule=CASCADE )

    meta = {
        'db_alias': 'core',
        'collection': 'tweets'
    }
class Replies(mongoengine.Document):
    reply_id = mongoengine.IntField(unique=True)
    author_id = mongoengine.IntField()
    in_reply_to_user_id = mongoengine.IntField()
    conversation_id = mongoengine.IntField()
    created_at = mongoengine.DateTimeField()  # 2021-09-05T18:34:04.000Z
    text = mongoengine.StringField()
    lang = mongoengine.StringField() #
    retweet_count = mongoengine.IntField()
    reply_count = mongoengine.IntField()
    like_count = mongoengine.IntField()
    quote_count = mongoengine.IntField()

    meta = {
        'db_alias': 'core',
        'collection': 'replies'
    }


class TweetsMeta(mongoengine.EmbeddedDocument):
    next_token = mongoengine.StringField()
    oldest_id = mongoengine.IntField()
    newest_id = mongoengine.IntField()
    result_count = mongoengine.IntField()

class RepliesMeta(mongoengine.EmbeddedDocument):
    next_token = mongoengine.StringField()
    oldest_id = mongoengine.IntField()
    newest_id = mongoengine.IntField()
    result_count = mongoengine.IntField()

# class SummarizationSentence(mongoengine.EmbeddedDocument):
#     text = mongoengine.StringField()
#     rankScore = mongoengine.FloatField()

class Summarizations(mongoengine.Document):
    summarization_id = mongoengine.IntField()
    text = mongoengine.StringField(unique=True)
    rankScore = mongoengine.FloatField()
    # job_id = mongoengine.StringField(unique=True)
    # sentences = mongoengine.EmbeddedDocumentListField(SummarizationSentence)
    
    meta = {
        'db_alias': 'core',
        'collection': 'extractive_summarization'
    }

class TweetsRequests(mongoengine.Document):
    total_reply_count = mongoengine.IntField(defaut=0)
    tweets_with_replies = mongoengine.ListField(mongoengine.IntField())
    request_meta = mongoengine.EmbeddedDocumentField(TweetsMeta)
    meta = {
        'db_alias': 'core',
        'collection': 'tweets_requests'
    }

class RepliesRequests(mongoengine.Document):
    request_meta = mongoengine.EmbeddedDocumentField(RepliesMeta)
    meta = {
        'db_alias': 'core',
        'collection': 'replies_requests'
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
