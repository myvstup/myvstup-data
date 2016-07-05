# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 11:55:04 2016

@author: Lina
"""

from pymongo import MongoClient
#import os
db = MongoClient('mongodb://lina:lina123@ds061395.mlab.com:61395/heroku_nlhh4h9z').heroku_nlhh4h9z

data=[]
#x = db.info.find({'tvorchNeeded': True, {'zno_coefs.tvorch_1': {$lt: 0.5}}})
#x = db.info.find({'point_median': {'$gt':150}})
#x = db.info.find({'tvorchNeeded': True, 'zno_coefs.tvorch_1': {'$lt': 0.5}})
#x = db.info.find({'tvorchNeeded': True, 'zno_coefs.tvorch_1': 1})

#db.info.update({'tvorchNeeded': True, 'zno_coefs.tvorch_1': {'$lt': 1.5}}, {'$set':{'score_case': 1}}, upsert=True, multi=True)

#x = db.info.find({'tvorchNeeded': True, 'zno_coefs.tvorch_1': {'$lt': 1.5}})
'''
from bson import ObjectId

useless_id = [data[i]['_id'] for i in range(0,10)]
db.info.remove({'_id' : { '$in' : useless_id } })
'''

#x = db.info.find({'score_case': 1})
x= db.info.find({'tvorchNeeded': True})
for i in x:
    data.append(i)

x= db.info.find({'fach_testNeeded': True})
for i in x:
    data.append(i)


for i in range(0,len(data)):
    if data[i]['possible_combinations']==[]:
        data[i]['score_case']=4
    elif sum(data[i]['zno_coefs'].values()) < 1:
        data[i]['score_case']=1
    elif len(data[i]['fach_tvorch_coefs'].keys())==1:
        data[i]['score_case']=2
    else:
        data[i]['score_case']=3
          
        
        
        


#data=[i for i in x if len(i['zno_coefs'].keys())==3]

#data={ 1:i for i in x}
'''
for i in x:
    if len(i['zno_coefs'].keys())==0:
        data.append(i)
'''
'''
for i in x:
    if 'zno_coefs' in i.keys():
        data.append(i)
'''       
'''
print(i.keys())
print(len(i.keys()))
print(i['cityName'])
print(len(i['zno_coefs'].keys()))
'''