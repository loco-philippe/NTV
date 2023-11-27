# -*- coding: utf-8 -*-
"""

"""
from jsonschema import validate
from json_ntv import Ntv

schntv = {   "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/ntv.schema.json",
    "title": "NTV",
    "description": "schema for NTV entities",
    
    "type": "object",
    "properties": {
        "E": { "enum" : ["NtvSingle", "NtvList"] },
        "N":   { "type": "string" },
        "T":   { "$ref": "#/$defs/types" } 
    },
    "$defs":{
        "json":    { "type": [ "boolean", "array", "null", "object", "number", "integer", "string" ] },
        "listNTV": { "type": "array", "items": { "$ref": "#" } },
        "types":   { "enum": [ "int32", "float", "point", "date", "string", "boolean", "object", "json", ""] } 
    }, 
    "allOf": [ 
        { "$comment": "test consistency of the structure",
        "if":  {"properties":{ "E": {"const": "NtvList"} } },
        "then":{"properties":{ "V":{ "$ref": "#/$defs/listNTV" } },
                "required": ["E", "V"] },
        "else":{"properties":{ "V":{ "$ref": "#/$defs/json" } },
                "required": ["E", "V", "T"] } 
        }
    ] }

val1 = {"E": "NtvSingle", "T": "string", "N": "val1", "V": 'truc'}
val2 = {"E": "NtvSingle", "T": "int32", "N": "val2", "V": 3}
val3 = {"E": "NtvSingle", "T": "object", "N": "val3", "V": {"v": 5, "r":3}}
val4 = {"E": "NtvSingle", "T": "boolean", "N": "val4", "V": True}

lis1 = {"E": "NtvList", "N": "lis1", "V": [val1, val2] }
lis2 = {"E": "NtvList", "N": "lis1", "V": [lis1, val3] }

print(validate(val1, schema=schntv))
print(validate(val2, schema=schntv))
print(validate(val3, schema=schntv))
print(validate(val4, schema=schntv))
print(validate(lis1, schema=schntv))
print(validate(lis2, schema=schntv))

schntv2 = {   "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/ntv.schema.json",
    "title": "NTV values",
    "description": "validation of NTV values",   
    "type": "object",
    "properties": {"E": { }, "N": { }, "T": { } },
    
    "$comment": "test consistency of the V",
    "allOf": [ 
        #{"if":  {"properties":{ "T": {"const": "int32"}, "E": {"const": "NtvSingle"} } },
        #"then":{"properties":{ "V":{"type": "integer"} } } },
        {"if":  {"properties":{ "T": {"const": "date"}, "E": {"const": "NtvSingle"} } },
        #"then":{"properties":{ "V": {"type": "string", "pattern": "((19|20)\d{2}-(0[1-9]|1[1,2])-0[1-9]|[12][0-9]|3[01])"} } } }
        #"then":{"properties":{ "V": {"type": "string", "pattern": "(0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])[-/](19\d\d|20\d\d)"} } } }
        "then":{"properties":{ "V": {"type": "string", "pattern": "0[1-9]|1[0-2]"} } } }
    ] }

print(validate(lis2, schema=schntv2))

#val2 = {"E": "NtvSingle", "T": "int32", "N": "val2", "V": 3.5}
#print(validate(val2, schema=schntv2))

"""a = [{'test:int32':25, ':date': "(800)FLOWERS"}, 32]
validate(Ntv.obj(a).expand(), schema=schntv2)
"""
#a = [{'test:int32':25, ':date': '2001-12-25'}, 32]
a = [{'test:int32':25, ':date': 'a0'}, 32]
validate(Ntv.obj(a).expand(), schema=schntv2)
a = [{'test:int32':25, ':date': '2001-13-25'}, 32]
validate(Ntv.obj(a).expand(), schema=schntv2)