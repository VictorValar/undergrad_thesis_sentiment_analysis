import config.mongo_setup as mongo_setup
import data.tweets_requests as tweets_requests
import yaml
import twitter

def main():
    mongo_setup.global_init()
    auth_data = process_yaml()
    #Twitter steps
    bearer_token = twitter.create_bearer_token(auth_data)
    next_token,since_id = twitter.has_next_token()
    url = twitter.get_user_tweets_url(next_token,since_id)
    tt_json_resp = twitter.get_tweets(bearer_token, url)
    tweets_requests.create_tt_request(tt_json_resp)

def process_yaml():
    with open("config/config.yaml") as file:
        return yaml.safe_load(file)



if __name__ == "__main__":
    main()