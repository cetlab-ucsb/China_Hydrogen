# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 21:15:27 2022

@author: haozheyang
"""

import pandas as pd
import numpy as np

def generate_prm_load_zone(cluster,non_prm):
    project_prm_load_zone=pd.DataFrame({'project':cluster['project'],
                                 'prm_zone':cluster['zone']})
    project_prm_load_zone=project_prm_load_zone.drop(cluster[cluster.capacity_group.isin(non_prm)].index)
    return project_prm_load_zone

def generate_prm_project_elcc(cluster):
    #project=cluster.loc[~cluster.capacity_group.isin(['group_p2g','group_H2','group_underground','group_tank']),'project']
    project=cluster.project
    project_elcc_chars=pd.DataFrame({
        'project':project,
        'prm_type': 'fully_deliverable',
        'elcc_simple_fraction':0.8,
        'contributes_to_elcc_surface':"",	
        'cap_factor_for_elcc_surface':"",
        'min_duration_for_full_capacity_credit_hours':"",
        'deliverability_group':""     
        })
    
    index1=cluster[cluster.capacity_group=='group_battery'].index
    project_elcc_chars.loc[index1,'min_duration_for_full_capacity_credit_hours']=4

    index2=cluster[cluster.capacity_group.isin(['group_coal','group_gas','group_nuclear','group_g2p'])].index
    project_elcc_chars.loc[index2,'elcc_simple_fraction']=0.9
    
    index3=cluster[cluster.capacity_group.isin(['group_pv'])].index
    project_elcc_chars.loc[index3,'elcc_simple_fraction']=0
    
    index3=cluster[cluster.capacity_group.isin(['group_wind'])].index
    project_elcc_chars.loc[index3,'elcc_simple_fraction']=0.10

    index4=cluster[cluster.capacity_group.isin(['group_p2g','group_H2','group_underground','group_tank'])].index
    project_elcc_chars.loc[index4,'elcc_simple_fraction']=0
    
    return project_elcc_chars

def generate_system_prm_req(scenario,share_path_rel):
   m=0
   for k in scenario:
       m=m+1
       load=pd.read_csv('C:/Program Files/GRIDPATH/db/csvs_plexos_hydrogen/system_load/system_load/'+str(m)+'_'+k+'.csv')
       load['period']=[int(str(i)[0:4]) for i in load['timepoint']]
        
       prm_zone=load.groupby(['load_zone','period'])['load_mw'].max().reset_index()
       system_prm=pd.DataFrame({
               'prm_zone':prm_zone['load_zone'],
               'period': prm_zone['period'],
               'prm_requirement_mw':prm_zone['load_mw']*1.15,
               'prm_peak_load_mw':"",	
               'prm_annual_load_mwh':""

               })
       
       #system_prm.loc[system_prm.period==2020,'prm_requirement_mw']=system_prm.loc[system_prm.period==2020,'prm_requirement_mw']*1/1.15
    
       system_prm.to_csv(share_path_rel+'reliability/prm/system_prm_requirement/'+str(m)+'_'+k+'.csv',index=False)
       
def generate_system_reserve_req(scenario):
   m=0
   for k in scenario:
       m=m+1
       load=pd.read_csv('system_load/system_load/'+str(m)+'_'+k+'.csv')
        
       reserve_zone=load['load_mw']*0.03
       #reserve_zone[load.timepoint<2030000000]=0
       
       lf_reserves_down=pd.DataFrame({
               'lf_reserves_down_ba':load['load_zone'],
               'stage_id':1,
               'timepoint': load['timepoint'],
               'lf_reserves_down_mw':reserve_zone,

               })
       
       lf_reserves_up=pd.DataFrame({
               'lf_reserves_up_ba':load['load_zone'],
               'stage_id':1,
               'timepoint': load['timepoint'],
               'lf_reserves_up_mw':reserve_zone,

               })
       
       regulation_reserves_up=pd.DataFrame({
               'regulation_up_ba':load['load_zone'],
               'stage_id':1,
               'timepoint': load['timepoint'],
               'regulation_up_mw':reserve_zone,

               })
       
       regulation_reserves_down=pd.DataFrame({
               'regulation_down_ba':load['load_zone'],
               'stage_id':1,
               'timepoint': load['timepoint'],
               'regulation_down_mw':reserve_zone,

               })
    
       lf_reserves_up.to_csv('reserves/lf_reserves_up/req/'+str(m)+'_'+k+'/'+'timepoint.csv',index=False)
       lf_reserves_down.to_csv('reserves/lf_reserves_down/req/'+str(m)+'_'+k+'/'+'timepoint.csv',index=False)
       regulation_reserves_up.to_csv('reserves/regulation_up/req/'+str(m)+'_'+k+'/'+'timepoint.csv',index=False)
       regulation_reserves_down.to_csv('reserves/regulation_down/req/'+str(m)+'_'+k+'/'+'timepoint.csv',index=False)
       
def generate_reserve_load_zone(cluster,gen_type):
    cluster2=pd.merge(cluster,gen_type)
    cluster2=cluster.drop(cluster2[cluster2.operational_type=='gen_must_run'].index)
        
    lf_reserves_up_zone=pd.DataFrame({'project':cluster2['project'],
                                      'lf_reserves_up_ba':cluster2['zone']})
    
    lf_reserves_down_zone=pd.DataFrame({'project':cluster2['project'],
                                         'lf_reserves_down_ba':cluster2['zone']})
    
    regulation_up_zone=pd.DataFrame({'project':cluster2['project'],
                                     'regulation_up_ba':cluster2['zone']})
    
    regulation_down_zone=pd.DataFrame({'project':cluster2['project'],
                                        'regulation_down_ba':cluster2['zone']})

    lf_reserves_up_zone.to_csv('reserves/lf_reserves_up/project_lf_reserves_up_bas/1_china.csv',index=False)
    lf_reserves_down_zone.to_csv('reserves/lf_reserves_down/project_lf_reserves_down_bas/1_china.csv',index=False)
    regulation_up_zone.to_csv('reserves/regulation_up/project_regulation_up_bas/1_china.csv',index=False)
    regulation_down_zone.to_csv('reserves/regulation_down/project_regulation_down_bas/1_china.csv',index=False)   




       
