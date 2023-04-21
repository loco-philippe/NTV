# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `NTV.ntv_connector` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

It contains :
    - methods `from_csv` and `to_csv` to convert CSV files and 'tab' NTV entity
    - the child classes of `NTV.json_ntv.ntv.NtvConnector` abstract class.
"""
import csv
import json
import pandas as pd

from json_ntv.ntv import Ntv, NtvConnector, NtvSet, NtvList, NtvSingle, NtvError

def from_csv(file_name, single_tab=True, dialect='excel', **fmtparams):
    ''' return a 'tab' NtvSingle from a csv file
    
    *parameters*
    
    - **file_name** : name of the csv file
    - **single_tab** : boolean (default True) - if True return a 'tab' NtvSingle,
    else return a NtvSet.
    - **dialect, fmtparams** : parameters of csv.DictReader object'''
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', **fmtparams)
        names = reader.fieldnames
        list_ntv_value = [[] for nam in names]
        for row in reader:
            for ind_field, val in enumerate(list(row.values())):
                list_ntv_value[ind_field].append(json.loads(val))
    list_ntv = []
    for ind_field, field in enumerate(names):
        list_ntv.append(NtvList(list_ntv_value[ind_field], *Ntv.from_obj_name(field)[:2]))
    if single_tab:
        return NtvSingle(NtvSet(list_ntv, None, None).to_obj(), None, 'tab')
    return NtvSet(list_ntv, None, None)


def to_csv(file_name, ntv, restval='', extrasaction='raise', dialect='excel', *args, **kwds):
    ''' convert a 'tab' NtvSingle into csv file and return the file name
    
    *parameters*
    
    - **file_name** : name of the csv file
    - **ntv** : 'tab' NtvSingle to convert
    - **restval, extrasaction, dialect, args, kwds** : parameters of csv.DictWriter object'''
    if isinstance(ntv, NtvSingle):
        ntv_set = Ntv.obj(ntv.ntv_value)
    else:
        ntv_set = ntv
    list_ntv = [Ntv.obj(field) for field in ntv_set]
    fieldnames = [ntv_field.obj_name(string=True) for ntv_field in list_ntv]
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=restval, extrasaction=extrasaction, 
                                dialect=dialect, *args, **kwds)
        writer.writeheader()
        for i in range(len(list_ntv[0])):
            writer.writerow({name: field_ntv[i].to_obj(field_ntv.ntv_type, encoded=True)
                             for name, field_ntv in zip(fieldnames, list_ntv)})
    return file_name
    
class IlistConnec(NtvConnector):
    '''NTV connector for Ilist'''
    
    clas_obj = 'Ilist'

    @staticmethod
    def from_ntv(ntv_value):
        ''' convert ntv_value into the return object'''
        from observation import Ilist
        print('ok')
        ntv = Ntv.obj(ntv_value)
        return Ilist.from_ntv(ntv)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, json-value)'''
        return (self.name, 'tab', self.to_ntv().to_obj())


class DataFrameConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''

    clas_obj = 'DataFrame'

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
    clas_obj = 'Series'

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
