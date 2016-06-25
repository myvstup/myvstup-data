# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 21:31:17 2016

@author: Lina
"""
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import time 
def request_link(website):

    time.sleep(0.2)

##just text
    soup =BeautifulSoup(urllib2.urlopen(website),"lxml")
    for i in range(1,5):
        try :
            table=soup.find('table', id="denna%s"%i)
            [i for i in table.find_all('tr')]
            break
        except AttributeError:
            pass

    if type(table)==type(None):
        return []
    ## find data
    napriams=[]
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        napriams.append(cells)
    #str(napriams[2][2]).split('<br/>')
    ## clean up data from empty cells
    napriams = [x for x in napriams if x!=[]]

    ## clean up data
    for i in range(0,len(napriams)):
        napriams[i]=[napriams[i][0],napriams[i][1],napriams[i][4]]
        
    
    ## find all href for napriam konkurs
    for i in range(0,len(napriams)):
        if napriams[i][1].find_all('a')!=[]:
            napriams[i][1]=napriams[i][1].find_all('a')[0].get('href')
        else:
            napriams[i][1]=''
        
        
        
        ## dictionary for coefficents
        
    '''coeff={'Українська мова і література':0, 'Історія України':0, 'Математика':0, 
        'Біологія':0, 'Географія':0, 'Фізика':0, 'Хімія':0, 'Англійська мова':0, 
        'Іноземна мова (Англійська мова, Французька мова, Німецька мова, Іспанська мова)':0, 
        'Російська мова':0,'Творчий конкурс 1':0,'Творчий конкурс 2':0,'Творчий конкурс 3':0, 
        'Фаховий іспит 1':0,'Фаховий іспит 2':0,'Фаховий іспит 3':0, 
        'Документ про освіту':0}'''
        
        
        
        ## cleaning data for coefficents
        ## napriams[0]=name of faculty and napriam(not cleaned)
        ## napriams[1]=href
        ## napriams[2]=coeff
    
    
        
    for i in range(0, len(napriams)):
        napriams[i][2]=str(napriams[i][2]).replace('</td>','')
        napriams[i][2]=str(napriams[i][2]).replace('<td>','')
        napriams[i][2]=str(napriams[i][2]).split('<br/>')
        napriams[i][2]=[x for x in napriams[i][2] if x!='']
        for j in range(0,len(napriams[i][2])):
            napriams[i][2][j]=napriams[i][2][j].split(' (k=')
            napriams[i][2][j][0]=napriams[i][2][j][0][3:len(napriams[i][2][j][0])]
            if len(napriams[i][2][j])==2:
                napriams[i][2][j][1]=float(napriams[i][2][j][1].replace(')',''))
            else:
                napriams[i][2][j].append(1)
                
    ## clean up from empty predmets    
    napriams=[x for x in napriams if x[2]!=[]]   
    
    
    ##dictionary for coefficients
    data = []
    for i in range(0, len(napriams)):
        ##coefhier it's just a notation for coefficients hier 
        coeffhier={'Українська мова та література':0, 'Історія України':0, 'Математика':0, 'Біологія':0, 'Географія':0, 'Фізика':0, 'Хімія':0, 'Англійська мова':0, 'Іноземна мова (Англійська мова, Французька мова, Німецька мова, Іспанська мова)':0, 'Російська мова':0,'Творчий конкурс 1':0,'Творчий конкурс 2':0,'Творчий конкурс 3':0, 'Фаховий іспит 1':0,'Фаховий іспит 2':0,'Фаховий іспит 3':0, 'Документ про освіту':0}
        fach=0
        tvor=0
        for j in range(0,len(napriams[i][2])):
            if napriams[i][2][j][0]=='Фаховий іспит':
                fach=fach+1
                coeffhier['Фаховий іспит %s'%fach]=napriams[i][2][j][1]
                '''
                if fach==1:
                    coeffhier['Фаховий іспит 1']=napriams[i][2][j][1]
                if fach==2:
                    coeffhier['Фаховий іспит 2']=napriams[i][2][j][1]
                if fach==3:
                    coeffhier['Фаховий іспит 3']=napriams[i][2][j][1]'''
            if napriams[i][2][j][0]=='Творчий конкурс':
                tvor=tvor+1
                coeffhier['Творчий конкурс %s' %tvor]=napriams[i][2][j][1]
                ''''
                if tvor==1:
                    coeffhier['Творчий конкурс 1']=napriams[i][2][j][1]
                if tvor==2:
                    coeffhier['Творчий конкурс 2']=napriams[i][2][j][1]
                if tvor==3:
                    coeffhier['Творчий конкурс 3']=napriams[i][2][j][1]'''
            if napriams[i][2][j][0]!='Творчий конкурс'and napriams[i][2][j][0]!='Фаховий іспит':
                coeffhier[napriams[i][2][j][0]]=napriams[i][2][j][1]
        data.append([napriams[i][0],napriams[i][1],str(coeffhier)])

    return data

    #napriams[i][2]=coeffhier

#print(data)
#dict(zip(range(0,10),range(10,21)))
#print(predmety[0].find(text=True))
import csv
import glob
files = glob.glob("c:/users/lina/dropbox/myvstup/cities unis href/*.txt")

for file in files:

    uni_data = []
    f = open(file,'r',encoding='CP1251')
    city=str(file.split('\\')[1][:-4])
    for i in csv.reader(f):
        if len(i) != 0:
            website = 'http://www.vstup.info/2015/'+ str(i[0])[2:]
            uni_data.append(request_link(website))
            

    filename=str('c:/users/lina/dropbox/myvstup/links_on_competitions/' + city+ ' napriam'+'.csv')
    with open(filename, 'w',encoding='utf-8') as file:
        writer=csv.writer(file)
        for uni in uni_data:
            for row in uni:
                writer.writerow(row)
