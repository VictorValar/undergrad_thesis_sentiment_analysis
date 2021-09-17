import requests
import yaml
from vcolors.colors import *
import config.mongo_setup as mongo_setup
from models import Tweets, Replies, TweetsSentiment, RepliesSentiment
import time
from data.replies_azure import save_replies_sentiment_analysis
from data.tweets_azure import save_tweets_sentiment_analysis
import re
import sys
import os
os.chdir(r"C:\Users\victor.santos2\OneDrive - Grupo Marista\TCC\Twitter Sentiment Analysis\MongoTwitter")
output = open("azure_output.out", 'w')

fetch_tweets, fetch_replies = False, True

def main():
    mongo_setup.global_init()
    sentiment_url, azure_header = connect_azure()
    if  fetch_replies and fetch_tweets == True:
        replies_sentiment_analysis(azure_header, sentiment_url)
        tweets_sentiment_analysis(azure_header, sentiment_url)
    elif fetch_tweets == True and fetch_replies == False:
        tweets_sentiment_analysis(azure_header, sentiment_url)
    else:
        replies_sentiment_analysis(azure_header, sentiment_url)
    printSBG('--- END ---')
    sys.stdout = output
    output.close()

def replies_sentiment_analysis(azure_header, sentiment_url):
    '''Gets the replies from the DB, cleans the data and sends it to Azure, afterwards calls save_replies_sentiment_analysis to save the Azure responso to the DB'''
    replies = Replies.objects.all()
    documents = {'documents':[]}
    reply_counter = 1
    batch_counter = 1
    for reply in replies:
        if not RepliesSentiment.objects.filter(reply_id=reply.reply_id).first():
            
            clean_text,no_text = clear_text(reply.text)
            
            if no_text == True:
                printWBG(f'Reply {reply.reply_id} has no text')
                continue
            
            if reply.lang == 'und' or reply.lang == 'pt':
                lang = 'pt-BR'

            formatted_reply = {'id':reply.reply_id,'text':clean_text,'language':lang} 
            documents['documents'].append(formatted_reply)
            print(f"reply {reply_counter} added to documents")

            if reply_counter % 10 == 0:
                response = requests.post(sentiment_url, headers=azure_header, json=documents)
                time.sleep(0.7)
                documents = {'documents':[]}
                try:
                    response.json()['documents']
                    printS(f"replies bacth {batch_counter} sent to Azure")
                    save_replies_sentiment_analysis(response.json(),batch_counter)
                    batch_counter += 1
                    if response.json()['errors'] != []:
                        printW(response.json()['errors'])
                        printWBG(f'reply text:{clean_text}')
                except KeyError:
                    printF(response.json()['error'])
                
            reply_counter += 1
        else:
            printW(f'Reply Sentiment {reply.reply_id} alredy exists')

def tweets_sentiment_analysis(azure_header, sentiment_url):
    '''Gets the tweets from the DB, cleans the data and sends it to Azure, afterwards calls save_tweets_sentiment_analysis to save the Azure responso to the DB'''
    tweets = Tweets.objects.all()
    documents = {'documents':[]}
    tweet_counter = 1
    batch_counter = 1
    for tweet in tweets:
        if not TweetsSentiment.objects.filter(tweet_id=tweet.tweet_id).first():
            
            clean_text,no_text = clear_text(tweet.text)
            
            if no_text == True:
                printWBG(f'Tweet {tweet.tweet_id} has no text')
                continue
            
            if tweet.lang == 'und' or tweet.lang == 'pt':
                lang = 'pt-BR'

            formatted_tweet = {'id':tweet.tweet_id,'text':clean_text,'language':lang} 
            documents['documents'].append(formatted_tweet)
            print(f"tweet {tweet_counter} added to documents")

            if tweet_counter % 10 == 0:
                response = requests.post(sentiment_url, headers=azure_header, json=documents)
                time.sleep(0.7)
                documents = {'documents':[]}
                try:
                    response.json()['documents']
                    printS(f"Tweets bacth {batch_counter} sent to Azure")
                    save_tweets_sentiment_analysis(response.json(),batch_counter)
                    batch_counter += 1
                    if response.json()['errors'] != []:
                        printW(response.json()['errors'])
                except KeyError:
                    printF(response.json()['error'])
                
            tweet_counter += 1
        else:
            printW(f'Tweet Sentiment {tweet.tweet_id} alredy exists')
    


def clear_text(text) -> str:
    '''Removes new lines, twitter handles, hashtags and links'''
    clean_text = text
    clean_text = clean_text.lower()
    
    # handles and hashtags:
    clean_text = re.sub('(?<=^|(?<=[^a-zA-Z0-9-_\.]))(#|@)([A-Za-z]+[A-Za-z0-9-_]+)','',clean_text)
    
    #URLs:
    clean_text = re.sub('http\S+','',clean_text)
    
    #new lines:
    clean_text = re.sub('(\r\n|\n|\r|\\n)','',clean_text)

    #Checks if re clean text is empty
    no_text = False
    white = ['',' ','  ','   ','    ','     ']
    if clean_text in white:
        no_text = True

    return clean_text, no_text

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
