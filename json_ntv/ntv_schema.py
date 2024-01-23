# -*- coding: utf-8 -*-
"""
The `ntv_schema` module is part of the `json_ntv` package.

The main function `ntv_validate` validate a NTVdata against a NTVschema.

It also contains functions:
- to convert NTVschema into JSONschema : `_simple_to_jsch`, `_items_to_jsch`,
- to validate a NTVschema : `kw_validate`, `val_items`, `val_simple`, `validat`,
- to convert NTV entity into Json data : `_ntv_to_json`, `_json`, `_pure` 

For more information, see the 
[user guide](https://loco-philippe.github.io/NTV/documentation/user_guide.html) 
or the [github repository](https://github.com/loco-philippe/NTV).

"""

import pathlib

import json_ntv
from json_ntv.ntv import Ntv, NtvList, NtvSingle
from json_ntv.ntv_patch import NtvPointer
from json_ntv.namespace import from_file
from jsonpointer import resolve_pointer
from jsonschema import validate

file = pathlib.Path(json_ntv.__file__).parent.parent / "RFC" / "NTV_NTVschema_namespace.ini"
#from_file(file, '$NTVschema.')

def ntv_validate2(ntv_data, ntv_sch, mode=0):
    valid = True 
    if mode:
        #print('\n           : ', ntv_data)
        #print('           : ', ntv_sch)
        print('  validate : ', ntv_data.pointer()) #, sch)
    if isinstance(ntv_sch, NtvSingle):
        #return val_simple2(ntv_data, ntv_sch, mode)
        ntv_sch = NtvList([ntv_sch])
    for sch in ntv_sch: 
        if sch.name.isdecimal():
            idx = int(sch.name)
            if len(ntv_data) > idx:
                valid &= ntv_validate2(ntv_data.ntv_value[idx], sch.ntv_value, mode)            
                #valid &= ntv_validate2(ntv_data['#/'+idx], sch.ntv_value, mode)            
        elif sch.type_str[:4] == 'sch.' and sch.type_str[-1] == '.':
            valid &= val_prop2(ntv_data, sch, mode)
        elif sch.type_str == "sch.items":
            print('items : ', ntv_data, sch)
        elif sch.type_str[:4] != 'sch.':
            print('json_name : ', ntv_data, sch)
        else:
            valid &= val_simple2(ntv_data, sch, mode)     
    return valid

"""def _simp2(sch):
    return NtvList([ntv for ntv in sch 
                    if ntv.type_str[:4] == 'sch.' and ntv.type_str[-1] != '.'],
                   ntv_name=sch.name)"""

def val_prop2(ntv_data, sch, mode):
    valid = True
    #sch_name = [ntv.name for ntv in sch]
    for ntv in ntv_data:
        p_name = ntv.ntv_name if ntv.ntv_name == sch.name else (ntv.json_name_str if ntv.json_name_str == sch.name else None)
        #p_name = ntv.ntv_name if ntv.ntv_name in sch_name else (ntv.json_name_str if ntv.json_name_str in sch_name else None)
        if not p_name is None:
            valid &= ntv_validate2(ntv, sch, mode)
            #valid &= ntv_validate2(ntv, sch[p_name], mode)
        #elif mode:
        #    print('    not include : ', ntv.pointer()) 
    return valid

def val_simple2(ntv_data, sch, mode) :
    print('simple : ', ntv_data, sch)
    return True

"""def val_pref2(ntv_data, idx, mode):
    valid = True
    if len(ntv_data) > idx:
        return ntv_validate2(ntv.ntv_value[idx], sch_pref, mode)
    return valid"""

def ntv_validate(ntv_data, sch, mode=0):
    valid = True 
    if mode:
        print('  validate : ', ntv_data.pointer()) #, sch)
    simp_sch = _simp(sch)
    if simp_sch:
        valid &= val_simple(ntv_data, simp_sch, mode) 
    if 'properties.' in sch:
        valid &= val_prop(ntv_data, sch['properties.'], mode)
    if 'prefixItems.' in sch:
        valid &= val_pref(ntv_data, sch['prefixItems.'], mode)
    if 'items.' in sch:
        valid &= val_item(ntv_data, sch['items.'], mode)        
    return valid
    
def val_prop(ntv_data, sch, mode):
    valid = True
    for ntv in ntv_data:
        p_name = ntv.ntv_name if ntv.ntv_name in sch else (ntv.json_name_str if ntv.json_name_str in sch else None)
        if not p_name is None:
            valid &= ntv_validate(ntv, sch[p_name], mode)
        #elif mode:
        #    print('    not include : ', ntv.pointer()) 
    return valid

def val_pref(ntv_data, sch, mode):
    valid = True
    for ntv, sch_pref in zip(ntv_data, sch):
        valid &= ntv_validate(ntv, sch_pref, mode)
    return valid

def val_item(ntv_data, sch, mode):
    valid = True
    for ntv in ntv_data:
        valid &= ntv_validate(ntv, sch, mode)
    return valid
    

    
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
        valid &= validat(json_data[part], json_sch[part], part, mode)
    return valid

def validat(json_data, jsch, part, mode):
    '''return the validation (True/False) of a json data conformity to a 'jsch' JSONschema.

    *Parameters*
    
        - **json_data**: json_data to validate
        - **jsch**: json-value - JSONschema
        - **mode**: integer (default 0) - level of information
            - 0: no information
            - 1: list of controls and errors
            - 2: details of errors (traceback)
    '''  
    if mode > 1 and jsch:
        print('    ', part, ' : ', json_data, jsch)
    valid = False
    if mode < 3:
        try:
            valid = validate(json_data, jsch) is None
        except :
            if mode > 0:
                print('  error : ', json_data, 'is not valid with schema : ', jsch)
    else:
        valid = validate(json_data, jsch) is None
    return valid    
    
def _ntv_to_json(ntv_data):  
    '''transform a Ntv entity into a json representation'''
    return {    'value' : ntv_data.ntv_value,
                'name'  : ntv_data.ntv_name, 
                'type'  : ntv_data.type_str}

def _simple_to_jsch(ntvsch):
    '''transform a simple NTVschema into a JSONschema'''
    jsonsch = {}
    jsonsch['type']  = ntvsch['type.']  if 'type.'  in ntvsch.keys() else {}
    jsonsch['name']  = ntvsch['name.']  if 'name.'  in ntvsch.keys() else {}
    jsonsch['value'] = ntvsch['value.'] if 'value.' in ntvsch.keys() else {}
    jsonsch['value'] |= {key:val for key, val in ntvsch.items() 
                     if not key in ['type.', 'name.', 'value.']}
    return _json(jsonsch)

def _json(dic):
    '''transform in a schema leaf NTVkeywords into JSONkeywords'''
    return {(lambda k : k[1:] if k[0] == ':' else k)(key): _json(value) 
            for key, value in dic.items()} if isinstance(dic, dict) else dic
    
def _simp(dic, keywords=None):
    '''return a dict schema without keywords members'''
    keyw = list(keywords) if keywords else []
    keyw += ['properties.', 'prefixItems.', 'items.']
    return {key: val for key, val in dic.items() 
                  if not key in keyw} if isinstance(dic, dict) else dic

    
"""def ntv_validate_old(data, sch, mode=0):
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
        new_p_data = str(ntv.pointer())
        parent_ntv = str(ntv.pointer()[:-1])
        if not parent_ntv in mapping:
            if mode: 
                print('  validate : parent not include', new_p_data)
        else:
            #print('parent_sch : ', parent_ntv)
            #print(mapping)
            parent_sch = resolve_pointer(sch, mapping[parent_ntv])
            if mode:
                print('\nvalidation : ', new_p_data)
            if 'properties.' in parent_sch:
                p_prop = parent_sch['properties.']
                #if ntv.ntv_name in p_prop or ntv.json_name_str in p_prop:
                p_name = ntv.ntv_name if ntv.ntv_name in p_prop else (ntv.json_name_str if ntv.json_name_str in p_prop else None)
                if not p_name is None:
                    mapping[new_p_data] = mapping[parent_ntv] + '/properties.' + '/' + p_name
                    valid &= kw_validate('properties', ntv_data['#' + new_p_data], 
                             _pure(p_prop[p_name]), mode)
            if 'prefixItems.' in parent_sch:
                row = list(ntv.pointer(index=True))[-1]
                p_item = parent_sch['prefixItems.']
                if len(p_item) > row:
                    mapping[new_p_data] = mapping[parent_ntv] + '/prefixItems.' + '/' + str(row)
                    valid &= kw_validate('prefixItems ' + str(row), ntv_data['#' + new_p_data],
                                         _pure(p_item[row]), mode)
            if mode and not new_p_data in mapping:
                print('  validate : not include', new_p_data)
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
    print('kw_val : ', ntv_data, sch)
    if mode:
        print('  validate : ', keyword, 
              ntv_data.ntv_name if keyword == 'properties' else '')
    valid = val_items(ntv_data, {'items.': sch['items.']}, mode) if 'items.' in sch else True
    #valid = val_items(ntv_data, sch['items.'], mode) if 'items.' in sch.keys() else True
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
    valid = True
    for ntv in ntv_data:
        valid &= ntv_validate(ntv, items_sch, mode)
        new_p_data = str(ntv.pointer())
        parent_ntv = str(ntv_data.pointer())
        row = list(ntv.pointer(index=True))[-1]
        p_item = items_sch
        mapping[new_p_data] = mapping[parent_ntv] + '/items.'
        valid &= kw_validate('items ' + str(row), ntv_data['#' + new_p_data],
                             _pure(p_item), mode)
    return valid
    #return validat(_ntv_to_json(ntv_data), _items_to_jsch(items_sch), mode)

def _items_to_jsch(schema):
    '''transform an items NTVschema into a JSONschema'''
    schema = schema['items.'] if 'items.' in schema else schema
    name  = {'name':  {'items': schema['name.']}}  if 'name.'  in schema else {}
    typ   = {'type':  {'items': schema['type.']}}  if 'type.'  in schema else {}
    val   = schema['value.'] if 'value.' in schema else {}
    value = {'value': {'items': val | {k:v for k, v in schema.items() 
                                       if not k in ['name.', 'type.']}}}
    return {'properties' : value | name | typ }

def _pure(dic, keywords=None):
    '''return a dict schema without keywords members'''
    keyw = list(keywords) if keywords else []
    keyw += ['properties.', 'prefixItems.']
    return _json({key: val for key, val in dic.items() 
                  if not key in keyw}) if isinstance(dic, dict) else dic
"""
class NtvSchemaError(Exception):
    ''' NtvSchema Exception'''
    # pass
