import requests
import yaml
from vcolors.colors import *
import config.mongo_setup as mongo_setup
from models import Tweets, Replies
import time
from data.replies_azure import save_replies_sentiment_analysis

def main():
    sentiment_url, azure_header = connect_azure()
    replies_sentiment_analysis(azure_header, sentiment_url)

def replies_sentiment_analysis(azure_header, sentiment_url):
    mongo_setup.global_init()
    replies = Replies.objects[:10]
    documents = {'documents':[]}
    reply_counter = 1
    batch_counter = 1
    for reply in replies:
        if reply.lang == 'und':
            lang = 'pt'
        formatted_reply = {'id':reply.reply_id,'text':reply.text,'language':lang} 
        documents['documents'].append(formatted_reply)
        print(f"reply {reply_counter} added to documents")
        if reply_counter % 10 == 0:
            response = requests.post(sentiment_url, headers=azure_header, json=documents)
            time.sleep(1.5)
            documents = {'documents':[]}
            
            if response.json()['errors'] == []:
                printS(f"bacth {batch_counter} analysed")
                save_replies_sentiment_analysis(response.json(),batch_counter)
            else:
                printF(response.json()['errors'])
            batch_counter += 1
        reply_counter += 1
    return 

def connect_azure():
    auth = process_yaml()
    azure_url = auth["azure"]["endpoint"]
    sentiment_url = f"{azure_url}text/analytics/v3.1/sentiment"
    subscription_key = auth["azure"]["subscription_key"]
    azure_header = {"Ocp-Apim-Subscription-Key": subscription_key}
    return sentiment_url, azure_header


def process_yaml():
    with open("config/config.yaml") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    main()
