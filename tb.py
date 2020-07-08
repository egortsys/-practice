# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 01:15:35 2020

@author: user
"""

import requests
import telebot
#from telebot import Telebot

bot = telebot.TeleBot('1196310787:AAE3pLYlECBoJdF62pbXqcRQDPWprSEQKB0')

api_version = '?api-version=2019-05-06'
    
endpoint_doctors = 'https://medbot-asszui4utwzhzk4.search.windows.net/'
headers_doctors = {'Content-Type': 'application/json',
        'api-key': '6F4996024DC92D46D4E8817168C33E6D' }
       
endpoint = 'https://medbot-search.search.windows.net/'
headers = {'Content-Type': 'application/json',
       'api-key': 'F6B1E7E306C5048C7AE8CD127F6502F0' }
    
index_diseases = 'indexes/medbot-search-index-diseases/docs'
index_symptoms = 'indexes/medbot-search-index-symptoms/docs'
index_specialists = 'indexes/medbot-search-diseases-list/docs'

index_doctors = 'indexes/docs/docs'
validity_level = 0.2

def clear_string(string):
        if not(string.isdigit()):
            return 0
        else:
            return int(string)
        
def search_symptoms(text):
        url = endpoint + index_symptoms + api_version + '&search=' + text
        responsed = requests.get(url,headers=headers,json='&search='+ text)
        query = responsed.json()
        found_symptoms=''
        for record in query.get('value'):
            if float(record.get('@search.score')) > validity_level:
                found_symptoms+=' '+record.get('Symptom')
        return found_symptoms    

def search_diseases(symptoms):
        url = endpoint + index_diseases + api_version + '&search=' + symptoms
        responsed = requests.get(url,headers=headers,json='&search='+ symptoms)
        query = responsed.json()
        possible_diseases = list()
        for record in query.get('value'):
            if float(record.get('@search.score'))>validity_level:
                possible_diseases.append({'score':record.get('@search.score'),'Disease':record.get('Disease')})
        return possible_diseases
    
def search_specialist(disease):
        url = endpoint + index_specialists + api_version + '&search=' + disease
        responsed = requests.get(url,headers=headers,json='&search='+ disease)
        query = responsed.json()
        specialist = query.get('value')[0].get('Specialist')
        return specialist
            
        
    
def contact_spec(spe):
        return "Specialist phone number - 111-22-33"
def clarify_diseases(text):
        #print(turn_context.activity.text)
        symptoms = search_symptoms(text)
        #await turn_context.send_activity(f"Detected symptoms: '{ symptoms }'")
        if len(symptoms)!=0:
            diseases = search_diseases(symptoms)
            return (diseases,True)
        else:
            return (0,False)
    
def find_most_possible_disease(inp):
        diseases = inp[0]
        most_possible_disease = dict()
        max_score = 0
        for i in range(len(diseases)):
            if float(diseases[i].get('score'))>max_score:
                most_possible_disease = diseases[i]
                max_score = float(diseases[i].get('score'))
        return most_possible_disease
    
def get_min_score(lst):
        min_ind=0
        for i in len(lst):
            if float(lst[i].get('score'))<float(lst[min_ind].get('score')):
                min_ind=i
        return min_ind
    
def extract_most_possible_diseases1(inp):
        diseases = inp[0]
        res = list()
        res.append(diseases.pop(0))
        
        for x in diseases:
            add=True
            for j in res:
                if x.get('Disease')==j.get('Disease'):
                    add=False
                    break
            if add:
                res.append(x)
            if len(res)==3:
                break
        return res
    
def extract_most_possible_diseases(inp):
        diseases = inp[0]
        res = list()
        min_score_ind=0
        j =0
        while (j<3)and(len(diseases)>0):
            add = True
            toadd = diseases.pop(0)
            for x in res:
                if x.get('Disease')==toadd.get('Disease'):
                    add=False
                    break
            if add:
                if(float(toadd.get('score'))<float(res[min_score_ind].get('score'))):
                    min_score_ind=j
                    res.append(toadd)
                    j+=1
            
        for i in range(len(diseases)):
            if float(diseases[i].get('score'))>float(res[min_score_ind].get('score')):
                res[i]=diseases[i]
                min_score_ind=get_min_score(res)
        return res
           
def find_most_usefull_doctor(diseases):
        dis_list = list()
        search_string = "&search="
        for x in diseases:
            if (dis_list.count(x.get('Disease'))==0):
                dis_list.append(x.get('Disease'))
                search_string+=search_specialist(x.get('Disease'))+' '
        url = endpoint_doctors + index_doctors + api_version + search_string
        responsed = requests.get(url,headers=headers_doctors,json=search_string)
        
        query = responsed.json()
        #print(query)
        doc = query.get('value')
        if doc!=None:
            return doc[0]
        else:
            return dict()       

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
        if message.text.find( "Contact: ")!=-1:
            x = clear_string((message.text.strip().split(' ')[1]))
            specialist = contact_spec(x)
            #await turn_context.send_activity(specialist)
        else:
            diseases = clarify_diseases(message.text)
            #print(diseases)
            #print('----------------------------------------')
            if diseases[1]==True:
                mpd = find_most_possible_disease(diseases)
                #print(mpd)
                #print('----------------------------------------')
                response = "Possible disease: " + mpd.get('Disease') + ". Prediction accuracy: " + str(mpd.get('score'))
                specialist = search_specialist(mpd.get('Disease'))
                #print(specialist)
                #print('----------------------------------------')
                response_2 = "Suggest: visit or contact specialist: "+specialist
                dis_test = extract_most_possible_diseases1(diseases)
                

                #print(dis_test)
                #print('----------------------------------------')
                doc=find_most_usefull_doctor(dis_test)
                #print(doc)
                # (no)
                response_3 = "In our base best choice for you is to contact: " +str(doc.get('name')) + " Phone: " +str(doc.get('telephone'))
                bot.send_message(message.from_user.id, response)
                bot.send_message(message.from_user.id, response_2)
                bot.send_message(message.from_user.id, response_3)
                #spec_code=1
                #await turn_context.send_activity(f"If you would like to contact our specialist send: \"Contact: <specialization code>\"\n For your disease code is:'{spec_code}'")
            else:
                bot.send_message(message.from_user.id, "No valid symptoms found in your message")


bot.polling(none_stop=True,interval=0)
