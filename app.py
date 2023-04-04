from flask import Flask , render_template , url_for , redirect , abort , request
from pymongo import MongoClient
import pymongo
import operator
import spacy
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
#from __future__ import unicode_literals, print_function
import plac
import random
import re
from pathlib import Path
import spacy
import sys, fitz
from pyresparser import ResumeParser
import os
from docx import Document
from tqdm import tqdm
import bson
import json
from pymongo.collation import Collation
app = Flask(__name__)
connection_string = "mongodb://localhost:27017"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
client = MongoClient(connection_string)
db1=client['jobPortal']
mydb1=db1['jobapplicantinfos']
mydb3 = db1['jobs']
db2=client['youtube']
mydb2=db2['playlists']
#EXTRACT SKILLS FROM THE GIVEN TEXT
    
def extract_information_from_user(text,respath):
    key=[]
    value=[]
    nlp = spacy.load("./data/ner_model")

    doc = nlp(text)
    print(doc.ents)
    test_skills=[]
    for ent in doc.ents:
                test_skills.append(ent.text.title())
    print("Skills:",list(set(test_skills)))
    data=ResumeParser(respath).get_extracted_data()
    print(data['skills'])
    # for ent in doc.ents:
    #     key.append(ent.label_)
    #     value.append(ent.text)
    
    # Dict = {key[i]: value[i] for i in range(len(key))}
    
    # SKILLS= Dict["SKILLS"].split(",")

    # Dict.update(SKILLS=SKILLS)

    # text = Dict["SKILLS"]
    # txt=list(set(test_skills))
    # for ele in text:
    #     i=ele.strip(' ')
    #     #str(ele).replace(' ','')
    #     #print(i)
    #     txt.append(i)
    # print("Hello",txt)
    txt=list(set(list(test_skills)+list(data['skills'])))
    print("Welcome",txt)
    return retirve_info_from_db(txt)

def extract_information_from_usercourse(text,interests,respath):
    key=[]
    value=[]
    nlp = spacy.load("./data/ner_model")

    doc = nlp(text)
    #print(doc.ents)
    test_skills=[]
    for ent in doc.ents:
                test_skills.append(ent.text.title())
    print("Skills:",list(set(test_skills)))
    data=ResumeParser(respath).get_extracted_data()
    print(data['skills'])
    # for ent in doc.ents:
    #     key.append(ent.label_)
    #     value.append(ent.text)
    
    # Dict = {key[i]: value[i] for i in range(len(key))}
    
    # SKILLS= Dict["SKILLS"].split(",")

    # Dict.update(SKILLS=SKILLS)

    # text = Dict["SKILLS"]
    # txt=list(set(test_skills))
    # for ele in text:
    #     i=ele.strip(' ')
    #     #str(ele).replace(' ','')
    #     #print(i)
    #     txt.append(i)
    # print("Hello",txt)
    print("hdj",interests)
    txt=list(set(list(test_skills)+list(data['skills'])+interests))
    print("Welcome",txt)
    return retirve_info_from_dbcourse(txt)

#RETRIVE RELATED JOBS BASED ON JACCARD COEFFICIENT 
def retirve_info_from_db(user_list):
    
    len_user_list = len(user_list)
    n = mydb3.find( { 'skillsets': { '$in': user_list}} ,{'_id':0}) #COLLECTING JOBS BASED ON MATCHING SKILLS
    
    jobs = []
    joblist=[]
    for i in n:

        job_skill = i['skillsets']
        job_skills=list(map(lambda x:x.title(), job_skill))
        print("Jobs",job_skills)
        match = len([k for k , val in enumerate(job_skills) if val in user_list])
        total_len = len(job_skills) + len_user_list 
        i['rank'] = match/total_len #RANKING COEFFICIENT
        jobs.append(i)
    jobs.sort(key=operator.itemgetter('rank') , reverse=True) #SORTING JOBS BASED ON THE RANK SCORE
    # print("XYZZ",jobs)
    for i in jobs:
        joblist.append(i['title'])
    print(joblist)

    return json.dumps({"result":joblist})

"""#SORT THE JOBS RANK WISE AND DISPLAY
def show_info(jobs , job_skills , job_len):

    return render_template('show_job.html' , jobs=jobs , job_skills=job_skills , job_len=job_len)"""

# @app.route('/scrape',methods=['GET'])
# def scrape_jobs():

def retirve_info_from_dbcourse(user_list):
    
    len_user_list = len(user_list)
    n = mydb2.find( { 'skills': { '$in': user_list}} ,{'_id':0}) #COLLECTING JOBS BASED ON MATCHING SKILLS
    
    jobs = []
    joblist=[]
    for i in n:

        job_skill = i['skills']
        job_skills=list(map(lambda x:x.title(), job_skill))
        print("Jobs",job_skills)
        match = len([k for k , val in enumerate(job_skills) if val in user_list])
        total_len = len(job_skills) + len_user_list 
        i['rank'] = match/total_len #RANKING COEFFICIENT
        jobs.append(i)
    jobs.sort(key=operator.itemgetter('rank') , reverse=True) #SORTING JOBS BASED ON THE RANK SCORE
    # print("XYZZ",jobs)
    for i in jobs:
        joblist.append(i['playListName'])
    print(joblist)

    return json.dumps({"result":joblist})

"""#SORT THE JOBS RANK WISE AND DISPLAY
def show_info(jobs , job_skills , job_len):

    return render_template('show_job.html' , jobs=jobs , job_skills=job_skills , job_len=job_len)"""

# @app.route('/scrape',methods=['GET'])
# def scrape_jobs():
    

@app.route('/recommend', methods=['POST'])
def my_form_post():
    data= request.get_json()
    userid=data['id']
    myskills=mydb1.find({'userId': bson.ObjectId(oid=str(userid))},{'_id':0})
    resumepath =""
    ski=""
    for data in myskills:
        ski=" , ".join(data['skills'])
        resumepath=data['resume']
    #ski=ski.title();   
    
    ski="SKILLS "+ski
    resumepath=resumepath.replace("/host/", "C:/Users/Ashutosh/Desktop/crowdfunding-react/job-portal/backend/public/")
    print(resumepath)
    return(extract_information_from_user(ski,resumepath))    

@app.route('/recommendcourse', methods=['POST'])
def my_form_post1():
    data= request.get_json()
    userid=data['id']
    myskills=mydb1.find({'userId': bson.ObjectId(oid=str(userid))},{'_id':0})
    resumepath =""
    ski=""
    interests=[]
    for data in myskills:
        ski=" , ".join(data['skills'])
        resumepath=data['resume']
        interests=data['interests']
        print(data['interests'])
    #ski=ski.title();   
    
    ski="SKILLS "+ski
    resumepath=resumepath.replace("/host/", "C:/Users/Ashutosh/Desktop/crowdfunding-react/job-portal/backend/public/")
    print(resumepath)
    return(extract_information_from_usercourse(ski,interests,resumepath))    

if __name__ == "__main__":
    
    #CONNECTING WITH MONGO DB
    connection_string = "mongodb://localhost:27017"
    client = MongoClient(connection_string)

    db = client['jobs']
    db1=client['jobPortal']
    mydb = db1['jobs']
    mydb1=db1['jobapplicantinfos']
    #STARTING THE APPLICATION
    app.run(host="0.0.0.0" ,port=5000, debug = True)