#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 10:54:21 2024
Routine to read Lobster Institute's HOBO surface temps
@author: JiM 
"""
filename='2023 HOBO Logs.csv'

import pandas as pd
from conversions import dd2dm,c2f,m2fth
for j in [1,4,7,10,13]:
    dfo=pd.DataFrame() # output dataframe
    with open(filename, 'r') as f:
      for line in f:
        row=line.split(',')
        if row[0]=='HOBO':
            sn=row[j]
        if row[0]=='LON':
            lon=row[j]
        if row[0]=='LAT':
            lat=row[j]  
        if row[0]=='Water Column Depth (m)':
            dep=round(m2fth(float(row[j])),1)
        if row[0]=='Captain':
            capt=row[j]        
        if row[0]=='eMOLT_site':
            site=row[j]
    f.close()
    [ladm,lodm]=dd2dm(float(lat),float(lon))
    print('insert into emolt_site values ('+site+','+str(ladm)+','+str(lodm)+','+'%0.1f' %dep+',Rick,Wahle,,,'+capt+',,,,,,,,,,,,);')
            
    df=pd.read_csv('2023 HOBO Logs.csv',skiprows=7)

    
    if j==1:
        df=df[pd.notnull(df['Date'])]
        dfo['datet']=pd.to_datetime(df['Date'])
    elif j==4:
        df=df[pd.notnull(df['Date.1'])]
        dfo['datet']=pd.to_datetime(df['Date.1'])
    elif j==7:
        df=df[pd.notnull(df['Date.2'])]
        dfo['datet']=pd.to_datetime(df['Date.2'])
    elif j==10:
        df=df[pd.notnull(df['Date.3'])]
        dfo['datet']=pd.to_datetime(df['Date.3'])
    elif j==13:
        df=df[pd.notnull(df['Date.4'])]
        dfo['datet']=pd.to_datetime(df['Date.4'])    
    dfo['site']=site
    dfo['sn']=sn
    dfo['ps']=2
    
    date_str,yd,tempf=[],[],[]
    for k in range(len(dfo)):
            yd.append(dfo['datet'][k].timetuple().tm_yday+(dfo['datet'][k].hour+(dfo['datet'][k].minute)/60)/24.)
            if j==1:
                tempf.append(c2f(df['Temperature (°C)'][k])[0])
                date_str.append(pd.to_datetime(df['Date'][k]).strftime('%Y-%m-%d %H:%M:%S'))
            elif j==4:
                tempf.append(c2f(df['Temperature (°C).1'][k])[0])
                date_str.append(pd.to_datetime(df['Date.1'][k]).strftime('%Y-%m-%d %H:%M:%S'))
            elif j==7:
                tempf.append(c2f(df['Temperature (°C).2'][k])[0])
                date_str.append(pd.to_datetime(df['Date.2'][k]).strftime('%Y-%m-%d %H:%M:%S'))
            elif j==10:
                tempf.append(c2f(df['Temperature (°C).3'][k])[0])
                date_str.append(pd.to_datetime(df['Date.3'][k]).strftime('%Y-%m-%d %H:%M:%S'))
            elif j==13:
                tempf.append(c2f(df['Temperature (°C).4'][k])[0])
                date_str.append(pd.to_datetime(df['Date.4'][k]).strftime('%Y-%m-%d %H:%M:%S'))
    dfo['date_str']=date_str
    dfo['yd']=yd
    dfo['tempf']=tempf
    dfo['salt']=99.999
    dfo['dep']=1# note at "dep" which is water_column depth
    cols=['site','sn','ps','date_str','yd','tempf','salt','dep']
    dfo=dfo[cols]
    dfo.to_csv(site+'h'+sn[-4:]+'02'+site[2:]+'.dat',float_format='%10.3f',index=False,header=False)


