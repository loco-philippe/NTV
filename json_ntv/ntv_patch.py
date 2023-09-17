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

class NtvOp:
    ''' The NtvOp class defines operations to apply to an NTV entity'''
    
    def __init__(self, op, path=None, entity=None, comment=None, from_path=None, index=None):
        dic = isinstance(op, dict)
        self.op         = op.get('op')         if dic else op
        self.path       = op.get('path')       if dic else path
        self.entity     = op.get('entity')     if dic else entity
        self.comment    = op.get('comment')    if dic else comment
        self.from_path  = op.get('from')       if dic else from_path
        self.index      = op.get('index')      if dic else index
        self.ntv = Ntv.obj(self.entity) if self.entity else None
        if not self.path or not self.op in ['add', 'test', 'move', 'remove', 
                                            'copy', 'replace']:
            raise NtvOpError('path or op is not correct')
        
    def __repr__(self):
        return json.dumps(self.json)
    
    @property
    def json(self):
        dic = {'op': self.op, 'path': self.path, 'entity': self.entity, 
               'comment':self.comment, 'from': self.from_path, 'index': self.index}
        return {key: val for key, val in dic.items() if val}

    @staticmethod 
    def index(path):
        '''return the last pointer of the path and the path without the last pointer'''
        pointer = Ntv.pointer_list(path)
        return (pointer[-1], Ntv.pointer_json(pointer[:-1]))

    def exe(self, ntv):
        ntv_res = copy(ntv)
        if self.op in ['move', 'copy', 'add']:
            if self.op == 'move':
                ntv = ntv_res[self.from_path]
                idx = NtvOp.index(self.from_path)[0]
                if isinstance(idx, str): 
                    idx = NtvOp.index(ntv_res[self.from_path].json_pointer(True))[0]
                ntv_res[self.from_path].remove(index=idx)       
                ntv.parent = None
            elif self.op == 'add':
                ntv = self.ntv           
            else:
                ntv = copy(ntv_res[self.from_path])
            if self.index is None:
                ntv_res[self.path].append(ntv)
            else:
                ntv_res[self.path].insert(self.index, ntv)                
        elif self.op == 'test' and self.entity and (
            self.index is None and self.ntv in ntv[self.path] or
            not self.index is None and self.ntv == ntv[self.path][self.index]):
            pass
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

class NtvOpError(Exception):
    ''' NtvOp Exception'''
    # pass