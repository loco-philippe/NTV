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
    fieldnames = [ntv_field.json_name(string=True) for ntv_field in list_ntv]
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=restval, extrasaction=extrasaction, 
                                dialect=dialect, *args, **kwds)
        writer.writeheader()
        for i in range(len(list_ntv[0])):
            writer.writerow({name: field_ntv[i].to_obj(field_ntv.ntv_type, encoded=True)
                             for name, field_ntv in zip(fieldnames, list_ntv)})
    return file_name

class NfieldConnec(NtvConnector):
    '''NTV connector for Iindex'''
    
    clas_obj = 'Nfield'

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        from observation.fields import Nfield
        ntv = Ntv.obj(ntv_value)
        return Nfield.from_ntv(ntv)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, json-value)'''
        return (None, 'field', self.to_ntv(name=True).to_obj())
    
class SfieldConnec(NtvConnector):
    '''NTV connector for Iindex'''
    
    clas_obj = 'Sfield'

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        from observation.fields import Sfield
        ntv = Ntv.obj(ntv_value)
        return Sfield.from_ntv(ntv)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, json-value)'''
        return (None, 'field', self.to_ntv(name=True).to_obj())
    
class NdatasetConnec(NtvConnector):
    '''NTV connector for Ndataset'''
    
    clas_obj = 'Ndataset'

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        from observation.datasets import Ndataset
        ntv = Ntv.obj(ntv_value)
        return Ndataset.from_ntv(ntv)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, json-value)'''
        return (None, 'tab', self.to_ntv().to_obj())

class SdatasetConnec(NtvConnector):
    '''NTV connector for Sdataset'''
    
    clas_obj = 'Sdataset'

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        from observation.datasets import Sdataset
        ntv = Ntv.obj(ntv_value)
        return Sdataset.from_ntv(ntv)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, json-value)'''
        return (None, 'tab', self.to_ntv().to_obj())

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
        option = kwargs | {'leng': leng}
        list_series = [SeriesConnec.from_ntv(d, **option) for d in ntv]
        df = pd.DataFrame({ser.name: ser for ser in list_series})
        if 'index' in df.columns:
            df = df.set_index('index')
            df.index.rename(None, inplace=True)
        return df

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, value)'''
        # from observation import Ilist
        df2 = self.reset_index()
        """js = NtvList([[SeriesConnec.to_ntv(df2[col])[2] 
                     if len(df2[col].astype('category').cat.categories) > 1
                     else SeriesConnec.to_ntv(df2[col][0])[2] 
                     for col in df2.columns]]).to_obj() # methode si unique et hash"""
        js = NtvList([SeriesConnec.to_ntv(df2[col])[2] for col in df2.columns]).to_obj()
        # methode si non unique
        return (None, 'tab', js) 
        #return (None, 'tab', Ilist.ntv(js).to_ntv(modecodec='full').to_obj()) 
        # methode si non categorical


class SeriesConnec(NtvConnector):
    '''NTV connector for pandas Series'''
    
    clas_obj = 'Series'
    types = pd.DataFrame({'ntv_type':  ['durationiso', 'uint64', 'float32', 'string', 'datetime', 'int32', 'int64', 
                                        'float64', 'array', 'boolean'], 
                          'name_type': [None, None, None, None, None, None, 'int64', 
                                        'float64', 'array', 'boolean'], 
                          'dtype':     ['timedelta64[ns]', 'UInt64', 'Float32', 'string', 'datetime64[ns]', 'Int32', 'Int64', 
                                        'Float64', 'object', 'boolean']})
    astype = {'uint64': 'UInt64', 'float32': 'Float32', 'int32': 'Int32', 'int64': 'Int64', 'float64': 'Float64', 
              'bool': 'boolean'}
    deftype = { val: key for key, val in astype.items()}
    
    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        option = {'index':None, 'leng':None, 'alias':False, 
                  'annotated':False} | kwargs 
        types = SeriesConnec.types
        astype = SeriesConnec.astype
        deftype = SeriesConnec.deftype
        ntv = Ntv.obj(ntv_value)
        ntv_name = ntv.name
        codes = len(ntv) == 2 and len(ntv[1]) > 1 # categorical
        if codes:
            cod = ntv[1].to_obj(simpleval=True)
            ntv = ntv[0]
        ntv_type = ntv.type_str if ntv.type_str != 'json' else ''
        pd_convert = ntv_type in types['ntv_type'].values or ntv_type == '' # pandas conversion
    
        if pd_convert:
            dtype = types.set_index('ntv_type').loc[ntv_type]['dtype'] if ntv_type != '' else None
            name_type = types.set_index('ntv_type').loc[ntv_type]['name_type'] if ntv_type != '' else ''
            pd_name = ntv_name + '::' + name_type if name_type else ntv_name
            pd_name = pd_name if pd_name else None
            if name_type == 'array':
                ntv_obj = ntv.to_obj(format='obj', simpleval=True)
            else:
                #list_val = ntv.obj_value()
                #list_val = ntv.obj_value(simpleval=True)
                list_val = ntv.obj_value(simpleval=option['annotated']) 
                ntv_list = NtvList(list_val) if isinstance(list_val, (list, dict)) else  NtvList([list_val])
                ntv_obj = ntv_list.to_obj() # add simpleval=True ?
                #ntv_obj = ntv_list.to_obj(simpleval=True)
        else:    
            dtype = 'object'
            name_type = ntv_type
            pd_name = ntv_name+'::'+name_type
            ntv_obj = ntv.to_obj(format='obj', simpleval=True, def_type=ntv_type)
            #ntv_obj = ntv.to_obj(format='obj', simpleval=option['annotated'],
            #                     def_type=ntv_type)
    
        if codes:
            if pd_convert and name_type != 'array':
                dtype = types.set_index('ntv_type').loc[ntv_type]['dtype'] if ntv_type != '' else None
                categories = pd.read_json(json.dumps(ntv_obj), dtype=dtype, typ='series')
                cat_type = categories.dtype.name
                categories = categories.astype(astype.get(cat_type, cat_type))
            else:
                categories = pd.Series(ntv_obj, dtype='object')
            cat = pd.CategoricalDtype(categories=categories)
            data = pd.Categorical.from_codes(codes=cod, dtype=cat)
            sr = pd.Series(data, name=pd_name, index=option['index'] , dtype='category')
        else:   
            data = ntv_obj * option['leng'] if len(ntv) == 1 and option['leng'] else ntv_obj
            if pd_convert:
                sr = pd.read_json(json.dumps(data), dtype=dtype, typ='series').rename(pd_name)
            else:
                sr = pd.Series(data, name=pd_name, dtype=dtype) 
        
        if option['alias']:
            return sr.astype(astype.get(sr.dtype.name, sr.dtype.name))
        return sr.astype(deftype.get(sr.dtype.name, sr.dtype.name))
    
    def ntv_type_val(name_type, sr):
        types = SeriesConnec.types
        dtype = sr.dtype.name
        if not name_type:
            types_none = types.set_index('name_type').loc[None]
            if dtype in types_none.dtype.values:
                ntv_type = types_none.set_index('dtype').loc[dtype].ntv_type
            else:
                ntv_type = 'json'
            ntv_value = json.loads(sr.to_json(orient='records', date_format='iso', default_handler=str))
        else:
            ntv_type = name_type
            if dtype == 'object':
                ntv_value = sr.to_list()   
            else:
                ntv_value = json.loads(sr.to_json(orient='records', date_format='iso', default_handler=str))
        return (ntv_type, ntv_value)
    
    def to_ntv(sr):
        ''' convert object into the NTV entity'''
        astype = SeriesConnec.astype
        ntv_type_val = SeriesConnec.ntv_type_val
        sr = sr.astype(astype.get(sr.dtype.name, sr.dtype.name))
        sr_name = sr.name if sr.name else ''
        ntv_name, name_type = Ntv.from_obj_name(sr_name)[:2]
        if sr.dtype.name == 'category':
            cdc = pd.Series(sr.cat.categories)  
            ntv_type, cat_value = ntv_type_val(name_type, cdc)
            cat_value = NtvList(cat_value, ntv_type=ntv_type).to_obj()
            ntv_value = [cat_value, NtvList(list(sr.cat.codes))]
            ntv_type = 'json'
        else:
            ntv_type, ntv_value = ntv_type_val(name_type, sr)
        return (None, 'field', NtvList(ntv_value, ntv_name, ntv_type).to_obj())
    
""" type_to_dtype = {'datetime': 'datetime64[ns]',
                     'string': 'string', 'int32': 'int32', 'int64': 'int64',
                     'float': 'float', 'float32': 'float32', 'boolean': 'bool',
                     'json': None}
    dtype_to_type = {'datetime64[ns]': 'datetime', 'string': 'string', 
                     'int32': 'int32', 'int64': 'json', 'float': 'json', 
                     'float32': 'float32', 'bool': 'json'}

    @staticmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''
        option = {'index':None, 'leng':None} | kwargs 
        dtype = 'object'
        ntv = Ntv.obj(ntv_value)
        name = ntv.ntv_name
        codes = len(ntv) == 2 and len(ntv[1]) > 1
        if codes:
            cod = ntv[1].to_obj(simpleval=True)
            ntv = ntv[0]
        ntv_obj = ntv.to_obj(format='obj', simpleval=True)
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
            dtype = 'category'
        name = name + '::' + ntv.type_str \
            if dtype == 'object' or (codes and ntv.type_str != 'json') else name
        name = name if name else None
        return pd.Series(data, name=name, index=option['index'] , dtype=dtype)

    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, value)'''
        to_type = SeriesConnec.dtype_to_type
        dtype = self.dtype.name
        ntv_type = None
        ntv_name = self.name if self.name else ''
        if dtype in to_type and to_type[dtype] != 'json':
            ntv_type = to_type[dtype]
        if dtype in to_type:
            js = self.to_json(orient='records', date_format='iso', default_handler=str)
            ntv_value = json.loads(js)
        elif dtype == 'object':
            ntv_name, ntv_type, sep = Ntv.from_obj_name(ntv_name)
            ntv_value = self.to_list()
        elif dtype == 'category':
            ntv_name, ntv_type, sep = Ntv.from_obj_name(ntv_name)
            cdc = pd.Series(self.cat.categories)
            if cdc.dtype.name == 'object':
                ntv_value = [Ntv.obj(Ntv.obj(cdc).val),
                             NtvList(list(self.cat.codes))] 
            else:
                js = cdc.to_json(orient='records', date_format='iso', default_handler=str)
                ntv_value = [NtvList(json.loads(js), ntv_type=ntv_type),
                             NtvList(list(self.cat.codes))] 
            ntv_type = 'json'
        return (None, 'field', NtvList(ntv_value, ntv_name, ntv_type).to_obj())
"""