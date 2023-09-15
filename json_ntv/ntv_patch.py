# -*- coding: utf-8 -*-
"""
Created on Sept 10 2023

@author: Philippe@loco-labs.io

The `ntv_patch` module is part of the `NTV.json_ntv` package ([specification document](
https://loco-philippe.github.io/ES/JSON%20semantic%20format%20(JSON-NTV).htm)).

It contains the classes `NtvOperation`, `NtvPatch`.
"""
from json_ntv import Ntv
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
        self.ntv = Ntv.obj(entity) if entity else None
        if not self.path or not self.op in ['add', 'test', 'move', 'remove', 
                                            'copy', 'replace']:
            raise NtvOpError('path or op is not correct')
        
    @property
    def json(self):
        dic = {'op': self.op, 'path': self.path, 'entity': self.entity, 
               'comment':self.comment, 'from': self.from_path, 'index': self.index}
        return {key: val for key, val in dic.items() if val}

    def exec_op(self, ntv):
        ntv_res = copy(ntv)
        if self.op == 'add' and not self.index is None:
            ntv_res[self.path].insert(self.index, self.ntv)
        elif self.op == 'add' and self.index is None:
            ntv_res[self.path].append(self.ntv)
        elif self.op == 'test' and self.entity and (
            self.index is None and self.ntv in ntv[self.path] or
            not self.index is None and self.ntv == ntv[self.path][self.index]):
            pass
        else:
            raise NtvOpError('op add no result')
        return ntv_res
    
class NtvOpError(Exception):
    ''' NtvOp Exception'''
    # pass