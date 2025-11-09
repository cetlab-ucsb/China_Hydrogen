# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 14:24:48 2023

@author: haozheyang
"""

import pickle
import numpy as np
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
