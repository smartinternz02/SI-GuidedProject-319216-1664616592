# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 14:59:33 2021

@author: Admin
"""


from flask import Flask, request, render_template, redirect, url_for
from cloudant.client import Cloudant
import numpy as np
import re
import os
#from gevent.pywsgi import WSGIServer
import requests as HTTP
from bs4 import BeautifulSoup as SOUP


# Authenticate using an IAM API key
client = Cloudant.iam('ea42a4f2-5b3d-47ae-89d7-c6a17c5673c0-bluemix','BdpOvgvRCZtVHwXMrm8y6-XA2uxlHw8JA-UMSB8VWLGV', connect=True)


# Create a database using an initialized client
my_database = client.create_database('my_datamovie')

app = Flask(__name__)
app=Flask(__name__,template_folder="templates") 

@app.route('/',methods=['GET'])
def index():
    return render_template('home.html')

@app.route('/home', methods=['GET'])
def about():
    return render_template('home.html')

# registration page
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/afterreg', methods=['POST'])
def afterreg():
    x = [x for x in request.form.values()]
    print(x)
    data = {
    '_id': x[1], # Setting _id is optional
    'name': x[0],
    'psw':x[2]
    }
    print(data)
    
    query = {'_id': {'$eq': data['_id']}}
    
    docs = my_database.get_query_result(query)
    print(docs)
    
    print(len(docs.all()))
    
    if(len(docs.all())==0):
        url = my_database.create_document(data)
        #response = requests.get(url)
        return render_template('register.html', pred="Registration Successful, please login using your details")
    else:
        return render_template('register.html', pred="You are already a member, please login using your details")
    
# login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/afterlogin',methods=['POST'])
def afterlogin():
    user = request.form['_id']
    passw = request.form['psw']
    print(user,passw)
    
    query = {'_id': {'$eq': user}}    
    
    docs = my_database.get_query_result(query)
    print(docs)
    
    print(len(docs.all()))
    
    
    if(len(docs.all())==0):
        return render_template('login.html', pred="The username is not found.")
    else:
        if((user==docs[0][0]['_id'] and passw==docs[0][0]['psw'])):
            return redirect(url_for('prediction'))
        else:
            return render_template('login.html', pred="The password is incorrect.")
            print('Invalid User')
            
@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/predict', methods=["GET","POST"])
def predict():
    #emotion=None
    #urlhere='http://www.imdb.com/search/title?genres=drama&title_type=feature&sort=moviemeter, asc'
    if request.method == "POST":
        emotion=request.form['emotion']
    print(emotion)
    if(emotion == "happy"):
        urlhere = 'http://www.imdb.com/search/title?genres=drama&title_type=feature&sort=moviemeter, asc'
    elif(emotion == "angry"):
        urlhere = 'http://www.imdb.com/search/title?genres=thriller&title_type=feature&sort=moviemeter, asc'
    elif(emotion == "disgust"):
        urlhere = 'http://www.imdb.com/search/title?genres=sport&title_type=feature&sort=moviemeter, asc'
    elif(emotion == "think"):
        urlhere = 'http://www.imdb.com/search/title?genres=thriller&title_type=feature&sort=moviemeter, asc'
    elif(emotion == "sad"):
        urlhere = 'http://www.imdb.com/search/title?genres=western&title_type=feature&sort=moviemeter, asc'
    response = HTTP.get(urlhere)
    data = response.text
    soup = SOUP(data, "lxml")
    supa = soup.find_all('h3', attrs={'class' : 'lister-item-header'})
    list = []
    for header in supa:
        name = "";   
        aElement_soup = header.find_all('a')
        spanElement_soup = header.find_all('span')
        spanElement = spanElement_soup[0]
        name = name + spanElement.text
        aElement = aElement_soup[0]
        name = name + "" + aElement.text
        if len(spanElement_soup)>1:
            spanElement = spanElement_soup[1]
            name = name + "\n" + spanElement.text
        list.append(name)
    
    return render_template('home.html',prediction_text="{}".format(emotion),data=list)

if __name__ == "__main__":
   app.run(debug=False) 

    
