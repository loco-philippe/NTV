# -*- coding: utf-8 -*-
"""

"""
from jsonschema import validate

schntv = {   "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/ntv.schema.json",
    "title": "NTV",
    "description": "schema for NTV entities",
    
    "type": "object",
    "properties": {
        "NTVentity": { "enum" : ["NtvSingle", "NtvList"] },
        "NTVname":   { "type": "string" },
        "NTVtype":   { "$ref": "#/$defs/types" } 
    },
    "$defs":{
        "json":    { "type": [ "boolean", "array", "null", "object", "number", "integer", "string" ] },
        "listNTV": { "type": "array", "items": { "$ref": "#" } },
        "types":   { "enum": [ "int32", "float", "point", "date", "string", "boolean", "object"] } 
    }, 
    "allOf": [ 
        { "$comment": "test consistency of the structure",
        "if":  {"properties":{ "NTVentity": {"const": "NtvList"} } },
        "then":{"properties":{ "NTVvalue":{ "$ref": "#/$defs/listNTV" } },
                "required": ["NTVentity", "NTVvalue"] },
        "else":{"properties":{ "NTVvalue":{ "$ref": "#/$defs/json" } },
                "required": ["NTVentity", "NTVvalue", "NTVtype"] } 
        },
        {"$comment": "test consistency of the NtvValue",
        "if":  {"properties":{ "NTVtype": {"const": "int32"}, "NTVentity": {"const": "NtvSingle"} } },
        "then":{"properties":{ "NTVvalue":{"type": "integer"} } } }
    ] }

val1 = {"NTVentity": "NtvSingle", "NTVtype": "string", "NTVname": "val1", "NTVvalue": 'truc'}
val2 = {"NTVentity": "NtvSingle", "NTVtype": "int32", "NTVname": "val2", "NTVvalue": 3}
val3 = {"NTVentity": "NtvSingle", "NTVtype": "object", "NTVname": "val3", "NTVvalue": {"v": 5, "r":3}}
val4 = {"NTVentity": "NtvSingle", "NTVtype": "boolean", "NTVname": "val4", "NTVvalue": True}

lis1 = {"NTVentity": "NtvList", "NTVname": "lis1", "NTVvalue": [val1, val2] }
lis2 = {"NTVentity": "NtvList", "NTVname": "lis1", "NTVvalue": [lis1, val3] }

print(validate(val1, schema=schntv))
print(validate(val2, schema=schntv))
print(validate(val3, schema=schntv))
print(validate(val4, schema=schntv))
print(validate(lis1, schema=schntv))
print(validate(lis2, schema=schntv))