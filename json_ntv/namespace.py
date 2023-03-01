# -*- coding: utf-8 -*-
"""
Created on Feb 27 22:44:05 2023

@author: Philippe@loco-labs.io

The `namespace` module contains the Namespace and the NtvType classes for NTV entity.
"""
import configparser
import json


class NtvType():
    ''' type of NTV entities.

    *Attributes :

    - **name** : String - name of the type
    - **nspace** : Namespace - namespace associated

    The methods defined in this class are :

    *classmethods*
    - `types`
    - `add`
    - `add_ntv_type`

    *dynamic values (@property)
    - `gen_type`
    - `long_name`

    *instance methods*
    - `isin_namespace`
    '''
    _types_ = {}

    @classmethod
    def types(cls):
        '''return the list of NtvType created'''
        return [nam.long_name for nam in cls._types_.values()]

    @classmethod
    def add(cls, long_name):
        '''activate and return a valid NtvType defined by the long name'''
        if long_name in NtvType.types():
            return cls._types_[long_name]
        split_name = long_name.rsplit('.', 1)
        if split_name[-1] == '':
            raise NtvError(long_name + ' is not a valid NTVtype')
        if len(split_name) == 1:
            return cls.add_ntv_type(split_name[0])
        if len(split_name) == 2:
            nspace = Namespace.add(split_name[0]+'.')
            return cls.add_ntv_type(split_name[1], nspace)
        raise NtvError(long_name + ' is not a valid NTVtype')

    @classmethod
    def add_ntv_type(cls, name, nspace=None):
        '''activate and return a valid NtvType defined by a name and a Namespace'''
        if not nspace:
            nspace = Namespace()
        if not name in nspace.content['type']:
            raise NtvError(name + ' is not defined in ' + nspace.long_name)
        return cls(name, nspace)

    def __init__(self, name, nspace=None):
        '''NtvType constructor.

        *Parameters*

        - **name** : string - name of the Type
        - **nspace** : Namespace (default None) - namespace associated'''
        if not nspace:
            nspace = Namespace()
        self.name = name
        self.nspace = nspace
        self._types_[self.long_name] = self

    def __eq__(self, other):
        ''' equal if name and nspace are equal'''
        return self.name == other.name and self.nspace == other.nspace

    def __str__(self):
        '''return string format'''
        return self.long_name

    def __repr__(self):
        '''return classname and long name'''
        return self.__class__.__name__ + '(' + self.long_name + ')'

    @property
    def gen_type(self):
        '''return the generic type of the NtvType'''
        return self.nspace.content['type'][self.name]

    @property
    def long_name(self):
        '''return a string with the absolute name'''
        return self.nspace.long_name + self.name

    def isin_namespace(self, long_name):
        '''return the number of level between self and nspace, -1 if None'''
        return self.nspace.is_child(Namespace.add(long_name))


class Namespace():
    ''' Namespace of NTV entities.

    *Attributes :

    - **name** : String - name of the namespace
    - **file** : string - location of the file init
    - **parent** : Namespace - parent namespace

    The methods defined in this class are :

    *classmethods*
    - `namespaces`
    - `add`
    - `add_namespace`

    *dynamic values (@property)
    - `file`
    - `long_name`
    - `content`

    *instance methods*
    - `is_child`
    - `is_parent`
    '''
    _namespaces_ = {}

    @classmethod
    def namespaces(cls):
        '''return the list of Namespace created'''
        return [nam.long_name for nam in cls._namespaces_.values()]

    @classmethod
    def add(cls, long_name):
        '''activate and return a valid Namespace defined by the long name'''
        if long_name in Namespace.namespaces():
            return cls._namespaces_[long_name]
        split_name = long_name.rsplit('.', 2)
        if len(split_name) == 1 or split_name[-1] != '':
            raise NtvError(long_name + ' is not a valid classname')
        if len(split_name) == 2:
            return cls.add_namespace(split_name[0]+'.')
        if len(split_name) == 3:
            parent = Namespace.add(split_name[0]+'.')
            return cls.add_namespace(split_name[1]+'.', parent)
        raise NtvError(long_name + ' is not a valid classname')

    @classmethod
    def add_namespace(cls, name, parent=None):
        '''activate and return a valid Namespace defined by a name and a parent Namespace'''
        if parent is None:
            parent = cls._namespaces_['']
        if not name in parent.content['namespace']:
            raise NtvError(name + ' is not defined in ' + parent.long_name)
        return cls(name, parent)

    def __init__(self, name='', parent=None):
        '''
        Namespace constructor.

        *Parameters*

        - **name** : String - name of the namespace
        - **file** : string - location of the file init
        - **parent** : Namespace - parent namespace'''
        self.name = name
        self.parent = parent
        self._namespaces_[self.long_name] = self

    def __eq__(self, other):
        ''' equal if name and parent are equal'''
        return self.name == other.name and self.parent == other.parent

    def __str__(self):
        '''return string format'''
        return self.long_name

    def __repr__(self):
        '''return classname and long name'''
        return self.__class__.__name__ + '(' + self.long_name + ')'

    @property
    def file(self):
        '''return the file name of the Namespace configuration'''
        config = configparser.ConfigParser()
        if self.parent:
            config.read(self.parent.file)
            return '../config/'+json.loads(config['data']['namespace'])[self.name]
        return "../config/NTV_global_namespace.ini"

    @property
    def content(self):
        '''return the content of the Namespace configuration'''
        config = configparser.ConfigParser()
        config.read(self.file)
        config_name = config['data']['name']
        if config_name != self.name:
            raise NtvError(self.file + ' is not correct')
        return {'type': json.loads(config['data']['type']),
                'namespace': json.loads(config['data']['namespace'])}

    @property
    def long_name(self):
        '''return a string with the absolute name'''
        if self.parent is None or self.parent.name == '':
            return self.name
        return self.parent.long_name + self.name

    def is_child(self, nspace):
        '''return the number of level between self and parent, -1 if None'''
        parent = self.parent
        if self == nspace:
            return 0
        rang = 1
        while parent.name != '' and parent != nspace:
            rang += 1
            parent = parent.parent
        if parent == nspace:
            return rang
        if parent.name == '':
            return -1


    def is_parent(self, nspace):
        '''return the number of level between self and parent, -1 if None'''
        return nspace.is_child(self)


class NtvError(Exception):
    ''' Type Exception'''
    # pass


Nroot = Namespace()
