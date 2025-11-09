# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 14:51:57 2023

@author: haozheyang
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 17:02:45 2022

@author: haozheyang
"""


from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default='browser'
        
s1=['Hydrogen_1p5C','Hydrogen_1p5C_no_trans','Hydrogen_1p5C_100_RE']
s=s1

region=read_excel('H:/electricity modeling/labor/province_region.xlsx')

output=DataFrame()
output_capacity=DataFrame()
output_capacity_province=DataFrame()
output_generation=DataFrame()
output_generation_province=DataFrame()

for test_id in s:
    
    path='H:/Hydrogen/Data/'+test_id+'/results/'

    file1='dispatch_all.csv'
    file2='carbon_emissions_by_project.csv'
    file3='costs_capacity_all_projects.csv'
    file4='costs_operations.csv'
    file5='costs_transmission_capacity.csv'
    file6='capacity_all.csv'
    file7='transmission_new_capacity.csv'
    file8='capacity_gen_new_lin.csv'
    file9='capacity_stor_new_lin.csv'

    dispatch_path=path+file1
    capacity_path=path+file6
    carbon_path=path+file2
    capacity_cost_path=path+file3
    operation_cost_path=path+file4
    transmission_cost_path=path+file5
    transmission_capacity_path=path+file7
    capacity_new_path=path+file8
    stor_new_path=path+file9
    

#dispatch
    dispatch=read_csv(dispatch_path)
    dispatch.loc[dispatch.project.str.contains('Offshore'),'technology']='Offshore_wind'
    dispatch.loc[dispatch.project.str.contains('Hydrogen_turbine'),'technology']='Hydrogen_turbine'
    dispatch.loc[dispatch.project.str.contains('Hydrogen_fuel'),'technology']='Hydrogen_fuel_cell'
    dispatch.loc[dispatch.project.str.contains('Battery'),'technology']='Battery'
    dispatch.loc[dispatch.project.str.contains('Hydro_Pumped'),'technology']='Hydro_Pumped'
    
    dispatch_hourly=dispatch.loc[dispatch.period==2040,].groupby(['timepoint','technology'])['power_mw'].sum().reset_index()
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

    
    color_map = [ '#FB6F6F',
                 '#F4A666',
                 '#BA75FF',
                 '#6FFFFF',
                 '#EDE76D',
                 '#4FBDFF',
                 '#1E3CFF',
                 '#B0FFB0',
                 '#6b5ca5',
                 '#b0a990',
                 '#39304a']
    
    labels=['Coal',
            'Gas',
            'Nuclear',
            'Hydro',
            'Solar',
            'Wind',
            'Offshore wind',
            'Battery',
            'Hydro Pumped',
            'Hydrogen turbine',
            'Hydrogen fuel cell']
    day=np.linspace(1,365,365)
    
    fig,ax=plt.subplots()
    #df_pos.plot.area(ax=ax)
    #ax.set_prop_cycle(None)
    #df_neg.rename(columns=lambda x: '_' + x).plot.area(ax=ax)
    ax.stackplot(day,
                 df_pos.Coal,
                 df_pos.Gas,
                 df_pos.Nuclear,
                 df_pos.Hydro,
                 df_pos.Solar,
                 df_pos.Wind,
                 df_pos.Offshore_wind,
                 df_pos.Battery,
                 df_pos.Hydro_Pumped,
                 df_pos.Hydrogen_turbine,
                 df_pos.Hydrogen_fuel_cell,
                 colors=color_map,
                 labels=labels)
    
    ax.stackplot(day,
             df_neg.Coal,
             df_neg.Gas,
             df_neg.Nuclear,
             df_neg.Hydro,
             df_neg.Solar,
             df_neg.Wind,
             df_neg.Offshore_wind,
             df_neg.Battery,
             df_neg.Hydro_Pumped,
             df_neg.Hydrogen_turbine,
             df_neg.Hydrogen_fuel_cell,
             colors=color_map)
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
    
    ax.legend(bbox_to_anchor=(1.5, 0.5),loc='right')
    ax.set_ylim([-2*10**7,2*10**7])
    
    mean_dispatch=dispatch.groupby(['period','load_zone','project','technology'])['power_mw'].mean().reset_index()
    def power_total(x):
        return sum(x)*8760/10**6

    capacity_technology=mean_dispatch.groupby(['period','technology'])['power_mw'].sum().reset_index()
    output_technology=mean_dispatch.groupby(['period','technology'])['power_mw'].apply(power_total).reset_index()
    output_technology_province=mean_dispatch.groupby(['period','load_zone','technology'])['power_mw'].apply(power_total).reset_index()
    
    Inner_Mongolia_tmp1=output_technology_province.loc[output_technology_province.load_zone=='East_Inner_Mongolia',]
    Inner_Mongolia_tmp2=output_technology_province.loc[output_technology_province.load_zone=='West_Inner_Mongolia',]
    Inner_Mongolia_tmp=Inner_Mongolia_tmp1.merge(Inner_Mongolia_tmp2,how='inner',on=['period','technology'])

    Inner_Mongolia_output=DataFrame({
        'load_zone': 'Inner Mongolia',
        'period':Inner_Mongolia_tmp['period'],
        'technology': Inner_Mongolia_tmp['technology'],
        'power_mw':Inner_Mongolia_tmp['power_mw_x']+Inner_Mongolia_tmp['power_mw_y']
        })
    
    output_technology_province=output_technology_province.append(Inner_Mongolia_output,ignore_index=True)
    output_technology_province=output_technology_province.drop(output_technology_province[output_technology_province['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
    
    output_generation=output_technology_province.groupby(['period','load_zone'])['power_mw'].sum().reset_index()
    output_generation['scenario']=test_id
    output_generation_province=output_generation_province.append(output_generation)
    
    output_technology_province=output_technology_province.pivot(index=['period','load_zone'],columns='technology',values='power_mw')
   # output_technology_province.to_excel('data visualization/generation/generation_tech_'+test_id+'.xlsx',na_rep=0)

    output_technology['scenario']=test_id
    output=output.append(output_technology)
           
    
    
    capacity=read_csv(capacity_path)
    capacity.loc[capacity.project.str.contains('Offshore'),'technology']='Offshore_wind'
    capacity.loc[capacity.project.str.contains('Hydrogen_turbine'),'technology']='Hydrogen_turbine'
    capacity.loc[capacity.project.str.contains('Hydrogen_fuel'),'technology']='Hydrogen_fuel_cell'
    capacity.loc[capacity.project.str.contains('Battery'),'technology']='Battery'
    capacity.loc[capacity.project.str.contains('Hydro_Pumped'),'technology']='Hydro_Pumped'
    capacity_technology=capacity.groupby(['period','technology'])['capacity_mw'].sum().reset_index()
    capacity_technology['scenario']=test_id
    output_capacity=output_capacity.append(capacity_technology)
    
    capacity_2040=capacity.loc[capacity.period==2040,:]
    capacity_2040=capacity_2040.groupby(['period','load_zone','technology'])['capacity_mw'].sum().reset_index()
    
    Inner_Mongolia_tmp1=capacity_2040.loc[capacity_2040.load_zone=='East_Inner_Mongolia',]
    Inner_Mongolia_tmp2=capacity_2040.loc[capacity_2040.load_zone=='West_Inner_Mongolia',]
    Inner_Mongolia_tmp=Inner_Mongolia_tmp1.merge(Inner_Mongolia_tmp2,how='inner',on=['period','technology'])

    Inner_Mongolia_load=DataFrame({
        'load_zone': 'Inner Mongolia',
        'period':Inner_Mongolia_tmp['period'],
        'technology': Inner_Mongolia_tmp['technology'],
        'capacity_mw':Inner_Mongolia_tmp['capacity_mw_x']+Inner_Mongolia_tmp['capacity_mw_y']
        })
    
    capacity_2040=capacity_2040.append(Inner_Mongolia_load, ignore_index=True)
    capacity_2040=capacity_2040.drop(capacity_2040[capacity_2040['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
    capacity_2040['scenario']=test_id
    output_capacity_province=output_capacity_province.append(capacity_2040)
    
output_capacity['capacity_mw']=output_capacity['capacity_mw']/1000

#output_capacity_province=output_capacity_province.loc[output_capacity_province.technology.isin(['Hydro','Solar','Wind','Offshore_wind']),:]
output_capacity_province=output_capacity_province.loc[output_capacity_province.technology.isin(['Coal','Gas']),:]

output_capacity_province=output_capacity_province.merge(region).groupby(['region','scenario'])['capacity_mw'].sum().reset_index()
output_capacity_region=output_capacity_province.pivot(index='region',columns='scenario',values='capacity_mw').sort_index(axis=1,ascending=False)
region_order=['Northeast','East Coast','Central','West']
output_capacity_region=output_capacity_region.loc[region_order,:]   

output_capacity_region=output_capacity_region[s]

output_generation_province=output_generation_province.merge(region).groupby(['region','period','scenario'])['power_mw'].sum().reset_index()
output_generation_region=output_generation_province.pivot(index=['region','period'],columns='scenario',values='power_mw').sort_index(axis=1,ascending=False)
region_order=['Northeast','East Coast','Central','West']
output_generation_region=output_generation_region.loc[region_order,:]   

#output_capacity=output_capacity.pivot(index=['period','scenario'],columns='technology',values='capacity_mw')
#output_capacity=output_capacity.sort_index(axis=0,level=['period','scenario'],ascending=[True,False])
#output_capacity.to_csv('data_analysis/capacity_mix_prm_uncertain.csv')

#file_output='data_analysis/generation_mix_prm_uncertain.csv'
#output_generation=output.pivot(index=['period','scenario'],columns='technology',values='power_mw')  
#output_generation=output_generation.sort_index(axis=0,level=['period','scenario'],ascending=[True,False])
#output_generation.to_csv(file_output,index=False)
#%%
coal_color = '#FB6F6F'
gas_color = '#F4A666'
hydro_color = '#6FFFFF'
nuclear_color = '#BA75FF'
solar_color = '#EDE76D'
battery_color = '#B0FFB0'
pump_color='#6b5ca5'
wind_color = '#4FBDFF'
offshore_color='#1E3CFF'
turbine_color='#b0a990'
cell_color='#39304a'

#scenario_axis=np.repeat(['REF','$2{^\circ}C$',"$1.5{^\circ}C$"],24)
#scenario_axis=np.concatenate([scenario_axis,np.repeat(['Hydrogen_REF','Hydrogen_2C','Hydrogen_1p5C'],30)],axis=0)

scenario_axis=np.repeat(['Hydrogen_1p5C','No new Transmission','100% RE'],22)  #technology * number of period

#scenario_axis_num=np.repeat([1,3,5],24)
#scenario_axis_num=np.concatenate([scenario_axis_num,np.repeat([2,4,6],30)],axis=0)
scenario_axis_num=np.repeat([1,2,3],22)

label=['A','B']
fig = make_subplots(rows=2, cols=2, shared_yaxes=False,shared_xaxes=False, 
                    subplot_titles=("Capacity", "Generation")
                    )
for i in range(1):
    scenario=s[i*3:i*3+3]
    output_capacity_tmp=output_capacity.loc[output_capacity.scenario.isin(scenario),:]
    output_generation_tmp=output.loc[output.scenario.isin(scenario),:]
    
    output_capacity_tmp['scenario']=scenario_axis
    output_capacity_tmp['scenario_id']=scenario_axis_num
    output_generation_tmp['scenario']= scenario_axis
    output_generation_tmp['scenario_id']=scenario_axis_num
    
    output_capacity_tmp=output_capacity_tmp.pivot(index=['period','scenario','scenario_id'],columns='technology',values='capacity_mw').sort_index(level=['period','scenario_id'],ascending=[True,True])
    output_generation_tmp=output_generation_tmp.pivot(index=['period','scenario','scenario_id'],columns='technology',values='power_mw').sort_index(level=['period','scenario_id'],ascending=[True,True])

    
    x1 = [list(output_capacity_tmp.index.get_level_values(0)),
          list(output_capacity_tmp.index.get_level_values(1))]
    
    if i==0:
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Coal), name='Coal', marker_color=coal_color,legendgroup='Coal'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Gas), name='Gas', marker_color=gas_color,legendgroup='Gas'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydro), name='Hydro', marker_color=hydro_color,legendgroup='Hdyro'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Nuclear), name='Nuclear', marker_color=nuclear_color,legendgroup='Nuclear'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Offshore_wind), name='Offshore wind', marker_color=offshore_color,legendgroup='Offshore wind'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Wind), name='Onshore wind', marker_color=wind_color,legendgroup='Onshore wind'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Solar), name='Solar', marker_color=solar_color,legendgroup='Solar'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Battery), name='Battery', marker_color=battery_color,legendgroup='Storage'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydro_Pumped), name='Pumped hydro', marker_color=pump_color,legendgroup='Pumped hydro'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydrogen_turbine), name='Hydrogen turbine', marker_color=turbine_color,legendgroup='Hydrogen turbine'),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydrogen_fuel_cell), name='Hydrogen fuel cell', marker_color=cell_color,legendgroup='Hydrogen fuel cell'),row=i+1,col=1)
        #fig['layout']['yaxis'].update(range=[0,10000],tickformat=',d')
    elif i==1:
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Coal), name='Coal', marker_color=coal_color,legendgroup='Coal',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Gas), name='Gas', marker_color=gas_color,legendgroup='Gas',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydro), name='Hydro', marker_color=hydro_color,legendgroup='Hdyro',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Nuclear), name='Nuclear', marker_color=nuclear_color,legendgroup='Nuclear',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Offshore_wind), name='Offshore wind', marker_color=offshore_color,legendgroup='Offshore wind',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Wind), name='Onshore wind', marker_color=wind_color,legendgroup='Onshore wind',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Solar), name='Solar', marker_color=solar_color,legendgroup='Solar',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Battery), name='Battery', marker_color=battery_color,legendgroup='Battery',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydro_Pumped), name='Pumped hydro', marker_color=pump_color,legendgroup='Pumped hydro',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydrogen_turbine), name='Hydrogen turbine', marker_color=turbine_color,legendgroup='Hydrogen turbine',showlegend=False),row=i+1,col=1)
        fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydrogen_fuel_cell), name='Hydrogen fuel cell', marker_color=cell_color,legendgroup='Hydrogen fuel cell',showlegend=False),row=i+1,col=1)
        #fig['layout']['yaxis'+str(i*2+1)].update(range=[0,10000],tickformat=',d')
    fig.update_yaxes(range=[0,15000],tickformat=',d',row=i+1,col=1)
    fig.add_annotation(xref='x domain',
                   yref='y domain',
                   x=0.01,
                   y=1.1,
                   text=label[2*i], 
                   font=dict(size=20),
                   showarrow=False,
                   row=i+1, col=1)
    
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Coal), name='Coal', marker_color=coal_color,legendgroup='Coal',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Gas), name='Gas', marker_color=gas_color,legendgroup='Gas',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Hydro), name='Hydro', marker_color=hydro_color,legendgroup='Hdyro',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Nuclear), name='Nuclear', marker_color=nuclear_color,legendgroup='Nuclear',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Offshore_wind), name='Offshore wind', marker_color=offshore_color,legendgroup='Offshore wind',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Wind), name='Onshore wind', marker_color=wind_color,legendgroup='Onshore wind',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Solar), name='Solar', marker_color=solar_color,legendgroup='Solar',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Battery), name='Battery', marker_color=battery_color,legendgroup='Battery',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Hydro_Pumped), name='Pumped hydro', marker_color=pump_color,legendgroup='Pumped hydro',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Hydrogen_turbine), name='Hydrogen_turbine', marker_color=turbine_color,legendgroup='Hydrogen turbine',showlegend=False),row=i+1,col=2)
    fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Hydrogen_fuel_cell), name='Hydrogen_cell', marker_color=cell_color,legendgroup='Hydorgen fuel cell',showlegend=False),row=i+1,col=2)
    #fig['layout']['yaxis'+str(i*2+2)].update(range=[0,15000],tickformat=',d')
    fig.update_yaxes(range=[-5000,20000],tickformat=',d',row=i+1,col=2)
    fig.add_annotation(xref='x domain',
                   yref='y domain',
                   x=0.01,
                   y=1.1,
                   font=dict(size=20),
                   text=label[2*i+1], 
                   showarrow=False,
                   row=i+1, col=2)
#Remove white lines separating elements of bars
#fig.update_traces(marker_line_width = 0, 
#                  selector=dict(type="bar"))

  
fig.update_layout(barmode="relative", font = dict(size=12),
                  width=1200, height=600, 
                  plot_bgcolor='white',legend_traceorder="reversed",#showlegend=False)
                  legend=dict(yanchor="top",y=0.71,xanchor="left", x=1.00), margin=dict(l=10,r=10,b=10,t=10),
                  )

fig.update_yaxes(showgrid=True,linecolor='black')
fig.update_xaxes(showgrid=True,linecolor='black')
                 
fig['layout']['yaxis1'].update(title_text="Capacity (GW)",
                               title_font=dict(size=16)
                               )

fig['layout']['yaxis2'].update(title_text="Generation (TWh)", 
                              title_font = dict(size=16)            
                              )
        
fig.show()
fig.write_image( 'H:/Hydrogen/mix_hydro_1p5.jpeg')
