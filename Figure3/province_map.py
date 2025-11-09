#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 11:54:35 2024

@author: hy4174
"""

import geopandas
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import PercentFormatter
import numpy as np
import math
from matplotlib.colors import LinearSegmentedColormap
#import cartopy.crs as ccrs
#%%
China = geopandas.read_file('/Users/hy4174/Documents/Hydrogen/China_map/2020_map/2020_map/province.shp')
China.loc[China.PINYIN_NAM=='Xinjiang Wei', 'PINYIN_NAM']='Xinjiang'
China.loc[China.PINYIN_NAM=='Ningxia Hui', 'PINYIN_NAM']='Ningxia'
China.loc[China.PINYIN_NAM=='Xizang', 'PINYIN_NAM']='Tibet'
China.loc[China.PINYIN_NAM=='Guangxi Zhuang', 'PINYIN_NAM']='Guangxi'
China.loc[China.PINYIN_NAM=='Neimenggu', 'PINYIN_NAM']='Inner Mongolia'
China.loc[China.PINYIN_NAM=='chongqingshi', 'PINYIN_NAM']='Chongqing'
China.loc[China.PINYIN_NAM=='gansu', 'PINYIN_NAM']='Gansu'

China = China.to_crs(4326)

center=pd.read_excel('/Users/hy4174/Documents/Hydrogen/China_map/2020_map/2020_map/capital_center.xlsx')
#%%
all_project=pd.read_csv('/Users/hy4174/Documents/Hydrogen/all_projects.csv')
all_project=all_project.replace('.','0')
all_project['zone']=all_project['gen_load_zone']
all_project['gen_capacity_limit_mw']=all_project['gen_capacity_limit_mw'].astype(float)/1000

potential=all_project.groupby(['zone','technology'])['gen_capacity_limit_mw'].sum().reset_index()
potential.loc[potential.zone=='West_Inner_Mongolia','zone']='Inner Mongolia'
potential.loc[potential.zone=='East_Inner_Mongolia','zone']='Inner Mongolia'

potential.loc[potential.technology=='Commercial_PV','technology']='PV'
potential.loc[potential.technology=='Residential_PV','technology']='PV'
potential.loc[potential.technology=='Central_PV','technology']='PV'
potential=potential.loc[potential.technology.isin(['Wind','Offshore_Wind','PV']),:]
potential.loc[potential.technology.isin(['Offshore_wind','Wind']),'gen_capacity_limit_mw']=potential.loc[potential.technology.isin(['Offshore_wind','Wind']),'gen_capacity_limit_mw']*2.6
potential=potential.groupby(['zone','technology'])['gen_capacity_limit_mw'].sum().reset_index()
potential=potential.pivot(index='zone',columns='technology',values='gen_capacity_limit_mw')


file1='dispatch_all.csv'
file2='carbon_emissions_by_project.csv'
file3='costs_capacity_all_projects.csv'
file4='costs_operations.csv'
file5='costs_transmission_capacity.csv'
file6='capacity_all.csv'
file7='transmission_new_capacity.csv'
file8='capacity_gen_new_lin.csv'
file9='capacity_stor_new_lin.csv'
file10='dispatch_H2.csv'
file11='stor_ccs.csv'
file12='imports_exports.csv'
file13='imports_exports_H2.csv'
file14='imports_exports_ccs.csv'
file15='load_balance.csv'
file16='H2_balance.csv'
    
test_id=[
         'Hydrogen_400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day_H2_expand_flat'
         ]

capacity_province=pd.DataFrame()
generation_province=pd.DataFrame()
generation_H2_province=pd.DataFrame()

transmission_province=pd.DataFrame()
transmission_H2_province=pd.DataFrame()

import_province = pd.DataFrame()
import_H2_province = pd.DataFrame()
load_H2_province = pd.DataFrame()
load_province = pd.DataFrame()

for case in test_id:
    path='/Users/hy4174/Documents/Hydrogen/data/'+case+'/results/'
    dispatch_path=path+file1
    capacity_path=path+file6
    carbon_path=path+file2
    capacity_cost_path=path+file3
    operation_cost_path=path+file4
    transmission_cost_path=path+file5
    transmission_new_capacity_path=path+file7
    capacity_new_path=path+file8
    stor_new_path=path+file9
    H2_path=path+file10
    ccs_path=path+file11
    import_path=path+file12
    import_H2_path=path+file13
    import_ccs_path=path+file14
    load_balance_path=path+file15
    H2_balance_path=path+file16
    
    load_H2_tmp = pd.read_csv(H2_balance_path)
    load_H2_tmp.H2_mw=load_H2_tmp.H2_mw/10**6*load_H2_tmp.timepoint_weight    
    load_H2_tmp.loc[load_H2_tmp.zone=='West_Inner_Mongolia','zone'] = 'Inner Mongolia'
    load_H2_tmp.loc[load_H2_tmp.zone=='East_Inner_Mongolia','zone'] = 'Inner Mongolia'    
    load_H2_province_tmp=load_H2_tmp.groupby(['zone'])[['H2_mw']].sum().reset_index()
    load_H2_province_tmp['scenario']=case
    load_H2_province=pd.concat([load_H2_province,load_H2_province_tmp])
    
    load_tmp = pd.read_csv(load_balance_path)
    load_tmp.load_mw=load_tmp.load_mw/10**6*load_tmp.timepoint_weight    
    load_tmp.loc[load_tmp.zone=='West_Inner_Mongolia','zone'] = 'Inner Mongolia'
    load_tmp.loc[load_tmp.zone=='East_Inner_Mongolia','zone'] = 'Inner Mongolia'    
    load_province_tmp=load_tmp.groupby(['zone'])[['load_mw']].sum().reset_index()
    load_province_tmp['scenario']=case
    load_province=pd.concat([load_province,load_province_tmp])
    
    capacity_tmp=pd.read_csv(capacity_path)
    capacity_tmp.capacity_mw=capacity_tmp.capacity_mw/10**3
    capacity_tmp.capacity_mwh=capacity_tmp.capacity_mwh/10**6
    capacity_province_tmp=capacity_tmp.groupby(['load_zone','technology'])[['capacity_mwh','capacity_mw']].sum().reset_index()
    
    West= capacity_province_tmp.loc[capacity_province_tmp.load_zone=='West_Inner_Mongolia',:]
    East= capacity_province_tmp.loc[capacity_province_tmp.load_zone=='East_Inner_Mongolia',:]
    Inner_Mongolia=pd.merge(West,East, on=['technology'], how='outer').fillna(0)
    
    Inner_Mongolia_capacity=pd.DataFrame({
        'load_zone': 'Inner Mongolia',
        'technology': Inner_Mongolia.technology,
        'capacity_mwh':Inner_Mongolia.capacity_mwh_x + Inner_Mongolia.capacity_mwh_y,
        'capacity_mw': Inner_Mongolia.capacity_mw_x + Inner_Mongolia.capacity_mw_y
        })
    
    capacity_province_tmp=pd.concat([capacity_province_tmp,Inner_Mongolia_capacity],ignore_index=True)
    capacity_province_tmp=capacity_province_tmp.drop(capacity_province_tmp[capacity_province_tmp['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
    capacity_province_tmp['scenario']=case
    capacity_province=pd.concat([capacity_province,capacity_province_tmp])
    
    generation_tmp=pd.read_csv(dispatch_path)
    generation_tmp.power_mw=generation_tmp.power_mw/10**6*generation_tmp.timepoint_weight
    #generation_ele_tmp = generation_tmp.loc[generation_tmp.technology == 'Electrolyzer',:]
    generation_ele_tmp = generation_tmp
    
    generation_ele_tmp.loc[generation_ele_tmp.load_zone=='West_Inner_Mongolia','load_zone'] = 'Inner Mongolia'
    generation_ele_tmp.loc[generation_ele_tmp.load_zone=='East_Inner_Mongolia','load_zone'] = 'Inner Mongolia'    
    
    generation_province_tmp=generation_ele_tmp.groupby(['load_zone'])[['power_mw']].sum().reset_index()
    
    
    generation_province_tmp.power_mw =  generation_province_tmp.power_mw
    
    generation_province_tmp['scenario']=case
    generation_province=pd.concat([generation_province,generation_province_tmp])
    
    generation_H2_tmp=pd.read_csv(H2_path)
    generation_H2_tmp.H2_mw=generation_H2_tmp.H2_mw*generation_H2_tmp.timepoint_weight/10**6
    #generation_H2_tmp = generation_H2_tmp.loc[generation_H2_tmp.technology.isin(['Electrolyzer', 'SMR', 'Gasification']),:]
    
    generation_H2_tmp.loc[generation_H2_tmp.load_zone=='West_Inner_Mongolia','load_zone'] = 'Inner Mongolia'
    generation_H2_tmp.loc[generation_H2_tmp.load_zone=='East_Inner_Mongolia','load_zone'] = 'Inner Mongolia'    
    generation_H2_province_tmp=generation_H2_tmp.groupby(['load_zone'])[['H2_mw']].sum().reset_index()
    #this is used to calculate total H2 production

    generation_H2_technlogy_tmp=generation_H2_tmp.groupby(['technology'])[['H2_mw']].sum().reset_index()
    
    generation_H2_province_tmp['scenario']=case
    generation_H2_province=pd.concat([generation_H2_province,generation_H2_province_tmp])
    
    import_tmp = pd.read_csv(import_path)
    import_tmp.net_imports_mw=import_tmp.net_imports_mw/10**6 * import_tmp.timepoint_weight
    import_tmp.loc[import_tmp.load_zone=='West_Inner_Mongolia','load_zone'] = 'Inner Mongolia'
    import_tmp.loc[import_tmp.load_zone=='East_Inner_Mongolia','load_zone'] = 'Inner Mongolia'    
    import_province_tmp=import_tmp.groupby(['load_zone'])[['net_imports_mw']].sum().reset_index()    
    import_province_tmp['scenario']=case
    import_province=pd.concat([import_province,import_province_tmp])

    import_H2_tmp = pd.read_csv(import_H2_path)
    import_H2_tmp.net_imports_H2_mw=import_H2_tmp.net_imports_H2_mw/10**6 * import_H2_tmp.timepoint_weight
    import_H2_tmp.loc[import_H2_tmp.load_zone=='West_Inner_Mongolia','load_zone'] = 'Inner Mongolia'
    import_H2_tmp.loc[import_H2_tmp.load_zone=='East_Inner_Mongolia','load_zone'] = 'Inner Mongolia'    
    import_H2_province_tmp=import_H2_tmp.groupby(['load_zone'])[['net_imports_H2_mw']].sum().reset_index()    
    import_H2_province_tmp['scenario']=case
    import_H2_province=pd.concat([import_H2_province,import_H2_province_tmp])
    
    transmission_new_capacity=pd.read_csv(transmission_new_capacity_path)  
    transmission_H2=transmission_new_capacity.loc[transmission_new_capacity.transmission_line.str.contains('H2'),:]
    transmission_H2.loc[transmission_H2.load_zone_from=='East_Inner_Mongolia','load_zone_from']='Inner Mongolia'
    transmission_H2.loc[transmission_H2.load_zone_from=='West_Inner_Mongolia','load_zone_from']='Inner Mongolia'
    transmission_H2.loc[transmission_H2.load_zone_to=='East_Inner_Mongolia','load_zone_to']='Inner Mongolia'
    transmission_H2.loc[transmission_H2.load_zone_to=='West_Inner_Mongolia','load_zone_to']='Inner Mongolia'
    transmission_H2=transmission_H2.groupby(['load_zone_from','load_zone_to'])['new_build_transmission_capacity_mw'].sum().reset_index()
    transmission_H2['scenario'] = case
    transmission_H2_province = pd.concat([transmission_H2_province, transmission_H2])
    
    transmission=transmission_new_capacity.loc[~transmission_new_capacity.transmission_line.str.contains('H2'),:]
    transmission.loc[transmission.load_zone_from=='East_Inner_Mongolia','load_zone_from']='Inner Mongolia'
    transmission.loc[transmission.load_zone_from=='West_Inner_Mongolia','load_zone_from']='Inner Mongolia'
    transmission.loc[transmission.load_zone_to=='East_Inner_Mongolia','load_zone_to']='Inner Mongolia'
    transmission.loc[transmission.load_zone_to=='West_Inner_Mongolia','load_zone_to']='Inner Mongolia'
    transmission=transmission.groupby(['load_zone_from','load_zone_to'])['new_build_transmission_capacity_mw'].sum().reset_index()
    transmission['scenario'] = case
    transmission_province = pd.concat([transmission_province, transmission])
    '''
    generation_tmp=pd.read_csv(dispatch_path)
    generation_tmp.power_mw=generation_tmp.power_mw*generation_tmp.timepoint_weight/10**6
    generation_province_tmp=generation_tmp.groupby(['load_zone','technology'])['power_mw'].sum().reset_index()
    
    Inner_Mongolia_generation=pd.DataFrame({
        'load_zone': 'Inner Mongolia',
        'technology': generation_province_tmp.loc[generation_province_tmp.load_zone=='East_Inner_Mongolia','technology'].values,
        'power_mw':generation_province_tmp.loc[generation_province_tmp.load_zone=='East_Inner_Mongolia','power_mw'].values+generation_province_tmp.loc[generation_province_tmp.load_zone=='West_Inner_Mongolia','power_mw'].values,
        })
    
    generation_province_tmp=generation_province_tmp.append(Inner_Mongolia_generation,ignore_index=True)
    generation_province_tmp=generation_province_tmp.drop(generation_province_tmp[generation_province_tmp['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
    generation_province=generation_province.append(generation_province_tmp)
    '''
    

#%%
transmission_H2_province=transmission_H2_province.merge(center,left_on='load_zone_from',right_on='load_zone', how='left')
transmission_H2_province=transmission_H2_province.merge(center,left_on='load_zone_to',right_on='load_zone', how='left')

transmission_H2_province=transmission_H2_province.rename(columns={'lon_x':'lon_from',
                                                'lat_x':'lat_from',
                                                'lon_y':'lon_to',
                                                'lat_y':'lat_to'})

#transmission_H2_province=transmission_H2_province.drop(transmission_H2_province[transmission_H2_province.new_build_transmission_capacity_mw==0].index)

transmission_H2_400 = transmission_H2_province.loc[transmission_H2_province.scenario == 'Hydrogen_400ppm_1period_36day',:]
transmission_H2_expand = transmission_H2_province.loc[transmission_H2_province.scenario == 'Hydrogen_400ppm_1period_36day_H2_expand_flat',:]

transmission_H2_delta = transmission_H2_400.copy()
transmission_H2_delta.new_build_transmission_capacity_mw = transmission_H2_expand.new_build_transmission_capacity_mw.values - transmission_H2_400.new_build_transmission_capacity_mw.values

transmission_province=transmission_province.merge(center,left_on='load_zone_from',right_on='load_zone', how='left')
transmission_province=transmission_province.merge(center,left_on='load_zone_to',right_on='load_zone', how='left')

transmission_province=transmission_province.rename(columns={'lon_x':'lon_from',
                                                'lat_x':'lat_from',
                                                'lon_y':'lon_to',
                                                'lat_y':'lat_to'})

#transmission_province=transmission_province.drop(transmission_province[transmission_province.new_build_transmission_capacity_mw==0].index)

transmission_ele_400 = transmission_province.loc[transmission_province.scenario == 'Hydrogen_400ppm_1period_36day',:]
transmission_ele_expand = transmission_province.loc[transmission_province.scenario == 'Hydrogen_400ppm_1period_36day_H2_expand_flat',:]

transmission_delta = transmission_ele_400.copy()
transmission_delta.new_build_transmission_capacity_mw = transmission_ele_expand.new_build_transmission_capacity_mw.values - transmission_ele_400.new_build_transmission_capacity_mw.values
#450
generation_ele=generation_province.loc[generation_province.scenario=='Hydrogen_400ppm_1period_36day',['load_zone','power_mw']]
generation_hydrogen=generation_H2_province.loc[generation_H2_province.scenario=='Hydrogen_400ppm_1period_36day',['load_zone','H2_mw']]

generation_ele_expand=generation_province.loc[generation_province.scenario=='Hydrogen_400ppm_1period_36day_H2_expand_flat',['load_zone','power_mw']]
generation_hydrogen_expand=generation_H2_province.loc[generation_H2_province.scenario=='Hydrogen_400ppm_1period_36day_H2_expand_flat',['load_zone','H2_mw']]
generation_hydrogen_expand.loc[:,'H2_mw'].sum()


import_ele=import_province.loc[import_province.scenario=='Hydrogen_400ppm_1period_36day',['load_zone','net_imports_mw']]
import_hydrogen=import_H2_province.loc[import_H2_province.scenario=='Hydrogen_400ppm_1period_36day_flat',['load_zone','net_imports_H2_mw']]

import_ele_expand=import_province.loc[import_province.scenario=='Hydrogen_400ppm_1period_36day_H2_expand_flat',['load_zone','net_imports_mw']]
import_hydrogen_expand=import_H2_province.loc[import_H2_province.scenario=='Hydrogen_400ppm_1period_36day_H2_expand_flat',['load_zone','net_imports_H2_mw']]
import_hydrogen_expand.loc[import_hydrogen_expand.net_imports_H2_mw>0,'net_imports_H2_mw'].sum()

import_ele_delta = import_ele_expand.copy()
import_ele_delta.net_imports_mw = import_ele_expand.net_imports_mw - import_ele.net_imports_mw

import_H2_delta = import_hydrogen_expand.copy()
import_H2_delta.net_imports_H2_mw = import_hydrogen_expand.net_imports_H2_mw - import_hydrogen.net_imports_H2_mw
#China_hydrogen_400=China_hydrogen_400.fillna(0)

ele_expand=load_province.loc[load_province.scenario=='Hydrogen_400ppm_1period_36day_H2_expand_flat',['zone','load_mw']]
H2_expand=load_H2_province.loc[load_H2_province.scenario=='Hydrogen_400ppm_1period_36day_H2_expand_flat',['zone','H2_mw']]


re_ele=China.merge(generation_ele,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_H2=China.merge(generation_hydrogen,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')

re_expand_ele=China.merge(generation_ele_expand,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_expand_H2=China.merge(generation_hydrogen_expand,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_expand_ele.loc[re_expand_ele.power_mw.isna(),'power_mw'] = 0
re_expand_H2.loc[re_expand_H2.H2_mw.isna(),'H2_mw'] = 0

re_expand_load=China.merge(ele_expand,left_on=['PINYIN_NAM'],right_on=['zone'],how='outer')
re_expand_load_H2=China.merge(H2_expand,left_on=['PINYIN_NAM'],right_on=['zone'],how='outer')
re_expand_load.loc[re_expand_load.load_mw.isna(),'load_mw'] = 0
re_expand_load_H2.loc[re_expand_load_H2.H2_mw.isna(),'H2_mw'] = 0



re_delta = re_ele.copy()
re_delta.power_mw = re_expand_ele.power_mw - re_ele.power_mw

re_H2_delta = re_H2.copy()
re_H2_delta.H2_mw = re_expand_H2.H2_mw - re_H2.H2_mw

#trade
trade_ele=China.merge(import_ele,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
trade_H2=China.merge(import_hydrogen,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')

trade_expand_ele=China.merge(import_ele_expand,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
trade_expand_H2=China.merge(import_hydrogen_expand,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')

trade_expand_ele.loc[trade_expand_ele.net_imports_mw.isna(),'net_imports_mw'] = 0
trade_expand_H2.loc[trade_expand_H2.net_imports_H2_mw.isna(),'net_imports_H2_mw'] = 0

trade_delta = China.merge(import_ele_delta,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
trade_H2_delta = China.merge(import_H2_delta,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')


#hydrogen storage
capacity_storage=capacity_province.loc[capacity_province.scenario=='Hydrogen_400ppm_1period_36day',:].pivot(index='load_zone',columns=['technology'],values='capacity_mwh').reset_index()
capacity_storage['Storage']=capacity_storage.Salt_cavern.fillna(0) + capacity_storage.Tank.fillna(0)

capacity_storage_expand=capacity_province.loc[capacity_province.scenario=='Hydrogen_400ppm_1period_36day_H2_expand_flat',:].pivot(index='load_zone',columns=['technology'],values='capacity_mwh').reset_index()
capacity_storage_expand['Storage']=capacity_storage_expand.Salt_cavern.fillna(0) + capacity_storage_expand.Tank.fillna(0)

capacity_storage_delta = capacity_storage.copy()
capacity_storage_delta.Storage = capacity_storage_expand.Storage - capacity_storage.Storage

re_storage=China.merge(capacity_storage,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_storage_expand=China.merge(capacity_storage_expand,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_storage_delta=China.merge(capacity_storage_delta,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')

capacity_hydrogen_400=capacity_province.loc[capacity_province.scenario=='Hydrogen_400ppm_1period_36day_H2_expand_flat',:]
China_hydrogen_400_mw=capacity_hydrogen_400[['load_zone','technology','capacity_mw']].pivot(index='load_zone',columns=['technology'],values='capacity_mw').reset_index()
re_400_mw=China.merge(China_hydrogen_400_mw,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_400_mw['Generation'] = re_400_mw.Hydro.fillna(0) + re_400_mw.Nuclear.fillna(0) + re_400_mw.Offshore_Wind.fillna(0) + re_400_mw.Solar.fillna(0) + re_400_mw.Wind.fillna(0)
re_400_mw.loc[re_400_mw.Generation.isna(),'Generation'] = 0
re_400_mw.loc[re_400_mw.Electrolyzer.isna(),'Electrolyzer'] = 0

re_potential=China.merge(potential,left_on=['PINYIN_NAM'],right_on=['zone'],how='outer')


#%%
bins1=[0,250,500,750,1000]
bins2=[0,50,100,150,200]
bins3=[-250,-100,0,100,250]
bins4=[-10,-5,0,5,10]

#bounds = np.linspace(-1, 1, 9)
#norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')

divergent='bwr_r'
divergent='seismic_r'
directional = 'YlOrRd'

norm_direction1 = colors.Normalize(vmin= 0, vmax= 1000)
norm_direction2 = colors.Normalize(vmin= 0, vmax= 500)
norm_direction3 = colors.Normalize(vmin= 0, vmax= 200)
norm_diverge = colors.TwoSlopeNorm(vcenter=0, vmin=-250, vmax=250)

# Define the colors for the colormap
colors1 = [(1, 1, 1), (1, 0, 0)]  # White to Red

# Create the colormap

cmap = LinearSegmentedColormap.from_list("white_to_red", colors1)

cmap = plt.cm.get_cmap("YlOrRd")
colors = [(1, 1, 1)] + [cmap(i) for i in range(cmap.N)]
new_cmap = LinearSegmentedColormap.from_list("WhiteYlOrRd", colors, N=cmap.N+1)

# For seismic_r example:
cmap2 = plt.cm.get_cmap("Blues")
colors2 = [(1, 1, 1)] + [cmap2(i) for i in range(cmap2.N)]
new_cmap2 = LinearSegmentedColormap.from_list("WhiteBlues", colors2, N=cmap2.N+1)

cmap3 = plt.cm.get_cmap("RdPu")
colors3 = [(1, 1, 1)] + [cmap3(i) for i in range(cmap3.N)]
new_cmap3 = LinearSegmentedColormap.from_list("WhiteRdPu", colors3, N=cmap3.N+1)

fig, ((ax1,ax2,ax3),(ax4,ax5,ax6),(ax7,ax8,ax9))=plt.subplots(ncols=3,nrows=3, sharex=True, sharey=True)

plt.subplots_adjust(
                    wspace=0.1, 
                    hspace=0.1
                    )

re_expand_load.plot(ax=ax1, column='load_mw', norm = norm_direction1,
                   cmap=new_cmap,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25
                   )     


re_expand_ele.plot(ax=ax2, column='power_mw', 
                           norm = norm_direction1,
                           cmap=new_cmap,
                           #scheme='UserDefined', 
                           #classification_kwds={'bins': bins1},
                           edgecolor='grey',
                           linewidth=0.25,
                           #missing_kwds= dict(color = "lightgrey",aspect='equal')
                           )

trade_expand_ele.plot(ax=ax3, column='net_imports_mw', norm = norm_diverge,
                   cmap=divergent,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   #missing_kwds= dict(color = "lightgrey",aspect='equal')
                   )


xx = np.vstack([transmission_ele_expand.lon_from,transmission_ele_expand.lon_to])
yy = np.vstack([transmission_ele_expand.lat_from,transmission_ele_expand.lat_to])
capacity=transmission_ele_expand.new_build_transmission_capacity_mw.values

#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    if (i==0) | (abs(i)<1):
        continue
    elif i>1:
        ax3.plot(xx[:,i_id],yy[:,i_id],'orange',linewidth=math.log10(i)/3,alpha=0.7)
        

re_expand_load_H2.plot(ax=ax4, column='H2_mw', norm = norm_direction1,
                   cmap=new_cmap,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25
                   )     


re_expand_H2.plot(ax=ax5, column='H2_mw', norm = norm_direction1,
                   cmap=new_cmap,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   #missing_kwds= dict(color = "lightgrey",aspect='equal')
                   )

trade_expand_H2.plot(ax=ax6, column='net_imports_H2_mw', norm = norm_diverge,
                   cmap=divergent,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   #missing_kwds= dict(color = "lightgrey",aspect='equal')
                   )

xx = np.vstack([transmission_H2_expand.lon_from,transmission_H2_expand.lon_to])
yy = np.vstack([transmission_H2_expand.lat_from,transmission_H2_expand.lat_to])
capacity=transmission_H2_expand.new_build_transmission_capacity_mw.values
 #capacity[capacity<1]=1
 #colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    if (i==0) | (abs(i)<1):
        continue
    elif i>1:
        ax6.plot(xx[:,i_id],yy[:,i_id],'orange',linewidth=math.log10(i)/3,alpha=0.7)

line1, = plt.plot([], label="100", linewidth=2/3, linestyle='-',color='orange')
line2, = plt.plot([], label="1,000", linewidth=3/3, linestyle='-',color='orange')
line3, = plt.plot([], label="10,000", linewidth=4/3, linestyle='-',color='orange')


#plt.gca().set_aspect('equal')

# Create another legend for the second line.
fig.legend(handles=[line1, line2,line3],  bbox_to_anchor=(1.2, 0.7),
          frameon=False,
          title='Transmission and\n pipeline capacity (MW)')._legend_box.align = "left"


#fig.supxlabel('Longitude',y=-0.35)
#fig.supylabel('Latitude', y=0.3)

ax1.title.set_text('Demand')
ax2.title.set_text('Supply')
ax3.title.set_text('Net import')

cb_ax = fig.add_axes([0.66, 0.28, 0.3, 0.02])
patch_col = ax6.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
cb.ax.set_xticks([-200,-100,0,100,200])
#cb.ax.set_xticklabels(bins3)
cb.ax.set_title('Net import (TWh)', size=12)

cb_ax = fig.add_axes([0.15, 0.28, 0.45, 0.02])
patch_col = ax1.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
#cb.ax.set_xticks([0,1,2,3,4])
#cb.ax.set_xticklabels(bins1)
cb.ax.set_xticks([0,250,500,750,1000])
cb.ax.set_title('Demand/supply (TWh)', size=12)


re_400_mw.plot(ax=ax7, column='Generation',cmap=new_cmap2,
                norm = norm_direction2,
                   edgecolor='grey',
                   linewidth=0.25)

re_400_mw.plot(ax=ax8, column='Electrolyzer',cmap=new_cmap2,
                norm = norm_direction2,
                   edgecolor='grey',
                   linewidth=0.25)

re_storage_expand.plot(ax=ax9, column='Salt_cavern',
                       norm = norm_direction3,
                       cmap= new_cmap3,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins2},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey")
                   #,aspect='equal')
                  )  

pos = ax7.get_position()
new_pos = [pos.x0, -0.1, pos.width, pos.height] 
ax7.set_position(new_pos)

pos = ax8.get_position()
new_pos = [pos.x0, -0.1, pos.width, pos.height] 
ax8.set_position(new_pos)

pos = ax9.get_position()
new_pos = [pos.x0, -0.1, pos.width, pos.height] 
ax9.set_position(new_pos)

ax7.title.set_text('Electricity \ngeneration')
ax8.title.set_text('Hydrogen \ngeneration')
ax9.title.set_text('Underground\n hydrogen storage')

cb_ax = fig.add_axes([0.15, -0.23, 0.45, 0.02])
patch_col = ax7.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
cb.ax.set_xticks([0,100,200,300,400,500])
#cb.ax.set_xticklabels([0,50,100,150,200])
cb.ax.set_title('Capacity (GW)', size=12)

cb_ax = fig.add_axes([0.66, -0.23, 0.3, 0.02])
patch_col = ax9.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
cb.ax.set_xticks([0,50,100,150,200])
#cb.ax.set_xticklabels([-40,-20,0,20,40])
cb.ax.set_title('Storage (TWh)', size=12)

fig.text(0.0,0.9,'a', fontsize =10, fontweight="bold")
ax1.set_ylabel('Electricity')

fig.text(0.0,0.6,'b', fontsize =10, fontweight="bold")
ax4.set_ylabel('Hydrogen')

fig.text(0.0,0.1,'c', fontsize =10, fontweight="bold")
ax7.set_ylabel('Infrastructure')

ax1.set_yticklabels('')
ax1.set_xticklabels('')
ax1.set_xticks([])
ax1.set_yticks([])
plt.show()

'''
fig, ((ax1,ax2,ax3),(ax4,ax5,ax6),(ax7,ax8,ax9))=plt.subplots(ncols=3,nrows=3, sharex=True, sharey=True)

plt.subplots_adjust(
                    wspace=0.1, 
                    hspace=0.3
                    )

re_ele.plot(ax=ax1,
               column='power_mw', norm = norm_direction,
               cmap=directional,
               #scheme='UserDefined', 
               #classification_kwds={'bins': bins1},
               edgecolor='grey',
               linewidth=0.25,
               #missing_kwds= dict(color = "lightgrey", aspect='equal')
               )

xx = np.vstack([transmission_ele_400.lon_from,transmission_ele_400.lon_to])
yy = np.vstack([transmission_ele_400.lat_from,transmission_ele_400.lat_to])
capacity=transmission_ele_400.new_build_transmission_capacity_mw.values
#capacity[capacity<1]=1
#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    if (i==0) | (abs(i)<1):
        continue
    elif i>1:
        ax1.plot(xx[:,i_id],yy[:,i_id],'#0edad8',linewidth=math.log10(i)/2)
    elif i<0:
        ax1.plot(xx[:,i_id],yy[:,i_id],'r',linewidth=math.log10(-i)/2)

    
re_expand_ele.plot(ax=ax2, column='power_mw', norm = norm_direction,
                   cmap=directional,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   #missing_kwds= dict(color = "lightgrey",aspect='equal')
                   )

xx = np.vstack([transmission_ele_expand.lon_from,transmission_ele_expand.lon_to])
yy = np.vstack([transmission_ele_expand.lat_from,transmission_ele_expand.lat_to])
capacity=transmission_ele_expand.new_build_transmission_capacity_mw.values

#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    if (i==0) | (abs(i)<1):
        continue
    elif i>1:
        ax2.plot(xx[:,i_id],yy[:,i_id],'#0edad8',linewidth=math.log10(i)/2)
    elif i<0:
        ax2.plot(xx[:,i_id],yy[:,i_id],'r',linewidth=math.log10(-i)/2)


re_delta.plot(ax=ax3,
               column='power_mw',
               cmap=divergent,
               scheme='UserDefined', 
               classification_kwds={'bins': bins3},
               edgecolor='grey',
               linewidth=0.25,
               #missing_kwds= dict(color = "lightgrey", aspect='equal')
               )   

xx = np.vstack([transmission_delta.lon_from,transmission_delta.lon_to])
yy = np.vstack([transmission_delta.lat_from,transmission_delta.lat_to])
capacity=transmission_delta.new_build_transmission_capacity_mw.values
#capacity[capacity<1]=1
#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    if (i==0) | (abs(i)<1):
        continue
    elif i>1:
        ax3.plot(xx[:,i_id],yy[:,i_id],'#0edad8',linewidth=math.log10(i)/2)
    elif i<0:
        ax3.plot(xx[:,i_id],yy[:,i_id],'r',linewidth=math.log10(-i)/2)


re_H2.plot(ax=ax4, 
           column='H2_mw',
           cmap=directional,
           norm = norm_direction,
           #scheme='UserDefined', 
           #classification_kwds={'bins': bins1},
           edgecolor='grey',
           linewidth=0.25,
           #missing_kwds= dict(color = "lightgrey", aspect='equal')
           )


xx = np.vstack([transmission_H2_400.lon_from,transmission_H2_400.lon_to])
yy = np.vstack([transmission_H2_400.lat_from,transmission_H2_400.lat_to])
capacity=transmission_H2_400.new_build_transmission_capacity_mw.values
#capacity[capacity<1]=1
#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    if (i==0) | (abs(i)<1):
        continue
    elif i>1:
        ax4.plot(xx[:,i_id],yy[:,i_id],'#0edad8',linewidth=math.log10(i)/2)
    elif i<0:
        ax4.plot(xx[:,i_id],yy[:,i_id],'r',linewidth=math.log10(-i)/2)


re_expand_H2.plot(ax=ax5, column='H2_mw',
                   cmap=directional,
                   norm = norm_direction,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   #missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

xx = np.vstack([transmission_H2_expand.lon_from,transmission_H2_expand.lon_to])
yy = np.vstack([transmission_H2_expand.lat_from,transmission_H2_expand.lat_to])
capacity=transmission_H2_expand.new_build_transmission_capacity_mw.values
#capacity[capacity<1]=1
#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    if (i==0) | (abs(i)<1):
        continue
    elif i>1:
        ax5.plot(xx[:,i_id],yy[:,i_id],'#0edad8',linewidth=math.log10(i)/2)
    elif i<0:
        ax5.plot(xx[:,i_id],yy[:,i_id],'r',linewidth=math.log10(-i)/2)

re_H2_delta.plot(ax=ax6,
               column='H2_mw',
               cmap=divergent,
               scheme='UserDefined', 
               classification_kwds={'bins': bins3},
               edgecolor='grey',
               linewidth=0.25,
               #missing_kwds= dict(color = "lightgrey", aspect='equal')
               )

xx = np.vstack([transmission_H2_delta.lon_from,transmission_H2_delta.lon_to])
yy = np.vstack([transmission_H2_delta.lat_from,transmission_H2_delta.lat_to])
capacity=transmission_H2_delta.new_build_transmission_capacity_mw.values
#capacity[capacity<1]=1
#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    if (i==0) | (abs(i)<1):
        continue
    elif i>1:
        ax6.plot(xx[:,i_id],yy[:,i_id],'#0edad8',linewidth=math.log10(i)/2)
    elif i<0:
        ax6.plot(xx[:,i_id],yy[:,i_id],'r',linewidth=math.log10(-i)/2)


line1, = plt.plot([], label="100", linewidth=2/2, linestyle='-',color='b')
line2, = plt.plot([], label="1,000", linewidth=3/2, linestyle='-',color='b')
line3, = plt.plot([], label="10,000", linewidth=4/2, linestyle='-',color='b')


#plt.gca().set_aspect('equal')

# Create another legend for the second line.
fig.legend(handles=[line1, line2,line3],  bbox_to_anchor=(1.18, 0.6),
          frameon=False,
          title='Transmission and\n pipeline capacity (MW)')._legend_box.align = "left"


fig.supxlabel('Longitude',y=-0.2 )
fig.supylabel('Latitude')

ax1.title.set_text('ZE')
ax2.title.set_text('ZE + Hydrogen demand')


cb_ax = fig.add_axes([0.7, 0.3, 0.25, 0.02])
patch_col = ax6.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
cb.ax.set_xticks([0,1,2,3,4])
cb.ax.set_xticklabels(bins3)
cb.ax.set_title('Change in energy generation(TWh)', size=12)

cb_ax = fig.add_axes([0.15, 0.3, 0.45, 0.02])
patch_col = ax1.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
#cb.ax.set_xticks([0,1,2,3,4])
#cb.ax.set_xticklabels(bins1)
cb.ax.set_xticks([0,250,500,750,1000])
cb.ax.set_title('Energy generation (TWh)', size=12)

re_storage.plot(ax=ax7, column='Storage',cmap=cmap,
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins2},
                   edgecolor='grey',
                   linewidth=0.25,
                   #missing_kwds= dict(color = "lightgrey")
                   #,aspect='equal')
                  )

re_storage_expand.plot(ax=ax8, column='Storage',cmap=cmap,
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins2},
                   edgecolor='grey',
                   linewidth=0.25,
                   #missing_kwds= dict(color = "lightgrey")
                   #,aspect='equal')
                  )

re_storage_delta.plot(ax=ax9, column='Storage',cmap=divergent,
                      norm=norm_diverge,
                   #scheme='UserDefined', 
                   #classification_kwds={'bins': bins4},
                   edgecolor='grey',
                   linewidth=0.25,
                   #missing_kwds= dict(color = "lightgrey")
                   #,aspect='equal')
                  )


pos = ax7.get_position()
new_pos = [pos.x0, 0.01, pos.width, pos.height] 
ax7.set_position(new_pos)

pos = ax8.get_position()
new_pos = [pos.x0, 0.01, pos.width, pos.height] 
ax8.set_position(new_pos)

pos = ax9.get_position()
new_pos = [pos.x0, 0.01, pos.width, pos.height] 
ax9.set_position(new_pos)


cb_ax = fig.add_axes([0.15, -0.1, 0.45, 0.02])
patch_col = ax7.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
#cb.ax.set_xticks([0,50,100,150,200])
cb.ax.set_xticklabels([0,50,100,150,200])
cb.ax.set_title('Energy generation (TWh)', size=12)

cb_ax = fig.add_axes([0.7, -0.1, 0.25, 0.02])
patch_col = ax9.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
cb.ax.set_xticks([-40,-20,0,20,40])
#cb.ax.set_xticklabels([-40,-20,0,20,40])
cb.ax.set_title('Energy generation (TWh)', size=12)

plt.show()
'''
#%%
#fig.savefig('/Users/hy4174/Documents/Hydrogen/Figure/' + 'Fig4' + '.png', dpi=300, bbox_inches='tight')

