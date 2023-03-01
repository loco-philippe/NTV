# -*- coding: utf-8 -*-
"""
Created on Feb 27 22:44:05 2023

@author: Philippe@loco-labs.io

The `ntv` module contains the NtvSingle, NtvSet and NtvList classes for NTV entity.
"""
import json
from namespace import Namespace, NtvType

class NtvSingle():
    ''' NTV-single entity

    *Attributes :

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**: Json entity - value of the entity   
    '''
    def __init__(self, ntv_value, ntv_name=None, ntv_type=None):
        '''NtvSingle constructor.

        *Parameters*
        
        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **ntv_value**: Json entity - value of the entity
        '''
        if ntv_type: 
            self.ntv_type = NtvType.add(ntv_type)
        else:
            self.ntv_type = None
        self.ntv_name = ntv_name
        self.ntv_value = ntv_value
    
    def __str__(self):
        '''return string format'''
        return json.dumps(self.to_obj())

    def __repr__(self):
        '''return classname and code'''
        return self.__class__.__name__ + '(' + self.code_ntv + ')'

    @property 
    def type_str(self):
        if not self.ntv_type:
            return None
        return self.ntv_type.long_name

    @property 
    def code_ntv(self):
        code = ''
        if self.ntv_name:
            code += 'N'
        if self.ntv_type:
            code += 'T'
        code += 'V'
        return code
    
    def to_obj(self):
        '''return the JSON representation of the NTV entity (json-ntv format)'''
        if not self.ntv_type and not self.ntv_name:
            return self.ntv_value
        if not self.ntv_type and self.ntv_name:
            return { self.ntv_name : self.ntv_value }
        if self.ntv_type and not self.ntv_name:
            return { ':' + self.type_str : self.ntv_value }  
        else:
            return { self.ntv_name + ':' + self.type_str : self.ntv_value }
        