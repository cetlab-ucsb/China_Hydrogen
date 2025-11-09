# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 15:16:09 2023

@author: haozheyang
"""

#Practice 1
from pyomo.environ import *
model=ConcreteModel()
model.x=Var(domain=NonNegativeReals)
model.profit=Objective(expr=40*model.x,
                       sense=maximize)
model.demand=Constraint(expr=model.x<=40)
model.laborA=Constraint(expr=model.x<=80)
model.laborB=Constraint(expr=2*model.x<=100)

SolverFactory('cbc').solve(model).write()
model.profit()
model.x()
model.profit.display()
model.x.display()


#practice 2

data = {
    None:
    {
    'C': {None: ['A','B','W']},
    'abv_order':{None: 0.04},
    'vol':{None: 100},
    'abv': {'A': 0.045, 'B': 0.037,'W':0.000},
    'cost': {'A': 0.32, 'B': 0.25,'W':0.05}
    }
}
    
model=AbstractModel()

model.C=Set()
model.cost=Param(model.C)
model.abv=Param(model.C)
model.abv_order=Param()
model.vol=Param()

model.x = Var(model.C, domain=NonNegativeReals)

def abv_constraint(model,i):
    return sum(model.x[i]*(model.abv[i]-model.abv_order) for i in model.C)==0
    
model.abv_c = Constraint(model.C,rule=abv_constraint)

def obj(model):
    return summation(model.cost,model.x)

model.npv=Objective(rule=obj)

def vol_constraint(model):
    return model.vol==summation(model.x)
model.vol_c=Constraint(rule=vol_constraint)
    
i=model.create_instance(data)

i.pprint()

solver = SolverFactory('cbc')
solver.solve(i)

i.npv()
[i.x[c]() for c in i.C]



