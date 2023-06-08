# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 23:09:43 2023

@author: a lab in the Air
"""
from ntv import NtvList, NtvSingle, NtvSet, Ntv

class NtvStruct:
    
    def __init__(self, name, fields):
        '''fields : list of jsonname'''
        self.name = name
        self.fields_n = [Ntv.from_obj_name(field)[0] for field in fields]
        self.fields_t = [Ntv.from_obj_name(field)[1] for field in fields]
        self.values = None
        
    def setvalue(self, list_val):
        self.values = list_val
        
    def to_objset(self, **kwargs):
        return NtvSet([NtvSingle(val, nam, typ) for val, nam, typ in 
                        zip(self.values, self.fields_n, self.fields_t )], self.name).to_obj(**kwargs)
    
    def to_objlist(self, **kwargs):
        return NtvList([NtvSingle(val, nam, typ) for val, nam, typ in 
                        zip(self.values, self.fields_n, self.fields_t )], self.name).to_obj(**kwargs)
    
sensor = NtvStruct('sensor', ['measure', 'date_meas:datetime'])
sensor.setvalue([45.1, '2023-01-10'])

print(sensor.to_objset())
print(sensor.to_objset(format='obj'))
print(sensor.to_objlist(simpleval=True))
print(sensor.to_objlist(format='obj', simpleval=True))
