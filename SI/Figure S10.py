# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:35:18 2024

@author: haozheyang
"""

#cost of adding H2
from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter

pio.renderers.default='browser'
        
test_id=[
         'Hydrogen_400ppm_1period_36day',
         'Hydrogen_400ppm_1period_36day_pipeline',
         'Hydrogen_400ppm_1period_36day_noturbine',
         'Hydrogen_400ppm_1period_36day_tank',
         'Hydrogen_400ppm_1period_36day_grid',
         'Hydrogen_400ppm_1period_36day_safe',
         '400ppm_1period_36day'
         ]

cost=pd.DataFrame()
import_total=pd.DataFrame()
generation_H2=pd.DataFrame()
capacity_energy=pd.DataFrame()
capacity=pd.DataFrame()
generation=pd.DataFrame()

for case in test_id:
    output=DataFrame()
    output_capacity=DataFrame()
    output_capacity_province=DataFrame()
    output_generation=DataFrame()
    output_generation_province=DataFrame()
    
    path='H:/Hydrogen/Data/'+case+'/results/'
    
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
    capacity_energy_technology_tmp=capacity_tmp.groupby(['technology'])['capacity_mwh'].sum().reset_index()
    capacity_energy_technology_tmp['scenario']=case
    capacity_energy_technology_tmp=capacity_energy_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mwh')
    capacity_energy=capacity_energy.append(capacity_energy_technology_tmp)
    
    transmission_tmp=pd.read_csv(transmission_capacity_path)
    transmission_tmp['technology']='Grid'
    transmission_tmp['capacity_mw']=abs(transmission_tmp.transmission_max_capacity_mw)/1000
    
    for line_id, line in enumerate(transmission_tmp.tx_line):
        if 'H2' in line:
            transmission_tmp.loc[line_id,'technology']='Pipeline'
        
    capacity_technology_tmp=capacity_tmp.groupby(['technology'])['capacity_mw'].sum().reset_index()
    transmission_technology_tmp=transmission_tmp.groupby(['technology'])['capacity_mw'].sum().reset_index()
    
    capacity_technology_tmp=capacity_technology_tmp.append(transmission_technology_tmp)
    capacity_technology_tmp['scenario']=case    
    
    capacity_technology_tmp=capacity_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mw')
    capacity=capacity.append(capacity_technology_tmp)
    
    generation_tmp=pd.read_csv(dispatch_path)
    generation_tmp.power_mw=generation_tmp.power_mw*generation_tmp.timepoint_weight/10**6
    generation_technology_tmp=generation_tmp.groupby(['technology'])['power_mw'].sum().reset_index()
    generation_technology_tmp['scenario']=case
    generation_technology_tmp=generation_technology_tmp.pivot(index='scenario',columns='technology',values='power_mw')
    generation=generation.append(generation_technology_tmp)      
    
    cost_capacity=pd.read_csv(capacity_cost_path)
    
    cost_operation=pd.read_csv(operation_cost_path).fillna(0)
    cost_operation['variable_cost']=(cost_operation.variable_om_cost+cost_operation.fuel_cost)*cost_operation.timepoint_weight
    
    try:
        cost_transmission=pd.read_csv(transmission_cost_path)
        cost_transmission['technology']='Grid'    
        for line_id, line in enumerate(cost_transmission.tx_line):
            if 'H2' in line:
                cost_transmission.loc[line_id,'technology']='Pipeline'
    except:
        cost_transmission=pd.DataFrame({'technology': ['Grid'],
                                        'capacity_cost': 0})
        
    cost_capacity_technology=cost_capacity.groupby(['technology'])['capacity_cost'].sum().reset_index()
    cost_operation_technology=cost_operation.groupby(['technology'])['variable_cost'].sum().reset_index()
    cost_transmission=cost_transmission.groupby(['technology'])['capacity_cost'].sum().reset_index()
    
    cost_tmp=cost_capacity_technology.merge(cost_operation_technology)
    cost_tmp=cost_tmp.append(cost_transmission).fillna(0)
    
    cost_tmp['total_cost']=cost_tmp.capacity_cost+cost_tmp.variable_cost
    cost_tmp=cost_tmp[['technology','total_cost']]
    cost_tmp['scenario']=case
    
    cost_tmp=cost_tmp.pivot(index='scenario',columns='technology',values='total_cost')
    
    cost=cost.append(cost_tmp)
    
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
    
    load=pd.read_csv(load_balance_path)
    load.load_mw=load.load_mw*load.timepoint_weight
    load_sum=load.load_mw.sum()
    
    H2=pd.read_csv(H2_balance_path)
    H2.H2_mw=H2.H2_mw*H2.timepoint_weight
    H2_sum=H2.H2_mw.sum()

    total_cost=cost_capacity_technology.capacity_cost.sum()+cost_operation_technology.variable_cost.sum()+cost_transmission.capacity_cost.sum()
    total_sum=load_sum+H2_sum
    
    import_tmp=pd.read_csv(import_path)
    import_tmp.net_imports_mw=import_tmp.net_imports_mw*import_tmp.timepoint_weight/10**6
    
    import_H2_tmp=pd.read_csv(import_H2_path)
    import_H2_tmp.net_imports_H2_mw=import_H2_tmp.net_imports_H2_mw*import_H2_tmp.timepoint_weight/10**6
    
    import_total_tmp=import_tmp.loc[import_tmp.net_imports_mw>0,'net_imports_mw'].sum()
    import_H2_total_tmp=import_H2_tmp.loc[import_H2_tmp.net_imports_H2_mw>0,'net_imports_H2_mw'].sum()
    
    import_total=import_total.append(
        pd.DataFrame(
        {
        'total_import': [import_total_tmp],
        'total_H2_import': import_H2_total_tmp,
        },
        index=[case]
        )
        )
    
    print(total_cost/total_sum)                      

#%%
order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
       'Salt_cavern','Tank',
       'Grid','Pipeline']

cost=cost[order]

scenario_order=['Hydrogen_400ppm_1period_36day_safe',
                  'Hydrogen_400ppm_1period_36day_tank',
                  'Hydrogen_400ppm_1period_36day_grid',
                  'Hydrogen_400ppm_1period_36day_noturbine',
                  'Hydrogen_400ppm_1period_36day_pipeline',
                  'Hydrogen_400ppm_1period_36day',
                  '400ppm_1period_36day']
    
cost_ze=cost.loc[scenario_order,:]
cost_ze=cost_ze.fillna(0)
cost_ze=(cost_ze-cost_ze.loc['Hydrogen_400ppm_1period_36day',:])/cost_ze.loc['Hydrogen_400ppm_1period_36day'].sum()

generation_H2=generation_H2.loc[scenario_order,:]
import_total=import_total.loc[scenario_order,:]
capacity_energy=capacity_energy.loc[scenario_order,:]

color=['#404040','#C0C0C0','#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       '#8f470d','#a68a64',
       '#b5179e','#f72585']

H2_color=['#0a9396',
       '#8f470d','#a68a64']

order=['Electrolyzer',
       'Salt_cavern','Tank']

generation_H2=generation_H2[order]

label=['Coal','Gas','Hydropower','Nuclear',
       'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro', 'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell',
       'Underground storage', 'Tank',
       'Electricity grid','Hydrogen pipeline']

capacity_energy=capacity_energy[['Battery','Salt_cavern','Tank']]
H2_storage_color=['#FADC65','#8f470d','#a68a64']
#%%
fig,(ax1,ax2,ax3)=plt.subplots(nrows=3,ncols=1,figsize=(10, 15),sharex=True,sharey=False)

#print(plt.rcParams.get('figure.figsize'))

plt.subplots_adjust(
                    hspace=0.2
                    )

bar_ze=cost_ze.plot.bar(ax=ax1,
                        stacked=True,
                        color=color,
                        label=label,
                        legend=False)


ax1.axhline(y=0,color='black',linewidth=0.5)
line_ze=ax1.vlines(x=[0.4,1.4,2.4,3.4,4.4,5.4,6.4],ymin=0,ymax=cost_ze.sum(axis=1),zorder=2)


capacity_energy.plot.bar(ax=ax2,
                         stacked=True,
                         color=H2_storage_color,
                         legend=False)
ax2.axhline(y=0,color='black',linewidth=0.5)
ax2_1=ax2.twinx()

import_total.plot.bar(
    ax=ax3,
    #stacked=True,
    legend=False,
    color=['#b5179e','#f72585']
    )
ax3.axhline(y=0,color='black',linewidth=0.5)

#ax1.title.set_text('REF')
#ax2.title.set_text('90%')
#ax3.title.set_text('Zero emission')
font = {'family' : 'Arial',
        'weight': 'normal',
        'size'   : 12}

plt.rc('font', **font)

params={'mathtext.default': 'regular',
        'legend.title_fontsize' : 14}

plt.rcParams.update(params)

ax1.set_ylim([-0.5,0.5])
#ax1.set_yticks([-0.25,0,0.25,0.5,0.75,1])
ax1.set_yticklabels(['{:,.0%}'.format(x) for x in ax1.get_yticks()])
ax1.set_ylabel('Change in cost')
ax1.set_xticklabels(['w/o new electricity grid\n& $H_{2}$ pipeline',
                     'w/o underground storage',
                     'w/o new electricity grid',
                     'w/o $H_{2}$ turbine',
                     'w/o $H_{2}$ pipeline',
                     'ZE',
                     'ZE w/o $H_{2}$'],
                    fontsize=14)

ax1.tick_params(axis='x',top=True, labeltop=True, bottom=False, labelbottom=False,labelrotation=90)

ax2.set_ylabel('Hydrogen production (TWh)')
ax2.set_ylim([0,900])
ax2_1.set_ylim([0,900/33.3])
ax2_1.set_ylabel('million tonne')

ax3.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax3.set_ylabel('Energy trade (TWh)')
ax3.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

fig.align_ylabels([ax1,ax2,ax3])

handles,labels=ax1.get_legend_handles_labels()

'''
legend1=ax1.legend(handles1[0:4],label[0:4],
                   loc='center left', 
                   frameon=False,
                   bbox_to_anchor=(1, 1),
                   title="Conventional energy",
                   title_fontsize=14,#default font size=10
                   prop={'family':'Arial','size':12}) 

legend1._legend_box.align = "left"



dummy_lines=(plt.plot([],[], c="blue", marker='|', linestyle = 'None',markersize=15, markeredgewidth=2))

                  
legend2=ax1.legend( dummy_lines, ["Change in cost %"], 
                    loc=(1,0.0),
                    frameon=False,
                    title="Total",
                    title_fontsize=14)

legend2._legend_box.align = "left"

#legend2=plt.legend(handles1[-1],[['total']],loc='center left', bbox_to_anchor=(1, 0))

ax1.add_artist(legend1)
'''

dummy_lines=plt.plot([],[], c="blue", marker='|', linestyle = 'None',markersize=15, markeredgewidth=2)

fig.legend(dummy_lines, ['Net change in cost %'],
           title='Net change',
           loc='center left', bbox_to_anchor=(0.98, 0.8),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[0:4]), reversed(label[0:4]),
           title='Conventional energy',
           loc='center left', bbox_to_anchor=(0.98, 0.25),frameon=False
           )._legend_box.align = "left"


fig.legend(reversed(handles[4:7]), reversed(label[4:7]),
           title='Renewable energy',
           loc='center left', bbox_to_anchor=(0.98, 0.35),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[7:9]), reversed(label[7:9]),
           title='Conventional storage',
           loc='center left', bbox_to_anchor=(0.98, 0.42),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[9]), [label[9]],
           title='Power to gas',
           loc='center left', bbox_to_anchor=(0.98, 0.50),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[10:12]), reversed(label[10:12]),
           title='Gas to power',
           loc='center left', bbox_to_anchor=(0.98, 0.56),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[12:14]), reversed(label[12:14]),
           title='Hydrogen storage',
           loc='center left', bbox_to_anchor=(0.98, 0.64),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[14:16]), reversed(label[14:16]),
           title='Transmission',
           loc='center left', bbox_to_anchor=(0.98, 0.71),
           frameon=False
           )._legend_box.align = "left"


#plt.legend(label,loc='center left', bbox_to_anchor=(1, 1.3))
fig.text(0,0.87,'a', fontweight="bold",fontsize=14)
fig.text(0,0.61,'b', fontweight="bold",fontsize=14)
fig.text(0,0.35,'c', fontweight="bold",fontsize=14)

fig.savefig('H:/Hydrogen/Figure/' + 'Fig2' + '.png', dpi=300, bbox_inches='tight')

