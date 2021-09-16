import json
from vcolors.colors import *
from models import RepliesSentiment

def save_replies_sentiment_analysis(json_file,batch_counter) -> RepliesSentiment:
    '''Saves the responses from Azure to the DB, it updates the Replies documents with the new info and also creates new RepliesSentimentScores documents  '''
    json_files = json_file['documents']
    reply_sentiment_counter = 1
    for file in json_files:
        if not RepliesSentiment.objects.filter(reply_id=file['id']).first():
            reply_sentiment = RepliesSentiment()
            reply_sentiment.reply_id = file['id']
            reply_sentiment.lenth = file['sentences'][0]['length']
            reply_sentiment.sentiment = file['sentiment']
            reply_sentiment.positive = file['confidenceScores']['positive']
            reply_sentiment.neutral = file['confidenceScores']['neutral']
            reply_sentiment.negative = file['confidenceScores']['negative']
            reply_sentiment.clean_text = file['sentences'][0]['text']
            reply_sentiment.save()
            print(f'Reply sentiment {reply_sentiment_counter} saved')
            if file['warnings'] != []:
                printW(f'file id {file["id"]} warnings: {file["warnings"]}')
            
            reply_sentiment_counter += 1
        else:
            printW(f'Reply Sentiment {file["id"]} alredy exists')

    printSBG(f'Replies batch {batch_counter} saved')

