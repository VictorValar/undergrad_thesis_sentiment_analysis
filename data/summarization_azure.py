import json
from vcolors.colors import *
from models import Summarizations 

def save_Sumarization(json_file,tweet_counter) -> Summarizations:
    '''Saves the responses from Azure to the DB, saves the Extractive Summarization response'''
    json_id = json_file['tasks']['extractiveSummarizationTasks'][0]['results']['documents'][0]['id']
    sentences = json_file['tasks']['extractiveSummarizationTasks'][0]['results']['documents'][0]['sentences']
    s = 1
    for sentence in sentences:
        text  = sentence['text']
        if not Summarizations.objects(text=text).first():
            summarization_obj = Summarizations()
            summarization_obj.summarization_id = json_id
            summarization_obj.text = sentence['text']
            summarization_obj.rankScore = sentence['rankScore']           
            summarization_obj.save()
            printS(f'Summarization {s} saved')
            s += 1

            if json_file['tasks']['extractiveSummarizationTasks'][0]['results']['documents'][0]['warnings'] != []:
                printW(json_file['tasks']['extractiveSummarizationTasks'][0]['results']['documents'][0]['warnings']) 
        else:
            printW(f'Summarization {json_id} already exists')

