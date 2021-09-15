from vcolors.colors import *
import config.mongo_setup as mongo_setup
from models import Tweets, Replies
import time
import pandas as pd
import requests

def save_replies_sentiment_analysis(json_file,batch_counter):
    printSBG(f'Azure batch {batch_counter} saved')   