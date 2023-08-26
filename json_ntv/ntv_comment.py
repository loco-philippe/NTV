# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `python.observation.dataset_interface` module contains the `DatasetInterface` class
(`python.observation.dataset.Dataset` methods).
"""
import copy
from json_ntv.ntv import NtvSingle, NtvType, NtvList, Ntv

class NtvComment:
    '''this class includes NTV comments and change management methods :

    - `NtvComment.add_comment`
    - `NtvComment.accept_comment`
    - `NtvComment.reject_comment`
    '''
    def __init__(self, ntv):
        ''' the parameter of the constructor is the Ntv entity'''
        self._ntv = ntv

    def add_comment(self, text, val=None, name=None, typ=None):
        '''add a comment (text) and a proposal for a new NTV entity defined by (val, name and typ)'''
        parent = self._ntv.parent
        if (val, typ, name) == (None, None, None):
            comment = NtvSingle(text, ntv_type='$comment')
        else:            
            if self.type_str == '$history':
                new_self = copy.copy(self._ntv.ntv_value[0])
            else:
                new_self = copy.copy(self._ntv)
            new_self.ntv_value = new_self.ntv_value if val is None else val 
            new_self.ntv_type = new_self.ntv_type if typ is None else NtvType(typ) 
            new_self.ntv_name = new_self.ntv_name if name is None else name
            comment = NtvSingle(new_self, text)
        if self._ntv.type_str == '$history':
            self._ntv.ntv_value.append(comment)
            return
        com_val = [self._ntv]
        com_val.append(comment)
        com_list = NtvList(com_val, ntv_type=NtvType('$history'), ntv_name=self._ntv.name)
        parent[parent.ntv_value.index(self._ntv)] = com_list
        return
    
    def reject_comment(self):
        '''delete all the comments'''
        parent = self._ntv.parent
        if self._ntv.type_str != '$history':   
            return
        old_ntv = self._ntv.ntv_value[0]
        parent[parent.ntv_value.index(self._ntv)] = old_ntv

    def accept_comment(self):
        ''' replace self by the last NTV proposal and delete all comments''' 
        parent = self._ntv.parent
        if self._ntv.type_str != '$history':   
            return
        for ntv in reversed(self._ntv.ntv_value):
            if ntv.type_str != '$comment':
                new_ntv = ntv
                break
        new_ntv = Ntv.obj(new_ntv.ntv_value) if new_ntv.type_str == 'ntv' else new_ntv
        parent[parent.ntv_value.index(self._ntv)] = new_ntv

    
