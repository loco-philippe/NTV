# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 09:32:30 2023

@author: phili
"""
from datetime import time
from json_ntv import Ntv, NtvConnector

def is_json(obj, ntvobj=False):
    if not obj:
        return True
    match obj:
        case str() | int() | float() | bool() as obj:
            return True
        case list() | tuple() as obj:
            return min([is_json(obj_in) for obj_in in obj])
        case dict() as obj:
            return (min([isinstance(key, str) for key in obj.keys()]) and 
                    min([is_json(obj_in) for obj_in in obj.values()]))
        case obj.__class__.__name__ if 
        case _:
            return False

print(NtvConnector.castable)     
print(is_json({'tst':[1, 2, 'test', None, True, {'test': 1}, [1, 'tst']]}))

print(is_json(time()))
print(is_json({'tst':[1, 2, 'test', None, True, {23: 1}, [1, 'tst']]}))
print(is_json({'tst':[1, 2, 'test', None, True, {'test': time()}, [1, 'tst']]}))
