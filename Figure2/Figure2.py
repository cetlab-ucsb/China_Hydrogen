# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:29:33 2024

@author: haozheyang
"""

from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np
#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
#import plotly.io as pio

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter

#pio.renderers.default='browser'
        

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
         'Hydrogen_400ppm_1period_36day_H2_SMR',
         'Hydrogen_400ppm_1period_36day_H2_expand_decouple_flat',
         'Hydrogen_400ppm_1period_36day_H2_expand_flat',
         #'Hydrogen_400ppm_1period_36day_onlyH2_expand',  
         #'Hydrogen_400ppm_1period_36day_ccs_storage',
         #'Hydrogen_400ppm_1period_36day_H2_expand_ccs',
         'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_80_decouple',
         'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_80_flat'
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
    df_neg=pd.concat([df_neg,df_neg_tmp])

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
    
    capacity_technology_tmp=pd.concat([capacity_technology_tmp,transmission_technology_tmp])
    capacity_technology_tmp['scenario']=case
    generation_technology_tmp['scenario']=case
    H2_technology_tmp['scenario']=case
    capacity_energy_technology_tmp['scenario']=case

    capacity_technology_tmp=capacity_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mw')
    generation_technology_tmp=generation_technology_tmp.pivot(index='scenario',columns='technology',values='power_mw')
    H2_technology_tmp=H2_technology_tmp.pivot(index='scenario',columns='technology',values='H2_mw')
    capacity_energy_technology_tmp=capacity_energy_technology_tmp.pivot(index='scenario',columns='technology',values='capacity_mwh')

    capacity=pd.concat([capacity,capacity_technology_tmp])
    generation=pd.concat([generation,generation_technology_tmp])  
    generation_H2=pd.concat([generation_H2,H2_technology_tmp])
    capacity_energy=pd.concat([capacity_energy,capacity_energy_technology_tmp])


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
    
    #df_load_tmp= load.copy()
    #df_load_tmp['month']=df_load_tmp.timepoint.astype(str).str[0:6]
    #df_load_tmp['day']=df_load_tmp.timepoint.astype(str).str[0:8]
    #df_load_tmp=df_load_tmp.groupby(['month'])['load_mw'].sum().reset_index()

    
    load_H2=pd.read_csv(H2_balance_path)
    load_H2.H2_mw=load_H2.H2_mw * load_H2.timepoint_weight
    H2_sum=load_H2.H2_mw.sum()

    total_cost=cost_capacity_technology.capacity_cost.sum()+cost_operation_technology.variable_cost.sum()+cost_transmission.capacity_cost.sum()
    total_sum=load_sum+H2_sum  

    unitcost=pd.concat([unitcost,cost_tmp/total_sum])
    print(total_cost)
    
cost=cost/10**12
#%%
'''
order=['Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell',
       'Salt_cavern','Tank',
       'Grid','H2_Pipeline']
'''
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
'''
color=['#404040','#C0C0C0','#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       '#8f470d','#a68a64',
       '#b5179e','#f72585'
       ]
'''
unitcost=unitcost[order]
unitcost=unitcost.loc[[
                       'Hydrogen_400ppm_1period_36day',
                       'Hydrogen_400ppm_1period_36day_H2_expand_decouple_flat',
                       'Hydrogen_400ppm_1period_36day_H2_expand_flat',
                       #'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_conservative_decouple',
                       'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_80_flat',
                       ],:]
unitcost=unitcost[::-1]

generation_order=[
        'Coal','Gas','Hydro','Nuclear',
       'Offshore_Wind','Wind','Solar','Battery','Pumped_hydro','Electrolyzer','H2_turbine','Fuel_cell'
       ]

generation=generation[generation_order]

generation_color=['#404040','#C0C0C0','#316589','#EA4855',
       '#84BBD7','#2897C0','#F7AE39','#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9',
       ]


generation_H2_order=['Fuel_cell','H2_turbine','SMR','Gasification']
generation_H2=generation_H2[generation_H2_order]
generation_H2['H2_consumption']=-generation_H2[['Fuel_cell','H2_turbine']].sum(axis=1)
generation_H2.loc[:,'demand']=H2_sum/10**6
generation_H2=generation_H2.loc[[ 
                                'Hydrogen_400ppm_1period_36day',
                                'Hydrogen_400ppm_1period_36day_H2_expand_decouple_flat',
                                'Hydrogen_400ppm_1period_36day_H2_expand_flat',
                                #'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_conservative_decouple',
                                'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_80_flat',
                                 ],['H2_consumption','demand','SMR']
    ]

generation_H2.loc['Hydrogen_400ppm_1period_36day','demand']=0

#decouple='Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_conservative_decouple',
#generation_H2.loc[decouple,'demand']=generation_H2.loc[decouple,'demand']-generation_H2.loc[decouple,'SMR']

couple='Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs_80_flat',
generation_H2.loc[couple,'demand']=generation_H2.loc[couple,'demand']-generation_H2.loc[couple,'SMR']


generation_H2=generation_H2[::-1]

storage_color=[
       '#FADC65','#94d2bd','#0a9396','#d9ed92','#3f37c9'
       ]

'''
label=[
       'Coal','Gas',
       'Hydropower','Nuclear',
       'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro',
       'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell',
       'Underground storage', 'Tank',
       'Grid',' $H_{2}$ pipeline'
       ]
'''
label=['Coal','Gas','Hydropower','Nuclear',
       'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro', 'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell',
       'Steam methane reforming + CCS','Gasification + CCS',
       'Underground storage', 'Tank',
       'Grid',' $H_{2}$ pipeline',
       ' $CO_{2}$ pipeline','DAC','CCS storage'
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

generation_label=[
           'Coal','Gas','Hydropower','Nuclear',
           'Offshore wind', 'Onshore wind', 'Solar', 'Battery', 'Pumped hydro',
           'Electrolyzer', 'Hydrogen combustion turbine','Fuel cell'
           ]

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
        lcoe_SMR_full[i,j]=(SMR_cost*1000+SMR_gas*8760*gas_cost)/8760*120/3600 +0.8*120/3600 

X, Y = np.meshgrid(price_range,SMR_range)


gasification=386506.2796
gasification_range=np.linspace(40,600,100)

gasification_coal=5.3 #mmbtu per MWh

coal_price_range=np.linspace(2,6,100)


lcoe_gasification_full=np.zeros((len(gasification_range),len(coal_price_range)))

for i, gasification_cost in enumerate(gasification_range):
    for j, coal_cost in enumerate(coal_price_range):
        lcoe_gasification_full[i,j]=(gasification_cost*1000+gasification_coal*8760*coal_cost)/8760*120/3600 + 1.3*120/3600

X_coal, Y_coal = np.meshgrid(coal_price_range,gasification_range)
#%%
fig = plt.figure() 

fig.set_figheight(12)
fig.set_figwidth(10)


#ax1 = plt.subplot2grid(shape=(3, 2), loc=(0, 0), colspan=1)
#ax2 = plt.subplot2grid(shape=(3, 2), loc=(0, 1), colspan=1)
ax3 = plt.subplot2grid(shape=(2, 2), loc=(0, 0), colspan=1)
ax4 = plt.subplot2grid(shape=(2, 2), loc=(0, 1), colspan=1)
ax5 = plt.subplot2grid(shape=(2, 2), loc=(1, 0), colspan=1)
ax6 = plt.subplot2grid(shape=(2, 2), loc=(1, 1), colspan=1)

plt.subplots_adjust(hspace=0.5,
                    wspace=0.3)

unitcost.plot.barh(ax=ax3,
                  stacked=True,
                  color=color,
                  legend=False)
ax3.set_title('Cost of energy', y= 1.15)

generation_H2.plot.barh(ax=ax4,
                  stacked=True,
                  color=['#0a9396','#0a9396','#03045e'],
                  edgecolor='white',
                  legend=True)
ax4_1=ax4.twiny()

for container, hatch in zip(ax4.containers, ("","x", "x")):
    for patch in container.patches:
        patch.set_hatch(hatch)

handles1, labels1 = ax4.get_legend_handles_labels()

ax4.set_title('Hydrogen demand', y=1.15)
ax4.legend([handles1[0],handles1[1]],['Long-term storage','Fuel/feedstock'],frameon=False)


day=np.linspace(1,12,12)

df_pos_h=df_pos.loc[df_pos.scenario=='Hydrogen_400ppm_1period_36day']
df_neg_h=df_neg.loc[df_neg.scenario=='Hydrogen_400ppm_1period_36day']

df_pos_h.drop('scenario',axis=1).sum(axis=1)+df_neg_h.drop('scenario',axis=1).sum(axis=1)
'''
ax1.stackplot(day,
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

ax1.stackplot(day,
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
             colors=storage_color
             )

ax1.axhline(y=0,color='black',linewidth=0.5)

df_pos_d=df_pos.loc[df_pos.scenario=='Hydrogen_400ppm_1period_36day_H2_expand']
df_neg_d=df_neg.loc[df_neg.scenario=='Hydrogen_400ppm_1period_36day_H2_expand']
ax2.stackplot(day,
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

ax2.stackplot(day,
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

ax2.axhline(y=0,color='black',linewidth=0.5)
ax2_1=ax2.twinx()
'''

lg='lightgray'

level1=[0.4,
        0.7,
        1,
        1.3,
        1.6,
        1.9,
        2.2,
        2.5,
        ]

level2=[
        1.82,
        1.88,
        2.34,
        ]

CF=ax5.contourf(X, Y, lcoe_SMR_full,
                      level1,
                      extend='both'
                      )


CS=ax5.contour(X, Y, lcoe_SMR_full,
                      level2,zorder=2,
                      colors=['k','k','k'],
                      linestyles=['-','--','--']
                      )

manual_locations = [
                    #(2, 60), 
                    #(5, 60), 
                    #(7, 60), 
                    (9, 50), 
                    (11, 60),
                    (13, 70), 
                    ]

ax5.clabel(CS,
          # levels=[1.88,1.93,2.4],
           inline=True,
           colors='k',
           fontsize=12,
           fmt=' {:.2f} '.format,
           manual=manual_locations
           )

ax5.plot([14.23,8.31],[59,59], marker='o', color='r')
#ax4.scatter(13.85,59,s=320, marker='*', color='r')

CF=ax6.contourf(X_coal, Y_coal, lcoe_gasification_full,
                      level1,
                      extend='both',
                      )

CS=ax6.contour(X_coal, Y_coal, lcoe_gasification_full,
                      level2,zorder=2,
                      colors=['k','k','k'],
                      linestyles=['-','--','--'])

manual_locations = [
                    #(2.5, 60), 
                    #(3, 100), 
                    #(3.5, 200), 
                    (5, 200), 
                    (3,380),
                    (2.5, 500)
                    ]

clabels=ax6.clabel(CS,
           #levels=[1.88,1.93,2.4],
           inline=True,
           colors='k',
           fontsize=12,
           fmt=' {:.2f} '.format,
           manual=manual_locations
           )

ax6.plot([5.8,2.03],[387,387], marker='o', color='r') #15,000 $/pound
#ax5.scatter(4.5,301,s=320, marker='*', color='r')

cbar_ax = fig.add_axes([0.98, 0.16, 0.015, 0.2])
cbar=fig.colorbar(CF, orientation='vertical',cax=cbar_ax)
cbar.set_label('Levelized cost of hydrogen $/kg',labelpad=15)

handles, labels = ax3.get_legend_handles_labels()
#fig.legend(handles, labels, loc='upper center')

#fig.legend(handles,label,loc='center left', bbox_to_anchor=(0.9, 0.5),frameon=False)

fig.legend(reversed(handles[2:4]), reversed(label[2:4]),
           title='Conventional energy',
           loc='center left', bbox_to_anchor=(0.98, 0.42),frameon=False
           )._legend_box.align = "left"


fig.legend(reversed(handles[4:7]), reversed(label[4:7]),
           title='Renewable energy',
           loc='center left', bbox_to_anchor=(0.98, 0.49),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[7:9]), reversed(label[7:9]),
           title='Conventional storage',
           loc='center left', bbox_to_anchor=(0.98, 0.56),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[9]), [label[9]],
           title='Power to gas',
           loc='center left', bbox_to_anchor=(0.98, 0.61),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[10:12]), reversed(label[10:12]),
           title='Gas to power',
           loc='center left', bbox_to_anchor=(0.98, 0.66),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[12:14]), reversed(label[12:14]),
           title='Fossil fuel-based hydrogen',
           loc='center left', bbox_to_anchor=(0.98, 0.72),frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[14:16]), reversed(label[14:16]),
           title='Hydrogen storage',
           loc='center left', bbox_to_anchor=(0.98, 0.78),
           frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[16:19]), reversed(label[16:19]),
           title='Transmission',
           loc='center left', bbox_to_anchor=(0.98, 0.85),
           frameon=False
           )._legend_box.align = "left"

fig.legend(reversed(handles[19:]), reversed(label[19:]),
           title='Carbon capture and storage',
           loc='center left', bbox_to_anchor=(0.98, 0.92),
           frameon=False
           )._legend_box.align = "left"

#line1, = plt.plot([],[],markersize=25, marker='*',color='r',linestyle = 'None')

line1, = plt.plot([],[],color='k',linestyle = '-')
line2, = plt.plot([],[],color='k',linestyle = '--')

line3, = plt.plot([],[], color=lg,linestyle = '-') 
line4, = plt.plot([],[], color='r',linestyle = '-') 

# Create another legend for the second line.
fig.legend(#handles=[line3,line4],
           handles=[line4],
           #labels=['Contour line: fixed cost+fuel cost','fixed cost(2050)+fuel cost(2018-2023)'],
           labels=['fixed cost(2050)+fuel cost(2018-2023)'],
           title='Levelized cost of gray hyrogen $/kg', 
           loc='center left',
           bbox_to_anchor=(0.98, 0.11),
          frameon=False
          )._legend_box.align = "left"


leg = fig.legend(handles=[line1,line2],labels=['ZE+$H_{2}$ demand','uncertainty range by costs and efficiencies'], 
           loc='center left',
           title='Hydrogen-only cost $/kg',
           bbox_to_anchor=(0.98, 0.04),
          frameon=False
          )._legend_box.align = "left"

ax3.set_yticklabels([ 
                     'ZE+$H_{2}$ demand+Blue',
                     #'ZE+$H_{2}$ demand+Blue\n+decouple',
                     'ZE+$H_{2}$ demand',
                     'ZE+$H_{2}$ demand\n+decouple',
                     'ZE',
                     ],fontsize=14,rotation=0)


ax3.set_ylabel('')
ax3.set_xlabel('$/MWh',fontsize=14)
#ax1.set_ylim([-10000,25000])
#ax1.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax4.set_yticklabels('')
'''
ax4.set_yticklabels([
                     'ZE',
                     'ZE +\n$H_{2}$\ndemand\n+ decouple',
                     'ZE +\n$H_{2}$\ndemand',
                     'ZE+\n$H_{2}$\ndemand+\nBlue+\ndecouple',
                     'ZE+\n$H_{2}$\ndemand+\nBlue',
                     ],fontsize=14,rotation=0)
'''
ax4.set_ylabel('')
ax4.set_xlabel('TWh',fontsize=14)
ax4.set_xlim([0,8000])
ax4_1.set_xlabel('million tonne',fontsize=14)
ax4_1.set_xlim([0,8000/33.3])

'''
ax1.set_title('Electricity charge and discharge\n under the ZE scenario')
ax1.set_ylabel('TWh',fontsize=14)
ax1.set_xlabel('')
ax1.set_xlim([1,12])
ax1.set_ylim([-1000,450])
ax1.set_xticks(day)
ax1.set_xticklabels(['Jan','Feb','Mar','Arp','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],rotation=90)


ax2.set_title('Electricity charge and discharge\n under the ZE + $H_{2}$ demand scenario')
ax2.set_ylabel('')
ax2.set_xlabel('')
ax2.set_ylim([-1000,450])
ax2.set_xlim([1,12])
ax2.set_yticklabels('')
ax2.set_xticks(day)
ax2.set_xticklabels(['Jan','Feb','Mar','Arp','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],rotation=90)
ax2.set_xlabel('')
ax2_1.set_ylim([-1000/33.3,450/33.3])
ax2_1.set_ylabel('million tonne',fontsize=14)
'''



ax5.set_ylabel('Fixed annual cost of $H_{2}$ infrastructure \n($/kW/yr)',fontsize=14)
ax5.set_xlabel('Cost of natural gas \n $/mmBtu',fontsize=14)
ax6.set_xlabel('Cost of coal \n $/mmBtu',fontsize=14)

ax5.set_title('Levelized cost of gray hydrogen\n produced by natural gas')
ax6.set_title('Levelized cost of gray hydrogen\n produced by coal')

#fig.align_ylabels([ax2,ax4])

#fig.text(0.5,0.64,'Month',fontsize=14)
#fig.text(0.5,0.09,'$/mmbtu')

fig.text(0.05 , 0.88,'a', fontweight="bold",fontsize=14)
fig.text(0.5,0.88,'b', fontweight="bold",fontsize=14)

fig.text(0.05,0.45,'c', fontweight="bold",fontsize=14)
fig.text(0.5,0.45,'d', fontweight="bold",fontsize=14)

#fig.text(0.05,0.6,'c', fontweight="bold",fontsize=14)
#fig.text(0.5,0.6,'d', fontweight="bold",fontsize=14)
#fig.text(0.05,0.34,'e', fontweight="bold",fontsize=14)
#fig.text(0.5,0.34,'f', fontweight="bold",fontsize=14)

fig.text(0.5,0.34,'f', fontweight="bold",fontsize=14)

font = {'family' : 'Arial',
        'weight': 'normal',
        'size'   : 12}

params={'mathtext.default': 'regular' }

plt.rcParams.update(params)
plt.rc('font', **font)

plt.show()
#fig.tight_layout()

#%%
fig.savefig('/Users/hy4174/Documents/Hydrogen/Figure/revision/' + 'Fig4' + '.png', dpi=300, bbox_inches='tight')
