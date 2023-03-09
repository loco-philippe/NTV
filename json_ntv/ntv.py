# -*- coding: utf-8 -*-
"""
Created on Feb 27 22:44:05 2023

@author: Philippe@loco-labs.io

The `ntv` module contains the NtvSingle, NtvSet and NtvList classes for NTV entity.

# 1 - JSON-NTV structure

The NTV triplet (name, type, value) is represented using a JSON-NTV format inspired by the RFC [JSON-ND](https://github.com/glenkleidon/JSON-ND) project :
- **```value```** (if name and type are not documented)
- **```{ "name" : value }```** (if name is documented but not type)
- **```{ ":type" : value }```** for primitive entities and **```{ "::type" : value }```** for structured entities (if type is documented but not name)
- **```{ "name:type" : value }```** for primitive entities and **```{ "name::type" : value }```** for structured entities (if type and name are documented).     

For an NTV-single, the value is the JSON-value of the entity. 
For an NTV-list, value is a JSON-array where JSON-elements are the JSON-NTV formats of included NTV entities. 
For an NTV-set, value is a JSON-object where JSON-members are the JSON-members of the JSON-NTV formats of included NTV entities. 

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
import json
from namespace import NtvType, Namespace
from util import util

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
    - `to_json_name`
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
    def from_obj(value, def_type=None):
        ''' return an Ntv object from an object value '''
        if value.__class__.__name__ in ['NtvSingle', 'NtvList', 'NtvSet']:
            return value
        if value is None:
            return NtvSingle(None)
        ntv_name, str_type, ntv_value, sep = Ntv._decode(value)
        if isinstance(ntv_value, list) and sep in (None, '::'):
            def_type = Ntv._agreg_type(str_type, def_type, False)
            ntv_list = [Ntv.from_obj(val, def_type) for val in ntv_value]
            return NtvList(ntv_list, ntv_name, def_type)
        if (isinstance(ntv_value, (int, str, float, bool, list)) 
            or ntv_value is None) and sep in (None, ':'):
            ntv_type = Ntv._agreg_type(str_type, def_type, True)            
            return NtvSingle(ntv_value, ntv_name, ntv_type,)
        if isinstance(ntv_value, dict) and len(ntv_value) != 1 and sep in (None, '::'):
            keys = list(ntv_value.keys())
            values = list(ntv_value.values())
            def_type = Ntv._agreg_type(str_type, def_type, False)
            ntv_list = [Ntv.from_obj({key: val}, def_type)
                        for key, val in zip(keys, values)]
            return NtvSet(ntv_list, ntv_name, def_type,)
        if isinstance(ntv_value, dict) and len(ntv_value) == 1 and sep in (None, ':'):
            ntv_type = Ntv._agreg_type(str_type, def_type, True)            
            return NtvSingle(ntv_value, ntv_name, ntv_type)
        #raise NtvError(json.dumps(value) + ' is not a consistent Json NTV value')
        return NtvSingle(ntv_value, ntv_name, str_type)

    def __repr__(self):
        '''return classname and code'''
        return self.__class__.__name__ + '(' + self.code_ntv + ')'

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

    def to_json_name(self, sep=':'):
        '''return the JSON name of the NTV entity (json-ntv format)'''
        if not self.ntv_type and not self.ntv_name:
            return ''
        if not self.ntv_type and self.ntv_name:
            return self.ntv_name
        if self.ntv_type and not self.ntv_name:
            return sep + self.type_str
        return self.ntv_name + sep + self.type_str

    def to_obj(self):
        '''return the JSON representation of the NTV entity (json-ntv format)'''
        if not self.json_name:
            return self.json_value
        return {self.json_name: self.json_value}

    @staticmethod 
    def _agreg_type(str_type, def_type, single):
        '''aggregate str_type and def_type to return an NtvType or a Namespace if not single'''
        if not str_type and not def_type:
            return None
        if not str_type and isinstance(def_type, NtvType):
            return def_type        
        if not str_type and isinstance(def_type, Namespace):
            return None 
        if not def_type and str_type[-1] == '.':
            return Namespace.add(str_type)
        if not def_type and str_type[-1] != '.':
            return NtvType.add(str_type)
        if str_type[-1] != '.':
            try:
                return NtvType.add(str_type)
            except: 
                return NtvType.add(Ntv._join_type(def_type.long_name, str_type))
        if str_type[-1] == '.' and not single:
            try:
                return Namespace.add(str_type)
            except:
                return Namespace.add(Ntv._join_type(def_type.long_name, str_type))
        raise NtvError(str_type + 'and' + def_type.long_name + 'are incompatible')               

    @staticmethod 
    def _join_type(namesp, str_type):
        '''join Namespace string and NtvType or Namespace string'''
        namesp_split = namesp.split('.')[:-1]
        for name in str_type.split('.'):
            if not name in namesp_split:
                namesp_split.append(name)
        return '.'.join(namesp_split)
        
        
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
            nam, typ, sep = Ntv._from_json_name(json_name)
            return (nam, typ, val, sep)
        #raise NtvError('the value is not a JSON value')               
        val = Ntv._cast(json_value)
        return (val[0], val[1], val[2], None)

    @staticmethod
    def _cast(data):
        '''return (name, type, value) of the data'''
        match data.__class__.__name__:
            case 'date':
                return (None, 'date', data.isoformat())
            case 'time':
                return (None, 'time', data.isoformat())            
            case 'datetime':
                return (None, 'datetime', data.isoformat()) 
            case 'Point':
                return (None, 'point', util.listed(data.__geo_interface__['coordinates']))
            case 'MultiPoint':
                return (None, 'multipoint', util.listed(data.__geo_interface__['coordinates']))
            case 'LineString':
                return (None, 'line', util.listed(data.__geo_interface__['coordinates']))
            case 'MultiLineString':
                return (None, 'multiline', util.listed(data.__geo_interface__['coordinates']))
            case 'Polygon':
                return (None, 'polygon', util.listed(data.__geo_interface__['coordinates']))    
            case 'MultiPolygon':
                return (None, 'multipolygon', util.listed(data.__geo_interface__['coordinates']))    
            case _:
                raise NtvError('connector is not defined to NTV entity')   

    @staticmethod
    def _from_json_name(string):
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
    - `json_name`
    - `json_value`
    - `type_str`
    - `code_ntv`

    *instance methods*
    - `to_json_name`
    - `to_obj`
    '''

    def __init__(self, value, ntv_name=None, ntv_type=None):
        '''NtvSingle constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **value**: value of the entity
        '''
        is_json = value is None or isinstance(value, (list, int, str, float, bool, dict))
        if not ntv_type and not is_json:
            name, ntv_type, ntv_value = Ntv._cast(value)
            if not ntv_name :
                ntv_name = name
        elif ntv_type and not is_json:
            raise NtvError('ntv_value is not compatible with ntv_type')
        else: 
            ntv_value = value
        if ntv_type and isinstance(ntv_type, str) and ntv_type[-1] == '.' :
            raise NtvError('the ntv_type is not valid')
        Ntv.__init__(self, ntv_value, ntv_name, ntv_type)

    def __str__(self):
        '''return string format'''
        return json.dumps(self.to_obj())

    def __eq__(self, other):
        ''' equal if name type and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_type == other.ntv_type and\
            self.ntv_value == other.ntv_value

    @property
    def json_name(self):
        '''return the string format of ntv_name + ntv_type'''
        return Ntv.to_json_name(self, ':')

    @property
    def json_value(self):
        '''return the Json format of the ntv_value'''
        return self.ntv_value


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
    - `json_name`
    - `json_value`
    - `type_str`
    - `code_ntv`

    *instance methods*
    - `to_json_name`
    - `to_obj`
    '''

    def __init__(self, list_ntv, ntv_name=None, ntv_type=None):
        '''NtvList constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - default type or namespace of the included entities
        - **list_ntv**: list - list of Ntv objects or json_value of Ntv objectd
        '''
        if list_ntv.__class__.__name__ != 'list':
            raise NtvError('ntv_value is not a list')
        #Ntv.__init__(self, list_ntv, ntv_name, ntv_type)
        ntv_value = [Ntv.from_obj(ntv, ntv_type) for ntv in list_ntv]
        Ntv.__init__(self, ntv_value, ntv_name, ntv_type)

    def __str__(self):
        '''return string format'''
        return json.dumps(self.to_obj())

    def __eq__(self, other):
        ''' equal if name and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_value == other.ntv_value

    @property
    def json_name(self):
        '''return the string format of ntv_name + ntv_type'''
        return Ntv.to_json_name(self, '::')

    @property
    def json_value(self):
        '''return the Json format of the ntv_value'''
        return [ntv.to_obj() for ntv in self.ntv_value]


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
    - `json_name`
    - `json_value`
    - `type_str`
    - `code_ntv`

    *instance methods*
    - `to_json_name`
    - `to_obj`
    '''

    def __init__(self, list_ntv, ntv_name=None, ntv_type=None):
        '''NtvSet constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - default type or namespace of the included entities
        - **list_ntv**: list - list of Ntv objects or json_value of Ntv objectd
        '''
        if list_ntv.__class__.__name__ != 'list':
            raise NtvError('ntv_value is not a list')
        #Ntv.__init__(self, list_ntv, ntv_name, ntv_type)
        ntv_value = [Ntv.from_obj(ntv, ntv_type) for ntv in list_ntv]
        Ntv.__init__(self, ntv_value, ntv_name, ntv_type)
        
    def __str__(self):
        '''return string format'''
        return json.dumps(self.to_obj())

    def __eq__(self, other):
        ''' equal if name and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_value == other.ntv_value

    @property
    def json_name(self):
        '''return the string format of ntv_name + ntv_type'''
        return Ntv.to_json_name(self, '::')

    @property
    def json_value(self):
        '''return the Json format of the ntv_value'''
        return {ntv.json_name: ntv.json_value for ntv in self.ntv_value}


class NtvError(Exception):
    ''' NTV Exception'''
    # pass
