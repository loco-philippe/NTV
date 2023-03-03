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
from namespace import NtvType


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
        '''NtvSingle constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **ntv_value**: value of the entity
        '''
        if ntv_type:
            self.ntv_type = NtvType.add(ntv_type)
        else:
            self.ntv_type = None
        self.ntv_name = ntv_name
        self.ntv_value = ntv_value

    @staticmethod
    def from_obj(value):
        ''' return an Ntv object from a Json value '''
        if value.__class__.__name__ in ['NtvSingle', 'NtvList', 'NtvSet']:
            return value
        ntv_name, ntv_type, ntv_value = Ntv._decode(value)
        if isinstance(ntv_value, list):
            ntv_list = [Ntv.from_obj(val) for val in ntv_value]
            return NtvList(ntv_list, ntv_name, ntv_type,)
        if isinstance(ntv_value, (int, str, float, bool)):
            return NtvSingle(ntv_value, ntv_name, ntv_type,)
        if isinstance(ntv_value, dict) and len(ntv_value) != 1:
            keys = list(ntv_value.keys())
            values = list(ntv_value.values())
            ntv_list = [Ntv.from_obj({key: val})
                        for key, val in zip(keys, values)]
            return NtvSet(ntv_list, ntv_name, ntv_type,)
        if isinstance(ntv_value, dict) and len(ntv_value) == 1:
            return NtvSingle(ntv_value, ntv_name, ntv_type)
        #if None

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
    def _decode(value):
        if isinstance(value, (list, int, str, float, bool)):
            return (None, None, value)
        if isinstance(value, dict) and len(value) != 1:
            return (None, None, value)
        if isinstance(value, dict) and len(value) == 1:
            json_name = list(value.keys())[0]
            val = value[json_name]
            sep = ':'
            if isinstance(val, list) or (isinstance(val, dict) and len(val) != 1):
                sep = '::'
            nam, typ = Ntv._from_json_name(json_name, sep)
            return (nam, typ, val)
        # if None and other cases

    @staticmethod
    def _from_json_name(string, sep=':'):
        '''return a tuple with name and type from string'''
        if not isinstance(string, str):
            raise NtvError('a json-name have to be str')
        if string == '':
            return (None, None)
        split = string.rsplit(sep, 2)
        if len(split) == 1:
            return (string, None)
        if split[0] == '':
            return (None, string)
        if split[1] == '':
            return (split[0], None)
        return (split[0], split[1])


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

    def __init__(self, ntv_value, ntv_name=None, ntv_type=None):
        '''NtvSingle constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **ntv_value**: Json entity - value of the entity
        '''
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
        - **ntv_type**: String (default None) - default type of the included entities
        - **list_ntv**: list - list of Ntv objects or json_value of Ntv objectd
        '''
        if list_ntv.__class__.__name__ != 'list':
            raise NtvError('ntv_value is not a list')
        Ntv.__init__(self, list_ntv, ntv_name, ntv_type)

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
        - **ntv_type**: String (default None) - default type of the included entities
        - **list_ntv**: list - list of Ntv objects or json_value of Ntv objectd
        '''
        if list_ntv.__class__.__name__ != 'list':
            raise NtvError('ntv_value is not a list')
        Ntv.__init__(self, list_ntv, ntv_name, ntv_type)

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
