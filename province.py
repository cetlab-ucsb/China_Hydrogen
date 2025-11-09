# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:09:44 2024

@author: haozheyang
"""

import geopandas
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.ticker import PercentFormatter
import numpy as np
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

#%%
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
    
test_id=['REF_1period_24day',
         'Hydrogen_REF_1period_24day',
         '550ppm_1period_24day',
         'Hydrogen_550ppm_1period_24day',
         '400ppm_1period_24day',
         'Hydrogen_400ppm_1period_24day',
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
    capacity_province_tmp=capacity_tmp.groupby(['load_zone','technology'])['capacity_mw'].sum().reset_index()
    
    West= capacity_province_tmp.loc[capacity_province_tmp.load_zone=='West_Inner_Mongolia',:]
    East= capacity_province_tmp.loc[capacity_province_tmp.load_zone=='East_Inner_Mongolia',:]
    Inner_Mongolia=pd.merge(West,East, on=['technology'], how='outer').fillna(0)
    
    Inner_Mongolia_capacity=pd.DataFrame({
        'load_zone': 'Inner Mongolia',
        'technology': Inner_Mongolia.technology,
        'capacity_mw':Inner_Mongolia.capacity_mw_x + Inner_Mongolia.capacity_mw_y
        })
    
    capacity_province_tmp=capacity_province_tmp.append(Inner_Mongolia_capacity,ignore_index=True)
    capacity_province_tmp=capacity_province_tmp.drop(capacity_province_tmp[capacity_province_tmp['load_zone'].isin(['East_Inner_Mongolia','West_Inner_Mongolia'])].index,axis=0)
    capacity_province_tmp['scenario']=case
    capacity_province=capacity_province.append(capacity_province_tmp)
    
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
capacity_REF=capacity_province.loc[capacity_province.scenario=='REF_1period_24day',:]
China_REF=capacity_REF.pivot(index='load_zone',columns=['technology'],values='capacity_mw').reset_index()
China_REF=China_REF.fillna(0)
China_REF['total_wind']=China_REF.Wind+China_REF.Offshore_Wind

capacity_hydrogen=capacity_province.loc[capacity_province.scenario=='Hydrogen_REF_1period_24day',:]
China_hydrogen=capacity_hydrogen.pivot(index='load_zone',columns=['technology'],values='capacity_mw').reset_index()
China_hydrogen=China_hydrogen.fillna(0)
China_hydrogen['total_wind']=China_hydrogen.Wind+China_hydrogen.Offshore_Wind

China_hydrogen_delta=(China_hydrogen.loc[:,'Battery':]-China_REF.loc[:,'Battery':])/China_REF.loc[:,'Battery':]
China_hydrogen_delta['load_zone']=China_hydrogen['load_zone']
China_hydrogen_delta=China_hydrogen_delta.fillna(0)
China_hydrogen_delta=China_hydrogen_delta.replace(np.inf,2)

re_REF=China.merge(China_REF,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_hydrogen_REF=China.merge(China_hydrogen_delta,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')

#550 ppm
capacity_550=capacity_province.loc[capacity_province.scenario=='550ppm_1period_24day',:]
China_550=capacity_550.pivot(index='load_zone',columns=['technology'],values='capacity_mw').reset_index()
China_550=China_550.fillna(0)
China_550['total_wind']=China_550.Wind+China_550.Offshore_Wind

capacity_hydrogen_550=capacity_province.loc[capacity_province.scenario=='Hydrogen_550ppm_1period_24day',:]
China_hydrogen_550=capacity_hydrogen_550.pivot(index='load_zone',columns=['technology'],values='capacity_mw').reset_index()
China_hydrogen_550=China_hydrogen_550.fillna(0)
China_hydrogen_550['total_wind']=China_hydrogen_550.Wind+China_hydrogen_550.Offshore_Wind

China_hydrogen_550_delta=(China_hydrogen_550.loc[:,'Battery':]-China_550.loc[:,'Battery':])/China_550.loc[:,'Battery':]
China_hydrogen_550_delta['load_zone']=China_hydrogen_550['load_zone'].fillna(0)
China_hydrogen_550_delta=China_hydrogen_550_delta.fillna(0)
China_hydrogen_550_delta=China_hydrogen_550_delta.replace(np.inf,2)

re_550=China.merge(China_550,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_hydrogen_550=China.merge(China_hydrogen_550_delta,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')

#450
capacity_400=capacity_province.loc[capacity_province.scenario=='400ppm_1period_24day',:]
China_400=capacity_400.pivot(index='load_zone',columns=['technology'],values='capacity_mw').reset_index()
China_400=China_400.fillna(0)
China_400['total_wind']=China_400.Wind+China_400.Offshore_Wind

capacity_hydrogen_400=capacity_province.loc[capacity_province.scenario=='Hydrogen_400ppm_1period_24day',:]
China_hydrogen_400=capacity_hydrogen_400.pivot(index='load_zone',columns=['technology'],values='capacity_mw').reset_index()
China_hydrogen_400=China_hydrogen_400.fillna(0)
China_hydrogen_400['total_wind']=China_hydrogen_400.Wind+China_hydrogen_400.Offshore_Wind

China_hydrogen_400_delta=(China_hydrogen_400.loc[:,'Battery':]-China_400.loc[:,'Battery':])/China_400.loc[:,'Battery':]
China_hydrogen_400_delta['load_zone']=China_hydrogen_400['load_zone']
China_hydrogen_400_delta=China_hydrogen_400_delta.fillna(0)
China_hydrogen_400_delta=China_hydrogen_400_delta.replace(np.inf,2)

re_400=China.merge(China_400,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
re_hydrogen_400=China.merge(China_hydrogen_400_delta,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='outer')
#%%
bins1=[0,100,200,300,400,500,600,700,800]
bins2=[-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1]

bounds = np.linspace(-1, 1, 9)
norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')

divergent='bwr_r'

norm = colors.TwoSlopeNorm(vcenter=0,vmin=-1,vmax=1)

fig1, ((ax1, ax2,ax3),(ax4,ax5,ax6))=plt.subplots(nrows=2, ncols=3, sharey=True, sharex=True)

plt.subplots_adjust(
                    wspace=0.2, 
                    hspace=0.5
                    )

re_REF.plot(ax=ax1, column='Solar',cmap='YlOrRd', 
               scheme='UserDefined', 
               classification_kwds={'bins': bins1},
               edgecolor='grey',
               linewidth=0.25)

re_550.plot(ax=ax2, column='Solar',cmap='YlOrRd',
                    scheme='UserDefined', 
               classification_kwds={'bins': bins1})

re_400.plot(ax=ax3, column='Solar',cmap='YlOrRd',
                   scheme='UserDefined', 
                   classification_kwds={'bins': bins1},
                   edgecolor='grey',
                   linewidth=0.25)

re_hydrogen_REF.plot(ax=ax4, column='Solar',cmap=divergent,
                    #norm=colors.CenteredNorm(),
                    norm=norm,
                    edgecolor='grey',
                    linewidth=0.25,
                    #scheme='UserDefined', 
                    #classification_kwds={'bins': bins2}
                    )

re_hydrogen_550.plot(ax=ax5, column='Solar',cmap=divergent,
                    #norm=colors.CenteredNorm(),
                    norm=norm,
                    edgecolor='grey',
                    linewidth=0.25,
                    #scheme='UserDefined', 
                    #classification_kwds={'bins': bins2}
                    )

re_hydrogen_400.plot(ax=ax6, column='Solar',cmap=divergent,
                    #norm=colors.CenteredNorm(),
                    norm=norm,
                    edgecolor='grey',
                    linewidth=0.25,
                    #scheme='UserDefined', 
                    #classification_kwds={'bins': bins2}
                    )


cb_ax1 = fig1.add_axes([0.15, 0.5, 0.75, 0.02])

patch_col1 = ax1.collections[0]

cb1 = fig1.colorbar(patch_col1, cax=cb_ax1, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)

cb1.ax.set_title('Capacity', size=12)
cb1.ax.set_ylabel('GW', size=12)
ticks_loc = cb1.ax.get_yticks().tolist()
cb1.ax.set_xticks([0,1,2,3,4,5,6,7,8])
cb1.ax.set_xticklabels(bins1)
#cb.set_label('Capacity_GW', labelpad=0, y=1.05, rotation=0)

cb_ax2 = fig1.add_axes([0.15, 0, 0.75, 0.02])

patch_col2 = ax4.collections[0]

cb2 = fig1.colorbar(patch_col2, cax=cb_ax2, shrink=0.5, orientation='horizontal', extend='both', extendrect=True)

cb2.ax.set_title('Capacity', size=12)
cb2.ax.set_xlabel('GW', size=12)
cb2.ax.locator_params(nbins=9)
ticks_loc = cb2.ax.get_yticks().tolist()
#cb2.ax.set_yticks(ticks_loc)
cb2.ax.set_xticklabels(bins2)
cb2.ax.xaxis.set_major_formatter(PercentFormatter(1, 0))
#%%
fig2, ((ax1, ax2,ax3),(ax4,ax5,ax6))=plt.subplots(nrows=2, ncols=3, sharey=True, sharex=True)

plt.subplots_adjust(
                    wspace=0.2, 
                    hspace=0.5
                    )

re_REF.plot(ax=ax1, column='Wind',cmap='YlOrRd', 
               scheme='UserDefined', 
               classification_kwds={'bins': bins1},
               edgecolor='grey',
               linewidth=0.25)

re_550.plot(ax=ax2, column='Wind',cmap='YlOrRd',
                    scheme='UserDefined', 
                    classification_kwds={'bins': bins1},
                    edgecolor='grey',
                    linewidth=0.25
                    )

re_400.plot(ax=ax3, column='Wind',cmap='YlOrRd',
               scheme='UserDefined', 
               classification_kwds={'bins': bins1},
               edgecolor='grey',
               linewidth=0.25)

re_hydrogen_REF.plot(ax=ax4, column='total_wind',cmap=divergent,
                    #norm=colors.CenteredNorm(),
                    norm=norm,
                    #scheme='UserDefined', 
                    #classification_kwds={'bins': bins2},
                    edgecolor='grey',
                    linewidth=0.25
                    )

re_hydrogen_550.plot(ax=ax5, column='total_wind',cmap=divergent,
                    #norm=colors.CenteredNorm(),
                    norm=norm,
                    edgecolor='grey',
                    linewidth=0.25,
                    #scheme='UserDefined', 
                    #classification_kwds={'bins': bins2}
                    )

re_hydrogen_400.plot(ax=ax6, column='total_wind',cmap=divergent,
                    #norm=colors.CenteredNorm(),
                    norm=norm,
                    edgecolor='grey',
                    linewidth=0.25,
                    #scheme='UserDefined', 
                    #classification_kwds={'bins': bins2}
                    )


cb_ax1 = fig2.add_axes([0.15, 0.5, 0.75, 0.02])

patch_col1 = ax1.collections[0]

cb1 = fig2.colorbar(patch_col1, cax=cb_ax1, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)

cb1.ax.set_title('Capacity', size=12)
cb1.ax.set_xlabel('GW', size=12)
ticks_loc = cb1.ax.get_yticks().tolist()
cb1.ax.set_xticks([0,1,2,3,4,5,6,7,8])
cb1.ax.set_xticklabels(bins1)
#cb.set_label('Capacity_GW', labelpad=0, y=1.05, rotation=0)

cb_ax2 = fig2.add_axes([0.15, 0, 0.75, 0.02])

patch_col2 = ax4.collections[0]

cb2 = fig1.colorbar(patch_col2, cax=cb_ax2, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)

cb2.ax.set_title('Capacity', size=12)
cb2.ax.set_ylabel('GW', size=12)

cb2.ax.locator_params(nbins=9)
#ticks_loc = cb2.ax.get_yticks().tolist()
#cb2.ax.set_yticks(ticks_loc)
cb2.ax.set_xticklabels(bins2)
