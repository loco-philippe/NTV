# -*- coding: utf-8 -*-
"""
Created on Sept 10 2023

@author: Philippe@loco-labs.io

The `ntv_patch` module is part of the `NTV.json_ntv` package ([specification document](
https://loco-philippe.github.io/ES/JSON%20semantic%20format%20(JSON-NTV).htm)).

It contains the classes `NtvOperation`, `NtvPatch`.

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
from json_ntv.ntv import Ntv
from copy import copy

OPERATIONS = ['add', 'test', 'move', 'remove', 'copy', 'replace']

class NtvOp:
    ''' The NtvOp class defines operations to apply to an NTV entity'''
    
    def __init__(self, op, path=None, entity=None, comment=None, from_path=None):
        op = op.json if isinstance(op, NtvOp) else op
        dic = isinstance(op, dict)
        self.op         = op.get('op')         if dic else op
        self.path       = op.get('path')       if dic else path
        self.entity     = op.get('entity')     if dic else entity
        self.comment    = op.get('comment')    if dic else comment
        self.from_path  = op.get('from')       if dic else from_path
        self.ntv = Ntv.obj(self.entity) if self.entity else None
        if not self.path or not self.op in OPERATIONS:
            raise NtvOpError('path or op is not correct')
        
    def __repr__(self):
        '''return the op and the path'''
        return 'op : ' + (self.op + ',').ljust(8, ' ') + ' path : ' + self.path

    def __str__(self):
        '''return json format'''
        return json.dumps(self.json)
    
    def __eq__(self, other):
        ''' equal if op, path, entity, comment and from_path are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.op == other.op and self.path == other.path and\
            self.entity == other.entity and self.comment == other.comment and\
            self.from_path == other.from_path

    @property
    def json(self):
        '''return the json-value representation (dict)'''
        dic = {'op': self.op, 'path': self.path, 'entity': self.entity, 
               'comment':self.comment, 'from': self.from_path}
        return {key: val for key, val in dic.items() if val}

    @staticmethod 
    def pointer_index(path):
        '''return the last pointer of the path and the path without the last pointer'''
        pointer = Ntv.pointer_list(path)
        if pointer == []:
            return (None, None)
        return (pointer[-1], Ntv.pointer_json(pointer[:-1]))

    def exe(self, ntv):
        '''execute the operation with ntv entity and return the resulting entity'''
        ntv_res = copy(ntv)
        idx, p_path = NtvOp.pointer_index(self.path)
        if self.op in ['move', 'copy', 'add']:
            if self.op == 'add' and self.entity:
                ntv = self.ntv
            elif self.op == 'copy' and self.from_path:
                ntv = copy(ntv_res[self.from_path])                
            elif self.op == 'move' and self.from_path:
                ntv = ntv_res[self.from_path]
                from_idx, from_p_path = NtvOp.pointer_index(self.from_path)
                del ntv_res[from_p_path][from_idx]
                ntv.parent = None
            else:
                raise NtvOpError('op is not correct')
            if idx == '-':
                ntv_res[p_path].append(ntv)
            else:
                ntv_res[p_path].insert(idx, ntv)                            
        elif self.op == 'test' and self.entity:
            if not (idx == '-' and self.ntv in ntv[p_path]) and not (
                isinstance(idx, int) and self.ntv == ntv[self.path]):
                raise NtvOpError('test is not correct')                
        elif self.op == 'remove':
            idx = NtvOp.pointer_index(self.path)[0]
            idx = len(ntv[p_path]) - 1 if idx == '-' else idx
            if isinstance(idx, str): 
                idx = NtvOp.pointer_index(ntv_res[self.path].json_pointer(True))[0]
            ntv_res[p_path+'/'+str(idx)].remove(index=idx)       
        elif self.op == 'replace' and self.entity:
            ntv_res[self.path].replace(self.ntv)
        else:
            raise NtvOpError('op add no result')
        return ntv_res

class NtvPatch:
    ''' The NtvPatch class defines a sequence of operations to apply to an 
    NTV entity'''

    def __init__(self, list_op=None):
        list_op = [] if not list_op else list_op 
        self.list_op = [NtvOp(ope) for ope in list_op]
        
    def __eq__(self, other):
        ''' equal if list_op are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self.list_op == other.list_op

    def __copy__(self):
        ''' Copy all the data '''
        cop = self.__class__(self)
        return cop

    def __setitem__(self, ind, ope):
        ''' replace op item at the `ind` row with `op`'''
        if ind < 0 or ind >= len(self):
            raise NtvOpError("out of bounds")
        self.list_op[ind] = ope

    def __delitem__(self, ind):
        '''remove ntv_value item at the `ind` row'''
        if isinstance(ind, int):
            self.list_op.pop(ind)
        else:            
            self.list_op.pop(self.list_op.index(self[ind]))

    def __len__(self):
        ''' len of list_op'''
        return len(self.list_op)

    def __str__(self):
        '''return list of op json format'''
        return json.dumps([ope.json for ope in self.list_op])

    def __repr__(self):
        '''return classname and code'''
        rep = 'NtvPatch :\n'
        for ind, op in enumerate(self):
            rep += '    op' + str(ind).ljust(3, ' ') + ' : ' + repr(op)[5:] + '\n'
        return rep

    def __contains__(self, item):
        ''' item of NtvPatch'''
        return item in self.list_op

    def __iter__(self):
        ''' iterator for op'''
        return iter(self.list_op)

    def __getitem__(self, selec):
        ''' return ntv_value item '''
        if selec is None or selec == [] or selec == () or selec == '':
            return self
        if isinstance(selec, (list, tuple)) and len(selec) == 1:
            selec = selec[0]
        if isinstance(selec, (list, tuple)):
            return [self[i] for i in selec]
        return self.list_op[selec]            

    def append(self, ope):
        '''append ope in the NtvPatch'''
        self.list_op.append(ope)

    def exe(self, ntv):
        '''execute the included operations with ntv entity and return 
        the resulting entity'''
        ntv_res = ntv
        for ope in self:
            ntv_res = ope.exe(ntv_res)
        return ntv_res
    
class NtvOpError(Exception):
    ''' NtvOp Exception'''
    # pass