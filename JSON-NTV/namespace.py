# -*- coding: utf-8 -*-
"""
Created on Feb 27 22:44:05 2023

@author: Philippe@loco-labs.io

The `namespace` module contains the Namespace class for NTV entity.
"""
import configparser, json

class NtvType():
    ''' type of NTV entities.
    
    *Attributes :
    
    - **name** : String - name of the type
    - **nspace** : Namespace - namespace associated
    - **gentype** : Type - generic type associated
    
    The methods defined in this class are :
    
    *instance methods*
    - `jsonNtvType`    
    - `isAssociated`
    - `isNamespace`
    - `hasNamespace`
    - `toStr`
    '''
    
    def __init__(self, name, nspace=None, gentype=None): 
        '''
        Type constructor.

        *Parameters*

        - **name** : string - name of the Type
        - **nspace** : Namespace (default None) - namespace associated
        - **gentype** : Type (default None) - generic type associated'''
        self.name = name
        self.nspace = nspace
        self.gentype = gentype
        
class Namespace():
    ''' Namespace of NTV entities.
    
    *Attributes :
    
    - **name** : String - name of the namespace
    - **file** : string - location of the file init
    - **parent** : Namespace - parent namespace
    
    The methods defined in this class are :
    
    *classmethods*
    - `namespaces`
    
    *dynamic values (@property)
    - `file`
    - `cName`
    - `content`
    
    *instance methods*
    - `isChild`    
    - `isParent`
    
    *static methods*
    - `load`
    '''
    _namespaces_ =[]
    
    @classmethod
    def namespaces(cls):
        return [nam.cName for nam in cls._namespaces_]
    
    def __init__(self, name='', parent=None): 
        '''
        Namespace constructor.

        *Parameters*

        - **name** : String - name of the namespace
        - **file** : string - location of the file init
        - **parent** : Namespace (default None) - parent namespace'''
        self.name = name
        self.parent = parent
        self._namespaces_.append(self)
        
    @property
    def file(self):
        config = configparser.ConfigParser()
        if self.parent:
            config.read(self.parent.file)
            return json.loads(config['data']['namespace'])[self.name]
        return "NTV_global_namespace.ini"
    
    @property
    def content(self):
        return self.load(self.name, self.parent)
    
    @property
    def cName(self):
        '''return a string with the absolute name'''
        if self.parent is None:
            return self.name
        else:
            return self.parent.cName + self.name

    @staticmethod
    def load(name, parent=None):
        '''return list of Type and list of Namespace included in a Namespace''' 
        config = configparser.ConfigParser()
        if parent:
            config.read(parent.file)
            filename = json.loads(config['data']['namespace'])[name]
        else:
            filename = "NTV_global_namespace.ini"
        config.read(filename)
        configName = config['data']['name']
        if configName != name:
            raise TypeError('name is not correct')            
        dicType = json.loads(config['data']['type'])
        dicNsp = json.loads(config['data']['namespace'])
        return ({'file': filename,
                 'type':{typ:NtvType(typ, dicType[typ], name) for typ in dicType.keys()},
                'namespace': {nsp:Namespace(nsp, parent) for nsp in dicNsp.keys()}})
        
class TypeError(Exception):
    ''' Type Exception'''
    # pass
        