# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `ntv_util` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

It contains the classes `NtvUtil`, `NtvConnector`, `NtvTree`, `NtvJsonEncoder`
and `NtvError` for NTV entities.
"""
from abc import ABC, abstractmethod
import datetime
import json
import re


class NtvUtil:
    ''' The NtvUtil class includes static methods used by several NTV classes.
    NtvUtil is the parent class of `Datatype`, `Namespace`, `Ntv`.

    *class variables :*
    - **_namespaces_** : list of Namespace defined
    - **_types_** : list of Datatype defined

    *static methods :*
    - `is_dictable`
    - `from_obj_name`
    - `decode_ntv_tab`
    - `to_ntv_pointer`

    '''
    _namespaces_ = {}
    _types_ = {}

    @staticmethod
    def is_dictable(lis):
        keys = set()
        for val in lis:
            if not isinstance(val, dict):
                return False
            if len(val) != 1:
                return False
            keys.add(list(val)[0])
        return len(keys) == len(lis)
    
    @staticmethod
    def from_obj_name(string):
        '''return a tuple with name, type_str and separator from string'''
        if not isinstance(string, str):
            raise NtvError('a json-name have to be str')
        if string == '':
            return (None, None, None)
        spl = string.rsplit(':', maxsplit=1)
        if len(spl) == 1:
            if string[-1] == '.':
                return (None, string, None)
            return(string, None, None)
        if spl[0] == '':
            return (None, spl[1], ':')
        if spl[0][-1] == ':':
            sp0 = spl[0][:-1]
            return (None if sp0 == '' else sp0, None if spl[1] == '' else spl[1], '::')
        return (None if spl[0] == '' else spl[0], None if spl[1] == '' else spl[1], ':')

    @staticmethod
    def decode_ntv_tab(ntv, ntv_to_val):
        '''Generate a tuple data from a Ntv tab value (bytes, string, json, Ntv object)

        *parameters:*

        - **ntv**: Ntv data to decode,
        - **ntv_to_val**: method to convert external value form ntv in internal Field value

        *Returns tuple: (name, dtype, codec, parent, keys, coef, leng)*

        - name (None or string): name of the Field
        - dtype (None or string): type of data
        - codec (list): list of Field codec values
        - parent (None or int): Field parent or None
        - keys (None or list): Field keys
        - coef (None or int): coef if primary Field else None
        - leng (int): length of the Field
        '''
        typ = ntv.type_str if ntv.ntv_type else None
        nam = ntv.name
        val = ntv_to_val(ntv)
        if ntv.__class__.__name__ == 'NtvSingle':
            return (nam, typ, [val], None, None, None, 1)
        if len(ntv) < 2 or len(ntv) > 3 or ntv[0].__class__.__name__ == 'NtvSingle':
            return (nam, typ, val, None, None, None, len(ntv))

        ntvc = ntv[0]
        leng = max(len(ind) for ind in ntv)
        typc = ntvc.type_str if ntvc.ntv_type else None
        valc = ntv_to_val(ntvc)
        if len(ntv) == 3 and ntv[1].__class__.__name__ == 'NtvSingle' and \
                isinstance(ntv[1].val, (int, str)) and \
                ntv[2].__class__.__name__ != 'NtvSingle' and \
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

    @staticmethod
    def to_ntvpointer(jsonpointer, unique_root=False):
        '''convert a json pointer inter a NTV pointer (string)

        *parameters:*

        - **jsonpointer**: String - json pointer to convert,
        - **unique_root**: Boolean (default False) - True if the json root length is 1 '''
        single = '/([0-9]+)(/[a-z])'
        if unique_root and not ('0' <= jsonpointer[1] <= '9'):
            return re.sub(single, '\g<2>', jsonpointer)[1:]
        return re.sub(single, '\g<2>', jsonpointer)


class NtvConnector(ABC):
    ''' The NtvConnector class is an abstract class used by all NTV connectors
    for conversion between NTV-JSON data and NTV-OBJ data.

    A NtvConnector child is defined by:
    - clas_obj: str - define the class name of the object to convert
    - clas_typ: str - define the Datatype of the converted object
    - to_obj_ntv: method - converter from JsonNTV to the object
    - to_json_ntv: method - converter from the object to JsonNTV

    *class method :*
    - `connector`
    - `dic_connec`
    - `castable` (@property)
    - `dic_obj` (@property)
    - `dic_type` (@property)

    *abstract method*
    - `to_obj_ntv`
    - `to_json_ntv`

    *static method*
    - `cast`
    - `uncast`
    - `is_json_class`
    - `is_json`
    - `init_ntv_keys`
    '''

    DIC_NTV_CL = {'NtvSingle': 'ntv', 'NtvList': 'ntv'}
    DIC_GEO_CL = {'Point': 'point', 'MultiPoint': 'multipoint', 'LineString': 'line',
                  'MultiLineString': 'multiline', 'Polygon': 'polygon',
                  'MultiPolygon': 'multipolygon'}
    DIC_DAT_CL = {'date': 'date', 'time': 'time', 'datetime': 'datetime'}
    DIC_FCT = {'date': datetime.date.fromisoformat, 'time': datetime.time.fromisoformat,
               'datetime': datetime.datetime.fromisoformat}
    DIC_GEO = {'point': 'point', 'multipoint': 'multipoint', 'line': 'linestring',
               'multiline': 'multilinestring', 'polygon': 'polygon',
               'multipolygon': 'multipolygon'}
    DIC_CBOR = {'point': False, 'multipoint': False, 'line': False,
                'multiline': False, 'polygon': False, 'multipolygon': False,
                'date': True, 'time': False, 'datetime': True}
    DIC_OBJ = {'tab': 'DataFrameConnec', 'field': 'SeriesConnec',
               'ndarray': 'NdarrayConnec',
               'point': 'ShapelyConnec', 'multipoint': 'ShapelyConnec',
               'line': 'ShapelyConnec', 'multiline': 'ShapelyConnec',
               'polygon': 'ShapelyConnec', 'multipolygon': 'ShapelyConnec',
               'other': None}

    @classmethod
    @property
    def castable(cls):
        '''return a list with class_name allowed for json-obj conversion'''
        return ['str', 'int', 'bool', 'float', 'dict', 'tuple', 'NoneType',
                'NtvSingle', 'NtvList'] \
            + list(NtvConnector.DIC_GEO_CL.keys()) \
            + list(NtvConnector.DIC_FCT.keys()) \
            + list(NtvConnector.dic_connec().keys())

    @classmethod
    @property
    def dic_obj(cls):
        '''return a dict with the connectors: { type: class_connec_name }'''
        return {clas.clas_typ: clas.__name__ for clas in cls.__subclasses__()} |\
            NtvConnector.DIC_OBJ

    @classmethod
    @property
    def dic_type(cls):
        '''return a dict with the connectors: { class_obj_name: type }'''
        return {clas.clas_obj: clas.clas_typ for clas in cls.__subclasses__()} |\
            NtvConnector.DIC_GEO_CL | NtvConnector.DIC_DAT_CL | NtvConnector.DIC_NTV_CL

    @classmethod
    def connector(cls):
        '''return a dict with the connectors: { class_connec_name: class_connec }'''
        return {clas.__name__: clas for clas in cls.__subclasses__()}

    @classmethod
    def dic_connec(cls):
        '''return a dict with the clas associated to the connector:
        { class_obj_name: class_connec_name }'''
        return {clas.clas_obj: clas.__name__ for clas in cls.__subclasses__()}

    @staticmethod
    @abstractmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' abstract - convert ntv_value into the return object'''

    @staticmethod
    @abstractmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' abstract - convert NTV object (value, name, type) into the NTV json
        (json-value, name, type)'''

    @staticmethod
    def cast(data, name=None, type_str=None):
        '''return JSON-NTV conversion (json_value, name, type_str) of the NTV entity
        defined in parameters.

        *Parameters*

        - **data**: NtvSingle entity or NTVvalue of the NTV entity
        - **name** : String (default None) - name of the NTV entity
        - **type_str**: String (default None) - type of the NTV entity
        '''
        clas = data.__class__.__name__
        if clas == 'NtvSingle':
            name = data.ntv_name
            type_str = data.type_str
            data = data.ntv_value
        dic_geo_cl = NtvConnector.DIC_GEO_CL
        dic_connec = NtvConnector.dic_connec()
        match clas:
            case 'int' | 'float' | 'bool' | 'str':
                return (data, name, type_str)
            case 'dict':
                return ({key: NtvConnector.cast(val, name, type_str)[0]
                         for key, val in data.items()}, name, type_str)
            case 'list':
                return ([NtvConnector.cast(val, name, type_str)[0] for val in data],
                        name, NtvConnector._typ_obj(data) if not type_str else type_str)
            case 'tuple':
                return (list(data), name, 'array' if not type_str else type_str)
            case 'date' | 'time' | 'datetime':
                return (data.isoformat(), name, clas if not type_str else type_str)
            case 'Point' | 'MultiPoint' | 'LineString' | 'MultiLineString' | \
                    'Polygon' | 'MultiPolygon':
                return (NtvConnector.connector()[dic_connec['geometry']].to_json_ntv(data)[0],
                        name, dic_geo_cl[data.__class__.__name__] if not type_str else type_str)
            case 'NtvSingle' | 'NtvList':
                return (data.to_obj(), name, 'ntv' if not type_str else type_str)
            case _:
                connec = None
                if clas in dic_connec and dic_connec[clas] in NtvConnector.connector():
                    connec = NtvConnector.connector()[dic_connec[clas]]
                if connec:
                    return connec.to_json_ntv(data, name, type_str)
                raise NtvError(
                    'connector is not defined for the class : ', clas)
        return (data, name, type_str)

    @staticmethod
    def uncast(value, name=None, type_str=None, **kwargs):
        '''return OBJ-NTV conversion (obj_value, name, type_str) of a NTV entity

        *Parameters*

        - **data**: NtvSingle entity or NTVvalue of the NTV entity
        - **name** : String (default None) - name of the NTV entity
        - **type_str**: String (default None) - type of the NTV entity
        '''
        if type_str == 'json':
            return (value, name, type_str)
        typebase_str = type_str
        if value.__class__.__name__ == 'NtvSingle':
            if not (type_str in set(NtvConnector.dic_type.values()) and
                    NtvConnector.is_json(value) or type_str is None):
                return (value.ntv_value, value.name, value.type_str)
            type_str = value.type_str if value.ntv_type else None
            typebase_str = value.typebase_str if value.ntv_type else None
            name = value.ntv_name
            value = value.ntv_value
        option = {'dicobj': {}, 'format': 'json', 'type_obj': False} | kwargs
        value_obj = NtvConnector._uncast_val(value, typebase_str, **option)
        return (value_obj, name, type_str if type_str else NtvConnector._typ_obj(value_obj))

    @staticmethod
    def _typ_obj(value):
        if isinstance(value, dict):
            return NtvConnector._typ_obj(list(value.values()))
        if isinstance(value, (tuple, list)):
            for val in value:
                typ = NtvConnector._typ_obj(val)
                if typ:
                    return typ
            return None
        return NtvConnector.dic_type.get(value.__class__.__name__)

    @staticmethod
    def _uncast_val(value, type_n, **option):
        '''return value from ntv value'''
        dic_fct = NtvConnector.DIC_FCT
        dic_geo = NtvConnector.DIC_GEO
        dic_obj = NtvConnector.dic_obj | option['dicobj']
        dic_cbor = NtvConnector.DIC_CBOR
        if not type_n or type_n == 'json' or (option['format'] == 'cbor' and
                                              not dic_cbor.get(type_n, False)):
            return value
        if type_n in dic_fct:
            if isinstance(value, (tuple, list)):
                return [NtvConnector._uncast_val(val, type_n, **option) for val in value]
            if isinstance(value, dict):
                return {key: NtvConnector._uncast_val(val, type_n, **option)
                        for key, val in value.items()}
            return dic_fct[type_n](value)
        if type_n == 'array':
            return tuple(value)
        if type_n == 'ntv':
            from json_ntv.ntv import Ntv
            return Ntv.from_obj(value)
        if type_n in dic_geo:
            option['type_geo'] = dic_geo[type_n]
        connec = None
        if type_n in dic_obj and \
                dic_obj[type_n] in NtvConnector.connector():
            connec = NtvConnector.connector()[dic_obj[type_n]]
        elif dic_obj['other'] in NtvConnector.connector():
            connec = NtvConnector.connector()['other']
        if connec:
            return connec.to_obj_ntv(value, **option)
        return value

    @staticmethod
    def is_json_class(val):
        ''' return True if val is a json type'''
        return val is None or isinstance(val, (list, int, str, float, bool, dict))

    @staticmethod
    def is_json(obj):
        ''' check if obj is a json structure and return True if obj is a json-value

        *Parameters*

        - **obj** : object to check
        - **ntvobj** : boolean (default False) - if True NTV class value are accepted'''
        if obj is None:
            return True
        is_js = NtvConnector.is_json
        match obj:
            case str() | int() | float() | bool() as obj:
                return True
            case list() | tuple() as obj:
                if not obj:
                    return True
                return min(is_js(obj_in) for obj_in in obj)
            case dict() as obj:
                if not obj:
                    return True
                if not min(isinstance(key, str) for key in obj.keys()):
                    raise NtvError('key in dict in not string')
                return min(is_js(obj_in) for obj_in in obj.values())
            case _:
                if not obj.__class__.__name__ in NtvConnector.castable:
                    raise NtvError(obj.__class__.__name__ +
                                   ' is not valid for NTV')
                return False

    @staticmethod
    def keysfromderkeys(parentkeys, derkeys):
        '''return keys from parent keys and derkeys

        *Parameters*

        - **parentkeys** : list of keys from parent
        - **derkeys** : list of derived keys

        *Returns* : list of keys'''
        return [derkeys[pkey] for pkey in parentkeys]

    @staticmethod
    def encode_coef(lis):
        '''Generate a repetition coefficient for periodic list'''
        if len(lis) < 2:
            return 0
        coef = 1
        while coef != len(lis):
            if lis[coef-1] != lis[coef]:
                break
            coef += 1
        if (not len(lis) % (coef * (max(lis) + 1)) and
                lis == NtvConnector.keysfromcoef(coef, max(lis) + 1, len(lis))):
            return coef
        return 0

    @staticmethod
    def keysfromcoef(coef, period, leng=None):
        ''' return a list of keys with periodic structure'''
        if not leng:
            leng = coef * period
        return None if not (coef and period) else [(ind % (coef * period)) // coef
                                                   for ind in range(leng)]

    @staticmethod
    def format_field(lidx_decode, leng):
        ''' return a list of format'''
        # name: 0, type: 1, codec: 2, parent: 3, keys: 4, coef: 5, leng: 6
        field_format = []
        for field_decode in lidx_decode:
            name, typ, codec, parent, keys, coef, length = field_decode
            if (keys, parent, coef) == (None, None, None):  # full or unique
                if len(codec) == 1:  # unique
                    field_format.append('unique')
                elif len(codec) == leng:    # full
                    field_format.append('full')
                else:
                    raise NtvError('impossible to generate keys')
                continue
            if keys and len(keys) > 1 and parent is None:  # complete
                field_format.append('complete')
                continue
            if coef:  # primary
                field_format.append('primary')
                continue
            if parent is None:
                raise NtvError('keys not referenced')
            if not keys:    # implicit
                field_format.append('implicit')
                continue
            field_format.append('relative')
        return field_format

    @staticmethod
    def init_ntv_keys(ind, lidx, leng):
        ''' initialization of explicit keys data in lidx object of tabular data'''
        # name: 0, type: 1, codec: 2, parent: 3, keys: 4, coef: 5, leng: 6
        name, typ, codec, parent, keys, coef, length = lidx[ind]
        if (keys, parent, coef) == (None, None, None):  # full or unique
            if len(codec) == 1:  # unique
                lidx[ind][4] = [0] * leng
            elif len(codec) == leng:    # full
                lidx[ind][4] = list(range(leng))
            else:
                raise NtvError('impossible to generate keys')
            return
        if keys and len(keys) > 1 and parent is None:  # complete
            return
        if coef:  # primary
            lidx[ind][4] = [(ikey % (coef * len(codec))) //
                            coef for ikey in range(leng)]
            lidx[ind][3] = None
            return
        if parent is None:
            raise NtvError('keys not referenced')
        if not lidx[parent][4] or len(lidx[parent][4]) != leng:
            NtvConnector.init_ntv_keys(parent, lidx, leng)
        if not keys and len(codec) == len(lidx[parent][2]):    # implicit
            lidx[ind][4] = lidx[parent][4]
            lidx[ind][3] = None
            return
        lidx[ind][4] = NtvConnector.keysfromderkeys(
            lidx[parent][4], keys)  # relative
        lidx[ind][3] = None
        return


class NtvTree:
    ''' The NtvTree class is an iterator class used to traverse a NTV tree structure.
    Some other methods give tree indicators and data.

    *Attributes :*

    - **ntv** : Ntv entity
    - **_node**:  Ntv entity - node pointer
    - **_stack**:  list - stack used to store context in recursive methods

    *dynamic values (@property)*
    - `breadth`
    - `size`
    - `height`
    - `adjacency_list`
    - `nodes`
    - `dic_nodes`
    - `leaf_nodes`
    - `inner_nodes`
    '''

    def __init__(self, ntv):
        ''' the parameter of the constructor is the Ntv entity'''
        self._ntv = ntv
        self._node = None
        self._stack = []

    def __iter__(self):
        ''' iterator without initialization'''
        return self

    def __next__(self):
        ''' return next node in the tree'''
        if self._node is None:
            self._node = self._ntv
        elif len(self._node) == 0:
            raise StopIteration
        elif self._node.__class__.__name__ == 'NtvList':
            self._next_down()
        else:
            self._next_up()
        return self._node

    def _next_down(self):
        ''' find the next subchild node'''

        self._node = self._node[0]
        self._stack.append(0)

    def _next_up(self):
        ''' find the next sibling or ancestor node'''
        parent = self._node.parent
        if not parent or self._node == self._ntv:
            raise StopIteration
        ind = self._stack[-1]
        if ind < len(parent) - 1:  # if ind is not the last
            self._node = parent[ind + 1]
            self._stack[-1] += 1
        else:
            if parent == self._ntv:
                raise StopIteration
            self._node = parent
            self._stack.pop()
            self._next_up()

    @property
    def breadth(self):
        ''' return the number of leaves'''
        return len(self.leaf_nodes)

    @property
    def size(self):
        ''' return the number of nodes'''
        return len(self.nodes)

    @property
    def height(self):
        ''' return the height of the tree'''
        return max(len(node.pointer()) for node in self.__class__(self._ntv)) - 1

    @property
    def adjacency_list(self):
        ''' return a dict with the list of child nodes for each parent node'''
        return {node: node.val for node in self.inner_nodes}

    @property
    def nodes(self):
        ''' return the list of nodes according to the DFS preordering algorithm'''
        return list(self.__class__(self._ntv))

    @property
    def dic_nodes(self):
        ''' return a dict of nodes according to the DFS preordering algorithm'''
        return {node.ntv_name: node for node in self.__class__(self._ntv)
                if node.ntv_name}

    @property
    def leaf_nodes(self):
        ''' return the list of leaf nodes according to the DFS preordering algorithm'''
        return [node for node in self.__class__(self._ntv)
                if node.__class__.__name__ == 'NtvSingle']

    @property
    def inner_nodes(self):
        ''' return the list of inner nodes according to the DFS preordering algorithm'''
        return [node for node in self.__class__(self._ntv)
                if node.__class__.__name__ == 'NtvList']


class NtvJsonEncoder(json.JSONEncoder):
    """json encoder for Ntv data"""

    def default(self, o):
        try:
            return NtvConnector.cast(o)[0]
        except NtvError:
            return json.JSONEncoder.default(self, o)
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class NtvError(Exception):
    ''' NTV Exception'''
