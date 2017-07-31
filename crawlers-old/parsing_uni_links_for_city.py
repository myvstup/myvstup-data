# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 15:52:17 2016

@author: Lina
"""

from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
    
city='м. Київ'

##blabla
website='http://www.vstup.info/2015/i2015o27.html#reg'
soup =BeautifulSoup(urllib2.urlopen(website),"lxml")

divuniv=soup.find_all('div', id="univ")
divakad=soup.find_all('div', id="akad")
divinst=soup.find_all('div', id="inst")


datauniv=[]
for row in divuniv[0].find_all('tr'):
    cells = row.find_all('td')
    datauniv.append(cells)

dataakad=[]
for row in divakad[0].find_all('tr'):
    cells = row.find_all('td')
    dataakad.append(cells)
    
datainst=[]
for row in divinst[0].find_all('tr'):
    cells = row.find_all('td')
    datainst.append(cells)

for i in range(0,len(datauniv)):
   datauniv[i]=[datauniv[i][0].find_all('a')[0].get('href'),
            datauniv[i][0].find_all('a')[0].get('title')]

for i in range(0,len(dataakad)):
   dataakad[i]=[dataakad[i][0].find_all('a')[0].get('href'),
            dataakad[i][0].find_all('a')[0].get('title')]

for i in range(0,len(datainst)):
   datainst[i]=[datainst[i][0].find_all('a')[0].get('href'),
            datainst[i][0].find_all('a')[0].get('title')]
            
#print(datauniv,dataakad,datainst)
#print(datauniv[1][0].find_all('a')[0].get('href'))

#print(datauniv[0][0])

import csv

filename=str(city+ '.csv')
with open(filename, 'w',encoding='utf-8') as file:
    writer=csv.writer(file)
    writer.writerows(datauniv)
    writer.writerows(dataakad)
    writer.writerows(datainst)    
    
'''
filename=str(city+'.txt')
#print(str(city+'.txt'))
file=open(filename, 'w')
file.close()
'''