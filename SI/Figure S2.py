# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 15:04:43 2024

@author: haozheyang
"""


from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

import matplotlib.pyplot as plt

pio.renderers.default='browser'
        
test_id=['400ppm_1period_36day','Hydrogen_400ppm_1period_36day']

day=np.linspace(1,365,365)
day=np.linspace(1,36,36)

output=DataFrame()
output_capacity=DataFrame()
output_capacity_province=DataFrame()
output_generation=DataFrame()
output_generation_province=DataFrame()

fig,ax=plt.subplots(nrows=1,ncols=2,figsize=(10, 6))
plt.subplots_adjust(hspace=0.2,
                    wspace=0.1)

for i,case in enumerate(test_id):
    path='H:/Hydrogen/Data/'+case+'/results/'
    
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
    
    
    dispatch_path=path+file1
    capacity_path=path+file6
    carbon_path=path+file2
    capacity_cost_path=path+file3
    operation_cost_path=path+file4
    transmission_cost_path=path+file5
    transmission_capacity_path=path+file7
    capacity_new_path=path+file8
    stor_new_path=path+file9
    H2_path=path+file10
    ccs_path=path+file11
    import_path=path+file12
    import_H2_path=path+file13
    import_ccs_path=path+file14
    
    #dispatch
    dispatch=read_csv(dispatch_path)
    dispatch.power_mw=dispatch.power_mw*dispatch.timepoint_weight/10**6
    
    dispatch_H2=read_csv(H2_path)
    dispatch_H2.H2_mw=dispatch_H2.H2_mw*dispatch_H2.timepoint_weight/10**6
    
    #transmission
    import_ele=pd.read_csv(import_path)
    import_ele['net_imports_mw']=import_ele.timepoint_weight*import_ele.net_imports_mw/10**6
    
    
    dispatch_hourly=dispatch.groupby(['timepoint','technology'])['power_mw'].sum().reset_index()
    df_neg= dispatch_hourly.copy()
    df_neg.loc[df_neg.power_mw>0,'power_mw']=0
    df_neg['day']=df_neg.timepoint.astype(str).str[0:8]
    df_neg=df_neg.groupby(['day','technology'])['power_mw'].sum().reset_index()
    df_neg=df_neg.pivot(index='day',columns='technology',values='power_mw')
        
    df_pos=dispatch_hourly.copy()
    df_pos.loc[df_pos.power_mw<0,'power_mw']=0
    df_pos['day']=df_pos.timepoint.astype(str).str[0:8]
    df_pos=df_pos.groupby(['day','technology'])['power_mw'].sum().reset_index()
    df_pos=df_pos.pivot(index='day',columns='technology',values='power_mw')
    
    if case=='400ppm_1period_36day':
        df_pos['Electrolyzer']=0
        df_pos['H2_turbine']=0
        df_pos['Fuel_cell']=0
        df_neg['Electrolyzer']=0
        df_neg['H2_turbine']=0
        df_neg['Fuel_cell']=0
    
    #coal_color = '#FB6F6F'
    #gas_color = '#F4A666'
    hydro_color = '#6FFFFF'
    nuclear_color = '#BA75FF'
    solar_color = '#EDE76D'
    storage_color = '#B0FFB0'
    wind_color = '#4FBDFF'
    offshore_color='#1E3CFF'
    electrolyzer_color='#b0a990'
    fuel_cell_color='#39304a'
    H2_turbine_color='#606c38'
    pumped_hydro_color="#283618"
    
    order=['Hydro','Nuclear',
           'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
           ]
    
    color=['#316589','#EA4855',
           '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9'
           ]
    
    df_pos=df_pos[order]
    df_neg=df_neg[order]
    
    color_map=[
              #'#FB6F6F',
              #'#F4A666',
              '#316589',
              '#EA4855',
              '#84BBD7',
              '#2897C0',
              '#F7AE39',
              '#FADC65',
              '#94d2bd',
              '#0a9396',
              '#d9ed92',
              '#3f37c9',
              ]
    
    labels=[
            #'Coal',
            #'Gas',
            'Hydro',
            'Nuclear',
            'Offshore wind',
            'Wind',
            'Solar',
            'Battery',
            'Pumped hydro',
            'Electrolyzer',
            'H2 turbine',
            'Fuel cell']
    
    #fig,ax=plt.subplots()
    #df_pos.plot.area(ax=ax)
    #ax.set_prop_cycle(None)
    #df_neg.rename(columns=lambda x: '_' + x).plot.area(ax=ax)
    ax[i].stackplot(day,
                 #df_pos.Coal,
                 #df_pos.Gas,
                 df_pos.Hydro,
                 df_pos.Nuclear,
                 df_pos.Offshore_Wind,
                 df_pos.Wind,
                 df_pos.Solar,
                 df_pos.Battery,
                 df_pos.Pumped_hydro,
                 df_pos.Electrolyzer,
                 df_pos.H2_turbine,
                 df_pos.Fuel_cell,
                 colors=color_map,
                 labels=labels)
    
    ax[i].stackplot(day,
                 #df_neg.Coal,
                 #df_neg.Gas,
                 df_neg.Hydro,                 
                 df_neg.Nuclear,
                 df_neg.Offshore_Wind,
                 df_neg.Wind,
                 df_neg.Solar,
                 df_neg.Battery,
                 df_neg.Pumped_hydro,                 
                 df_neg.Electrolyzer,
                 df_neg.H2_turbine,
                 df_neg.Fuel_cell,
                 colors=color_map)
    
    ax[i].set_ylim([-300,700])
    ax[i].set_xlabel('Day')
    '''
    ax.axvline(x=31)
    ax.axvline(x=59)
    ax.axvline(x=90)
    ax.axvline(x=120)
    ax.axvline(x=151)
    ax.axvline(x=181)
    ax.axvline(x=212)
    ax.axvline(x=243)
    ax.axvline(x=273)
    ax.axvline(x=304)
    ax.axvline(x=334)
    '''
ax[0].set_ylabel('TWh')
ax[1].legend(bbox_to_anchor=(1.6, 0.5),loc='right',frameon=False)
ax[1].set_yticklabels('')
ax[0].title.set_text('ZE w/o $H_{2}$')
ax[1].title.set_text('ZE')
    #ax.set_ylim([-2*10**7,2*10**7])    
fig.savefig('H:/Hydrogen/Figure/' + 'FigS2' + '.png', dpi=300, bbox_inches='tight')
 
    
'''    
    dispatch_H2_hourly=dispatch_H2.groupby(['timepoint','technology'])['H2_mw'].sum().reset_index()
    
    df_H2= dispatch_H2_hourly.copy()
    df_H2['day']=df_H2.timepoint.astype(str).str[0:8]
    df_H2=df_H2.groupby(['day'])['H2_mw'].sum().reset_index()
    #df_H2=df_H2.pivot(index='day',columns='technology',values='H2_mw')
        
    
    df_H2_neg= dispatch_H2_hourly.copy()
    df_H2_neg.loc[df_H2_neg.H2_mw>0,'H2_mw']=0
    df_H2_neg['day']=df_H2_neg.timepoint.astype(str).str[0:8]
    df_H2_neg=df_H2_neg.groupby(['day','technology'])['H2_mw'].sum().reset_index()
    df_H2_neg=df_H2_neg.pivot(index='day',columns='technology',values='H2_mw')
        
    df_H2_pos=dispatch_H2_hourly.copy()
    df_H2_pos.loc[df_H2_pos.H2_mw<0,'H2_mw']=0
    df_H2_pos['day']=df_H2_pos.timepoint.astype(str).str[0:8]
    df_H2_pos=df_H2_pos.groupby(['day','technology'])['H2_mw'].sum().reset_index()
    df_H2_pos=df_H2_pos.pivot(index='day',columns='technology',values='H2_mw')
    
    
    electrolyzer_color='#b0a990'
    fuel_cell_color='#39304a'
    H2_turbine_color='#606c38'
    tank_color="#fefae0"
    underground_color="#a69005"
    
    color_map=[
              '#b0a990',
              '#39304a',
              '#606c38',
              "#fefae0",
              "#a69005",
              ]
    
    labels=[
            'Electrolyzer',
            'Fuel cell',
            'H2_turbine',
            'Tank',
            'Salt cavern',
            ]


fig1,ax1=plt.subplots()
fig2,ax2=plt.subplots()
#df_pos.plot.area(ax=ax)
#ax.set_prop_cycle(None)
#df_neg.rename(columns=lambda x: '_' + x).plot.area(ax=ax)
ax1.bar(day,df_H2.H2_mw)
ax1.legend(bbox_to_anchor=(1.5, 0.5),loc='right')


ax2.stackplot(day,
             df_H2_pos.Electrolyzer,
             df_H2_pos.H2_turbine,
             df_H2_pos.Fuel_cell,
             df_H2_pos.Tank,
             df_H2_pos.Salt_cavern,
             colors=color_map,
             labels=labels)

ax2.stackplot(day,
             df_H2_neg.Electrolyzer,
             df_H2_neg.H2_turbine,
             df_H2_neg.Fuel_cell,
             df_H2_neg.Tank,
             df_H2_neg.Salt_cavern,
         colors=color_map)
ax2.legend(bbox_to_anchor=(1.5, 0.5),loc='right')


import_ele['day']=import_ele.timepoint.astype(str).str[0:8]
import_ele=import_ele.groupby(['day'])['net_imports_mw'].sum().reset_index()
'''
