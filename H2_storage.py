# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 19:45:37 2024

@author: haozheyang
"""


from pandas import read_csv,merge,concat, DataFrame, read_excel
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter


        

file1='dispatch_stor_H2.csv'
file2='dispatch_H2.csv'



    
test_id=[
         'Hydrogen_400ppm_1period_36day_grid',
         #'Hydrogen_400ppm_1period_36day_H2',
         #'Hydrogen_400ppm_1period_36day_H2_ccs',
         #'Hydrogen_400ppm_1period_36day_H2_SMR',
         #'Hydrogen_400ppm_1period_36day_H2_expand',
         #'Hydrogen_400ppm_1period_36day_H2_expand',
         #'Hydrogen_400ppm_1period_36day_H2_expand_SMR'
         ]
capacity=pd.DataFrame()
generation=pd.DataFrame()
cost=pd.DataFrame()
unitcost=pd.DataFrame()
for case in test_id:
    path='H:/Hydrogen/Data/'+case+'/results/'
    H2_path=path+file2
    stor=pd.read_csv(path+file1)
    stor=stor.groupby(['timepoint','timepoint_weight'])[['H2_stor_mwh',
                                                         'H2_charge_mw',
                                                         'H2_discharge_mw']].sum()
    
    H2_tmp=pd.read_csv(H2_path)
    H2_tmp.H2_mw=H2_tmp.H2_mw*H2_tmp.timepoint_weight/10**6
    H2_pos_tmp= H2_tmp.loc[H2_tmp.H2_mw>0,:]
    H2_neg_tmp= H2_tmp.loc[H2_tmp.H2_mw<0,:]
        
    H2_technology_pos_tmp=H2_pos_tmp.groupby(['technology'])['H2_mw'].sum().reset_index()
    H2_technology_pos_tmp['scenario']=case
    
    H2_technology_neg_tmp=H2_neg_tmp.groupby(['technology'])['H2_mw'].sum().reset_index()
    H2_technology_neg_tmp['scenario']=case
    
    H2_technology_pos_tmp=H2_technology_pos_tmp.pivot(index='scenario',columns='technology',values='H2_mw')
    H2_technology_neg_tmp=H2_technology_neg_tmp.pivot(index='scenario',columns='technology',values='H2_mw')

    