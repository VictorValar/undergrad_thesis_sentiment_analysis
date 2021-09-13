import config.mongo_setup as mongo_setup
import data.tweets_requests as tweets_requests
import data.replies_requests as replies_requests
import yaml
import twitter

max_tweets, max_replies = 100, 100
user = "cirogomes"  

def main():
    mongo_setup.global_init()
    auth_data = process_yaml()
    # Twitter steps
    bearer_token = twitter.create_bearer_token(auth_data)
    tweet_next_token, since_id = None, None
    
    i = 1 
    while (tweet_next_token != None and i <= 3) or i == 1:
        url = twitter.get_user_tweets_url(tweet_next_token, since_id, max_tweets, user)
        tt_json_resp = twitter.get_tweets(bearer_token, url,i)
        tweets_requests.create_tt_request(tt_json_resp)
        tweet_next_token, since_id = twitter.tweet_resp_has_next_page()
        print(f'tweet request {i} saved') 
        # replies steps
        replies_ids = twitter.get_replies_ids()
        z = 1
        for conversation_id in replies_ids:
            reply_next_token, reply_since_id = None, None
            n = 1            
            while (tweet_next_token != None and n <= 3) or n == 1:
                reply_url = twitter.get_reply_url(max_replies, conversation_id,reply_next_token)
                replies_json_resp = twitter.get_replies(bearer_token, reply_url,z)
                replies_requests.create_reply_requests(replies_json_resp)
                print(f'reply {z} page {n} saved')
                reply_next_token, reply_since_id = twitter.reply_resp_has_next_page()
                n += 1
            z += 1     
        i += 1
    print('--- END ---')

def process_yaml():
    with open("config/config.yaml") as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    main()
