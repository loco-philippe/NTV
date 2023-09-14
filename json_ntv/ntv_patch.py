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
    
    def __init__(self, op, path, entity=None, from_path=None, index=None):
        self.op = op
        self.path = path
        self.entity = entity
        self.from_path = from_path
        self.index = index
        
    @property
    def json(self):
        dic = {'op': self.op, 'path': self.path, 'entity': self.entity, 
               'from': self.from_path, 'index': self.index}
        return {key: val for key, val in dic.items() if val}

    def exec_op(self, ntv):
        ntv_res = copy(ntv)
        if self.op == 'add' and self.index:
            ntv_res[self.path].insert(self.index, Ntv.obj(self.entity))
        elif self.op == 'add' and not self.index:
            ntv_res[self.path].append(Ntv.obj(self.entity))
        return ntv_res