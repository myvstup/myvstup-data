# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 19:42:26 2016

@author: Lina
"""

from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
    
import statistics
#import re
import ast
import time 
#bla

#website='http://www.vstup.info/2015/328/i2015i328p212903.html#list'
#coeff={'Творчий конкурс 1':1, 'Творчий конкурс 2':0, 'Творчий конкурс 3':0, 'Фаховий іспит 1':0,'Фаховий іспит 2':0,'Фаховий іспит 3':0}
#print(type(coeff))
#coeff['Творчий конкурс 1']

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def competition(website,coeff):

    time.sleep(0.2)

    soup =BeautifulSoup(urllib2.urlopen(website),"lxml")
    table = soup.find('table', class_='tablesaw tablesaw-stack tablesaw-sortable')
    
    #Parsing of data
    #data = table from website
    data=[]
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        data.append(cells)
        #words = cells[1].find(text=True)
        
    ##data = list(filter(None, data))
    #deleting empty cells from data 
    data=[x for x in data if x!=[]]
    
    #deleting trash from data 
    for i in range(0,len(data)):
        for j in range(0,len(data[0])):
            data[i][j]=data[i][j].find_all(text=True)
    ##print(data[0][1][0])
    
    #Parsing of stat
    #stat[0]=обсяг прийому, stat[1]=обсяг державного замовлення
    stat=soup.find_all('table', id='shortstat')
    try:
        stat=stat[0].find_all('td')
        stat=[stat[0],stat[1]]
        stat[0]=str(stat[0])[str(stat[0]).find(':')+2:len(str(stat[0]))-5]
        #print(str(stat[1]).find('Всього'))
        if str(stat[1]).find('Обсяг державного')==-1:
            stat[1]=0
        else:
            stat[1]=str(stat[1])[str(stat[1]).find(':')+2:len(str(stat[1]))-5]
        
        stat[0]=int(stat[0])
        stat[1]=int(stat[1])
    except IndexError:
        stat=[0,0]
    
    #calculating ofcompetition
    #ofcompetition = кількість, які поступили з правом на позаконкурсний вступ
    addexams=[]
    ofcompetition=0
    accepted=0
    grades=[]
    
    try:
        if len(data[0])==12:
            for i in range(0,len(data)):
                try:
                    if data[i][12-1][0]=='+' and data[i][9-1][0]=='+':
                        ofcompetition=ofcompetition+1
                except IndexError:
                    ofcompetition=0
            #grades = grades for accepted students (Зараховані)
            #without of-competition students
            #accepted =number ccepted students without of-competition students
            
            for i in range(0,len(data)):
                try:
                    if data[i][12-1][0]=='+' and data[i][9-1][0]=='—':
                        grades.append(data[i][4-1][0])
                        accepted=accepted+1
                except IndexError:
                    print('IndexError data[i] 1', website,data[i] )
            
            
            
            if coeff['Творчий конкурс 1']!=0 or coeff['Фаховий іспит 1']!=0 or coeff['Творчий конкурс 2']!=0 or coeff['Фаховий іспит 2']!=0 or coeff['Творчий конкурс 3']!=0 or coeff['Фаховий іспит 3']!=0:
              
                for i in range(0, len(data)):
                    if data[i][12-1][0]=='+' and data[i][9-1][0]=='—':
                        addexam=[float(x) for x in data[i][7-1] if is_number(x)]
                        #addexam=data[i][7-1][0]
                        #addexam=re.findall(r'\b\d+\b', addexam)
                        addexams.append(addexam)
        
        if len(data[0])==11:
            for i in range(0,len(data)):
                try:
                    if data[i][11-1][0]=='+' and data[i][8-1][0]=='+':
                        ofcompetition=ofcompetition+1
                except IndexError:
                    ofcompetition=0
                    print('IndexError data[i] 2',website, data[i] )
            #grades = grades for accepted students (Зараховані)
            #without of-competition students
            #accepted =number ccepted students without of-competition students
            
            for i in range(0,len(data)):
                try:
                    if data[i][11-1][0]=='+' and data[i][8-1][0]=='—':
                        grades.append(data[i][3-1][0])
                        accepted=accepted+1
                except IndexError:
                    print('IndexError data[i] 3',website, data[i] )
            
            
            
            if coeff['Творчий конкурс 1']!=0 or coeff['Фаховий іспит 1']!=0 or coeff['Творчий конкурс 2']!=0 or coeff['Фаховий іспит 2']!=0 or coeff['Творчий конкурс 3']!=0 or coeff['Фаховий іспит 3']!=0:
              
                for i in range(0, len(data)):
                    if data[i][11-1][0]=='+' and data[i][8-1][0]=='—':
                        addexam=[float(x) for x in data[i][6-1] if is_number(x)]
                        #addexam=data[i][7-1][0]
                        #addexam=re.findall(r'\b\d+\b', addexam)
                        addexams.append(addexam)
    except IndexError:
        print('IndexError data',website , data)
        
    
    median_of_addexams=[]
    
    if len(addexams)!=0:
        if len(addexams[0])!=1:
            try:
                for i in range(0,len(addexams[0])):
                    oneaddexams=[x[i] for x in addexams]
                    median_of_addexams.append(statistics.median(oneaddexams))
            except IndexError:
                print('IndexError addexams 1',website, addexams)
        else:
            try:                
                median_of_addexams=[statistics.median(addexams)]
            except TypeError:
                try:
                    addexams=[x for x in addexams if x!=[]]
                    addexams=[x[0] for x in addexams]
                    median_of_addexams=[statistics.median(addexams)]
                except IndexError:
                    print('IndexError addexams 2',website,addexams) 

                
    
            
        
    #accepted+ofcompetition= all accepted students
    
    #point[0]=fail score, point[1]=middle score, point[3]= succeed score
    points=[0,0,0]
    if stat[1]==0 or ofcompetition>=stat[1]:
        points=[1000,1000,1000]
    else:
        if accepted+ofcompetition>=stat[1]:
            try:
                points[0]=float(grades[stat[1]-1-ofcompetition])
            except IndexError:
                points[0]='?'
                print('IndexError stat',website,stat) 
            try:         
                points[1]=float(grades[stat[1]-ofcompetition-int(0.2*(stat[1]-ofcompetition))+1-1])
            except IndexError:
                points[1]='?'
                print('IndexError stat',website,stat)
            try:
                points[2]=float(grades[int(0.5*(stat[1]-ofcompetition))-1])
            except IndexError:
                points[2]='?'
                print('IndexError stat',website,stat)
        else:
            points=[0,0,0]
    ##print (points)
    
    
    #title of page: uni, napriam, napriamid and faculty
    
    
    title=soup.find_all('div', class_='title-page')
  
    
    
    #uni=university name
    if title[0].find_all('h3')!=[]:
        uni=title[0].find_all('h3')
        uni=str(uni)
        uni =uni[uni.find('tion">')+6:uni.find('</h3>')]
    else:
        uni=''
    
    #napriamid = napriam id, napriam = napriam name
    title=str(title)

    if title.find('Напрям')!=-1:
        if title.find('<br/>Спец')!=-1:
                napriam=title[title.find('Напрям')+8:title.find('<br/>Спец')]
                napriamid=napriam[0:8]
                napriam=napriam[9:len(napriam)]
        else:
            if title.find('факультет')!=-1:
                napriam=title[title.find('Напрям')+8:title.find(',<br/>факультет')]
                napriamid=napriam[0:8]
                napriam=napriam[9:len(napriam)]
            else:
                if title.find('<br>денна')!=-1:
                    napriam=title[title.find('Напрям')+8:title.find('<br>денна')]
                    napriamid=napriam[0:8]
                    napriam=napriam[9:len(napriam)]
                else:
                    napriam=title[title.find('Напрям')+8:title.find('<br/>денна')]
                    napriamid=napriam[0:8]
                    napriam=napriam[9:len(napriam)]
    else:
        napriam=''
        napriamid=''
    
    #faculty-faculty name
    if title.find('факультет')!=-1:
        faculty=title[title.find('факультет')+11:title.find('<br/>денна')]
    else:
        faculty=''
    
    
    #result=[uni,faculty, napriam id, napriam name, обсяг прийому, обсяг державного замовлення, all accepted students,points]
    #point[0]=fail score, point[1]=middle score, point[3]= succeed score
    #coeff=coefficients for subjects[Українська мова і література, Історія України, Математика, Біологія, Географія, Фізика, Хімія, Англійська мова, Іноземна мова (Англійська мова, Французька мова, Німецька мова, Іспанська мова), Російська мова]
    #set coefisients here by hands
    #coeff=[0.25,0,0.25,0,0,0.4,0,0,0,0]
    
    #додати ще творчі конкурси та фахові іспити
    
    result=[uni,faculty, napriamid, napriam, stat[0], stat[1], accepted+ofcompetition, points,median_of_addexams]
    return result
    
import csv
import glob
files = glob.glob("c:/users/lina/dropbox/myvstup/links_on_competitions/*.csv")
#print(files[6:])
for file in files [7:]:

    competitions_data = []
    f = open(file,'r',encoding='utf-8')
    city=str(file.split('\\')[1][:-12])
    for i in csv.reader(f):
        if len(i) != 0:
            website = 'http://www.vstup.info/2015/'+ str(i[1])[2:]
            coeff=ast.literal_eval(i[2])
            comp=competition(website,coeff)
            comp.append(coeff)
            comp.append(website)
            competitions_data.append(comp)
    
    competitions_data=[x for x in competitions_data if x!=[]]
    print(competitions_data)

    filename=str('c:/users/lina/dropbox/myvstup/competitions/' + city+'.csv')
    with open(filename, 'w',encoding='utf-8') as file:
        writer=csv.writer(file)
        writer.writerows(competitions_data)
        '''for competitions in competitions_data:
                for row in competitions:
                writer.writerow(row)
                
    filename=str(city+ '.csv')
    with open(filename, 'w',encoding='utf-8') as file:
        writer=csv.writer(file)
        writer.writerows(datauniv)'''

