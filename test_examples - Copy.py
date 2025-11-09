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

import matplotlib.pyplot as plt

pio.renderers.default='browser'
        
test_id='Hydrogen_400ppm_1period_36day_safe'


output=DataFrame()
output_capacity=DataFrame()
output_capacity_province=DataFrame()
output_generation=DataFrame()
output_generation_province=DataFrame()

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

mean_dispatch=dispatch.groupby(['period','load_zone','project','technology'])['power_mw'].sum().reset_index()

output_technology=dispatch.groupby(['period','load_zone','technology'])['power_mw'].sum().reset_index()

output_technology['scenario']=test_id

               
capacity=read_csv(capacity_path)
capacity.loc[capacity.project.str.contains('Offshore'),'technology']='Offshore_wind'
capacity.capacity_mw=capacity.capacity_mw/1000
capacity_technology=capacity.groupby(['period','load_zone','technology'])['capacity_mw'].sum().reset_index()
capacity_technology['scenario']=test_id

capacity_technology_all=capacity.groupby(['period','technology'])['capacity_mw'].sum().reset_index()



dispatch_H2=read_csv(H2_path)
dispatch_H2.H2_mw=dispatch_H2.H2_mw*dispatch_H2.timepoint_weight/10**6

H2_technology=dispatch_H2.groupby(['period','load_zone','technology'])['H2_mw'].sum().reset_index()
H2_technology['scenario']=test_id   

try:
    dispatch_ccs=read_csv(ccs_path)
    ccs_technology=dispatch_ccs.groupby(['period','load_zone'])['ccs_storage_tonne','ccs_capture_tonne'].sum().reset_index()
    ccs_technology['scenario']=test_id 
except:
    pass


#transmission
import_ele=pd.read_csv(import_path)
import_ele['net_imports_mw']=import_ele.timepoint_weight*import_ele.net_imports_mw/10**6
import_ele=import_ele.groupby(['period','load_zone'])['net_imports_mw'].sum().reset_index()


import_H2=pd.read_csv(import_H2_path)
import_H2['net_imports_H2_mw']=import_H2.timepoint_weight*import_H2.net_imports_H2_mw/10**6
import_H2=import_H2.groupby(['period','load_zone'])['net_imports_H2_mw'].sum().reset_index()

fig, (ax1,ax2) = plt.subplots(nrows=1, ncols=2, sharey=True)

ax1.barh(import_ele.load_zone.str.replace("_"," "), import_ele.net_imports_mw)
ax2.barh(import_H2.load_zone.str.replace("_"," "), import_H2.net_imports_H2_mw)

plt.draw()

ax1.set_yticklabels(ax1.get_yticklabels(), fontsize=8)
ax1.set_xticklabels(ax1.get_xticklabels(), fontsize=10)
ax2.set_xticklabels(ax2.get_xticklabels(), fontsize=10)

try:
    import_ccs=pd.read_csv(import_ccs_path)
    import_ccs['net_imports_tonne']=import_ccs.timepoint_weight*import_ccs.net_imports_tonne
    import_ccs=import_ccs.groupby(['period','load_zone'])['net_imports_tonne'].sum()
except:
    pass
#%%
coal_color = '#FB6F6F'
gas_color = '#F4A666'
hydro_color = '#6FFFFF'
nuclear_color = '#BA75FF'
solar_color = '#EDE76D'
storage_color = '#B0FFB0'
wind_color = '#4FBDFF'
offshore_color='#1E3CFF'
electrolyzer_color='#b0a990'
fuel_cell_color='#39304a'
H2_turbine_color='#606c38'
pumped_hydro_color="#345211"
tank_color="#fefae0"
underground_color="#a69005"
SMR_color='#bc6c25'
gasification_color='#bc6c25'

ccs_capture_color='#c1121f'
ccs_storage_color='#780000'
#scenario_axis=np.repeat(['REF','$2{^\circ}C$',"$1.5{^\circ}C$"],24)
#scenario_axis=np.concatenate([scenario_axis,np.repeat(['Hydrogen_REF','Hydrogen_2C','Hydrogen_1p5C'],30)],axis=0)
output_capacity_tmp=capacity_technology.pivot(index=['period','load_zone'],columns=['technology'],values='capacity_mw')
output_generation_tmp=output_technology.pivot(index=['period','load_zone'],columns=['technology'],values='power_mw')
output_H2_tmp=H2_technology.pivot(index=['period','load_zone'],columns=['technology'],values='H2_mw')

label=['A','B','C']
fig = make_subplots(rows=1, cols=3, shared_yaxes=False,shared_xaxes=False, 
                    subplot_titles=("Capacity", "Generation","H2 generation")
                    )


x1 = [list(output_capacity_tmp.index.get_level_values(0)),
      list(output_capacity_tmp.index.get_level_values(1))]

x1=list(output_capacity_tmp.index.get_level_values(1))
#go.Bar(output_technology,x='load_zone',y='power_mw')

fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Coal), name='Coal', marker_color=coal_color,legendgroup='Coal'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Gas), name='Gas', marker_color=gas_color,legendgroup='Gas'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Hydro), name='Hydro', marker_color=hydro_color,legendgroup='Hdyro'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Nuclear), name='Nuclear', marker_color=nuclear_color,legendgroup='Nuclear'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Offshore_wind), name='Offshore wind', marker_color=offshore_color,legendgroup='Offshore wind'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Battery), name='Battery', marker_color=storage_color,legendgroup='Battery'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Pumped_hydro), name='Pumped hydro', marker_color=pumped_hydro_color,legendgroup='Pumped hydro'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Wind), name='Wind', marker_color=wind_color,legendgroup='Wind'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Solar), name='Solar', marker_color=solar_color,legendgroup='Solar'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Tank), name='H2 tank Storage', marker_color=tank_color,legendgroup='H2 Storage'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Salt_cavern), name='Salt cavern', marker_color=underground_color,legendgroup='H2 Storage'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Electrolyzer), name='Electrolyzer', marker_color=electrolyzer_color,legendgroup='Power to H2'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.Fuel_cell), name='Fuel cell', marker_color=fuel_cell_color,legendgroup='H2 to power'),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_capacity_tmp.H2_turbine), name='H2 combustion turbine', marker_color=H2_turbine_color,legendgroup='H2 to power'),row=1,col=1)



fig.update_yaxes(range=[0,3000],dtick=200,ticks="inside",tickformat=',d',row=1,col=1)

'''
fig.add_annotation(xref='x domain',
               yref='y domain',
               x=0.01,
               y=0.5,
               text=label[0], 
               font=dict(size=6),
               showarrow=False,
               row=1, col=1)
'''
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Coal), name='Coal', marker_color=coal_color,legendgroup='Coal',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Gas), name='Gas', marker_color=gas_color,legendgroup='Gas',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Hydro), name='Hydro', marker_color=hydro_color,legendgroup='Hdyro',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Nuclear), name='Nuclear', marker_color=nuclear_color,legendgroup='Nuclear',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Offshore_Wind), name='Offshore wind', marker_color=offshore_color,legendgroup='Offshore wind',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Wind), name='Wind', marker_color=wind_color,legendgroup='Wind',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Solar), name='Solar', marker_color=solar_color,legendgroup='Solar',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Battery), name='Battery', marker_color=storage_color,legendgroup='Battery',showlegend=False),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Pumped_hydro), name='Pumped hydro', marker_color=pumped_hydro_color,legendgroup='Pumped hydro',showlegend=False),row=1,col=1)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Tank), name='H2 tank Storage', marker_color=tank_color,legendgroup='H2 Storage',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Salt_cavern), name='Salt cavern', marker_color=underground_color,legendgroup='H2 Storage',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Electrolyzer), name='Electrolyzer', marker_color=electrolyzer_color,legendgroup='Power to H2',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.Fuel_cell), name='Fuel cell', marker_color=fuel_cell_color,legendgroup='H2 to power',showlegend=False),row=1,col=2)
fig.add_trace(go.Bar(x=x1, y=list(output_generation_tmp.H2_turbine), name='H2 combustion turbine', marker_color=H2_turbine_color,legendgroup='H2 to power',showlegend=False),row=1,col=2)

fig.update_yaxes(range=[-2000,3000],dtick=500,ticks="inside",tickformat=',d',row=1,col=2)
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

fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.SMR), name='SMR', marker_color=SMR_color,legendgroup='H2 to power',showlegend=False),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.Gasification), name='Gasification', marker_color=gasification_color,legendgroup='H2 to power',showlegend=False),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.Tank), name='H2 tank Storage', marker_color=tank_color,legendgroup='Storage',showlegend=False),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.Salt_cavern), name='Salt_cavern', marker_color=underground_color,legendgroup='Storage',showlegend=False),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.Electrolyzer), name='Electrolyzer', marker_color=electrolyzer_color,legendgroup='Power to H2',showlegend=False),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.Fuel_cell), name='Fuel cell', marker_color=fuel_cell_color,legendgroup='H2 to power',showlegend=False),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(output_H2_tmp.H2_turbine), name='H2 combustion turbine', marker_color=H2_turbine_color,legendgroup='H2 to power',showlegend=False),row=1,col=3)

'''
x2=list(ccs_technology.load_zone)
fig.add_trace(go.Bar(x=x1, y=list(-ccs_technology.ccs_storage_tonne), name='CCS storage', marker_color=ccs_storage_color,legendgroup='CCS storage'),row=1,col=3)
fig.add_trace(go.Bar(x=x1, y=list(ccs_technology.ccs_capture_tonne), name='CCS capture', marker_color=ccs_capture_color,legendgroup='CCS storage'),row=1,col=3)
'''

fig.update_yaxes(range=[-3000,3000],dtick=500,ticks="inside",tickformat=',d',row=1,col=3)


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

fig.update_layout(barmode="relative", font = dict(size=8),
                  width=1600, height=400, 
                  plot_bgcolor='white',legend_traceorder="reversed",#showlegend=False)
                  legend=dict(font=dict(size= 12),yanchor="top",y=1,xanchor="left", x=1.00), margin=dict(l=10,r=10,b=10,t=10),
                  )

fig.update_yaxes(showgrid=True,linecolor='black')
fig.update_xaxes(showgrid=True,linecolor='black')
                 
fig['layout']['yaxis1'].update(title_text="Capacity (GW)",
                               title_font=dict(size=16)
                               )

fig['layout']['yaxis2'].update(title_text="Generation (TWh)", 
                              title_font = dict(size=16)            
                              )

fig['layout']['yaxis3'].update(title_text="H2 (TWh)", 
                              title_font = dict(size=16)            
                            )

'''
fig['layout']['yaxis3'].update(title_text="CO2 (tonne)", 
                              title_font = dict(size=16)            
                            )
'''     
fig.show()
fig.write_image( 'H:/Hydrogen/test/'+test_id+'.jpeg')
