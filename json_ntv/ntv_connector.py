# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `ntv` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

It contains the classes `NtvConnector`(abstract) for NTV entities.
"""
from abc import ABC
import datetime
import json
from json import JSONDecodeError

import cbor2
from shapely import geometry
from util import util
from namespace import NtvType, Namespace, str_type     
from ntv import Ntv, NtvConnector
import pandas as pd
    
class DatConnector(NtvConnector):
    '''NTV connector for datation'''

    @staticmethod    
    def from_ntv(ntv_value):
        return datetime.datetime.fromisoformat(ntv_value)
    
class DataFrameConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''
    
    @staticmethod    
    def from_ntv(ntv_value):
        ntv = Ntv.obj(ntv_value)
        return pd.DataFrame({ d.ntv_name : SeriesConnec.from_ntv(d) for d in ntv})
    
class SeriesConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''
    
    @staticmethod    
    def from_ntv(ntv_value):
        dtype = None
        ntv = Ntv.obj(ntv_value)
        if ntv.ntv_type and ntv.ntv_type.long_name in type_to_dtype:
            dtype = type_to_dtype[ntv.ntv_type.long_name]
        return Series(ntv.to_obj(encode_format='obj', simpleval=True), name=ntv.ntv_name, dtype=dtype)        