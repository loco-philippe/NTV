# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `NTV.ntv_connector` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

It contains :
    - methods `from_csv` and `to_csv` to convert CSV files and 'tab' NTV entity
    - the child classes of `NTV.json_ntv.ntv.NtvConnector` abstract class:
        - `IindexConnec`:    'field' connector 
        - `IlistConnec`:     'tab' connector 
        - `DataFrameConnec`: 'tab' connector 
        - `SeriesConnec`:    'field' connector 
"""
import csv
import json
import pandas as pd

from json_ntv.ntv import Ntv, NtvConnector, NtvList, NtvSingle

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
        return NtvSingle(NtvList(list_ntv, None, None).to_obj(), None, 'tab')
    return NtvList(list_ntv, None, None)


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

class IindexConnec(NtvConnector):
    '''NTV connector for Iindex'''
    
    clas_obj = 'Iindex'

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        from observation import Iindex
        ntv = Ntv.obj(ntv_value)
        return Iindex.from_ntv(ntv)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, json-value)'''
        return (None, 'field', self.to_ntv(name=True).to_obj())
    
class IlistConnec(NtvConnector):
    '''NTV connector for Ilist'''
    
    clas_obj = 'Ilist'

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        from observation import Ilist
        ntv = Ntv.obj(ntv_value)
        return Ilist.from_ntv(ntv)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, json-value)'''
        return (None, 'tab', self.to_ntv().to_obj())


class DataFrameConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''

    clas_obj = 'DataFrame'

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        ntv = Ntv.obj(ntv_value)
        leng = max([len(ntvi) for ntvi in ntv.ntv_value])
        #keys_ntv = [d[1] if len(d) == 2 and len(d[1]) == leng else None for d in ntv]
        df = pd.DataFrame({d.name: SeriesConnec.from_ntv(d, leng=leng) for d in ntv})
        #    {d.ntv_name: SeriesConnec.from_ntv(d, index=keys, leng=leng) for d, keys in zip(ntv, keys_ntv)})
        if 'index' in df.columns:
            return df.set_index('index')
        return df

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, value)'''
        df2 = self.reset_index()
        return (None, 'tab', NtvList([SeriesConnec.to_ntv(df2[colon])[2]
                                     for colon in df2.columns]).to_obj())


class SeriesConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''
    type_to_dtype = {'date': 'datetime64[ns]', 'datetime': 'datetime64[ns]',
                     'string': 'string', 'int32': 'int32', 'int64': 'int64',
                     'float': 'float', 'float32': 'float32', 'boolean': 'boolean'}
    dtype_to_type = {'datetime64[ns]': 'datetime', 'string': 'string', 
                     'int32': 'int32', 'int64': 'json', 'float': 'json', 
                     'float32': 'float32', 'boolean': 'json', 'object': None}
    clas_obj = 'Series'

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        option = {'index':None, 'leng':None} | kwargs 
        dtype = None
        ntv = Ntv.obj(ntv_value)
        codes = len(ntv) == 2 and len(ntv[1]) > 1
        if codes:
            cod = ntv[1].to_obj(simpleval=True)
            ntv = ntv[0]
        ntv_obj = ntv.to_obj(encode_format='obj', simpleval=True)
        if ntv.type_str in SeriesConnec.type_to_dtype:
            dtype = SeriesConnec.type_to_dtype[ntv.type_str]
        if isinstance(ntv, NtvSingle) and option['leng']:
            data = [ntv_obj] * option['leng']
        elif len(ntv) == 1 and option['leng']:
            data = ntv_obj * option['leng']
        elif not codes:
            data = ntv_obj
        else:
            cat = pd.CategoricalDtype(categories=pd.Series(ntv_obj))
            data = pd.Categorical.from_codes(codes=cod, dtype=cat)
        return pd.Series(data, name=ntv.ntv_name, index=option['index'] , dtype=dtype)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, value)'''
        dtype = self.dtype.name
        ntv_type = None
        if dtype in SeriesConnec.dtype_to_type and SeriesConnec.dtype_to_type[dtype] != 'json':
            ntv_type = SeriesConnec.dtype_to_type[dtype]
        if dtype in SeriesConnec.dtype_to_type:
            #if SeriesConnec.dtype_to_type[dtype] != 'json':
            #    ntv_type = SeriesConnec.dtype_to_type[dtype]
            ntv_value = json.loads(self.to_json(orient='records', date_format='iso',
                                                default_handler=str))
        elif dtype == 'object':
            ntv_value = self.to_list()
        elif dtype == 'category':
            sr_codec = pd.Series(self.cat.categories)
            ntv_type = SeriesConnec.dtype_to_type[self.cat.categories.dtype.name]
            val_codec = json.loads(sr_codec.to_json(orient='records', date_format='iso',
                                                    default_handler=str))
            #ntv_value = NtvList([NtvList(val_codec, ntv_type=ntv_type),
            #             NtvList(list(self.cat.codes))], ntv_type='json') 
            ntv_value = [NtvList(val_codec, ntv_type=ntv_type),
                         NtvList(list(self.cat.codes))] 
        ntv_name = self.name
        return (None, 'field', NtvList(ntv_value, ntv_name, ntv_type).to_obj())
