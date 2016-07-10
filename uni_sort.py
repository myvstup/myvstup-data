from pymongo import MongoClient
import os
import json

db = MongoClient(os.environ.get('MONGODB_URI')).heroku_rcbs36lq

def get_data():
    return json.load(open('uni_data.json','r',encoding = 'utf-8-sig'))

def sort_data(schema):
    
    def try_except(key):
        print (key)
        try: rank = int(schema[key['name']])
        except KeyError: rank = 101
        return rank

    new_data = []

    for city_data in data:
        city_name = city_data['name']
        city_unis = city_data['univerList']
        city_unis = sorted(city_unis, key=lambda i : try_except(i))
        new_data.append({'name'         : city_name,
                         'univerList'   : city_unis})

    return new_data

if __name__=="__main__":

    print ('getting data ...')
    data = get_data()

    print ('sorting...')
    schema = json.load(open('uni_rank.json','r',encoding = 'utf-8-sig'))
    new_data = sort_data(schema)

    r = db.auto_complete.remove({})
    print (r)
    r = db.auto_complete.insert(new_data)
    print (r)

    print ('done.')