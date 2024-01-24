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


from json_ntv.ntv import Ntv, NtvList, NtvSingle
from jsonschema import validate

# %% interface json schema
def validat(json_data, json_sch, part, mode):
    '''return the validation (True/False) of a json data conformity to a 'json_sch' JSONschema.

    *Parameters*
    
        - **json_data**: json_data to validate
        - **json_sch**: json-value - JSONschema
        - **mode**: integer (default 0) - level of information
            - 0: no information
            - 1: list of controls and errors
            - 2: details of errors (traceback)
    '''  
    if mode > 1 and json_sch:
        print('    ', part, ' : ', json_data, json_sch)
    valid = False
    if mode < 3:
        try:
            valid = validate(json_data, json_sch) is None
        except :
            if mode > 0:
                print('  error : ', json_data, 'is not valid with schema : ', json_sch)
    else:
        valid = validate(json_data, json_sch) is None
    return valid    

def _ntv_to_json(ntv_data):  
    '''transform a Ntv entity into a json representation'''
    return {    'value' : ntv_data.ntv_value,
                'name'  : ntv_data.ntv_name, 
                'type'  : ntv_data.type_str}
    
# %% validate schema ntv
def ntv_validate2(ntv_data, ntv_sch, mode=0):
    '''return the validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.

    *Parameters*

    - **ntv_data**: Ntv entity (json_ntv or NTV)
    - **sch**: NTV_schema (json_ntv or NTV)
    - **mode**: integer (default 0) - level of information
        - 0: no information
        - 1: list of controls and errors
        - 2: details of errors (traceback)
    '''      
    ntv_data = Ntv.obj(ntv_data)
    ntv_sch = Ntv.obj(ntv_sch)
    valid = True 
    if mode:
        print('  validate : ', ntv_data.pointer()) #, sch)
    if isinstance(ntv_sch, NtvSingle):
        ntv_sch = NtvList([ntv_sch])
    for sch in ntv_sch: 
        if sch.name.isdecimal():
            idx = int(sch.name)
            if len(ntv_data) > idx:
                valid &= ntv_validate2(ntv_data.ntv_value[idx], sch.ntv_value, mode)            
        elif sch.type_str == "sch.items":
            valid &= _val_item2(ntv_data, sch, mode)  
        elif sch.type_str[:4] == 'sch.' and sch.type_str[-1] == '.':
            valid &= _val_prop2(ntv_data, sch, mode)
        elif sch.type_str[:4] != 'sch.':
            valid &= _val_prop2(ntv_data, sch, mode)
        else:
            valid &= _val_simple2(ntv_data, sch, mode)     
    return valid

def _val_prop2(ntv_data, sch, mode):
    '''return the properties validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.'''
    valid = True
    for ntv in ntv_data:
        if ntv.ntv_name and ntv.ntv_name == sch.name:
            valid &= ntv_validate2(ntv, sch, mode)
            break
        if ntv.json_name_str and ntv.json_name_str == sch.json_name_str:
            valid &= ntv_validate2(ntv, Ntv.obj({'sch.':sch.val}), mode)
            break
    return valid

def _val_simple2(ntv_data, sch, mode) :
    '''return the validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.'''
    if not sch:
        return True
    json_data = _ntv_to_json(ntv_data)
    json_sch  = _simple_to_jsch2(sch)
    valid = True
    for part in ['value', 'type', 'name']:
        valid &= validat(json_data[part], json_sch[part], part, mode)
    return valid

def _val_item2(ntv_data, sch, mode):
    '''return the items validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.'''
    valid = True
    sch_item = Ntv.obj({'sch.':sch.val})
    if isinstance(ntv_data, NtvSingle):
        ntv_data = NtvList([ntv_data])
    for ntv in ntv_data:
        valid &= ntv_validate2(ntv, sch_item, mode)
    return valid

def _replace(keyword):
    keyw = keyword[1:] if keyword[0] == ':' else keyword
    keyw = keyw[4:] if keyw[0:4] == 'sch.' else keyw
    keyw = 'type' if keyw == 'typeNtv' else keyw
    keyw = 'name' if keyw == 'nameNtv' else keyw
    keyw = 'value' if keyw == 'valeNtv' else keyw
    return keyw

def _json2(dic):
    '''in a schema leaf, transform NTVkeywords into JSONkeywords'''
    return {_replace(key): _json2(value) 
            for key, value in dic.items()} if isinstance(dic, dict) else dic

def _simple_to_jsch2(ntvsch):
    '''transform a simple NTVschema into a JSONschema'''
    jssch = _json2(Ntv.to_obj(ntvsch))
 
    jsonsch = {}
    jsonsch['type']  = jssch['type']  if 'type'  in jssch.keys() else {}
    jsonsch['name']  = jssch['name']  if 'name'  in jssch.keys() else {}
    jsonsch['value'] = jssch['value'] if 'value' in jssch.keys() else {}
    jsonsch['value'] |= {key:val for key, val in jssch.items() 
                     if not key in ['type', 'name', 'value']}
    return jsonsch


# %% validate schema json
def ntv_validate(ntv_data, sch, mode=0):
    '''return the validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.

    *Parameters*

    - **ntv_data**: Ntv entity (json_ntv or NTV)
    - **sch**: json-value - NTVschema (JsonSchema keywords)
    - **mode**: integer (default 0) - level of information
        - 0: no information
        - 1: list of controls and errors
        - 2: details of errors (traceback)
    '''  
    ntv_data = Ntv.obj(ntv_data)
    valid = True 
    if mode:
        print('  validate : ', ntv_data.pointer()) #, sch)
    simp_sch = _simp(sch)
    if simp_sch:
        valid &= _val_simple(ntv_data, simp_sch, mode) 
    if 'properties' in sch:
        valid &= _val_prop(ntv_data, sch['properties'], mode)
    if 'prefixItems' in sch:
        valid &= _val_pref(ntv_data, sch['prefixItems'], mode)
    if 'items' in sch:
        valid &= _val_item(ntv_data, sch['items'], mode)        
    return valid
    
def _val_prop(ntv_data, sch, mode):
    '''return the properties validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.'''
    valid = True
    for idx,ntv in enumerate(ntv_data):
        p_name = ntv.ntv_name if ntv.ntv_name in sch else (ntv.json_name_str if ntv.json_name_str in sch else None)
        p_name = p_name if p_name else (str(idx) if str(idx) in sch else None)
        if not p_name is None:
            valid &= ntv_validate(ntv, sch[p_name], mode)
    return valid

def _val_pref(ntv_data, sch, mode):
    '''return the prefixItems validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.'''
    valid = True
    for ntv, sch_pref in zip(ntv_data, sch):
        valid &= ntv_validate(ntv, sch_pref, mode)
    return valid

def _val_item(ntv_data, sch, mode):
    '''return the items validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.'''
    valid = True
    for ntv in ntv_data:
        valid &= ntv_validate(ntv, sch, mode)
    return valid
       
def _val_simple(ntv_data, sch, mode) :
    '''return the validation (True/False) of a NTV entity conformity to a 'sch' NTVschema.'''  
    if not sch:
        return True
    json_data = _ntv_to_json(ntv_data)
    json_sch  = _simple_to_jsch(sch)
    valid = True
    for part in ['value', 'type', 'name']:
        valid &= validat(json_data[part], json_sch[part], part, mode)
    return valid

def _simple_to_jsch(ntvsch):
    '''transform a simple NTVschema into a JSONschema'''
    jsonsch = {}
    jsonsch['type']  = ntvsch['typeNtv']  if 'typeNtv'  in ntvsch else {}
    jsonsch['name']  = ntvsch['nameNtv']  if 'nameNtv'  in ntvsch else {}
    jsonsch['value'] = ntvsch['valueNtv'] if 'valueNtv' in ntvsch else {}
    jsonsch['value'] |= {key:val for key, val in ntvsch.items() 
                     if not key in ['typeNtv', 'nameNtv', 'valueNtv', 'propertyNames']}
    jsonsch['name'] |= ntvsch['propertyNames'] if 'propertyNames' in ntvsch else {}
    return _json(jsonsch)

def _json(dic):
    '''in a schema leaf, transform NTVkeywords into JSONkeywords'''
    return {(lambda k : k[1:] if k[0] == ':' else k)(key): _json(value) 
            for key, value in dic.items()} if isinstance(dic, dict) else dic
    
def _simp(dic, keywords=None):
    '''return a dict schema without keywords members'''
    keyw = list(keywords) if keywords else []
    keyw += ['properties', 'prefixItems', 'items']
    return {key: val for key, val in dic.items() 
                  if not key in keyw} if isinstance(dic, dict) else dic

class NtvSchemaError(Exception):
    ''' NtvSchema Exception'''
    # pass
