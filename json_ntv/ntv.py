# -*- coding: utf-8 -*-
"""
Created on Feb 27 22:44:05 2023

@author: Philippe@loco-labs.io

The `ntv` module contains the NtvSingle, NtvSet and NtvList classes for NTV entity.

# 1 - JSON-NTV structure

The NTV triplet (name, type, value) is represented using a JSON-NTV format inspired
by the RFC [JSON-ND](https://github.com/glenkleidon/JSON-ND) project :
- **```value```** (if name and type are not documented)
- **```{ "name" : value }```** (if name is documented but not type)
- **```{ ":type" : value }```** for primitive entities and **```{ "::type" : value }```**
 for structured entities (if type is documented but not name)
- **```{ "name:type" : value }```** for primitive entities and **```{
 "name::type" : value }```** for structured entities (if type and name are documented).

For an NTV-single, the value is the JSON-value of the entity.
For an NTV-list, value is a JSON-array where JSON-elements are the JSON-NTV formats
 of included NTV entities.
For an NTV-set, value is a JSON-object where JSON-members are the JSON-members of
the JSON-NTV formats of included NTV entities.

This JSON-NTV format allows full compatibility with existing JSON structures:
- a JSON-number, JSON-string or JSON-boolean is the representation of an NTV-single entity,
- a JSON-object with a single member is the representation of an NTV-single entity
- a JSON-array is the representation of an NTV-list entity
- a JSON-object without a single member is the representation of an NTV-set entity

# 2 - Examples of JSON-NTV representations
- NTV-single, simple format :
   - ```"lyon"```
   - ```52.5```
   - ```{ }```
- NTV-single, named format :
   - ```{ "paris:point" : [2.3522, 48.8566] }```
   - ```{ ":point" : [4.8357, 45.7640] }```
   - ```{ "city" : "paris" }```
- NTV-list, simple format :
   - ```[ [2.3522, 48.8566], {"lyon" : [4.8357, 45.7640]} ]```
   - ```[ { ":point" : [2.3522, 48.8566]}, {":point" : [4.8357, 45.7640]} ]```
   - ```[ 4, 45 ]```
   - ```[ "paris" ]```
   - ```[ ]```
- NTV-list, named format :
   - ```{ "cities::point" : [ [2.3522, 48.8566], [4.8357, 45.7640] ] }```
   - ```{ "::point" : [ [2.3522, 48.8566], {"lyon" : [4.8357, 45.7640]} ] }```
   - ```{ "simple list" : [ 4, 45.7 ] }```
   - ```{ "generic date::dat" : [ "2022-01-28T18-23-54Z", "2022-01-28", 1234.78 ] }```
- NTV-set, simple format :
   - ```{ "nom”: "white", "prenom": "walter", "surnom": "heisenberg" }```
   - ```{ "paris:point" : [2.3522, 48.8566] , "lyon" : "france" }```
   - ```{ "paris" : [2.3522, 48.8566], "" : [4.8357, 45.7640] }```
- NTV-set, named format :
   - ```{ "cities::point": { "paris": [2.352, 48.856], "lyon": [4.835, 45.764]}}```
   - ```{ "cities" : { "paris:point" : [2.3522, 48.8566] , "lyon" : "france"} }```
   - ```{ "city" : { "paris" : [2.3522, 48.8566] } }```

"""
from copy import copy
from datetime import date, time, datetime
import json
from json import JSONDecodeError

from shapely import geometry
from util import util
from namespace import NtvType, Namespace, NtvTypeError


class Ntv():
    ''' NTV entity

    *Attributes :

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**:  value of the entity

    The methods defined in this class are :

    *classmethods*
    - `from_obj`

    *dynamic values (@property)
    - `type_str`
    - `code_ntv`

    *instance methods*
    - `to_obj`
    '''

    def __init__(self, ntv_value, ntv_name=None, ntv_type=None):
        '''Ntv constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String or NtvType or Namespace (default None) - type of the entity
        - **ntv_value**: Json entity - value of the entity
        '''
        if isinstance(ntv_type, (NtvType, Namespace)):
            self.ntv_type = ntv_type
        elif ntv_type and ntv_type[-1] != '.':
            self.ntv_type = NtvType.add(ntv_type)
        elif ntv_type and ntv_type[-1] == '.':
            self.ntv_type = Namespace.add(ntv_type)
        else:
            self.ntv_type = None
        self.ntv_name = ntv_name
        self.ntv_value = ntv_value

    @staticmethod
    def from_obj(value, def_type=None, def_sep=None):
        ''' return an Ntv object from an object value '''
        if value.__class__.__name__ in ['NtvSingle', 'NtvList', 'NtvSet']:
            return value
        if value is None or value == 'null':
            return NtvSingle(None)
        if value == 'true':
            return NtvSingle(True)
        if value == 'false':
            return NtvSingle(False)
        if isinstance(value, str) and value.lstrip() and value.lstrip()[0] in '"-{[0123456789':
            try:
                value = json.loads(value)
            except JSONDecodeError:
                pass
        return Ntv._from_obj(value, def_type, def_sep)

    @staticmethod
    def _from_obj(value, def_type, def_sep):
        ''' return an Ntv object from an object value '''
        ntv_name, str_type, ntv_value, sep = Ntv._decode(value)
        if not sep:
            sep = def_sep
        if isinstance(ntv_value, list) and sep in (None, '::'):
            def_type = Ntv._agreg_type(str_type, def_type, False)
            if sep and not def_type:
                sep = None
            if sep:
                sep = ':'
            ntv_list = [Ntv.from_obj(val, def_type, sep) for val in ntv_value]
            return NtvList(ntv_list, ntv_name, def_type)
        if sep == ':' or (not isinstance(ntv_value, dict) and sep is None):
            ntv_type = Ntv._agreg_type(str_type, def_type, True)
            return NtvSingle(ntv_value, ntv_name, ntv_type,)
        if isinstance(ntv_value, dict) and len(ntv_value) != 1 and sep in (None, '::'):
            keys = list(ntv_value.keys())
            values = list(ntv_value.values())
            def_type = Ntv._agreg_type(str_type, def_type, False)
            if sep and not def_type:
                sep = None
            if sep:
                sep = ':'
            ntv_list = [Ntv.from_obj({key: val}, def_type, sep)
                        for key, val in zip(keys, values)]
            return NtvSet(ntv_list, ntv_name, def_type,)
        if isinstance(ntv_value, dict) and len(ntv_value) == 1 and sep in (None, ':'):
            ntv_type = Ntv._agreg_type(str_type, def_type, True)
            ntv_single = Ntv.from_obj(ntv_value, ntv_type, sep)
            return NtvSingle(ntv_single, ntv_name, ntv_type)
        raise NtvError('separator ":" is not compatible with value')

    def __len__(self):
        ''' len of ntv_value'''
        if isinstance(self.ntv_value, (list, set)):
            return len(self.ntv_value)
        return 1

    def __str__(self):
        '''return string format'''
        return self.to_obj(encoded=True)

    def __repr__(self):
        '''return classname and code'''
        return json.dumps(self.to_repr(False, False, False, 10))

    def __getitem__(self, ind):
        ''' return ntv_value item (value conversion)'''
        if isinstance(ind, tuple):
            return [copy(self.ntv_value[i]) for i in ind]
        return copy(self.ntv_value[ind])

    def __setitem__(self, ind, value):
        ''' modify ntv_value item'''
        if ind < 0 or ind >= len(self):
            raise NtvError("out of bounds")
        self.ntv_value[ind] = value

    def __delitem__(self, ind):
        '''remove a ntv_value item'''
        self.ntv_value.pop(ind)

    @property
    def type_str(self):
        '''return a string with the NTV type of the entity'''
        if not self.ntv_type:
            return None
        return self.ntv_type.long_name

    @property
    def code_ntv(self):
        '''return a NTV code to indicate if name or type are present'''
        code = ''
        if self.ntv_name:
            code += 'N'
        if self.ntv_type:
            code += 'T'
        code += 'V'
        return code

    def to_repr(self, nam=True, typ=True, val=True, maxi=10):
        '''return a simple json representation of the ntv entity'''
        clas = self.__class__.__name__
        dic = {'NtvList': 'l', 'NtvSet': 's', 'NtvSingle': 'v'}
        ntv = dic[clas] + self.code_ntv[:-1]
        if self.ntv_name and nam:
            ntv += '-' + self.ntv_name
        if self.ntv_type and typ:
            ntv += '-' + self.ntv_type.long_name
        if isinstance(self, NtvSingle) and not isinstance(self.ntv_value, NtvSingle):
            if val:
                if ntv:
                    ntv += '-'
                ntv += json.dumps(self.ntv_value)
            return ntv
        if isinstance(self, NtvSingle) and isinstance(self.ntv_value, NtvSingle):
            return {ntv:  self.ntv_value.to_repr(nam, typ, val)}
        if isinstance(self, (NtvList, NtvSet)):
            return {ntv:  [ntv.to_repr(nam, typ, val) for ntv in self.ntv_value[:maxi]]}
        raise NtvError('the ntv entity is not consistent')

    def to_obj(self, def_type=None, **kwargs):
        '''return the JSON representation of the NTV entity (json-ntv format)'''
        option = {'encoded': False, 'encode_format': 'json',
                  'simpleval': False} | kwargs
        value, single = self._obj_value(**option)
        sep = '::'
        if self.__class__.__name__ == 'NtvSingle':
            sep = ':'
        name = self._obj_name(sep, single, not option['simpleval'], def_type)
        not_single = isinstance(value, list) or (
            isinstance(value, dict) and len(value) != 1)
        if name == ':' and (not not_single or option['simpleval'] or def_type):
            name = None
        elif name == '::' and (not_single or option['simpleval'] or not def_type):
            name = None
        if not name:
            json_obj = value
        else:
            json_obj = {name: value}
        if option['encoded'] and option['encode_format'] == 'json':
            return json.dumps(json_obj)
        return json_obj

    def _obj_value(self):
        # defined into child classes
        return (None, None)

    def _obj_name(self, sep=':', typ=True, nam=True, def_type=None):
        '''return the JSON name of the NTV entity (json-ntv format)'''
        typ = typ and self.ntv_type
        nam = nam and self.ntv_name
        if not typ and not nam and not sep:
            return ''
        if not typ and not nam and sep:
            return sep
        if not typ and nam:
            return self.ntv_name
        relative_type = Ntv._relative_type(def_type, self.ntv_type.long_name)
        if not relative_type:
            sep = ''
        if typ and not nam:
            return sep + relative_type
        return self.ntv_name + sep + relative_type

    @staticmethod
    def _agreg_type(str_type, def_type, single):
        '''aggregate str_type and def_type to return an NtvType or a Namespace if not single'''
        if not str_type and (not def_type or isinstance(def_type, Namespace)):
            return None
        if not str_type and isinstance(def_type, NtvType):
            return def_type
        clas = NtvType
        if str_type[-1] == '.':
            clas = Namespace
        if not def_type:
            return clas.add(str_type)
        if clas == NtvType or clas == Namespace and not single:
            try:
                return clas.add(str_type)
            except NtvTypeError:
                return clas.add(Ntv._join_type(def_type.long_name, str_type))
        raise NtvError(str_type + 'and' +
                       def_type.long_name + 'are incompatible')

    @staticmethod
    def _join_type(namesp, str_type):
        '''join Namespace string and NtvType or Namespace string'''
        namesp_split = namesp.split('.')[:-1]
        for name in str_type.split('.'):
            if not name in namesp_split:
                namesp_split.append(name)
        return '.'.join(namesp_split)

    @staticmethod
    def _relative_type(namesp, str_type):
        '''return relative str_type from namesp type'''
        if not namesp and not str_type:
            return ''
        if namesp == str_type:
            return ''
        if not namesp or not namesp in str_type:
            return str_type
        if not str_type and namesp[-1] != ".":
            return namesp
        namesp_split = namesp.split('.')[:-1]
        str_type_split = str_type.split('.')
        ind = 0
        for ind, name in enumerate(str_type_split):
            if not name in namesp_split:
                break
        return '.'.join(str_type_split[ind:])

    @staticmethod
    def _decode(json_value):
        '''return (name, type, value, separator) of the json value'''
        if json_value is None:
            return (None, None, None, None)
        if isinstance(json_value, (list, int, str, float, bool)):
            return (None, None, json_value, None)
        if isinstance(json_value, dict) and len(json_value) != 1:
            return (None, None, json_value, None)
        if isinstance(json_value, dict) and len(json_value) == 1:
            json_name = list(json_value.keys())[0]
            val = json_value[json_name]
            nam, typ, sep = Ntv._from_obj_name(json_name)
            return (nam, typ, val, sep)
        nam, typ, val = Ntv._cast(json_value)
        return (nam, typ, val, ':')

    @staticmethod
    def _cast(data):
        '''return (name, type, value) of the data'''
        dic_geo_cl = {'point': 'point', 'multipoint': 'multipoint', 'linestring': 'line',
                      'multilinestring': 'multiline', 'polygon': 'polygon',
                      'multipolygon': 'multipolygon'}
        match data.__class__.__name__.lower():
            case 'date':
                return (None, 'date', data.isoformat())
            case 'time':
                return (None, 'time', data.isoformat())
            case 'datetime':
                return (None, 'datetime', data.isoformat())
            case 'point' | 'multipoint' | 'linestring' | 'multilinestring' | \
                    'polygon' | 'multipolygon':
                return (None, dic_geo_cl[data.__class__.__name__.lower()],
                        util.listed(data.__geo_interface__['coordinates']))
            case _:
                raise NtvError('connector is not defined to NTV entity')
        return (None, None, None)

    def _uncast(self):
        '''return object from ntv_value'''
        dic_geo = {'point': 'point', 'multipoint': 'multipoint', 'line': 'linestring',
                   'multiline': 'multilinestring', 'polygon': 'polygon',
                   'multipolygon': 'multipolygon'}
        if self.ntv_type is None:
            return (self.ntv_value, True)
        match self.ntv_type.name:
            case 'date':
                return (date.fromisoformat(self.ntv_value), False)
            case 'time':
                return (time.fromisoformat(self.ntv_value), False)
            case 'datetime':
                return (datetime.fromisoformat(self.ntv_value), False)
            case 'point' | 'multipoint' | 'line' | 'multiline' | 'polygon' | 'multipolygon':
                return (geometry.shape({"type": dic_geo[self.ntv_type.name],
                                        "coordinates": self.ntv_value}), False)
            case _:
                return (self.ntv_value, True)

    @staticmethod
    def _from_obj_name(string):
        '''return a tuple with name, type ans separator from string'''
        if not isinstance(string, str):
            raise NtvError('a json-name have to be str')
        if string == '':
            return (None, None, None)
        sep = None
        if '::' in string:
            sep = '::'
        elif ':' in string:
            sep = ':'
        if sep is None:
            return (string, None, None)
        split = string.rsplit(sep, 2)
        if len(split) == 1:
            return (string, None, sep)
        if split[0] == '':
            return (None, split[1], sep)
        if split[1] == '':
            return (split[0], None, sep)
        return (split[0], split[1], sep)


class NtvSingle(Ntv):
    ''' An NTV-single entity is a Ntv entity not composed with other entities.

    *Attributes :

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**:  value of the entity

    The methods defined in this class are :

    *classmethods*
    - `from_obj`

    *dynamic values (@property)
    - `type_str`
    - `code_ntv`

    *instance methods*
    - `to_obj`
    '''

    def __init__(self, value, ntv_name=None, ntv_type=None):
        '''NtvSingle constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **value**: value of the entity
        '''
        is_json_ntv = value is None or isinstance(
            value, (list, int, str, float, bool, dict, NtvSingle))
        if not ntv_type and not is_json_ntv:
            name, ntv_type, ntv_value = Ntv._cast(value)
            if not ntv_name:
                ntv_name = name
        elif ntv_type and not is_json_ntv:
            raise NtvError('ntv_value is not compatible with ntv_type')
        else:
            ntv_value = value
        if ntv_type and isinstance(ntv_type, str) and ntv_type[-1] == '.':
            raise NtvError('the ntv_type is not valid')
        Ntv.__init__(self, ntv_value, ntv_name, ntv_type)

    def __eq__(self, other):
        ''' equal if name type and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_type == other.ntv_type and\
            self.ntv_value == other.ntv_value

    def _obj_value(self, **kwargs):
        option = {'encoded': False, 'encode_format': 'json',
                  'simpleval': False} | kwargs
        if isinstance(self.ntv_value, NtvSingle):
            def_type = ''
            if self.ntv_type:
                def_type = self.ntv_type.long_name
            option2 = option | {'encoded': False}
            return (self.ntv_value.to_obj(def_type=def_type, **option2), True)
        if option['encode_format'] == 'json':
            return (self.ntv_value, True)
        return Ntv._uncast(self)


class NtvList(Ntv):
    '''An NTV-list entity is a Ntv entity where:
        - ntv_value is a list of NTV entities,
        - ntv_type is a default type available for included NTV entities

    *Attributes :

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**:  value of the entity

    The methods defined in this class are :

    *classmethods*
    - `from_obj`

    *dynamic values (@property)
    - `type_str`
    - `code_ntv`

    *instance methods*
    - `to_obj`
    '''

    def __init__(self, list_ntv, ntv_name=None, ntv_type=None):
        '''NtvList constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - default type or namespace of the included entities
        - **list_ntv**: list - list of Ntv objects or obj_value of Ntv objectd
        '''
        if not isinstance(list_ntv, list):
            raise NtvError('ntv_value is not a list')
        ntv_value = [Ntv.from_obj(ntv, ntv_type, ':') for ntv in list_ntv]
        Ntv.__init__(self, ntv_value, ntv_name, ntv_type)

    def __eq__(self, other):
        ''' equal if name and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_value == other.ntv_value

    def _obj_value(self, **kwargs):
        '''return the Json format of the ntv_value'''
        option = {'encoded': False, 'encode_format': 'json',
                  'simpleval': False} | kwargs
        option2 = option | {'encoded': False}
        def_type = ''
        if self.ntv_type:
            def_type = self.ntv_type.long_name
        return ([ntv.to_obj(def_type=def_type, **option2)
                 for ntv in self.ntv_value], True)


class NtvSet(Ntv):
    '''An NTV-set entity is a Ntv entity where:
        - ntv_value is a list of NTV entities,
        - ntv_type is a default type available for included NTV entities

    *Attributes :

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**:  value of the entity

    The methods defined in this class are :

    *classmethods*
    - `from_obj`

    *dynamic values (@property)
    - `type_str`
    - `code_ntv`

    *instance methods*
    - `to_obj`
    '''

    def __init__(self, list_ntv, ntv_name=None, ntv_type=None):
        '''NtvSet constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - default type or namespace of the included entities
        - **list_ntv**: list - list of Ntv objects or obj_value of Ntv objectd
        '''
        if not isinstance(list_ntv, list):
            raise NtvError('ntv_value is not a list')
        ntv_value = [Ntv.from_obj(ntv, ntv_type, ':') for ntv in list_ntv]
        Ntv.__init__(self, ntv_value, ntv_name, ntv_type)

    def __eq__(self, other):
        ''' equal if name and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_value == other.ntv_value

    def _obj_value(self, **kwargs):
        '''return the Json format of the ntv_value'''
        option = {'encoded': False, 'encode_format': 'json',
                  'simpleval': False} | kwargs
        option2 = option | {'encoded': False}
        def_type = ''
        if self.ntv_type:
            def_type = self.ntv_type.long_name
        return ({list(ntv.to_obj(def_type=def_type, **option2).items())[0][0]:
                 list(ntv.to_obj(def_type=def_type, **option2).items())[0][1]
                for ntv in self.ntv_value}, True)


class NtvError(Exception):
    ''' NTV Exception'''
    # pass
