# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `ntv_connector` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

It contains the child classes of `NtvConnector` abstract class.
"""
import json
import pandas as pd

from ntv import Ntv, NtvConnector, NtvSet, NtvList


class DataFrameConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''

    clas_obj = 'dataframe'

    @staticmethod
    def from_ntv(ntv_value):
        ''' convert ntv_value into the return object'''
        ntv = Ntv.obj(ntv_value)
        dataframe = pd.DataFrame(
            {d.ntv_name: SeriesConnec.from_ntv(d) for d in ntv})
        if 'index' in dataframe.columns:
            return dataframe.set_index('index')
        return dataframe

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, value)'''
        df2 = self.reset_index()
        return (None, 'tab', NtvSet([SeriesConnec.to_ntv(df2[colon])[2]
                                     for colon in df2.columns]).to_obj())


class SeriesConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''
    type_to_dtype = {'date': 'datetime64[ns]', 'datetime': 'datetime64[ns]',
                     'string': 'string', 'int32': 'int32', 'int64': 'int64',
                     'float': 'float', 'float32': 'float32', }
    dtype_to_type = {'datetime64[ns]': 'datetime', 'string': 'string', 'int32': 'int32',
                     'int64': 'json'}
    clas_obj = 'series'

    @staticmethod
    def from_ntv(ntv_value):
        ''' convert ntv_value into the return object'''
        dtype = None
        ntv = Ntv.obj(ntv_value)
        if ntv.ntv_type and ntv.ntv_type.long_name in SeriesConnec.type_to_dtype:
            dtype = SeriesConnec.type_to_dtype[ntv.ntv_type.long_name]
        return pd.Series(ntv.to_obj(encode_format='obj', simpleval=True),
                         name=ntv.ntv_name, dtype=dtype)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, value)'''
        ntv_type = None
        dtype = self.dtype.name
        if dtype in SeriesConnec.dtype_to_type:
            if SeriesConnec.dtype_to_type[dtype] != 'json':
                ntv_type = SeriesConnec.dtype_to_type[dtype]
            ntv_value = json.loads(self.to_json(orient='records', date_format='iso',
                                                default_handler=str))
        elif self.dtype.name == 'object':
            ntv_value = self.to_list()
        ntv_name = self.name
        return (None, 'field', NtvList(ntv_value, ntv_name, ntv_type).to_obj())
