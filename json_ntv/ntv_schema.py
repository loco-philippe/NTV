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