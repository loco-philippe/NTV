# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:31:23 2024

@author: phili
"""

import json
from copy import copy
import pathlib
from collections.abc import Callable

import json_ntv
from json_ntv.ntv import Ntv, NtvList
from json_ntv.ntv_patch import NtvPointer
from json_ntv.namespace import from_file
from jsonpointer import resolve_pointer
from jsonschema import validate

file = pathlib.Path(json_ntv.__file__).parent.parent / "RFC" / "NTV_NTVschema_namespace.ini"
from_file(file, '$NTVschema.')

def validat(ntv_data, sch):
    #print('    ', ntv_data, sch)
    return validate(ntv_data, sch) is None    
    
def sh_expand(ntv_data):    
    return {'value' : [ntv.ntv_value for ntv in ntv_data.ntv_value],
            'name'  : [ntv.ntv_name if ntv.ntv_name else None for ntv in ntv_data.ntv_value], 
            'type'  : [ntv.type_str for ntv in ntv_data.ntv_value]
            } if isinstance (ntv_data, NtvList) else {
                'value' : ntv_data.ntv_value,
                'name'  : ntv_data.ntv_name, 
                'type'  : ntv_data.type_str}

def sh_compact(schema):
    sch = {}
    sch['type']  = schema['type.']  if 'type.'  in schema.keys() else {}
    sch['name']  = schema['name.']  if 'name.'  in schema.keys() else {}
    sch['value'] = schema['value.'] if 'value.' in schema.keys() else {}
    sch['value'] |= {key:val for key, val in schema.items() 
                     if not key in ['type.', 'name.', 'value.']}
    return sch

def sh_items(schema):
    schema = schema['items.'] if 'items.' in schema else schema
    name = {'name': {'items': schema['name.']}} if 'name.' in schema else {}
    typ  = {'type': {'items': schema['type.']}} if 'type.' in schema else {}
    value = {'value': {'items': {k:v for k, v in schema.items() if not k in ['name.', 'type.']}}}
    return {'properties' : value | name | typ }

def val_items(ntv_data, sch) : 
    return validat(sh_expand(ntv_data), sh_items(sch))
    
def val_simple(ntv_data, sch) :
    if not sch:
        return True
    #print('val_simple', ntv_data, sch)
    json_data = sh_expand(ntv_data)
    valid = True
    valid &= validat(json_data['value'], sh_compact(sch)['value'])
    valid &= validat(json_data['type'],  sh_compact(sch)['type'])
    valid &= validat(json_data['name'],  sh_compact(sch)['name'])
    return valid

def validate_ntv(keyword, ntv_data, sch):
    print('validate : ', keyword, ntv_data)
    valid = val_items(ntv_data, sch['items.']) if 'items.' in sch.keys() else True
    valid &= val_simple(ntv_data, {key: val for key, val in sch.items() if not key == 'items.'})
    print('valide : ', valid)
    return valid

def _json(dic):
    return {(lambda k : k[1:] if k[0] == ':' else k)(key): _json(value) 
            for key, value in dic.items()} if isinstance(dic, dict) else dic
    
def _pure(dic, keywords=None):
    keyw = list(keywords) if keywords else []
    keyw += ['properties.', 'prefixItems.']
    return _json({key: val for key, val in dic.items() if not key in keyw})

def navigate(data, sch):
    ntv_data = Ntv.obj(data)
    p_data = str(ntv_data.pointer())
    sch_p =  list(sch.keys())[0]
    mapping = {p_data : '/' + sch_p}
    validate_ntv('global', ntv_data, _pure(sch[sch_p]))
    for ntv in list(ntv_data.tree)[1:]:
        parent_ntv = ntv.pointer()[:-1]
        parent_sch = resolve_pointer(sch, mapping[str(parent_ntv)])
        new_p_data = str(ntv.pointer())
        if 'properties.' in parent_sch:
            if ntv.ntv_name in parent_sch['properties.']:
                mapping[new_p_data] = mapping[str(parent_ntv)] + '/properties.' + '/' + ntv.ntv_name
                validate_ntv('properties', ntv_data['#' + new_p_data], 
                         _pure(parent_sch['properties.'][ntv.ntv_name]))
            else:
                print('not include', ntv_data['#' + new_p_data], True)
        elif 'prefixItems.' in parent_sch:
            row = NtvPointer.pointer_list(ntv.pointer()[-1])[0]
            if len(parent_sch['prefixItems.']) > row:
                mapping[new_p_data] = mapping[str(parent_ntv)] + '/prefixItems.' + '/' + str(row)
                validate_ntv('prefixItems', ntv_data['#' + new_p_data], 
                         _pure(parent_sch['prefixItems.'][row]))
            else:
                print('not include', ntv_data['#' + new_p_data], True)
        else:
            print('pas de properties et de PrefixItems')

