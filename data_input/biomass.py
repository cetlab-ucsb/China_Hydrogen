#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 23:34:40 2025

@author: hy4174
"""

from IPython import get_ipython
get_ipython().magic('reset -sf')

#import os
#os.chdir("H:/Hydrogen")

import pandas as pd
import numpy as np

timepoints=pd.read_csv('/Users/hy4174/Documents/gridpath-0.10.1/db/csvs_plexos_hydrogen/temporal/9_China_1period_3horizon_full/structure.csv')['timepoint']
structure=pd.read_csv('/Users/hy4174/Documents/gridpath-0.10.1/db/csvs_plexos_hydrogen/temporal/9_China_1period_3horizon_full/structure.csv')

share_path='/Users/hy4174/Documents/gridpath-0.10.1/db/csvs_plexos_hydrogen/project/'


path='/Users/hy4174/Documents/gridpath-0.10.1/db/csvs_plexos_hydrogen/project/'
path_load='/Users/hy4174/Documents/gridpath-0.10.1/db/csvs_plexos_hydrogen/system_load/'
path_transmission='/Users/hy4174/Documents/gridpath-0.10.1/db/csvs_plexos_hydrogen/transmission/'
#%%portfolio
portfolio=pd.read_csv(path+'project_portfolios/4_portofolio_H2_ccs_dac_storage.csv')

#add biomass

load_zone=pd.read_csv(path_load+'load_zones/1_china.csv')

#portfolio
biomass_project=pd.DataFrame()
for i in load_zone.load_zone:
    biomass_project_tmp=pd.DataFrame(
        {'project': [i+'_Biomass',i+'_Biomass_CCS'],
         'zone':[i,i],	
         'technology':["Biomass","BECCS"],
         'capacity_group': ["group_biomass","group_biomass"],
         'gen_full_load_heat_rate':[4.8, 5.3],
         'variable_om_cost_per_mwh':[0.8,1.3],
         'gen_dbid': ["new","new"],
         'fuel': ['Biomass','Biomass']
         }
        )

    biomass_project=pd.concat([biomass_project, biomass_project_tmp.project])
        
#load zone

#heat rate
generator=biomass_project
heat_rate_full=13.5
heat_scenario=1
heat_scenario_description='base'

for project in biomass_project.project:
  
    heatrate_full_tmp=13.5
    
    project_heat_rate=pd.DataFrame({'period': [0]	,
                                  'load_point_fraction':[1],
                                  'average_heat_rate_mmbtu_per_mwh': [heatrate_full_tmp]
                                  })       
        
    rp=project+'-'+str(heat_scenario)+'-'+heat_scenario_description
    path_to_file=share_path+'project_heat_rate_curves/'+rp+'.csv'
    project_heat_rate.to_csv(path_to_file,index=False)
    
#new potential

#new cost

#capacity group potential

#availability
exogenous=biomass_project
exogenous_availability_scenario=1
exogenous_scenario_description='cali'

for project in exogenous.project:
    project_availability_exogenous=pd.DataFrame()
    availability_derate=0.64

    project_availability_exogenous=pd.DataFrame({
                                                'stage_id': 1,
                                                'timepoint' :timepoints,
                                                'availability_derate': availability_derate
                                                }) 
    #project_availability_exogenous=concat([project_availability_exogenous,project_availability_exogenous_tmp])     
    rp=project +'-'+str(exogenous_availability_scenario)+'-'+exogenous_scenario_description
    filename=share_path+'project_availability/'+'project_availability_exogenous/'+rp+'.csv'    
    project_availability_exogenous.to_csv(filename, index=False)
#operation


#planning reserve margin


#carbon cap
