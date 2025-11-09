# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:16:50 2024

@author: haozheyang
"""

#cost of adding H2
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
file11='stor_ccs.csv'
file12='imports_exports.csv'
file13='imports_exports_H2.csv'
file14='imports_exports_ccs.csv'
file15='load_balance.csv'
file16='H2_balance.csv'
file17='carbon_emissions_by_project.csv'

    
test_id=[
         '400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day_lowcost',
         'Hydrogen_400ppm_1period_36day_highcost',
         'Hydrogen_400ppm_1period_36day_low_efficiency',
         'Hydrogen_400ppm_1period_36day_fossil_reserve'
         ]

capacity=pd.DataFrame()
capacity_energy=pd.DataFrame()
generation=pd.DataFrame()
generation_H2=pd.DataFrame()
cost=pd.DataFrame()

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
    carbon_path=path+file17
    
    carbon=pd.read_csv(carbon_path)
    print(carbon.carbon_emissions_tons.sum()*carbon.timepoint_weight.mean()/10**9)
    
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
            transmission_tmp.loc[line_id,'technology']='Pipeline'
        
    capacity_technology_tmp=capacity_tmp.groupby(['technology'])['capacity_mw'].sum().reset_index()
    capacity_energy_technology_tmp=capacity_tmp.groupby(['technology'])['capacity_mwh'].sum().reset_index()
    generation_technology_tmp=generation_tmp.groupby(['technology'])['power_mw'].sum().reset_index()
    H2_technology_tmp=H2_tmp.groupby(['technology'])['H2_mw'].sum().reset_index()
    transmission_technology_tmp=transmission_tmp.groupby(['technology'])['capacity_mw'].sum().reset_index()
    
    capacity_technology_tmp=capacity_technology_tmp.append(transmission_technology_tmp)
    capacity_technology_tmp['scenario']=case
    capacity_energy_technology_tmp['scenario']=case
    H2_technology_tmp['scenario']=case
    generation_technology_tmp['scenario']=case
    
    
    capacity_technology_tmp=capacity_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mw')
    capacity_energy_technology_tmp=capacity_energy_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mwh')
    H2_technology_tmp=H2_technology_tmp.pivot(index='scenario',columns='technology',values='H2_mw')
    generation_technology_tmp=generation_technology_tmp.pivot(index='scenario',columns='technology',values='power_mw')
        
    capacity=capacity.append(capacity_technology_tmp)
    capacity_energy=capacity_energy.append(capacity_energy_technology_tmp)
    generation_H2=generation_H2.append(H2_technology_tmp)
    generation=generation.append(generation_technology_tmp)  
    '''
    H2_tmp=pd.read_csv(H2_path)
    H2_tmp.H2_mw=H2_tmp.H2_mw*H2_tmp.timepoint_weight/10**6
    H2_pos_tmp= H2_tmp.loc[H2_tmp.H2_mw>0,:]
    H2_neg_tmp= H2_tmp.loc[H2_tmp.H2_mw<0,:]
    
    if H2_tmp.H2_mw.sum()==0:
        H2_pos_tmp=pd.DataFrame({
            'technology':['Electrolyzer','Fuel_cell','H2_turbine','Salt_cavern','Tank'],
            'H2_mw':[0,0,0,0,0]
            })
        
    H2_technology_pos_tmp=H2_pos_tmp.groupby(['technology'])['H2_mw'].sum().reset_index()
    H2_technology_pos_tmp['scenario']=case
    
    H2_technology_pos_tmp=H2_technology_pos_tmp.pivot(index='scenario',columns='technology',values='H2_mw')
    generation_H2=generation_H2.append(H2_technology_pos_tmp)    
    '''
    cost_capacity=pd.read_csv(capacity_cost_path)
    
    cost_operation=pd.read_csv(operation_cost_path).fillna(0)
    cost_operation['variable_cost']=(cost_operation.variable_om_cost+cost_operation.fuel_cost)*cost_operation.timepoint_weight
    
    cost_transmission=pd.read_csv(transmission_cost_path)
    cost_transmission['technology']='Grid'
    
    for line_id, line in enumerate(cost_transmission.tx_line):
        if 'H2' in line:
            cost_transmission.loc[line_id,'technology']='Pipeline'
        
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
    
    H2=pd.read_csv(H2_balance_path)
    H2.H2_mw=H2.H2_mw*H2.timepoint_weight
    H2_sum=H2.H2_mw.sum()

    total_cost=cost_capacity_technology.capacity_cost.sum()+cost_operation_technology.variable_cost.sum()+cost_transmission.capacity_cost.sum()
    total_sum=load_sum+H2_sum  

unitcost=cost/total_sum      
cost=cost/10**12

capacity_factor=generation/capacity/8760*1000
unitcost.sum(axis=1)
#%%
scenario_id=[
         '400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day_lowcost',
         'Hydrogen_400ppm_1period_36day_highcost',
         'Hydrogen_400ppm_1period_36day_low_efficiency'
         ]

generation_capacity_order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','H2_turbine','Fuel_cell',
       ]

capacity_color=['#404040','#C0C0C0','#316589','#EA4855',
                '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#d9ed92','#3f37c9',
                ]

generation_capacity=capacity.loc[scenario_id,generation_capacity_order]


transmission_color=['#b5179e','#f72585']
transmission_capacity=capacity[['Grid','Pipeline']]

storage_capacity=capacity[['Battery','Pumped_hydro','H2_turbine','Fuel_cell']]
storage_capacity['charging_Battery']=-capacity.Battery
storage_capacity['charging_Pumped_hydro']=-capacity.Pumped_hydro
storage_capacity['charging_Electrolyzer']=-capacity.Electrolyzer
storage_capacity_color=['#FADC65','#94d2bd','#d9ed92','#3f37c9','#FADC65','#94d2bd','#0a9396']

generation_order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
       'Salt_cavern','Tank']

generation=generation.loc[scenario_id,generation_order]

order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
       'Salt_cavern', 'Tank',
       'Grid','Pipeline']

#cost=cost[order]
unitcost=unitcost.loc[scenario_id,order]




energy_order=['Battery','Salt_cavern','Tank']

capacity_energy=capacity_energy.loc[scenario_id,energy_order]

storage_color=['#FADC65','#8f470d','#a68a64']

color=['#404040','#C0C0C0','#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       '#8f470d','#a68a64',
       '#b5179e','#f72585']

label=['Coal','Gas','Hydropower','Nuclear',
       'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro', 'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell',
       'Underground storage', 'Tank',
       'Electricity grid','Hydrogen pipeline']

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
              color=storage_color,
              legend=False)

generation.plot.bar(ax=ax5,
                    stacked=True,
                    color=color,
                    legend=False)


unitcost.plot.bar(ax=ax6,
                  stacked=True,
                  color=color,
                  legend=False)

plt.subplots_adjust(
                    wspace=0.5, 
                    hspace=0.3
                    )

handles, labels = ax6.get_legend_handles_labels()

fig.legend(reversed(handles[0:4]), reversed(label[0:4]),
           title='Conventional energy',
           loc='center left', bbox_to_anchor=(0.9, 0.1),frameon=False
           )._legend_box.align = "left"


fig.legend(reversed(handles[4:7]), reversed(label[4:7]),
           title='Renewable energy',
           loc='center left', bbox_to_anchor=(0.9, 0.26),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[7:9]), reversed(label[7:9]),
           title='Conventional storage',
           loc='center left', bbox_to_anchor=(0.9, 0.4),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[9]), [label[9]],
           title='Power to gas',
           loc='center left', bbox_to_anchor=(0.9, 0.5),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[10:12]), reversed(label[10:12]),
           title='Gas to power',
           loc='center left', bbox_to_anchor=(0.9, 0.6),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[12:14]), reversed(label[12:14]),
           title='Hydrogen storage',
           loc='center left', bbox_to_anchor=(0.9, 0.72),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[14:16]), reversed(label[14:16]),
           title='Transmission',
           loc='center left', bbox_to_anchor=(0.9, 0.84),
           frameon=False
           )._legend_box.align = "left"


'''
l1._legend_box.align = "left"
l2._legend_box.align = "left"
l3._legend_box.align = "left"
l4._legend_box.align = "left"
'''

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
ax4.set_ylim([0,750])
ax4.set_xticklabels('')
ax4.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax4.yaxis.set_major_locator(ticker.MultipleLocator(100))
ax4.yaxis.set_minor_locator(ticker.MultipleLocator(50))

ax5.set_ylabel('TWh')
ax5.set_xlabel('')
ax5.set_ylim([-5000,20000])
ax5.set_xticklabels(['ZE w/o $H_{2}$','ZE','ZE + Low cost', 'ZE + high cost', 'ZE + high cost + low efficiency'])

ax6.set_ylabel('$/MWh')
ax6.set_xlabel('')
ax6.set_xticklabels(['ZE w/o $H_{2}$','ZE','ZE + Low cost', 'ZE + high cost', 'ZE + high cost + low efficiency'])

fig.align_ylabels([ax1,ax2,ax3,ax4,ax5,ax6])


font = {'family' : 'Arial',
        'weight': 'normal',
        'size'   : 12}

plt.rc('font', **font)

params={'mathtext.default': 'regular',
        'legend.title_fontsize' : 14}

plt.rcParams.update(params)

fig.text(0,0.9,'a', fontweight="bold")
fig.text(0.47,0.9,'b', fontweight="bold")
fig.text(0.0,0.64,'c', fontweight="bold")
fig.text(0.47,0.64,'d', fontweight="bold")
fig.text(0.0,0.35,'e', fontweight="bold")
fig.text(0.47,0.35,'f', fontweight="bold")


fig.savefig('H:/Hydrogen/Figure/' + 'FigS1' + '.png', dpi=300, bbox_inches='tight')
