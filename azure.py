import requests
import yaml
from vcolors.colors import *
import config.mongo_setup as mongo_setup
from models import Tweets, Replies
import time
from data.replies_azure import save_replies_sentiment_analysis
import re

def main():
    sentiment_url, azure_header = connect_azure()
    replies_sentiment_analysis(azure_header, sentiment_url)

def replies_sentiment_analysis(azure_header, sentiment_url):
    '''Gets the replies from the DB, cleans the data and sends it to Azure, afterwards calls save_replies_sentiment_analysis to save the Azure responso to the DB'''
    mongo_setup.global_init()
    replies = Tweets.objects[:10]
    documents = {'documents':[]}
    reply_counter = 1
    batch_counter = 1
    for reply in replies:
        if reply.lang == 'und':
            lang = 'pt'
        clean_text = clear_text(reply.text)
        formatted_reply = {'id':reply.tweet_id,'text':clean_text,'language':lang} 
        documents['documents'].append(formatted_reply)
        print(f"reply {reply_counter} added to documents")
        if reply_counter % 10 == 0:
            response = requests.post(sentiment_url, headers=azure_header, json=documents)
            time.sleep(1.5)
            documents = {'documents':[]}
            try:
                response.json()['documents']
                printS(f"Bacth {batch_counter} analysed")
                save_replies_sentiment_analysis(response.json(),batch_counter)
                batch_counter += 1
                if response.json()['errors'] != []:
                    printW(response.json()['errors'])
            except KeyError:
                printF(response.json()['error'])
            
        reply_counter += 1
    return 
def clear_text(text) -> str:
    '''Removes new lines, twitter handles, hashtags and links'''
    clean_text = text
    clean_text = clean_text.lower()
    
    #handles and hashtags:
    clean_text = re.sub('(?<=^|(?<=[^a-zA-Z0-9-_\.]))(#|@)([A-Za-z]+[A-Za-z0-9-_]+)','',clean_text)
    
    #URLs:
    clean_text = re.sub('http\S+','',clean_text)
    
    #new lines:
    clean_text = re.sub('(\r\n|\n|\r|\\n)','',clean_text)
    return clean_text

def connect_azure():
    '''Gets Azure auth data'''
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
