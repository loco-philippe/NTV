# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:31:23 2024

@author: phili
"""

import pathlib

import json_ntv
from json_ntv.ntv import Ntv, NtvList
from json_ntv.ntv_patch import NtvPointer
from json_ntv.namespace import from_file
from jsonpointer import resolve_pointer
from jsonschema import validate

file = pathlib.Path(json_ntv.__file__).parent.parent / "RFC" / "NTV_NTVschema_namespace.ini"
from_file(file, '$NTVschema.')

def ntv_validate(data, sch, mode=0):
    ntv_data = Ntv.obj(data)
    p_data = str(ntv_data.pointer())
    sch_p =  list(sch.keys())[0]
    mapping = {p_data : '/' + sch_p}
    valid = kw_validate('global', ntv_data, _pure(sch[sch_p]), mode)
    for ntv in list(ntv_data.tree)[1:]:
        parent_ntv = ntv.pointer()[:-1]
        parent_sch = resolve_pointer(sch, mapping[str(parent_ntv)])
        new_p_data = str(ntv.pointer())
        if 'properties.' in parent_sch:
            if ntv.ntv_name in parent_sch['properties.']:
                mapping[new_p_data] = mapping[str(parent_ntv)] + '/properties.' + '/' + ntv.ntv_name
                valid &= kw_validate('properties', ntv_data['#' + new_p_data], 
                         _pure(parent_sch['properties.'][ntv.ntv_name]), mode)
        if 'prefixItems.' in parent_sch:
            row = NtvPointer.pointer_list(ntv.pointer()[-1])[0]
            if len(parent_sch['prefixItems.']) > row:
                mapping[new_p_data] = mapping[str(parent_ntv)] + '/prefixItems.' + '/' + str(row)
                valid &= kw_validate('prefixItems ' + str(row), ntv_data['#' + new_p_data],
                                     _pure(parent_sch['prefixItems.'][row]), mode)
        if mode and not new_p_data in mapping:
            print('not include', new_p_data)
    return valid

def kw_validate(keyword, ntv_data, sch, mode):
    if mode:
        print('validate : ', keyword, 
              ntv_data.ntv_name if keyword == 'properties' else '')
    valid = val_items(ntv_data, sch['items.'], mode) if 'items.' in sch.keys() else True
    valid &= val_simple(ntv_data, {key: val for key, val in sch.items() 
                                   if not key == 'items.'}, mode)
    return valid

def val_items(ntv_data, sch, mode) : 
    return validat(_sh_expand(ntv_data), _sh_items(sch), mode)
    
def val_simple(ntv_data, sch, mode) :
    if not sch:
        return True
    json_data = _sh_expand(ntv_data)
    valid = True
    valid &= validat(json_data['value'], _sh_compact(sch)['value'], mode)
    valid &= validat(json_data['type'],  _sh_compact(sch)['type'], mode)
    valid &= validat(json_data['name'],  _sh_compact(sch)['name'], mode)
    return valid

def validat(ntv_data, sch, mode):
    if mode > 1:
        print('    ', ntv_data, sch)
    valid = False
    if mode < 2:
        try:
            valid = validate(ntv_data, sch) is None
        except :
            if mode > 0:
                print('error : ', ntv_data, 'is not valid with schema : ', sch)
    else:
        valid = validate(ntv_data, sch) is None
    return valid    
    
def _sh_expand(ntv_data):    
    return {'value' : [ntv.ntv_value for ntv in ntv_data.ntv_value],
            'name'  : [ntv.ntv_name if ntv.ntv_name else None for ntv in ntv_data.ntv_value], 
            'type'  : [ntv.type_str for ntv in ntv_data.ntv_value]
            } if isinstance (ntv_data, NtvList) else {
                'value' : ntv_data.ntv_value,
                'name'  : ntv_data.ntv_name, 
                'type'  : ntv_data.type_str}

def _sh_compact(schema):
    sch = {}
    sch['type']  = schema['type.']  if 'type.'  in schema.keys() else {}
    sch['name']  = schema['name.']  if 'name.'  in schema.keys() else {}
    sch['value'] = schema['value.'] if 'value.' in schema.keys() else {}
    sch['value'] |= {key:val for key, val in schema.items() 
                     if not key in ['type.', 'name.', 'value.']}
    return sch

def _sh_items(schema):
    schema = schema['items.'] if 'items.' in schema else schema
    name = {'name': {'items': schema['name.']}} if 'name.' in schema else {}
    typ  = {'type': {'items': schema['type.']}} if 'type.' in schema else {}
    value = {'value': {'items': {k:v for k, v in schema.items() 
                                 if not k in ['name.', 'type.']}}}
    return {'properties' : value | name | typ }

def _json(dic):
    return {(lambda k : k[1:] if k[0] == ':' else k)(key): _json(value) 
            for key, value in dic.items()} if isinstance(dic, dict) else dic
    
def _pure(dic, keywords=None):
    keyw = list(keywords) if keywords else []
    keyw += ['properties.', 'prefixItems.']
    return _json({key: val for key, val in dic.items() if not key in keyw})


    
class NtvSchemaError(Exception):
    ''' NtvSchema Exception'''
    # pass
