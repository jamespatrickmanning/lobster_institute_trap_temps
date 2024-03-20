#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 06:46:41 2023
map with bathy from GEBCO (see "bathy_gebco_example.py" which explains where I got most of the code)
This version decides where to plot based on input lats, lons and evolved into "plot_wahle_sites.py" (see non-realtime_emolt/wahle on Linux2 kitchen)
Also checks the fisher-provided depths vs NGDC depths
@author: user
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import xarray as xr
import cartopy
import netCDF4
import cartopy.crs as ccrs
import conversions #homegrown functions need to be included
from dateutil.parser import parse
from get_depth_functions import get_depth, nearlonlat_zl,nearlonlat


bathy_file_path = Path('~/bathy/gebco_2022_n46.3184_s34.1895_w-77.168_e-59.5898.nc')# extracted from https://download.gebco.net/ 
bathy_ds = xr.open_dataset(bathy_file_path)
bathy_lon, bathy_lat, bathy_h = bathy_ds.elevation.lon, bathy_ds.elevation.lat, bathy_ds.elevation.values# had to specify "elevation" instead of "bathy"
bathy_h[bathy_h > 0] = 0 # removes land
bathy_conts = np.arange(-120, 5, 5)
fisherman='JordanDrouin' # specify lats>44 below and change "27" to "30
#fisherman='CurtBrown'
fisher='RW'

def getsite_latlon(site):
    df=pd.read_csv('/home/user/emolt_non_realtime/emolt/emolt_site.csv')
    df1=df[df['SITE']==site]
    return df1['LAT_DDMM'].values[0],df1['LON_DDMM'].values[0]

def getobs_tempdepth_latlon(lat,lon):
    """
    Function written by Jim Manning to get emolt data from url, return datetime, depth, and temperature.
    this version needed in early 2023 when "site" was no longer served via ERDDAP
    """
    url = 'https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&latitude='+str(lat)+'&longitude='+str(lon)+'+&orderBy(%22time%22)'
    df=pd.read_csv(url,skiprows=[1])
    df['time']=df['time (UTC)']
    temp=1.8 * df['sea_water_temperature (degree_C)'].values + 32 #converts to degF
    depth=df['depth (m)'].values
    time=[];
    for k in range(len(df)):
            time.append(parse(df.time[k]))
    #print('using erddap')            
    dfnew=pd.DataFrame({'temp':temp,'depth (m)':depth,'latitude (degrees_north)':lat,'longitude (degrees_east)':lon},index=time)
    return dfnew

#df=pd.DataFrame()
for j in range(26):
    try:
        [lat,lon]=getsite_latlon(fisher+str(j+1).zfill(2))# started using this on 25 May 2023 when NEFSC took away "site" from ERDDAP
    except:
        continue
    print(fisher+str(j+1).zfill(2))
    df1=getobs_tempdepth_latlon(lat,lon)
    df1['SITE']=fisher+str(j+1).zfill(2)
    if j==0:
        df=df1
    else:
        df=pd.concat([df,df1])
df=df[df['latitude (degrees_north)']>44.]# Jordan
#df=df[df['latitude (degrees_north)']<43.8]# Curt
#df['datet']=pd.to_datetime(df['time (UTC)'])
df['datet']=pd.to_datetime(df.index)
listsites=list(set(df['SITE'].values))
lats,lons,depth,depthngdc,year=[],[],[],[],[]
for k in listsites:
    df1=df[df['SITE']==k]        
    lats.append(df1['latitude (degrees_north)'].values[0])
    lons.append(df1['longitude (degrees_east)'].values[0])
    depth.append(df1['depth (m)'].values[0])
    depthngdc.append(-1*get_depth(df1['longitude (degrees_east)'].values[0],df1['latitude (degrees_north)'].values[0],0.4))
    year.append(min(df1['datet']).year)

dfn=pd.read_excel('VemcoLog22.xlsx')# 2022 sites
dfn=dfn[dfn['Fisherman']==fisherman]
for k in range(len(dfn)):
    listsites.append('RW'+str(k+27).zfill(2))# 27 in Curt Brown case and 30 in J Drouin case
    [la,lo]=conversions.dm2dd(dfn['lat'].values[k],dfn['lon'].values[k])
    lats.append(la)
    lons.append(lo)
    depth.append(conversions.fth2m(dfn['Depth(ft)'].values[k]/6.))
    depthngdc.append(-1*get_depth(lo,la,0.4))
    year.append(2022) 

filename='2023 HOBO Logs.csv'# 2023 sites
#for j in [1,4]:# Curt Brown
for j in [7,10,13]:# Jordan Drouin
    with open(filename, 'r') as f:
      for line in f:
        row=line.split(',')
        if row[0]=='HOBO':
            sn=row[j]
        if row[0]=='LON':
            lon=float(row[j])
        if row[0]=='LAT':
            lat=float(row[j])  
        if row[0]=='Water Column Depth (m)':
            dep=float(row[j])
        if row[0]=='Captain':
            capt=row[j]        
        if row[0]=='eMOLT_site':
            site=row[j]
    f.close()
    listsites.append(site)# 27 in Curt Brown case
    lats.append(lat)
    lons.append(lon)
    depth.append(dep)
    depthngdc.append(-1*get_depth(lon,lat,0.4))
    year.append(2023)
p=(max(lats)-min(lats))/10.# added a little around the edges
ext=[min(lons)-p, max(lons)+p, min(lats)-p,max(lats)+p]# used to delimit geographic "extent"

coord = ccrs.PlateCarree()
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(111, projection=coord)
ax.set_extent(ext, crs=coord);
bathy = ax.contourf(bathy_lon, bathy_lat, bathy_h, bathy_conts, transform=coord, cmap="Blues_r")
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="k", alpha=0.5, linestyle="--")
gl.xlabels_top = False
gl.ylabels_right = False
gl.ylines = True
gl.xlines = True
fig.colorbar(bathy, ax=ax, orientation="horizontal", label="Depth (m)", shrink=0.7, pad=0.08, aspect=40);
coast = cartopy.feature.GSHHSFeature(scale="full")
ax.add_feature(coast, linewidth=1)
feature = cartopy.feature.NaturalEarthFeature(name="coastline", category="physical", scale="10m", zorder=1,edgecolor="0.5", facecolor="0.8")
#ax.add_feature(feature)
ax.scatter(lons, lats, zorder=5, color="red", s=4,label="Wahle Lab settlement trap temperature sites ("+str(min(df['datet']))+"-"+str(max(df['datet']))+")")
for k in range(len(lats)):
    if (listsites[k]=='RW04') | (listsites[k]=='RW29') | (listsites[k]=='RW34') | (listsites[k]=='RW35\n'): # sites that overlap other sites
        add=.0075 # 0.012 in Curt Brown case
        addlo=0.
    elif (listsites[k]=='RW33') :
        addlo=.04
        add=0.
    else:
        add=0.
        addlo=0.
    ax.text(lons[k]+addlo, lats[k]+add,listsites[k][2:4]+' '+str(year[k]),va='bottom',ha='center',weight='bold',color='magenta',zorder=20)
    ax.text(lons[k]+addlo, lats[k]+add-0.001,str(int(depth[k]))+'m ('+str(int(depthngdc[k]))+')',va='top',ha='center',weight='bold',color='magenta',zorder=20)
#fig.legend(bbox_to_anchor=(0.7, 0.4))
plt.title(fisherman+' region Lobster Institute settlement traps temperature "RW" sites ('+str(min(df['datet']).year)+"-"+str(max(df['datet']).year+2)+") with NGDC depths in ()")
tr2 = ccrs.Stereographic(central_latitude=43., central_longitude=-68.)
sub_ax = plt.axes([0.6, 0.3, 0.2, 0.2], projection=ccrs.Stereographic(central_latitude=43., central_longitude=-68.))
sub_ax.set_extent([-71., -67., 41., 45.])# Northeast Shelf
#x_co = [-70.5, -67., -67., -70.5, -70.5]
#y_co = [42.5, 42.5, 45, 45, 42.5]
x_co = [ext[0],ext[1],ext[1],ext[0],ext[0]]
y_co = [ext[2],ext[2],ext[3],ext[3],ext[2]]
sub_ax.add_feature(feature)
sub_ax.plot(x_co, y_co, transform=coord, zorder=1, color="red")
#ax.text(np.mean([ext[0],ext[1]]),np.mean([ext[2],ext[3]]), fisherman, fontsize=14)
fig.savefig(fisherman+'_RW_sites.png')
