# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 11:55:04 2016

@author: Lina
"""

from pymongo import MongoClient
#import os
db = MongoClient('mongodb://lina:lina123@ds061395.mlab.com:61395/heroku_nlhh4h9z').heroku_nlhh4h9z

data=[]

#from bson import ObjectId



x= db.info.find({'tvorchNeeded': True})
for i in x:
    data.append(i)

x= db.info.find({'fach_testNeeded': True})
for i in x:
    data.append(i)



for i in range(0,len(data)):
    if data[i]['possible_combinations']==[[]]:
        data[i]['score_case']=4
    elif len(data[i]['fach_tvorch_coefs'].keys())>1:
        data[i]['score_case']=3
    else:
        try:
            if data[i]['zno_coefs']['tvorch_1']<1:
                data[i]['score_case']=1
            else:
                data[i]['score_case']=2
        except KeyError:
            if data[i]['zno_coefs']['fach_test_1']<1:
                data[i]['score_case']=1
            else:
                data[i]['score_case']=2
     
        
id_to_change_1=[data[i]['_id'] for i in range(0, len(data)) if data[i]['score_case']==1]
id_to_change_2=[data[i]['_id'] for i in range(0, len(data)) if data[i]['score_case']==2]
id_to_change_3=[data[i]['_id'] for i in range(0, len(data)) if data[i]['score_case']==3]
id_to_change_4=[data[i]['_id'] for i in range(0, len(data)) if data[i]['score_case']==4]



'''
data1=[]
data2=[]
data3=[]
data4=[]  
for i in range(0,len(data)):
    if data[i]['score_case']==1:
        data1.append(data[i])
for i in range(0,len(data)):
    if data[i]['score_case']==2:
        data2.append(data[i])
for i in range(0,len(data)):
    if data[i]['score_case']==3:
        data3.append(data[i])
for i in range(0,len(data)):
    if data[i]['score_case']==4:
        data4.append(data[i])
'''



db.info.update_many({'_id': {'$in': id_to_change_1}, }, {'$set':{'score_case': 1}}, upsert=True)
db.info.update_many({'_id': {'$in': id_to_change_2}, }, {'$set':{'score_case': 2}}, upsert=True)
db.info.update_many({'_id': {'$in': id_to_change_3}, }, {'$set':{'score_case': 3}}, upsert=True)
db.info.update_many({'_id': {'$in': id_to_change_4}, }, {'$set':{'score_case': 4}}, upsert=True)



x=db.info.find({})
newdata=[]
for i in x:
    newdata.append(i)

