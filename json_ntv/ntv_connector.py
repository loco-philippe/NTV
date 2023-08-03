# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `NTV.ntv_connector` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

It contains :

- methods `from_csv` and `to_csv` to convert CSV files and 'tab' NTV entity
- the child classes of `NTV.json_ntv.ntv.NtvConnector` abstract class:
    - `SfieldConnec`:    'field' connector
    - `SdatasetConnec`:  'tab' connector
    - `NfieldConnec`:    'field' connector
    - `NdatasetConnec`:  'tab' connector
    - `DataFrameConnec`: 'tab' connector
    - `SeriesConnec`:    'field' connector
    - `MermaidConnec`:   '$mermaid' connector
    - `ShapelyConnec`:   'geometry' connector
    - `CborConnec`:      '$cbor' connector

"""
import datetime
import csv
import json
import pandas as pd
import numpy as np

from json_ntv.ntv import Ntv, NtvConnector, NtvList, NtvSingle, NtvTree
#from observation import Sfield


def from_csv(file_name, single_tab=True, dialect='excel', **fmtparams):
    ''' return a 'tab' NtvSingle from a csv file

    *parameters*

    - **file_name** : name of the csv file
    - **single_tab** : boolean (default True) - if True return a 'tab' NtvSingle,
    else return a NtvSet.
    - **dialect, fmtparams** : parameters of csv.DictReader object'''
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile, dialect=dialect, **fmtparams)
        names = reader.fieldnames
        list_ntv_value = [[] for nam in names]
        for row in reader:
            for ind_field, val in enumerate(list(row.values())):
                list_ntv_value[ind_field].append(json.loads(val))
    list_ntv = []
    for ind_field, field in enumerate(names):
        list_ntv.append(
            NtvList(list_ntv_value[ind_field], *Ntv.from_obj_name(field)[:2]))
    if single_tab:
        return NtvSingle(NtvList(list_ntv, None, None).to_obj(), None, 'tab')
    return NtvList(list_ntv, None, None)


def to_csv(file_name, ntv, *args, restval='', extrasaction='raise', dialect='excel', **kwds):
    ''' convert a 'tab' NtvSingle into csv file and return the file name

    *parameters*

    - **file_name** : name of the csv file
    - **ntv** : 'tab' NtvSingle to convert
    - **args, restval, extrasaction, dialect, kwds** : parameters of csv.DictWriter object'''
    if isinstance(ntv, NtvSingle):
        ntv_set = Ntv.obj(ntv.ntv_value)
    else:
        ntv_set = ntv
    list_ntv = [Ntv.obj(field) for field in ntv_set]
    fieldnames = [ntv_field.json_name(string=True) for ntv_field in list_ntv]
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=restval,
                                extrasaction=extrasaction, dialect=dialect, *args, **kwds)
        writer.writeheader()
        for i in range(len(list_ntv[0])):
            writer.writerow({name: field_ntv[i].to_obj(field_ntv.ntv_type, encoded=True)
                             for name, field_ntv in zip(fieldnames, list_ntv)})
    return file_name


class ShapelyConnec(NtvConnector):
    '''NTV connector for geographic location'''

    clas_obj = 'geometry'
    clas_typ = 'geometry'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into a shapely geometry object defined by 'type_geo'.

        *Parameters*

        - **type_geo** : type of geometry (point, multipoint, line, multiline',
        polygon, multipolygon)
        - **ntv_value** : array - coordinates'''
        from shapely import geometry
        return geometry.shape({"type": kwargs['type_geo'],
                               "coordinates": ntv_value})

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert NTV object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - NTV type of geometry (point, multipoint,
        line, multiline', polygon, multipolygon),
        - **name** : string (default None) - name of the NTV object
        - **value** : shapely geometry'''
        return (Ntv._listed(value.__geo_interface__['coordinates']), name, typ)


class CborConnec(NtvConnector):
    '''NTV connector for binary data'''

    clas_obj = 'bytes'
    clas_typ = '$cbor'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a binary CBOR object (no parameters).'''
        import cbor2
        return cbor2.dumps(ntv_value, datetime_as_timestamp=True,
                           timezone=datetime.timezone.utc, canonical=False,
                           date_as_datetime=True)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert NTV binary object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : binary data'''
        import cbor2
        return (cbor2.loads(value), name, typ)


class NfieldConnec(NtvConnector):
    '''NTV connector for NTV Field data'''

    clas_obj = 'Nfield'
    clas_typ = 'field'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a NTV Field object (no parameters).'''
        from observation.fields import Nfield
        ntv = Ntv.obj(ntv_value)
        return Nfield.from_ntv(ntv)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert NTV Field object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : NTV Field values (default format)'''
        return (value.to_ntv(name=True).to_obj(), name,
                NfieldConnec.clas_typ if not typ else typ)


class SfieldConnec(NtvConnector):
    '''NTV connector for simple Field data'''

    clas_obj = 'Sfield'
    clas_typ = 'field'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a simple Field object (no parameters).'''
        from observation.fields import Sfield
        ntv = Ntv.obj(ntv_value)
        return Sfield.from_ntv(ntv)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert simple Field object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : simple Field values (default format)'''
        return (value.to_ntv(name=True).to_obj(), name,
                NfieldConnec.clas_typ if not typ else typ)


class NdatasetConnec(NtvConnector):
    '''NTV connector for NTV Dataset data'''

    clas_obj = 'Ndataset'
    clas_typ = 'tab'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a NTV Dataset object (no parameters).'''
        from observation.datasets import Ndataset

        ntv = Ntv.obj(ntv_value)
        return Ndataset.from_ntv(ntv)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert NTV Dataset object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : NTV Dataset values'''
        return (value.to_ntv().to_obj(), name,
                NdatasetConnec.clas_typ if not typ else typ)


class SdatasetConnec(NtvConnector):
    '''NTV connector for simple Dataset data'''

    clas_obj = 'Sdataset'
    clas_typ = 'tab'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a simple Dataset object (no parameters).'''
        from observation.datasets import Sdataset

        ntv = Ntv.obj(ntv_value)
        return Sdataset.from_ntv(ntv)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert simple Dataset object (value, name, type) into NTV json
        (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : simple Dataset values'''
        return (value.to_ntv().to_obj(), name,
                SdatasetConnec.clas_typ if not typ else typ)


class DataFrameConnec(NtvConnector):
    '''NTV connector for pandas DataFrame'''

    clas_obj = 'DataFrame'
    clas_typ = 'tab'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):  # reindex=True, decode_str=False):
        ''' convert json ntv_value into a DataFrame.

        *Parameters*

        - **index** : list (default None) - list of index values,
        - **alias** : boolean (default False) - if True, alias dtype else default dtype
        - **annotated** : boolean (default False) - if True, NTV names are not included.'''
        #from observation import Sfield, Sdataset
        series = SeriesConnec.to_series

        ntv = Ntv.fast(ntv_value)
        lidx = [list(DataFrameConnec.decode_ntv_tab(ntvf, fast=True))
                for ntvf in ntv]
        #lidx = [list(NtvConnector.decode_ntv_tab(ntvf, fast=True)) for ntvf in ntv]
        leng = max([idx[6] for idx in lidx])
        option = kwargs | {'leng': leng}
        no_keys = []
        for ind in range(len(lidx)):
            no_keys.append(not lidx[ind][3]
                           and not lidx[ind][4] and not lidx[ind][5])
            NtvConnector.init_ntv_keys(ind, lidx, leng)
            lidx[ind][2] = Ntv.fast(Ntv.obj_ntv(lidx[ind][2], typ=lidx[ind][1],
                                                single=len(lidx[ind][2]) == 1))
        list_series = [series(lidx[ind][2], lidx[ind][0],
                              None if no_keys[ind] else lidx[ind][4], **option)
                       for ind in range(len(lidx))]
        dfr = pd.DataFrame({ser.name: ser for ser in list_series})
        if 'index' in dfr.columns:
            dfr = dfr.set_index('index')
            dfr.index.rename(None, inplace=True)
        return dfr

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert a DataFrame (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : DataFrame values'''
        df2 = value.reset_index()
        jsn = Ntv.obj([SeriesConnec.to_json_ntv(DataFrameConnec._unic(df2[col]))[0]
                       for col in df2.columns]).to_obj()
        return (jsn, name, DataFrameConnec.clas_typ if not typ else typ)

    @staticmethod
    def to_listidx(dtf):
        ''' convert a DataFrame in categorical data (list of dict for each column
        with keys : 'codec', 'name, 'keys' and length of the DataFrame)'''
        return ([SeriesConnec.to_idx(ser) for name, ser in dtf.items()], len(dtf))

    @staticmethod
    def _unic(srs):
        ''' return simple value if the Series contains a single value'''
        return srs[:1] if np.array_equal(srs.values, [srs.values[0]] * len(srs)) else srs

    @staticmethod
    def decode_ntv_tab(field, fast=False):
        '''Generate a tuple data from a Ntv tab value (bytes, string, json, Ntv object)

        *Parameters*

        - **field** : bytes, string json or Ntv object to convert
        - **format** : string (default 'json') - format to convert ntv_value
        - **fast**: boolean (default False) - if True, codec is created without
        conversion, else codec is created with json structure

        *Returns*

        - **tuple** : name, dtype, codec, parent, keys, coef, leng
            name (None or string): name of the Field
            dtype (None or string): type of data
            codec (list): list of Field codec values
            parent (None or int): Field parent or None
            keys (None or list): Field keys
            coef (None or int): coef if primary Field else None
            leng (int): length of the Field
        '''
        ntv = Ntv.obj(field)
        typ = ntv.type_str if ntv.ntv_type else None
        nam = ntv.name
        val = ntv.to_obj(simpleval=True)
        if isinstance(ntv, NtvSingle):
            return (nam, typ, [val], None, None, None, 1)
        if len(ntv) < 2 or len(ntv) > 3 or isinstance(ntv[0], NtvSingle):
            return (nam, typ, val, None, None, None, len(ntv))

        ntvc = ntv[0]
        leng = max(len(ind) for ind in ntv)
        typc = ntvc.type_str if ntvc.ntv_type else None
        valc = ntvc.to_obj(simpleval=True)
        if len(ntv) == 3 and isinstance(ntv[1], NtvSingle) and \
                isinstance(ntv[1].val, (int, str)) and not isinstance(ntv[2], NtvSingle) and \
                isinstance(ntv[2][0].val, int):
            return (nam, typc, valc, ntv[1].val, ntv[2].to_obj(), None, leng)
        if len(ntv) == 2 and len(ntv[1]) == 1 and isinstance(ntv[1].val, (int, str)):
            return (nam, typc, valc, ntv[1].val, None, None, leng)
        if len(ntv) == 2 and len(ntv[1]) == 1 and isinstance(ntv[1].val, list):
            leng = leng * ntv[1][0].val
            return (nam, typc, valc, None, None, ntv[1][0].val, leng)
        if len(ntv) == 2 and len(ntv[1]) > 1 and isinstance(ntv[1][0].val, int):
            return (nam, typc, valc, None, ntv[1].to_obj(), None, leng)
        return (nam, typ, val, None, None, None, len(ntv))


class SeriesConnec(NtvConnector):
    '''NTV connector for pandas Series'''

    clas_obj = 'Series'
    clas_typ = 'field'

    types = pd.DataFrame(
        {'ntv_type':  ['durationiso', 'uint64', 'float32', 'string', 'datetime',
                       'int32', 'int64', 'float64', 'array', 'boolean'],
         'name_type': [None, None, None, None, None,
                       None, 'int64', 'float64', 'array', 'boolean'],
         'dtype': ['timedelta64[ns]', 'UInt64', 'Float32', 'string', 'datetime64[ns]',
                   'Int32', 'Int64', 'Float64', 'object', 'boolean']})
    astype = {'uint64': 'UInt64', 'float32': 'Float32', 'int32': 'Int32',
              'int64': 'Int64', 'float64': 'Float64', 'bool': 'boolean'}
    deftype = {val: key for key, val in astype.items()}

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        '''Generate a Series Object from a Ntv field object

        *Parameters*

        - **ntv_value**: Ntv object or Ntv value - value to convert in Series

        *parameters (kwargs)*

        - **extkeys**: list (default None) - keys to use if not present in ntv_value
        - **decode_str**: boolean (default False) - if True, string values are converted
        in object values
        - **index**: list (default None) - if present, add the index in Series
        - **leng**: integer (default None) - leng of the Series (used with single codec value)
        - **alias**: boolean (default False) - if True, convert dtype in alias dtype
        - **annotated**: boolean - if True, ntv_codec names are ignored
        '''
        from observation import Sfield

        option = {'extkeys': None, 'decode_str': False, 'leng': None} | kwargs
        if ntv_value is None:
            return None
        ntv = Ntv.obj(ntv_value, decode_str=option['decode_str'])

        ntv_name, typ, codec, parent, ntv_keys, coef, leng_field = Sfield.decode_ntv(
            ntv, fast=True)
        #ntv_name, typ, codec, parent, ntv_keys, coef, leng_field = DataFrameConnec.decode_ntv_tab(ntv, fast=True)
        if parent and not option['extkeys']:
            return None
        if coef:
            #ntv_keys = Sfield.keysfromcoef(coef, leng_field//coef, option['leng'])
            ntv_keys = NtvConnector.keysfromcoef(
                coef, leng_field//coef, option['leng'])
        elif option['extkeys'] and parent:
            #ntv_keys = Sfield.keysfromderkeys(option['extkeys'], ntv_keys)
            ntv_keys = NtvConnector.keysfromderkeys(
                option['extkeys'], ntv_keys)
        elif option['extkeys'] and not parent:
            ntv_keys = option['extkeys']
        ntv_codec = Ntv.fast(Ntv.obj_ntv(
            codec, typ=typ, single=len(codec) == 1))
        return SeriesConnec.to_series(ntv_codec, ntv_name, ntv_keys, **kwargs)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert a Series (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : Series values'''
        from observation import Sfield

        astype = SeriesConnec.astype
        ntv_type_val = SeriesConnec._ntv_type_val
        srs = value.astype(astype.get(value.dtype.name, value.dtype.name))
        sr_name = srs.name if srs.name else ''
        ntv_name, name_type = Ntv.from_obj_name(sr_name)[:2]

        if srs.dtype.name == 'category':
            cdc = pd.Series(srs.cat.categories)
            ntv_type, cat_value = ntv_type_val(name_type, cdc)
            cat_value = NtvList(cat_value, ntv_type=ntv_type).to_obj()
            cod_value = list(srs.cat.codes)
            coef = Sfield.encode_coef(cod_value)
            ntv_value = [cat_value, [coef] if coef else cod_value]
            ntv_type = 'json'
        else:
            ntv_type, ntv_value = ntv_type_val(name_type, srs)
        if len(ntv_value) == 1:
            return (NtvSingle(ntv_value[0], ntv_name, ntv_type).to_obj(), name,
                    SeriesConnec.clas_typ if not typ else typ)
        return (NtvList(ntv_value, ntv_name, ntv_type).to_obj(), name,
                SeriesConnec.clas_typ if not typ else typ)

    @staticmethod
    def to_idx(ser):
        ''' convert a Series in categorical data

        *return (dict)*

        - 'codec': list of pandas categories
        - 'name': name of the series
        - 'keys': list of pandas codes
        '''
        idx = ser.astype('category')
        lis = list(idx.cat.categories)
        if lis and isinstance(lis[0], pd._libs.tslibs.timestamps.Timestamp):
            lis = [ts.to_pydatetime().astimezone(datetime.timezone.utc)
                   for ts in lis]
        return {'codec': lis, 'name': ser .name, 'keys': list(idx.cat.codes)}

    @staticmethod
    def to_series(ntv_codec, ntv_name, ntv_keys, **kwargs):
        ''' return a pd.Series from Field data (codec, name, keys)

        *Parameters*

        - **ntv_codec**: Ntv object - codec value to convert in Series values
        - **ntv_type**: string - default type to apply to convert in dtype
        - **ntv_name**: string - name of the Series

        *parameters (kwargs)*

        - **index**: list (default None) - if present, add the index in Series
        - **leng**: integer (default None) - leng of the Series (used with single codec value)
        - **alias**: boolean (default False) - if True, convert dtype in alias dtype
        - **annotated**: boolean - if True, ntv_codec names are ignored
        '''
        option = {'index': None, 'leng': None, 'alias': False,
                  'annotated': False} | kwargs
        types = SeriesConnec.types
        astype = SeriesConnec.astype

        str_type = ntv_codec.type_str
        ntv_type = str_type if str_type and str_type != 'json' else ''
        len_unique = option['leng'] if len(
            ntv_codec) == 1 and option['leng'] else 1
        pd_convert = ntv_type in types['ntv_type'].values or ntv_type == ''

        dtype = 'object'
        if pd_convert:
            dtype = types.set_index(
                'ntv_type').loc[ntv_type]['dtype'] if ntv_type != '' else None
        ntv_obj, pd_name, name_type = SeriesConnec._val_nam_typ(
            ntv_codec, ntv_type, ntv_name, pd_convert, option['annotated'])

        if ntv_keys:
            if pd_convert and name_type != 'array':
                categ = pd.read_json(json.dumps(ntv_obj),
                                     dtype=dtype, typ='series')
                cat_type = categ.dtype.name
                categories = categ.astype(astype.get(cat_type, cat_type))
            else:
                categories = pd.Series(ntv_obj, dtype='object')
            cat = pd.CategoricalDtype(categories=categories)
            data = pd.Categorical.from_codes(codes=ntv_keys, dtype=cat)
            srs = pd.Series(data, name=pd_name,
                            index=option['index'], dtype='category')
        else:
            data = ntv_obj * len_unique

            if pd_convert:
                srs = pd.read_json(json.dumps(data), dtype=dtype,
                                   typ='series').rename(pd_name)
            else:
                srs = pd.Series(data, name=pd_name, dtype=dtype)
        if option['alias']:
            return srs.astype(astype.get(srs.dtype.name, srs.dtype.name))
        return srs.astype(SeriesConnec.deftype.get(srs.dtype.name, srs.dtype.name))

    @staticmethod
    def _val_nam_typ(ntv_codec, ntv_type, ntv_name, pd_convert, annotated):
        ''' return Series data from ntv data

        *parameters*

        - **ntv_codec**: Ntv object - codec value to convert in Series values
        - **ntv_type**: string - default type to apply to convert in dtype
        - **ntv_name**: string - name of the Series
        - **pd_convert**: boolean - if True, use pandas json conversion
        - **annotated**: boolean - if True, ntv_codec names are ignored

        *return (tuple)*

        - ntv_obj : list with ntv_codec json values converted to object values
        - pd_name : string with the Serie name
        - name_type : string - pandas types to be converted in 'json' Ntv-type
        '''
        types = SeriesConnec.types
        if pd_convert:
            name_type = types.set_index(
                'ntv_type').loc[ntv_type]['name_type'] if ntv_type != '' else ''
            pd_name = ntv_name + '::' + name_type if name_type else ntv_name
            pd_name = pd_name if pd_name else None
            if name_type == 'array':
                ntv_obj = ntv_codec.to_obj(format='obj', simpleval=True)
            else:
                ntv_obj = ntv_codec.obj_value(simpleval=annotated,
                                              json_array=False, def_type=ntv_codec.type_str)
                ntv_obj = ntv_obj if isinstance(ntv_obj, list) else [ntv_obj]
        else:
            name_type = ntv_type
            pd_name = ntv_name+'::'+name_type
            ntv_obj = ntv_codec.to_obj(
                format='obj', simpleval=True, def_type=ntv_type)
            # ntv_obj = ntv_codec.to_obj_ntv(simpleval=True, def_type=ntv_type)  #!!!
        return (ntv_obj, pd_name, name_type)

    @staticmethod
    def _ntv_type_val(name_type, srs):
        ''' convert a simple Series into NTV data (NTV type, NTV json-value). If name_type is None and
        dtype is 'object', the NTV value is the srs values.

        *Parameters*

        - **name_type** : string - default NTV type to be used. If None, dtype is converted in NTV type,
        - **srs** : Series to be converted.'''
        types = SeriesConnec.types
        dtype = srs.dtype.name
        if not name_type:
            types_none = types.set_index('name_type').loc[None]
            if dtype in types_none.dtype.values:
                ntv_type = types_none.set_index('dtype').loc[dtype].ntv_type
            else:
                ntv_type = 'json'
            ntv_value = json.loads(srs.to_json(
                orient='records', date_format='iso', default_handler=str))
        else:
            ntv_type = name_type
            if dtype == 'object':
                ntv_value = srs.to_list()
            else:
                ntv_value = json.loads(srs.to_json(
                    orient='records', date_format='iso', default_handler=str))
        return (ntv_type, ntv_value)


class MermaidConnec(NtvConnector):
    '''NTV connector for Mermaid diagram'''

    clas_obj = 'Mermaid'
    clas_typ = '$mermaid'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into a mermaid flowchart

        *Parameters*

        - **title**: String (default '') - title of the flowchart
        - **disp**: Boolean (default False) - if true, return a display else return
        a mermaid text diagram
        - **row**: Boolean (default False) - if True, add the node row
        - **leaves**: Boolean (default False) - if True, add the leaf row
        '''
        from base64 import b64encode
        from IPython.display import Image, display

        option = {'title': '', 'disp': False, 'row': False,
                  'leaves': False} | kwargs
        diagram = MermaidConnec.diagram
        link = MermaidConnec._mermaid_link
        ntv = Ntv.obj(ntv_value)
        node_link = {'nodes': [], 'links': []}
        dic_node = {}
        if option['leaves']:
            nodes = [node for node in NtvTree(
                ntv) if not isinstance(node.val, list)]
            dic_node = {node: row for row, node in enumerate(nodes)}
        link(ntv, None, node_link, option['row'], dic_node)
        mermaid_json = {option['title'] + ':$flowchart': {
            'orientation': 'top-down',
            'node::': {node[0]: node[1] for node in node_link['nodes']},
            'link::': node_link['links']}}
        if option['disp']:
            return display(Image(url="https://mermaid.ink/img/" +
                                 b64encode(diagram(mermaid_json).encode("ascii")).decode("ascii")))
        return diagram(mermaid_json)

    @staticmethod
    def diagram(json_diag):
        '''create a mermaid code from a mermaid json'''
        ntv = Ntv.obj(json_diag)
        erdiagram = MermaidConnec._er_diagram
        flowchart = MermaidConnec._flowchart
        diag_type = ntv.type_str[1:]
        diag_txt = '---\ntitle: ' + ntv.name + '\n---\n' if ntv.name else ''
        diag_txt += diag_type
        match diag_type:
            case 'erDiagram':
                diag_txt += erdiagram(ntv)
            case 'flowchart':
                diag_txt += flowchart(ntv)
        return diag_txt

    @staticmethod
    def _mermaid_node(ntv, def_typ_str, num, dic_node):
        '''create and return a node'''
        j_name, j_sep, j_type = ntv.json_name(def_typ_str)
        name = ''
        if j_name:
            name += '<b>' + j_name + '</b>\n'
        if j_type:
            name += j_type + '\n'
        if ntv in dic_node:
            num += ' ' + str(dic_node[ntv])
        if num:
            name += '<i>' + num + '</i>\n'
        elif isinstance(ntv, NtvSingle):
            if isinstance(ntv.val, str):
                name += '<i>' + ntv.val + '</i>\n'
            else:
                name += '<i>' + json.dumps(ntv.val) + '</i>\n'
            return [ntv.address_name, ['rectangle', name[:-1]]]
        if not name:
            name = '<b>::</b>\n'
        name = name.replace('"', "'")
        return [ntv.address_name, ['roundedge', name[:-1]]]

    @staticmethod
    def _mermaid_link(ntv, def_typ_str, node_link, row, dic_node):
        '''add nodes and links from ntv in node_list and link_list '''
        num = str(len(node_link['nodes'])) if row else ''
        node_link['nodes'].append(MermaidConnec._mermaid_node(
            ntv, def_typ_str, num, dic_node))
        if isinstance(ntv, NtvList):
            for ntv_val in ntv:
                MermaidConnec._mermaid_link(ntv_val, ntv.type_str,
                                            node_link, row, dic_node)
                node_link['links'].append(
                    [ntv.address_name, 'normalarrow', ntv_val.address_name])

    @staticmethod
    def _flowchart(ntv):
        orientation = {'top-down': 'TD', 'top-bottom': 'TB',
                       'bottom-top': 'BT', 'right-left': 'RL', 'left-right': 'LR'}
        fcnode = MermaidConnec._fc_node
        fclink = MermaidConnec._fc_link
        flc = Ntv.obj(ntv.val)
        diag_txt = ' ' + orientation[flc['orientation'].val]
        for node in flc['node']:
            diag_txt += fcnode(node)
        for link in flc['link']:
            diag_txt += fclink(link)
        return diag_txt + '\n'

    @staticmethod
    def _fc_link(link):
        link_t = {'normal': ' ---', 'normalarrow': ' -->',
                  'dotted': ' -.-', 'dottedarrow': ' -.->'}
        link_txt = '\n    ' + str(link[0].val) + link_t[link[1].val]
        if len(link) == 4:
            link_txt += '|' + link[3].val + '|'
        return link_txt + ' ' + str(link[2].val)

    @staticmethod
    def _fc_node(node):
        shape_l = {'rectangle': '[', 'roundedge': '(', 'stadium': '(['}
        shape_r = {'rectangle': ']', 'roundedge': ')', 'stadium': '])'}
        return '\n    ' + node.name + shape_l[node[0].val] + '"' + \
               node[1].val.replace('"', "'") + '"' + shape_r[node[0].val]

    @staticmethod
    def _er_diagram(ntv):
        erentity = MermaidConnec._er_entity
        errelation = MermaidConnec._er_relation
        diag_txt = ''
        erd = Ntv.obj(ntv.val)
        for entity in erd['entity']:
            diag_txt += erentity(entity)
        for relation in erd['relationship']:
            diag_txt += errelation(relation)
        return diag_txt

    @staticmethod
    def _er_entity(entity):
        ent_txt = '\n    ' + entity.name + ' {'
        for att in entity:
            ent_txt += '\n        ' + att[0].val + ' ' + att[1].val
            if len(att) > 2:
                if att[2].val in ('PK', 'FK', 'UK'):
                    ent_txt += ' ' + att[2].val
                else:
                    ent_txt += ' "' + att[2].val + '"'
            if len(att) > 3:
                ent_txt += ' "' + att[3].val + '"'
        return ent_txt + '\n    }'

    @staticmethod
    def _er_relation(rel):
        rel_left = {'exactly one': ' ||', 'zero or one': ' |o',
                    'zero or more': ' }o', 'one or more': ' }|'}
        rel_right = {'exactly one': '|| ', 'zero or one': 'o| ',
                     'zero or more': 'o{ ', 'one or more': '|{ '}
        identif = {'identifying': '--', 'non-identifying': '..'}
        rel_txt = '\n    ' + rel[0].val + rel_left[rel[1].val] + \
            identif[rel[2].val] + rel_right[rel[3].val] + rel[4].val
        if len(rel) > 5:
            rel_txt += ' : ' + rel[5].val
        return rel_txt
