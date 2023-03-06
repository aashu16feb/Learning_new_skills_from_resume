from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime 
from bs4 import BeautifulSoup
from time import sleep
from skill_list import skills

from pymongo import MongoClient
import pymongo
web = webdriver.Chrome()

connection_string = "mongodb://localhost:27017"

client = MongoClient(connection_string)

def do():
    ex = []
    wrong = []
    db = client['jobs']
    mydb = db['narkuri']
    t = 0
    for search in skills:
        try:
            print("index:" ,t)
            t+=1
            search_title = search
            url = "https://www.naukri.com/" + search_title + "-jobs-in-india-it-jobs?k=" + search_title
            print(url)
            web.get(url)

            sleep(1)

            html = web.page_source
            soup = BeautifulSoup(html)

            data = []

            TITLE         = soup.find_all("a", {"class": "title"})
            EXPERIENCE    = soup.find_all("li", {"class": "experience"}) 
            SALARY        = soup.find_all("li", {"class": "salary"})
            LOCATION      = soup.find_all("li", {"class": "location"})
            SKILLS        = soup.find_all("ul", {"class": "has-description"})   
            timest= soup.find_all("span", {"class": "fleft postedDate"})   
            name=soup.find_all("a",{"class":"subTitle ellipsis fleft"})
            for i in range(5):
                #print(int(timest[i].text))
                #print(timest[i].text.split(" ")[0])
                ti=int(timest[i].text.split(" ")[0])
                if(ti<10):
                    print(ti)
                tod = datetime.datetime.now()
                d = datetime.timedelta(days = ti)
                a = tod - d
                print(a)
                
                x = {
                    'title'     : TITLE[i].text,
                    'link'       : TITLE[i].get('href'),
                    'experience': EXPERIENCE[i].text,
                    'salary'    : SALARY[i].text,
                    'location'  : (LOCATION[i].text).split(', '),
                    'skillsets'    : [j.text.title() for j in SKILLS[i]],
                    'dateOfPosting':a,
                    'rating':-1,
                    'userId':"Naukri",
                    'jobType':"Undefined",
                    'duration':0,
                    'Recruiter':name[i].text,
                }

                data.append(x)
            
            

            x = mydb.insert_many(data)

        except Exception as e:
            ex.append(e)
            wrong.append((search , url))

do()