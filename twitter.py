import requests
import time
import main
import config.mongo_setup as mongo_setup
from requests.models import Response
import data.replies_requests as replies_requests
from models import TweetsRequests, RepliesRequests
from vcolors.colors import *

def create_bearer_token(auth_data):
    return auth_data["search_tweets_api"]["bearer_token"]


def get_tweets_count(user, bearer_token):
    '''Returns the tweets count from the last 7 days of a given user'''
    handle = user
    q = f"query=from:{handle} -is:retweet"
    url = f"https://api.twitter.com/2/tweets/counts/recent?{q}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.request("GET", url, headers=headers)
    total_tweet_count = response.json()['meta']['total_tweet_count']
    # print(f' this user has {total_tweet_count} tweets in the last 7 days')
    return total_tweet_count


def get_replies_count(conversation_id):
    mongo_setup.global_init()
    auth_data = main.process_yaml()
    bearer_token = create_bearer_token(auth_data)

    q = f"query=conversation_id:{conversation_id}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    url = f"https://api.twitter.com/2/tweets/counts/recent?{q}"
    response = requests.request("GET", url, headers=headers)
    # print(response.json())
    replies_count = response.json()['meta']['total_tweet_count']
    print(f'there were {replies_count} replies')
    return replies_count


# def get_max_replies(tweets_count):
#     '''returns the max allowed replies given the tweet count from te last 7 days'''
#     max_tt_per_user = 22500
#     max_replies = tweets_count * max_tt_per_user


def tweet_resp_has_next_page():
    obj = TweetsRequests.objects.order_by('-id').first()
    if not obj:
        printW("No last tweet request")
        return None, None
    else:
        if obj.request_meta.next_token != None:
            next_token = obj.request_meta.next_token
            since_id = obj.request_meta.newest_id
            print(
                f'There is a next token in the last tweet request : {next_token}')
            return next_token, since_id
        else:
            printW("No next token in the last tweet request")
            return None, None


def reply_resp_has_next_page():
    obj = RepliesRequests.objects.order_by('-id').first()
    if not obj:
        printW("No last reply request")
        return None, None
    else:
        if obj.request_meta.next_token != None:
            next_token = obj.request_meta.next_token
            since_id = obj.request_meta.newest_id
            print(
                f'There is a next token in the last reply request: {next_token}')
            return next_token, since_id
        else:
            printW("No next token in the last reply request")
            return None, None


def get_user_tweets_url(next_token, since_id, max_tweets, user):
    handle = user
    max_results = max_tweets
    mrf = f"max_results={max_results}"
    q = f"query=from:{handle} -is:retweet"
    if next_token == None:
        printW('No next token for this tweet url')
        url = f"https://api.twitter.com/2/tweets/search/recent?{mrf}&{q}&tweet.fields=lang,created_at,public_metrics,author_id"
        return url
    else:
        nxt = f'&next_token={next_token}'
        sid = f'&since_id={since_id}'
        url = f"https://api.twitter.com/2/tweets/search/recent?{mrf}&{q}&tweet.fields=lang,created_at,public_metrics,author_id{nxt}"
        return url


def get_tweets(bearer_token, url, i):
    print(f'Fetching tweet request {i}')
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.request("GET", url, headers=headers)
    if 'errors' in response.json():
        printFBG(response.json())
    else:
        printSBG(response)
    time.sleep(2.2)
    return response.json()

# ------ Replies ------


def get_replies_ids():
    '''gets the replies ids list from the DB'''
    print('getting replies ids')
    last_request = TweetsRequests.objects.order_by('-id').first()
    return last_request.tweets_with_replies


def get_reply_url(max_replies, conversation_id, reply_next_token):
    base_url = 'https://api.twitter.com/2/tweets/search/recent?'
    max_results = max_replies
    mrf = f"max_results={max_results}"
    q = f"query=conversation_id:{conversation_id}"
    if reply_next_token == None:
        printW('No next token for this reply url')
        url = f'{base_url}{q}&tweet.fields=lang,in_reply_to_user_id,author_id,created_at,conversation_id,public_metrics&{mrf}'
        return url
    else:
        nxt = f'&next_token={reply_next_token}'
        printS(f'There is a next token for this reply url: {reply_next_token}')
        url = f'{base_url}{q}&tweet.fields=lang,in_reply_to_user_id,author_id,created_at,conversation_id,public_metrics&{mrf}{nxt}'
        return url


def get_replies(bearer_token, url, z):
    print(f'Fetching replies {z}')
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.request("GET", url, headers=headers)
    if 'errors' in response.json():
        printFBG(response.json())
    else:
        printSBG(response)
    time.sleep(2.2)
    return response.json()

# def get_replies_urls(replies_ids, max_replies):
#     base_url = 'https://api.twitter.com/2/tweets/search/recent?'
#     max_results = max_replies
#     mrf = f"max_results={max_results}"
#     urls = []
#     for id in replies_ids:
#         q = f"query=conversation_id:{id}"
#         urls.append(f'{base_url}{q}&tweet.fields=lang,in_reply_to_user_id,author_id,created_at,conversation_id,public_metrics&{mrf}')
#     return urls

# def get_reply_next_token_url(reply_next_token, max_replies, id):
#     base_url = 'https://api.twitter.com/2/tweets/search/recent?'
#     max_results = max_replies
#     nxt = f'&next_token={reply_next_token}'
#     mrf = f"max_results={max_results}"
#     q = f"query=conversation_id:{id}"
#     urls = [f'{base_url}{q}&tweet.fields=lang,in_reply_to_user_id,author_id,created_at,conversation_id,public_metrics&{mrf}{nxt}']
#     return urls

# def get_replies(bearer_token, urls, ids, max_replies):
#     print('Fetching replies...')
#     headers = {"Authorization": f"Bearer {bearer_token}"}
#     mrp = max_replies
#     i: int = 0
#     for url,id in zip(urls, ids):
#         response = requests.request("GET", url, headers=headers)
#         response_json = response.json()

#         if 'errors' in response_json:
#             print(response_json)
#         else:
#             print(f'reply {i}',response)
#         replies_requests.create_reply_requests(response_json)

#         n = 1
#         if 'next_token' in response_json['meta']:
#             print('reply',n, 'has a next token')
#             reply_next_token = response_json['meta']['next_token']
#         else:
#             reply_next_token = None
#         while reply_next_token != None and n <= 3:
#             replies_urls = get_reply_next_token_url(reply_next_token, mrp,id)
#             ids = [id]
#             get_replies(bearer_token, replies_urls, ids, mrp)
#             n += 1

#         time.sleep(2.1)
#         i += 1
#     return print('replies saved')
