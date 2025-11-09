# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:24:51 2024

@author: haozheyang
"""

from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter

        

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
file17='npv.csv'

base='Hydrogen_400ppm_1period_36day'
test_id=[
         #'Hydrogen_400ppm_1period_36day_H2',
         #'Hydrogen_400ppm_1period_36day_H2_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_SMR',
         '',
         '_lowcost',
         '_highcost',
         '_low_efficiency',
         '_decouple',
         #'_SMR_ccs_conservative_decouple_storage'
         #'Hydrogen_REF_1period_36day_onlyH2_SMR',
         #'Hydrogen_400ppm_1period_36day_onlyH2_expand_SMR',
         #'Hydrogen_400ppm_1period_36day_H2_expand_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_expand_SMR'
         ]

path='/Users/hy4174/Documents/Hydrogen/data/'+base+'/results/'  
npv_path=path+file17
H2_balance_path=path+file16
load_balance=path+file15

cost_base=pd.read_csv(npv_path).sum(axis=1)/10
load=pd.read_csv(path+file15)
load.load_mw=load.load_mw*load.timepoint_weight
load_sum=load.load_mw.sum()
lcoe=cost_base/load_sum
#print(lcoe.values[0])

generation_H2=pd.DataFrame()

for case in test_id:
    path='/Users/hy4174/Documents/Hydrogen/data/'+'Hydrogen_400ppm_1period_36day' + case+'/results/'
    if case.find( '_decouple')>-1:
        path='/Users/hy4174/Documents/Hydrogen/data/'+'Hydrogen_400ppm_1period_36day'+'/results/'
    path_H2='/Users/hy4174/Documents/Hydrogen/data/' +'Hydrogen_400ppm_1period_36day_H2_expand'+ case+'_flat/results/'    
    
    generation=pd.read_csv(path + file1)
    generation.power_mw=generation.power_mw*generation.timepoint_weight
    generation_sum = generation.power_mw.sum()
    
    capacity=pd.read_csv(path + file6)
    capacity_H2=capacity.loc[capacity.technology=='Electrolyzer','capacity_mw'].sum()

    cost=pd.read_csv(path + file17).sum(axis=1)/10  #per period is 10 years in npv
    cost_H2=pd.read_csv(path_H2 + file17).sum(axis=1)/10
    
    load_H2=pd.read_csv(path_H2+file16)
    load_H2.H2_mw=load_H2.H2_mw * load_H2.timepoint_weight
    H2_sum=load_H2.H2_mw.sum()
    
    load=pd.read_csv(path_H2+file15)
    load.load_mw=load.load_mw*load.timepoint_weight
    load_sum=load.load_mw.sum()
    
    lcoe=cost/(generation_sum)*120/3600
    #*120/3600
    print(lcoe.values[0])
    
    #lcoe=cost_H2/(load_sum+H2_sum)*120/3600
    #print(lcoe.values[0])
   
    lcoh=(cost_H2-cost)/H2_sum *120/3600 #$/MWh --> $/MJ --> $/kg
    print(lcoh.values[0])
  
    #############LCOH
    H2_path=path_H2+file10  
    H2_tmp=pd.read_csv(H2_path)
    H2_tmp.H2_mw=H2_tmp.H2_mw*H2_tmp.timepoint_weight/10**6
    

test_id2=[
         #'Hydrogen_400ppm_1period_36day_H2',
         #'Hydrogen_400ppm_1period_36day_H2_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_SMR',
         '',
         '_H2_expand_flat',
         '_H2_expand_lowcost_flat',
         '_H2_expand_highcost_flat',
         '_H2_expand_low_efficiency_flat',
         '_H2_expand_decouple_flat',
         '_H2_expand_SMR_ccs_80_decouple'
         #'Hydrogen_REF_1period_36day_onlyH2_SMR',
         #'Hydrogen_400ppm_1period_36day_onlyH2_expand_SMR',
         #'Hydrogen_400ppm_1period_36day_H2_expand_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_expand_SMR_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_expand_SMR'
         ]

for case in test_id2:
    path_H2='/Users/hy4174/Documents/Hydrogen/data/' +'Hydrogen_400ppm_1period_36day'+ case+'/results/'     

    generation=pd.read_csv(path_H2 + file1)
    generation.power_mw=generation.power_mw * generation.timepoint_weight
    generation_ele_sum = generation.loc[~(generation.technology == 'Electrolyzer'),'power_mw'].sum()
    generation_H2_sum = generation.loc[generation.technology == 'Electrolyzer','power_mw'].sum()
    generation_H2_ind_sum = generation.loc[(generation.technology == 'Electrolyzer') & generation.load_zone.str.contains('H2'),
                                           'power_mw'].sum()
    
    cost=pd.read_csv(path_H2 + file17).sum(axis=1)/10
    
    capacity_cost = pd.read_csv(path_H2+file3)
    
    operation_cost = pd.read_csv(path_H2+file4).fillna(0)
    operation_cost['variable_cost']=(operation_cost.variable_om_cost+operation_cost.fuel_cost)*operation_cost.timepoint_weight
    
    transmission_cost = pd.read_csv(path_H2+file5)
    
    #capacity_cost_H2 = capacity_cost.loc[capacity_cost.load_zone.str.contains('H2'),'capacity_cost'].sum()
    
    capacity_cost_ele = capacity_cost.loc[~capacity_cost.technology.isin(['Electrolyzer','Salt_cavern','Tank', 'SMR', 'Gasification']) ,'capacity_cost'].sum()
    capacity_cost_H2 = capacity_cost.loc[capacity_cost.technology.isin(['Electrolyzer','Salt_cavern','Tank', 'SMR', 'Gasification']) ,'capacity_cost'].sum()    
    capacity_cost_H2_ind = capacity_cost.loc[(capacity_cost.technology.isin(['Electrolyzer','Salt_cavern','Tank', 'SMR', 'Gasification'])) & (capacity_cost.load_zone.str.contains("H2")),
                                             'capacity_cost'].sum()    

    operation_cost_ele = operation_cost.loc[~operation_cost.technology.isin(['Electrolyzer','Salt_cavern','Tank', 'SMR', 'Gasification']),'variable_cost'].sum() 
    operation_cost_H2 = operation_cost.loc[operation_cost.technology.isin(['Electrolyzer','Salt_cavern','Tank', 'SMR', 'Gasification']) ,'variable_cost'].sum()    
    operation_cost_H2_ind = operation_cost.loc[(operation_cost.technology.isin(['Electrolyzer','Salt_cavern','Tank', 'SMR', 'Gasification'])) & (operation_cost.load_zone.str.contains("H2")),
                                             'variable_cost'].sum()   
    
    transmission_cost_ele = transmission_cost.loc[~transmission_cost.tx_line.str.contains('H2'),'capacity_cost'].sum() 
    transmission_cost_H2 = transmission_cost.loc[transmission_cost.tx_line.str.contains('H2'),'capacity_cost'].sum()    
    
    
    lcoe=(capacity_cost_ele + operation_cost_ele + transmission_cost_ele)/generation_ele_sum 
    
    lcoe_ind=(capacity_cost_ele + operation_cost_ele + transmission_cost_ele + transmission_cost_H2 + capacity_cost_H2 + operation_cost_H2 - capacity_cost_H2_ind - operation_cost_H2_ind )/generation_ele_sum 
    
    print(lcoe)

    capacity=pd.read_csv(path_H2 + file6)
    capacity_H2=capacity.loc[capacity.technology=='Electrolyzer','capacity_mw'].sum()

    capacity_ind_H2=capacity.loc[(capacity.technology=='Electrolyzer') & (capacity.load_zone.str.contains("H2")),'capacity_mw'].sum()

    
    H2_path=path_H2+file10  
    H2_tmp=pd.read_csv(H2_path)
    H2_tmp.H2_mw=H2_tmp.H2_mw*H2_tmp.timepoint_weight
    
    H2_prod_tmp = H2_tmp.loc[H2_tmp.technology.isin(['Electrolyzer', 'SMR', 'Gasification']),'H2_mw'].sum() 
    H2_prod_tmp_ind = H2_tmp.loc[ (H2_tmp.technology.isin(['Electrolyzer', 'SMR', 'Gasification']))  & (H2_tmp.load_zone.str.contains("H2")),
                             'H2_mw'].sum() 
    
    lcoh = (capacity_cost_H2 + operation_cost_H2 + transmission_cost_H2 - lcoe * generation_H2_sum)/H2_prod_tmp*120/3600 
    
    H2_electrolyzer=H2_tmp.loc[H2_tmp.technology == 'Electrolyzer','H2_mw'].sum()
    
    H2_ind_electrolyzer=H2_tmp.loc[(H2_tmp.technology == 'Electrolyzer') & (H2_tmp.load_zone.str.contains("H2")),'H2_mw'].sum()
    
    #c_ele = 41610.52775
    #eta_ele = 0.7
    #cf_H2 = H2_electrolyzer/(8760*capacity_H2*eta_ele)
    #cf_ind_H2 = H2_ind_electrolyzer/(8760*capacity_ind_H2*eta_ele)
        
    #lcoh_all =c_ele /(cf_H2*8760*eta_ele)*120/3600 + lcoe/eta_ele
    #lcoh_ind =c_ele /(cf_ind_H2*8760*eta_ele)*120/3600 + lcoe/eta_ele
    
    lcoh_ind = (capacity_cost_H2_ind + operation_cost_H2_ind - lcoe_ind * generation_H2_ind_sum)/H2_prod_tmp_ind*120/3600 
    
    print(lcoh)
    print(lcoh_ind)
        


    
    

base1='Hydrogen_400ppm_1period_36day_onlyH2_expand_SMR'
base2='Hydrogen_400ppm_1period_36day_onlyH2_expand'

path1='H:/Hydrogen/Data/'+base1+'/results/'
path2='H:/Hydrogen/Data/'+base2+'/results/'  

npv_path=path+file17
H2_balance_path=path+file16
load_balance=path+file15

cost1=pd.read_csv(path1+file17).sum(axis=1)/10
H21=pd.read_csv(path1+file16)
H21.H2_mw=H21.H2_mw*H21.timepoint_weight
H2_sum1=H21.H2_mw.sum()
lcoh1=cost1/H2_sum1*120/3600
print(lcoh1.values[0])

cost2=pd.read_csv(path2+file17).sum(axis=1)/10
H22=pd.read_csv(path2+file16)
H22.H2_mw=H22.H2_mw*H22.timepoint_weight
H2_sum2=H22.H2_mw.sum()
lcoh2=cost2/H2_sum2*120/3600
print(lcoh2.values[0])
    
    
SMR=59102.39761 # $/MW/yr
SMR_range=np.linspace(40000,80000,100)

SMR_CCS=30133.51805
SMR_gas=4.8 #mmbtu per MWh

var=0.8
price=13.67653313
price_range=np.linspace(2,14,100)

EF=0.05306
DAC=1074073.565

lcoe_SMR_full=np.zeros((len(SMR_range),len(price_range)))

for i, SMR_cost in enumerate(SMR_range):
    for j, gas_cost in enumerate(price_range):
        lcoe_SMR_full[i,j]=(SMR_cost+SMR_gas*8760*gas_cost)/8760*120/3600 


#print(lcoe_SMR_full)

'''
Electrolyzer=41610.52775
 #$/MW/yr
eff=0.7
ele_price=70
lcoe_electro=(Electrolyzer+1/0.6*ele_price*8760)/8760*120/3600
'''
X, Y = np.meshgrid(price_range,SMR_range)

levels=[0.4,
        0.7,
        1,
        1.3,
        1.6,
        1.9,
        2.2,
        2.5,
        2.8]

contoursf=plt.contourf(X, Y, lcoe_SMR_full,
                      levels,zorder=1
                      )

contours=plt.contour(X, Y, lcoe_SMR_full,
                      levels,zorder=2,
                      colors=['k','k','k','k','k','r','k'])

manual_locations = [
                    (2, 60000), 
                    (5, 60000), 
                    (7, 60000), 
                    (9, 60000), 
                    (11, 60000),
                    (13, 60000), 
                    ]

c=plt.clabel(contours,
           levels=[0.7,1,1.3,1.6,1.9,2.2],
           inline=True,
           colors='white',
           fontsize=12,
           fmt=' {:.1f} '.format,
           manual=manual_locations
           )

plt.colorbar(contoursf, orientation='horizontal')
