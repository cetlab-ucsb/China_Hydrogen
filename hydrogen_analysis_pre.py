# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:29:33 2024

@author: haozheyang
"""

from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter

pio.renderers.default='browser'
        

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
         'Hydrogen_400ppm_1period_36day',
         #'Hydrogen_400ppm_1period_36day_H2',
         #'Hydrogen_400ppm_1period_36day_H2_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_SMR',
         'Hydrogen_400ppm_1period_36day_H2_expand',
         'Hydrogen_400ppm_1period_36day_onlyH2_expand',
         #'Hydrogen_400ppm_1period_36day_ccs_storage',
         #'Hydrogen_400ppm_1period_36day_H2_expand_ccs',
         'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs'
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
    path='H:/Hydrogen/Data/'+case+'/results/'
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
    df_neg=df_neg.append(df_neg_tmp)

    df_pos_tmp=dispatch_hourly.copy()
    df_pos_tmp.loc[df_pos_tmp.power_mw<0,'power_mw']=0
    df_pos_tmp['month']=df_pos_tmp.timepoint.astype(str).str[0:6]
    df_pos_tmp['day']=df_pos_tmp.timepoint.astype(str).str[0:8]
    df_pos_tmp=df_pos_tmp.groupby(['month','technology'])['power_mw'].sum().reset_index()
    df_pos_tmp=df_pos_tmp.pivot(index='month',columns='technology',values='power_mw')
    df_pos_tmp['scenario']=case
    df_pos=df_pos.append(df_pos_tmp)
    
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
    
    capacity_technology_tmp=capacity_technology_tmp.append(transmission_technology_tmp)
    capacity_technology_tmp['scenario']=case
    generation_technology_tmp['scenario']=case
    H2_technology_tmp['scenario']=case
    capacity_energy_technology_tmp['scenario']=case

    capacity_technology_tmp=capacity_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mw')
    generation_technology_tmp=generation_technology_tmp.pivot(index='scenario',columns='technology',values='power_mw')
    H2_technology_tmp=H2_technology_tmp.pivot(index='scenario',columns='technology',values='H2_mw')
    capacity_energy_technology_tmp=capacity_energy_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mwh')

    capacity=capacity.append(capacity_technology_tmp)
    generation=generation.append(generation_technology_tmp)  
    generation_H2=generation_H2.append(H2_technology_tmp)
    capacity_energy=capacity_energy.append(capacity_energy_technology_tmp)


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
    cost_tmp=cost_tmp.append(cost_transmission).fillna(0)
    
    cost_tmp['total_cost']=(cost_tmp.capacity_cost+cost_tmp.variable_cost)
    cost_tmp=cost_tmp[['technology','total_cost']]
    cost_tmp['scenario']=case
    
    cost_tmp=cost_tmp.pivot(index='scenario',columns='technology',values='total_cost')
    
    cost=cost.append(cost_tmp)
        
    load=pd.read_csv(load_balance_path)
    load.load_mw=load.load_mw*load.timepoint_weight
    load_sum=load.load_mw.sum()
    
    load_H2=pd.read_csv(H2_balance_path)
    load_H2.H2_mw=load_H2.H2_mw * load_H2.timepoint_weight
    H2_sum=load_H2.H2_mw.sum()

    total_cost=cost_capacity_technology.capacity_cost.sum()+cost_operation_technology.variable_cost.sum()+cost_transmission.capacity_cost.sum()
    total_sum=load_sum+H2_sum  

    unitcost=unitcost.append(cost_tmp/total_sum)
    print(total_cost)
    
cost=cost/10**12
#%%

order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
       'Salt_cavern','Tank',
       'Grid','H2_Pipeline']

color=['#404040','#C0C0C0','#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       '#8f470d','#a68a64',
       '#b5179e','#f72585'
       ]

unitcost=unitcost[order]
unitcost=unitcost.loc[['Hydrogen_400ppm_1period_36day_H2_expand', 'Hydrogen_400ppm_1period_36day'],:]

generation_order=[
        'Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell'
       ]

generation=generation[generation_order]

generation_color=['#404040','#C0C0C0','#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       ]

storage_color=[
       '#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9'
       ]


label=[
       'Coal','Gas',
       'Hydropower','Nuclear',
       'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro',
       'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell',
       'Underground storage', 'Tank',
       'Grid',' $H_{2}$ pipeline'
       ]

generation_label=[
           'Coal','Gas','Hydropower','Nuclear',
           'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro',
           'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell'
           ]

unitcost_sum=unitcost.sum(axis=1)
unitcost_sum['Hydrogen_demand']=56
unitcost_sum=unitcost_sum[['Hydrogen_demand','Hydrogen_400ppm_1period_36day_H2_expand', 'Hydrogen_400ppm_1period_36day']]
#%%
SMR=59102.39761 # $/MW/yr
SMR_range=np.linspace(40,80,100)

SMR_CCS=30133.51805
SMR_gas=4.8 #mmbtu per MWh

var=0.8
price=13.67653313
price_range=np.linspace(2,15,100)

EF=0.05306
DAC=1074073.565

lcoe_SMR_full=np.zeros((len(SMR_range),len(price_range)))

for i, SMR_cost in enumerate(SMR_range):
    for j, gas_cost in enumerate(price_range):
        lcoe_SMR_full[i,j]=(SMR_cost*1000+SMR_gas*8760*gas_cost)/8760*120/3600 

X, Y = np.meshgrid(price_range,SMR_range)


gasification=386506.2796
gasification_range=np.linspace(40,600,100)

gasification_coal=5.3 #mmbtu per MWh

coal_price_range=np.linspace(2,6,100)


lcoe_gasification_full=np.zeros((len(gasification_range),len(coal_price_range)))

for i, gasification_cost in enumerate(gasification_range):
    for j, coal_cost in enumerate(coal_price_range):
        lcoe_gasification_full[i,j]=(gasification_cost*1000+gasification_coal*8760*coal_cost)/8760*120/3600 

X_coal, Y_coal = np.meshgrid(coal_price_range,gasification_range)
#%%
fig,ax = plt.subplots(nrows=1, ncols=1)


unitcost_sum.plot.barh(ax=ax,
                  stacked=True,
                  #color=color,
                  legend=False,)



fig1,ax1 = plt.subplots(nrows=1, ncols=1)

levels=[0.4,
        0.7,
        1,
        1.3,
        1.6,
        1.9,
        2.2,
        2.5,
        ]

CF=ax1.contourf(X, Y, lcoe_SMR_full,
                      levels,
                      extend='both'
                      )

CS=ax1.contour(X, Y, lcoe_SMR_full,
                      levels,zorder=2,
                      colors=['k','k','k','k','k','r','k'],
                      linestyles=['-','-','-','-','-','-','-']
                      )

manual_locations = [
                    (2, 60), 
                    (5, 60), 
                    (7, 60), 
                    (9, 60), 
                    (11, 60),
                    (13, 60), 
                    ]

ax1.clabel(CS,
           levels=[0.7,1,1.3,1.6,1.9,2.2],
           inline=True,
           colors='white',
           fontsize=12,
           fmt=' {:.1f} '.format,
           manual=manual_locations
           )

ax1.scatter(13.85,59,s=320, marker='*', color='r')

cbar_ax = fig1.add_axes([0.93, 0.125, 0.03, 0.75])
cbar=fig1.colorbar(CF, orientation='vertical',cax=cbar_ax)
cbar.ax.set_title('cost of hydrogen $/kg',fontsize=14,pad=10)

handles, labels = ax.get_legend_handles_labels()
#fig.legend(handles, labels, loc='upper center')

#fig.legend(handles,label,loc='center left', bbox_to_anchor=(0.9, 0.5),frameon=False)
'''
fig.legend(reversed(handles[0:4]), reversed(label[0:4]),
           title='Conventional energy',
           loc='center left', bbox_to_anchor=(0.9, 0.4),frameon=False
           )._legend_box.align = "left"


fig.legend(reversed(handles[4:7]), reversed(label[4:7]),
           title='Renewable energy',
           loc='center left', bbox_to_anchor=(0.9, 0.5),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[7:9]), reversed(label[7:9]),
           title='Conventional storage',
           loc='center left', bbox_to_anchor=(0.9, 0.58),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[9]), [label[9]],
           title='Power to gas',
           loc='center left', bbox_to_anchor=(0.9, 0.64),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[10:12]), reversed(label[10:12]),
           title='Gas to power',
           loc='center left', bbox_to_anchor=(0.9, 0.71),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[12:14]), reversed(label[12:14]),
           title='Hydrogen storage',
           loc='center left', bbox_to_anchor=(0.9, 0.78),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[14:16]), reversed(label[14:16]),
           title='Transmission',
           loc='center left', bbox_to_anchor=(0.9, 0.86),
           frameon=False
           )._legend_box.align = "left"
'''

ax.set_yticklabels(['Cost of hydrogen\nin zero-emission energy system', 'Zero-emission energy system','Zero-emiission power system'],fontsize=14)
ax.set_ylabel('TWh')
ax.set_ylabel('')
ax.set_xlabel('$/MWh')
#ax1.set_ylim([-10000,25000])
#ax1.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))



ax1.set_ylabel('$/kW/yr',fontsize=14)
ax1.set_xlabel('$/mmbtu',fontsize=14)


font = {'family' : 'Arial',
        'weight': 'normal',
        'size'   : 12}

params={'mathtext.default': 'regular' }

plt.rcParams.update(params)
plt.rc('font', **font)

#fig.tight_layout()

#%%
fig.savefig('H:/Hydrogen/Figure/' + 'Fig4_pre1' + '.png', dpi=300, bbox_inches='tight')
fig1.savefig('H:/Hydrogen/Figure/' + 'Fig4_pre2' + '.png', dpi=300, bbox_inches='tight')
