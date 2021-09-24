from models import TweetsRequests, Tweets, TweetsMeta, RepliesRequests
from datetime import datetime
import twitter
from vcolors.colors import * # custom module for printing colored text in terminal

def create_tt_request(tt_json_resp) -> TweetsRequests:
    if 'next_token' in tt_json_resp['meta']:
            nxt = tt_json_resp['meta']['next_token']
    else:
        nxt = ''
    if not TweetsRequests.objects(request_meta__next_token=nxt).first():
        request = TweetsRequests()

        tweet_meta_obj = TweetsMeta()
        tweet_meta_obj.result_count = tt_json_resp['meta']['result_count']
        print(f'tweets in response:{tweet_meta_obj.result_count}')
        if 'next_token' in tt_json_resp['meta']:
            tweet_meta_obj.next_token = tt_json_resp['meta']['next_token']
        if 'oldest_id' in tt_json_resp['meta']:
            tweet_meta_obj.oldest_id = tt_json_resp['meta']['oldest_id']
        if 'newest_id' in tt_json_resp['meta']:
            tweet_meta_obj.newest_id = tt_json_resp['meta']['newest_id']
        request.request_meta = tweet_meta_obj

        # tweet_data_obj = TweetsData()
        request.total_reply_count = 0
        
        for tweet in tt_json_resp['data']:
            if not Tweets.objects(tweet_id=tweet['id']).first():
                tweet_obj = Tweets()
                tweet_obj.tweet_id = tweet['id']
                tweet_obj.author_id = tweet['author_id']
                tweet_obj.created_at = datetime.strptime(tweet['created_at'][0:19], '%Y-%m-%dT%H:%M:%S')
                tweet_obj.text = tweet['text']
                tweet_obj.lang = tweet['lang']
                tweet_obj.retweet_count = tweet['public_metrics']['retweet_count']
                tweet_obj.reply_count = tweet['public_metrics']['reply_count']
                tweet_obj.like_count = tweet['public_metrics']['like_count']
                tweet_obj.quote_count = tweet['public_metrics']['quote_count']
                tweet_obj.save()
                if tweet['public_metrics']['reply_count'] != 0:
                    if twitter.get_replies_count(tweet['id']) != 0:
                        request.total_reply_count += tweet['public_metrics']['reply_count']
                        request.tweets_with_replies.append(tweet['id'])
            else:
                printW('tweet already exist')
                if tweet['public_metrics']['reply_count'] != 0:
                    if twitter.get_replies_count(tweet['id']) != 0:
                        request.total_reply_count += tweet['public_metrics']['reply_count']
                        request.tweets_with_replies.append(tweet['id'])

        print(f'there are {request.total_reply_count} replies')
        print(f'Tweets with replies: {len(request.tweets_with_replies)}')

        request.save()
    else:
        printW('tweet request already exists')
    

