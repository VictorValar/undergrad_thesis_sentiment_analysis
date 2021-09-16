from models import RepliesRequests, RepliesMeta, Replies
from datetime import datetime
from vcolors.colors import *

def create_reply_requests(replies_json_resp) -> RepliesRequests:
    if 'next_token' in replies_json_resp['meta']:
            nxt = replies_json_resp['meta']['next_token']
    else:
        nxt = ''
    if not RepliesRequests.objects(request_meta__next_token=nxt).first():
        request = RepliesRequests()

        tweet_meta_obj = RepliesMeta()
        tweet_meta_obj.result_count = replies_json_resp['meta']['result_count']
        print(f'replies in response:{tweet_meta_obj.result_count}')
        if replies_json_resp['meta']['result_count'] == 0:
            printF(replies_json_resp)
        if 'next_token' in replies_json_resp['meta']:
            tweet_meta_obj.next_token = replies_json_resp['meta']['next_token']
        if 'oldest_id' in replies_json_resp['meta']:
            tweet_meta_obj.oldest_id = replies_json_resp['meta']['oldest_id']
        if 'newest_id' in replies_json_resp['meta']:
            tweet_meta_obj.newest_id = replies_json_resp['meta']['newest_id']
        request.request_meta = tweet_meta_obj
        
        for tweet in replies_json_resp['data']:
            if not Replies.objects(reply_id=tweet['id']).first():
                tweet_obj = Replies()
                tweet_obj.reply_id = tweet['id']
                tweet_obj.author_id = tweet['author_id']
                tweet_obj.in_reply_to_user_id = tweet['in_reply_to_user_id']
                tweet_obj.conversation_id = tweet['conversation_id']
                tweet_obj.created_at = datetime.strptime(tweet['created_at'][0:19], '%Y-%m-%dT%H:%M:%S')
                tweet_obj.text = tweet['text']
                tweet_obj.lang = tweet['lang']
                tweet_obj.retweet_count = tweet['public_metrics']['retweet_count']
                tweet_obj.reply_count = tweet['public_metrics']['reply_count']
                tweet_obj.like_count = tweet['public_metrics']['like_count']
                tweet_obj.quote_count = tweet['public_metrics']['quote_count']
                tweet_obj.save()
            else:
                printW('reply already exist')

        request.save()
    else:
        printW('reply request already exist')

