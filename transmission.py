# -*- coding: utf-8 -*-
"""
Created on Fri May 24 14:09:54 2024

@author: haozheyang
"""

import geopandas
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import PercentFormatter
import numpy as np
import math
import cartopy.crs as ccrs
#%%
China = geopandas.read_file('H:/Hydrogen/Figure/2020_map/province.shp')
China.loc[China.PINYIN_NAM=='Xinjiang Wei', 'PINYIN_NAM']='Xinjiang'
China.loc[China.PINYIN_NAM=='Ningxia Hui', 'PINYIN_NAM']='Ningxia'
China.loc[China.PINYIN_NAM=='Xizang', 'PINYIN_NAM']='Tibet'
China.loc[China.PINYIN_NAM=='Guangxi Zhuang', 'PINYIN_NAM']='Guangxi'
China.loc[China.PINYIN_NAM=='Neimenggu', 'PINYIN_NAM']='Inner Mongolia'
China.loc[China.PINYIN_NAM=='chongqingshi', 'PINYIN_NAM']='Chongqing'
China.loc[China.PINYIN_NAM=='gansu', 'PINYIN_NAM']='Gansu'

China = China.to_crs(4326)

center=pd.read_excel('H:/Hydrogen/Figure/2020_map/capital_center.xlsx')
#%%
all_project=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/raw_data/all_projects.csv')
all_project=all_project.replace('.','0')
all_project['zone']=all_project['gen_load_zone']
all_project['gen_capacity_limit_mw']=all_project['gen_capacity_limit_mw'].astype(float)/1000

potential=all_project.groupby(['zone','technology'])['gen_capacity_limit_mw'].sum().reset_index()
potential.loc[potential.zone=='West_Inner_Mongolia','zone']='Inner Mongolia'
potential.loc[potential.zone=='East_Inner_Mongolia','zone']='Inner Mongolia'

potential.loc[potential.technology=='Commercial_PV','technology']='PV'
potential.loc[potential.technology=='Residential_PV','technology']='PV'
potential.loc[potential.technology=='Central_PV','technology']='PV'
potential=potential.loc[potential.technology.isin(['Wind','Offshore_Wind','PV']),:]
potential.loc[potential.technology.isin(['Offshore_wind','Wind']),'gen_capacity_limit_mw']=potential.loc[potential.technology.isin(['Offshore_wind','Wind']),'gen_capacity_limit_mw']*2.6
potential=potential.groupby(['zone','technology'])['gen_capacity_limit_mw'].sum().reset_index()
potential=potential.pivot(index='zone',columns='technology',values='gen_capacity_limit_mw')


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
file15='load_balance.csv'
file16='H2_balance.csv'
    
test_id=[
         'Hydrogen_400ppm_1period_36day',
          #'Hydrogen_400ppm_1period_36day_safe'
         ]

capacity_province=pd.DataFrame()
generation_province=pd.DataFrame()

for case in test_id:
    path='H:/Hydrogen/Data/'+case+'/results/'
    dispatch_path=path+file1
    capacity_path=path+file6
    carbon_path=path+file2
    capacity_cost_path=path+file3
    operation_cost_path=path+file4
    transmission_cost_path=path+file5
    transmission_new_capacity_path=path+file7
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
    capacity_tmp.capacity_mw=capacity_tmp.capacity_mw/10**3
    capacity_tmp.capacity_mwh=capacity_tmp.capacity_mwh/10**6
    capacity_province_tmp=capacity_tmp.groupby(['load_zone','technology'])['capacity_mwh','capacity_mw'].sum().reset_index()
    
    West= capacity_province_tmp.loc[capacity_province_tmp.load_zone=='West_Inner_Mongolia',:]
    East= capacity_province_tmp.loc[capacity_province_tmp.load_zone=='East_Inner_Mongolia',:]
    Inner_Mongolia=pd.merge(West,East, on=['technology'], how='outer').fillna(0)
    
    Inner_Mongolia_capacity=pd.DataFrame({
        'load_zone': 'Inner Mongolia',
        'technology': Inner_Mongolia.technology,
        'capacity_mwh':Inner_Mongolia.capacity_mwh_x + Inner_Mongolia.capacity_mwh_y,
        'capacity_mw': Inner_Mongolia.capacity_mw_x + Inner_Mongolia.capacity_mw_y
        })
    
    capacity_province_tmp=capacity_province_tmp.append(Inner_Mongolia_capacity,ignore_index=True)
    capacity_province_tmp=capacity_province_tmp.drop(capacity_province_tmp[capacity_province_tmp['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
    capacity_province_tmp['scenario']=case
    capacity_province=capacity_province.append(capacity_province_tmp)
    
    transmission_new_capacity=pd.read_csv(transmission_new_capacity_path)  
    transmission_H2=transmission_new_capacity.loc[transmission_new_capacity.transmission_line.str.contains('H2'),:]
    transmission_H2.loc[transmission_H2.load_zone_from=='East_Inner_Mongolia','load_zone_from']='Inner Mongolia'
    transmission_H2.loc[transmission_H2.load_zone_from=='West_Inner_Mongolia','load_zone_from']='Inner Mongolia'
    transmission_H2.loc[transmission_H2.load_zone_to=='East_Inner_Mongolia','load_zone_to']='Inner Mongolia'
    transmission_H2.loc[transmission_H2.load_zone_to=='West_Inner_Mongolia','load_zone_to']='Inner Mongolia'
    transmission_H2=transmission_H2.groupby(['load_zone_from','load_zone_to'])['new_build_transmission_capacity_mw'].sum().reset_index()
    
    transmission=transmission_new_capacity.loc[~transmission_new_capacity.transmission_line.str.contains('H2'),:]
    transmission.loc[transmission.load_zone_from=='East_Inner_Mongolia','load_zone_from']='Inner Mongolia'
    transmission.loc[transmission.load_zone_from=='West_Inner_Mongolia','load_zone_from']='Inner Mongolia'
    transmission.loc[transmission.load_zone_to=='East_Inner_Mongolia','load_zone_to']='Inner Mongolia'
    transmission.loc[transmission.load_zone_to=='West_Inner_Mongolia','load_zone_to']='Inner Mongolia'
    transmission=transmission.groupby(['load_zone_from','load_zone_to'])['new_build_transmission_capacity_mw'].sum().reset_index()
    '''
    generation_tmp=pd.read_csv(dispatch_path)
    generation_tmp.power_mw=generation_tmp.power_mw*generation_tmp.timepoint_weight/10**6
    generation_province_tmp=generation_tmp.groupby(['load_zone','technology'])['power_mw'].sum().reset_index()
    
    Inner_Mongolia_generation=pd.DataFrame({
        'load_zone': 'Inner Mongolia',
        'technology': generation_province_tmp.loc[generation_province_tmp.load_zone=='East_Inner_Mongolia','technology'].values,
        'power_mw':generation_province_tmp.loc[generation_province_tmp.load_zone=='East_Inner_Mongolia','power_mw'].values+generation_province_tmp.loc[generation_province_tmp.load_zone=='West_Inner_Mongolia','power_mw'].values,
        })
    
    generation_province_tmp=generation_province_tmp.append(Inner_Mongolia_generation,ignore_index=True)
    generation_province_tmp=generation_province_tmp.drop(generation_province_tmp[generation_province_tmp['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
    generation_province=generation_province.append(generation_province_tmp)
    '''
    
#%%
transmission_H2=transmission_H2.merge(center,left_on='load_zone_from',right_on='load_zone', how='left')
transmission_H2=transmission_H2.merge(center,left_on='load_zone_to',right_on='load_zone', how='left')

transmission_H2=transmission_H2.rename(columns={'lon_x':'lon_from',
                                                'lat_x':'lat_from',
                                                'lon_y':'lon_to',
                                                'lat_y':'lat_to'})

transmission_H2=transmission_H2.drop(transmission_H2[transmission.new_build_transmission_capacity_mw==0].index)

transmission=transmission.merge(center,left_on='load_zone_from',right_on='load_zone', how='left')
transmission=transmission.merge(center,left_on='load_zone_to',right_on='load_zone', how='left')

transmission=transmission.rename(columns={'lon_x':'lon_from',
                                                'lat_x':'lat_from',
                                                'lon_y':'lon_to',
                                                'lat_y':'lat_to'})

transmission=transmission.drop(transmission[transmission.new_build_transmission_capacity_mw==0].index)

#450
capacity_hydrogen_400=capacity_province.loc[capacity_province.scenario=='Hydrogen_400ppm_1period_36day',:]
China_hydrogen_400=capacity_hydrogen_400.pivot(index='load_zone',columns=['technology'],values='capacity_mwh').reset_index()
China_hydrogen_400_mw=capacity_hydrogen_400[['load_zone','technology','capacity_mw']].pivot(index='load_zone',columns=['technology'],values='capacity_mw').reset_index()
China_hydrogen_400_mw['Total_Wind']=China_hydrogen_400_mw.Wind.fillna(0) + China_hydrogen_400_mw.Offshore_Wind.fillna(0)
#China_hydrogen_400=China_hydrogen_400.fillna(0)

re_400=China.merge(China_hydrogen_400,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_400_mw=China.merge(China_hydrogen_400_mw,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')

re_potential=China.merge(potential,left_on=['PINYIN_NAM'],right_on=['zone'],how='outer')
#%%
bins1=[0,250,500,750,1000]
bins2=[0,50,100,150,200]
bins3=[-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1]

bounds = np.linspace(-1, 1, 9)
norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')

divergent='bwr_r'

norm = colors.TwoSlopeNorm(vcenter=0,vmin=-1,vmax=1)

fig, ((ax1,ax2),(ax3,ax4))=plt.subplots(ncols=2,nrows=2, sharex=True, sharey=True)

plt.subplots_adjust(
                    wspace=-0.1, 
                    hspace=0.5
                    )

re_400_mw.plot(ax=ax1, column='Solar',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

re_400_mw.plot(ax=ax2, column='Total_Wind',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey",aspect='equal')
                   )

re_400_mw.plot(ax=ax3, column='Battery',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

xx = np.vstack([transmission.lon_from,transmission.lon_to])
yy = np.vstack([transmission.lat_from,transmission.lat_to])
capacity=transmission.new_build_transmission_capacity_mw.values
capacity[capacity<1]=1
#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    ax3.plot(xx[:,i_id],yy[:,i_id],'b',linewidth=math.log10(i)/2)


re_400.plot(ax=ax4, column='Salt_cavern',cmap='Reds',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins2},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey",aspect='equal')
                  )


xx = np.vstack([transmission_H2.lon_from,transmission_H2.lon_to])
yy = np.vstack([transmission_H2.lat_from,transmission_H2.lat_to])
capacity=transmission_H2.new_build_transmission_capacity_mw.values
capacity[capacity<1]=1
#colors_line = plt.cm.jet(np.linspace(0,1,71))
for i_id, i in enumerate(capacity):
    ax4.plot(xx[:,i_id],yy[:,i_id],'b',linewidth=math.log10(i)/2)

line1, = plt.plot([], label="100", linewidth=2/2, linestyle='-',color='b')
line2, = plt.plot([], label="1,000", linewidth=3/2, linestyle='-',color='b')
line3, = plt.plot([], label="10,000", linewidth=4/2, linestyle='-',color='b')


# Create another legend for the second line.
fig.legend(handles=[line1, line2,line3],  bbox_to_anchor=(1.18, 0.6),
          frameon=False,
          title='Transmission and\n pipeline capacity (MW)')._legend_box.align = "left"


fig.supxlabel('Longitude')
fig.supylabel('Latitude')

ax1.title.set_text('Solar')
ax2.title.set_text('Wind')
ax3.title.set_text('Battery \n+ Transmission')
ax4.title.set_text('Underground storage \n+ Hydrogen pipeline')

cb_ax = fig.add_axes([0.15, -0.3, 0.75, 0.02])
patch_col = ax4.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
cb.ax.set_xticks([0,1,2,3,4])
cb.ax.set_xticklabels(bins2)
cb.ax.set_title('Energy capacity (TWh)', size=12)

cb_ax = fig.add_axes([0.15, -0.1, 0.75, 0.02])
patch_col = ax1.collections[0]
cb = fig.colorbar(patch_col, cax=cb_ax, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc = cb.ax.get_xticks().tolist()
cb.ax.set_xticks([0,1,2,3,4])
cb.ax.set_xticklabels(bins1)
cb.ax.set_title('Power capacity (GW)', size=12)
#%%
bins1=[0,10,20,30,40]
bins2=[-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1]

bounds = np.linspace(-1, 1, 9)
norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')

divergent='bwr_r'

norm = colors.TwoSlopeNorm(vcenter=0,vmin=-1,vmax=1)

fig2, ax2=plt.subplots()

plt.subplots_adjust(
                    wspace=0.1, 
                    hspace=0.5
                    )


re_400_mw.plot(ax=ax2, column='Fuel_cell',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

ax2.set_xlabel('Longitude')
ax2.set_ylabel('Latitude')

cb_ax2 = fig2.add_axes([0.15, -0.08, 0.75, 0.02])
patch_col = ax2.collections[0]
cb2 = fig2.colorbar(patch_col, cax=cb_ax2, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)
ticks_loc2 = cb2.ax.get_xticks().tolist()
cb2.ax.set_xticks([0,1,2,3,4])
cb2.ax.set_xticklabels(bins1)
cb2.ax.set_title('Capacity (GW)', size=12)
#%%
bins1=[0,250,500,750,1000]
bins2=[-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1]

bounds = np.linspace(-1, 1, 9)
norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')

divergent='bwr_r'

norm = colors.TwoSlopeNorm(vcenter=0,vmin=-1,vmax=1)

fig3, (ax3,ax4,ax5)=plt.subplots(nrows=3,ncols=1,sharex=True,figsize=(6, 8))

plt.subplots_adjust(
                    wspace=0.2, 
                    hspace=0.2
                    )

re_potential = re_potential.to_crs(4326)


re_potential.plot(ax=ax3, column='PV',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

re_potential.plot(ax=ax4, column='Wind',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

re_potential.plot(ax=ax5, column='Offshore_Wind',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

ax3.title.set_text('Solar')
ax4.title.set_text('Wind')
ax5.title.set_text('Offshore wind')

ax5.set_xlabel('Longitude')
ax4.set_ylabel('Latitude')

cb_ax3 = fig3.add_axes([0.8, 0.13, 0.015, 0.75])
patch_col = ax3.collections[0]
cb3 = fig3.colorbar(patch_col, cax=cb_ax3, 
                    shrink=0.5,
                    orientation='vertical',
                    extend='both', extendrect=True)
ticks_loc3 = cb3.ax.get_yticks().tolist()
cb3.ax.set_yticks([0,1,2,3,4])
cb3.ax.set_yticklabels(bins1)
cb3.ax.set_title('Potential (GW)', size=12)
#%%
bins1=[0,250,500,750,1000]
bins2=[-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1]

bounds = np.linspace(-1, 1, 9)
norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')

divergent='bwr_r'

norm = colors.TwoSlopeNorm(vcenter=0,vmin=-1,vmax=1)

fig4, (ax6,ax7,ax8)=plt.subplots(nrows=3,ncols=1,sharex=True,figsize=(6, 8))

plt.subplots_adjust(
                    wspace=0.2, 
                    hspace=0.2
                    )


re_400_mw.plot(ax=ax6, column='Solar',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

re_400_mw.plot(ax=ax7, column='Wind',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal')
                   )

re_400_mw.plot(ax=ax8, column='Offshore_Wind',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25,
                   missing_kwds= dict(color = "lightgrey", aspect='equal'))


ax6.title.set_text('Solar')
ax7.title.set_text('Wind')
ax8.title.set_text('Offshore wind')

ax8.set_xlabel('Longitude')
ax7.set_ylabel('Latitude')

cb_ax4 = fig4.add_axes([0.8, 0.13, 0.015, 0.75])
patch_col = ax4.collections[0]
cb4 = fig4.colorbar(patch_col, cax=cb_ax4, 
                    shrink=0.5,
                    orientation='vertical',
                    extend='both', extendrect=True)
ticks_loc4 = cb4.ax.get_yticks().tolist()
cb4.ax.set_yticks([0,1,2,3,4])
cb4.ax.set_yticklabels(bins1)
cb4.ax.set_title('Installed capacity (GW)', size=12)
#%%
fig.savefig('H:/Hydrogen/Figure/' + 'FigS5' + '.png', dpi=300, bbox_inches='tight')
fig2.savefig('H:/Hydrogen/Figure/' + 'FigS6' + '.png', dpi=300, bbox_inches='tight')
fig3.savefig('H:/Hydrogen/Figure/' + 'FigS7' + '.png', dpi=300, bbox_inches='tight')
fig4.savefig('H:/Hydrogen/Figure/' + 'FigS8' + '.png', dpi=300, bbox_inches='tight')
