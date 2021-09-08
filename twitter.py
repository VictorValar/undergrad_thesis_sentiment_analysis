import requests
from models import TweetsRequests

def create_bearer_token(auth_data):
    return auth_data["search_tweets_api"]["bearer_token"]

def has_next_token():
    obj = TweetsRequests.objects.order_by('-id').first()
    if not obj:
        print("No next token")
        return None,None
    else:
        next_token = obj.request_meta.next_token
        since_id = obj.request_meta.newest_id
        print(f'There is a next token: {next_token}')
        return next_token,since_id

def get_user_tweets_url(next_token,since_id):
    handle = "BolsonaroSP"
    max_results = 10
    mrf = f"max_results={max_results}"
    q = f"query=from:{handle} -is:retweet"
    if next_token == None:
        print('No next token detected')
        url = f"https://api.twitter.com/2/tweets/search/recent?{mrf}&{q}&tweet.fields=lang,created_at,public_metrics,author_id"
        return url
    else:
        nxt = f'&next_token={next_token}'
        sid = f'&since_id={since_id}'
        url = f"https://api.twitter.com/2/tweets/search/recent?{mrf}&{q}&tweet.fields=lang,created_at,public_metrics,author_id{nxt}"
        return url

def get_tweets(bearer_token, url):
    print('Fetching tweets...')
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.request("GET", url, headers=headers)
    if 'errors' in response.json():
        print(response.json())
    else:
        print(response)
    return response.json()