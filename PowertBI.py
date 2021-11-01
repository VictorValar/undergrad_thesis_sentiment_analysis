#Power BI Export

import importlib.util
spec = importlib.util.spec_from_file_location("MongoTwitter.models", r"C:\Users\victor.santos2\OneDrive - Grupo Marista\TCC\Twitter Sentiment Analysis\MongoTwitter\models.py")
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)
import pandas as pd
import mongoengine

mongoengine.register_connection(alias='core',name='sentimentAnalysis')
#1

candidates = [('lhmandetta',2726301380,'Mandetta'),
('EduardoLeite_',123891446,'Eduardo Leite'),
('DatenaOficial',68722955, 'Datena'),
('cirogomes',33374761, 'Ciro Gomes'),
('jdoriajr',64706049, 'Dória'),
('LulaOficial',2670726740,'Lula'),
('jairbolsonaro',128372940, 'Bolsonaro'),]
can_df = pd.DataFrame(data=candidates, columns=['Handle', 'author_id','Name'])
#2

objs_tweets = models.Tweets.objects().all().values_list('id', 'tweet_id','author_id','created_at','text','lang','retweet_count','reply_count','like_count','quote_count')
tweets = pd.DataFrame.from_records(data=objs_tweets, columns=['id','tweet_id','author_id','created_at','text','lang','retweet_count','reply_count','like_count','quote_count'])
tweets_df = tweets
tweets = tweets.drop(columns=['id','created_at','text','lang','retweet_count','reply_count','like_count','quote_count'])
tweets = tweets.rename(columns={"tweet_id": "conversation_id"})
tweets = pd.merge(tweets,can_df, how='left')
# tweets = tweets.merge(can_df)
tweets = tweets.drop(columns=['author_id'])
#3

tweets_sentiments = models.TweetsSentiment.objects.all().values_list('tweet_id','length','sentiment', 'negative','positive', 'neutral','clean_text')
tweets_sentiments_df = pd.DataFrame.from_records(data=tweets_sentiments, columns=['tweet_id','length','sentiment', 'negative','positive', 'neutral','clean_text'])
tweets_df = pd.merge(tweets_df,tweets_sentiments_df)
#4

objs_replies = models.Replies.objects.all().values_list('id','reply_id', 'in_reply_to_user_id', 'conversation_id' ,'author_id','created_at','text','lang','retweet_count','reply_count','like_count','quote_count')
replies_df = pd.DataFrame.from_records(data=objs_replies, columns=['id','reply_id', 'in_reply_to_user_id', 'conversation_id' ,'author_id','created_at','text','lang','retweet_count','reply_count','like_count','quote_count'])
#5

replies_sentiments = models.RepliesSentiment.objects.all().values_list('reply_id','length','sentiment', 'negative','positive', 'neutral','clean_text')
replies_sentiments_df = pd.DataFrame.from_records(data=replies_sentiments, columns=['reply_id','length','sentiment', 'negative','positive', 'neutral','clean_text'])
replies_df = replies_df.merge(replies_sentiments_df)
#6

replies_df = replies_df.merge(tweets)
tweets_df = tweets_df.merge(can_df)
exclude_tweets = [1440468001661198346,1440355742372937731,1440272143254581249,1440259056925511684,1435367536015593486,1435349563062243331]
for i in exclude_tweets:
    replies_df = replies_df.drop(replies_df[replies_df.conversation_id == i].index)
#7

obj_summa = models.Summarizations.objects.all().values_list('summarization_id','text', 'rankScore')
summs = pd.DataFrame(data=obj_summa, columns=['summarization_id','text', 'rankScore'])
summs_df = summs.rename(columns={"summarization_id": "tweet_id",'text':'summ_text'})
#8