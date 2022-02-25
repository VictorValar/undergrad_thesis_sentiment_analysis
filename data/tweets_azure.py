from vcolors.vcolors import *
from models import TweetsSentiment

def save_tweets_sentiment_analysis(json_file,batch_counter) -> TweetsSentiment:
    '''Saves the responses from Azure to the DB, it updates the Tweets documents with the new info and also creates new TweetsSentimentScores documents  '''
    json_files = json_file['documents']
    tweet_sentiment_counter = 1
    for file in json_files:
        if not TweetsSentiment.objects.filter(tweet_id=file['id']).first():
            reply_sentiment = TweetsSentiment()
            reply_sentiment.tweet_id = file['id']
            reply_sentiment.length = file['sentences'][0]['length']
            reply_sentiment.sentiment = file['sentiment']
            reply_sentiment.positive = file['confidenceScores']['positive']
            reply_sentiment.neutral = file['confidenceScores']['neutral']
            reply_sentiment.negative = file['confidenceScores']['negative']
            reply_sentiment.clean_text = file['sentences'][0]['text']
            reply_sentiment.save()
            print(f'Tweet sentiment {tweet_sentiment_counter} saved')
            if file['warnings'] != []:
                printF(f'file id {file["id"]} warnings: {file["warnings"]}')
            
            tweet_sentiment_counter += 1
        else:
            printW(f'Reply Sentiment {file["id"]} alredy exists')

    printSBG(f'Tweets batch {batch_counter} finished')