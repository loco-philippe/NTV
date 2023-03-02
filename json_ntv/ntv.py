# -*- coding: utf-8 -*-
"""
Created on Feb 27 22:44:05 2023

@author: Philippe@loco-labs.io

The `ntv` module contains the NtvSingle, NtvSet and NtvList classes for NTV entity.
"""
import json
from namespace import Namespace, NtvType

class Ntv():
    ''' NTV entity

    *Attributes :

    - **ntv_name** : String - name of the NTV entity
    - **ntv_type**: NtvType - type of the entity
    - **ntv_value**:  value of the entity   
    '''    
    def __init__(self, ntv_value, ntv_name=None, ntv_type=None):
        '''NtvSingle constructor.

        *Parameters*
        
        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **ntv_value**: value of the entity
        '''
        if ntv_type: 
            self.ntv_type = NtvType.add(ntv_type)
        else:
            self.ntv_type = None
        self.ntv_name = ntv_name
        self.ntv_value = ntv_value

    @classmethod 
    def from_obj(self, value):
        ''' return an Ntv object from a Json value '''
        if value.__class__.__name__ in ['NtvSingle', 'NtvList', 'NtvSet']:
            return value
        if isinstance(value, list):
            ntv_list = [Ntv.from_obj(val) for val in value]
            return NtvList(ntv_list)
        if isinstance(value, (int, str, float, bool)):
            return NtvSingle(value)
        if isinstance(value, dict) and len(value) == 1:
            json_name = list(value.keys())[0]
            json_value = value[json_name]
            ntv_name, ntv_type = Ntv.from_json_name(json_name) 
            return NtvSingle(json_value, ntv_name, ntv_type)
    
    @staticmethod
    def from_json_name(string, sep=':'):
        if not isinstance(string, str):
            raise NtvError('a json-name have to be str')
        if string == '':
            return (None, None)
        split = string.rsplit(sep, 2)
        if len(split) == 1:
            return (string, None)
        if split[0] == '':
            return (None, string)
        if split[1] == '':
            return (split[0], None)
        return (split[0], split[1])
        
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

    def to_obj(self, sep=':'):
        '''return the JSON representation of the NTV entity (json-ntv format)'''
        if not self.ntv_type and not self.ntv_name:
            return self.json_value
        if not self.ntv_type and self.ntv_name:
            return { self.ntv_name : self.json_value }
        if self.ntv_type and not self.ntv_name:
            return { sep + self.type_str : self.json_value }  
        else:
            return { self.ntv_name + sep + self.type_str : self.json_value }        

class NtvSingle(Ntv):
    ''' An NTV-single entity is a Ntv entity where ntv_value is the Json value of the entity
    '''
    def __init__(self, ntv_value, ntv_name=None, ntv_type=None):
        '''NtvSingle constructor.

        *Parameters*
        
        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - type of the entity
        - **ntv_value**: Json entity - value of the entity
        '''
        Ntv.__init__(self, ntv_value, ntv_name, ntv_type)

    def __str__(self):
        '''return string format'''
        return json.dumps(self.to_obj())
    
    def to_obj(self):
        '''return string format'''
        return Ntv.to_obj(self, ':')
    
    @property 
    def json_value(self):
        '''return the Json format of the ntv_value'''
        return self.ntv_value
    
class NtvList(Ntv):
    ''' An NTV-list entity is a Ntv entity where:
        - ntv_value is a list of NTV entities,
        - ntv_type is a default type available for included NTV entities
    '''
    def __init__(self, list_ntv, ntv_name=None, ntv_type=None):
        '''NtvList constructor.

        *Parameters*
        
        - **ntv_name** : String (default None) - name of the NTV entity
        - **ntv_type**: String (default None) - default type of the included entities
        - **list_ntv**: list - list of Ntv objects or json_value of Ntv objectd
        '''
        if list_ntv.__class__.__name__ != 'list':
            raise NtvError('ntv_value is not a list')
        #ntv_list_value = [Ntv.from_obj(value) for value in list_ntv]
        ntv_list_value = [value for value in list_ntv]
        Ntv.__init__(self, ntv_list_value, ntv_name, ntv_type)
    
    def __str__(self):
        '''return string format'''
        return json.dumps(self.to_obj())

    def to_obj(self):
        '''return string format'''
        return Ntv.to_obj(self, '::')
    
    @property 
    def json_value(self):
        '''return the Json format of the ntv_value'''
        #return [ntv.json_value for ntv in self.ntv_value]
        return [ntv.to_obj() for ntv in self.ntv_value]
    
class NtvError(Exception):
    ''' NTV Exception'''
    # pass        