from vcolors.colors import *
import config.mongo_setup as mongo_setup
from models import Tweets, Replies
import time
import pandas as pd
import requests

def save_replies_sentiment_analysis(json_file,batch_counter):
    '''Saves the responses from Azure to the DB, it updates the Replies documents with the new info and also creates new RepliesSentimentScores documents  '''
    printSBG(f'Azure batch {batch_counter} saved')   