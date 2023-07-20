# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 09:32:30 2023

@author: phili
"""
from datetime import time
from json_ntv import Ntv, NtvConnector
from shapely import geometry

def is_json(obj, ntvobj=False):
    if not obj:
        return True
    match obj:
        case str() | int() | float() | bool() as obj:
            return True
        case list() | tuple() as obj:
            return min([is_json(obj_in, ntvobj) for obj_in in obj])
        case dict() as obj:
            return (min([isinstance(key, str) for key in obj.keys()]) and 
                    min([is_json(obj_in, ntvobj) for obj_in in obj.values()]))
        case _:
            return ntvobj and obj.__class__.__name__ in NtvConnector.castable


print(is_json({'tst':[1, 2, 'test', None, True, {'test': 1}, [1, 'tst']]}))
print(is_json({'tst':[1, 2, 'test', None, True, {'test': time()}, 
                      [1, 'tst', geometry.Point(1,2)]]}, True))

print(is_json({'tst':[1, 2, 'test', None, True, {'test': time()}, 
                      [1, 'tst', geometry.Point(1,2)]]}))
print(is_json({'tst':[1, 2, 'test', None, True, {23: 1}, [1, 'tst']]}))
print(is_json({'tst':[1, 2, 'test', None, True, {'test': time()}, [1, 'tst']]}))


