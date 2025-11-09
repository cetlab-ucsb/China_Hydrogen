# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 14:59:59 2024

@author: haozheyang
"""

from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np


import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter
import matplotlib.ticker as ticker

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
file11='dispatch_capacity_commit_ccs.csv'
file12='imports_exports.csv'
file13='imports_exports_H2.csv'
file14='imports_exports_ccs.csv'
file15='load_balance.csv'
file16='H2_balance.csv'
file17='dispatch_gen_H2.csv'
file18='stor_ccs.csv'
    
test_id=['Hydrogen_REF_1period_36day',
         'Hydrogen_400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day_high_ccs_low_rate',
         'Hydrogen_400ppm_1period_36day_ccs_storage',
         'Hydrogen_400ppm_1period_36day_nuclear_flexible_500',
         'Hydrogen_400ppm_1period_36day_nuclear_flexible_500_highcost',
         'Hydrogen_400ppm_1period_36day_ccs_nuclear_flexible_500',  
         #'400ppm_1period_36day_ccs_storage',
         #'Hydrogen_400ppm_1period_36day_nuclear_500',
         #'Hydrogen_400ppm_1period_36day_nuclear_flexible_500',
         'Hydrogen_400ppm_1period_36day_nuclear_unlimited',
         ]

capacity=pd.DataFrame()
generation=pd.DataFrame()
cost=pd.DataFrame()
H2_production=pd.DataFrame()
generation_H2=pd.DataFrame()
carbon_capture=pd.DataFrame()
cost_group=pd.DataFrame()
dispatch=pd.DataFrame()
capacity_energy=pd.DataFrame()

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

    import_path=path+file12
    import_H2_path=path+file13
    import_ccs_path=path+file14
    load_balance_path=path+file15
    H2_balance_path=path+file16
    
    H2_production_path=path+file17
    ccs_commit_path=path+file11
    commit_path=path+'dispatch_capacity_commit.csv'
    stor_ccs_path=path+file18
    
    capacity_tmp=pd.read_csv(capacity_path)
    capacity_tmp.capacity_mw=capacity_tmp.capacity_mw/1000
    capacity_tmp.capacity_mwh=capacity_tmp.capacity_mwh/10**6
    
    generation_tmp=pd.read_csv(dispatch_path)
    generation_tmp.power_mw=generation_tmp.power_mw*generation_tmp.timepoint_weight/10**6
        
    H2_tmp=pd.read_csv(H2_path)
    H2_tmp.H2_mw=H2_tmp.H2_mw*H2_tmp.timepoint_weight/10**6
    
    if H2_tmp.H2_mw.sum()==0:
        H2_tmp=pd.DataFrame({
            'technology':['Electrolyzer','Fuel_cell','H2_turbine','Salt_cavern','Tank'],
            'H2_mw':[0,0,0,0,0]
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
    H2_technology_tmp['scenario']=case
    generation_technology_tmp['scenario']=case
    capacity_energy_technology_tmp['scenario']=case
    
    capacity_technology_tmp=capacity_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mw')
    capacity_energy_technology_tmp=capacity_energy_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mwh')
    H2_technology_tmp=H2_technology_tmp.pivot(index='scenario',columns='technology',values='H2_mw')
    generation_technology_tmp=generation_technology_tmp.pivot(index='scenario',columns='technology',values='power_mw')
        
    capacity=capacity.append(capacity_technology_tmp)
    generation_H2=generation_H2.append(H2_technology_tmp)
    generation=generation.append(generation_technology_tmp)  
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
    cost_tmp['scenario']=case
    cost_group=cost_group.append(cost_tmp)
    
    cost_tmp['total_cost']=(cost_tmp.capacity_cost+cost_tmp.variable_cost)
    cost_tmp=cost_tmp[['technology','total_cost']]
    cost_tmp['scenario']=case
    
    cost_tmp=cost_tmp.pivot(index='scenario',columns='technology',values='total_cost')
    
    cost=cost.append(cost_tmp)
        
    load=pd.read_csv(load_balance_path)
    load.load_mw=load.load_mw*load.timepoint_weight
    load_sum=load.load_mw.sum()
    
    H2=pd.read_csv(H2_balance_path)
    H2.H2_mw=H2.H2_mw*H2.timepoint_weight
    H2_sum=H2.H2_mw.sum()

    total_cost=cost_capacity_technology.capacity_cost.sum()+cost_operation_technology.variable_cost.sum()+cost_transmission.capacity_cost.sum()
    total_sum=load_sum+H2_sum  
    
    '''
    H2_production_tmp=pd.read_csv(H2_production_path)
    H2_production_tmp.H2_mw=H2_production_tmp.H2_mw*H2_production_tmp.timepoint_weight
    H2_production_tmp['scenario']=case
    H2_production=H2_production.append(H2_production_tmp[['scenario','H2_mw']])
    '''
    
    ccs_capture_tmp=pd.read_csv(stor_ccs_path)
    ccs_capture_tmp['ccs_capture_tonne']=ccs_capture_tmp.ccs_capture_tonne*ccs_capture_tmp.timepoint_weight/10**9        
    ccs_capture_tmp=ccs_capture_tmp.groupby('technology')['ccs_capture_tonne'].sum().reset_index()
    ccs_capture_tmp['scenario']=case
    ccs_capture_tmp=ccs_capture_tmp.pivot(index='scenario',columns='technology',values='ccs_capture_tonne')
    if ccs_capture_tmp.empty:
        ccs_capture_tmp=pd.DataFrame({
            'technology': 'Coal',
            'ccs_capture_tonne': 0},
            index=[case])
    carbon_capture=carbon_capture.append(ccs_capture_tmp)
    '''
    try:
        dispatch_tmp=pd.read_csv(ccs_commit_path)
    except:
        dispatch_tmp=pd.read_csv(commit_path)
        
    print(dispatch_tmp.gross_power_mw.sum())
    '''   
unitcost=cost/total_sum      
cost=cost/10**12

#%%

generation_capacity_order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','H2_turbine','Fuel_cell',
       ]

capacity_color=['#404040','#C0C0C0','#316589','#EA4855',
                '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#d9ed92','#3f37c9',
                ]

generation_capacity=capacity[generation_capacity_order]

transmission_color=['#b5179e','#f72585']
transmission_capacity=capacity[['Grid','H2_Pipeline']]

storage_capacity=capacity[['Battery','Pumped_hydro','H2_turbine','Fuel_cell']]
storage_capacity['charging_Battery']=-capacity.Battery
storage_capacity['charging_Pumped_hydro']=-capacity.Pumped_hydro
storage_capacity['charging_Electrolyzer']=-capacity.Electrolyzer

storage_capacity_color=['#FADC65','#94d2bd','#d9ed92','#3f37c9','#FADC65','#94d2bd','#0a9396']


order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
       'Salt_cavern', 'Tank',
       'Grid','H2_Pipeline','CO2_Pipeline',
       'DAC','CCS_storage']

cost=cost[order]
unitcost=unitcost[order]

order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
       'Salt_cavern','Tank','DAC']

generation=generation[order]

#%%
order=['Battery','Pumped_hydro','Salt_cavern','Tank']
capacity_energy=capacity_energy[order]
energy_color=['#FADC65','#94d2bd', '#8f470d','#a68a64',]
#%%
order=[
       'Electrolyzer','H2_turbine','Fuel_cell',
       'Salt_cavern','Tank']

generation_H2=generation_H2[order]

H2_color=['#0a9396','#d9ed92','#3f37c9',
       '#8f470d','#a68a64']


color=['#404040','#C0C0C0','#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       '#8f470d','#a68a64',
       '#b5179e','#f72585','#560bad',
       '#8ac926','#254d32']
#%%
color_generation=['#404040','#C0C0C0','#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       '#582f0e','#a68a64','#8ac926']

label=['Coal + CCS','Gas + CCS','Hydropower','Nuclear',
       'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro', 'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell',
       'Underground storage', 'Tank',
       'Electricity grid',' $H_{2}$ pipeline',' $CO_{2}$ pipeline','DAC','CCS storage']

#%%
fig,((ax1,ax2),(ax3,ax4),(ax5,ax6))=plt.subplots(nrows=3,ncols=2,figsize=(6, 8))

generation_capacity.plot.bar(ax=ax1,
                  stacked=True,
                  color=capacity_color,
                  legend=False)

transmission_capacity.plot.bar(ax=ax2,
                  stacked=True,
                  color=transmission_color,
                  legend=False)

storage_capacity.plot.bar(ax=ax3,
                  stacked=True,
                  color=storage_capacity_color,
                  legend=False)
ax3.axhline(0,color='black',linewidth=1)

capacity_energy.plot.bar(ax=ax4,
              stacked=True,
              color=energy_color,
              legend=False)

generation.plot.bar(ax=ax5,
                    stacked=True,
                    color=color_generation,
                    legend=False)


unitcost.plot.bar(ax=ax6,
                  stacked=True,
                  color=color,
                  legend=False)

plt.subplots_adjust(
                    wspace=0.5, 
                    hspace=0.2
                    )

handles, labels = ax6.get_legend_handles_labels()
#fig.legend(handles, labels, loc='upper center')

#fig.legend(handles,label,loc='center left', bbox_to_anchor=(0.9, 0.5),frameon=False)

fig.legend(reversed(handles[0:4]), reversed(label[0:4]),
           title='Conventional energy',
           loc='center left', bbox_to_anchor=(0.9, 0.05),frameon=False
           )._legend_box.align = "left"


fig.legend(reversed(handles[4:7]), reversed(label[4:7]),
           title='Renewable energy',
           loc='center left', bbox_to_anchor=(0.9, 0.21),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[7:9]), reversed(label[7:9]),
           title='Conventional storage',
           loc='center left', bbox_to_anchor=(0.9, 0.35),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[9]), [label[9]],
           title='Power to gas',
           loc='center left', bbox_to_anchor=(0.9, 0.45),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[10:12]), reversed(label[10:12]),
           title='Gas to power',
           loc='center left', bbox_to_anchor=(0.9, 0.55),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[12:14]), reversed(label[12:14]),
           title='Hydrogen storage',
           loc='center left', bbox_to_anchor=(0.9, 0.67),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[14:17]), reversed(label[14:17]),
           title='Transmission',
           loc='center left', bbox_to_anchor=(0.9, 0.79),
           frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[17:]), reversed(label[17:]),
           title='Carbon capture and storage',
           loc='center left', bbox_to_anchor=(0.9, 0.92),
           frameon=False
           )._legend_box.align = "left"

ax1.set_xticklabels('')
ax1.set_ylabel('GW')
ax1.set_xlabel('')
ax1.set_ylim([0,15000])
ax1.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

ax2.set_xticklabels('')
ax2.set_ylabel('GW')
ax2.set_xlabel('')
ax2.set_ylim([0,8000])
ax2.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

ax3.set_ylabel('GW')
ax3.set_xlabel('')
ax3.set_ylim([-3000,3000])
ax3.set_xticklabels('')
ax3.set_yticks([-2900,-1500,0,1500,2900])
ax3.set_yticklabels(['Discharge','1500','0','1500','Charge'])
ax3.yaxis.set_minor_locator(ticker.MultipleLocator(750))

ax4.set_ylabel('TWh')
ax4.set_xlabel('')
ax4.set_ylim([0,650])
ax4.set_xticklabels('')
ax4.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax4.yaxis.set_major_locator(ticker.MultipleLocator(100))
ax4.yaxis.set_minor_locator(ticker.MultipleLocator(50))

ax5.set_ylabel('TWh')
ax5.set_xlabel('')
ax5.set_xticklabels(['REF','ZE','ZE + CCS + DAC', 'ZE + CCS + DAC (Low cost+high efficiency)','ZE + Nuclear', 'ZE + Nuclear (high cost)', 'ZE + CCS + DAC + Nuclear', 'ZE + Unlimited nuclear'])

ax6.set_ylabel('$/MWh')
ax6.set_xlabel('')
ax6.set_xticklabels(['REF','ZE','ZE + CCS + DAC', 'ZE + CCS + DAC (Low cost+high efficiency)','ZE + Nuclear','ZE + Nuclear (high cost)', 'ZE + CCS + DAC + Nuclear', 'ZE + Unlimited nuclear'])

fig.align_ylabels([ax1,ax2,ax3,ax4,ax5,ax6])

font = {'family' : 'Arial',
        'weight': 'normal',
        'size'   : 12}

params={'mathtext.default': 'regular' }

plt.rcParams.update(params)
plt.rc('font', **font)
#fig.tight_layout()

#%% H2 production vs CO2 capture



#%%
fig.savefig('H:/Hydrogen/Figure/' + 'FigS3' + '.png', dpi=300, bbox_inches='tight')




