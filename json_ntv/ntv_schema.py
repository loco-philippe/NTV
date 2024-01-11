# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:31:23 2024

@author: phili
"""

import json
from copy import copy
import pathlib

import json_ntv
from json_ntv.ntv import Ntv
from json_ntv.namespace import from_file
from jsonpointer import resolve_pointer

file = pathlib.Path(json_ntv.__file__).parent.parent / "RFC" / "NTV_NTVschema_namespace.ini"
from_file(file, '$NTVschema.')

def sh_expand(ntv_list):
    
    return {'value' : [ntv.ntv_value for ntv in ntv_list.ntv_value],
            'name'  : [ntv.ntv_name if ntv.ntv_name else None for ntv in ntv_list.ntv_value], 
            'type'  : [ntv.type_str for ntv in ntv_list.ntv_value]}

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

def validate(ntv_data, sch):
    print('validate :')
    print('    ', ntv_data)
    print('    ', sch)
    
def navigate(data, sch):
    ntv_data = Ntv.obj(data)
    p_data = str(ntv_data.pointer())
    sch_p = '/' + list(sch.keys())[0]
    mapping = {p_data : sch_p}
    validate(ntv_data, sch)
    for ntv in list(ntv_data.tree)[1:]:
        parent_ntv = ntv.pointer[:-1]
        parent_sch = resolve_pointer(sch, mapping[str(parent_ntv)])
        new_p_data = str(ntv.pointer())
        if 'properties.' in sch_p:
            new_sch_p = sch_p['properties.']
            validate(ntv_data[new_p_data], new_sch_p)
        else:
            print('pas de properties')


        if len(new_p_data) > len(p_data):
            if 'properties.' in sch_p:
                new_sch_p = sch_p['properties.']
                validate(ntv_data[new_p_data], new_sch_p)
            else:
                print('pas de properties')
            p_data = new_p_data        

        if new_p_data == p_data:
            new_sch_p = sch_p 
            validate(ntv_data[new_p_data], new_sch_p)
        elif len(new_p_data) > len(p_data):
            if 'properties.' in sch_p:
                new_sch_p = sch_p['properties.']
                validate(ntv_data[new_p_data], new_sch_p)
            else:
                print('pas de properties')
            p_data = new_p_data
        elif len(new_p_data) == len(p_data):
            print('coté', new_p_data[-1])
            p_data = new_p_data
        elif len(new_p_data) < len(p_data):
            print('haut', new_p_data[-1])
            p_data = new_p_data
