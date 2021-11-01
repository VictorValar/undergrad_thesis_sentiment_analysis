from mongoengine import document
import requests
import yaml
from vcolors.colors import *
import config.mongo_setup as mongo_setup
from models import Summarizations, Tweets, Replies, TweetsSentiment, RepliesSentiment
import time
from data.replies_azure import save_replies_sentiment_analysis
from data.tweets_azure import save_tweets_sentiment_analysis
from data.summarization_azure import save_Sumarization
import re
import sys
import os
import json

os.chdir(r"C:\Users\victor.santos2\OneDrive - Grupo Marista\TCC\Twitter Sentiment Analysis\MongoTwitter")
output = open("azure_output.out", 'w')

fetch_tweets, fetch_replies = True, True


def main():
    mongo_setup.global_init()
    sentiment_url, azure_header, summarization_url, key_phrase_url, entities_recon_url = connect_azure()
    # replies_NER(azure_header, entities_recon_url)
    # replies_key_extraction(azure_header, key_phrase_url)
    if  fetch_replies == True and fetch_tweets == True:
        replies_sentiment_analysis(azure_header, sentiment_url)
        tweets_sentiment_analysis(azure_header, sentiment_url)
    elif fetch_tweets == True and fetch_replies == False:
        tweets_sentiment_analysis(azure_header, sentiment_url)
    else:
        replies_sentiment_analysis(azure_header, sentiment_url)
    # text_summarization(azure_header, summarization_url)
    printSBG('--- END ---')
    sys.stdout = output
    output.close()


def text_summarization(azure_header, summarization_url):
    '''Gets the replies from the DB, cleans the data and sends it to Azure'''
    tweets = Tweets.objects().all()
    tweet_counter = 1
    for tweet in tweets:
        if not Summarizations.objects(summarization_id=tweet.tweet_id).first():
            replies = Replies.objects.filter(conversation_id=tweet.tweet_id, in_reply_to_user_id=tweet.author_id)
            reply_counter = 1
            full_text = ''

            for reply in replies:
                clean_text, no_text = clear_text(reply.text)

                if no_text == True:
                    printW(f'Reply {reply.reply_id} has no text')
                    continue

                if reply.lang == 'und' or reply.lang != 'pt':
                    printW(f'Invalid reply language {reply.reply_id}')
                    continue

                if len(full_text + ' ' + clean_text) < 5120:
                    full_text = full_text + ' ' + clean_text
                    reply_counter += 1
                    print(f'Tweet {tweet_counter} reply {reply_counter} added to document')

            analysisInput = {"analysisInput": {"documents": [{"language": "pt-BR", "id": tweet.tweet_id,
                                                            "text":'"'+ full_text +'"' }]}, "tasks": {"extractiveSummarizationTasks": [{"parameters": {
                                                                "model-version": "latest",
                                                                "sentenceCount": 20,
                                                                "sortBy": "Offset"
                                                            }}]}}

            response = requests.post(summarization_url, headers=azure_header, json=analysisInput)
            printS(f'Tweet {tweet_counter} sent to Azure')
            printS(f'POST: {response}')
            time.sleep(10)
            get_url = response.headers['operation-location']
            get_response = requests.request("GET", get_url, headers=azure_header)
            while get_response.json()['status'] != 'succeeded':
                printW('Trying GET again')
                get_response = requests.request("GET", get_url, headers=azure_header)
            printS(f'GET: {get_response}' )
            save_Sumarization(get_response.json(),tweet_counter)
            save_file(get_response.json(), 'summarization_test')
            tweet_counter += 1
        else:
            printW('Summarization already extracted')


def replies_NER(azure_header, entities_recon_url):
    '''Gets the replies from the DB, cleans the data and sends it to Azure, afterwards calls save_replies_sentiment_analysis to save the Azure responso to the DB'''
    replies = replies = Replies.objects.filter(
        conversation_id=1436419548660617216, in_reply_to_user_id=128372940)
    documents = {'documents': []}
    reply_counter = 1
    batch_counter = 1
    output = {'documents': []}
    for reply in replies:
        # if not RepliesSentiment.objects.filter(reply_id=reply.reply_id).first():

        clean_text, no_text = clear_text(reply.text)

        if no_text == True:
            printWBG(f'Reply {reply.reply_id} has no text')
            continue

        if reply.lang == 'und' or reply.lang == 'pt':
            lang = 'pt-BR'

        formatted_reply = {'id': reply.reply_id,
                           'text': clean_text, 'language': lang}
        documents['documents'].append(formatted_reply)
        print(f"reply {reply_counter} added to documents")

        if reply_counter % 5 == 0:
            response = requests.post(
                entities_recon_url, headers=azure_header, json=documents)
            time.sleep(0.7)
            documents = {'documents': []}
            try:
                response.json()['documents']
                printS(f"replies bacth {batch_counter} sent to Azure")
                # save_replies_sentiment_analysis(response.json(),batch_counter)
                for i in response.json()['documents']:
                    output['documents'].append(i)
                # this is saving only the last request
                save_file(output, 'NER_test')
                batch_counter += 1
                if response.json()['errors'] != []:
                    printW(response.json()['errors'])
                    printWBG(f'reply text:{clean_text}')
            except KeyError:
                printF(response.json()['error'])

        reply_counter += 1
        # else:
        #     printW(f'Reply Sentiment {reply.reply_id} alredy exists')


def replies_key_extraction(azure_header, key_phrase_url):
    '''Gets the replies from the DB, cleans the data and sends it to Azure, afterwards calls save_replies_sentiment_analysis to save the Azure responso to the DB'''
    replies = replies = Replies.objects.filter(
        conversation_id=1436419548660617216, in_reply_to_user_id=128372940)
    documents = {'documents': []}
    reply_counter = 1
    batch_counter = 1
    output = {'documents': []}
    for reply in replies:
        # if not RepliesSentiment.objects.filter(reply_id=reply.reply_id).first():

        clean_text, no_text = clear_text(reply.text)

        if no_text == True:
            printWBG(f'Reply {reply.reply_id} has no text')
            continue

        if reply.lang == 'und' or reply.lang == 'pt':
            lang = 'pt-BR'

        formatted_reply = {'id': reply.reply_id,
                           'text': clean_text, 'language': lang}
        documents['documents'].append(formatted_reply)
        print(f"reply {reply_counter} added to documents")

        if reply_counter % 10 == 0:
            response = requests.post(
                key_phrase_url, headers=azure_header, json=documents)
            time.sleep(0.7)
            documents = {'documents': []}
            try:
                response.json()['documents']
                printS(f"replies bacth {batch_counter} sent to Azure")
                # save_replies_sentiment_analysis(response.json(),batch_counter)
                for i in response.json()['documents']:
                    output['documents'].append(i)
                # this is saving only the last request
                save_file(output, 'key_phrase_test')
                batch_counter += 1
                if response.json()['errors'] != []:
                    printW(response.json()['errors'])
                    printWBG(f'reply text:{clean_text}')
            except KeyError:
                printF(response.json()['error'])

        reply_counter += 1
        # else:
        #     printW(f'Reply Sentiment {reply.reply_id} alredy exists')


def replies_sentiment_analysis(azure_header, sentiment_url):
    '''Gets the replies from the DB, cleans the data and sends it to Azure, afterwards calls save_replies_sentiment_analysis to save the Azure responso to the DB'''
    replies = Replies.objects.all()
    documents = {'documents': []}
    reply_counter = 1
    batch_counter = 1
    for reply in replies:
        if not RepliesSentiment.objects.filter(reply_id=reply.reply_id).first():

            clean_text, no_text = clear_text(reply.text)

            if no_text == True:
                printWBG(f'Reply {reply.reply_id} has no text')
                continue

            if reply.lang == 'und' or reply.lang == 'pt':
                lang = 'pt-BR'

            formatted_reply = {'id': reply.reply_id,
                               'text': clean_text, 'language': lang}
            documents['documents'].append(formatted_reply)
            print(f"reply {reply_counter} added to documents")

            if reply_counter % 10 == 0:
                response = requests.post(
                    sentiment_url, headers=azure_header, json=documents)
                time.sleep(0.7)
                documents = {'documents': []}
                try:
                    response.json()['documents']
                    printS(f"replies bacth {batch_counter} sent to Azure")
                    save_replies_sentiment_analysis(
                        response.json(), batch_counter)
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
    documents = {'documents': []}
    tweet_counter = 1
    batch_counter = 1
    for tweet in tweets:
        if not TweetsSentiment.objects.filter(tweet_id=tweet.tweet_id).first():

            clean_text, no_text = clear_text(tweet.text)

            if no_text == True:
                printWBG(f'Tweet {tweet.tweet_id} has no text')
                continue

            if tweet.lang == 'und' or tweet.lang == 'pt':
                lang = 'pt-BR'

            formatted_tweet = {'id': tweet.tweet_id,
                               'text': clean_text, 'language': lang}
            documents['documents'].append(formatted_tweet)
            print(f"tweet {tweet_counter} added to documents")

            if tweet_counter % 10 == 0:
                response = requests.post(
                    sentiment_url, headers=azure_header, json=documents)
                time.sleep(0.7)
                documents = {'documents': []}
                try:
                    response.json()['documents']
                    printS(f"Tweets bacth {batch_counter} sent to Azure")
                    save_tweets_sentiment_analysis(
                        response.json(), batch_counter)
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
    clean_text = re.sub(
        '(?<=^|(?<=[^a-zA-Z0-9-_\.]))(#|@)([A-Za-z]+[A-Za-z0-9-_]+)', '', clean_text)

    # URLs:
    clean_text = re.sub('http\S+', '', clean_text)

    # new lines:
    clean_text = re.sub('(\r\n|\n|\r|\\n)', ' ', clean_text)

    # Checks if re clean text is empty
    no_text = False
    white = ['', ' ', '  ', '   ', '    ', '     ']
    if clean_text in white:
        no_text = True

    return clean_text, no_text


def save_file(json_dict, name):
    with open(f"{name}.json", "w") as out_file:
        json.dump(json_dict, out_file, indent=4)


def connect_azure():
    '''Gets Azure auth data'''
    auth = process_yaml()
    azure_url = auth["azure"]["endpoint"]
    sentiment_url = f"{azure_url}text/analytics/v3.1/sentiment"
    summarization_url = f"{azure_url}text/analytics/v3.2-preview.1/analyze"
    key_phrase_url = f"{azure_url}text/analytics/v3.1/keyPhrases"
    entities_recon_url = f"{azure_url}text/analytics/v3.1/entities/recognition/general"
    subscription_key = auth["azure"]["subscription_key"]
    azure_header = {"Ocp-Apim-Subscription-Key": subscription_key}
    return sentiment_url, azure_header, summarization_url, key_phrase_url, entities_recon_url


def process_yaml():
    with open("config/config.yaml") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    main()
