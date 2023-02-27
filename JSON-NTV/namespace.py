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
    
    *instance methods*
    - `isChild`    
    - `isParent`
    - `toStr`
    
    *static methods*
    - `loadNamespace`
    '''
    
    def __init__(self, name, file, parent=None): 
        '''
        Namespace constructor.

        *Parameters*

        - **name** : String - name of the namespace
        - **file** : string - location of the file init
        - **parent** : Namespace (default None) - parent namespace'''
        self.name = name
        self.file = file
        self.parent = parent
        
    @staticmethod
    def loadNamespace(name, fileName ='NTV_global_namespace.ini'):
        '''return list of Type and list of Namespace included in fileName''' 
        listType = []
        listNspace = []
        config = configparser.ConfigParser()
        config.read(fileName)
        configName = config['data']['name']
        print(configName, name)
        print(type(configName))
        if configName != name:
            raise TypeError('name is not correct')            
        dicType = json.loads(config['data']['type'])
        for typ in dicType.keys():
            listType.append(NtvType(typ, dicType[typ], name))
        dicNspace = json.loads(config['data']['namespace'])
        for nsp in dicNspace.keys():
            listNspace.append(Namespace(nsp, dicNspace[nsp], None))
        return (listType, listNspace)
    
class TypeError(Exception):
    ''' Type Exception'''
    # pass
        