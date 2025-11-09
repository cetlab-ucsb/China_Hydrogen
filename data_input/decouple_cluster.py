# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 19:15:29 2024

@author: haozheyang
"""

#decouple case
from IPython import get_ipython
get_ipython().magic('reset -sf')

import os
os.chdir("H:/Hydrogen")

import pandas as pd
import numpy as np

path='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/project/'
path_load='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/system_load/'
path_transmission='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/transmission/'
#%%portfolio
portfolio1=pd.read_csv(path+'project_portfolios/12_portofolio_ccs_storage_SMR_nocoal.csv')
portfolio2=pd.read_csv(path+'project_portfolios/9_portfolio_H2_100_renewable.csv')

#build new portfolio
electrolyzer=portfolio2.loc[portfolio2.project.str.contains('Electrolyzer'),:].copy()
electrolyzer.project=electrolyzer.project+'_H2'
portfolio2=portfolio2.append(electrolyzer)

portfolio2.to_csv(path+'project_portfolios/16_portofolio_2zones.csv',index=False)

salt_cavern=portfolio2.loc[portfolio2.project.str.contains('salt'),:]
salt_cavern.project=salt_cavern.project+'_H2'
portfolio2=portfolio2.append(salt_cavern)

tank=portfolio2.loc[portfolio2.project.str.contains('tank'),:]
tank.project=tank.project+'_H2'
portfolio2=portfolio2.append(tank)

portfolio2.to_csv(path+'project_portfolios/16_portofolio_2zones.csv',index=False)
#%%load zone
load_zone=pd.read_csv(path+'project_load_zones/1_china_Hydrogen.csv')

#build new load_zone
electrolyzer_load=load_zone.loc[load_zone.project.str.contains('Electrolyzer'),:]
electrolyzer_load=electrolyzer_load+'_H2'
load_zone=load_zone.append(electrolyzer_load)

salt_cavern_load=load_zone.loc[load_zone.project.str.contains('salt'),:]
salt_cavern_load=salt_cavern_load+'_H2'
load_zone=load_zone.append(salt_cavern_load)

tank_load=load_zone.loc[load_zone.project.str.contains('tank'),:]
tank_load=tank_load+'_H2'
load_zone=load_zone.append(tank_load)

load_zone.loc[load_zone.project.str.contains('SMR'),'load_zone']=load_zone.loc[load_zone.project.str.contains('SMR'),
                                                                     'load_zone']+'_H2'

load_zone.loc[load_zone.project.str.contains('Gasification'),'load_zone']=load_zone.loc[load_zone.project.str.contains('Gasification'),
                                                                     'load_zone']+'_H2'

load_zone.to_csv(path+'project_load_zones/3_china_Hydrogen_decouple.csv',index=False)

#%% new cost
new_cost=pd.read_csv(path+'project_new_cost/9_moderate_hydrogen_high_ccs.csv')

#build new load_zone
electrolyzer_cost=new_cost.loc[new_cost.project.str.contains('Electrolyzer'),:]
electrolyzer_cost.project=electrolyzer_cost.project+'_H2'
new_cost=new_cost.append(electrolyzer_cost)

salt_cavern_cost=new_cost.loc[new_cost.project.str.contains('salt'),:]
salt_cavern_cost.project=salt_cavern_cost.project+'_H2'
new_cost=new_cost.append(salt_cavern_cost)

tank_cost=new_cost.loc[new_cost.project.str.contains('tank'),:]
tank_cost.project=tank_cost.project+'_H2'
new_cost=new_cost.append(tank_cost)

new_cost.to_csv(path+'project_new_cost/10_moderate_decouple.csv',index=False)
#%% new potential
new_potential=pd.read_csv(path+'project_new_potential/1_project_nocap_hydrogen.csv')

#build new load_zone
electrolyzer_potential=new_potential.loc[new_potential.project.str.contains('Electrolyzer'),:]
electrolyzer_potential.project=electrolyzer_potential.project+'_H2'
new_potential=new_potential.append(electrolyzer_potential)

salt_cavern_potential=new_potential.loc[new_potential.project.str.contains('salt'),:]
salt_cavern_potential.project=salt_cavern_potential.project+'_H2'
new_potential=new_potential.append(salt_cavern_potential)

tank_storage_potential=new_potential.loc[new_potential.project.str.contains('tank'),:]
tank_storage_potential.project=tank_storage_potential.project+'_H2'
new_potential=new_potential.append(tank_storage_potential)

new_potential.to_csv(path+'project_new_potential/3_project_nocap_hydrogen_decouple.csv',index=False)
#%% availability
availability=pd.read_csv(path+'project_availability/project_availability_types/1_base_hydrogen.csv')

#build new load_zone
electrolyzer_availability=availability.loc[availability.project.str.contains('Electrolyzer'),:]
electrolyzer_availability.project=electrolyzer_availability.project+'_H2'
availability=availability.append(electrolyzer_availability)

salt_cavern_availability=availability.loc[availability.project.str.contains('salt'),:]
salt_cavern_availability.project=salt_cavern_availability.project+'_H2'
availability=availability.append(salt_cavern_availability)

tank_storage_availability=availability.loc[availability.project.str.contains('tank'),:]
tank_storage_availability.project=tank_storage_availability.project+'_H2'
availability=availability.append(tank_storage_availability)

availability.to_csv(path+'project_availability/project_availability_types/2_base_hydrogen_decouple.csv',index=False)
#%% operation
operation=pd.read_csv(path+'project_operational_chars/8_hydrogen_hourly_ccs_SMR_85.csv')

#build new load_zone
electrolyzer_operation=operation.loc[operation.project.str.contains('Electrolyzer'),:]
electrolyzer_operation.project=electrolyzer_operation.project+'_H2'
operation=operation.append(electrolyzer_operation)

salt_cavern_operation=operation.loc[operation.project.str.contains('salt'),:]
salt_cavern_operation.project=salt_cavern_operation.project+'_H2'
operation=operation.append(salt_cavern_operation)

tank_storage_operation=operation.loc[operation.project.str.contains('tank'),:]
tank_storage_operation.project=tank_storage_operation.project+'_H2'
operation=operation.append(tank_storage_operation)

operation.to_csv(path+'project_operational_chars/11_hydrogen_hourly_decouple.csv',index=False)

#%%load
system_load=pd.read_csv(path_load+'system_load/5_LBNL_H2_growth.csv')
system_load_H2=system_load.copy()
system_load_H2.load_zone=system_load_H2.load_zone+'_H2'
system_load_H2.load_mw=0

system_load.H2_mw=0
system_load=system_load.append(system_load_H2)
system_load.to_csv(path_load+'system_load/13_LBNL_H2_growth_decouple.csv',index=False)

load_zones=pd.read_csv(path_load+'load_zones/1_china.csv')
load_zones_H2=load_zones.copy()
load_zones_H2.load_zone=load_zones_H2.load_zone+'_H2'
load_zones = load_zones.append(load_zones_H2)
load_zones.to_csv(path_load+'load_zones/2_china_decouple.csv',index=False)

#%%transmission
transmission_portfolio=pd.read_csv(path_transmission+'transmission_portfolios/5_transmission_portfolios_H2.csv')
transmission_zone=pd.read_csv(path_load+'load_zones/1_china.csv')['load_zone']
transmission_zone_H2=transmission_zone+'_H2'
transmission_connect='H2_ele_'+transmission_zone+'_'+transmission_zone_H2
transmission_portfolio_H2=pd.DataFrame({
    'transmission_line': transmission_connect,
    'capacity_type':'tx_new_lin' 
    })
transmission_portfolio=transmission_portfolio.append(transmission_portfolio_H2)
transmission_portfolio.to_csv(path_transmission+'transmission_portfolios/9_transmission_portfolios_decouple.csv',index=False)

#%%transmission load zone
transmission_load_zone_H2=pd.DataFrame(
    {
    'transmission_line': transmission_connect,
    'load_zone_from': transmission_zone,
	'load_zone_to': transmission_zone_H2
    }
    )

transmission_load_zone=pd.read_csv(path_transmission+'transmission_load_zones/4_transmission_H2_ccs.csv')
transmission_load_zone=transmission_load_zone.append(transmission_load_zone_H2)
transmission_load_zone.to_csv(path_transmission+'transmission_load_zones/5_transmission_decouple.csv',index=False)

#%%
transmission_new_cost_H2=pd.DataFrame(
    {
    'transmission_line': transmission_connect,
    'vintage': 2050,
	'tx_lifetime_yrs':50,
	'tx_annualized_real_cost_per_mw_yr': 0,
	'tx_annualized_real_cost_per_tonne_yr': 0
    }
    )

transmission_new_cost=pd.read_csv(path_transmission+'transmission_new_cost/3_transmission_new_cost_H2_ccs.csv')
transmission_new_cost=transmission_new_cost.append(transmission_new_cost_H2)
transmission_new_cost.to_csv(path_transmission+'transmission_new_cost/4_transmission_new_cost_decouple.csv',index=False)

#%%

transmission_operation_H2=pd.DataFrame(
    {
    'transmission_line': transmission_connect,
    'operational_type': 'tx_simple',
	'tx_simple_loss_factor':0,
	'reactance_ohms':""

    }
    )

transmission_operation=pd.read_csv(path_transmission+'transmission_operational_chars/3_tx_H2_ccs_losses.csv')
transmission_operation=transmission_operation.append(transmission_operation_H2)
transmission_operation.to_csv(path_transmission+'transmission_operational_chars/4_tx_losses_decouple.csv',index=False)


