from bs4 import BeautifulSoup  
#pulls data out of html and xml

import requests                
#gets the page from url

import re
#find and replace string text

import operator
#regular python operations

import json
#help to parse and format json

import sys
#system calls for user arguments

from tabulate import tabulate
#use for tabulating data

from stop_words import get_stop_words
#stop words are a few words to be left out from our list due to negligible significance


#HELPER FUNCTIONS 



def get_word_list(url):
  word_list=[]
  source_code=requests.get(url)
  plain_text=source_code.text

  soup=BeautifulSoup(plain_text,'lxml')
 
  for text in soup.findAll('p'):
         if text.text is None:
            continue
         content=text.text
         words=content.lower().split()

         for word in words:
           cleaned_word=clean_word(word)
           if len(cleaned_word)>0:
             word_list.append(cleaned_word)

  return word_list

#get the page source code from url, convert into plain text and render it into beautifull soup . lxml is a python package that reads html amd xml
#find all para tags and if the data is text then convert into lower case and split for recognition
#the text is cleaned and appended to an empty word list


def clean_word(word):
        cleaned_word=re.sub('[^A-Za-z]+','',word)

        return cleaned_word

#word cleaning is done by using regex to remove something which is not char or letter

def createFrequencyTable(word_list):

 word_hash={}

 for word in word_list:
  if word in word_hash:
    word_hash[word]+=1
  else:
    word_hash[word]=1   
 return word_hash

#for each word in the list, create a key in hash map and update its frequency each time it is encountered




def remove_stop_words(word_hash):
        stop_words_total=get_stop_words('en')

        temp_list=[]

        for key,value in word_hash:
                if key not in stop_words_total:
                        temp_list.append([key,value])

        return temp_list                


#get a prepared list of stop words , analyse each key word one by one , if the key is a not a stop word it is appended to a new list of pair 






wikipedia_API_link="https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch="
#api link to get the wiki search api call
wikipedia_link="https://en.wikipedia.org/wiki/"
#wikipedia page direct link

if(len(sys.argv)<2):
        print("invalid string--too short")
        exit()
#system call for entering the string
#if string is too short then error

string_query=sys.argv[1]
#storing the argument in a variable

if(len(sys.argv)>2):
        search_mode=True
else:
    search_mode=False
#serach-mode true for valid string


url=wikipedia_API_link+string_query
#creating the user customised search url by concatonation

try:
        response=requests.get(url)
        #get raw data from the url 

        data=json.loads(response.content.decode("utf-8"))
        #format data as json dictionary

        wikipedia_page_tag=data['query']['search'][0]['title']
    # first we got the wiki api and user query concatonated to get the api call url
    #then we converted the api call into json format to parse it and created a wiki tag of the first data item by title

        url=wikipedia_link+wikipedia_page_tag
    #get the actual wiki page url to retrive data
    

        page_word_list=get_word_list(url)
    #get the words from wiki url

        page_word_count=createFrequencyTable(page_word_list)
    #calculate frequency of the words

        sorted_word_count_min=sorted(page_word_count.items(),key=operator.itemgetter(1),reverse=False)
        sorted_word_count_max=sorted(page_word_count.items(),key=operator.itemgetter(1),reverse=True)
    #create a sorted frequency table

        if(search_mode):
                sorted_word_count_max=remove_stop_words(sorted_word_count_max)
                sorted_word_count_min=remove_stop_words(sorted_word_count_min)

    # if search mode is true, remove the stop words     

        total_word_sum_max=0
        for key,value in sorted_word_count_max:
                total_word_sum_max=total_word_sum_max+value

    #count total words in the list
        if(len(sorted_word_count_max)>20):
                sorted_word_count_max=sorted_word_count_max[:20]
        if(len(sorted_word_count_min)>20):
                sorted_word_count_min=sorted_word_count_min[:20]        

    #if the list exceeds 20 words then cut short the list to 20
        

        final_list_max=[]
        for key,value in sorted_word_count_max:
                percentage_value = float(value * 100) / total_word_sum_max
                final_list_max.append([key,value,round(percentage_value,4)])
        final_list_min=[]
        for key,value in sorted_word_count_min:
                percentage_value = float(value * 100) / total_word_sum_max
                final_list_min.append([key,value,round(percentage_value,4)])        

    #final list containing all the words , values and pecentage of frequency
        
        print_headers_max=['Words_Maximum','Frequency','Percentage of Total']
        print_headers_min=['Words_Minimum','Frequency','Percentage of Total']
        #add headers to each column

        print(tabulate(final_list_max,headers=print_headers_max,tablefmt='orgtbl'))

        print(tabulate(final_list_min,headers=print_headers_min,tablefmt='orgtbl'))
    #print table using tabulate command




except requests.exceptions.Timeout:
        print("Time Out . Server did not respond")


