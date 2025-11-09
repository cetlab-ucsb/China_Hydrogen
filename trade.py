# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 17:00:04 2024

@author: haozheyang
"""


#cost of adding H2
import geopandas

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter
import matplotlib.ticker as ticker
import matplotlib.colors as colors
from matplotlib import gridspec
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


    
test_id=['REF_1period_36day',
         'Hydrogen_REF_1period_36day',
         '550ppm_1period_36day','Hydrogen_550ppm_1period_36day',
         '400ppm_1period_36day','Hydrogen_400ppm_1period_36day']

import_zone=pd.DataFrame()
import_total=pd.DataFrame()
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
    
    load_balance_tmp=pd.read_csv(load_balance_path)
    load_balance_tmp.load_mw=load_balance_tmp.load_mw*load_balance_tmp.timepoint_weight/10**6
    load_balance_tmp=load_balance_tmp.rename(columns={"zone": "load_zone"})
    
    
    import_tmp=pd.read_csv(import_path)
    import_tmp.net_imports_mw=import_tmp.net_imports_mw*import_tmp.timepoint_weight/10**6
    
    import_H2_tmp=pd.read_csv(import_H2_path)
    import_H2_tmp.net_imports_H2_mw=import_H2_tmp.net_imports_H2_mw*import_H2_tmp.timepoint_weight/10**6
    
    import_zone_tmp = import_tmp.groupby(['load_zone'])['net_imports_mw'].sum().reset_index()
    import_H2_zone_tmp = import_H2_tmp.groupby(['load_zone'])['net_imports_H2_mw'].sum().reset_index()
    
    import_zone_tmp=import_zone_tmp.merge(import_H2_zone_tmp)
    import_zone_tmp['total_import_mw']=import_zone_tmp.net_imports_mw + import_zone_tmp.net_imports_H2_mw
    
    import_zone_tmp['scenario']=case
    
    import_total_tmp=import_zone_tmp.loc[import_zone_tmp.net_imports_mw>0,'net_imports_mw'].sum()
    import_H2_total_tmp=import_H2_zone_tmp.loc[import_H2_zone_tmp.net_imports_H2_mw>0,'net_imports_H2_mw'].sum()
    
    import_total=import_total.append(
        pd.DataFrame(
        {
        'total_import': [import_total_tmp],
        'total_H2_import': import_H2_total_tmp,
        'scenario': case
        }
        )
        )
    

    import_zone=import_zone.append(import_zone_tmp[['load_zone','net_imports_mw','net_imports_H2_mw','total_import_mw','scenario']])
    '''
    
    
    generation_tmp=pd.read_csv(dispatch_path)
    generation_tmp.power_mw=generation_tmp.power_mw*generation_tmp.timepoint_weight/10**6
    
    generation_wo_g2p_tmp=generation_tmp.loc[~generation_tmp.technology.isin(['Electrolyzer','Fuel_cell','H2_turbine']),:]
    generation_wt_g2p_tmp=generation_tmp.loc[generation_tmp.technology.isin(['Electrolyzer','Fuel_cell','H2_turbine']),:]
    
    load_zone_tmp   = load_balance_tmp.groupby(['load_zone'])['load_mw'].sum().reset_index()
    import_zone_tmp = import_tmp.groupby(['load_zone'])['net_imports_mw'].sum().reset_index()
    import_H2_zone_tmp = import_H2_tmp.groupby(['load_zone'])['net_imports_mw'].sum().reset_index()
    generation_wo_g2p_zone_tmp=generation_wo_g2p_tmp.groupby(['load_zone'])['power_mw'].sum().reset_index()
    generation_wt_g2p_zone_tmp=generation_wt_g2p_tmp.groupby(['load_zone'])['power_mw'].sum().reset_index()

    demand_tmp=pd.merge(load_zone_tmp, generation_wt_g2p_zone_tmp)
    supply_tmp=pd.merge(import_zone_tmp, generation_wo_g2p_zone_tmp)
    
    supply_tmp['local_mw']=supply_tmp['net_imports_mw']+supply_tmp['power_mw']
    '''

West= import_zone.loc[import_zone.load_zone=='West_Inner_Mongolia',:]
East= import_zone.loc[import_zone.load_zone=='East_Inner_Mongolia',:]

Inner_Mongolia=pd.DataFrame({
    'load_zone': 'Inner Mongolia',
    'net_imports_mw':West.net_imports_mw.values + East.net_imports_mw.values,
    'net_imports_H2_mw':West.net_imports_H2_mw.values + East.net_imports_H2_mw.values,
    'total_import_mw':West.total_import_mw.values + East.total_import_mw.values,
    'scenario' : West.scenario
    }
    )


import_zone=import_zone.append(Inner_Mongolia,ignore_index=True)
    
import_total_400=import_total.loc[import_total.scenario.isin(['400ppm_1period_36day','Hydrogen_400ppm_1period_36day']),:]
#import_total_400=import_total_400.set_index('scenario')

import_zone_REF=import_zone.loc[import_zone.scenario.isin(['REF_1period_24day','Hydrogen_REF_1period_24day']),:]
import_zone_REF=import_zone_REF.pivot(index='load_zone', columns='scenario',values='total_import_mw')

import_zone_400=import_zone.loc[import_zone.scenario.isin(['400ppm_1period_36day']),:]
import_zone_hydrogen_400=import_zone.loc[import_zone.scenario.isin(['Hydrogen_400ppm_1period_36day']),:]

re_400=China.merge(import_zone_400,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='inner') 
re_hydrogen_400=China.merge(import_zone_hydrogen_400,left_on=['PINYIN_NAM'],right_on=['load_zone'],how='inner')    


    
#%%

fig = plt.figure() 

fig.set_figheight(5)
fig.set_figwidth(11)

'''
gs = gridspec.GridSpec(2, 4) 
ax1 = plt.subplot(gs[:,0])
ax2 = plt.subplot(gs[0,1])
ax3 = plt.subplot(gs[0,2])
ax4 = plt.subplot(gs[0,3])
ax6 = plt.subplot(gs[1,1])
ax7 = plt.subplot(gs[1,2])
ax8 = plt.subplot(gs[1,3])
'''

ax1 = plt.subplot2grid(shape=(2, 3), loc=(0, 0), rowspan=2)
ax2 = plt.subplot2grid(shape=(2, 3), loc=(0, 1), colspan=1)
ax3 = plt.subplot2grid(shape=(2, 3), loc=(0, 2), colspan=1)
#ax4 = plt.subplot2grid(shape=(2, 4), loc=(0, 3), colspan=1)
ax6 = plt.subplot2grid(shape=(2, 3), loc=(1, 1), colspan=1)
ax7 = plt.subplot2grid(shape=(2, 3), loc=(1, 2), colspan=1)
#ax8 = plt.subplot2grid(shape=(2, 4), loc=(1, 3), colspan=1)

plt.subplots_adjust(hspace=0.2,
                    wspace=0.1)

import_total_400.plot.bar(ax=ax1,
                         #stacked=True,
                         legend=False,
                         color=['#b5179e','#f72585'])


ax1.legend(['electricity','hydrogen'],
           loc='lower center', 
           bbox_to_anchor=(0.5, -0.3),
           frameon=False,
           fontsize=12
           )


ax1.set_ylabel('TWh')
ax1.set_xlabel('')
ax1.set_xticklabels(['ZE','ZE + $H_{2}$'],rotation=0)
#ax5.yaxis.set_major_locator(ticker.MultipleLocator(2000))  



bins1=[0,100,200,300,400,500,600,700,800]
bins2=[-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1]

bounds = np.linspace(-1, 1, 9)
norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256, extend='both')

divergent='bwr_r'

norm = colors.TwoSlopeNorm(vcenter=0,vmin=-500,vmax=500)



re_400.plot(ax=ax2, column='net_imports_mw',
            cmap=divergent, 
             #scheme='UserDefined', 
               #classification_kwds={'bins': bins1},
               norm=norm,
               edgecolor='grey',
               linewidth=0.25)

ax2.set_xticklabels('')

re_400.plot(ax=ax3, column='net_imports_H2_mw', cmap=divergent, 
             #scheme='UserDefined', 
               #classification_kwds={'bins': bins1},
               norm=norm,
               edgecolor='grey',
               linewidth=0.25
               )

ax3.set_xticklabels('')
ax3.set_yticklabels('')

'''
re_400.plot(ax=ax4, column='total_import_mw',
            cmap=divergent, 
            #scheme='UserDefined', 
            #classification_kwds={'bins': bins1},
            norm=norm,
            edgecolor='grey',
            linewidth=0.25
                   )

ax4.set_yticklabels('')
ax4.set_xticklabels('')
'''
re_hydrogen_400.plot(ax=ax6, column='net_imports_mw',
            cmap=divergent, 
             #scheme='UserDefined', 
               #classification_kwds={'bins': bins1},
               norm=norm,
               edgecolor='grey',
               linewidth=0.25)

re_hydrogen_400.plot(ax=ax7, column='net_imports_H2_mw', cmap=divergent, 
             #scheme='UserDefined', 
               #classification_kwds={'bins': bins1},
               norm=norm,
               edgecolor='grey',
               linewidth=0.25
               )

ax7.set_yticklabels('')

'''
re_hydrogen_400.plot(ax=ax8, column='total_import_mw',
            cmap=divergent, 
            #scheme='UserDefined', 
            #classification_kwds={'bins': bins1},
            norm=norm,
            edgecolor='grey',
            linewidth=0.25
                   )

ax8.set_yticklabels('')
'''
cb_ax1 = fig.add_axes([0.42, -0.05, 0.45, 0.02])

patch_col1 = ax2.collections[0]

cb1 = fig.colorbar(patch_col1, cax=cb_ax1, shrink=0.5,orientation='horizontal', extend='both', extendrect=True)

cb1.ax.set_title('Annual net import (TWh)', size=12)
#cb1.ax.set_ylabel('TWh', size=12)
ticks_loc = cb1.ax.get_yticks().tolist()
#cb1.ax.set_xticks([0,1,2,3,4,5,6,7,8])
#cb1.ax.set_xticklabels(bins1)
#cb.set_label('Capacity_GW', labelpad=0, y=1.05, rotation=0)



fig.text(0.05,0.9,'a', fontweight="bold")
fig.text(0.38,0.9,'b', fontweight="bold")
fig.text(0.65,0.9,'c', fontweight="bold")
#fig.text(0.71,0.9,'d', fontweight="bold")
fig.text(0.38,0.47,'e', fontweight="bold")
fig.text(0.65,0.47,'f', fontweight="bold")
#fig.text(0.71,0.47,'g', fontweight="bold")

font = {'family' : 'Arial',
        'weight': 'normal',
        'size'   : 12}

plt.rc('font', **font)

fig.savefig('H:/Hydrogen/Figure/' + 'Fig2' + '.png', dpi=300, bbox_inches='tight')

'''
fig, (ax1, ax2)=plt.subplots(nrows=2, ncols=1, sharex=True, sharey=True)

import_zone_REF.plot.scatter(y='REF_1period_24day', x='Hydrogen_REF_1period_24day',
                             ax=ax1,
                             c='none',
                             edgecolor='red',
                             lw=0.5
                             )
    
ax1.plot(np.arange(-1500,1501,1),np.arange(-1500,1501,1),
         color='black',
         linewidth=0.5)

ax1.axhline(y=0,color='black',linewidth=0.5)
ax1.axvline(x=0,color='black',linewidth=0.5)

import_zone_400.plot.scatter(y='400ppm_1period_24day', x='Hydrogen_400ppm_1period_24day',
                             ax=ax2,
                             marker='o',
                             c='none',
                             edgecolor='red',
                             lw=0.5)    

ax2.plot(np.arange(-1000,1001,1),np.arange(-1000,1001,1),
         color='black',
         linewidth=0.5)

ax2.axhline(y=0,color='black',linewidth=0.5)
ax2.axvline(x=0,color='black',linewidth=0.5)

ax1.set_ylim([-1000,1000])
ax1.set_xlim([-1000,1000])

ax1.yaxis.set_major_locator(ticker.MultipleLocator(2000))
ax1.xaxis.set_major_locator(ticker.MultipleLocator(2000))
ax1.yaxis.set_minor_locator(ticker.MultipleLocator(1000))
ax1.xaxis.set_minor_locator(ticker.MultipleLocator(1000))

ax1.set_aspect('equal', adjustable='box')
ax2.set_aspect('equal', adjustable='box')
'''