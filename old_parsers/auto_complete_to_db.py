import json
from pymongo import MongoClient
import os
import time

db = MongoClient(os.environ.get('MONGODB_URI')).heroku_rcbs36lq
print ('reading data...')
with open('uni_data.json','r',encoding='utf-8') as f:
	data = json.load(f)
print ('inserting in db...')
t = time.time()
db.auto_complete.insert(data)

i = round(time.time() - t,2)
print ('done in %s sec'%i)
