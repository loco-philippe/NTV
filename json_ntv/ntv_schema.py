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
    '''return the validation (True/False) of 'data' conformity to a 'sch' NTVschema.
    
    *Parameters*

        - **data**: Ntv, json-value, json_text - data to validate
        - **sch**: json-value - NTVschema
        - **mode**: integer (default 0) - level of information
            - 0: no information
            - 1: list of controls and errors
            - 2: details of errors (traceback)
    '''  
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
    '''return the validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.
    
    *Parameters*

        - **keyword**: string - context 'properties' or 'prefixItems'
        - **ntv_data**: Ntv entity
        - **sch**: json-value - NTVschema
        - **mode**: integer (default 0) - level of information
            - 0: no information
            - 1: list of controls and errors
            - 2: details of errors (traceback)
    '''  
    if mode:
        print('validate : ', keyword, 
              ntv_data.ntv_name if keyword == 'properties' else '')
    valid = val_items(ntv_data, sch['items.'], mode) if 'items.' in sch.keys() else True
    valid &= val_simple(ntv_data, {key: val for key, val in sch.items() 
                                   if not key == 'items.'}, mode)
    return valid

def val_items(ntv_data, items_sch, mode) : 
    '''return the validation (True/False) of a NTV entity conformity to a items 'sch' schema.
    
    *Parameters*

        - **ntv_data**: Ntv entity
        - **items_sch**: json-value - items NTVschema
        - **mode**: integer (default 0) - level of information
            - 0: no information
            - 1: list of controls and errors
            - 2: details of errors (traceback)
    '''  
    return validat(_ntv_to_json(ntv_data), _items_to_jsch(items_sch), mode)
    
def val_simple(ntv_data, sch, mode) :
    '''return the validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.

    *Parameters*

    - **ntv_data**: Ntv entity
    - **sch**: json-value - NTVschema with simple keywords
    - **mode**: integer (default 0) - level of information
        - 0: no information
        - 1: list of controls and errors
        - 2: details of errors (traceback)
    '''  
    if not sch:
        return True
    json_data = _ntv_to_json(ntv_data)
    json_sch  = _simple_to_jsch(sch)
    valid = True
    for part in ['value', 'type', 'name']:
        valid &= validat(json_data[part], json_sch[part], mode)
    return valid

def validat(json_data, jsch, mode):
    '''return the validation (True/False) of a json data conformity to a 'jsch' JSONschema.

    *Parameters*
    
        - **json_data**: json_data to validate
        - **jsch**: json-value - JSONschema
        - **mode**: integer (default 0) - level of information
            - 0: no information
            - 1: list of controls and errors
            - 2: details of errors (traceback)
    '''  
    if mode > 1:
        print('    ', json_data, jsch)
    valid = False
    if mode < 2:
        try:
            valid = validate(json_data, jsch) is None
        except :
            if mode > 0:
                print('error : ', json_data, 'is not valid with schema : ', jsch)
    else:
        valid = validate(json_data, jsch) is None
    return valid    
    
def _ntv_to_json(ntv_data):  
    '''transform a Ntv entity into a json representation'''
    return {'value' : [ntv.ntv_value for ntv in ntv_data.ntv_value],
            'name'  : [ntv.ntv_name if ntv.ntv_name else None for ntv in ntv_data.ntv_value], 
            'type'  : [ntv.type_str for ntv in ntv_data.ntv_value]
            } if isinstance (ntv_data, NtvList) else {
                'value' : ntv_data.ntv_value,
                'name'  : ntv_data.ntv_name, 
                'type'  : ntv_data.type_str}

def _simple_to_jsch(ntvsch):
    '''transform a NTVntvsch into JSONntvsch'''
    jsonsch = {}
    jsonsch['type']  = ntvsch['type.']  if 'type.'  in ntvsch.keys() else {}
    jsonsch['name']  = ntvsch['name.']  if 'name.'  in ntvsch.keys() else {}
    jsonsch['value'] = ntvsch['value.'] if 'value.' in ntvsch.keys() else {}
    jsonsch['value'] |= {key:val for key, val in ntvsch.items() 
                     if not key in ['type.', 'name.', 'value.']}
    return jsonsch

def _items_to_jsch(schema):
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
