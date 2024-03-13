# -*- coding: utf-8 -*-
"""
@author: Philippe@loco-labs.io

The `ntv` module is part of the `NTV.json_ntv` package ([specification document](
https://loco-philippe.github.io/ES/JSON%20semantic%20format%20(JSON-NTV).htm)).

It contains the classes `NtvSingle`, `NtvList`, `Ntv`(abstract) for NTV entities.

For more information, see the
[user guide](https://loco-philippe.github.io/NTV/documentation/user_guide.html)
or the [github repository](https://github.com/loco-philippe/NTV).

"""
import copy
from abc import ABC, abstractmethod
from numbers import Number
import json

from json_ntv.namespace import Datatype, Namespace, str_type, relative_type, agreg_type
from json_ntv.ntv_util import NtvError, NtvJsonEncoder, NtvConnector, NtvTree, NtvUtil
from json_ntv.ntv_patch import NtvPointer

NAME = 'N'
TYPE = 'T'
VALUE = 'V'
ENTITY = 'E'
NTVSINGLE = 'S'
NTVLIST = 'L'


class Ntv(ABC, NtvUtil):
    ''' The Ntv class is an abstract class used by `NtvSingle`and `NtvList` classes.

    *Attributes :*
    - **ntv_name** :  String - name of the NTV entity
    - **ntv_type**:   Datatype or Namespace - type of the entity
    - **ntv_value**:  value of the entity

    *Internal attributes :*
    - **parent**:     parent NtvList entity
    - **is_json**:    True if ntv_value is a json_value

    *dynamic values (@property)*
    - `code_ntv`
    - `json_name_str`
    - `json_array` (abstract method)
    - `max_len`
    - `name`
    - `tree`
    - `type_str`
    - `val`

    The methods defined in this class are :

    *Ntv constructor (staticmethod)*
    - `fast`
    - `obj`
    - `from_obj`
    - `from_att`

    *NTV conversion (instance methods)*
    - `alike`
    - `to_json_ntv`
    - `to_obj_ntv`
    - `validate` (validation)

    *export - conversion (instance methods)*
    - `expand`
    - `no_type`
    - `no_name`
    - `reduce`
    - `to_fast`
    - `to_name`
    - `to_obj`
    - `to_repr`
    - `to_mermaid`
    - `to_tuple`
    - `to_ntvsingle`
    - `to_ntvlist`

    *tree methods (instance methods)*
    - `childs`
    - `pointer`
    - `replace`
    - `remove`
    - `append` (NtvList only)
    - `insert` (NtvList only)

    *other instance methods*
    - `from_value`
    - `json_name`
    - `set_name`
    - `set_type`
    - `set_value`
    - `obj_value` (abstract method)

    *utility methods*
    - `decode_json` *(staticmethod)*
    - `obj_ntv` *(staticmethod)*
    '''

    def __init__(self, ntv_value, ntv_name, ntv_type):
        '''Ntv constructor.

        *Parameters*

        - **ntv_value**: Json entity - value of the entity
        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String or Datatype or Namespace (default None) - type of the entity
        '''
        if ntv_type.__class__.__name__ in ['Datatype', 'Namespace']:
            self.ntv_type = ntv_type
        elif ntv_type and ntv_type[-1] != '.':
            self.ntv_type = Datatype(ntv_type)
        elif ntv_type and ntv_type[-1] == '.':
            self.ntv_type = Namespace.add(ntv_type)
        else:
            self.ntv_type = None
        if not isinstance(ntv_name, str):
            ntv_name = ''
        self.ntv_name = ntv_name
        self.ntv_value = ntv_value
        self.is_json = NtvConnector.is_json(ntv_value)
        self.parent = None

    @staticmethod
    def fast(data, no_typ=False, typ_auto=False):
        ''' return an Ntv entity from data without conversion.

        *Parameters* : see `obj` method'''
        return Ntv.obj(data, no_typ=no_typ, typ_auto=typ_auto, fast=True)

    @staticmethod
    def obj(data, no_typ=False, decode_str=False, typ_auto=False, fast=False):
        ''' return an Ntv entity from data.

        *Parameters*

        - **Data** can be :
            - a tuple with value, name, typ and cat (see `from_att` method)
            - a value to decode (see `from_obj`method)
        - **no_typ** : boolean (default False) - if True, NtvList is with None type
        - **type_auto**: boolean (default False) - if True, default type for NtvList
        is the ntv_type of the first Ntv in the ntv_value
        - **fast** : boolean (default False) - if True, Ntv entity is created without conversion
        - **decode_str**: boolean (default False) - if True, string are loaded in json data'''
        #print('obj : ', Namespace.namespaces(), '\n')

        if isinstance(data, tuple):
            return Ntv.from_att(*data, decode_str=decode_str, fast=fast)
        # if isinstance(data, str) and data.lstrip() and data.lstrip()[0] in '{[':
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass
        return Ntv.from_obj(data, no_typ=no_typ, decode_str=decode_str,
                            typ_auto=typ_auto, fast=fast)

    @staticmethod
    def from_att(value, name, typ, cat, decode_str=False, fast=False):
        ''' return an Ntv entity.

        *Parameters*

        - **value**: Ntv entity or value to convert in an Ntv entity
        - **name** : string - name of the Ntv entity
        - **typ** : string or NtvType - type of the NTV entity
        - **cat**: string - NTV category ('single', 'list')
        - **fast** : boolean (default False) - if True, Ntv entity is created without conversion
        - **decode_str**: boolean (default False) - if True, string are loaded as json data'''

        value = Ntv._from_value(value, decode_str)
        if value.__class__.__name__ in ['NtvSingle', 'NtvList']:
            return value
        if isinstance(value, list) and cat == 'list':
            return NtvList(value, name, typ, fast=fast)
        if cat == 'single':
            return NtvSingle(value, name, typ, fast=fast)
        return Ntv.from_obj(value, def_type=typ, fast=fast)

    @staticmethod
    def from_obj(value, def_type=None, def_sep=None, no_typ=False, decode_str=False,
                 typ_auto=False, fast=False):
        ''' return an Ntv entity from an object value.

        *Parameters*

        - **value**: Ntv value to convert in an Ntv entity
        - **no_typ** : boolean (default None) - if True, NtvList is with None type
        - **def_type** : Datatype or Namespace (default None) - default type of the value
        - **def_sep**: ':', '::' or None (default None) - default separator of the value
        - **decode_str**: boolean (default False) - if True, string are loaded as json data
        - **type_auto**: boolean (default False) - if True, default type for NtvList
        is the ntv_type of the first Ntv in the ntv_value
        - **fast** : boolean (default False) - if True, Ntv entity is created without conversion'''
        value = Ntv._from_value(value, decode_str)
        if value.__class__.__name__ in ['NtvSingle', 'NtvList']:
            return value
        ntv_value, ntv_name, str_typ, sep, is_json = Ntv.decode_json(value)
        sep = def_sep if not sep else sep
        sep = None if str_typ and str_typ[-1] == '.' and sep == ':' else sep
        if isinstance(ntv_value, (list, dict)) and sep in (None, '::'):
            return Ntv._create_ntvlist(str_typ, def_type, sep, ntv_value,
                                       typ_auto, no_typ, ntv_name, fast)
        if sep == ':' or (sep is None and isinstance(ntv_value, dict)):
            ntv_type = agreg_type(str_typ, def_type, False)
            return NtvSingle(ntv_value, ntv_name, ntv_type, fast=fast)
        if sep is None and not isinstance(ntv_value, dict):
            #is_single_json = isinstance(value, (int, str, float, bool))
            is_single_json = isinstance(ntv_value, (int, str, float, bool))
            ntv_type = agreg_type(str_typ, def_type, is_single_json)
            return NtvSingle(ntv_value, ntv_name, ntv_type, fast=fast)
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
        # return json.dumps(self.to_repr(False, False, False, 10), cls=NtvJsonEncoder)
        return self.reduce(obj=False, level=3, maxi=6).to_obj(encoded=True)

    def __contains__(self, item):
        ''' item of Ntv entities'''
        if isinstance(self.val, list):
            return item in self.ntv_value
        return item == self.ntv_value

    def __iter__(self):
        ''' iterator for Ntv entities'''
        if isinstance(self, NtvSingle):
            # return iter([self.val])
            return iter([self])
        return iter(self.val)

    def __getitem__(self, selec):
        ''' return ntv_value item with selec:
            - String beginning with "#" : json-pointer,
            - string : name of the ntv,
            - list : recursive selector
            - tuple : list of name or index '''
        if selec is None or selec == '':
            return self
        if isinstance(selec, NtvPointer) or isinstance(selec, str) and selec[0] == '#':
            selec = self._pointer_to_list(selec)
        if selec in ([], ()):
            return self
        if isinstance(selec, (list, tuple)) and len(selec) == 1:
            selec = selec[0]
        if (selec == 0 or selec == self.ntv_name) and isinstance(self, NtvSingle):
            return self.ntv_value
        if isinstance(self, NtvSingle):
            raise NtvError('item not present')
        if isinstance(selec, tuple):
            return [self[i] for i in selec]
        if isinstance(selec, str):
            return self.ntv_value[self._string_to_ind(selec)]
        if isinstance(selec, list):
            return self[selec[0]][selec[1:]]
        return self.ntv_value[selec]

    def _pointer_to_list(self, pointer):
        '''return a list of child pointers from a string or a NtvPointer'''
        if isinstance(pointer, str):
            selec = list(NtvPointer(pointer[1:]))
        elif isinstance(pointer, NtvPointer):
            selec = list(pointer)
        else:
            raise NtvError('pointer is not a valid pointer')
        if not (selec[0] in [self.json_name(string=True), self.ntv_name]
                or (isinstance(selec[0], int) and selec[0] == 0)):
            raise NtvError(
                str(selec[0]) + 'is not the root json_name : ' + self.ntv_name)
        return selec[1:]

    def _string_to_ind(self, json_name):
        '''return the index of a name or a json_name'''
        if NtvUtil.from_obj_name(json_name)[1]:
            return [ntv.json_name(def_type=self.type_str, string=True)
                    for ntv in self.ntv_value].index(json_name)
        return [ntv.ntv_name for ntv in self.ntv_value].index(json_name)

    def __lt__(self, other):
        ''' return a comparison between two ntv_value'''
        # order: number > string > None
        res = Ntv.lower(self, other)
        if res is None:
            res = None if len(self) == len(other) else len(self) < len(other)
        res = self.to_obj(encoded=True) < other.to_obj(
            encoded=True) if res is None else res
        return res

    @property
    def code_ntv(self):
        '''return a string with the NTV code composed with 1 to 3 letters:
        - 'l' (NtvList), 's' (NtvSingle / json_value) or 'o' (NtvSingle / obj_value)
        - 'N' if ntv_name is present else none
        - 'T' if ntv_type is present else none'''
        dic = {'NtvList': 'l', 'NtvSingle': 's'}
        code = dic[self.__class__.__name__]
        if isinstance(self, NtvSingle) and not self.is_json:
            code = 'o'
        if self.ntv_name:
            code += 'N'
        if self.ntv_type and self.ntv_type.long_name != 'json':
            code += 'T'
        return code

    @property
    def json_name_str(self):
        '''return the JSON name of the NTV entity'''
        return self.json_name(def_type=self.parent.type_str, string=True)

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
    def tree(self):
        '''return a tree with included entities (NtvTree object)'''
        return NtvTree(self)

    @property
    def typebase_str(self):
        '''return a string with the value of the TypeBase of the entity'''
        if not self.ntv_type:
            return ''
        return self.ntv_type.typebase.long_name

    @property
    def type_str(self):
        '''return a string with the value of the NtvType of the entity'''
        if not self.ntv_type:
            return ''
        return self.ntv_type.long_name

    @property
    def val(self):
        '''return the ntv_value of the entity'''
        return self.ntv_value

    def alike(self, ntv_value):
        ''' return a Ntv entity with same name and type.

        *Parameters*

        - **ntv_value**: list of ntv values'''
        return self.__class__(ntv_value, self.ntv_name, self.ntv_type)

    def childs(self, obj=False, nam=False, typ=False):
        ''' return a list of child Ntv entities or child data

        *parameters*

        - **obj**: boolean (default False) - return json-value
        - **nam**: boolean (default False) - return name (with or without type)
        - **typ**: boolean (default False) - return type (with or without name)
        '''
        if isinstance(self, NtvSingle):
            return []
        if not (obj or nam or typ):
            return self.val
        if obj:
            return [ntv.to_obj() for ntv in self.val]
        return [(ntv.name if nam else '') + (' - ' if nam and typ else '') +
                (ntv.type_str if typ else '') for ntv in self.val]

    def expand(self, full=True, entity=True):
        '''return a json representation of the triplet (name, type, value)


        *Parameters*

        - **full**: Boolean (default True) - If False only members with non empty values are present
        - **entity**: Boolean (default True) - If True, member with entity name is added
        '''
        exp = {ENTITY: self.__class__.__name__} if entity else {}
        if isinstance(self, NtvList) and full:
            return exp | {NAME: self.name, TYPE: self.type_str,
                          VALUE: [ntv.expand(full) for ntv in self.val]}
        if isinstance(self, NtvSingle) and full:
            return exp | {NAME: self.name, TYPE: self.type_str, VALUE: self.val}
        exp |= {} if not self.name else {NAME: self.name}
        if not self.type_str in ['json', '']:
            exp[TYPE] = self.type_str
        if isinstance(self, NtvList):
            exp[VALUE] = [ntv.expand(full) for ntv in self.val]
        else:
            exp[VALUE] = self.val
        return exp

    def from_value(self):
        '''return a Ntv entity from ntv_value'''
        if isinstance(self.ntv_value, list):
            return NtvList(self.ntv_value)
        return Ntv.from_obj(self.ntv_value)

    def json_name(self, def_type=None, string=False, explicit=False):
        '''return the JSON name of the NTV entity (json-ntv format)

        *Parameters*

        - **def_typ** : Datatype or Namespace (default None) - type of the parent entity
        - **string** : boolean (default False) - If True, return a string else a tuple
        - **explicit** : boolean (default False) - If True, type is always included'''
        if def_type is None:
            def_type = ''
        elif isinstance(def_type, (Datatype, Namespace)):
            def_type = def_type.long_name
        json_name = self.ntv_name if self.ntv_name else ''
        json_type = relative_type(
            def_type, self.type_str) if self.ntv_type else ''
        implicit = isinstance(self, NtvSingle) and (json_type == 'json'
                                                    and (not def_type or def_type == 'json' or def_type[-1] == '.')
                                                    or not NtvConnector.is_json_class(self.val))
        if implicit and not explicit:
            json_type = ''
        json_sep = self._obj_sep(json_name, json_type, def_type)
        if string:
            return json_name + json_sep + json_type
        return [json_name, json_sep, json_type]

    @staticmethod
    def lower(val1, val2):
        ''' compare two ntv_value and return True if val1 < val2, False if val1 > val2 and
        None in the other cases'''
        res = None
        for v1, v2 in zip(Ntv.obj(val1).tree.leaf_nodes, Ntv.obj(val2).tree.leaf_nodes):
            if v1.val is None:
                res = True
            elif isinstance(v1.val, (dict, list)):
                res = Ntv.lower(v1.val, v2)
            elif isinstance(v2.val, (dict, list)):
                res = Ntv.lower(v1, v2.val)
            elif isinstance(v1.val, Number):
                if isinstance(v2.val, Number):
                    res = None if v1.val == v2.val else v1.val < v2.val
                else:
                    res = False
            elif isinstance(v1.val, str):
                if isinstance(v2.val, Number):
                    res = True
                elif isinstance(v2.val, str):
                    res = None if v1.val == v2.val else v1.val < v2.val
                else:
                    res = False
            if not res is None:
                break
        return res

    def no_type(self):
        '''convert NTV entity in a NV entity (in which ntv_type is 'json' or None')'''
        no_typ = copy.copy(self)
        for ntv in NtvTree(no_typ).leaf_nodes:
            ntv.set_type('json')
        for ntv in NtvTree(no_typ).inner_nodes:
            ntv.set_type()
        return no_typ

    def no_name(self):
        '''convert NTV entity in a TV entity (in which ntv_name is None)'''
        no_nam = copy.copy(self)
        for ntv in NtvTree(no_nam):
            ntv.ntv_name = None
        return no_nam

    def no_value(self):
        '''convert NTV entity in a NV entity (in which ntv_value of leaf nodes is ntv_type )'''
        no_val = copy.copy(self)
        for ntv in NtvTree(no_val).leaf_nodes:
            ntv.ntv_value = ntv.type_str
            ntv.set_type('json')
        return no_val

    def only_type(self):
        '''convert NTV entity in a V entity (in which ntv_value of leaf nodes
        is ntv_type )'''
        only_typ = copy.copy(self)
        for ntv in NtvTree(only_typ).leaf_nodes:
            ntv.ntv_value = ntv.type_str
            ntv.set_type('json')
            ntv.set_name()
        for ntv in NtvTree(only_typ).inner_nodes:
            ntv.set_name()
            ntv.set_type()
        return only_typ

    def only_name(self):
        '''convert NTV entity in a V entity (in which ntv_value of leaf nodes
        is ntv_name )'''
        only_nam = copy.copy(self)
        for ntv in NtvTree(only_nam).leaf_nodes:
            ntv.ntv_value = ntv.name
            ntv.set_type('json')
            ntv.set_name()
        for ntv in NtvTree(only_nam).inner_nodes:
            ntv.set_type()
        return only_nam

    def only_value(self):
        '''convert NTV entity in a V entity'''
        only_val = copy.copy(self)
        for ntv in NtvTree(only_val).leaf_nodes:
            ntv.set_type('json')
            ntv.set_name()
        for ntv in NtvTree(only_val).inner_nodes:
            ntv.set_type()
            ntv.set_name()
        return only_val

    @staticmethod
    def obj_ntv(value, name='', typ='', single=False):
        '''return a json-ntv representation without using Ntv structure.

        *Parameters*

        - **value** : ntv-value of the json-ntv
        - **name** : string (default '') - ntv-name of the json-ntv
        - **typ** : string (default '') - ntv_type of the json-ntv
        - **single** : boolean (default False) - if True, value is a single object
        else value is a set of objetcs.
        '''
        value = {} if not value else value
        name = '' if not name else name
        typ = '' if not typ else typ
        ntv_list = isinstance(value, (list, dict))
        if not single and not ntv_list:
            raise NtvError('value is not compatible with not single NTV data')
        sep = ':' if single else '::'
        sep = '' if not typ and (
            not single or single and not ntv_list) else sep
        name += sep + typ
        value = [value] if not name and isinstance(
            value, dict) and len(value) == 1 else value
        return {name: value} if name else value

    def pointer(self, index=False, item_idx=None):
        '''return a nested list of pointer from root

        *Parameters*

        - **index**: Boolean (default False) - use index instead of name
        - **item_idx**: Integer (default None) - index value for the pointer
        (useful with duplicate data)'''
        if not self.parent:
            root_pointer = 0 if index else self.json_name(string=True)
            return NtvPointer([root_pointer])
        idx = item_idx if item_idx else self.parent.ntv_value.index(self)
        num = index or self.parent.json_array
        pointer = self.parent.pointer(index)
        pointer.append(idx if num else self.json_name_str)
        return pointer

    def reduce(self, obj=True, maxi=6, level=3):
        '''reduce the length and the level of the entity

        *Parameters*

        - **obj**: boolean (default True) - If True return jsonNTV else NTV entity
        - **maxi**: integer (default 6) - Number of returned entities in an NtvList
        - **level**: integer (default 6) - returned entities in an NtvList at this level is None

        *return*

        - **NTV entity** or **jsonNTV**
        '''
        ntv = copy.copy(self)
        cont = Ntv.obj('___') if self.json_array else Ntv.obj({'___': ''})
        if isinstance(self, NtvSingle):
            return ntv
        if level == 0:
            ntv.ntv_value = [Ntv.obj('___', no_typ=True)]
        if len(self) <= maxi:
            ntv.ntv_value = [child.reduce(False, maxi, level-1)
                             for child in ntv]
            return ntv
        mid = maxi // 2
        cont.set_type(ntv.type_str)
        start = [child.reduce(False, maxi, level-1) for child in ntv[:mid]]
        middle = [cont]
        end = [child.reduce(False, maxi, level-1) for child in ntv[-mid:]]
        ntv.ntv_value = start + middle + end
        if obj:
            return ntv.to_obj()
        return ntv

    def remove(self, first=True, index=None):
        '''remove self from its parent entity.

        *parameters*

        - **first** : boolean (default True) - if True only the first instance
        else all
        - **index** : integer (default None) - index of self in its parent
        '''
        parent = self.parent
        if not parent:
            return
        idx = parent.ntv_value.index(self) if index is None else index
        if not parent[idx] == self:
            raise NtvError('the entity is not present at the index')
        del parent.ntv_value[idx]
        if not first and index is None:
            while self in parent:
                idx = parent.ntv_value.index(self)
                del parent.ntv_value[idx]
        if not self in parent:
            self.parent = None
        return

    def replace(self, ntv):
        '''replace self by ntv in the tree'''
        parent = self.parent
        if parent:
            idx = parent.ntv_value.index(self)
            parent.insert(idx, ntv)
            del parent[idx+1]
            if not self in parent:
                self.parent = None
        else:
            self = ntv

    def set_name(self, name='', nodes='simple'):
        '''set new names to the entity

        *Parameters*

        - **name**: list or string (default '') - New name values
        - **nodes**: string (default 'simple') - nodes to be changed
            'simple': current entity
            'leaves': NtvSingle entities
            'inner': NtvList entities
            'all': all entities  '''
        name = '' if name is None else name
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
        '''set a new type to the entity

        *Parameters*

        - **typ**: string, Datatype, Namespace (default None)'''
        if typ and not isinstance(typ, (str, Datatype, Namespace)):
            raise NtvError('the type is not a valid type')
        self.ntv_type = str_type(typ, self.__class__.__name__ == 'NtvSingle')

    def set_value(self, value=None, fast=False):
        '''set new ntv_value of a single entity or of a list of entities included

        *Parameters*

        - **value**: list or single value
        - **fast** : boolean (default False) - if True, value is not converted'''
        if isinstance(self, NtvSingle):
            self.ntv_value = NtvSingle(value, ntv_type=self.ntv_type,
                                       fast=fast).val
            return
        if not isinstance(value, list):
            value = [value] * NtvTree(self).breadth
        ntv_val = NtvList(value, fast=fast)
        for val, ntv in zip(ntv_val, NtvTree(self).leaf_nodes):
            ntv.ntv_value = val.val
        return

    def to_ntvsingle(self, name=None, typ=None, def_type=None, **kwargs):
        '''convert NtvList entity to NtvSingle entity

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **value**: value of the entity
        - **fast**: boolean (default False) - Ntv is created with a list of json values
        without control
        '''
        return NtvSingle(self.obj_value(def_type=def_type, **kwargs),
                         self.name if self.name else name,
                         self.type_str if self.type_str else typ)

    def to_ntvlist(self, def_type=None, def_sep=None, no_typ=False, decode_str=False,
                   typ_auto=False, fast=False):
        '''convert NtvSingle entity to NtvList entity

        *Parameters*

        - **value**: Ntv value to convert in an Ntv entity
        - **no_typ** : boolean (default None) - if True, NtvList is with 'json' type
        - **def_type** : Datatype or Namespace (default None) - default type of the value
        - **def_sep**: ':', '::' or None (default None) - default separator of the value
        - **decode_str**: boolean (default False) - if True, string are loaded as json data
        - **type_auto**: boolean (default False) - if True, default type for NtvList
        is the ntv_type of the first Ntv in the ntv_value
        - **fast** : boolean (default False) - if True, Ntv entity is created without conversion
        '''
        ntv = Ntv.from_obj(self.ntv_value, def_type, def_sep, no_typ, decode_str,
                           typ_auto, fast)
        if ntv.__class__.__name__ == 'NtvSingle':
            return NtvList([self])
        if self.ntv_name:
            ntv.set_name(self.ntv_name)
        return ntv

    def to_mermaid(self, title='', disp=False, row=False, leaves=False):
        '''return a mermaid flowchart.

        *Parameters*

        - **title**: String (default '') - title of the flowchart
        - **disp**: Boolean (default False) - if true, return a display else return
        a mermaid text diagram
        - **row**: Boolean (default False) - if True, add the node row
        - **leaves**: Boolean (default False) - if True, add the leaf row
        '''
        option = {'title': title, 'disp': disp, 'row': row, 'leaves': leaves}
        if disp:
            Ntv.obj({':$mermaid': self.to_obj()}).to_obj(
                format='obj', **option)
            return None
        return Ntv.obj({':$mermaid': self.to_obj()}).to_obj(format='obj', **option)

    def to_repr(self, nam=True, typ=True, val=True, jsn=False, maxi=10):
        '''return a simple json representation of the Ntv entity.

        *Parameters*

        - **nam**: Boolean(default True) - if true, the names are included
        - **typ**: Boolean(default True) - if true, the types are included
        - **val**: Boolean(default True) - if true, the values are included
        - **jsn**: Boolean(default False) - if false, the 'json' type is not included
        - **maxi**: Integer (default 10) - number of values to include for NtvList
        entities. If maxi < 1 all the values are included.
        '''
        ntv = self.code_ntv
        if nam and typ:
            ntv = ntv[0]
        if self.ntv_name and nam:
            ntv += '-' + self.ntv_name
        if self.ntv_type and typ and (jsn or self.ntv_type.long_name != 'json'):
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
            return {ntv:  self.ntv_value.to_repr(nam, typ, val, jsn, maxi)}
        if clas == 'NtvList':
            maxv = len(self.ntv_value) if maxi < 1 else maxi
            return {ntv:  [ntvi.to_repr(nam, typ, val, jsn, maxi)
                           for ntvi in self.ntv_value[:maxv]]}
        raise NtvError('the ntv entity is not consistent')

    def to_name(self, default=''):
        '''return the name of the NTV entity

        *Parameters*

        - **default**: string (default ''): returned value if name is not present '''
        if self.ntv_name == '':
            return default
        return self.ntv_name

    def to_fast(self, def_type=None, **kwargs):
        '''return the JSON representation of the NTV entity (json-ntv format)
        without value conversion.

        *Parameters*

        - **def_type** : Datatype or Namespace (default None) - default type to apply
        to the NTV entity
        - **encoded** : boolean (default False) - choice for return format
        (string/bytes if True, dict/list/tuple else)
        - **format**  : string (default 'json')- choice for return format
        (json, cbor, obj)
        - **simpleval** : boolean (default False) - if True, only value (without
        name and type) is included
        - **name** : boolean (default true) - if False, name is not included
        - **json_array** : boolean (default false) - if True, Json-object is not used for NtvList
        - **maxi**: Integer (default -1) - number of values to include for NtvList
        entities. If maxi < 1 all the values are included.
        '''
        option = kwargs | {'fast': True}
        return self.to_obj(def_type=def_type, **option)

    def to_obj(self, def_type=None, **kwargs):
        '''return the JSON representation of the NTV entity (json-ntv format).

        *Parameters*

        - **def_type** : Datatype or Namespace (default None) - default type to apply
        to the NTV entity
        - **encoded** : boolean (default False) - choice for return format
        (string/bytes if True, dict/list/tuple else)
        - **format**  : string (default 'json')- choice for return format
        (json, cbor, obj)
        - **simpleval** : boolean (default False) - if True, only value (without
        name and type) is included
        - **name** : boolean (default true) - if False, name is not included
        - **type** : boolean (default False) - if True, type is always included
        - **json_array** : boolean (default false) - if True, Json-object is not used for NtvList
        - **fast** : boolean (default False) - if True, json is created without conversion
        - **maxi**: Integer (default -1) - number of values to include for NtvList
        entities. If maxi < 1 all the values are included.
        '''
        option = {'encoded': False, 'format': 'json', 'fast': False, 'maxi': -1,
                  'simpleval': False, 'name': True, 'json_array': False, 
                  'type': False} | kwargs
        value = self.obj_value(def_type=def_type, **option)
        obj_name = self.json_name(def_type)
        if not option['name']:
            obj_name[0] = ''
        if option['simpleval']:
            name = ''
        elif (option['format'] in ('cbor', 'obj') and 
              not NtvConnector.is_json_class(value) and not option['type']):
            name = obj_name[0]
        else:
            name = obj_name[0] + obj_name[1] + obj_name[2]
        value = [value] if not name and isinstance(
            value, dict) and len(value) == 1 else value
        json_obj = {name: value} if name else value
        if option['encoded'] and option['format'] == 'json':
            return json.dumps(json_obj, cls=NtvJsonEncoder)
        if option['encoded'] and option['format'] == 'cbor':
            return NtvConnector.connector()['CborConnec'].to_obj_ntv(json_obj)
        return json_obj

    def to_json_ntv(self):
        ''' create a copy where ntv-value of the self-tree nodes is converted
        in json-value'''
        ntv = copy.copy(self)
        for leaf in ntv.tree.leaf_nodes:
            if isinstance(leaf.ntv_value, (NtvSingle, NtvList)):
                leaf.ntv_value = leaf.ntv_value.to_obj()
                leaf.ntv_type = Datatype('ntv')
            elif not leaf.is_json:
                leaf.ntv_value, leaf.ntv_name, type_str = NtvConnector.cast(
                    leaf.ntv_value, leaf.ntv_name, leaf.type_str)
                leaf.ntv_type = Datatype(type_str)
                leaf.is_json = True
        return ntv

    def to_obj_ntv(self, **kwargs):
        ''' create a copy where ntv-value of the self-tree nodes is converted
        in object-value

        *Parameters*

        - **kwargs** : parameters used in NtvConnector class (specific for each Connector)'''
        ntv = copy.copy(self)
        for leaf in ntv.tree.leaf_nodes:
            if (leaf.is_json and leaf.type_str in set(NtvConnector.dic_type.values())
                    or leaf.ntv_type is None):
                leaf.ntv_value, leaf.ntv_name, type_str = NtvConnector.uncast(
                    leaf, **kwargs)
                leaf.ntv_type = Datatype(type_str) if type_str else None
                leaf.is_json = NtvConnector.is_json(leaf.ntv_value)
        return ntv

    def to_tuple(self, maxi=10):
        '''return a nested tuple representation of the NTV entity
        (NtvList/NtvSingle, ntv_name, ntv_type, ntv_value).

        *Parameters*

        - **maxi**: Integer (default 10) - number of values to include for NtvList
        entities. If maxi < 1 all the values are included.
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
            maxv = len(self.ntv_value) if maxi < 1 else maxi
            return (clas, name, typ, [ntv.to_tuple(maxi=maxi) for ntv in val[:maxv]])
        raise NtvError('the ntv entity is not consistent')

    def validate(self, unique=False):
        '''check the ntv_type validity and return a boolean and a list of errors

        *Parameters*

        - **unique**: boolean (default False) - if True, stop validation at the
        first error'''
        errors = []
        for ntv in self.tree.leaf_nodes:
            valid = ntv.ntv_type.validate(ntv.ntv_value)
            if not valid:
                errors.append(str(ntv.pointer()))
                if unique:
                    return (False, errors)
        return (not errors, errors)

    @abstractmethod
    def obj_value(self):
        '''return the ntv_value with different formats defined by kwargs (abstract method)'''

    @property
    @abstractmethod
    def json_array(self):
        ''' return the json_array dynamic attribute (abstract method)'''

    @abstractmethod
    def _obj_sep(self, json_type, def_type):
        ''' return separator to include in json_name (abstract method)'''

    @staticmethod
    def _from_value(value, decode_str=False):
        '''return a decoded value

        *Parameters*

        - **decode_str**: boolean (default False) - if True, string are loaded as json data
        '''
        if isinstance(value, bytes):
            value = Ntv.from_obj({'$cbor': value}).ntv_value
        elif decode_str and isinstance(value, str) and value.lstrip() and\
                value.lstrip()[0] in '"-{[0123456789tfn':
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        return value

    @staticmethod
    def decode_json(json_value):
        '''return (value, name, type, separator, isjson) of a json object'''
        if isinstance(json_value, dict) and len(json_value) == 1:
            json_name = list(json_value.keys())[0]
            val = json_value[json_name]
            return (val, *NtvUtil.from_obj_name(json_name), NtvConnector.is_json(val))
        return (json_value, None, None, None, NtvConnector.is_json(json_value))

    @staticmethod
    def _create_ntvlist(str_typ, def_type, sep, ntv_value, typ_auto, no_typ, ntv_name, fast):
        '''return a NtvList with parameters from Ntv.from_obj method'''
        def_type = agreg_type(str_typ, def_type, False)
        sep_val = ':' if sep and def_type else None
        if isinstance(ntv_value, dict):
            keys = list(ntv_value.keys())
            values = list(ntv_value.values())
            ntv_list = [Ntv.from_obj({key: val}, def_type, sep_val, fast=fast)
                        for key, val in zip(keys, values)]
        else:
            ntv_list = [Ntv.from_obj(val, def_type, sep_val, fast=fast)
                        for val in ntv_value]
        if typ_auto and not def_type and ntv_list:
            def_type = ntv_list[0].ntv_type
        def_type = None if no_typ else def_type
        return NtvList(ntv_list, ntv_name, def_type, typ_auto, fast=fast)

    @staticmethod
    def _listed(idx):
        '''transform a tuple of tuple object in a list of list object'''
        return [val if not isinstance(val, tuple) else Ntv._listed(val) for val in idx]


class NtvSingle(Ntv):
    ''' A NTV-single entity is a Ntv entity not composed with other entities.

    *Attributes :*
    - no additional attributes to those of parent class `Ntv`

    *dynamic values (@property)*
    - `json_array`

    The additional methods defined in this class are :

    *instance methods*
    - `obj_value`
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
            value, ntv_name, ntv_type = NtvSingle._decode_s(
                value, ntv_name, ntv_type)
            if ntv_type and isinstance(ntv_type, str) and ntv_type[-1] == '.':
                raise NtvError('the ntv_type is not valid')
        super().__init__(value, ntv_name, ntv_type)

    def __eq__(self, other):
        ''' equal if name type and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_type == other.ntv_type and\
            self.ntv_value == other.ntv_value

    def __hash__(self):
        '''return hash(name) + hash(type) + hash(value)'''
        return hash(self.ntv_name) + hash(self.ntv_type) + \
            hash(json.dumps(self.ntv_value, cls=NtvJsonEncoder))

    def __copy__(self):
        ''' Copy all the Ntv tree '''
        return self.__class__(copy.copy(self.ntv_value), self.ntv_name,
                              self.ntv_type, fast=True)

    @property
    def json_array(self):
        ''' return the json_array dynamic attribute (always False)'''
        return False

    def obj_value(self, def_type=None, **kwargs):
        '''return the ntv_value with different formats defined by kwargs'''
        option = {'encoded': False, 'format': 'json',
                  'simpleval': False, 'fast': False} | kwargs
        if option['fast'] or option['format'] in ('json', 'tuple'):
            return self.ntv_value
        if option['format'] == 'obj' and self.ntv_value == 'null':
            return None
        return NtvConnector.uncast(self, **option)[0]

    def _obj_sep(self, json_name, json_type, def_type=None):  # REQ5
        ''' return separator to include in json_name'''
        if json_type or not def_type and isinstance(self.ntv_value, (list, dict)):
            return ':'
        return ''

    @staticmethod
    def _decode_s(ntv_value, ntv_name, ntv_type_str):
        '''return adjusted ntv_value, ntv_name, ntv_type(str)'''
        is_json = NtvConnector.is_json(ntv_value)
        name = None
        if is_json:
            if isinstance(ntv_value, (list)):
                ntv_value = [NtvSingle._decode_s(val, '', ntv_type_str)[
                    0] for val in ntv_value]
            elif isinstance(ntv_value, (dict)):
                ntv_value = {key: NtvSingle._decode_s(val, '', ntv_type_str)[
                    0] for key, val in ntv_value.items()}
        elif isinstance(ntv_value, NtvSingle):
            ntv_value = ntv_value.to_obj()
            return (ntv_value, ntv_name, 'ntv')
        else:
            ntv_value, name, typ_str = NtvConnector.cast(ntv_value, ntv_name)
            ntv_type_str = Datatype(typ_str).name if typ_str else ntv_type_str
        if not ntv_type_str:
            if is_json:
                ntv_type_str = 'json'
            else:
                ntv_type_str = typ_str
        elif not is_json and ntv_type_str != typ_str:
            raise NtvError('ntv_value is not compatible with ntv_type')
        ntv_name = name if not ntv_name else ntv_name                
        '''
        if not ntv_type_str:
            if is_json:
                ntv_type_str = 'json'
            else:
                ntv_type_str = typ_str
            if not ntv_name:
                ntv_name = name
        elif not is_json and ntv_type_str != typ_str:
            raise NtvError('ntv_value is not compatible with ntv_type')'''
        return (ntv_value, ntv_name, ntv_type_str)


class NtvList(Ntv):
    '''A NTV-list entity is a Ntv entity where:

    - ntv_value is a list of NTV entities,
    - ntv_type is a default type available for included NTV entities

    *Attributes :*
    - no additional attributes to those of parent class `Ntv`

    *dynamic values (@property)*
    - `json_array`

    The additional methods defined in this class are :

    *instance methods*
    - `obj_value`
    '''

    def __init__(self, list_ntv, ntv_name=None, ntv_type=None, typ_auto=False, fast=False):
        '''NtvList constructor.

        *Parameters*

        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - default type or namespace of
        the included entities
        - **list_ntv**: list - list of Ntv objects or obj_value of Ntv objects
        - **fast**: boolean (default False) - if True, Ntv is created with a list
        of json values without control
        - **type_auto**: boolean (default False) - if True, default type for NtvList
        is the ntv_type of the first Ntv in the ntv_value'''
        if isinstance(list_ntv, NtvList):
            ntv_value = [copy.copy(ntv) for ntv in list_ntv.ntv_value]
            ntv_type = list_ntv.ntv_type
            ntv_name = list_ntv.ntv_name
        elif isinstance(list_ntv, list):
            ntv_value = [Ntv.from_obj(ntv, ntv_type, ':', fast=fast)
                         for ntv in list_ntv]
        elif isinstance(list_ntv, dict):
            ntv_value = [Ntv.from_obj({key: val}, ntv_type, ':', fast=fast)
                         for key, val in list_ntv.items()]
        else:
            raise NtvError('ntv_value is not a list')
        if typ_auto and not ntv_type and len(ntv_value) > 0 and ntv_value[0].ntv_type:
            ntv_type = ntv_value[0].ntv_type
        super().__init__(ntv_value, ntv_name, ntv_type)
        for ntv in self:
            ntv.parent = self

    @property
    def json_array(self):
        ''' return the json_array dynamic attribute'''
        set_name = {ntv.json_name(
            def_type=self.type_str, string=True) for ntv in self}
        return '' in set_name or len(set_name) != len(self)

    def __eq__(self, other):
        ''' equal if name and value are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ntv_name == other.ntv_name and self.ntv_value == other.ntv_value

    def __hash__(self):
        '''return hash(name) + hash(value)'''
        return hash(self.ntv_name) + hash(tuple(self.ntv_value))

    def __copy__(self):
        ''' Copy all the data '''
        cop = self.__class__(self)
        cop.parent = None
        return cop

    def __setitem__(self, ind, value):
        ''' replace ntv_value item at the `ind` row with `value`'''
        if ind < 0 or ind >= len(self):
            raise NtvError("out of bounds")
        self.ntv_value[ind] = value
        if isinstance(value, (NtvSingle, NtvList)):
            value.parent = self

    def __delitem__(self, ind):
        '''remove ntv_value item at the `ind` row'''
        if isinstance(ind, int):
            self.ntv_value.pop(ind)
        else:
            self.ntv_value.pop(self.ntv_value.index(self[ind]))

    def append(self, ntv):
        ''' add ntv at the end of the list of Ntv entities included'''
        old_parent = ntv.parent
        if old_parent:
            del(old_parent[old_parent.ntv_value.index(ntv)])
        self.ntv_value.append(ntv)
        ntv.parent = self

    def insert(self, idx, ntv):
        ''' add ntv at the index idx of the list of Ntv entities included'''
        old_parent = ntv.parent
        if old_parent:
            del(old_parent[old_parent.ntv_value.index(ntv)])
        self.ntv_value.insert(idx, ntv)
        ntv.parent = self

    def _obj_sep(self, json_name, json_type, def_type=None):
        ''' return separator to include in json_name'''
        sep = ':' if (json_type and json_type[-1] == '.') else '::'
        return sep if (json_type and json_type[-1] != '.') or (json_type and json_name) else ''

    def obj_value(self, def_type=None, **kwargs):
        '''return the ntv_value with different formats defined by kwargs
        '''
        option = {'encoded': False, 'format': 'json', 'simpleval': False,
                  'json_array': False, 'fast': False, 'maxi': -1} | kwargs
        opt2 = option | {'encoded': False}
        maxv = len(self.ntv_value) if option['maxi'] < 1 else option['maxi']
        def_type = self.ntv_type.long_name if self.ntv_type else def_type
        values = [ntv.to_obj(def_type=def_type, **opt2)
                  for ntv in self.ntv_value[:maxv]]
        if len(self) == 1 and isinstance(self[0], NtvSingle) and isinstance(values[0], dict):
            return values[0]
        if not NtvUtil.is_dictable(values) or option['simpleval'] or option['json_array']:
            return values
        return {list(val.items())[0][0]: list(val.items())[0][1] for val in values}
