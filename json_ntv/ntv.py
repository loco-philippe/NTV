# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `ntv` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

It contains the classes `NtvSingle`, `NtvList`, `Ntv`(abstract),
`NtvConnector`, `NtvTree` and `NtvError` for NTV entities.

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
For an NTV-list, value is a JSON-array (JSON-object) where JSON-elements (JSON-members)
are the JSON-NTV formats of included NTV entities.

This JSON-NTV format allows full compatibility with existing JSON structures:
- a JSON-number, JSON-string or JSON-boolean is the representation of an NTV-single entity,
- a JSON-object with a single member is the representation of an NTV-single entity
- a JSON-array or JSON-object is the representation of an NTV-list entity

# 2 - Examples of JSON-NTV representations
- NTV-single, simple format :
   - ```"lyon"```
   - ```52.5```
- NTV-single, named format :
   - ```{ "paris:point" : [2.3522, 48.8566] }```
   - ```{ ":point" : [4.8357, 45.7640] }```
   - ```{ "city" : "paris" }```
- NTV-list, simple format (whithout names):
   - ```[ [2.3522, 48.8566], {"lyon" : [4.8357, 45.7640]} ]```
   - ```[ { ":point" : [2.3522, 48.8566]}, {":point" : [4.8357, 45.7640]} ]```
   - ```[ 4, 45 ]```
   - ```[ "paris" ]```
   - ```[ ]```
- NTV-list, named format (whithout names):
   - ```{ "cities::point" : [ [2.3522, 48.8566], [4.8357, 45.7640] ] }```
   - ```{ "::point" : [ [2.3522, 48.8566], {"lyon" : [4.8357, 45.7640]} ] }```
   - ```{ "simple list" : [ 4, 45.7 ] }```
   - ```{ "generic date::dat" : [ "2022-01-28T18-23-54Z", "2022-01-28", 1234.78 ] }```
- NTV-list, simple format (with names):
   - ```{ "nom”: "white", "prenom": "walter", "surnom": "heisenberg" }```
   - ```{ "paris:point" : [2.3522, 48.8566] , "lyon" : "france" }```
   - ```{ "paris" : [2.3522, 48.8566], "" : [4.8357, 45.7640] }```
   - ```{ }```
- NTV-list, named format (with names):
   - ```{ "cities::point": { "paris": [2.352, 48.856], "lyon": [4.835, 45.764]}}```
   - ```{ "cities" :     { "paris:point" : [2.3522, 48.8566] , "lyon" : "france"} }```
   - ```{ "city" : { "paris" : [2.3522, 48.8566] } }```

"""
from abc import ABC, abstractmethod
import datetime
import json
from json import JSONDecodeError

from json_ntv.namespace import NtvType, Namespace, str_type, relative_type, agreg_type


class Ntv(ABC):
    ''' The Ntv class is an abstract class used for all NTV entities.

    *Attributes :*

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**:  value of the entity
    - **parent**:  parent NtvList entity
    - **_row**:  row in the parent NtvList

    *dynamic values (@property)*
    - `address`
    - `address_name`
    - `json_array`
    - `type_str`
    - `code_ntv`
    - `max_len`
    - `val`

    The methods defined in this class are :

    *Ntv constructor (staticmethod)*
    - `obj`
    - `from_obj`
    - `from_att`

    *instance methods*
    - `alike`
    - `from_value`
    - `json_name`
    - `set_name`
    - `set_type`
    - `set_value`
    - `to_obj`
    - `to_repr`
    - `to_mermaid`
    - `to_tuple`

    *utility methods*
    - `from_obj_name` *(staticmethod)*
    '''

    def __init__(self, ntv_value, ntv_name, ntv_type):
        '''Ntv constructor.

        *Parameters*

        - **ntv_value**: Json entity - value of the entity
        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String or NtvType or Namespace (default None) - type of the entity
        '''
        if isinstance(ntv_type, (NtvType, Namespace)):
            self.ntv_type = ntv_type
        elif ntv_type and ntv_type[-1] != '.':
            self.ntv_type = NtvType.add(ntv_type)
        elif ntv_type and ntv_type[-1] == '.':
            self.ntv_type = Namespace.add(ntv_type)
        else:
            self.ntv_type = None
        if not isinstance(ntv_name, str):
            ntv_name = ''
        self.ntv_name = ntv_name
        self.ntv_value = ntv_value
        self.parent = None
        self._row = None

    @staticmethod
    def obj(data, no_typ=False, decode_str=False):
        ''' return an Ntv entity from data.
        **Data** can be :
        - a tuple with value, name, typ and cat (see `from_att` method)
        - a value to decode (see `from_obj`method)
        - **no_typ** : boolean (default None) - if True, NtvList is with 'json' type
        - **decode_str**: boolean (default False) - if True, string are loaded in json data'''
        if isinstance(data, tuple):
            return Ntv.from_att(*data, decode_str=decode_str)
        return Ntv.from_obj(data, no_typ=no_typ, decode_str=decode_str)

    @staticmethod
    def from_att(value, name, typ, cat, decode_str=False):
        ''' return an Ntv entity.

        *Parameters*

        - **value**: Ntv entity or value to convert in an Ntv entity
        - **name** : string - name of the Ntv entity
        - **typ** : string or NtvType - type of the NTV entity
        - **cat**: string - NTV category ('single', 'list')
        - **decode_str**: boolean (default False) - if True, string are loaded as json data'''
        
        value = Ntv._from_value(value, decode_str)
        if value.__class__.__name__ in ['NtvSingle', 'NtvList']:
            return value
        if isinstance(value, list) and cat == 'list':
            return NtvList(value, name, typ)
        if cat == 'single':
            return NtvSingle(value, name, typ)
        return Ntv.from_obj(value, def_type=typ)

    @staticmethod
    def from_obj(value, def_type=None, def_sep=None, no_typ=False, decode_str=False, typ_auto=False):
        ''' return an Ntv entity from an object value.

        *Parameters*

        - **value**: Ntv value to convert in an Ntv entity
        - **no_typ** : boolean (default None) - if True, NtvList is with 'json' type
        - **def_type** : NtvType or Namespace (default None) - default type of the value
        - **def_sep**: ':', '::' or None (default None) - default separator of the value
        - **decode_str**: boolean (default False) - if True, string are loaded as json data'''
        value = Ntv._from_value(value, decode_str)
        if value.__class__.__name__ in ['NtvSingle', 'NtvList']:
            return value
        ntv_name, str_typ, ntv_value, sep = Ntv._decode(value)
        sep = def_sep if not sep else sep
        if isinstance(ntv_value, list) and sep in (None, '::'):
            def_type = agreg_type(str_typ, def_type, False)
            sep = None if sep and not def_type else sep
            sep = ':' if sep else sep
            ntv_list = [Ntv.from_obj(val, def_type, sep) for val in ntv_value]
            '''if typ_auto and not def_type and ntv_list:
                def_type = ntv_list[0].ntv_type'''
            def_type = 'json' if no_typ else def_type
            return NtvList(ntv_list, ntv_name, def_type)
        if sep == ':' or (sep is None and isinstance(ntv_value, dict) and
                          len(ntv_value) == 1):
            ntv_type = agreg_type(str_typ, def_type, False)
            return NtvSingle(ntv_value, ntv_name, ntv_type)
        if sep is None and not isinstance(ntv_value, dict):
            is_json = isinstance(value, (int, str, float, bool))
            ntv_type = agreg_type(str_typ, def_type, is_json)
            return NtvSingle(ntv_value, ntv_name, ntv_type)
        if isinstance(ntv_value, dict) and (sep == '::' or len(ntv_value) != 1 and
                                            sep is None):
            keys = list(ntv_value.keys())
            values = list(ntv_value.values())
            def_type = agreg_type(str_typ, def_type, False)
            sep = None if sep and not def_type else sep
            sep = ':' if sep else sep
            ntv_list = [Ntv.from_obj({key: val}, def_type, sep)
                        for key, val in zip(keys, values)]
            if not def_type and ntv_list:
                def_type = ntv_list[0].ntv_type
            def_type = 'json' if no_typ else def_type
            return NtvList(ntv_list, ntv_name, def_type)
        raise NtvError('separator ":" is not compatible with value')

    def __len__(self):
        ''' len of ntv_value'''
        if isinstance(self.ntv_value, list):
            return len(self.ntv_value)
        return 1

    def __str__(self):
        '''return string format'''
        return self.to_obj(encoded=True)

    def __repr__(self):
        '''return classname and code'''
        return json.dumps(self.to_repr(False, False, False, 10), cls=NtvJsonEncoder)

    def __contains__(self, item):
        ''' item of Ntv entities'''
        if isinstance(self.val, list):
            return item in self.ntv_value
        return item == self.ntv_value

    def __iter__(self):
        ''' iterator for Ntv entities'''
        if isinstance(self, NtvSingle):
            return iter([self.val])
        return iter(self.val)

    def __getitem__(self, selector):
        ''' return ntv_value item '''
        if isinstance(self, NtvSingle) and selector == 0:
            return self.ntv_value
        if isinstance(self, NtvSingle) and selector != 0:
            raise NtvError('item not present')
        if isinstance(selector, tuple):
            return [self.ntv_value[i] for i in selector]
        if isinstance(selector, str) and isinstance(self, NtvList):
            ind = [ntv.ntv_name for ntv in self.ntv_value].index(selector)
            return self.ntv_value[ind]
        return self.ntv_value[selector]

    def __setitem__(self, ind, value):
        ''' modify ntv_value item'''
        if ind < 0 or ind >= len(self):
            raise NtvError("out of bounds")
        self.ntv_value[ind] = value

    def __delitem__(self, ind):
        '''remove a ntv_value item'''
        self.ntv_value.pop(ind)

    def __lt__(self, other):
        ''' return a comparison between hash value'''
        return hash(self) < hash(other)

    @property
    def address(self):
        '''return a list of parent row from root'''
        if not self.parent:
            return [0]
        return self.parent.address + [self._row]

    @property
    def address_name(self):
        '''return a string of address'''
        name = ''
        for ind in self.address:
            name += str(ind) + '.'
        return name[:-1]

    @property
    def code_ntv(self):
        '''return a string with the NTV code composed with :
        - 'l' (for NtvList) or 's' (for NtvSingle)
        - 'N' if ntv_name is present
        - 'T' if ntv_type is present'''
        dic = {'NtvList': 'l', 'NtvSingle': 's'}
        code = dic[self.__class__.__name__]
        if self.ntv_name:
            code += 'N'
        if self.ntv_type and self.ntv_type.long_name != 'json':
            code += 'T'
        return code

    @property
    def max_len(self):
        '''return the highest len of Ntv entity included'''
        maxi = len(self)
        if isinstance(self.ntv_value, (list, set)):
            maxi = max(maxi, max(ntv.max_len for ntv in self.ntv_value))
        return maxi

    @property
    def name(self):
        '''return the ntv_name of the entity'''
        return self.ntv_name

    @property
    def type_str(self):
        '''return a string with the value of the NtvType of the entity'''
        if not self.ntv_type:
            return None
        return self.ntv_type.long_name

    @property
    def val(self):
        '''return the ntv_value of the entity'''
        return self.ntv_value

    @staticmethod
    def from_obj_name(string):
        '''return a tuple with name, type and separator from string'''
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

    def alike(self, ntv_value):
        ''' return a Ntv entity with same name and type.

        *Parameters*

        - **ntv_value**: list of ntv values'''
        return self.__class__(ntv_value, self.ntv_name, self.ntv_type)

    def from_value(self):
        '''return a Ntv entity from ntv_value'''
        if isinstance(self.ntv_value, list):
            return NtvList(self.ntv_value)
        return Ntv.obj(self.ntv_value)

    def json_name(self, def_type=None, string=False, explicit=False):
        '''return the JSON name of the NTV entity (json-ntv format)

        *Parameters*

        - **def_typ** : NtvType or Namespace (default None) - type of the parent entity
        - **string** : boolean (default False) - If True, return a string else a tuple
        - **explicit** : boolean (default False) - If True, type is always included'''
        if def_type is None:
            def_type = ''
        elif isinstance(def_type, (NtvType, Namespace)):
            def_type = def_type.long_name
        json_name = ''
        if self.ntv_name:
            json_name = self.ntv_name
        json_type = ''
        if self.ntv_type:
            json_type = relative_type(def_type, self.ntv_type.long_name)
        if json_type == 'json' and (not def_type or def_type == 'json') and not explicit:
            json_type = ''
        json_sep = self._obj_sep(json_type, def_type)
        if string:
            return json_name + json_sep + json_type
        return [json_name, json_sep, json_type]

    def set_name(self, name='', nodes='simple'):
        '''set new names to the entity

        *Parameters*

        - **name**: list or string (default '') - New name values
        - **nodes**: string (default 'simple') - nodes to be changed
            'simple': current entity
            'leaves': NtvSingle entities
            'inner': NtvList entities
            'all': all entities  '''
        match nodes:
            case 'simple':
                self.ntv_name = str(name)
            case 'leaves':
                if not isinstance(name, list):
                    name = [str(name)] * NtvTree(self).breadth
                for nam, ntv in zip(name, NtvTree(self).leaf_nodes):
                    ntv.ntv_name = nam
            case 'inner':
                if not isinstance(name, list):
                    name = [str(name)] * len(NtvTree(self).inner_nodes)
                for nam, ntv in zip(name, NtvTree(self).inner_nodes):
                    ntv.ntv_name = nam
            case 'all':
                if not isinstance(name, list):
                    name = [str(name)] * NtvTree(self).size
                for nam, ntv in zip(name, NtvTree(self).nodes):
                    ntv.ntv_name = nam
            case _:
                raise NtvError('the nodes option is not valid')

    def set_type(self, typ=None):
        '''set a new type to the entity (default None)'''
        if typ and not isinstance(typ, (str, NtvType, Namespace)):
            raise NtvError('the type is not a valid type')
        self.ntv_type = str_type(typ, True)

    def set_value(self, value=None):
        '''set new ntv_value of 'Ntv Single' entities included

        *Parameters*

        - **value**: list or single value'''
        if not isinstance(value, list):
            value = [value] * NtvTree(self).breadth
        ntv_val = NtvList(value)
        for val, ntv in zip(ntv_val, NtvTree(self).leaf_nodes):
            ntv.ntv_value = val.val

    def to_mermaid(self, title='', disp=False, row=False, leaves=False):
        '''return a mermaid flowchart.

        *Parameters*

        - **title**: String (default '') - title of the flowchart
        - **disp**: Boolean (default False) - if true, return a display else return
        - **row**: Boolean (default False) - if True, add the node row
        - **leaves**: Boolean (default False) - if True, add the leaf row
        a mermaid text diagram
        '''
        option = {'title': title, 'disp': disp, 'row': row, 'leaves': leaves}
        if disp:
            Ntv.obj({':$mermaid': self.to_obj()}).to_obj(
                format='obj', **option)
            return None
        return Ntv.obj({':$mermaid': self.to_obj()}).to_obj(format='obj', **option)

    def to_repr(self, nam=True, typ=True, val=True, maxi=10):
        '''return a simple json representation of the Ntv entity.

        *Parameters*

        - **nam**: Boolean (default True) : if true, the names are included
        - **typ**: Boolean (default True) : if true, the types are included
        - **val**: Boolean (default True) : if true, the values are included
        - **maxi**: Integer (default 10) : number of values to included for NtvList
        entities. If maxi < 1 all the values are included.
        '''
        ntv = self.code_ntv
        if nam and typ:
            ntv = ntv[0]
        if self.ntv_name and nam:
            ntv += '-' + self.ntv_name
        if self.ntv_type and typ:
            ntv += '-' + self.ntv_type.long_name
        clas = self.__class__.__name__
        clas_val = self.ntv_value.__class__.__name__
        if clas == 'NtvSingle' and clas_val != 'NtvSingle':
            if val:
                if ntv:
                    ntv += '-'
                ntv += json.dumps(self.ntv_value, cls=NtvJsonEncoder)
            return ntv
        if clas == 'NtvSingle' and clas_val == 'NtvSingle':
            return {ntv:  self.ntv_value.to_repr(nam, typ, val)}
        if clas == 'NtvList':
            if maxi < 1:
                maxi = len(self.ntv_value)
            return {ntv:  [ntvi.to_repr(nam, typ, val) for ntvi in self.ntv_value[:maxi]]}
        raise NtvError('the ntv entity is not consistent')

    def to_name(self, default=''):
        '''return the name of the NTV entity'''
        if self.ntv_name == '':
            return default
        return self.ntv_name

    def to_obj(self, def_type=None, **kwargs):
        '''return the JSON representation of the NTV entity (json-ntv format).

        *Parameters*

        - **def_type** : NtvType or Namespace (default None) - default type to apply
        to the NTV entity
        - **encoded** : boolean (default False) - choice for return format
        (string/bytes if True, dict/list/tuple else)
        - **format**  : string (default 'json')- choice for return format
        (json, cbor, obj)
        - **simpleval** : boolean (default False) - if True, only value (without
        name and type) is included
        - **name** : boolean (default true) - if False, name is not included
        - **json_array** : boolean (default false) - if True, Json-object is not used for NtvList
        '''
        option = {'encoded': False, 'format': 'json',
                  'simpleval': False, 'name': True, 'json_array': False} | kwargs
        if option['simpleval'] and isinstance(self, NtvList) and not self.json_array:
            value = NtvList(self).obj_value(def_type=def_type, **option)
        else:
            value = self.obj_value(def_type=def_type, **option)
        obj_name = self.json_name(def_type)
        if not option['name']:
            obj_name[0] = ''
        if option['simpleval']:
            name = ''
        elif option['format'] in ('cbor', 'obj') and not Ntv._is_json_ntv(value):
            name = obj_name[0]
        else:
            name = obj_name[0] + obj_name[1] + obj_name[2]
        json_obj = {name: value} if name else value
        if option['encoded'] and option['format'] == 'json':
            return json.dumps(json_obj, cls=NtvJsonEncoder)
        if option['encoded'] and option['format'] == 'cbor':
            return NtvConnector.connector()['CborConnec'].from_ntv(json_obj)
            #return NtvConnector.uncast(Ntv.from_obj({':$cbor': json_obj}), format=None)
        return json_obj

    def to_tuple(self, maxi=10):
        '''return the JSON representation of the NTV entity (json-ntv format).

        *Parameters*

        - **def_type** : NtvType or Namespace (default None) - default type to apply
        to the NTV entity
        - **encoded** : boolean (default False) - choice for return format
        (string/bytes if True, dict/list/tuple else)
        - **format**  : string (default 'json')- choice for return format
        (json, cbor, tuple, obj)
        - **simpleval** : boolean (default False) - if True, only value (without
        name and type) is included
        '''
        clas = self.__class__.__name__
        val = self.ntv_value
        name = self.ntv_name
        typ = None
        if self.ntv_type:
            typ = self.ntv_type.long_name
        if isinstance(self, NtvSingle) and not isinstance(val, NtvSingle):
            return (clas, name, typ, val)
        if isinstance(self, NtvSingle) and isinstance(val, NtvSingle):
            return (clas, name, typ, val.to_tuple(maxi=maxi))
        if isinstance(self, NtvList):
            if maxi < 1:
                maxi = len(val)
            return (clas, name, typ, [ntv.to_tuple(maxi=maxi) for ntv in val[:maxi]])
        raise NtvError('the ntv entity is not consistent')

    @abstractmethod
    def obj_value(self):
        '''return the ntv_value with different formats defined by kwargs'''

    @property
    @abstractmethod
    def json_array(self):
        ''' return the json_array dynamic attribute'''

    @abstractmethod
    def _obj_sep(self, json_type, def_type):
        ''' return separator to include in json_name'''

    @staticmethod
    def _from_value(value, decode_str=False):
        '''return a decoded value
        
        *Parameters*

        - **decode_str**: boolean (default False) - if True, string are loaded as json data'''

        if isinstance(value, bytes):
            value = Ntv.from_obj({'$cbor': value}).ntv_value
        elif decode_str and isinstance(value, str) and value.lstrip() and\
            value.lstrip()[0] in '"-{[0123456789':
            try:
                value = json.loads(value)
            except JSONDecodeError:
                pass
        string = isinstance(value, str)
        if value is None or (string and value == 'null'):
            return NtvSingle(None)
        if string and value == 'true':
            return NtvSingle(True)
        if string and value == 'false':
            return NtvSingle(False)
        return value

    @staticmethod
    def _decode(json_value):
        '''return (name, type, value, separator) of the json value'''
        if json_value is None:
            return (None, None, None, None)
        if isinstance(json_value, (list, int, str, float, bool)):
            return (None, None, json_value, None)
        if isinstance(json_value, dict):
            if len(json_value) != 1:
                return (None, None, json_value, None)
            key = list(json_value.keys())[0]
            if len(json_value) == 1 and not isinstance(key, str):
                return (None, None, json_value, None)
            val = json_value[key]
            nam, typ, sep = Ntv.from_obj_name(key)
            return (nam, typ, val, sep)
        return (*NtvConnector.cast(json_value), ':')

    @staticmethod
    def _is_json_ntv(val):
        ''' return True if val is a json type'''
        # return val is None or isinstance(val, (list, int, str, float, bool, dict))
        return val is None or isinstance(val, (list, int, str, float, bool, dict))

    @staticmethod
    def _listed(idx):
        '''transform a tuple of tuple in a list of list'''
        return [val if not isinstance(val, tuple) else Ntv._listed(val) for val in idx]


class NtvSingle(Ntv):
    ''' An NTV-single entity is a Ntv entity not composed with other entities.

    *Attributes :*

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**:  value of the entity

    *dynamic values (@property)*
    - `type_str`
    - `code_ntv`

    The methods defined in this class are :

    *Ntv constructor*
    - `obj`
    - `from_obj`
    - `from_att`

    *instance methods*
    - `set_name`
    - `set_type`
    - `set_value`
    - `to_obj`
    - `to_repr`
    '''

    def __init__(self, value, ntv_name=None, ntv_type=None, fast=False):
        '''NtvSingle constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **value**: value of the entity
        - **fast**: boolean (default False) - Ntv is created with a list of json values 
        without control
        '''
        if not fast:
            value, ntv_name, ntv_type = NtvSingle._decode_s(value, ntv_name, ntv_type)
            if ntv_type and isinstance(ntv_type, str) and ntv_type[-1] == '.':
                raise NtvError('the ntv_type is not valid')
        super().__init__(value, ntv_name, ntv_type)
    
    @staticmethod
    def _decode_s(ntv_value, ntv_name, ntv_type):
        '''return adjusted ntv_value, ntv_name, ntv_type'''
        is_json_ntv = Ntv._is_json_ntv(ntv_value)
        if is_json_ntv:
            if isinstance(ntv_value, (list)):
                ntv_value = [NtvSingle._decode_s(val, '', ntv_type)[0] for val in ntv_value]
            elif isinstance(ntv_value, (dict)):
                ntv_value = {key: NtvSingle._decode_s(val, '', ntv_type)[0] for key, val in ntv_value.items()}
        else:
            name, typ, ntv_value = NtvConnector.cast(ntv_value)
        if not ntv_type:
            if is_json_ntv:
                ntv_type = 'json'
            else:
                ntv_type = typ
                if not ntv_name:
                    ntv_name = name
        elif not is_json_ntv and NtvType(ntv_type) != NtvType(typ):
            raise NtvError('ntv_value is not compatible with ntv_type')
        return (ntv_value, ntv_name, ntv_type)
        
    def __eq__(self, other):
        ''' equal if name type and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_type == other.ntv_type and\
            self.ntv_value == other.ntv_value

    def __hash__(self):
        '''return hash(name) + hash(type) + hash(value)'''
        return hash(self.ntv_name) + hash(self.ntv_type) + \
            hash(json.dumps(self.ntv_value, cls=NtvJsonEncoder))

    def _obj_sep(self, json_type, def_type=None):
        ''' return separator to include in json_name'''
        if json_type or not def_type and \
            (isinstance(self.ntv_value, list) or
             isinstance(self.ntv_value, dict) and len(self.ntv_value) != 1):
            return ':'
        return ''

    @property
    def json_array(self):
        ''' return the json_array dynamic attribute'''
        return False

    def obj_value(self, def_type=None, **kwargs):
        '''return the ntv_value with different formats defined by kwargs'''
        option = {'encoded': False, 'format': 'json',
                  'simpleval': False} | kwargs
        if option['format'] in ('json', 'tuple'):
            return self.ntv_value
        if option['format'] == 'obj' and self.ntv_value == 'null':
            return None
        return NtvConnector.uncast(self, **option)


class NtvList(Ntv):
    '''An NTV-list entity is a Ntv entity where:

    - ntv_value is a list of NTV entities,
    - ntv_type is a default type available for included NTV entities

    *Attributes :*

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**:  value of the entity
    - **json_array**: Boolean - False if all the entity names are present and different
    (dynamic value)

    The methods defined in this class are :

    *Ntv constructor*
    - `obj`
    - `from_obj`
    - `from_att`

    *dynamic values (@property)*
    - `type_str`
    - `code_ntv`
    - `json_array`

    *instance methods*
    - `set_name`
    - `set_type`
    - `set_value`
    - `to_obj`
    - `to_repr`
    '''

    def __init__(self, list_ntv, ntv_name=None, ntv_type=None, fast=False):
        '''NtvList constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - default type or namespace of 
        the included entities
        - **list_ntv**: list - list of Ntv objects or obj_value of Ntv objects
        - **fast**: boolean (default False) - if True, Ntv is created with a list 
        of json values without control 
        '''
        if isinstance(list_ntv, NtvList):
            ntv_value = list_ntv.ntv_value
            ntv_type = list_ntv.ntv_type
            ntv_name = list_ntv.ntv_name
        elif fast and isinstance(list_ntv, list):
            ntv_value = [NtvSingle(val, ntv_type=ntv_type, fast=True)
                         for val in list_ntv]
        elif not fast and isinstance(list_ntv, list):
            ntv_value = [Ntv.from_obj(ntv, ntv_type, ':') for ntv in list_ntv]
        else:
            raise NtvError('ntv_value is not a list')
        if not ntv_type and len(ntv_value) > 0 and ntv_value[0].ntv_type:
            ntv_type = ntv_value[0].ntv_type
        super().__init__(ntv_value, ntv_name, ntv_type)
        for row, ntv in enumerate(self):
            ntv.parent = self
            ntv._row = row

    @property
    def json_array(self):
        ''' return the json_array dynamic attribute'''
        set_name = {ntv.ntv_name for ntv in self}
        return '' in set_name or len(set_name) != len(self)

    def __eq__(self, other):
        ''' equal if name and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_value == other.ntv_value

    def __hash__(self):
        '''return hash(name) + hash(value)'''
        return hash(self.ntv_name) + hash(tuple(self.ntv_value))

    def _obj_sep(self, json_type, def_type=None):
        ''' return separator to include in json_name'''
        if json_type or (len(self.ntv_value) == 1 and not self.json_array):
            return '::'
        return ''

    def obj_value(self, def_type=None, **kwargs):
        '''return the ntv_value with different formats defined by kwargs
        '''
        option = {'encoded': False, 'format': 'json',
                  'simpleval': False, 'json_array': False} | kwargs
        opt2 = option | {'encoded': False}
        if self.ntv_type:
            def_type = self.ntv_type.long_name
        if self.json_array or option['simpleval'] or option['json_array']:
            return [ntv.to_obj(def_type=def_type, **opt2) for ntv in self.ntv_value]
        values = [ntv.to_obj(def_type=def_type, **opt2) for ntv in self.ntv_value]
        return {list(val.items())[0][0]: list(val.items())[0][1] for val in values}


class NtvTree:
    ''' The NtvTree class is an iterator class used to traverse a NTV tree structure.
    Some other methods give tree indicators and data.

    *Attributes :*

    - **ntv** : Ntv entity
    - **_node**:  Ntv entity - node pointer

    *dynamic values (@property)*
    - `breadth`
    - `size`
    - `height`
    - `adjacency_list`
    - `nodes`
    - `leaf_nodes`
    - `inner_nodes`
    '''

    def __init__(self, ntv):
        ''' the parameter of the constructor is the Ntv entity'''
        self.ntv = ntv
        self._node = None

    def __iter__(self):
        ''' iterator without initialization'''
        return self

    def __next__(self):
        ''' return next node in the tree'''
        if not self._node:
            self._node = self.ntv
        elif isinstance(self._node.val, list):
            self._next_down()
        else:
            self._next_up()
        return self._node

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
        return max(len(node.address) for node in self.__class__(self.ntv)) - 1

    @property
    def adjacency_list(self):
        ''' return a dict with the list of child nodes for each parent node'''
        return {node: node.val for node in self.inner_nodes}

    @property
    def nodes(self):
        ''' return the list of nodes'''
        return list(self.__class__(self.ntv))

    @property
    def leaf_nodes(self):
        ''' return the list of leaf nodes'''
        return [node for node in self.__class__(self.ntv) if not isinstance(node.val, list)]

    @property
    def inner_nodes(self):
        ''' return the list of inner nodes'''
        return [node for node in self.__class__(self.ntv) if isinstance(node.val, list)]

    def _next_down(self):
        ''' find the next subchild node'''
        self._node = self._node[0]

    def _next_up(self):
        ''' find the next sibling or ancestor node'''
        parent = self._node.parent
        if not parent:
            raise StopIteration
        ind = parent.val.index(self._node)
        if ind < len(parent) - 1:  # if ind is not the last
            self._node = parent[ind + 1]
        else:
            if parent == self.ntv:
                raise StopIteration
            self._node = parent
            self._next_up()


class NtvConnector(ABC):
    ''' The NtvConnector class is an abstract class used by all NTV connectors
    for conversion between NTV data and an object.

    *class method :*
    - `connector`
    - `dic_connec`

    *abstract method*
    - `from_ntv`
    - `to_ntv`

    *static method*
    - `cast`
    - `uncast`
    - `obj_to_json`
    - `json_to_obj`
    '''

    @classmethod
    def connector(cls):
        '''return a dict with the connectors: { name: class }'''
        return {clas.__name__: clas for clas in cls.__subclasses__()}

    @classmethod
    def dic_connec(cls):
        '''return a dict with the clas associated to the connector:
        { clas_obj: classconnector }'''
        return {clas.clas_obj: clas.__name__ for clas in cls.__subclasses__()}

    @staticmethod
    @abstractmethod
    def from_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into the return object'''

    @abstractmethod
    def to_ntv(self):
        ''' convert object into the NTV entity (name, type, json-value)'''
            
    @staticmethod
    def cast(data):
        '''return (name, type, json_value) of the data'''
        dic_geo_cl = {'Point': 'point', 'MultiPoint': 'multipoint', 'LineString': 'line',
                      'MultiLineString': 'multiline', 'Polygon': 'polygon',
                      'MultiPolygon': 'multipolygon'}
        dic_connec = NtvConnector.dic_connec()
        clas = data.__class__.__name__
        match clas:
            case 'tuple':
                return (None, 'array', list(data))
            case 'date' | 'time' | 'datetime':
                return (None, clas, data.isoformat())
            case 'Point' | 'MultiPoint' | 'LineString' | 'MultiLineString' | \
                    'Polygon' | 'MultiPolygon':
                return (None, dic_geo_cl[data.__class__.__name__],
                        NtvConnector.connector()[dic_connec['geometry']].to_ntv(data)[2])
            case 'NtvSingle' | 'NtvSet' | 'NtvList':
                return (None, 'ntv', data.to_obj())
            case _:
                connec = None
                if clas in dic_connec and dic_connec[clas] in NtvConnector.connector():
                    connec = NtvConnector.connector()[dic_connec[clas]]
                if connec:
                    return connec.to_ntv(data)
                raise NtvError(
                    'connector is not defined for NTV entity of class : ', clas)
        return (None, None, None)

    @staticmethod
    def uncast(ntv, **option):
        '''return object from ntv entity'''
        dic_fct = {'date': datetime.date.fromisoformat, 'time': datetime.time.fromisoformat,
                   'datetime': datetime.datetime.fromisoformat, 'array': tuple}
        dic_geo = {'point': 'point', 'multipoint': 'multipoint', 'line': 'linestring',
                   'multiline': 'multilinestring', 'polygon': 'polygon',
                   'multipolygon': 'multipolygon'}
        dic_cbor = {'point': False, 'multipoint': False, 'line': False,
                    'multiline': False, 'polygon': False, 'multipolygon': False,
                    'date': True, 'time': False, 'datetime': True}
        dic_obj = {'tab': 'DataFrameConnec', 'field': 'SeriesConnec',
                   '$mermaid': 'MermaidConnec', '$cbor': 'CborConnec',
                   'point': 'ShapelyConnec', 'multipoint': 'ShapelyConnec',
                   'line': 'ShapelyConnec', 'multiline': 'ShapelyConnec',
                   'polygon': 'ShapelyConnec', 'multipolygon': 'ShapelyConnec',
                   'other': None}
        type_n = ntv.ntv_type.name
        if 'dicobj' in option:
            dic_obj |= option['dicobj']
        obj = not option['format'] == 'cbor' or \
            (ntv.ntv_type and type_n in dic_cbor and dic_cbor[type_n])
        if ntv.ntv_type is None or not obj:
            return ntv.ntv_value
        if type_n in dic_fct:
            if isinstance(ntv.ntv_value, (tuple, list)):
                return [dic_fct[type_n](val) for val in ntv.ntv_value]
            return dic_fct[type_n](ntv.ntv_value)
        if type_n == 'ntv':
            return Ntv.obj(ntv.ntv_value)
        if type_n in dic_geo:
            option['type_geo'] = dic_geo[type_n]
        connec = None
        if type_n in dic_obj and \
                dic_obj[type_n] in NtvConnector.connector():
            connec = NtvConnector.connector()[dic_obj[type_n]]
        elif dic_obj['other'] in NtvConnector.connector():
            connec = NtvConnector.connector()['other']
        if connec:
            return connec.from_ntv(ntv.ntv_value, **option)
        return ntv.ntv_value

    @staticmethod
    def obj_to_json(obj, complete=True):
        '''conversion from an object to json or NTV object.

        *Parameters*

        - **complete** : Boolean (default True) - if True, return a NTV object with a type,
        if False, return Json object without type
        '''
        if complete:
            return Ntv.obj(obj)
        return NtvConnector.cast(obj)[2]

    @staticmethod
    def json_to_obj(jsn, complete=True, class_name=None):
        '''conversion from a json or NTV object to an object.

        *Parameters*

        - **complete** : Boolean (default True) - if True, the type is included
        in the json or NTV object
        - **class_name** : string (default None) - class of the object to create'''
        ntv = Ntv.obj(jsn)
        ntv_type = ntv.type_str if complete else 'object'
        ntv.set_type(ntv_type)
        if class_name:
            connector = NtvConnector.dic_connec()[class_name]
            option = {'format': 'obj', 'dicobj': {ntv_type: connector}}
        else:
            option = {'format': 'obj'}
        return NtvConnector.uncast(ntv, **option)

class NtvJsonEncoder(json.JSONEncoder):
    """add a new json encoder for Ntv"""

    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        option = {'encoded': False, 'format': 'json'}
        try:
            return o.to_obj(**option)
        except:
            try:
                return o.__to_json__()
            except:
                return json.JSONEncoder.default(self, o)
            
class NtvError(Exception):
    ''' NTV Exception'''
    # pass
