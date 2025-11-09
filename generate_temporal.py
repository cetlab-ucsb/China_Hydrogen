# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 14:39:54 2021

@author: haozheyang
"""

import os
os.chdir("H:/Hydrogen")

from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy as np
import pandas as pd
from temporal_function import generate_period,generate_horizon_params,generate_horizon_timepoint, generate_structure

#create period
period_gap=10
start_year=np.arange(2020,2050,20)
start_year=np.arange(2050,2060,10)
discount=0.08

file='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/temporal/10_China_1period_3horizon_12day/'
period_params=generate_period(start_year, period_gap, discount)
period_params.to_csv(file+'period_params.csv',index=False)

#horizon params
month=12
#day_in_month=[31,28,31,30,31,30,31,31,30,31,30,31]
day_in_month=[1,1,1,1,1,1,1,1,1,1,1,1]
subproblem='capacity_expansion'
linkage_option='circular'
horizon_params=generate_horizon_params(start_year, subproblem, month, day_in_month, linkage_option)
horizon_params.to_csv(file+'horizon_params.csv',index=False)

#create  horizon_timepoints
peak=0
timepoint_option=24  #determine the resolution by 24/timepoint_option
stage_option=1
horizon_timepoints=generate_horizon_timepoint(timepoint_option, horizon_params, stage_option, day_in_month)
horizon_timepoints.to_csv(file+'horizon_timepoints.csv',index=False)

#create structure.csv
structure=generate_structure(timepoint_option,month,horizon_timepoints,horizon_params,period_params,stage_option,day_in_month,peak)
structure.to_csv(file+'structure.csv',index=False)
#===============================================================================================================================
#choose the peak demand day, median demand day, and low wind day
wind=pd.DataFrame()
path_to_zone='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/system_load/load_zones'
load_zone=pd.read_csv(path_to_zone+'/1_china.csv')['load_zone']


demand=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/China_Load_'+str(2050)+'.csv').groupby(['Year','Month','Day']).mean().reset_index()
demand.loc[:,'total']=demand.loc[:,'Beijing':'Xinjiang'].sum(axis=1)


for i in load_zone:      
    wind_tmp=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/Renewables/'+i+'_'+'Wind.csv').groupby(['Month','Day'])['Value'].mean().reset_index()
    wind=wind.append(wind_tmp)

wind=wind.groupby(['Month','Day'])['Value'].sum().reset_index()

dayth_in_month={}
for month in [1,2,3,4,5,6,7,8,9,10,11,12]:
    wind_month=wind.loc[wind.Month==month,:]
    
    demand_month=demand.loc[demand.Month==month,['Year','Month','Day','total']]
    #demand_month_average=demand_month['total'].mean()
    #demand_month_delta=demand_month.copy()
    #demand_month_delta.total=abs(demand_month_delta['total']-demand_month_average)
    
    #day3=wind_month.loc[wind_month['Value'].idxmin(),'Day']
    #demand_month=demand_month.loc[demand_month.Day!=day3,:]
    
    demand_mean=demand_month.total.mean()
    demand_month['delta']=abs(demand_month.total-demand_mean)
    day1=demand_month.loc[demand_month['total'].idxmin(),'Day']
    day2=demand_month.loc[demand_month['delta'].idxmin(),'Day']
    day3=demand_month.loc[demand_month['total'].idxmax(),'Day']
    
    dayth_in_month[month]=[day1,day2,day3]
 
#==========================================================================================================================
from temporal_function import generate_horizon_params_select, generate_horizon_timepoint_select, generate_structure_select
#choose the day in each month
file='C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/temporal/11_China_1period_3horizon_36day/'
subproblem='capacity_expansion'
linkage_option='circular'
month=12

period_params=generate_period(start_year, period_gap, discount)
period_params.to_csv(file+'period_params.csv',index=False)

horizon_params=generate_horizon_params_select(start_year, subproblem, dayth_in_month, linkage_option)


horizon_params.to_csv(file+'horizon_params.csv',index=False)

#create  horizon_timepoints
peak=0
timepoint_option=24  #determine the resolution by 24/timepoint_option
stage_option=1
horizon_timepoints=generate_horizon_timepoint_select(timepoint_option, horizon_params, stage_option, dayth_in_month)
horizon_timepoints.to_csv(file+'horizon_timepoints.csv',index=False)

#create structure.csv
structure=generate_structure_select(timepoint_option,horizon_timepoints,horizon_params,period_params,stage_option,dayth_in_month,peak)
structure.to_csv(file+'structure.csv',index=False)

sum(structure.timepoint_weight)
