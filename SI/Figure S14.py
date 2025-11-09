# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:29:33 2024

@author: haozheyang
"""

from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter

        

file1='dispatch_all.csv'
file2='carbon_emissions_by_project.csv'
file3='costs_capacity_all_projects.csv'
file4='costs_operations.csv'
file5='costs_transmission_capacity.csv'
file6='capacity_all.csv'
file7='transmission_capacity.csv'
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
         #'Hydrogen_400ppm_1period_36day',
         #'Hydrogen_400ppm_1period_36day_H2',
         #'Hydrogen_400ppm_1period_36day_H2_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_SMR',
         'Hydrogen_400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day_gas',
         'Hydrogen_400ppm_1period_36day_H2_expand_flat_gas',
         'Hydrogen_400ppm_1period_36day_H2_expand_flat',
         'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_80_flat'
         #'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs',
         #'Hydrogen_400ppm_1period_36day_ccs_storage',
         #'Hydrogen_400ppm_1period_36day_H2_expand_ccs',
         ]

capacity=pd.DataFrame()
capacity_energy=pd.DataFrame()
generation=pd.DataFrame()
generation_H2=pd.DataFrame()
cost=pd.DataFrame()
unitcost=pd.DataFrame()
df_pos=pd.DataFrame()
df_neg=pd.DataFrame()

for case in test_id:
    path='/Users/hy4174/Documents/Hydrogen/data/'+case+'/results/'
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
    load_balance_path=path+file15
    H2_balance_path=path+file16
    
    
    capacity_tmp=pd.read_csv(capacity_path)
    capacity_tmp.capacity_mw=capacity_tmp.capacity_mw/1000
    capacity_tmp.capacity_mwh=capacity_tmp.capacity_mwh/10**6
    
    generation_tmp=pd.read_csv(dispatch_path)
    generation_tmp.power_mw=generation_tmp.power_mw*generation_tmp.timepoint_weight/10**6

    dispatch_hourly=generation_tmp.groupby(['timepoint','technology'])['power_mw'].sum().reset_index()
    df_neg_tmp= dispatch_hourly.copy()
    df_neg_tmp.loc[df_neg_tmp.power_mw>0,'power_mw']=0
    df_neg_tmp['month']=df_neg_tmp.timepoint.astype(str).str[0:6]
    df_neg_tmp['day']=df_neg_tmp.timepoint.astype(str).str[0:8]
    df_neg_tmp=df_neg_tmp.groupby(['month','technology'])['power_mw'].sum().reset_index()
    df_neg_tmp=df_neg_tmp.pivot(index='month',columns='technology',values='power_mw')
    df_neg_tmp['scenario']=case
    df_neg=pd.concat([df_neg, df_neg_tmp])

    df_pos_tmp=dispatch_hourly.copy()
    df_pos_tmp.loc[df_pos_tmp.power_mw<0,'power_mw']=0
    df_pos_tmp['month']=df_pos_tmp.timepoint.astype(str).str[0:6]
    df_pos_tmp['day']=df_pos_tmp.timepoint.astype(str).str[0:8]
    df_pos_tmp=df_pos_tmp.groupby(['month','technology'])['power_mw'].sum().reset_index()
    df_pos_tmp=df_pos_tmp.pivot(index='month',columns='technology',values='power_mw')
    df_pos_tmp['scenario']=case
    df_pos=pd.concat([df_pos, df_pos_tmp])
    
    H2_tmp=pd.read_csv(H2_path)
    H2_tmp.H2_mw=H2_tmp.H2_mw*H2_tmp.timepoint_weight/10**6
    
    if H2_tmp.H2_mw.sum()==0:
        H2_tmp=pd.DataFrame({
            'technology':['Electrolyzer','SMR','Fuel_cell','H2_turbine','Salt_cavern','Tank'],
            'H2_mw':[0,0,0,0,0,0]
            })
        
    transmission_tmp=pd.read_csv(transmission_capacity_path)
    transmission_tmp['technology']='Grid'
    transmission_tmp['capacity_mw']=abs(transmission_tmp.transmission_max_capacity_mw)/1000
    
    for line_id, line in enumerate(transmission_tmp.tx_line):
        if 'H2' in line:
            transmission_tmp.loc[line_id,'technology']='H2_Pipeline'
        
    capacity_technology_tmp=capacity_tmp.groupby(['technology'])['capacity_mw'].sum().reset_index()
    capacity_energy_technology_tmp=capacity_tmp.groupby(['technology'])['capacity_mwh'].sum().reset_index()
    generation_technology_tmp=generation_tmp.groupby(['technology'])['power_mw'].sum().reset_index()
    H2_technology_tmp=H2_tmp.groupby(['technology'])['H2_mw'].sum().reset_index()
    transmission_technology_tmp=transmission_tmp.groupby(['technology'])['capacity_mw'].sum().reset_index()
    
    capacity_technology_tmp=pd.concat([capacity_technology_tmp, transmission_technology_tmp])
    capacity_technology_tmp['scenario']=case
    generation_technology_tmp['scenario']=case
    H2_technology_tmp['scenario']=case
    capacity_energy_technology_tmp['scenario']=case

    capacity_technology_tmp=capacity_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mw')
    generation_technology_tmp=generation_technology_tmp.pivot(index='scenario',columns='technology',values='power_mw')
    H2_technology_tmp=H2_technology_tmp.pivot(index='scenario',columns='technology',values='H2_mw')
    capacity_energy_technology_tmp=capacity_energy_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mwh')

    capacity=pd.concat([capacity, capacity_technology_tmp])
    generation=pd.concat([generation,generation_technology_tmp])  
    generation_H2=pd.concat([generation_H2, H2_technology_tmp])
    capacity_energy=pd.concat([capacity_energy, capacity_energy_technology_tmp])


    cost_capacity=pd.read_csv(capacity_cost_path)
    cost_capacity.loc[cost_capacity.technology.isin(['CCS_storage_saline','CCS_storage_offshore','CCS_storage_oil']),
                      'technology']='CCS_storage'
        
    cost_operation=pd.read_csv(operation_cost_path).fillna(0)
    cost_operation['variable_cost']=(cost_operation.variable_om_cost+cost_operation.fuel_cost)*cost_operation.timepoint_weight
    cost_operation.loc[cost_operation.technology.isin(['CCS_storage_saline','CCS_storage_offshore','CCS_storage_oil']),
                       'technology']='CCS_storage'
    
    cost_transmission=pd.read_csv(transmission_cost_path)
    cost_transmission['technology']='Grid'
    
    for line_id, line in enumerate(cost_transmission.tx_line):
        if 'H2' in line:
            cost_transmission.loc[line_id,'technology']='H2_Pipeline'
        elif 'ccs' in line:
            cost_transmission.loc[line_id,'technology']='CO2_Pipeline'
            
    cost_capacity_technology=cost_capacity.groupby(['technology'])['capacity_cost'].sum().reset_index()
    cost_operation_technology=cost_operation.groupby(['technology'])['variable_cost'].sum().reset_index()
    cost_transmission=cost_transmission.groupby(['technology'])['capacity_cost'].sum().reset_index()
    
    cost_tmp=cost_capacity_technology.merge(cost_operation_technology)
    cost_tmp=pd.concat([cost_tmp,cost_transmission]).fillna(0)
    
    cost_tmp['total_cost']=(cost_tmp.capacity_cost+cost_tmp.variable_cost)
    cost_tmp=cost_tmp[['technology','total_cost']]
    cost_tmp['scenario']=case
    
    cost_tmp=cost_tmp.pivot(index='scenario',columns='technology',values='total_cost')
    
    cost=pd.concat([cost,cost_tmp])
        
    load=pd.read_csv(load_balance_path)
    load.load_mw=load.load_mw*load.timepoint_weight
    load_sum=load.load_mw.sum()
    
    load_H2=pd.read_csv(H2_balance_path)
    load_H2.H2_mw=load_H2.H2_mw * load_H2.timepoint_weight
    H2_sum=load_H2.H2_mw.sum()

    total_cost=cost_capacity_technology.capacity_cost.sum()+cost_operation_technology.variable_cost.sum()+cost_transmission.capacity_cost.sum()
    total_sum=load_sum+H2_sum  

    unitcost=pd.concat([unitcost,cost_tmp/total_sum])
    print(total_cost)
    
cost=cost/10**12
#%%

order=[
       'Coal','Gas',
       'Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
       'SMR','Gasification',
       'Salt_cavern','Tank',
       'Grid','H2_Pipeline',
       'CO2_Pipeline',
       'DAC','CCS_storage'
       ]

color=[
       '#404040','#C0C0C0',
       '#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       '#03045e','#7400b8',
       '#8f470d','#a68a64',
       '#b5179e','#f72585',
       '#560bad',
       '#8ac926','#254d32'
       ]

unitcost['Coal']=0
unitcost['Gas']=0

unitcost=unitcost[order]
unitcost=unitcost[::-1]

scenario_order=[
         'Hydrogen_400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day_gas',
         'Hydrogen_400ppm_1period_36day_H2_expand_flat',
         'Hydrogen_400ppm_1period_36day_H2_expand_flat_gas',
         ]
unitcost = unitcost.loc[scenario_order[::-1],:]

label=['Coal ','Gas ','Hydropower','Nuclear',
       'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro', 'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell',
       'Steam methane reforming + CCS','Gasification + CCS',
       'Underground storage', 'Tank',
       'Grid',' $H_{2}$ pipeline',
       ' $CO_{2}$ pipeline','DAC','CCS storage'
       ]

#%%
fig, ax = plt.subplots(nrows=1,ncols=1,figsize=(6, 8))

'''
fig.set_figheight(10)
fig.set_figwidth(10)


ax1 = plt.subplot2grid(shape=(2, 2), loc=(0, 0), colspan=2)
ax2 = plt.subplot2grid(shape=(2, 2), loc=(1, 0), colspan=1)
ax3 = plt.subplot2grid(shape=(2, 2), loc=(1, 1), colspan=1)

plt.subplots_adjust(hspace=0.2,
                    wspace=0.2)
'''
unitcost.plot.barh(ax=ax,
                  stacked=True,
                  color=color,
                  legend=False)

'''
day=np.linspace(1,12,12)

df_pos_h=df_pos.loc[df_pos.scenario=='Hydrogen_400ppm_1period_36day']
df_neg_h=df_neg.loc[df_neg.scenario=='Hydrogen_400ppm_1period_36day']
ax2.stackplot(day,
             #df_pos_h.Coal,
             #df_pos_h.Gas,
             #df_pos_h.Nuclear,
             #df_pos_h.Hydro,
             #df_pos_h.Solar,
             #df_pos_h.Wind,
             #df_pos_h.Offshore_Wind,
             df_pos_h.Battery,
             df_pos_h.Pumped_hydro,
             df_pos_h.Electrolyzer,
             df_pos_h.H2_turbine,
             df_pos_h.Fuel_cell,
             colors=storage_color,
             )

ax2.stackplot(day,
             #df_neg_h.Coal,
             #df_neg_h.Gas,
             #df_neg_h.Nuclear,
             #df_neg_h.Hydro,
             #df_neg_h.Solar,
             #df_neg_h.Wind,
             #df_neg_h.Offshore_Wind,
             df_neg_h.Battery,
             df_pos_h.Pumped_hydro,
             df_neg_h.Electrolyzer,
             df_neg_h.H2_turbine,
             df_neg_h.Fuel_cell,
             df_neg_h.Pumped_hydro,
             colors=storage_color
             )

ax2.axhline(y=0,color='black',linewidth=0.5)

df_pos_d=df_pos.loc[df_pos.scenario=='Hydrogen_400ppm_1period_36day_H2_expand']
df_neg_d=df_neg.loc[df_neg.scenario=='Hydrogen_400ppm_1period_36day_H2_expand']
ax3.stackplot(day,
             #df_pos_d.Coal,
             #df_pos_d.Gas,
             #df_pos_d.Nuclear,
             #df_pos_d.Hydro,
             #df_pos_d.Solar,
             #df_pos_d.Wind,
             #df_pos_d.Offshore_Wind,
             df_pos_d.Battery,
             df_pos_d.Pumped_hydro,
             df_pos_d.Electrolyzer,
             df_pos_d.H2_turbine,
             df_pos_d.Fuel_cell,
             colors=storage_color
             )

ax3.stackplot(day,
             #df_neg_d.Coal,
             #df_neg_d.Gas,
             #df_neg_d.Nuclear,
             #df_neg_d.Hydro,
             #df_neg_d.Solar,
             #df_neg_d.Wind,
             #df_neg_d.Offshore_Wind,
             df_neg_d.Battery,
             df_neg_d.Pumped_hydro,
             df_neg_d.Electrolyzer,
             df_neg_d.H2_turbine,
             df_neg_d.Fuel_cell,
             colors=storage_color
             )

ax3.axhline(y=0,color='black',linewidth=0.5)
'''
handles, labels = ax.get_legend_handles_labels()
#fig.legend(handles, labels, loc='upper center')

#fig.legend(handles,label,loc='center left', bbox_to_anchor=(0.9, 0.5),frameon=False)
fig.legend(reversed(handles[0:4]), reversed(label[0:4]),
           title='Conventional energy',
           loc='center left', bbox_to_anchor=(0.9, 0.16),frameon=False
           )._legend_box.align = "left"


fig.legend(reversed(handles[4:7]), reversed(label[4:7]),
           title='Renewable energy',
           loc='center left', bbox_to_anchor=(0.9, 0.28),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[7:9]), reversed(label[7:9]),
           title='Conventional storage',
           loc='center left', bbox_to_anchor=(0.9, 0.38),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[9]), [label[9]],
           title='Power to gas',
           loc='center left', bbox_to_anchor=(0.9, 0.45),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[10:12]), reversed(label[10:12]),
           title='Gas to power',
           loc='center left', bbox_to_anchor=(0.9, 0.53),frameon=False
           )._legend_box.align = "left"


fig.legend(reversed(handles[12:14]), reversed(label[12:14]),
           title='Fossil-based hydrogen',
           loc='center left', bbox_to_anchor=(0.9, 0.61),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[14:16]), reversed(label[14:16]),
           title='Hydrogen storage',
           loc='center left', bbox_to_anchor=(0.9, 0.7),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[16:19]), reversed(label[16:19]),
           title='Transmission',
           loc='center left', bbox_to_anchor=(0.9, 0.8),
           frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[19:]), reversed(label[19:]),
           title='Carbon capture and storage',
           loc='center left', bbox_to_anchor=(0.9, 0.9),
           frameon=False
           )._legend_box.align = "left"

ax.set_yticklabels([
                    'ZE+ $H_{2}$ demand\n + Repurposing',
                    'ZE+ $H_{2}$ demand\n',
                    'ZE+ Repurposing',
                    'ZE'
                   ],
                   fontsize=14)

ax.set_xlabel('$/MWh')
ax.set_ylabel('')
#ax1.set_ylim([-10000,25000])
#ax1.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
'''
ax2.set_ylabel('TWh',fontsize=14)
ax2.set_xlabel('')
ax2.set_xlim([1,12])
ax2.set_ylim([-1000,450])
ax2.set_xticks(day)
ax2.set_xticklabels(['Jan','Feb','Mar','Arp','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],rotation=90)
'''

'''
ax2.axvline(x=1,linestyle='--',color='grey')
ax2.axvline(x=4,linestyle='--',color='grey')
ax2.axvline(x=7,linestyle='--',color='grey')
ax2.axvline(x=10,linestyle='--',color='grey')
ax2.axvline(x=13,linestyle='--',color='grey')
ax2.axvline(x=16,linestyle='--',color='grey')
ax2.axvline(x=19,linestyle='--',color='grey')
ax2.axvline(x=22,linestyle='--',color='grey')
ax2.axvline(x=25,linestyle='--',color='grey')
ax2.axvline(x=28,linestyle='--',color='grey')
ax2.axvline(x=31,linestyle='--',color='grey')
ax2.axvline(x=34,linestyle='--',color='grey')
'''
'''
ax3.set_ylabel('')
ax3.set_xlabel('')
ax3.set_ylim([-1000,450])
ax3.set_xlim([1,12])
ax3.set_yticklabels('')
ax3.set_xticks(day)
ax3.set_xticklabels(['Jan','Feb','Mar','Arp','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],rotation=90)
'''
'''
ax3.axvline(x=1,linestyle='--',color='grey')
ax3.axvline(x=4,linestyle='--',color='grey')
ax3.axvline(x=7,linestyle='--',color='grey')
ax3.axvline(x=10,linestyle='--',color='grey')
ax3.axvline(x=13,linestyle='--',color='grey')
ax3.axvline(x=16,linestyle='--',color='grey')
ax3.axvline(x=19,linestyle='--',color='grey')
ax3.axvline(x=22,linestyle='--',color='grey')
ax3.axvline(x=25,linestyle='--',color='grey')
ax3.axvline(x=28,linestyle='--',color='grey')
ax3.axvline(x=31,linestyle='--',color='grey')
ax3.axvline(x=34,linestyle='--',color='grey')
'''
#fig.text(0.5,0.05,'Month',fontsize=14)

#fig.text(0.05 , 0.9,'a', fontweight="bold",fontsize=14)
#fig.text(0.05,0.47,'b', fontweight="bold",fontsize=14)
#fig.text(0.5,0.47,'c', fontweight="bold",fontsize=14)

font = {'family' : 'Arial',
        'weight': 'normal',
        'size'   : 12}

params={'mathtext.default': 'regular' }

plt.rcParams.update(params)
plt.rc('font', **font)
#fig.tight_layout()
plt.show()
#%%
fig.savefig('/Users/hy4174/Documents/Hydrogen/Figure/revision/' + 'FigS_gas' + '.png', dpi=300, bbox_inches='tight')
