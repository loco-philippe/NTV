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

file = pathlib.Path(json_ntv.__file__).parent.parent / "RFC" / "NTV_NTVschema_namespace.ini"
from_file(file, '$NTVschema.')

def val_maxItems(ntv_data, sch) : pass
#def val_properties(ntv_data, sch) : pass
val_properties = None

VALID = {'maxItems' : val_maxItems, 'properties': val_properties}

def sh_expand(ntv_data):
    
    return {'value' : [ntv.ntv_value for ntv in ntv_data.ntv_value],
            'name'  : [ntv.ntv_name if ntv.ntv_name else None for ntv in ntv_data.ntv_value], 
            'type'  : [ntv.type_str for ntv in ntv_data.ntv_value]
            } if isinstance (ntv_data, NtvList) else {
                'value' : ntv_data.ntv_value,
                'name'  : ntv_data.ntv_name, 
                'type'  : ntv_data.ntv_type}
 
def sh_items(schema):
    name = {}
    typ = {}
    schema = schema['items.'] if 'items.' in schema else schema
    if 'name.' in schema:
        name = {'name': {'items': schema['name.']}}
        del(schema['name.'])
    if 'type.' in schema:
        typ = {'type': {'items': schema['type.']}}
        del(schema['type.'])
    value = {'value': {'items': schema}} if schema else {}
    js_items = {'properties' : value | name | typ }
    return js_items

def val_maxItems(ntv_data, sch) : 
    print('    ', ntv_data)
    print('    ', sch)
    return True
    
def val_properties(ntv_data, sch) :
    print('    ', ntv_data)
    print('    ', sch)
    return True

def validate(keyword, ntv_data, sch):
    json_data = sh_expand(ntv_data)
    valid = False
    if keyword in VALID:
        print(keyword)
        valid = VALID[keyword](json_data['value'], sch)
    print('validate : ', keyword, valid)


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
    validate('global', ntv_data, _pure(sch[sch_p]))
    for ntv in list(ntv_data.tree)[1:]:
        parent_ntv = ntv.pointer()[:-1]
        parent_sch = resolve_pointer(sch, mapping[str(parent_ntv)])
        new_p_data = str(ntv.pointer())
        if 'properties.' in parent_sch:
            if ntv.ntv_name in parent_sch['properties.']:
                mapping[new_p_data] = mapping[str(parent_ntv)] + '/properties.' + '/' + ntv.ntv_name
                validate('properties', ntv_data['#' + new_p_data], 
                         _pure(parent_sch['properties.'][ntv.ntv_name]))
            else:
                validate('not include', ntv_data['#' + new_p_data], True)
        elif 'prefixItems.' in parent_sch:
            row = NtvPointer.pointer_list(ntv.pointer()[-1])[0]
            if len(parent_sch['prefixItems.']) > row:
                mapping[new_p_data] = mapping[str(parent_ntv)] + '/prefixItems.' + '/' + str(row)
                validate('prefixItems', ntv_data['#' + new_p_data], 
                         _pure(parent_sch['prefixItems.'][row]))
            else:
                validate('not include', ntv_data['#' + new_p_data], True)
        else:
            print('pas de properties et de PrefixItems')

