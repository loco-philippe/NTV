# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `NTV.json_ntv.ntv_comment` module contains the `NtvComment` class.
"""
import copy
from json_ntv.ntv import NtvSingle, NtvType, NtvList, Ntv
from json_ntv.ntv_patch import NtvPatch

class NtvComment:
    '''this class includes comments and change management methods for NTV entities :

    - `NtvComment.add_comment`
    - `NtvComment.accept_comment`
    - `NtvComment.reject_comment`
    - `NtvComment.show_comment`
    '''
    def __init__(self, ntv):
        ''' the parameter of the constructor is the Ntv entity'''
        self._ntv = ntv
        self.comment = []
        
    def add_comment(self, context, patch=None):
        '''add [context, patch] in the comment'''
        patch = patch if isinstance(patch, NtvPatch) else NtvPatch(patch)
        self.comment.add([context, patch])
        return len(self.comment)-1

    def reject_comment(self, all_comment=False):
        '''delete the last or all comments'''
        if all_comment:
            self.comment = []
        elif len(self.comment) > 0:
            self.comment = self.comment[:-1]

    def accept_comment(self, all_comments=True):
        '''accept the or all comments and return the resulted NTV''' 
        if not self.comment:
            return self._ntv
        apply = self.comment if all_comments else [self.comment[0]]
        ntv = self.ntv
        for comment in apply:
            ntv = comment[1].exe(ntv)
        return ntv
    
    def show_comment(self, context=True, comments=False):
        ''' return a list with comments and context'''
        if context and not comments:
            return [comment[0] for comment in self.comments]
        if not context and comments:
            return [comment[1] for comment in self.comments]
        return [{'context': comment[0], 'patch': comment[1]}
                for comment in self.comments]

    def add_comment_old(self, text, val=None, name=None, typ=None):
        '''add a comment (text) and a proposal for a new NTV entity defined by (val, name and typ)'''
        parent = self._ntv.parent
        if (val, typ, name) == (None, None, None):
            comment = NtvSingle(text, ntv_type='$comment')
        else:            
            if self._ntv.type_str == '$history':
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
    
    def reject_comment_old(self):
        '''delete all the comments'''
        parent = self._ntv.parent
        if self._ntv.type_str != '$history':   
            return
        old_ntv = self._ntv.ntv_value[0]
        parent[parent.ntv_value.index(self._ntv)] = old_ntv

    def accept_comment_old(self):
        ''' replace the NTV entity by the last NTV proposal and delete all comments''' 
        parent = self._ntv.parent
        if self._ntv.type_str != '$history':   
            return
        for ntv in reversed(self._ntv.ntv_value):
            if ntv.type_str != '$comment':
                new_ntv = ntv
                break
        new_ntv = Ntv.obj(new_ntv.ntv_value) if new_ntv.type_str == 'ntv' else new_ntv
        parent[parent.ntv_value.index(self._ntv)] = new_ntv

    def show_comment(self):
        ''' return a dict with comments for each commented node'''
        return NtvList([node for node in self._ntv.tree if node.type_str == '$history']).to_obj()
