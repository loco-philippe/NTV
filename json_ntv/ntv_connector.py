# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `ntv` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

It contains the child classes of `NtvConnector` abstract class.
"""
import datetime

from shapely import geometry
from util import util
from namespace import NtvType, Namespace, str_type     
from ntv import Ntv, NtvConnector
import pandas as pd
    
class DataFrameConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''
    
    @staticmethod    
    def from_ntv(ntv_value):
        ntv = Ntv.obj(ntv_value)
        df = pd.DataFrame({ d.ntv_name : SeriesConnec.from_ntv(d) for d in ntv})
        if 'index' in df.columns:
            return df.set_index('index')
        return df
    
class SeriesConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''
    type_to_dtype = {'date': 'datetime64[ns]', 'datetime': 'datetime64[ns]', 'string': 'string', 'int32': 'int32', 'int64': 'int64' }
    dtype_to_type = {val:key for key, val in type_to_dtype.items()}
    
    @staticmethod    
    def from_ntv(ntv_value):
        dtype = None
        ntv = Ntv.obj(ntv_value)
        if ntv.ntv_type and ntv.ntv_type.long_name in SeriesConnec.type_to_dtype:
            dtype = SeriesConnec.type_to_dtype[ntv.ntv_type.long_name]
        return pd.Series(ntv.to_obj(encode_format='obj', simpleval=True), 
                         name=ntv.ntv_name, dtype=dtype)        