# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 15:40:45 2024

@author: haozheyang
"""

from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default='browser'
        
test_id='test_ccs_stor_new_2zones'


output=DataFrame()
output_capacity=DataFrame()
output_capacity_province=DataFrame()
output_generation=DataFrame()
output_generation_province=DataFrame()

path='C:/Program Files/GRIDPATH/scenarios/'+test_id+'/results/'

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

#dispatch
dispatch=read_csv(dispatch_path)

mean_dispatch=dispatch.groupby(['period','load_zone','project','technology'])['power_mw'].mean().reset_index()

output_technology=dispatch.groupby(['period','load_zone','technology'])['power_mw'].sum().reset_index()

output_technology['scenario']=test_id

               
capacity=read_csv(capacity_path)

capacity_technology=capacity.groupby(['period','load_zone','technology'])['capacity_mw'].sum().reset_index()
capacity_technology['scenario']=test_id

dispatch_H2=read_csv(H2_path)

H2_technology=dispatch_H2.groupby(['period','load_zone','technology'])['H2_mw'].sum().reset_index()

H2_technology['scenario']=test_id   


dispatch_ccs=read_csv(ccs_path)
ccs_technology=dispatch_ccs.groupby(['period','load_zone'])['ccs_storage_tonne','ccs_capture_tonne'].sum().reset_index()
ccs_technology['scenario']=test_id   
#%%
coal_color = '#FB6F6F'
gas_color = '#F4A666'
#hydro_color = '#6FFFFF'
nuclear_color = '#BA75FF'
solar_color = '#EDE76D'
storage_color = '#B0FFB0'
wind_color = '#4FBDFF'
#offshore_color='#1E3CFF'
p2g_color='#b0a990'
cell_color='#39304a'
smr_color='#bc6c25'

ccs_capture_color='#c1121f'
ccs_storage_color='#780000'
#scenario_axis=np.repeat(['REF','$2{^\circ}C$',"$1.5{^\circ}C$"],24)
#scenario_axis=np.concatenate([scenario_axis,np.repeat(['Hydrogen_REF','Hydrogen_2C','Hydrogen_1p5C'],30)],axis=0)
output_capacity_tmp=capacity_technology.pivot(index=['period','load_zone'],columns=['technology'],values='capacity_mw')
output_generation_tmp=output_technology.pivot(index=['period','load_zone'],columns=['technology'],values='power_mw')
output_H2_tmp=H2_technology.pivot(index=['period','load_zone'],columns=['technology'],values='H2_mw')

label=['A','B','C']
fig = make_subplots(rows=1, cols=3, shared_yaxes=False,shared_xaxes=False, 
                    subplot_titles=("Capacity", "Generation","CO2 generation")
                    )


x1 = [list(output_capacity_tmp.index.get_level_values(0)),
      list(output_capacity_tmp.index.get_level_values(1))]

x1=list(output_capacity_tmp.index.get_level_values(1))
#go.Bar(output_technology,x='load_zone',y='power_mw')

fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Coal), name='Coal', marker_color=coal_color,legendgroup='Coal'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Gas), name='Gas', marker_color=gas_color,legendgroup='Gas'),row=1,col=1)
#fig.add_trace(go.Bar(x=x1, y=list(output_technology.Hydro), name='Hydro', marker_color=hydro_color,legendgroup='Hdyro'),row=i+1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Nuclear), name='Nuclear', marker_color=nuclear_color,legendgroup='Nuclear'),row=1,col=1)
#fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Offshore_wind), name='Offshore wind', marker_color=offshore_color,legendgroup='Offshore wind'),row=i+1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Wind), name='Wind', marker_color=wind_color,legendgroup='Wind'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Solar), name='Solar', marker_color=solar_color,legendgroup='Solar'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.H2_Storage), name='H2 Storage', marker_color=storage_color,legendgroup='H2 Storage'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Electrolyzer), name='power to H2', marker_color=p2g_color,legendgroup='Power to H2'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Fuel_cell), name='H2 to power', marker_color=cell_color,legendgroup='H2 to power'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Fuel_cell), name='H2 to power', marker_color=cell_color,legendgroup='H2 to power'),row=1,col=1)



fig.update_yaxes(range=[0,150],dtick=20,ticks="inside",tickformat=',d',row=1,col=1)
'''
fig.add_annotation(xref='x domain',
               yref='y domain',
               x=0.01,
               y=0.5,
               text=label[0], 
               font=dict(size=20),
               showarrow=False,
               row=1, col=1)
'''

fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Coal), name='Coal', marker_color=coal_color,legendgroup='Coal',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Gas), name='Gas', marker_color=gas_color,legendgroup='Gas',showlegend=False),row=1,col=2)
#fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Hydro), name='Hydro', marker_color=hydro_color,legendgroup='Hdyro',showlegend=False),row=i+1,col=2)
#fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Nuclear), name='Nuclear', marker_color=nuclear_color,legendgroup='Nuclear',showlegend=False),row=1,col=2)
#fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Offshore_wind), name='Offshore wind', marker_color=offshore_color,legendgroup='Offshore wind',showlegend=False),row=i+1,col=2)
#fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Wind), name='Wind', marker_color=wind_color,legendgroup='Onshore wind',showlegend=False),row=1,col=2)
#fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Solar), name='Solar', marker_color=solar_color,legendgroup='Solar',showlegend=False),row=1,col=2)
#fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.H2_Storage), name='H2 Storage', marker_color=storage_color,legendgroup='Storage',showlegend=False),row=1,col=2)
#fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Electrolyzer), name='power to H2', marker_color=p2g_color,legendgroup='Power to H2',showlegend=False),row=1,col=2)
#fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Fuel_cell), name='H2 to power', marker_color=cell_color,legendgroup='H2 to power',showlegend=False),row=1,col=2)

fig.update_yaxes(range=[-50,180],dtick=20,ticks="inside",tickformat=',d',row=1,col=2)
'''
fig.add_annotation(xref='x domain',
               yref='y domain',
               x=0.01,
               y=0.5,
               font=dict(size=20),
               text=label[1], 
               showarrow=False,
               row=1, col=2)
'''
#Remove white lines separating elements of bars
#fig.update_traces(marker_line_width = 0, 
#                  selector=dict(type="bar"))
'''
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.H2_Storage), name='H2 Storage', marker_color=storage_color,legendgroup='Storage',showlegend=False),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.Electrolyzer), name='power to H2', marker_color=p2g_color,legendgroup='Power to H2',showlegend=False),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.Fuel_cell), name='H2 to power', marker_color=cell_color,legendgroup='H2 to power',showlegend=False),row=1,col=3)
'''
x2=list(ccs_technology.load_zone)
fig.add_trace(go.Bar(x=x1, y=list(-ccs_technology.ccs_storage_tonne), name='CCS storage', marker_color=ccs_storage_color,legendgroup='CCS storage'),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(ccs_technology.ccs_capture_tonne), name='CCS capture', marker_color=ccs_capture_color,legendgroup='CCS storage'),row=1,col=3)

fig.update_yaxes(range=[-20,60],dtick=10,ticks="inside",tickformat=',d',row=1,col=3)
'''
fig.add_annotation(xref='x domain',
               yref='y domain',
               x=0.01,
               y=0.5,
               font=dict(size=20),
               text=label[2], 
               showarrow=False,
               row=1, col=3) 
'''

fig.update_layout(barmode="relative", font = dict(size=16),
                  width=1200, height=400, 
                  plot_bgcolor='white',legend_traceorder="reversed",#showlegend=False)
                  legend=dict(font=dict(size= 28),yanchor="top",y=1,xanchor="left", x=1.00), margin=dict(l=10,r=10,b=10,t=10),
                  )

fig.update_yaxes(showgrid=True,linecolor='black')
fig.update_xaxes(showgrid=True,linecolor='black')
                 
fig['layout']['yaxis1'].update(title_text="Capacity (MW)",
                               title_font=dict(size=16)
                               )

fig['layout']['yaxis2'].update(title_text="Generation (MWh)", 
                              title_font = dict(size=16)            
                              )
'''
fig['layout']['yaxis3'].update(title_text="H2 (MWh)", 
                              title_font = dict(size=16)            
                            )
'''

fig['layout']['yaxis3'].update(title_text="CO2 (tonne)", 
                              title_font = dict(size=16)            
                            )
     
fig.show()
fig.write_image( 'H:/Hydrogen/test/'+test_id+'.jpeg')
