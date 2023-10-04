# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `NTV.json_ntv.ntv_comment` module contains the `NtvComment` class.
"""
import copy
import json 
from json_ntv.ntv import NtvSingle, NtvType, NtvList, Ntv
from json_ntv.ntv_patch import NtvPatch, NtvOp

class NtvComment:
    '''this class includes comments and change management methods for NTV entities :

    - `NtvComment.add_comment`
    - `NtvComment.accept_comment`
    - `NtvComment.reject_comment`
    - `NtvComment.show_comment`
    '''
    def __init__(self, ntv, comments=None):
        ''' the parameter of the constructor is the NtvComment entity'''
        self._ntv = ntv
        self._comments = []
        if not comments:
            return 
        if comments.__class__.__name__ in ('NtvPatch', 'NtvOp'):
            self._comments = [NtvPatch(comments)]
        elif isinstance(comments, list):
            self._comments = [NtvPatch(comment) for comment in comments]
    
    def __repr__(self):
        if not self._comments:
            return 'no comments'
        return json.dumps(self.show_comment())

    def __eq__(self, other):
        ''' equal if _comments and _ntv are equal'''
        return self.__class__.__name__ == other.__class__.__name__ and\
            self._ntv == other._ntv and self._comment == other._comment
    
    def add_comment(self, comment=None):
        '''add comment in comments'''
        #comment = comment if isinstance(comment, (NtvPatch, NtvOp)) else NtvPatch(comment)
        self._comments.append(NtvPatch(comment))
        return len(self._comments)-1

    def reject_comment(self, all_comment=False):
        '''delete the last or all patch'''
        if all_comment or len(self._comments) <= 1:
            return NtvComment(self._ntv, [])
        return NtvComment(self._ntv, self._comments[:-1])
            
    def accept_comment(self, all_comments=True):
        '''accept the first or all comments and return the resulted NTV''' 
        if not self._comments:
            return NtvComment(self._ntv, self._comments)
        apply = self._comments if all_comments else [self._comments[0]]
        ntv = self._ntv
        for comment in apply:
            ntv = comment.exe(ntv)
        return NtvComment(ntv, [] if all_comments else self._comments[1:])
    
    def show_comment(self):
        ''' return comments'''
        if self._comments:
            return [comment.json for comment in self._comments]
        return None
    
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

    def show_comment_old(self):
        ''' return a dict with comments for each commented node'''
        return NtvList([node for node in self._ntv.tree if node.type_str == '$history']).to_obj()
