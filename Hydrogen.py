# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 14:57:43 2023

@author: haozheyang
"""
import pandas as pd
import numpy as np
#Add hyfro profile
path_to_zone='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/system_load/load_zones'
load_zone=pd.read_csv(path_to_zone+'/1_china.csv')['load_zone']

#%%
#generate hydro profile
hydrogen_project=pd.DataFrame()
for i in load_zone:
    hydrogen_project_tmp=pd.DataFrame(
        {'project': ['Hydrogen_fuel_cell'+'_'+i,'Hydrogen_turbine'+'_'+i],
         'specified':["",""],	
         'new_build':["",""],	
         'capacity_type': ["stor_new_lin","stor_new_lin"]
         }
        )
    hydrogen_project=hydrogen_project.append(hydrogen_project_tmp)

path_to_portofolio='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/project/project_portfolios'
portofolio=pd.read_csv(path_to_portofolio+'/'+'1_portofolio.csv')
portofolio_new=portofolio.append(hydrogen_project)
    
portofolio_new.to_csv(path_to_portofolio+'/'+'3_portofolio_Hydrogen.csv',index=False)

#%%load_zone
hydrogen_load_zone=pd.DataFrame()
for i in load_zone:
    hydrogen_load_zone_tmp=pd.DataFrame(
        {'project': ['Hydrogen_fuel_cell'+'_'+i,'Hydrogen_turbine'+'_'+i],
         'load_zone':i
         }
        )
    hydrogen_load_zone=hydrogen_load_zone.append(hydrogen_load_zone_tmp)

path_to_load_zone='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/project/project_load_zones'
project_load_zone=pd.read_csv(path_to_load_zone+'/'+'1_china.csv')
project_load_zone_new=project_load_zone.append(hydrogen_load_zone)
project_load_zone_new.to_csv(path_to_load_zone+'/'+'2_china_Hydrogen.csv',index=False)

path_prm='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/reliability/prm/project_prm_zones'
project_load_zone_new.to_csv(path_prm+'/'+'2_china_Hydrogen.csv',index=False)

path_carbon='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/policy/carbon_cap/project_carbon_cap_zones'
project_load_zone_new.to_csv(path_carbon+'/'+'3_china_Hydrogen.csv',index=False)

#%%
#generate cost profile
import pickle

path_to_atb='//babylon/phd/haozheyang/Hydrogen'
with open(path_to_atb + '/tech_costs.pkl', 'rb') as _file:
    data_ = pickle.load(_file)
keys_, Costs_ = data_
  
print(Costs_.shape)
  
technologies_, scenarios_, metrics_, x_hat_ = keys_
x_hat_ = np.array(x_hat_)
print(x_hat_)

hydro_Cap=Costs_[[3,4,5],1,0,]
hydro_OM=Costs_[[3,4,5],1,1,]

Cap_cell=np.linspace(3000,434,81)
OM_cell=Cap_cell*0.05

energy_cost=0.16
efficiency_turbine=0.4*0.73
efficiency_cell=0.58*0.73

life_cell=20
life_turbine=30

r=0.08
CRF_cell=r*(1+r)**(life_cell)/((1+r)**life_cell-1)
CRF_turbine=r*(1+r)**(life_turbine)/((1+r)**life_turbine-1)


Cap_ele_turbine=hydro_Cap[0,[0,10,20]]*CRF_cell+hydro_Cap[1,[0,10,20]]*CRF_cell+hydro_Cap[0,[0,10,20]]*CRF_turbine
OM_ele_turbine=hydro_OM.sum(axis=0)[[0,10,20]]

Cap_ele_cell=(Cap_cell[[0,10,20]]+hydro_Cap[0,[0,10,20]]+hydro_Cap[1,[0,10,20]])*CRF_cell
OM_ele_cell=OM_cell[[0,10,20]]+hydro_OM[0,[0,10,20]]+hydro_OM[1,[0,10,20]]

hydrogen_cost=pd.DataFrame()
for i in hydrogen_project.project:
    for year_id,year in enumerate([2020,2030,2040]):
        if 'cell' in i:
            hydrogen_cost_tmp=pd.DataFrame(
                {
                    'project':[i],
                    'vintage': year,
                    'lifetime_yrs': life_cell,
                    'annualized_real_cost_per_mw_yr': Cap_ele_cell[year_id]*1000,
                    'annualized_real_cost_per_mwh_yr':energy_cost*CRF_cell*1000,
                    'levelized_cost_per_mwh':""
                    }
                )
        if 'turbine' in i:
            hydrogen_cost_tmp=pd.DataFrame(
                {
                    'project':[i],
                    'vintage': year,
                    'lifetime_yrs': life_turbine,
                    'annualized_real_cost_per_mw_yr': Cap_ele_turbine[year_id]*1000,
                    'annualized_real_cost_per_mwh_yr':energy_cost*CRF_cell*1000,
                    'levelized_cost_per_mwh':""
                    }
                )
        hydrogen_cost=hydrogen_cost.append(hydrogen_cost_tmp)

path_to_cost='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/project/project_new_cost'
project_new_cost=pd.read_csv(path_to_cost+'/2_high.csv')
project_new_cost_new=project_new_cost.append(hydrogen_cost)
project_new_cost_new.to_csv(path_to_cost+'/5_advance_hydrogen.csv',index=False)

#%%new potential           

hydrogen_potential=pd.DataFrame()
for i in hydrogen_project.project:
    hydrogen_potential_tmp=pd.DataFrame(
        {
            'project':[i,i,i],
            'period':[2020,2030,2040],
            'min_cumulative_new_build_mw':"",	
            'max_cumulative_new_build_mw':"",
            'min_cumulative_new_build_mwh':"",
            'max_cumulative_new_build_mwh':""
            }
        )
    hydrogen_potential=hydrogen_potential.append(hydrogen_potential_tmp)
        
path_to_potential='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/project/project_new_potential'
        
project_new_potential=pd.read_csv(path_to_potential+'/3_project_2035lbnl_coal_no_limit.csv')
project_new_potential_new=project_new_potential.append(hydrogen_potential)
project_new_potential_new.to_csv(path_to_potential+'/4_moderate_hydrogen.csv',index=False)


#%%
#operation
hydrogen_operation=pd.DataFrame()
for i in hydrogen_project.project:
    if 'cell' in i:
        hydrogen_operation_tmp=pd.DataFrame(
        {
            'project':	[i],
            'technology':'Storage',	
            'operational_type': 'stor',
            'balancing_type_project':  'year',
            'charging_efficiency': 0.73,
            'discharging_efficiency': 0.58,
            'minimum_duration_hours': 1	,
            'maximum_duration_hours': 24*60,
        }
        )
    if 'turbine' in i:
        hydrogen_operation_tmp=pd.DataFrame(
        {
            'project':	[i],
            'technology':'Storage',	
            'operational_type': 'stor',
            'balancing_type_project':  'year',
            'charging_efficiency': 0.73,
            'discharging_efficiency': 0.4,
            'minimum_duration_hours': 1	,
            'maximum_duration_hours': 24*60,
        }
        )
    hydrogen_operation=hydrogen_operation.append(hydrogen_operation_tmp)


path_to_operation='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/project/project_operational_chars'
        
project_operation=pd.read_csv(path_to_operation+'/2_full.csv')
project_operation_new=project_operation.append(hydrogen_operation)
project_operation_new.to_csv(path_to_operation+'/3_full_hydrogen.csv',index=False)

