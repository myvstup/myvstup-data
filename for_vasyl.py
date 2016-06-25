import csv
import json
import numpy as np
import pandas as pd
import glob
files = glob.glob("c:/users/prost/dropbox/myvstup/competitions/*.csv")

def remove_nans(list_data):
    try: list_data.remove('Дані відсутні')
    except ValueError : pass
    return list_data

citiesList = []
for file in files:
    unis = []
    with open(file,'r',encoding = 'utf-8') as f :
        rreader = csv.reader(f)
        for row in rreader:
            if len(row)!=0 :
                if 'Вступна' not in row[0]: 
                    unis.append(row)
        data = pd.DataFrame(unis,columns=['uni','fac','id','spec',1,2,3,4,5,6,7]).replace('','Дані відсутні')
        uni_list = list(np.unique(data['uni']))
        uni_list = remove_nans(uni_list)
        data.set_index(['uni','fac'],inplace = True)
        unis_data = []
        for uni in uni_list:
            uni_data = data.ix[uni,['spec']]
            fac_data = []
            ite_fac_list = remove_nans(list(np.unique(uni_data.index)))
            for fac in ite_fac_list:
                if len(list(uni_data.ix[fac,'spec'])[0])==1:
                    spec_list = list(set([str(spec) for spec in list(uni_data.ix[fac,['spec']])]))
                    spec_list = remove_nans(spec_list)
                else:
                    spec_list = list(set([str(spec) for spec in list(uni_data.ix[fac,'spec'])]))
                    spec_list = remove_nans(spec_list)

                fac_data.append({'name':str(fac),
                                 'spetializationList': spec_list})

            unis_data.append({'name':str(uni),
                              'facultatyList':fac_data})
        citiesList.append({'name' : str(file.split('\\')[-1].split('.csv')[0]),
                           'univerList':unis_data})

import io
with io.open('uni_data.json', 'w', encoding='utf8') as f:
    json.dump(citiesList,f ,ensure_ascii=False, indent=4)

citiesList = []

for file in files:
    unis = []
    with open(file,'r',encoding = 'utf-8') as f :
        rreader = csv.reader(f)
        for row in rreader:
            if len(row)!=0 :
                if 'Вступна' not in row[0]: 
                    unis.append(row)
        data = pd.DataFrame(unis,columns=['uni','fac','id','spec',1,2,3,4,5,6,7]).replace('','Дані відсутні')
        spec_data = list(np.unique(data['spec']))
        spec_data = remove_nans(spec_data)
        citiesList.append({'name' : str(file.split('\\')[-1].split('.csv')[0]),
                           'specializationList': spec_data})

ukr_data = []
for city in citiesList:
    for i in city['specializationList']:
        ukr_data.append(i)

citiesList.append({'name':'Україна',
                   'specializationList':list(set(ukr_data))})

import io
with io.open('spec_data.json', 'w', encoding='utf8') as f:
    json.dump(citiesList,f ,ensure_ascii=False, indent=4)
