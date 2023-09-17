# -*- coding: utf-8 -*-
"""
Created on Sept 10 2023

@author: Philippe@loco-labs.io

The `ntv_patch` module is part of the `NTV.json_ntv` package ([specification document](
https://loco-philippe.github.io/ES/JSON%20semantic%20format%20(JSON-NTV).htm)).

It contains the classes `NtvOperation`, `NtvPatch`.
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
        '''return the json representation'''
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
               'comment':self.comment, 'from': self.from_path, 'index': self.index}
        return {key: val for key, val in dic.items() if val}

    @staticmethod 
    def index(path):
        '''return the last pointer of the path and the path without the last pointer'''
        pointer = Ntv.pointer_list(path)
        if pointer == []:
            return (None, None)
        return (pointer[-1], Ntv.pointer_json(pointer[:-1]))

    def exe(self, ntv):
        '''execute the operation with ntv entity and return the resulting entity'''
        ntv_res = copy(ntv)
        idx, p_path = NtvOp.index(self.path)
        if self.op in ['move', 'copy', 'add']:
            if self.op == 'add' and self.entity:
                ntv = self.ntv
            elif self.op == 'copy' and self.from_path:
                ntv = copy(ntv_res[self.from_path])                
            elif self.op == 'move' and self.from_path:
                ntv = ntv_res[self.from_path]
                from_idx, from_p_path = NtvOp.index(self.from_path)
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
            idx = NtvOp.index(self.path)[0]
            if isinstance(idx, str): 
                idx = NtvOp.index(ntv_res[self.path].json_pointer(True))[0]
            ntv_res[self.path].remove(index=idx)       
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
        self.list_op = [NtvOp(op) for op in list_op]
        

class NtvOpError(Exception):
    ''' NtvOp Exception'''
    # pass