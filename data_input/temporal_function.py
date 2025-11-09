# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 15:39:32 2021

@author: haozheyang
"""

from numpy import linspace, arange
import numpy as np
from math import ceil,log
from pandas import DataFrame

def generate_period(start_year,period_gap,discount):
   
   period_params=DataFrame()
   if start_year.size>1:
        for i in start_year:
          period_params=period_params.append(DataFrame({'period' : [i],
                                'discount_factor': 1/(1+discount)**(i-start_year[0]),
                                'period_start_year': i,
                                'period_end_year': i+period_gap,
                               
                                })
                               )
   else:
        period_params=period_params.append(DataFrame({'period' : start_year,
                      'discount_factor': 1,
                      'period_start_year': start_year,
                      'period_end_year': start_year+period_gap,
                     
                      })
                     )
 
   return period_params


def generate_horizon_params(start_year,subproblem,month,day,linkage_option):

   horizon_day=[]
   horizon_month=[]
   horizon_year=[]
   for i in start_year: 
       
    if subproblem=='capacity_expansion':
         subproblem_id=1
    elif subproblem=='production_cost':
         subproblem_id=i+1
            
    tmp_year="%d" % i   
    tmp_horizon_year=tmp_year
    horizon_year.append( {'subproblem_id' : subproblem_id,
                          'balancing_type_horizon' : 'year',
                          'horizon' : tmp_horizon_year,
                          'boundary' : linkage_option
                              }
                              )     
    for j in range(month):
        if subproblem=='capacity_expansion':
            subproblem_id=1
        elif subproblem=='production_cost':
            subproblem_id=j+1
        tmp_month="%02d" % (j+1)
        tmp_horizon_month=tmp_year+tmp_month
        horizon_month.append({'subproblem_id' : subproblem_id,
                              'balancing_type_horizon' : 'month',
                              'horizon' : tmp_horizon_month,
                              'boundary' : linkage_option
                              }
                              )
        for k in range(day[j]):   
            if subproblem=='capacity_expansion':
                subproblem_id=1
            elif subproblem=='production_cost':
                subproblem_id=k+1
            
            tmp_day="%02d" % (k+1)
            tmp_horizon_day=tmp_year+tmp_month+tmp_day
            horizon_day.append({'subproblem_id' : subproblem_id,
                              'balancing_type_horizon' : 'day',
                              'horizon' : tmp_horizon_day,
                              'boundary' : linkage_option
                             }
                             )
    if linkage_option in ["linkage", "linear"]:
        horizon_day[0]['boundary']="circular" 
        horizon_month[0]['boundary']="circular"   
        
   horizon=horizon_year+horizon_month+horizon_day
   fields=['subproblem_id','balancing_type_horizon','horizon','boundary']
   horizon_params=DataFrame(horizon,columns=fields)
   
   return horizon_params

def generate_horizon_timepoint(timepoint_option,horizon_params,stage_option,day):

 timepoint=np.arange(0,24,24/timepoint_option)
 timepoint1="%02d" % timepoint[0]
 timepoint2="%02d" % timepoint[-1]

                              
 horizon_timepoints=[]

 for i in range(stage_option):
   for j in range(len(horizon_params)):
     if horizon_params.loc[j,'balancing_type_horizon'] in 'day':
      tmp_start=int(str(horizon_params.loc[j,'horizon'])+timepoint1)
      tmp_end=int(str(horizon_params.loc[j,'horizon'])+timepoint2)
   
      horizon_timepoints.append({'subproblem_id' : horizon_params.loc[j,'subproblem_id'],
                              'stage_id' : i+1,
                              'balancing_type_horizon' : horizon_params.loc[j,'balancing_type_horizon'],
                              'horizon' : horizon_params.loc[j,'horizon'],
                              'tmp_start' : tmp_start,
                              'tmp_end': tmp_end}
                              )
     
     if horizon_params.loc[j,'balancing_type_horizon'] in 'month':
      month_tmp=str(horizon_params.loc[j,'horizon'])
      day_start=1
      day_end=day[int(month_tmp[-2:])-1]
      day_start_tmp="%02d" % day_start
      day_end_tmp="%02d" % day_end
            
      tmp_start=int(month_tmp+day_start_tmp+timepoint1)
      tmp_end=int(month_tmp+day_end_tmp+timepoint2)
      
      horizon_timepoints.append({'subproblem_id' : horizon_params.loc[j,'subproblem_id'],
                              'stage_id' : i+1,
                              'balancing_type_horizon' : horizon_params.loc[j,'balancing_type_horizon'],
                              'horizon' : horizon_params.loc[j,'horizon'],
                              'tmp_start' : tmp_start,
                              'tmp_end': tmp_end}
                              )
      
     if horizon_params.loc[j,'balancing_type_horizon'] in 'year':
      year_tmp=str(horizon_params.loc[j,'horizon'])
      day_start=1
      day_end=day[-1]
      day_start_tmp="%02d" % day_start
      day_end_tmp="%02d" % day_end
      month_tmp_start="%02d" % 1
      month_tmp_end="%02d" % 12
            
      tmp_start=int(year_tmp+month_tmp_start+day_start_tmp+timepoint1)
      tmp_end=int(year_tmp+month_tmp_end+day_end_tmp+timepoint2)
      horizon_timepoints.append({'subproblem_id' : horizon_params.loc[j,'subproblem_id'],
                                 'stage_id' : i+1,
                                 'balancing_type_horizon' : horizon_params.loc[j,'balancing_type_horizon'],
                                 'horizon' : horizon_params.loc[j,'horizon'],
                                 'tmp_start' : tmp_start,
                                 'tmp_end': tmp_end}
                              ) 
 fields=['subproblem_id','stage_id','balancing_type_horizon','horizon','tmp_start','tmp_end']
 horizon_timepoints=DataFrame(horizon_timepoints,columns=fields)
      
 return horizon_timepoints





def generate_structure(timepoint_option,month,horizon_timepoints,horizon_params,period_params,stage_option,day_in_month,peak):
  structure=[]
  #period_start=[d['period_start_year'] for d in period_params], this is used for list
  period_start=period_params['period_start_year']

  for i in range(stage_option):
    
   for j in range(len(horizon_timepoints)):
      
    if 'day' in horizon_timepoints.loc[j,'balancing_type_horizon']:
                                       
      tmp_start=horizon_timepoints.loc[j,'tmp_start']
      tmp_end=horizon_timepoints.loc[j,'tmp_end']
      timepoint_weight=8760/(timepoint_option*sum(day_in_month))
      
      for k in arange(tmp_start,tmp_end+24/timepoint_option,24/timepoint_option):
       hour_of_day=k-tmp_start+1       
       day_str=str(int(k))       
       structure_day=int(day_str[-4:-2])
       structure_month=int(day_str[-6:-4])
       
       if peak==1:
           if structure_month in [1,3,5,7,8,10,12]: 
               if structure_day==1:
                timepoint_weight=30
               elif structure_day==2:
                timepoint_weight=1
           if structure_month in [4,6,9,11]:  
               if structure_day==1:
                timepoint_weight=29
               elif structure_day==2:
                timepoint_weight=1
           if structure_month in [2]:  
               if structure_day==1:
                timepoint_weight=27
               elif structure_day==2:
                timepoint_weight=1
           
           
           
       timepoints=int(k)
       #structure_perio=int(day_str[0:4])
       period_str=int(day_str[0:4])    
       structure_period = min([ii for ii in period_start if ii >= int(period_str)])
       
       previous_stage= ""
       spinup=0
       linked=""
       
       if i in range(1,2):
        previous_stage= timepoints
        spinup=0
       if 'linkage' in horizon_params.loc[j,'boundary'] and (j<month*day_in_month-1):
           if k==tmp_start and horizon_params.loc[j,'subproblem_id']!=horizon_params.loc[j+1,'subproblem_id']:
             linked=-1
       
       minute=0
       second=0
       
       structure_stamp=(structure_period,structure_month,structure_day,hour_of_day-1,minute,second)
       time_stamp='%04d/%02d/%02d %02d:%02d:%02d' % structure_stamp



       structure.append({'subproblem_id': horizon_timepoints.loc[j,'subproblem_id'],
                         'stage_id': i+1,
                         'timepoint': timepoints,
                         'period': structure_period,
                         'number_of_hours_in_timepoint': 24/timepoint_option,
                         'timepoint_weight': timepoint_weight,
                         'previous_stage_timepoint_map' : previous_stage,
                         'spinup_or_lookahead': spinup,
                         'linked_timepoint': linked,
                         'month': structure_month,
                         'hour_of_day': hour_of_day,
                         'timestamp': time_stamp,
                               })
       
  fields=['subproblem_id',
          'stage_id',
          'timepoint',
          'period',
          'number_of_hours_in_timepoint',
          'timepoint_weight',
          'previous_stage_timepoint_map',
          'spinup_or_lookahead',
          'linked_timepoint',
          'month',
          'hour_of_day',
          'timestamp']
  
  structure=DataFrame(structure,columns=fields)
  return structure



def generate_horizon_params_select(start_year,subproblem,dayth_in_month,linkage_option):

   horizon_day=[]
   horizon_month=[]
   horizon_year=[]
   for i in start_year: 
       
    if subproblem=='capacity_expansion':
         subproblem_id=1
    elif subproblem=='production_cost':
         subproblem_id=i+1
            
    tmp_year="%d" % i   
    tmp_horizon_year=tmp_year
    horizon_year.append( {'subproblem_id' : subproblem_id,
                          'balancing_type_horizon' : 'year',
                          'horizon' : tmp_horizon_year,
                          'boundary' : linkage_option
                              }
                              )     
    for j in list(dayth_in_month):
        if subproblem=='capacity_expansion':
            subproblem_id=1
        elif subproblem=='production_cost':
            subproblem_id=j+1
        tmp_month="%02d" % j
        tmp_horizon_month=tmp_year+tmp_month
        horizon_month.append({'subproblem_id' : subproblem_id,
                              'balancing_type_horizon' : 'month',
                              'horizon' : tmp_horizon_month,
                              'boundary' : linkage_option
                              }
                              )
        for k in dayth_in_month[j]:   
            if subproblem=='capacity_expansion':
                subproblem_id=1
            elif subproblem=='production_cost':
                subproblem_id=k+1
            
            tmp_day="%02d" % k
            tmp_horizon_day=tmp_year+tmp_month+tmp_day
            horizon_day.append({'subproblem_id' : subproblem_id,
                              'balancing_type_horizon' : 'day',
                              'horizon' : tmp_horizon_day,
                              'boundary' : linkage_option
                             }
                             )
    if linkage_option in ["linkage", "linear"]:
        horizon_day[0]['boundary']="circular" 
        horizon_month[0]['boundary']="circular"   
        
   horizon=horizon_year+horizon_month+horizon_day
   fields=['subproblem_id','balancing_type_horizon','horizon','boundary']
   horizon_params=DataFrame(horizon,columns=fields)
   
   return horizon_params

def generate_horizon_timepoint_select(timepoint_option,horizon_params,stage_option,dayth_in_month):

 timepoint=np.arange(0,24,24/timepoint_option)
 timepoint1="%02d" % timepoint[0]
 timepoint2="%02d" % timepoint[-1]

                              
 horizon_timepoints=[]

 for i in range(stage_option):
   for j in range(len(horizon_params)):
     if horizon_params.loc[j,'balancing_type_horizon'] in 'day':
      tmp_start=int(str(horizon_params.loc[j,'horizon'])+timepoint1)
      tmp_end=int(str(horizon_params.loc[j,'horizon'])+timepoint2)
   
      horizon_timepoints.append({'subproblem_id' : horizon_params.loc[j,'subproblem_id'],
                              'stage_id' : i+1,
                              'balancing_type_horizon' : horizon_params.loc[j,'balancing_type_horizon'],
                              'horizon' : horizon_params.loc[j,'horizon'],
                              'tmp_start' : tmp_start,
                              'tmp_end': tmp_end}
                              )
     
     if horizon_params.loc[j,'balancing_type_horizon'] in 'month':
      month_tmp=str(horizon_params.loc[j,'horizon'])
      day_start=min(dayth_in_month[int(month_tmp[-2:])])
      day_end=max(dayth_in_month[int(month_tmp[-2:])])
      day_start_tmp="%02d" % day_start
      day_end_tmp="%02d" % day_end
            
      tmp_start=int(month_tmp+day_start_tmp+timepoint1)
      tmp_end=int(month_tmp+day_end_tmp+timepoint2)
      
      horizon_timepoints.append({'subproblem_id' : horizon_params.loc[j,'subproblem_id'],
                              'stage_id' : i+1,
                              'balancing_type_horizon' : horizon_params.loc[j,'balancing_type_horizon'],
                              'horizon' : horizon_params.loc[j,'horizon'],
                              'tmp_start' : tmp_start,
                              'tmp_end': tmp_end}
                              )
      
     if horizon_params.loc[j,'balancing_type_horizon'] in 'year':
      year_tmp=str(horizon_params.loc[j,'horizon'])
      day_start=min(dayth_in_month[list(dayth_in_month)[0]])
      day_end=max(dayth_in_month[list(dayth_in_month)[-1]])
      day_start_tmp="%02d" % day_start
      day_end_tmp="%02d" % day_end
      month_tmp_start="%02d" % 1
      month_tmp_end="%02d" % 12
            
      tmp_start=int(year_tmp+month_tmp_start+day_start_tmp+timepoint1)
      tmp_end=int(year_tmp+month_tmp_end+day_end_tmp+timepoint2)
      horizon_timepoints.append({'subproblem_id' : horizon_params.loc[j,'subproblem_id'],
                                 'stage_id' : i+1,
                                 'balancing_type_horizon' : horizon_params.loc[j,'balancing_type_horizon'],
                                 'horizon' : horizon_params.loc[j,'horizon'],
                                 'tmp_start' : tmp_start,
                                 'tmp_end': tmp_end}
                              ) 
 fields=['subproblem_id','stage_id','balancing_type_horizon','horizon','tmp_start','tmp_end']
 horizon_timepoints=DataFrame(horizon_timepoints,columns=fields)
      
 return horizon_timepoints


def generate_structure_select(timepoint_option,horizon_timepoints,horizon_params,period_params,stage_option,dayth_in_month,peak):
  structure=[]
  #period_start=[d['period_start_year'] for d in period_params], this is used for list
  period_start=period_params['period_start_year']

  for i in range(stage_option):
    
   for j in range(len(horizon_timepoints)):
      
    if 'day' in horizon_timepoints.loc[j,'balancing_type_horizon']:
                                       
      tmp_start=horizon_timepoints.loc[j,'tmp_start']
      tmp_end=horizon_timepoints.loc[j,'tmp_end']
      
      number_day=sum(len(v) for v in dayth_in_month.values())
      
      timepoint_weight=8760/(timepoint_option*number_day)
      
      if peak==1:
          if j%2==1:
             timepoint_weight=(8760)/12/24*2/7
          if j%2==0:
             timepoint_weight=(8760)/12/24*5/7
      
      
      for k in arange(tmp_start,tmp_end+24/timepoint_option,24/timepoint_option):
       hour_of_day=k-tmp_start+1       
       day_str=str(int(k))       
       structure_day=int(day_str[-4:-2])
       structure_month=int(day_str[-6:-4])
       
           
       timepoints=int(k)
       #structure_perio=int(day_str[0:4])
       period_str=int(day_str[0:4])    
       structure_period = min([ii for ii in period_start if ii >= int(period_str)])
       
       previous_stage= ""
       spinup=0
       linked=""
       
       minute=0
       second=0
       
       structure_stamp=(structure_period,structure_month,structure_day,hour_of_day-1,minute,second)
       time_stamp='%04d/%02d/%02d %02d:%02d:%02d' % structure_stamp



       structure.append({'subproblem_id': horizon_timepoints.loc[j,'subproblem_id'],
                         'stage_id': i+1,
                         'timepoint': timepoints,
                         'period': structure_period,
                         'number_of_hours_in_timepoint': 24/timepoint_option,
                         'timepoint_weight': timepoint_weight,
                         'previous_stage_timepoint_map' : previous_stage,
                         'spinup_or_lookahead': spinup,
                         'linked_timepoint': linked,
                         'month': structure_month,
                         'hour_of_day': hour_of_day,
                         'timestamp': time_stamp,
                               })
       
  fields=['subproblem_id',
          'stage_id',
          'timepoint',
          'period',
          'number_of_hours_in_timepoint',
          'timepoint_weight',
          'previous_stage_timepoint_map',
          'spinup_or_lookahead',
          'linked_timepoint',
          'month',
          'hour_of_day',
          'timestamp']
  
  structure=DataFrame(structure,columns=fields)
  return structure
