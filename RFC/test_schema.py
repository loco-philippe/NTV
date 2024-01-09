# -*- coding: utf-8 -*-
"""

"""
from jsonschema import validate
from json_ntv import Ntv

schntv = {   "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/ntv.schema.json",
    "title": "NTV",
    "description": "schema for NTV entities",
    
    "properties": {
        "E": { "enum" : ["NtvSingle", "NtvList"] },
        "N": { "type": "string" },
        "T": { "$ref": "#/$defs/types" },
    },
    
    "$defs":{
        "listNTV": { "type": "array", "items": { "$ref": "#" } },
        "types":   { "enum": [ "int32", "float", "point", "date", "string", "boolean", "object", "json", ""] } 
    }, 
    "allOf": [ 
        { "$comment": "test consistency of the structure",
        "if":  {"properties":{ "E": {"const": "NtvList"} } },
        "then":{"properties":{ "V":{ "$ref": "#/$defs/listNTV" } },
                "required": ["E", "V"] },
        "else":{"properties":{ "V": True },
                "required": ["E", "V", "T"] } 
        }
    ] }

val1 = {"E": "NtvSingle", "T": "string", "N": "val1", "V": 'truc'}
val2 = {"E": "NtvSingle", "T": "int32", "N": "val2", "V": 3}
val3 = {"E": "NtvSingle", "T": "object", "N": "val3", "V": {"v": 5, "r":3}}
val4 = {"E": "NtvSingle", "T": "boolean", "N": "val4", "V": True}

lis1 = {"E": "NtvList", "N": "lis1", "V": [val1, val2] }
lis2 = {"E": "NtvList", "N": "lis1", "V": [lis1, val3] }
lis3 = {"E": "NtvList", "N": "lis1", "V": 45 }

validate(val1, schema=schntv)
validate(val2, schema=schntv)
validate(val3, schema=schntv)
validate(val4, schema=schntv)
validate(lis1, schema=schntv)
validate(lis2, schema=schntv)

schntv2 = {   "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/ntv.schema.json",
    "title": "NTV values",
    "description": "validation of NTV values",   
    
    "$comment": "test consistency of the V",
    "allOf": [ 
        {"if":  {"properties":{ "T": {"const": "int32"}, "E": {"const": "NtvSingle"} } },
         "then":{"properties":{ "V": {"type": "integer"} } } },
        
        {"if":  {"properties":{ "T": {"const": "date"}, "E": {"const": "NtvSingle"} } },
         "then":{"properties":{ "V": {"pattern": "(19\d\d|20\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"} } } }
    ] }

validate(lis2, schema=schntv2)

#val2 = {"E": "NtvSingle", "T": "int32", "N": "val2", "V": 3.5}
#print(validate(val2, schema=schntv2))

a = [{'test:int32':25, ':date': '2001-13-25'}, 32]
validate(Ntv.obj(a).expand(), schema=schntv2)

a= {'test': 45, 'str': 'truc'}

scha = {'properties': {'test': {"maximum": 100}}}
validate(a, schema=scha)


#exemple :
a = { 'test': 45 }
n = { 'E': 'NtvSingle', 'N': 'test', 'T': 'json', 'V': 45}

#single :   "properties": {"xx": { yy } }
#      ->   "properties": {"N": { "const": "xx"},"V": { yy }}
scha = { "properties": { "test": { "maximum": 100}}}
validate(a, schema=scha) 

schn = { "properties": {"N": { "const": "test"},"V": { "maximum": 100}}}
validate(n, schema=schn) 

a = { 'test': 45, 'str': 'truc'}  
n = {'E': 'NtvList', 'N': '', 'T': '',
     'V': [{'E': 'NtvSingle', 'N': 'test', 'T': 'json', 'V': 45},
           {'E': 'NtvSingle', 'N': 'str', 'T': 'json', 'V': 'truc'}]}

#list :     "properties": {"xx": { yy } } 
#      ->   "properties": {"V" : {"contains": {"N": { "const": "xx"},"V": { yy }}}}
scha = { "properties": { "test": { "maximum": 100}}}
validate(a, schema=scha)

schn = { "properties": {"V" : {"contains": {"properties": {"N": { "const": "test"},"V": { "maximum": 100}}}}}}
validate(n, schema=schn)  


"""
json :
    properties:
        {name: value_schema}
    propertiesType:
        {name: type_schema}
    patternProperties:
        {pattern_name: pat_schema}
    patternPropertiesType:
        {pattern_name: type_schema}
    additionalProperties: add_schema
    additionalPropertiesType: add_type_schema
    unevaluatedProperties: uneval_schema
    unevaluatedPropertiesType: uneval_type_schema    
    required: [req_name]
    propertyNames: names_schema
    minProperties: int
    maxProperties: int
    
    items: items_schema
    prefixItems: [item_schema]
    prefixItemsType: [name_type_schema]
    unevaluatedItems: uneval_schema
    unevaluatedItemsType: uneval_type_schema
    contains: cont_schema
    containsType: cont_type_schema
    minContains: int
    minContainsType: int
    maxContains: int
    maxContainsType: int
    minItems: int
    maxItems: int
    uniqueItems: boolean
    
NTV:
    items
    namesValues: {}
    namesTypes: {}
    typesValues: {}
    patternxxx: {}
    additionalxxx
    unevaluatedxxx
    
"""