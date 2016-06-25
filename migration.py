import csv
import os
from collections import defaultdict
from pymongo import MongoClient
import json

db = MongoClient(os.environ.get('MONGODB_URI')).heroku_rcbs36lq

useless_zno = ['Психологія','Правознавство','Екологія','Економіка','Інформатика','Людина і світ']
zno_dict = {
 'Документ про освіту': 'certificateScore',

 'Англійська мова': 'eng',
 'Російська мова': 'rus',
 'Українська мова та література': 'ukr',
 'Українська мова': 'ukr',
 'Українська мова і література (поглиблений рівень)': 'ukr',
 'Французька мова': 'fra',
 'Німецька мова': 'de',
 'Іспанська мова': 'es',
 'Іноземна мова': ['eng','rus','fra','de','es'],
 
 'Всесвітня історія': 'history',
 'Історія України': 'history',
 'Біологія': 'biology',
 'Хімія': 'chemistry',
 'Географія': 'geography',
 'Математика': 'math',
 'Математика (поглиблений рівень)':'math',
 'Фізика': 'physics',

 'Творчий конкурс 1': 'tvorch_1',
 'Творчий конкурс 2': 'tvorch_2',
 'Творчий конкурс 3': 'tvorch_3',
 ' Фаховий іспит': 'fach_test_1',
 'Фаховий іспит 1': 'fach_test_1',
 'Фаховий іспит 2': 'fach_test_2',
 'Фаховий іспит 3': 'fach_test_3',
 'Фаховий іспит 4': 'fach_test_4',
 'Фаховий іспит 5': 'fach_test_5',
 'Фаховий іспит 6': 'fach_test_6',
 'Фаховий іспит 7': 'fach_test_7',
 'Фаховий іспит 8': 'fach_test_8',
 'Фаховий іспит 9': 'fach_test_9'}

fach_tvorch = ['tvorch_1','tvorch_2','tvorch_3',
                'fach_test_1','fach_test_1', 'fach_test_2',
                'fach_test_3','fach_test_4','fach_test_5',
                'fach_test_6','fach_test_7','fach_test_8','fach_test_9']

counter = 21576
import glob
files = glob.glob("competitions/*.csv")

data = []
for f in files:

    with open(f,'r',encoding = 'utf-8') as file:
        reader = csv.reader(file)
        city_data = []
        for row in reader:
            if len(row)!=0:
                data_row = defaultdict(dict)
                data_row['cityName'] = str(f.split('\\')[-1].split('.')[0])
                data_row['universityName'] = str(row[0])
                data_row['facultatyName'] = str(row[1])
                data_row['specialityId'] = str(row[2])
                data_row['specialityName'] = str(row[3])
                data_row['placeRange'] = {"all":int(row[4]),
                                          "free":int(row[5]),
                                          "payable":int(row[6])}

                points = row[7].replace('[','').replace(']','').split(', ')

                if '?' not in row[7]:
                    data_row['point_min'] = float(points[0])
                    data_row['point_mid_median'] = float(points[1])
                    data_row['point_median'] = float(points[2])
                else : 
                    continue

                coefs_dict = {}
                temp_dict = json.loads(row[9].replace("'",'"'))
                if str in [type(i) for i in list(temp_dict.values())]:
                    str_indexes = [j for j,i in enumerate([type(i) for i in list(temp_dict.values())]) if i==str]
                    for str_item in str_indexes:
                        str_value = temp_dict[list(temp_dict.keys())[str_item]]
                        coef, extra_zno = str_value.split(') або ')
                        temp_dict[list(temp_dict.keys())[str_item]] = float(coef)
                        temp_dict[extra_zno] = float(coef)

                non_zero_keys = [k for k in list(temp_dict.keys()) if temp_dict[k]!=0]
                for key in non_zero_keys:
                    try:
                        if key == 'Іноземна мова':
                            coefs_dict.update({lang: float(temp_dict[key]) for lang in zno_dict[key]})
                        else:
                            db_name = zno_dict[key]
                            coefs_dict[db_name] = float(temp_dict[key])
                    except KeyError:
                        if key in useless_zno : continue
                        else :
                            if 'Іноземна мова (' in key:
                                coefs_dict.update({zno_dict[lang] : float(temp_dict[key]) for lang in key.split('(')[-1].split(')')[0].split(', ')})
                            else: print (key)

                coefs_dict['needed_zno'] = [zno_name for zno_name in list(coefs_dict.keys()) if zno_name not in fach_tvorch]
                data_row['zno_coefs'] = coefs_dict

                data_row['tvorchNeeded'] = False
                data_row['fach_testNeeded'] = False

                for zno_name in list(coefs_dict.keys()):
                    if zno_name in fach_tvorch:
                        data_row[str(zno_name[:-2]+'Needed')] = True

                data_row['link'] = row[10]

                if data_row['placeRange']['free'] != 0:
                    data_row['isFreePlaces'] = True
                else: data_row['isFreePlaces'] = False

                if len(data_row['zno_coefs']['needed_zno']) == 0:
                    data_row['searchable'] = False
                db.info.insert_one( data_row )
                counter -= 1
                print ('left %s'%counter)