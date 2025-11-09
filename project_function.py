# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 17:49:53 2021

@author: haozheyang
"""
from pandas import DataFrame, Series, concat, read_csv
import pandas as pd
import numpy as np
import glob

def generate_project_portfolio(cluster,ccs_option):
    project_portofolio=[]
    generator=cluster['project']
    for i in generator:
        index=cluster[generator==i].index
        gen_type=cluster.loc[index,'technology']
        gen_dbid=cluster.loc[index,'gen_dbid']
        
        if gen_dbid.values[0]=='existing':
            gen_type_tmp='gen_spec'
            if (gen_type.values[0]=='Battery_Storage'):
                gen_type_tmp='stor_spec'
            if (gen_type.values[0]=='Hydro_Pumped'):
                gen_type_tmp='stor_spec'
        if gen_dbid.values[0]=='new':
            gen_type_tmp='gen_new_lin'
            if gen_type.values[0]=='Battery_Storage':
                gen_type_tmp='stor_new_lin'
            if gen_type.values[0]=='Hydro_Pumped':
                gen_type_tmp='stor_new_lin'
            if (gen_type.values[0]=='Salt_cavern') | (gen_type.values[0]=='Tank'):
                gen_type_tmp='stor_new_lin'
                
        if ccs_option==1:
            if gen_type.values[0] in ['Coal','Gas','SMR','Gasification','Coal_IGCC','Gas_CCGT']:
                if gen_dbid.values[0]=="existing":
                    gen_type_tmp= 'gen_ccs_spec'
                if gen_dbid.values[0]=="new":
                    gen_type_tmp= 'gen_ccs_new'
            if gen_type.values[0] in ['CCS_storage_oil','CCS_storage_saline','CCS_storage_offshore','DAC']:
                gen_type_tmp='stor_ccs_new_lin'
                
            
        project_portofolio.append({'project': i,
                                   'specified': "",
                                   'new_build': "",
                                   'capacity_type':gen_type_tmp                               
                                   }
                                  )
    fields=['project','specified','new_build','capacity_type']
    project_portofolio=DataFrame(project_portofolio,columns=fields)
    return project_portofolio

def generate_project_cap_group(cluster):
    
    project_cap_group=[]
    generator=cluster['project']
    Resource=cluster['capacity_group']
    for i in generator:
            index=generator[generator==i].index[0]
            cap_tmp=Resource.loc[index]
            project_cap_group.append({'project': i,
                                      'capacity_group': cap_tmp                              
                                      }
                                     )
            
    fields=['capacity_group','project']
    project_cap_group=DataFrame(project_cap_group,columns=fields)
    return project_cap_group


def generate_availability_type(cluster,exogenous_availability_scenario_id):
    availability_type=Series(['exogenous' for i in range(len(cluster))])
    generator=cluster['project']
    exogenous_availability_scenario_id=Series([exogenous_availability_scenario_id for i in range(len(cluster))])
    endogenous_availability_scenario_id=Series(["" for i in range(len(cluster))])
            
    project_availability_type=DataFrame({'project': generator,
                                         'availability_type': availability_type,
                                         'exogenous_availability_scenario_id': exogenous_availability_scenario_id,
                                         'endogenous_availability_scenario_id': endogenous_availability_scenario_id
                                         }
                                        )
    return project_availability_type



def generate_availability_endogenous(path,endogenous_availability_scenario,scenario_description,
                                      endogenous,binary,continuous,
                                      unavailable_hours_per_period,available_hours_per_event_min, available_hours_between_events_min):
    availability_endogeous=[]
    project_availability_endogenous=DataFrame({'unavailable_hours_per_period': unavailable_hours_per_period,
                                               'available_hours_per_event_min': available_hours_per_event_min,	
                                               'available_hours_between_events_min': available_hours_between_events_min
                                               },
                                              index=range(3)
                                              )
    if 'binary' in endogenous:
        for i in binary:
            rp=i+'-'+str(endogenous_availability_scenario)+'-'+scenario_description
            filename=path+i+'-'+str(endogenous_availability_scenario)+'-'+scenario_description+'.csv'    
            project_availability_endogenous.to_csv(filename, index=False)
            availability_endogeous.append({'file': rp})
    
    if 'continous' in endogenous:
        for i in continuous:
            rp=i+'-'+str(endogenous_availability_scenario)+'-'+scenario_description
            filename=path+rp+'.csv'    
            project_availability_endogenous.to_csv(filename, index=False)
            availability_endogeous.append({'file': rp})
    
    return availability_endogeous


def generate_availability_exogenous(cluster,derate_group,group,timepoints,exogenous_availability_scenario,scenario_description,share_path):
    
    exogenous=cluster.loc[cluster['capacity_group'].isin(derate_group['tech']),:]
    cap=exogenous['capacity_group']
    generator=exogenous['project']
    outage=exogenous['gen_scheduled_outage_rate']+exogenous['gen_forced_outage_rate']

    for i in range(len(exogenous)):
        project_availability_exogenous=DataFrame()
        availability_derate=1-outage.iloc[i]
        if cap.iloc[i] in group:
          availability_derate=derate_group.loc[derate_group['tech']==cap.iloc[i],'derate'].values[0]

        project_availability_exogenous=DataFrame({
                                                    'stage_id': 1,
                                                    'timepoint' :timepoints,
                                                    'availability_derate': availability_derate
                                                    }) 
        #project_availability_exogenous=concat([project_availability_exogenous,project_availability_exogenous_tmp])     
        rp=generator.iloc[i]+'-'+str(exogenous_availability_scenario)+'-'+scenario_description
        filename=share_path+'project_availability/'+'project_availability_exogenous/'+rp+'.csv'    
        project_availability_exogenous.to_csv(filename, index=False)
        #availability_exogeous.append({'file':rp})
    #return availability_exogeous

def generate_heat_rate_curve(heat_scenario,heat_scenario_description,cluster,share_path):
   heat_rate_file=[]
   fuel_gen=[i in ['group_coal','group_gas','group_nuclear','group_H2'] for i in cluster['capacity_group']]
   
   cluster_heat=cluster.loc[fuel_gen,:]
   generator=cluster_heat['project']
   heat_rate_full=cluster_heat['gen_full_load_heat_rate'].astype(float)
   #heat_rate_04=cluster_heat['gen_04_load_heat_rate'].astype(float)
   #capacity_group=cluster_heat['capacity_group']
   for i in range(len(cluster_heat)):
       power_station=generator.iloc[i]
       heatrate_full_tmp=heat_rate_full.iloc[i]
       
       project_heat_rate=DataFrame({'period': [0]	,
                                     'load_point_fraction':[1],
                                     'average_heat_rate_mmbtu_per_mwh': [heatrate_full_tmp]
                                     })       
           
       rp=power_station+'-'+str(heat_scenario)+'-'+heat_scenario_description
       path_to_file=share_path+'project_heat_rate_curves/'+rp+'.csv'
       project_heat_rate.to_csv(path_to_file,index=False)
       heat_rate_file.append({'file':rp})
 
   return heat_rate_file

def generate_hydro_operation_chars(cluster,hydro_profile,hydro_oper_scenario_id,horizon):
    horizon_day=horizon.loc[horizon['balancing_type_horizon']=='day','horizon'].reset_index()
    hydro=cluster.loc[cluster['capacity_group']=='group_hydro',:]    
    hydro_gen=hydro['project']
    hydro_zone=hydro['zone']
    n=int(len(horizon_day)/len(hydro_profile['Anhui']))
    hydro_op_file=[]
    for i in range(len(hydro)):
        gen=hydro_gen.iloc[i]
        zone=hydro_zone.iloc[i]
        rp=gen+'-'+str(hydro_oper_scenario_id)+'-'+'project_hydro_operational_chars.csv'
        path_hydro_op='project/project_hydro_operational_chars/'+rp       
        project_hydro_operation_chars=concat([hydro_profile[zone]]*n,axis=0,ignore_index=True)
        project_hydro_operation_chars['horizon']=horizon_day['horizon']
        project_hydro_operation_chars['period']=[int(k[0:4]) for k in horizon_day['horizon'].astype(str)]
        project_hydro_operation_chars.to_csv(path_hydro_op,index=False)
        hydro_op_file.append({'file':rp})
    return hydro_op_file


def generate_hydro_operation_chars_full(cluster,hydro_oper_scenario_id,horizon,share_path):
    horizon_day=horizon.loc[horizon['balancing_type_horizon']=='day','horizon']
    period=horizon_day.astype(str).str[0:4].astype(int) 
    hydro_project=cluster.loc[cluster.technology=='Hydro_NonPumped','project']
    hydro_op_file=[]
   
    for i in hydro_project:    
        file_id='C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/project/project_hydro_operational_chars/'+i+'-1-project_hydro_operational_chars.csv'
        hydro_month=pd.read_csv(file_id)
        ratio=hydro_month['average_power_fraction']
        ratio_min=hydro_month['min_power_fraction']
        ratio_max=hydro_month['max_power_fraction']
        
        t=[31,28,31,30,31,30,31,31,30,31,30,31]
        ratio2=[]
        ratio_min2=[]
        ratio_max2=[]
        
        for j in range(0,12):
            ratio_tmp=np.repeat(ratio.values[j],t[j])
            ratio_min_tmp=np.repeat(ratio_min.values[j],t[j])
            ratio_max_tmp=np.repeat(ratio_max.values[j],t[j])
            ratio2.extend(ratio_tmp)
            ratio_min2.extend(ratio_min_tmp)
            ratio_max2.extend(ratio_max_tmp)
            
        
        gen=i.split('\\')[-1].split('-')[0]
        
        rp=gen+'-'+str(hydro_oper_scenario_id)+'-'+'project_hydro_operational_chars.csv'
        path_hydro_op=share_path+'project_hydro_operational_chars/'+rp       

        project_hydro_operation_chars=pd.DataFrame({
        'balancing_type_project':'day',
        'horizon':horizon_day,
        'period': period,
        'average_power_fraction':np.tile(ratio2,len(horizon.loc[horizon.balancing_type_horizon=='year','horizon'])),
        'min_power_fraction': np.tile(ratio_min2,len(horizon.loc[horizon.balancing_type_horizon=='year','horizon'])),
        'max_power_fraction': np.tile(ratio_max2,len(horizon.loc[horizon.balancing_type_horizon=='year','horizon']))
        })
        project_hydro_operation_chars.to_csv(path_hydro_op,index=False)
        hydro_op_file.append({'file':rp})
    return hydro_op_file

def generate_load_zone(cluster):
    project_load_zone=DataFrame({'project':cluster['project'],
                                 'load_zone':cluster['zone']})
    
    return project_load_zone

def generate_carbon_cap_load_zone(cluster):
    group=['group_coal','group_gas','group_nuclear','group_H2','group_dac']
    carbon_cap_load_zone=DataFrame({'project':cluster.loc[cluster['capacity_group'].isin(group),'project'],
                                   'carbon_cap_zone':cluster.loc[cluster['capacity_group'].isin(group),'zone']})
    
    carbon_cap_load_zone=DataFrame({'project':cluster.loc[cluster['capacity_group'].isin(group),'project'],
                                   'carbon_cap_zone':'China'})
        
    return carbon_cap_load_zone

def generate_new_cost(cluster,capital_cost,lifetime,fixed_cost):
    technology=cluster.loc[cluster['gen_dbid']=="new",'technology']
    generator=cluster.loc[cluster['gen_dbid']=="new",'project']
    #zone=cluster.loc[cluster['gen_dbid']=="new",'zone']
    project_new_cost=pd.DataFrame()
    for i in range(len(technology)):
        tech_tmp=technology.iloc[i]
        cost_tmp=capital_cost[tech_tmp]+fixed_cost[tech_tmp]
        cost_mwh_tmp=[0 for j in range(len(cost_tmp))]
        cost_tonne_tmp=[0 for j in range(len(cost_tmp))]
        
        lifetime_tmp=lifetime[tech_tmp]
        '''
        zone_tmp=zone.iloc[i]
        if tech_tmp=='Offshore_Wind':
            cost_tmp=offshore[zone_tmp]+fixed_offshore[zone_tmp]
        '''
        if tech_tmp=='Battery_Storage':
            cost_mwh_tmp=capital_cost['Battery_Storage_energy']
            
        if tech_tmp in ['Salt_cavern','Tank']:
            cost_mwh_tmp=cost_tmp
            cost_tmp=0
            
        if tech_tmp in ['Coal','Coal_IGCC','Gas_Combustion_Turbine','Gas_CCGT','SMR','Gasification']:
            cost_tonne_tmp=capital_cost[tech_tmp+'_CCS']+fixed_cost[tech_tmp+'_CCS']
            
        if tech_tmp in ['CCS_storage_oil','CCS_storage_saline','CCS_storage_offshore','DAC']:
            cost_tonne_tmp=cost_tmp
            cost_tmp=0                        
            cost_mwh_tmp=0
            
        project_new_cost=project_new_cost.append(DataFrame({
            'project': generator.iloc[i],
            'vintage': capital_cost['Vintage'],
            'ccs_lifetime_yrs':lifetime_tmp,
            'lifetime_yrs': lifetime_tmp,
            'annualized_real_cost_per_mw_yr': cost_tmp,
            'annualized_real_cost_per_mwh_yr': cost_mwh_tmp,
            'annualized_real_cost_per_tonne_yr': cost_tonne_tmp,
            'levelized_cost_per_mwh': "",
            'supply_curve_scenario_id':""
            }))
        
    return project_new_cost

def generate_fixed_cost(cluster,fixed_cost,capital_cost):
    technology=cluster.loc[cluster.gen_dbid=='existing','technology'].str.replace('_EP','')
    generator=cluster.loc[cluster.gen_dbid=='existing','project']
    group=cluster.loc[cluster.gen_dbid=='existing','capacity_group']
    #zone=cluster['zone']
    project_fixed_cost=DataFrame()
    for i in range(len(technology)):
        tech_tmp=technology.iloc[i]
        cost_tmp=fixed_cost[tech_tmp]
        '''
        zone_tmp=zone.iloc[i]
        if tech_tmp=='Offshore_Wind':
            cost_tmp=offshore[zone_tmp]
        '''  
        project_tmp=DataFrame({
            'project': [generator.iloc[i] for j in range(len(cost_tmp))],
            'period': fixed_cost['Vintage'],
            'fixed_cost_per_mw_year': cost_tmp,
            'hyb_gen_fixed_cost_per_mw_yr': ["" for j in range(len(cost_tmp))],
            'hyb_stor_fixed_cost_per_mw_yr':["" for j in range(len(cost_tmp))],
            'fixed_cost_per_mwh_year':["" for j in range(len(cost_tmp))],
            'ccs_fixed_cost_per_tonne_year': ["" for j in range(len(cost_tmp))]
            })
        if tech_tmp=='Hydro_Pumped':
            project_tmp['fixed_cost_per_mwh_year']=0
            
        if group.iloc[i] in ['group_coal','group_gas']:
            cost_tonne_tmp=capital_cost[tech_tmp+'_CCS']+fixed_cost[tech_tmp+'_CCS']
            project_tmp=DataFrame({
            'project': [generator.iloc[i] for j in range(len(cost_tmp))],
            'period': fixed_cost['Vintage'],
            'fixed_cost_per_mw_year': cost_tmp,
            'hyb_gen_fixed_cost_per_mw_yr': ["" for j in range(len(cost_tmp))],
            'hyb_stor_fixed_cost_per_mw_yr':["" for j in range(len(cost_tmp))],
            'fixed_cost_per_mwh_year':["" for j in range(len(cost_tmp))],
            'ccs_fixed_cost_per_tonne_year': cost_tonne_tmp
            })
    
        project_fixed_cost=project_fixed_cost.append(project_tmp)
    return project_fixed_cost

def generate_new_potential(cluster,period,stop_build):
    generator=cluster.loc[cluster['gen_dbid']=="new",'project']
    max_mw=cluster.loc[cluster['gen_dbid']=="new",'gen_capacity_limit_mw']
    max_mw=max_mw.replace(0,"")
    capacity_group=cluster.loc[cluster['gen_dbid']=="new",'capacity_group']
    for i in range(len(capacity_group)):
        if capacity_group.iloc[i] in stop_build:
            max_mw.iloc[i]=0
        
    project_new_potential=DataFrame()
    for i in period:
        project_new_potential=project_new_potential.append(
            DataFrame({
                'project':generator,
                'period': [i for j in range(len(generator))],
                'min_cumulative_new_build_mw':["" for j in range(len(generator))],	
                'max_cumulative_new_build_mw':max_mw,
                'min_cumulative_new_build_mwh':["" for j in range(len(generator))],
                'max_cumulative_new_build_mwh':["" for j in range(len(generator))],
                'min_cumulative_new_build_tonne':["" for j in range(len(generator))],
                'max_cumulative_new_build_tonne':["" for j in range(len(generator))],
            })
            )
    
    return project_new_potential

def generate_operate_chars(cluster,var_scenario,ccs_option):
    template=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_test_examples_H2/project/project_operational_chars/1_project_operational_chars_2zones.csv').columns
    capacity_group=cluster['capacity_group']
    technology=cluster['technology']
    project_operate_chars=pd.DataFrame(columns=template)
    project_operate_chars['project']=cluster['project']
    project_operate_chars['balancing_type_project']='day'
    
    project_operate_chars['fuel']=cluster['fuel']
    project_operate_chars['variable_om_cost_per_mwh']=cluster['variable_om_cost_per_mwh'].replace("",0)
    
    project_operate_chars['variable_ccs_om_cost_per_tonne']=cluster['variable_ccs_om_cost_per_tonne']
    project_operate_chars['ccs_mwh_per_tonne']=cluster['ccs_mwh_per_tonne']
    project_operate_chars['ccs_efficiency']=cluster['ccs_efficiency']

    project_operate_chars['min_stable_level_fraction']=cluster['min_stable_level_fraction']
    project_operate_chars['charging_efficiency']=cluster['gen_storage_efficiency']**(1/2)    
    project_operate_chars['discharging_efficiency']=cluster['gen_storage_efficiency']**(1/2) 
    
    for i in range(len(project_operate_chars)):
        if capacity_group.loc[i]=='group_pv':
            project_operate_chars.loc[i,'technology']='Solar'
            project_operate_chars.loc[i,'operational_type']='gen_var'
            project_operate_chars.loc[i,'variable_generator_profile_scenario_id']=var_scenario
            project_operate_chars.loc[i,'variable_om_cost_per_mwh']=0
            
        if capacity_group.loc[i]=='group_wind':
            project_operate_chars.loc[i,'technology']=technology.loc[i]
            project_operate_chars.loc[i,'operational_type']='gen_var'
            project_operate_chars.loc[i,'variable_generator_profile_scenario_id']=var_scenario
            project_operate_chars.loc[i,'variable_om_cost_per_mwh']=0
            
        if capacity_group.loc[i]=='group_hydro':
            project_operate_chars.loc[i,'technology']='Hydro'
            project_operate_chars.loc[i,'operational_type']='gen_hydro'
            #project_operate_chars.loc[i,'variable_om_cost_per_mwh']=0
            project_operate_chars.loc[i,'hydro_operational_chars_scenario_id']=var_scenario
        
        if capacity_group.loc[i]=='group_battery':
            project_operate_chars.loc[i,'technology']='Battery'
            project_operate_chars.loc[i,'operational_type']='stor'
            project_operate_chars.loc[i,'minimum_duration_hours']=1
            project_operate_chars.loc[i,'maximum_duration_hours']=99
        
        if capacity_group.loc[i]=='group_PHS':
            project_operate_chars.loc[i,'technology']='Pumped_hydro'
            project_operate_chars.loc[i,'operational_type']='stor'
            project_operate_chars.loc[i,'maximum_duration_hours']=10
            project_operate_chars.loc[i,'variable_om_cost_per_mwh']=0.5125
            project_operate_chars.loc[i,'discharging_efficiency']=0.74**(1/2)
            project_operate_chars.loc[i,'charging_efficiency']=0.74**(1/2)
            
        if capacity_group.loc[i]=='group_g2p':
            
            project_operate_chars.loc[i,'operational_type']='gen_H2_ele'

            
            if technology.loc[i]=='Fuel_cell':
               project_operate_chars.loc[i,'technology']='Fuel_cell'
               project_operate_chars.loc[i,'discharging_efficiency']=0.6
            elif technology.loc[i] == 'Hydrogen_turbine':
               project_operate_chars.loc[i,'technology']='H2_turbine'
               project_operate_chars.loc[i,'discharging_efficiency']=0.4
               project_operate_chars.loc[i,'variable_om_cost_per_mwh']=3
               
        if capacity_group.loc[i]=='group_H2':
           
                project_operate_chars.loc[i,'operational_type']='gen_commit_cap_H2'
                project_operate_chars.loc[i,'unit_size_mw']=100
                project_operate_chars.loc[i,'heat_rate_curves_scenario_id']=1
                project_operate_chars.loc[i,'last_commitment_stage']=1
                project_operate_chars.loc[i,'technology']=technology.loc[i]
                project_operate_chars.loc[i,'min_stable_level_fraction']=0
                if ccs_option==1:
                    project_operate_chars.loc[i,'operational_type']='gen_commit_cap_H2_ccs'
        
        if capacity_group.loc[i]=='group_dac':
               project_operate_chars.loc[i,'technology']='DAC'
               project_operate_chars.loc[i,'operational_type']='dac'              
               
        if capacity_group.loc[i]=='group_p2g':
               project_operate_chars.loc[i,'charging_efficiency']=0.7
               project_operate_chars.loc[i,'technology']='Electrolyzer'
               project_operate_chars.loc[i,'operational_type']='gen_H2'
               project_operate_chars.loc[i,'unit_size_mw']=100

        if capacity_group.loc[i]=='group_underground':
            project_operate_chars.loc[i,'technology']='Salt_cavern'
            project_operate_chars.loc[i,'operational_type']='stor_H2'
            project_operate_chars.loc[i,'balancing_type_project']='year'
            project_operate_chars.loc[i,'charging_efficiency']=0.99
            project_operate_chars.loc[i,'discharging_efficiency']=1
            project_operate_chars.loc[i,'minimum_duration_hours']=0
            project_operate_chars.loc[i,'maximum_duration_hours']=1440
            
        if capacity_group.loc[i]=='group_tank':
            project_operate_chars.loc[i,'technology']='Tank'
            project_operate_chars.loc[i,'operational_type']='stor_H2'
            project_operate_chars.loc[i,'balancing_type_project']='year'
            project_operate_chars.loc[i,'charging_efficiency']=0.9
            project_operate_chars.loc[i,'discharging_efficiency']=1
            project_operate_chars.loc[i,'minimum_duration_hours']=0
            project_operate_chars.loc[i,'maximum_duration_hours']=1440
            
        if capacity_group.loc[i]=='group_coal':
            project_operate_chars.loc[i,'technology']='Coal'
            project_operate_chars.loc[i,'operational_type']='gen_commit_cap'
            #project_operate_chars.loc[i,'fuel']='Coal'
            project_operate_chars.loc[i,'fuel']='Coal'+'_'+cluster.loc[i,'zone'] #region specific coal price
            project_operate_chars.loc[i,'startup_plus_ramp_up_rate']=0.3	
            project_operate_chars.loc[i,'shutdown_plus_ramp_down_rate']=0.3	
            project_operate_chars.loc[i,'ramp_up_when_on_rate']=0.3	
            project_operate_chars.loc[i,'ramp_down_when_on_rate']=0.3

        if capacity_group.loc[i]=='group_gas':
            project_operate_chars.loc[i,'technology']='Gas'
            project_operate_chars.loc[i,'operational_type']='gen_commit_cap'
            project_operate_chars.loc[i,'fuel']='Gas'
            project_operate_chars.loc[i,'startup_plus_ramp_up_rate']=0.6	
            project_operate_chars.loc[i,'shutdown_plus_ramp_down_rate']=0.6	
            project_operate_chars.loc[i,'ramp_up_when_on_rate']=0.6
            project_operate_chars.loc[i,'ramp_down_when_on_rate']=0.6
            
        if capacity_group.loc[i]=='group_nuclear':
            project_operate_chars.loc[i,'technology']='Nuclear'
            project_operate_chars.loc[i,'operational_type']='gen_must_run' 
            project_operate_chars.loc[i,'fuel']='Uranium'
            
        if capacity_group.loc[i] in ['group_coal','group_gas']:
            project_operate_chars.loc[i,'unit_size_mw']=cluster.loc[i,'capacity']
            project_operate_chars.loc[i,'startup_cost_per_mw']=0
            project_operate_chars.loc[i,'shutdown_cost_per_mw']=0
            if ccs_option==1:
                project_operate_chars.loc[i,'operational_type']='gen_commit_cap_ccs'
                
        if capacity_group.loc[i] in ['group_coal','group_gas','group_nuclear']: 
            project_operate_chars.loc[i,'heat_rate_curves_scenario_id']=1
            project_operate_chars.loc[i,'last_commitment_stage']=1
            
        if capacity_group.loc[i]=='group_ccs_storage':
            project_operate_chars.loc[i,'technology']=technology.loc[i]
            project_operate_chars.loc[i,'operational_type']='stor_ccs'
            
    return project_operate_chars

def generate_specified_capacity(cluster,period):
    generator=cluster.loc[cluster['gen_dbid']=='existing','project']
    capacity_group=cluster.loc[cluster['gen_dbid']=='existing','capacity_group']
    #retire=cluster.loc[cluster['gen_dbid']=='existing','retire_year_y']
    project_specified_capacity=DataFrame()
    for i in period:
        capacity_tmp=cluster.loc[cluster['gen_dbid']=='existing','period_'+str(i)]
        #capacity_tmp[retire<i]=0
        project_tmp=DataFrame({
                                    'project':generator,
                                    'period': [i for j in range(len(capacity_tmp))],
                                    'specified_capacity_mw': capacity_tmp,	
                                    'hyb_gen_specified_capacity_mw': "",	
                                    'hyb_stor_specified_capacity_mw': "",	
                                    'specified_capacity_mwh': ""
                            })
        
        project_tmp.loc[capacity_group[capacity_group=='group_battery'].index,'specified_capacity_mwh']=4*project_tmp.loc[capacity_group[capacity_group=='group_battery'].index,'specified_capacity_mw']
        project_tmp.loc[capacity_group[capacity_group=='group_PHS'].index,'specified_capacity_mwh']=10*project_tmp.loc[capacity_group[capacity_group=='group_PHS'].index,'specified_capacity_mw']

        project_specified_capacity=project_specified_capacity.append(project_tmp)
        
    return project_specified_capacity




def generate_variable_generator_profile(cluster,scenario_id,description,timepoints):    
    generator=cluster.loc[cluster.capacity_group.isin (['group_pv','group_wind']),'project']
    zone=cluster.loc[cluster.capacity_group.isin (['group_pv','group_wind']),'zone']
    month=np.repeat([1,2,3,4,5,6,7,8,9,10,11,12],48)
    day=np.tile(np.repeat([1,2],24),12)
    hour=np.tile(np.arange(0,24),24)
    for i in range(len(generator)):
        f=generator.iloc[i]
        rp=f+'-'+str(scenario_id)+'-'+description
        name_variable='project/project_variable_generator_profiles/'+rp+'.csv'
        project_variable=DataFrame()
        project_variable['stage_id']=[1 for k in range(len(timepoints))]
        project_variable['timepoint']=timepoints
        
        
        if 'PV' in f:
            solar_variable=read_csv('Renewables/'+zone.iloc[i]+'_'+'Solar.csv').groupby(['Month','Period'])['Value'].mean().reset_index()
            n=int(len(timepoints)/len(solar_variable))
            project_variable['cap_factor']=np.tile(solar_variable['Value'],n)
        if 'Offshore' in f:
            offshore=read_csv('Renewables/'+zone.iloc[i]+'_'+'Offshore_Wind.csv')['cap_factor'][0:576]
            offshore=pd.DataFrame(offshore)
            offshore['month']=month
            offshore['day']=day
            offshore['hour']=hour
            offshore_tmp=offshore.groupby(['month','hour'])['cap_factor'].mean().reset_index()
            n=int(len(timepoints)/len(offshore_tmp))
            project_variable['cap_factor']=np.tile(offshore_tmp['cap_factor'],n)
        elif 'Wind' in f:
            wind_variable=read_csv('Renewables/'+zone.iloc[i]+'_'+'Wind.csv').groupby(['Month','Period'])['Value'].mean().reset_index()
            n=int(len(timepoints)/len(wind_variable))
            project_variable['cap_factor']=np.tile(wind_variable['Value'],n)
        project_variable.to_csv(name_variable,index=False)
   
def generate_variable_generator_profile_full(cluster,scenario_id,description,timepoints,share_path):    
    generator=cluster.loc[cluster.project.str.contains ('Wind|PV',regex=True),'project']
    zone=cluster.loc[cluster.project.str.contains ('Wind|PV',regex=True),'zone']
    month=np.repeat([1,2,3,4,5,6,7,8,9,10,11,12],48)
    day=np.tile(np.repeat([1,2],24),12)
    hour=np.tile(np.arange(0,24),24)
    
    for i in range(len(generator)):
        f=generator.iloc[i]
        rp=f+'-'+str(scenario_id)+'-'+description
        name_variable='project_variable_generator_profiles/'+rp+'.csv'
        project_variable=DataFrame()
        project_variable['stage_id']=[1 for k in range(len(timepoints))]
        project_variable['timepoint']=timepoints
        
        if 'PV' in f:
            solar_variable=read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/Renewables/'+zone.iloc[i]+'_'+'Solar.csv').groupby(['Month','Day','Period'])['Value'].mean().reset_index()
            n=int(len(timepoints)/len(solar_variable))
            project_variable['cap_factor']=np.tile(solar_variable['Value'],n)

        if 'Wind' in f:
            wind_variable=read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/Renewables/'+zone.iloc[i]+'_'+'Wind.csv').groupby(['Month','Day','Period'])['Value'].mean().reset_index()
            n=int(len(timepoints)/len(wind_variable))
 
            year_average=wind_variable['Value'].mean()
            if 'Offshore_Wind' in f:
                capacity_factor=0.4
                if zone.iloc[i]=='Fujian':
                    capacity_factor=1389.8/308.8/8760*1000
                if zone.iloc[i]=='Guangdong':
                    capacity_factor=1584.4/499.3/8760*1000
                if zone.iloc[i]=='Guangxi':
                    capacity_factor=310.3/111.7/8760*1000                    
                if zone.iloc[i]=='Hainan':
                    capacity_factor=1227/377.3/8760*1000   
                if zone.iloc[i]=='Hebei':
                    capacity_factor=397.2/122.4/8760*1000 
                if zone.iloc[i]=='Jiangsu':
                    capacity_factor=1543.7/462.7/8760*1000 
                if zone.iloc[i]=='Liaoning':
                    capacity_factor=1336.6/369.5/8760*1000 
                if zone.iloc[i]=='Shandong':
                    capacity_factor=2334.8/697.0/8760*1000 
                if zone.iloc[i]=='Zhejiang':
                    capacity_factor=1725.6/440.5/8760*1000                     
                    
                    
                #offshore=read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/Renewables/'+zone.iloc[i]+'_'+'Offshore_Wind.csv')['cap_factor'][0:576]
                #offshore=pd.DataFrame(offshore)
                wind_variable=wind_variable*capacity_factor/year_average
                #offshore['month']=month
                #offshore['day']=day
                #offshore['hour']=hour
                #offshore_tmp=offshore.groupby(['month','hour'])['cap_factor'].mean().reset_index()
                #offshore_tmp2=DataFrame()
                #for j_id, j in enumerate([31,28,31,30,31,30,31,31,30,31,30,31]):
                #    offshore_tmp_tmp=DataFrame()
                #    offshore_tmp_tmp['cap_factor']=np.tile(offshore_tmp.loc[offshore_tmp.month==j_id+1,'cap_factor'].values,j)
                #    offshore_tmp2=offshore_tmp2.append(offshore_tmp_tmp)
                #n=int(len(timepoints)/len(offshore_tmp2))
                #project_variable['cap_factor']=np.tile(offshore_tmp2['cap_factor'],n)
            project_variable['cap_factor']=np.tile(wind_variable['Value'],n)       
        project_variable.to_csv(share_path+name_variable,index=False)
        
        
def generate_system_load(period_select,structure,scale,scenario):
   m=0
   for k in scenario:
       system_load=DataFrame()
       m=m+1
       for i in period_select:
           load=read_csv('raw_data/China_Load_'+str(i)+'.csv').groupby(['Year','Month','Period']).mean().reset_index()
           load_total=read_csv('raw_data/China_Load_'+str(i)+'.csv').iloc[4:,].sum().sum()/10**9
           deflator=load_total/scale.loc[i,k]
           load['East_Inner_Mongolia']=load['Inner_Mongolia']*0.3
           load['West_Inner_Mongolia']=load['Inner_Mongolia']*0.7
           load=load.drop(['Day','Inner_Mongolia'],axis=1)
           load['timepoint']=structure.loc[structure['period']==i,'timepoint'].reset_index().drop('index',axis=1)
           load=load.melt(id_vars=['Year','Month','Period','timepoint'],var_name='load_zone',value_name='load_mw').sort_values(['load_zone','Month','Period'])
           system_load=system_load.append(DataFrame({
               'load_zone':load['load_zone'],
               'stage_id':1,
               'timepoint': load['timepoint'],
               'load_mw':load['load_mw']/deflator
               }),ignore_index=True)
       system_load.to_csv('system_load/system_load/'+str(m)+'_'+k+'.csv',index=False)
   
def generate_system_load_full(period_select,structure,scale,scenario,share_path_db):
   m=0
   for k in scenario:
       system_load=pd.DataFrame()
       m=m+1
       for i in period_select:
           load=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/China_Load_'+str(i)+'.csv')
           load=load.drop(load[(load.Month==2) & (load.Day==29)].index).reset_index().drop('index',axis=1)
           load_total=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/China_Load_'+str(i)+'.csv').iloc[4:,].sum().sum()/10**9
           deflator=load_total/scale.loc[i,k]
           load['East_Inner_Mongolia']=load['Inner_Mongolia']*0.3
           load['West_Inner_Mongolia']=load['Inner_Mongolia']*0.7
           load=load.drop(['Inner_Mongolia'],axis=1)
           load['timepoint']=structure.loc[structure['period']==i,'timepoint']
           load=load.melt(id_vars=['Year','Month','Day','Period','timepoint'],var_name='load_zone',value_name='load_mw').sort_values(['load_zone','Month','Day','Period'])
           load['pct']=load['load_mw']/(load.load_mw.sum())

           H2=pd.read_excel('H:/Hydrogen/hydrogen demand.xlsx',sheet_name='Total demand')
           
           if k=='LBNL':
               H2_scenario='REF'
           else:
               H2_scenario='Cap'
        
           H2=H2.loc[:,['load_zone', H2_scenario+'_H2_mwh_yr']]
           H2=H2.rename(columns={H2_scenario+'_H2_mwh_yr': 'H2_mw'})
           
           '''    
           new_H2=pd.DataFrame(
               {
               'load_zone':['East_Inner_Mongolia','West_Inner_Mongolia'],
               'H2_mw': [H2.loc[H2.load_zone=='Inner Mongolia','H2_mw'].values[0]*0.3, H2.loc[H2.load_zone=='Inner Mongolia','H2_mw'].values[0]*0.7]
                }
                  )
           H2=H2.append(new_H2)
           H2=H2.drop(index=H2[H2.load_zone=='Inner Mongolia'].index, axis=0)
           
           load=load.merge(H2,how='left')
           '''
           
           system_load=system_load.append(pd.DataFrame({
               'load_zone':load['load_zone'],
               'stage_id':1,
               'timepoint': load['timepoint'],
               'load_mw':load['load_mw']/deflator,
               'H2_mw': load['pct']*H2.H2_mw.values[0]
               }),ignore_index=True)
           
       system_load.to_csv(share_path_db+'system_load/'+str(m)+'_'+k+'.csv',index=False)
   
     
def generate_system_load_full_flat_hydrogen(period_select,structure,scale,scenario,share_path_db):
   m=0
   for k in scenario:
       system_load=pd.DataFrame()
       m=m+9
       for i in period_select:
           load=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/China_Load_'+str(i)+'.csv')
           load=load.drop(load[(load.Month==2) & (load.Day==29)].index).reset_index().drop('index',axis=1)
           load_total=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_new_china/raw_data/China_Load_'+str(i)+'.csv').iloc[4:,].sum().sum()/10**9
           deflator=load_total/scale.loc[i,k]
           load['East_Inner_Mongolia']=load['Inner_Mongolia']*0.3
           load['West_Inner_Mongolia']=load['Inner_Mongolia']*0.7
           load=load.drop(['Inner_Mongolia'],axis=1)
           load['timepoint']=structure.loc[structure['period']==i,'timepoint']
           load=load.melt(id_vars=['Year','Month','Day','Period','timepoint'],var_name='load_zone',value_name='load_mw').sort_values(['load_zone','Month','Day','Period'])
           load_province=load.groupby(['load_zone','Year'])['load_mw'].sum().reset_index()
           load_province['load_mw']=load_province['load_mw']/load_province.load_mw.sum()

           H2=pd.read_excel('H:/Hydrogen/hydrogen demand.xlsx',sheet_name='Total demand')
           
           if k=='LBNL':
               H2_scenario='REF'
           else:
               H2_scenario='Cap'
        
           H2=H2.loc[:,['load_zone', H2_scenario+'_H2_mwh_yr']]
           H2=H2.rename(columns={H2_scenario+'_H2_mwh_yr': 'H2_mw'})
           
           new_H2=load_province
           new_H2['H2_mw']=H2.H2_mw.values[0]*load_province.load_mw/8760
           
           load=load.merge(new_H2[['load_zone','H2_mw']], how='left')
           '''    
           new_H2=pd.DataFrame(
               {
               'load_zone':['East_Inner_Mongolia','West_Inner_Mongolia'],
               'H2_mw': [H2.loc[H2.load_zone=='Inner Mongolia','H2_mw'].values[0]*0.3, H2.loc[H2.load_zone=='Inner Mongolia','H2_mw'].values[0]*0.7]
                }
                  )
           H2=H2.append(new_H2)
           H2=H2.drop(index=H2[H2.load_zone=='Inner Mongolia'].index, axis=0)
           
           load=load.merge(H2,how='left')
           '''
           
           system_load=system_load.append(pd.DataFrame({
               'load_zone':load['load_zone'],
               'stage_id':1,
               'timepoint': load['timepoint'],
               'load_mw':load['load_mw']/deflator,
               'H2_mw': load['H2_mw']
               }),ignore_index=True)
           
       system_load.to_csv(share_path_db+'system_load/'+str(m)+'_'+k+'.csv',index=False)
    