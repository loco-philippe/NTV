# -*- coding: utf-8 -*-
"""
Created on Sept 10 2023

@author: Philippe@loco-labs.io

The `ntv_patch` module is part of the `NTV.json_ntv` package ([specification document](
https://loco-philippe.github.io/ES/JSON%20semantic%20format%20(JSON-NTV).htm)).

It contains the classes `NtvOp`, `NtvPatch`.

# 1 - NTV Patch

NTV Patch is a transposition of JSON Patch defined in RFC6902.

NTV Patch is a format for expressing a sequence of operations to be applied to a
target NTV entity.

This format is also potentially useful in cases where it is necessary to
make partial updates on an NTV entity.

The representation of an NTV Patch is a JSON-Array that can be added to an NTV
entity (e.g. comments and change management).

# 2 - Example

```
    [
     {'op': 'add',    'path': '/0/liste/0', 'entity': {'new value': 51}}
     {'op': 'test',   'path': '/0/1/-',     'entity': {'new value': 51}}
     {'op': 'remove', 'path': '/0/1/-'}
     ]
```
"""
import json
from copy import copy

OPERATIONS = ['add', 'test', 'move', 'remove', 'copy', 'replace']


class NtvOp:
    ''' The NtvOp class defines operations to apply to an NTV entity

    *Attributes :*

    - **op** : string - type of operation to apply
    - **entity**: Ntv - entity subject to the operation
    - **comment**: string - description of the operation
    - **path**: string - NtvPointer to the child entity concerned by the op
    - **from_path**: string - NtvPointer to the origin path (copy and move)

    *dynamic values (@property)*
    - `json`

    *instance method*
    - `exe`
    '''

    def __init__(self, ope, path=None, entity=None, comment=None, from_path=None):
        '''constructor

        *Parameters*

        - **ope**: str or dict - operation (str) or set of attributes (dict)
        - **path**: str (default None) - Json of NtvPointer to the child entity
        concerned by the ope
        - **entity**: Json-value (default None) - NTV entity
        - **comment** str (default None) - comment about ope
        - **from_path**: str (default None) - Json of NtvPointer to the origin
        path (copy and move)
        '''
        ope = ope.json if isinstance(ope, NtvOp) else ope
        if isinstance(ope, str):
            self.ope = None
            self.entity = None
            self.comment = ope
            self.from_path = []
            self.path = []
            return
        dic = isinstance(ope, dict)
        self.ope = ope.get('op') if dic else ope
        self.entity = ope.get('entity') if dic else entity
        self.comment = ope.get('comment') if dic else comment
        self.from_path = NtvPointer(
            ope.get('from')) if dic else NtvPointer(from_path)
        self.path = NtvPointer(ope.get('path')) if dic else NtvPointer(path)
        if self.ope and (not self.path or not self.ope in OPERATIONS):
            raise NtvOpError('path or op is not correct')

    def __repr__(self):
        '''return the op and the path'''
        txt = ''
        if self.ope:
            txt += 'op : ' + (self.ope + ',').ljust(8, ' ')
        if self.path:
            txt += ' path : ' + str(self.path)
        if self.comment:
            txt += self.comment
        return txt
        # return 'op : ' + (self.ope + ',').ljust(8, ' ') + ' path : ' + str(self.path)

    def __str__(self):
        '''return json format'''
        return json.dumps(self.json)

    def __eq__(self, other):
        ''' equal if all attributes are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.ope == other.ope and self.path == other.path and\
            self.entity == other.entity and self.comment == other.comment and\
            self.from_path == other.from_path

    def __copy__(self):
        ''' Copy all the data '''
        cop = self.__class__(self)
        return cop

    @property
    def json(self):
        '''return the json-value representation (dict)'''
        dic = {'op': self.ope, 'path': str(self.path), 'entity': self.entity,
               'comment': self.comment, 'from': str(self.from_path)}
        return {key: val for key, val in dic.items() if val and val != 'None'}

    def exe(self, ntv):
        '''applies the operation to the 'ntv' entity and return the resulting entity'''
        from json_ntv.ntv import Ntv
        ntv_res = copy(ntv)
        idx = self.path[-1]
        p_path = str(NtvPointer(self.path[:-1]))
        path = str(self.path)
        if self.ope in ['move', 'copy', 'add']:
            if self.ope == 'add' and self.entity:
                ntv = Ntv.obj(self.entity)
            elif self.ope == 'copy' and self.from_path:
                ntv = copy(ntv_res[str(self.from_path)])
            elif self.ope == 'move' and self.from_path:
                ntv = ntv_res[str(self.from_path)]
                del ntv_res[str(NtvPointer(self.from_path[:-1]))
                            ][self.from_path[-1]]
                ntv.parent = None
            else:
                raise NtvOpError('op is not correct')
            if idx == '-':
                ntv_res[p_path].append(ntv)
            else:
                ntv_res[p_path].insert(idx, ntv)
        elif self.ope == 'test' and self.entity:
            ntv = Ntv.obj(self.entity)
            if not (idx == '-' and ntv in ntv_res[p_path]) and not (
                    isinstance(idx, int) and ntv == ntv_res[path]):
                raise NtvOpError('test is not correct')
        elif self.ope == 'remove':
            idx = self.path[-1]
            idx = len(ntv[p_path]) - 1 if idx == '-' else idx
            ntv_res[p_path+'/'+str(idx)].remove(index=idx)
        elif self.ope == 'replace' and self.entity:
            ntv_res[path].replace(Ntv.obj(self.entity))
        else:
            raise NtvOpError('op add no result')
        return ntv_res


class NtvPatch:
    ''' The NtvPatch class defines a sequence of operations to apply to an
    NTV entity


    *Attributes :*

    - **list_op** : list - list of NtvOp to apply
    - **comment**: string - description of the patch

    *dynamic values (@property)*
    - `json`

    *instance method*
    - `append`
    - `exe`
    '''

    def __init__(self, list_op, comment=None):
        '''constructor

        *Parameters*

        - **list_op**: list, dict, str, NtvOp, NtvPatch - list of operations
            - list - list of op
            - dict - json representation of a NtvPatch
            - str - comment without op
            - NtvOp - if only one op
            - NtvPatch - copy of an existing NtvPatch
        - **comment**: str (default None) - comment if not included in the list_op
        '''
        if isinstance(list_op, NtvPatch):
            self.list_op = list_op.list_op
            self.comment = list_op.comment
            return
        if isinstance(list_op, NtvOp):
            self.comment = list_op.comment
            self.list_op = [copy(list_op)]
            self.list_op[0].comment = None
            return
        if isinstance(list_op, str):
            self.comment = list_op
            self.list_op = []
            return
        if isinstance(list_op, dict):
            self.comment = list_op.get('comment', None)
            lis = list_op.get('list-op', [])
            self.list_op = [NtvOp(ope) for ope in lis]
            return
        list_op = [] if not list_op else list_op
        self.list_op = [NtvOp(ope) for ope in list_op]
        self.comment = comment
        return

    def __eq__(self, other):
        ''' equal if list_op are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.list_op == other.list_op and self.comment == other.comment

    def __copy__(self):
        ''' Copy all the data '''
        cop = self.__class__(self)
        return cop

    def __setitem__(self, ind, ope):
        ''' replace op item in list_op at the `ind` row with `ope`'''
        if ind < 0 or ind >= len(self):
            raise NtvOpError("out of bounds")
        self.list_op[ind] = ope

    def __delitem__(self, ind):
        '''remove op item at the `ind` row'''
        if isinstance(ind, int):
            self.list_op.pop(ind)
        else:
            self.list_op.pop(self.list_op.index(self[ind]))

    def __len__(self):
        ''' len of list_op'''
        return len(self.list_op)

    def __str__(self):
        '''return comment and list of op in json-text format'''
        return json.dumps(self.json)

    def __repr__(self):
        '''return classname, comment and list of op'''
        rep = 'NtvPatch :' + (self.comment if self.comment else '')
        for ind, ope in enumerate(self):
            rep += '\n    op' + str(ind).ljust(3, ' ') + ' : ' + repr(ope)[5:]
        return rep

    def __contains__(self, item):
        ''' return item is in the list of op'''
        return item in self.list_op

    def __iter__(self):
        ''' iterator for list of op'''
        return iter(self.list_op)

    def __getitem__(self, selec):
        ''' return op item in list of op'''
        if selec is None or selec == [] or selec == () or selec == '':
            return self
        if isinstance(selec, (list, tuple)) and len(selec) == 1:
            selec = selec[0]
        if isinstance(selec, (list, tuple)):
            return [self[i] for i in selec]
        return self.list_op[selec]

    def append(self, ope):
        '''append 'ope' in the list of op'''
        self.list_op.append(ope)

    @property
    def json(self):
        '''return list of op in json-value format'''
        return {'comment': self.comment,
                'list-op': [ope.json for ope in self.list_op]}

    def exe(self, ntv):
        '''apply the included operations to NTV entity (ntv) and return
        the resulting NTV entity'''
        ntv_res = ntv
        for ope in self:
            ntv_res = ope.exe(ntv_res)
        return ntv_res


class NtvPointer(list):
    ''' The NtvPointer class defines methods to identify a node in a NTV entity

    NtvPointer is child class of `list` class

    *dynamic values (@property)*
    - `split`
    - `pointer_json`
    - `pointer_list`

    *instance method*
    - `json`
    - `append`
    '''

    def __init__(self, pointer):
        '''constructor

        *Parameters*

        - **pointer**: path from the root to the node
            - list: list of int or str that identify a node
            - NtvPointer: existing path to copy
            - int: single level
            - str: json_pointer
        '''
        if isinstance(pointer, (list, NtvPointer)):
            super().__init__(pointer)
        elif isinstance(pointer, (int, str)):
            super().__init__(NtvPointer.pointer_list(pointer))

    def __str__(self):
        '''json-text representation of the NtvPointer'''
        return self.json()

    def json(self, default=''):
        '''convert a NtvPointer into a json_pointer

        *Parameters*

        - **default**: Str (default '') - default value if pointer is empty
        '''
        return NtvPointer.pointer_json(self, default=default)

    def append(self, child):
        '''append a child pointer into a pointer '''
        self += NtvPointer(child)

    @staticmethod
    def split(path):
        '''return a tuple with the last pointer of the path
        and the path without the last pointer'''
        pointer = NtvPointer(path)
        if not pointer:
            return (None, None)
        return (NtvPointer(pointer[-1]), NtvPointer(pointer[:-1]))

    @staticmethod
    def pointer_json(list_pointer, default=''):
        '''convert a list of pointer into a json_pointer

        *Parameters*

        - **default**: Str (default '') - default value if pointer is empty
        '''
        json_p = ''
        if list_pointer == []:
            return default
        for name in list_pointer:
            json_p += '/' + str(name).replace('~', '~0').replace('/', '~1')
        return json_p

    @staticmethod
    def pointer_list(json_pointer):
        '''convert a json_pointer string into a pointer list'''
        json_pointer = str(json_pointer)
        split_pointer = json_pointer.split('/')
        if len(split_pointer) == 0:
            return []
        if split_pointer[0] != '' and len(split_pointer) > 1:
            raise NtvOpError("json_pointer is not correct")
        if split_pointer[0] != '':
            split_pointer.insert(0, '')
        return [int(nam) if nam.isdigit() else nam.replace('~1', '/').replace('~0', '/')
                for nam in split_pointer[1:]]


class NtvOpError(Exception):
    ''' NtvOp Exception'''
    # pass
