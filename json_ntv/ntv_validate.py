# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 14:35:22 2024

@author: a lab in the Air
"""
'''from json_ntv.namespace import Datatype

def mapping(typ=None, func=None):
    if typ and func:
        Datatype.add(typ).validate = func
    else:
        if isinstance(typ, str):
            func_lis = [ typ + '_valid' ]
        elif isinstance(typ, (list, tuple)):
            func_lis = [ typ_str + '_valid' for typ_str in typ]
        else:
            func_lis = [ typ_str + '_valid' for typ_str in Datatype._types_]
        for func_str in func_lis:
            if func_str in Validator.__dict__:
                Datatype.add(func_str[:-6]).validate = Validator.__dict__[func_str]            '''


class Validator:
    
    def float_valid(val):
        return isinstance(val, float)
    
    def string_valid(val):
        return isinstance(val, str)
    
    def day_valid(val):
        return isinstance(val, int) and 0 < val < 32