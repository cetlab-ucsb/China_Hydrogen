# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 18:50:35 2022

@author: haozheyang
"""
#cluster

from IPython import get_ipython
get_ipython().magic('reset -sf')

import os
os.chdir("H:/Hydrogen")

import pandas as pd
import numpy as np
#%%
all_project=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/raw_data/all_projects.csv')
fixed_cost=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/raw_data/existing_costs.csv')
new_cost=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/raw_data/new_costs.csv')
new_cost_2020=new_cost.loc[new_cost['build_year']==2020,:]

costs=pd.concat([fixed_cost,new_cost_2020])
all_project2=pd.merge(all_project,costs,on='project')
#project1=all_project['project'].sort_values()
#project2=all_project2['project'].sort_values()
#check=[]
#for i in project1:
#   if not i in project2.values:
#       check.append(i)
 
all_project2=all_project2.replace('.','0')
all_project2['zone']=all_project2['gen_load_zone']
capacity=all_project2['gen_capacity_limit_mw'].astype(float)+all_project2['gen_min_build_capacity'].astype(float)
capacity_id=np.zeros([len(capacity),1])
    
        
all_project2['capacity']=capacity
gas_combustion=(all_project2['capacity_group']=='group_gas') & (all_project2['capacity']==0) 
all_project2.loc[gas_combustion,'capacity']=600
all_project2['capacity_id']=capacity_id
all_project2['gen_capacity_limit_mw']=all_project2['gen_capacity_limit_mw'].astype(float)
all_project2['gen_min_build_mw']=all_project2['gen_min_build_capacity'].astype(float)
all_project2=all_project2.drop(all_project2[all_project2['retire_year_y']<2020].index,axis=0).reset_index().drop('index',axis=1)

for year in [2020,2025,2030,2035,2040,2045,2050]:
    period_tmp='_'.join(['period',str(year)])
    all_project2.loc[:,period_tmp]=0
    all_project2.loc[all_project2.retire_year_y>=year+5,period_tmp]=all_project2.loc[all_project2.retire_year_y>=year+5,'capacity']

  
solar=all_project2.loc[all_project2['capacity_group']=='group_pv',:].copy()
solar.technology=solar.technology.str.replace('_EP','')
solar.loc[solar.technology=='Commercial_PV','technology']='Central_PV'

solar2=solar.groupby(['zone','technology','capacity_group','gen_dbid']).agg({
    #'gen_dbid':'first',
    'variable_om_cost_per_mwh':'mean',
    'min_stable_level_fraction':'mean',
    'gen_max_age':'mean',
    'gen_variable_om':'mean',
    'gen_scheduled_outage_rate':'mean',
    'gen_forced_outage_rate':'mean',
    'capacity':'sum',
    'gen_capacity_limit_mw':'sum',
    'gen_min_build_capacity':'sum',
    'gen_overnight_cost':'sum',
    'gen_fixed_om':'mean',
    'period_2020':'sum',
    'period_2025':'sum',
    'period_2030':'sum',
    'period_2035':'sum',
    'period_2040':'sum',
    'period_2045':'sum',
    'period_2050':'sum'
   }).reset_index()

wind=all_project2.loc[all_project2['capacity_group']=='group_wind',:].copy() 
wind.technology=wind.technology.str.replace('_EP','')
 
wind2=wind.groupby(['zone','technology','capacity_group','gen_dbid']).agg({
    #'gen_dbid':'first',
    'variable_om_cost_per_mwh':'mean',
    'min_stable_level_fraction':'mean',
    'gen_max_age':'mean',
    'gen_variable_om':'mean',
    'gen_scheduled_outage_rate':'mean',
    'gen_forced_outage_rate':'mean',
    'capacity':'sum',
    'gen_capacity_limit_mw':'sum',
    'gen_min_build_capacity':'sum',
    'gen_overnight_cost':'sum',
    'gen_fixed_om':'mean',
    'period_2020':'sum',
    'period_2025':'sum',
    'period_2030':'sum',
    'period_2035':'sum',
    'period_2040':'sum',
    'period_2045':'sum',
    'period_2050':'sum'
   }).reset_index()

wind2.loc[(wind2.technology=='Wind') & (wind2.gen_dbid=='new'),'gen_capacity_limit_mw']=wind2.loc[(wind2.technology=='Wind') & (wind2.gen_dbid=='new'),'gen_capacity_limit_mw']*2.6

battery=all_project2.loc[all_project2['technology']=='Battery_Storage',:]  
battery2=battery.groupby(['zone','technology','capacity_group','gen_dbid']).agg({
    #'gen_dbid':'first',
    'variable_om_cost_per_mwh':'mean',
    'min_stable_level_fraction':'mean',
    'gen_max_age':'mean',
    'gen_variable_om':'mean',
    'gen_scheduled_outage_rate':'mean',
    'gen_forced_outage_rate':'mean',
    'capacity':'sum',
    'gen_storage_efficiency': lambda x: x.astype(float).mean(),
    'gen_capacity_limit_mw':'sum',
    'gen_min_build_capacity':'sum',
    'gen_overnight_cost':'sum',
    'gen_fixed_om':'mean'
   }).reset_index()

PHS=all_project2.loc[all_project2['technology']=='Hydro_Pumped',:].copy()
PHS.capacity_group='group_PHS'  
PHS2=PHS.groupby(['zone','technology','capacity_group','gen_dbid']).agg({
    #'gen_dbid':'first',
    'variable_om_cost_per_mwh':'mean',
    'min_stable_level_fraction':'mean',
    'gen_max_age':'mean',
    'gen_variable_om':'mean',
    'gen_scheduled_outage_rate':'mean',
    'gen_forced_outage_rate':'mean',
    'capacity':'sum',
    'gen_capacity_limit_mw':'sum',
    'gen_min_build_capacity':'sum',
    'gen_overnight_cost':'sum',
    'gen_fixed_om':'mean',
    'period_2020':'sum',
    'period_2025':'sum',
    'period_2030':'sum',
    'period_2035':'sum',
    'period_2040':'sum',
    'period_2045':'sum',
    'period_2050':'sum'
   }).reset_index()

hydro=all_project2.loc[all_project2['capacity_group']=='group_hydro',:]  
hydro2=hydro.groupby(['zone','technology','capacity_group','gen_dbid']).agg({
    #'gen_dbid':'first',
    'variable_om_cost_per_mwh':'mean',
    'min_stable_level_fraction':'mean',
    'gen_max_age':'mean',
    'gen_variable_om':'mean',
    'gen_scheduled_outage_rate':'mean',
    'gen_forced_outage_rate':'mean',
    'capacity':'sum',
    'gen_capacity_limit_mw':'sum',
    'gen_min_build_capacity':'sum',
    'gen_overnight_cost':'sum',
    'gen_fixed_om':'mean',
    'period_2020':'sum',
    'period_2025':'sum',
    'period_2030':'sum',
    'period_2035':'sum',
    'period_2040':'sum',
    'period_2045':'sum',
    'period_2050':'sum'
   }).reset_index()



nuclear=all_project2.loc[all_project2['capacity_group']=='group_nuclear',:].copy() 
nuclear['technology']='Nuclear'
nuclear2=nuclear.groupby(['zone','technology','capacity_group','gen_dbid']).agg({
    #'gen_dbid':'first',
    'variable_om_cost_per_mwh':'mean',
    'min_stable_level_fraction':'mean',
    'gen_max_age':'mean',
    'gen_variable_om':'mean',
    'gen_scheduled_outage_rate':'mean',
    'gen_forced_outage_rate':'mean',
    'gen_full_load_heat_rate':lambda x: x.astype(float).mean(),
    'capacity':'sum',
    'gen_capacity_limit_mw':'sum',
    'gen_min_build_capacity':'sum',
    'gen_overnight_cost':'sum',
    'gen_fixed_om':'mean',
    'period_2020':'sum',
    'period_2025':'sum',
    'period_2030':'sum',
    'period_2035':'sum',
    'period_2040':'sum',
    'period_2045':'sum',
    'period_2050':'sum'
   }).reset_index()



gas=all_project2.loc[all_project2['capacity_group']=='group_gas',:].copy()
gas_technology=gas.technology.str.split('_').str[0:-1]
gas_technology2=['_'.join(i) for i in gas_technology]
gas.technology=gas_technology2

gas2=gas.groupby(['zone','technology','capacity_group','gen_dbid']).agg({
    #'gen_dbid':'first',
    'variable_om_cost_per_mwh':'mean',
    'min_stable_level_fraction':'mean',
    'gen_max_age':'mean',
    'gen_variable_om':'mean',
    'gen_scheduled_outage_rate':'mean',
    'gen_forced_outage_rate': 'mean',
    'gen_04_load_heat_rate':lambda x: x.astype(float).mean(),
    'gen_full_load_heat_rate':lambda x: x.astype(float).mean(),
    'capacity':'sum',
    'gen_capacity_limit_mw':'sum',
    'gen_min_build_capacity':'sum',
    'gen_overnight_cost':'sum',
    'gen_fixed_om':'mean',
    'period_2020':'sum',
    'period_2025':'sum',
    'period_2030':'sum',
    'period_2035':'sum',
    'period_2040':'sum',
    'period_2045':'sum',
    'period_2050':'sum'
    #'retire_year_y':'mean'
   }).reset_index()

gas2.loc[:,'variable_ccs_om_cost_per_tonne']=3.54
gas2.loc[:,'ccs_mwh_per_tonne']=0.160
gas2.loc[:,'ccs_efficiency']=0.95
gas2.loc[:,'fuel']='Gas'

coal=all_project2.loc[all_project2['capacity_group']=='group_coal',:].copy()
coal_technology=coal.technology.str.split('_').str[0:2]

for i, t in zip(coal_technology.index,coal_technology):
    if t[1]=="IGCC":
        coal.loc[i,'technology']='Coal_IGCC'
    else:
        coal.loc[i,'technology']='Coal'
   
coal2=coal.groupby(['zone','technology','capacity_group','gen_dbid']).agg({
    #'gen_dbid':'first',
    'variable_om_cost_per_mwh':'mean',
    'min_stable_level_fraction':'mean',
    'gen_max_age':'mean',
    'gen_variable_om':'mean',
    'gen_scheduled_outage_rate':'mean',
    'gen_forced_outage_rate': 'mean',
    'gen_04_load_heat_rate':lambda x: x.astype(float).mean(),
    'gen_full_load_heat_rate':lambda x: x.astype(float).mean(),
    'capacity':'sum',
    'gen_capacity_limit_mw':'sum',
    'gen_min_build_capacity':'sum',
    'gen_overnight_cost':'sum',
    'gen_fixed_om':'mean',
    'period_2020':'sum',
    'period_2025':'sum',
    'period_2030':'sum',
    'period_2035':'sum',
    'period_2040':'sum',
    'period_2045':'sum',
    'period_2050':'sum'
    #'retire_year_y':'mean'
   }).reset_index()

coal2.loc[coal2.technology=='Coal_IGCC','variable_ccs_om_cost_per_tonne']=8.64
coal2.loc[coal2.technology=='Coal_IGCC','ccs_mwh_per_tonne']=0.21

coal2.loc[coal2.technology=='Coal','variable_ccs_om_cost_per_tonne']=6.26
coal2.loc[coal2.technology=='Coal','ccs_mwh_per_tonne']=0.145

coal2.loc[:,'ccs_efficiency']=0.95

coal2.loc[:,'fuel']=['Coal'+'_'+i for i in coal2.zone]

cluster=pd.concat([battery2,PHS2,solar2,wind2,hydro2,nuclear2,gas2,coal2])
name=cluster['zone']+'_'+cluster['technology']+'_'+cluster['gen_dbid']+'_'+[str(i) for i in cluster.index]
cluster.insert(0,'project',name)
cluster=cluster.reset_index().drop('index',axis=1)

path_to_zone='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/system_load/load_zones'
load_zone=pd.read_csv(path_to_zone+'/1_china.csv')['load_zone']

hydrogen_project=pd.DataFrame()
for i in load_zone:
    g2p_project_tmp=pd.DataFrame(
        {'project': [i+'_Hydrogen_fuel_cell',i+'_'+'Hydrogen_turbine'],
         'zone':i,	
         'technology':["Fuel_cell","Hydrogen_turbine"],
         'capacity_group': 'group_g2p',
         'gen_dbid': ["new","new"],
         }
        )
    
    p2g_project_tmp=pd.DataFrame(
        {'project': [i+'_'+'Electrolyzer', i+'_'+'SMR', i+'_'+'Gasification'],
         'zone':i,	
         'technology':["Electrolyzer","SMR","Gasification"],
         'capacity_group': ['group_p2g','group_H2','group_H2'],
         'gen_full_load_heat_rate':["",4.8, 5.3],
         'variable_om_cost_per_mwh':["",0.8,1.3],
         'variable_ccs_om_cost_per_tonne':["",0.033,0.033],
         'ccs_mwh_per_tonne':["",0.61,0.61],
         'ccs_efficiency':[0.95,0.95,0.95],
         'gen_dbid': ["new","new",'new'],
         'fuel': ['','Gas','Coal_'+i]
         }
        )
    
    storage_project_tmp=pd.DataFrame(
        {'project': [ i+'_'+'Hydrogen_tank_storage'],
         'zone':i,	
         'technology':["Tank"],
         'capacity_group': ['group_tank'],
         'gen_dbid': "new"
         }
        )
    
    hydrogen_project_tmp=pd.concat([g2p_project_tmp,p2g_project_tmp,storage_project_tmp])
    hydrogen_project=hydrogen_project.append(hydrogen_project_tmp)

#source:
#Site selection evaluation for salt cavern hydrogen storage in China    

hydrogen_storage_project=pd.DataFrame()
salt_zone=['Anhui','Hebei','Henan','Shandong','Hubei','Hunan','Sichuan','Jiangsu',
           'Jiangxi','Guangdong','Yunnan','Chongqing','Gansu','East_Inner_Mongolia','Ningxia','Shaanxi']
for i in salt_zone:
    storage_project_tmp=pd.DataFrame(
        {'project': [i+'_'+'Hydrogen_salt_storage'],
         'zone': i,
         'technology': 'Salt_cavern',
         'capacity_group': 'group_underground',
         'gen_dbid': 'new'
            })
    hydrogen_storage_project=hydrogen_storage_project.append(storage_project_tmp)

hydrogen_project=hydrogen_project.append(hydrogen_storage_project)
    
cluster=cluster.append(hydrogen_project).reset_index().drop('index',axis=1)
cluster=cluster.drop(cluster.index[cluster.fuel=='Coal_Tibet'])
cluster=cluster.reset_index().drop('index',axis=1)
#%%

#source: Carbon reduction potential of China's coal-fired power plants based on a CCUS source-sink matching model

ccs_storage=pd.DataFrame()
oil_load_zone=['Heilongjiang','Jilin','Liaoning',
               'Tianjin','Hebei','Henan','Jiangsu',
               'Anhui','Hubei','Sichuan','Chongqing','East_Inner_Mongolia','West_Inner_Mongolia','Qinghai','Xinjiang','Gansu']

# need to check saline zone

for i in oil_load_zone:
    ccs_storage_tmp=pd.DataFrame(
        {'project': [i+'_'+'CCS_storage_oil', i+'_'+'CCS_storage_saline'],
         'zone':i,	
         'technology':["CCS_storage_oil", 'CCS_storage_saline'],
         'capacity_group': ['group_ccs_storage', 'group_ccs_storage'],
         'gen_dbid': ["new","new"],
         'variable_ccs_om_cost_per_tonne':[1.02*1.1,1.02*1.01],
         'ccs_mwh_per_tonne':[0.01,0.01]
         }
        )
    ccs_storage=ccs_storage.append(ccs_storage_tmp)
    
ccs_storage_offshore=pd.DataFrame()
offshore_load_zone=['Guangxi','Guangdong','Hainan','Fujian','Zhejiang','Jiangsu','Shandong','Liaoning']
for i in offshore_load_zone:
    ccs_storage_offshore_tmp=pd.DataFrame(
        {'project': [i+'_'+'CCS_storage_offs6hore'],
         'zone':i,	
         'technology':["CCS_storage_offshore"],
         'capacity_group': ['group_ccs_storage'],
         'gen_dbid': "new",
         'variable_ccs_om_cost_per_tonne':2.51*1.1,
         'ccs_mwh_per_tonne':0.01
         }
        )
    ccs_storage_offshore=ccs_storage_offshore.append(ccs_storage_offshore_tmp)

ccs_storage=ccs_storage.append(ccs_storage_offshore)

cluster_ccs_storage=cluster.append(ccs_storage).reset_index().drop('index',axis=1)
#cluster_existing=cluster.loc[cluster['gen_dbid']=='existing',:]
#province_capacity=cluster_existing.groupby(['zone','capacity_group'])['capacity'].sum().reset_index().pivot(index='zone',columns='capacity_group',values='capacity')
#province_capacity.to_csv('raw_data/capcity_region.csv',na_rep='')


#%% DAC
DAC_project=pd.DataFrame()
for i in load_zone:
    DAC_project_tmp=pd.DataFrame(
        {'project': [i+'_DAC'],
         'zone':i,	
         'technology':["DAC"],
         'capacity_group': "group_dac",
         'variable_ccs_om_cost_per_tonne':0,
         'ccs_mwh_per_tonne':1.5,
         'gen_dbid': ["new"],
         'fuel': 'DAC'
         }
        )
    DAC_project=DAC_project.append(DAC_project_tmp)
        
cluster_ccs_dac=cluster_ccs_storage.append(DAC_project).reset_index().drop('index',axis=1)

'''
#calibrate
#This is only used for calibratio nrun
calibrate=pd.read_excel('raw_data/capacity_region.xlsx',sheet_name='ratio')
for i in np.unique(cluster['zone']):
    for j in np.unique(cluster.loc[cluster['gen_dbid']=='existing','capacity_group']):
            index_tmp=(cluster['zone']==i) & (cluster['capacity_group']==j)&(cluster['gen_dbid']=='existing')
            cluster.loc[index_tmp,'capacity']=cluster.loc[index_tmp,'capacity']*calibrate.loc[calibrate['zone']==i,j].values[0] 
 
#cluster_existing=cluster.loc[cluster['gen_dbid']=='existing',:]
#province_capacity=cluster_existing.groupby(['zone','capacity_group'])['capacity'].sum().reset_index().pivot(index='zone',columns='capacity_group',values='capacity')
'''

#%%
period=np.arange(2050,2060,10)
horizon=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/temporal/9_China_1period_3horizon_full/horizon_params.csv')

timepoints=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/temporal/9_China_1period_3horizon_full/structure.csv')['timepoint']
structure=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/temporal/9_China_1period_3horizon_full/structure.csv')

share_path='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/project/'

#%%
#project_portofolio
from project_function import generate_project_portfolio
portfolio_scenario=1
portfolio_description='portfolio_base'
path_portfolio=share_path+'project_portfolios/'+str(portfolio_scenario)+'_'+portfolio_description+'.csv'

ccs_option=0
cluster_base=cluster.loc[~cluster.capacity_group.isin(['group_p2g','group_g2p','group_H2','group_tank','group_underground']),:]

project_portofolio=generate_project_portfolio(cluster_base,ccs_option)
project_portofolio.to_csv(path_portfolio,index=False)

portfolio_scenario=2
portfolio_description='portfolio_H2'
cluster_H2=cluster.loc[~(cluster.capacity_group.isin(['group_H2'])),:]
ccs_option=0
project_portofolio=generate_project_portfolio(cluster_H2,ccs_option)
path_portfolio=share_path+'project_portfolios/'+str(portfolio_scenario)+'_'+portfolio_description+'.csv'
project_portofolio.to_csv(path_portfolio,index=False)

portfolio_scenario=3
portfolio_description='portofolio_H2_ccs'
path_portfolio=share_path+'project_portfolios/'+str(portfolio_scenario)+'_'+portfolio_description+'.csv'

ccs_option=1
cluster_ccs=cluster_ccs_dac.loc[~(cluster_ccs_dac.capacity_group.isin(['group_H2','group_ccs_storage'])),:]
project_portfolio_ccs=generate_project_portfolio(cluster_ccs,ccs_option)
project_portfolio_ccs.to_csv(path_portfolio,index=False)

portfolio_scenario=4
portfolio_description='portofolio_H2_ccs_storage'
path_portfolio=share_path+'project_portfolios/'+str(portfolio_scenario)+'_'+portfolio_description+'.csv'

ccs_option=1
cluster_storage=cluster_ccs_dac.loc[~cluster_ccs_dac.capacity_group.isin(['group_H2']),:]
project_portfolio_ccs=generate_project_portfolio(cluster_storage,ccs_option)
project_portfolio_ccs.to_csv(path_portfolio,index=False)

portfolio_scenario=5
portfolio_description='portofolio_H2_ccs_dac'
path_portfolio=share_path+'project_portfolios/'+str(portfolio_scenario)+'_'+portfolio_description+'.csv'

ccs_option=1
project_portfolio_ccs=generate_project_portfolio(cluster_ccs_dac,ccs_option)
project_portfolio_ccs.to_csv(path_portfolio,index=False)

#%%
#project_availability
from project_function import generate_availability_type
availability_type_scenario=1
availability_description='base_Hydrogen'
exogenous_availability_scenario_id=1
path_availability_type=share_path+'project_availability/project_availability_types/'+str(availability_type_scenario)+'_'+availability_description+'.csv'

project_availability_type=generate_availability_type(cluster_ccs_dac,exogenous_availability_scenario_id)
project_availability_type.to_csv(path_availability_type,index=False)

#%%
from project_function import generate_availability_exogenous
exogenous_availability_scenario=1
exogenous_scenario_description='cali'
derate_group=pd.DataFrame({'tech':['group_nuclear','group_coal','group_gas'],

                           'derate':[0.84,0.54,1]})
group=[]
generate_availability_exogenous(cluster, derate_group, group, timepoints, exogenous_availability_scenario, exogenous_scenario_description,share_path)


#%%project_capacity_group
from project_function import generate_project_cap_group
cap_group_scenario=2
cap_group_description='hydrogen_cap_groups'
path_capacity_group=share_path+'project_capacity_groups/projects/'+str(cap_group_scenario)+'_'+cap_group_description+'.csv'

project_capacity_groups=generate_project_cap_group(cluster_base)
project_capacity_groups.to_csv(path_capacity_group,index=False)

cap_group_scenario=3
cap_group_description='hydrogen_ccs_cap_groups'
path_capacity_group=share_path+'project_capacity_groups/projects/'+str(cap_group_scenario)+'_'+cap_group_description+'.csv'

project_capacity_groups=generate_project_cap_group(cluster_ccs_storage)
project_capacity_groups.to_csv(path_capacity_group,index=False)


cap_group_scenario=5
cap_group_description='hydrogen_cap_groups_ccs_dac'
path_capacity_group=share_path+'project_capacity_groups/projects/'+str(cap_group_scenario)+'_'+cap_group_description+'.csv'

project_capacity_groups=generate_project_cap_group(cluster_ccs_dac)
project_capacity_groups.to_csv(path_capacity_group,index=False)

#%%project_heat_rate_curves
from project_function import generate_heat_rate_curve
heat_scenario=1
heat_scenario_description='base'
project_heat_rate_curves=generate_heat_rate_curve(heat_scenario, heat_scenario_description, cluster,share_path)

#%%project_hydro_operational_chars
from project_function import generate_hydro_operation_chars_full
hydro_oper_scenario_id=1

load_zone=np.unique(cluster['zone'])

project_hydro_operational_chars=generate_hydro_operation_chars_full(cluster, hydro_oper_scenario_id,horizon,share_path)
    
#%%project_load_zone
from project_function import generate_load_zone
load_zone_scenario=1
load_zone_description='china_Hydrogen'

load_zone_path=share_path+'project_load_zones/'+str(load_zone_scenario)+'_'+load_zone_description+'.csv'
project_load_zone=generate_load_zone(cluster_ccs_dac)

project_load_zone.to_csv(load_zone_path,index=False)

from reliability_function import generate_prm_load_zone
path_prm='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/reliability/prm/project_prm_zones'

non_prm=[]
prm_load_zone=generate_prm_load_zone(cluster_base,non_prm)
prm_load_zone.to_csv(path_prm+'/'+'1_china_Hydrogen.csv',index=False)

non_prm=['group_p2g','group_underground','group_tank','group_H2']
prm_load_zone=generate_prm_load_zone(cluster,non_prm)
prm_load_zone.to_csv(path_prm+'/'+'2_china_Hydrogen_new.csv',index=False)


non_prm=['group_p2g','group_H2','group_underground','group_tank','group_ccs_storage']
prm_load_zone=generate_prm_load_zone(cluster_ccs_storage,non_prm)
prm_load_zone.to_csv(path_prm+'/'+'3_china_Hydrogen_ccs.csv',index=False)



non_prm=['group_p2g','group_underground','group_tank','group_ccs_storage','group_dac']
prm_load_zone=generate_prm_load_zone(cluster_ccs_storage,non_prm)
prm_load_zone.to_csv(path_prm+'/'+'5_china_Hydrogen_ccs.csv',index=False)

#%%project_fixed_cost
from project_function import generate_fixed_cost
from project_function import generate_new_cost

fixed_cost_set=pd.DataFrame(
    {
       'fixed_cost_description': ['moderate_hydrogen','advance_hydrogen','conservative_hydrogen','High_cost_wind',
                                  'High_cost_PV','High_cost_electrolyzer','High_cost_fuel_cell','High_cost_tank','moderate_hydrogen_high_ccs'],
       'fixed_cost_scenario': [1,2,3,4,5,6,7,8,9]
       }
    )

new_cost_set=pd.DataFrame(
    {
       'new_cost_description': ['moderate_hydrogen','advance_hydrogen','conservative_hydrogen','High_cost_wind',
                                  'High_cost_PV','High_cost_electrolyzer','High_cost_fuel_cell','High_cost_tank','moderate_hydrogen_high_ccs'],
       'new_cost_scenario': [1,2,3,4,5,6,7,8,9]
       }
    )

for i in range(len(fixed_cost_set)):
    fixed_cost_scenario=fixed_cost_set.loc[i,'fixed_cost_scenario']
    fixed_cost_description=fixed_cost_set.loc[i,'fixed_cost_description']
    path_fixed_cost=share_path+'project_specified_fixed_cost/'+str(fixed_cost_scenario)+'_'+fixed_cost_description+'.csv'

    fixed_cost=pd.read_excel('fixed_cost_new.xlsx',sheet_name=fixed_cost_description)

    new_cost_scenario=new_cost_set.loc[i,'new_cost_scenario']
    new_cost_description=new_cost_set.loc[i,'new_cost_description']

    path_new_cost=share_path+'project_new_cost/'+str(new_cost_scenario)+'_'+new_cost_description+'.csv'

    discount=0.08

    capital_cost=pd.read_excel('annualized_cost.xlsx',sheet_name=new_cost_description)
    lifetime=pd.read_excel('annualized_cost.xlsx',sheet_name='lifetime')
    lifetime_np=lifetime.iloc[:,1:].to_numpy()
    crf=discount*(1+discount)**lifetime_np/((1+discount)**lifetime_np-1)
    capital_cost.iloc[:,1:]=crf*capital_cost.iloc[:,1:]
    
    project_fixed_cost=generate_fixed_cost(cluster_ccs_dac,fixed_cost,capital_cost)
    project_fixed_cost.to_csv(path_fixed_cost,index=False)
    
    project_new_cost=generate_new_cost(cluster_ccs_dac, capital_cost, lifetime,fixed_cost)
    project_new_cost.to_csv(path_new_cost,index=False)

#%%project_new_cost


#Reference: The role of electricity storage and hydrogen technologies in enabling global low-carbon energy transitions
'''
Modrate
Cap_ele_storage=np.linspace(1014,525,91)

Cap_cell=np.linspace(3000,434,91)

Cap_turbine=np.linspace(318,289,91)

energy_cost=0.16 #Joule, Doweling
efficiency_turbine=0.4
efficiency_cell=0.58
efficiency_ele=0.73

life_ele=20
life_cell=20
life_turbine=30

r=0.08
CRF_cell=r*(1+r)**(life_cell)/((1+r)**life_cell-1)
CRF_turbine=r*(1+r)**(life_turbine)/((1+r)**life_turbine-1)
CRF_ele=r*(1+r)**(life_ele)/((1+r)**life_ele-1)

Cap_ele_turbine=(Cap_ele_storage[[0,5,10,15,20,25,30]]+efficiency_turbine*Cap_turbine[[0,5,10,15,20,25,30]])*1000
Cap_ele_cell=(Cap_ele_storage[[0,5,10,15,20,25,30]]+efficiency_cell*Cap_cell[[0,5,10,15,20,25,30]])*1000
'''

'''
Low cost
Cap_ele_storage=np.linspace(1014,263,91) # 2010-2100 cost

Cap_cell=np.linspace(3000,217,91)

Cap_turbine=np.linspace(318,289,91)

energy_cost=0.16 #Joule, Doweling
efficiency_turbine=0.4
efficiency_cell=0.58
efficiency_ele=0.73

life_ele=20
life_cell=20
life_turbine=30

r=0.08
CRF_cell=r*(1+r)**(life_cell)/((1+r)**life_cell-1)
CRF_turbine=r*(1+r)**(life_turbine)/((1+r)**life_turbine-1)
CRF_ele=r*(1+r)**(life_ele)/((1+r)**life_ele-1)

Cap_ele_turbine=(Cap_ele_storage[[0,5,10,15,20,25,30]]+efficiency_turbine*Cap_turbine[[0,5,10,15,20,25,30]])*1000
Cap_ele_cell=(Cap_ele_storage[[0,5,10,15,20,25,30]]+efficiency_cell*Cap_cell[[0,5,10,15,20,25,30]])*1000
'''
    

#%%project_new_potential
from project_function import generate_new_potential
new_potential_scenario=1
new_potential_description='project_nocap_hydrogen'
path_new_potential=share_path+'project_new_potential/'+str(new_potential_scenario)+'_'+new_potential_description+'.csv'

#stop_build=['group_coal']
stop_build=[]
project_new_potential=generate_new_potential(cluster_ccs_dac, period, stop_build)

project_new_potential.to_csv(path_new_potential,index=False)

#%%project_operation_chars
from project_function import generate_operate_chars
var_id=1
ccs_option=0
project_operation_chars=generate_operate_chars(cluster,var_id,ccs_option)

project_operation_chars.to_csv(share_path+'project_operational_chars/1_hydrogen_hourly.csv',na_rep='',index=False)


ccs_option=1
project_operation_chars=generate_operate_chars(cluster_ccs_dac,var_id,ccs_option)

project_operation_chars.to_csv(share_path+'project_operational_chars/3_hydrogen_hourly_ccs.csv',na_rep='',index=False)

#%%project_specified_capacity
from project_function import generate_specified_capacity
specified_capacity_scenario=1
specified_capacity_description='project_hydrogen'
path_specified_capacity=share_path+'project_specified_capacity/'+str(specified_capacity_scenario)+'_'+specified_capacity_description+'.csv'

project_specified_capacity=generate_specified_capacity(cluster,period)
project_specified_capacity.to_csv(path_specified_capacity,index=False)

#%%project_variable
from project_function import generate_variable_generator_profile_full

variable_scenario_id=1
description='generator_profile_1'
generate_variable_generator_profile_full(cluster, variable_scenario_id, description, timepoints,share_path)

#%%
from project_function import generate_carbon_cap_load_zone

carbon_cap_load_zone=generate_carbon_cap_load_zone(cluster_base)
carbon_cap_load_zone.to_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/policy/carbon_cap/project_carbon_cap_zones/1_project_carbon_cap_zones_china.csv',index=False)

carbon_cap_load_zone=generate_carbon_cap_load_zone(cluster_ccs_dac)
carbon_cap_load_zone.to_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/policy/carbon_cap/project_carbon_cap_zones/2_project_carbon_cap_zones_china.csv',index=False)
#%%
from project_function import generate_system_load_full, generate_system_load_full_flat_hydrogen

period_select=np.arange(2050,2060,10)

scale=pd.read_excel('load_scenario.xlsx',index_col=0)
scenario=scale.columns.tolist()
share_path_db='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/system_load/'
system_load=generate_system_load_full(period_select,structure,scale,scenario,share_path_db)
system_load=generate_system_load_full_flat_hydrogen(period_select,structure,scale,scenario,share_path_db)



#%% prm
from reliability_function import generate_prm_project_elcc
#project_elcc_chars
prm_project_elcc=generate_prm_project_elcc(cluster_no)
prm_project_elcc.to_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/reliability/prm/project_elcc_chars/4_project_hydrogen_elcc.csv',index=False)

#system prm requirement
from reliability_function import generate_system_prm_req
share_path_rel='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/'
generate_system_prm_req(scenario,share_path_rel)

#%%operating reserve
'''
from reliability_function import generate_system_reserve_req
generate_system_reserve_req(scenario)

from reliability_function import generate_reserve_load_zone
gen_type=pd.read_csv('project/project_operational_chars/2_hydrogen_full.csv')[['project','operational_type']]
generate_reserve_load_zone(cluster,gen_type)
'''
#%%% transmission lines
transmission_portfolio=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_portfolios/4_transmission_portfolios_new_and_existing_reduced.csv')

load_zone_from=transmission_portfolio.transmission_line.str.split('-').str[0]
load_zone_to=transmission_portfolio.transmission_line.str.split('-').str[1]

transmission_H2=transmission_portfolio.loc[transmission_portfolio.capacity_type=='tx_new_lin',:]
load_zone_from_H2=transmission_H2.transmission_line.str.split('-').str[0]
load_zone_to_H2=transmission_H2.transmission_line.str.split('-').str[1]
transmission_H2.transmission_line=['H2_'+i for i in transmission_H2.transmission_line]

transmission_mass=transmission_portfolio.loc[transmission_portfolio.capacity_type=='tx_new_lin',:]
load_zone_from_mass=transmission_mass.transmission_line.str.split('-').str[0]
load_zone_to_mass=transmission_mass.transmission_line.str.split('-').str[1]
transmission_mass.transmission_line=['ccs_'+i for i in transmission_mass.transmission_line]
transmission_mass.capacity_type='mass_new_lin'

transmission_H2=transmission_H2.append(transmission_portfolio)
transmission_mass=transmission_mass.append(transmission_H2)

transmission_load_zone_H2=pd.DataFrame()
load_zone_from_H2=load_zone_from_H2.append(load_zone_from)
load_zone_to_H2=load_zone_to_H2.append(load_zone_to)

transmission_load_zone_H2.loc[:,'transmission_line']=transmission_H2.transmission_line
transmission_load_zone_H2.loc[:,'load_zone_from']=load_zone_from_H2
transmission_load_zone_H2.loc[:,'load_zone_to']=load_zone_to_H2

transmission_load_zone_mass=pd.DataFrame()
load_zone_from_mass=load_zone_from_mass.append(load_zone_from_H2)
load_zone_to_mass=load_zone_to_mass.append(load_zone_to_H2)

transmission_load_zone_mass.loc[:,'transmission_line']=transmission_mass.transmission_line
transmission_load_zone_mass.loc[:,'load_zone_from']=load_zone_from_mass
transmission_load_zone_mass.loc[:,'load_zone_to']=load_zone_to_mass


transmission_H2.to_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_portfolios/5_transmission_portfolios_H2.csv',index=False)
transmission_mass.to_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_portfolios/6_transmission_portfolios_H2_ccs.csv',index=False)

transmission_load_zone_H2.to_csv("C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_load_zones/3_transmission_H2.csv",index=False)
transmission_load_zone_mass.to_csv("C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_load_zones/4_transmission_H2_ccs.csv",index=False)
#%%
#tranmission operation and new cost
#data are from nrel, cost of hydrogen storage and transport
#source: energy technology data, Danish energy agency
pipeline_cost=(200+1.1)*1.1
pipeline_loss=0.013
pipe_lifetime=50

discount=0.08

annualized_pipe=200*(discount*(1+discount)**pipe_lifetime)/((1+discount)**pipe_lifetime-1)+1.1
#from lbnl
HVAC_cost=300
annualized_HVAC=300*(discount*(1+discount)**20)/((1+discount)**20-1)+300*0.03
HVAC_loss=0.053


#ccs
ccs_cost=(13 *1.1*1000)+20*1.1  #tonne CO2/h/m
ccs_loss=0
ccs_lifetime=50
annualized_ccs=13000*(discount*(1+discount)**ccs_lifetime)/((1+discount)**ccs_lifetime-1)+20


transmission_operation=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_operational_chars/1_tx_simple_w_losses.csv')
transmission_operation_H2=transmission_operation.copy()
transmission_operation_H2.transmission_line=['H2_'+i for i in transmission_operation_H2.transmission_line]
transmission_operation_H2.operational_type='H2_simple'
transmission_operation_H2.tx_simple_loss_factor=transmission_operation_H2.tx_simple_loss_factor*pipeline_loss/HVAC_loss

transmission_operation_ccs=transmission_operation.copy()
transmission_operation_ccs.transmission_line=['ccs_'+i for i in transmission_operation_ccs.transmission_line]
transmission_operation_ccs.operational_type='ccs_simple'
transmission_operation_ccs.tx_simple_loss_factor=0


transmission_operation_H2=transmission_operation.append(transmission_operation_H2)
transmission_operation_H2.to_csv("C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_operational_chars/2_tx_H2_losses.csv",index=False)

transmission_operation_ccs=transmission_operation_ccs.append(transmission_operation_H2)
transmission_operation_ccs.to_csv("C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_operational_chars/3_tx_H2_ccs_losses.csv",index=False)

#==============================================================================

#new cost
transmission_new_cost=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_new_cost/1_transmission_new_cost_1.csv')
transmission_new_cost.vintage=transmission_new_cost.vintage-1
transmission_new_cost_2050=transmission_new_cost.loc[transmission_new_cost.vintage==2020,:].copy()
transmission_new_cost_2050.vintage=2050
transmission_new_cost=transmission_new_cost.append(transmission_new_cost_2050)
transmission_new_cost.loc[:,'tx_annualized_real_cost_per_tonne_yr']=""


transmission_new_cost_H2=transmission_new_cost.copy()
transmission_new_cost_H2.transmission_line=['H2_'+i for i in transmission_new_cost_H2.transmission_line]
transmission_new_cost_H2.tx_lifetime_yrs=pipe_lifetime
transmission_new_cost_H2.tx_annualized_real_cost_per_mw_yr=transmission_new_cost_H2.tx_annualized_real_cost_per_mw_yr*annualized_pipe/annualized_HVAC
transmission_new_cost_H2=transmission_new_cost_H2.append(transmission_new_cost)
transmission_new_cost_H2.to_csv("C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_new_cost/2_transmission_new_cost_H2.csv",index=False)

transmission_new_cost_ccs=transmission_new_cost.copy()
transmission_new_cost_ccs.transmission_line=['ccs_'+i for i in transmission_new_cost.transmission_line]
transmission_new_cost_ccs.tx_lifetime_yrs=ccs_lifetime
transmission_new_cost_ccs.tx_annualized_real_cost_per_tonne_yr=transmission_new_cost_ccs.tx_annualized_real_cost_per_mw_yr*annualized_ccs/annualized_HVAC
transmission_new_cost_ccs.tx_annualized_real_cost_per_mw_yr=0
transmission_new_cost_ccs=transmission_new_cost_ccs.append(transmission_new_cost_H2)
transmission_new_cost_ccs.to_csv("C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/transmission_new_cost/3_transmission_new_cost_H2_ccs.csv",index=False)