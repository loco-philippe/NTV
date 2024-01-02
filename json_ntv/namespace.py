# -*- coding: utf-8 -*-
"""
Created on Jan 20 2023

@author: Philippe@loco-labs.io

The `namespace` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).
 
It contains the `Namespace` and the `NtvType` classes and the `str_type` method for NTV entities.    
      
# 0 - Presentation

The NTVtype is defined by a name and a Namespace. The name is unique in the Namespace

A Namespace is represented by a string followed by a point.
Namespaces may be nested (the global Namespace is represented by an empty string).

The Namespace representations are added to the value of an NTVtype to have an absolute
representation of an NTVtype (long_name).

*Example for an absolute representation of an NTVtype defined in two nested Namespace :*
*“ns1.ns2.type”*
*where:*
- *ns1. is a Namespace defined in the global Namespace,*
- *ns2. is a Namespace defined in the ns1. Namespace,*
- *type is a NTVtype defined in the ns2. Namespace*

# 1 - Global Namespace

The structure of types by namespace makes it possible to have types corresponding
to recognized standards at the global level.
Generic types can also be defined (calculation of the exact type when decoding the value).

The global namespace can include the following structures:

## 1.1 - Simple (JSON RFC8259)

| type (generic type)| value example                 |
|--------------------|-------------------------------|
| boolean (json)     | true                          |
| null (json)        | null                          |
| number (json)      | 45.2                          |
| string (json)      | "string"                      |
| array  (json)      | [1, 2, 3]                     |
| object (json)      | { "str": "test", "bool": true}|

## 1.2 - Datation (ISO8601 and Posix)

| type (generic type)| value example                 |
|--------------------|-------------------------------|
| year               | 1998                          |
| month              | 10                            |
| day                | 21                            |
| wday               | 2                             |
| yday               | 251                           |
| week               | 38                            |
| hour               | 20                            |
| minute             | 18                            |
| second             | 54                            |
| date (dat)         | “2022-01-28”                  |
| time (dat)         | “T18:23:54”,  “18:23”, “T18”  |
| datetime (dat)     | “2022-01-28T18-23-54Z”, “2022-01-28T18-23-54+0400”        |

## 1.3 - Duration (ISO8601 and Posix)

| type (generic type)| value example                 |
|--------------------|-------------------------------|
| period             | "2007-03-01T13:00:00Z/2008-05-11T15:30:00Z"  |
| duration           | "P0002-10- 15T10:30:20"       |
| timearray          | [date1, date2]                |

## 1.4 - Location (RFC7946 and Open Location Code):

| type (generic type) | value example                                |
|---------------------|------------------------------|
| point (loc)         | [ 5.12, 45.256 ] (lon, lat)  |
| line (loc)          | [ point1, point2, point3 ]   |
| ring                | [ point1, point2, point3 ]   |
| multiline           | [ line1, line2, line3]       |
| polygon (loc)       | [ ring1, ring2, ring3]       |
| multipolygon (loc)  | [ poly1, poly2, poly3 ]      |
| box (loc)           | [ -10.0, -10.0, 10.0, 10.0 ] |
| geojson (loc)       | {“type”: “point”, “coordinates”: [40.0, 0.0] } |
| codeolc (loc)       | “8FW4V75V+8F6”               |

## 1.5 - Tabular data

| NTVtype  | NTVvalue                                               |
|----------|--------------------------------------------------------|
| row      | JSON-array of JSON-NTV                                 |
| field    | JSON-array of NTVvalue (following JSON-TAB format)     |
| table    | JSON-array of JSON-NTV fields with the same length     |


## 1.6 - Normalized strings

The type could be `uri`, cf exemples :
- "https://www.ietf.org/rfc/rfc3986.txt"
- "https://gallica.bnf.fr/ark:/12148/bpt6k107371t"
- "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
- "ni:///sha-256;UyaQV-Ev4rdLoHyJJWCi11OHfrYv9E1aGQAlMO2X_-Q"
- "geo:13.4125,103.86673" *(RFC5870)*
- "info:eu-repo/dai/nl/12345"
- "mailto:John.Doe@example.com"
- "news:comp.infosystems.www.servers.unix"
- "urn:oasis:names:specification:docbook:dtd:xml:4.1.2"

## 1.7 - Namespaces

Namespaces could also be defined to reference for example:
- geopolitical entities: ISO3166-1 country code (for example "fr." for France)
- data catalogs, for example:

| NTVtype      | example JSON-NTV                                                     |
|--------------|----------------------------------------------------------------------|
| schemaorg.   | <div>{ “:schemaorg.propertyID”: “NO2” }</div><div>{ “:schemaorg.unitText”:”µg/m3”}</div>  |
| darwincore.  | { “:darwincore.acceptedNameUsage”: “Tamias minimus” }                |

## 1.8 - Identifiers

For example :

| type         | definition                      | exemple               |
|--------------|---------------------------------|-----------------------|
| fr.uic       | code UIC station                | 8757449               |
| fr.iata      | code IATA airport               | CDG                   |


# 2 - Example of using a `fr.` namespace

This namespace is dedicated to datasets associated with the France geopolitical namespace
(see also the [presentation document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-namespace-fr.pdf)).

A namespace defines:
- identifiers used to access additional data,
- namespaces associated with catalogs or data sets,
- structured entities used to facilitate the use of data

## 2.1 - Identifiers
They could correspond to identifiers used in many referenced datasets
(via a data schema or a data model).

For example :

| type         | definition                      | example               |
|--------------|---------------------------------|-----------------------|
| fr.dep       | code département                | 60                    |
| fr.cp        | code postal                     | 76450                 |
| fr.naf       | code NAF                        | 23                    |
| fr.siren     | code SIREN enterprise           | 418447363             |
| fr.fantoir   | code FANTOIR voie               | 4500023086F           |
| fr.uai       | code UAI établissement          | 0951099D              |
| fr.aca       | code académies                  | 22                    |
| fr.finessej  | code FINESS entité juridique    | 790001606             |
| fr.rna       | code WALDEC association         | 843S0843004860        |
| fr.spi       | code SPI numéro fiscal          | 1899582886173         |
| fr.nir       | code NIR sécurité sociale       | 164026005705953       |

## 2.2 Namespaces
Namespaces could correspond to catalogs or data sets whose data types are identified
in data models or in referenced data schemas.

For example :

|    type     | example JSON-NTV                                          |
|-------------|-----------------------------------------------------------|
| fr.sandre.  | <div>{ ":fr.sandre.CdStationHydro": K163 3010 01 }</div><div>{ ":fr.sandre.TypStationHydro": "standard" }</div>    |
| fr.synop.   | <div>{ ":fr.synop.numer_sta": 07130 }</div><div>{  ":fr.synop.t": 300, ":fr.synop.ff": 5 }</div>                   |
| fr.IRVE.    | <div>{ ":fr.IRVE.nom_station": "M2026" }</div><div>{ ":fr.IRVE.nom_operateur": "DEBELEC" }</div>                   |
| fr.BAN.     | <div>{ ":fr.BAN.numero": 54 }</div><div>{ ":fr.BAN.lon": 3.5124 }</div>|

## 2.3 Entities
They could correspond to assemblies of data associated with a defined structure.

For example :

|    type      | example JSON-NTV                                         |
|--------------|----------------------------------------------------------|
| fr.parcelle  | <div>{“maParcelle:fr.parcelle”: [ 84500, 0, I, 97]}</div><div><i>(fr.cp, fr.cadastre.préfixe, fr.cadastre.section, fr.cadastre.numéro)</i></div> |
| fr.adresse   | <div>{“monAdresse:fr.adresse”: [ 54, bis, rue de la mairie, 78730 ]</div><div><i>(fr.BAN.numero, fr.BAN.rep, fr.BAN.nom_voie, fr.cp)</i></div>  |

"""
import configparser
from pathlib import Path
import json
import requests
from time import time

import json_ntv

def agreg_type(str_typ, def_type, single):
    '''aggregate str_typ and def_type to return an NtvType or a Namespace if not single

    *Parameters*

        - **str_typ** : NtvType or String (long_name) - NtvType to aggregate
        - **def_typ** : NtvType or String (long_name) - default NtvType or Namespace
        - **single** : Boolean - Ntv entity concerned (True if NtvSingle)'''
    if isinstance(str_typ, NtvType):
        str_typ = str_typ.long_name
    def_type = str_type(def_type, single)
    #if not str_typ and (isinstance(def_type, NtvType) or
    #                    (not isinstance(def_type, NtvType) and not single)):
    if not str_typ and (not single or isinstance(def_type, NtvType)):
        return def_type
    if not str_typ:
        return NtvType('json')
    clas = NtvType
    if str_typ[-1] == '.':
        clas = Namespace
    if not def_type:
        return clas.add(str_typ)
    if clas == NtvType or clas == Namespace and not single:
        try:
            return clas.add(str_typ)
        except NtvTypeError:
            return clas.add(_join_type(def_type.long_name, str_typ))
    raise NtvTypeError(str_typ + 'and' +
                       def_type.long_name + 'are incompatible')


def _join_type(namesp, str_typ):
    '''join Namespace string and NtvType or Namespace string'''
    namesp_split = namesp.split('.')[:-1]
    for name in str_typ.split('.'):
        if not name in namesp_split:
            namesp_split.append(name)
    return '.'.join(namesp_split)

def from_file(file, name, long_parent=None):
    long_parent = '' if not long_parent else long_parent
    if name[0] != '$':
        raise NtvTypeError(name + ' is not a custom NTVtype')
    if not long_parent in Namespace.namespaces():        
        raise NtvTypeError(long_parent + ' is not a valid NTVtype')
    schema_nsp = Namespace(name, long_parent)
    config = configparser.ConfigParser()
    config.read(file)
    _add_file(config, schema_nsp)
        
def _add_file(config, namesp):
    if namesp.name in config.sections():    
        confname = config[namesp.name]
        if 'type' in confname:
            for nspname in json.loads(confname['namespace']):
                nsp = Namespace(nspname, namesp, force=True)
                _add_file(config, nsp) 
            for typ in json.loads(confname['type']):
                NtvType(typ, namesp, force=True)
                
def relative_type(str_def, str_typ):
    '''return relative str_typ string from NtvType or Namespace str_def

    *Parameters*

        - **str_def** : String - long_name of the Namespace or NtvType
        - **str_type** : String - long_name of Ntvtype to be relative '''
    if not str_def and not str_typ:
        return ''
    if str_def == str_typ:
        return ''
    if not str_def or not str_def in str_typ:
        return str_typ
    if not str_typ and str_def[-1] != ".":
        return str_def
    str_def_split = str_def.split('.')[:-1]
    str_typ_split = str_typ.split('.')
    ind = 0
    for ind, name in enumerate(str_typ_split):
        if not name in str_def_split:
            break
    return '.'.join(str_typ_split[ind:])


def str_type(long_name, single):
    ''' create a NtvType or a Namespace from a string

    *Parameters*

        - **long_name** : String - name of the Namespace or NtvType
        - **single** : Boolean - If True, default type is 'json', else None'''
    if not long_name and single:
        return NtvType('json')
    if not long_name and not single:
        return None
    if isinstance(long_name, (NtvType, Namespace)):
        return long_name
    if not isinstance(long_name, str):
        raise NtvTypeError('the name is not a string')
    if long_name[-1] == '.':
        return Namespace.add(long_name)
    return NtvType.add(long_name)


class NtvType():
    ''' type of NTV entities.

    *Attributes :*

    - **name** : String - name of the type
    - **nspace** : Namespace - namespace associated
    - **custom** : boolean - True if not referenced

    The methods defined in this class are :

    *classmethods*
    - `types`
    - `add`

    *dynamic values (@property)*
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
    def add(cls, long_name, module=False, force=False):
        '''activate and return a valid NtvType defined by the long name
        
        *parameters :*

        - **long_name** : String - absolut name of the NtvType
        - **module** : boolean (default False) - if True search data in the 
        local .ini file, else in the distant repository
        '''
        if long_name == '':
            return None
        if long_name in NtvType.types():
            return cls._types_[long_name]
        split_name = long_name.rsplit('.', 1)
        if split_name[-1] == '':
            raise NtvTypeError(long_name + ' is not a valid NTVtype')
        if len(split_name) == 1:
            return cls(split_name[0], force=force)
        if len(split_name) == 2:
            nspace = Namespace.add(split_name[0]+'.', module=module, force=force)
            return cls(split_name[1], nspace, force=force)
        raise NtvTypeError(long_name + ' is not a valid NTVtype')

    def __init__(self, name, nspace=None, force=False):
        '''NtvType constructor.

        *Parameters*

        - **name** : string - name of the Type
        - **nspace** : Namespace (default None) - namespace associated'''
        if isinstance(name, NtvType):
            self.name = name.name
            self.nspace = name.nspace
            self.custom = name.custom
            return
        if not name or not isinstance(name, str):
            raise NtvTypeError('null name is not allowed')
        if not name and not nspace:
            name = 'json'
        if not nspace:
            nspace = Namespace._namespaces_['']
        #if name[0] != '$' and not nspace.custom and not name in nspace.content['type']:
        if name[0] != '$' and not force and not name in nspace.content['type']:
            raise NtvTypeError(name + ' is not defined in ' + nspace.long_name)
        self.name = name
        self.nspace = nspace
        self.custom = nspace.custom or name[0] == '$'
        self._types_[self.long_name] = self
        return

    def __eq__(self, other):
        ''' equal if name and nspace are equal'''
        if self is None and other is None:
            return True
        if self is None or other is None:
            return False
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return self.name == other.name and self.nspace == other.nspace
    def __hash__(self):
        '''return hash(name) + hash(nspace)'''
        return hash(self.name) + hash(self.nspace)

    def __str__(self):
        '''return string format'''
        return self.long_name

    def __repr__(self):
        '''return classname and long name'''
        return self.__class__.__name__ + '(' + self.long_name + ')'

    @property
    def gen_type(self):
        '''return the generic type of the NtvType'''
        if self.custom:
            return ''
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

    *Attributes :*

    - **name** : String - name of the namespace
    - **file** : string - location of the file init
    - **content** : dict - {'type': <list of ntv_type names>,  
                            'namespace': <list of namespace names>}
    - **parent** : Namespace - parent namespace
    - **custom** : boolean - True if not referenced

    The methods defined in this class are :

    *classmethods*
    - `namespaces`
    - `add`

    *dynamic values (@property)*
    - `long_name`

    *instance methods*
    - `is_child`
    - `is_parent`
    '''
    _namespaces_ = {}
    #_pathconfig_ = 'https://raw.githubusercontent.com/loco-philippe/NTV/master/config/'
    _pathconfig_ = 'https://raw.githubusercontent.com/loco-philippe/NTV/master/json_ntv/config/'
    #_global_ = "NTV_global_namespace.ini"
    _global_ = "NTV_global_namespace.ini"

    @classmethod
    def namespaces(cls):
        '''return the list of Namespace created'''
        return [nam.long_name for nam in cls._namespaces_.values()]

    @classmethod
    def add(cls, long_name, module=False, force=False):
        '''activate and return a valid Namespace defined by the long_name.
                
        *parameters :*

        - **long_name** : String - absolut name of the Namespace
        - **module** : boolean (default False) - if True search data in the 
        local .ini file, else in the distant repository
        '''
        if long_name in Namespace.namespaces():
            return cls._namespaces_[long_name]
        split_name = long_name.rsplit('.', 2)
        if len(split_name) == 1 or split_name[-1] != '':
            raise NtvTypeError(long_name + ' is not a valid classname')
        if len(split_name) == 2:
            return cls(split_name[0]+'.', module=module, force=force)
        if len(split_name) == 3:
            parent = Namespace.add(split_name[0]+'.', force=force)
            return cls(split_name[1]+'.', parent, module=module, force=force)
        raise NtvTypeError(long_name + ' is not a valid classname')

    def __init__(self, name='', parent=None, module=False, force=False):
        '''
        Namespace constructor.

        *Parameters*

        - **name** : String - name of the namespace
        - **parent** : Namespace - parent namespace
        - **module** : boolean (default False) - if True search data in the 
                        local .ini file, else in the distant repository
        - **content** : dict : {'type': <list of ntv_type names>,  
                                'namespace': <list of namespace names>}
        '''
        if name and not parent:
            parent = Namespace._namespaces_['']
        #if name and name[0] != '$' and not parent.custom and \
        if name and name[0] != '$' and not force and \
          not name in parent.content['namespace']:
            raise NtvTypeError(name + ' is not defined in ' + parent.long_name)
        self.name = name
        self.parent = parent
        self.custom = parent.custom or name[0] == '$' if parent else False
        self.file = Namespace._file(self.parent, self.name, self.custom, module)
        #print(self.file, self.name, self.custom, module)
        self.content = Namespace._content(self.file, self.name, self.custom, module)
        self._namespaces_[self.long_name] = self

    def __eq__(self, other):
        ''' equal if name and parent are equal'''
        if self is None and other is None:
            return True
        if self is None or other is None:
            return False
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return self.name == other.name and self.parent == other.parent

    def __hash__(self):
        '''return hash(name) + hash(parent)'''
        return hash(self.name) + hash(self.parent)

    def __str__(self):
        '''return string format'''
        return self.long_name

    def __repr__(self):
        '''return classname and long name'''
        return self.__class__.__name__ + '(' + self.long_name + ')'

    @staticmethod
    def _file(parent, name, custom, module):
        '''return the file name of the Namespace configuration
                
        *parameters :*

        - **parent** : Namespace - Parent of the Namespace
        - **name** : String - name of the Namespace
        - **custom** : boolean - if True, return None (custom Namespace)
        - **module** : boolean (default False) - if True search data in the 
        local .ini file, else in the distant repository
        '''
        if custom:
            return None
        if parent:
            config = configparser.ConfigParser()
            if module:
                p_file = Path(parent.file).stem + Path(parent.file).suffix
                config.read(Path(json_ntv.__file__).parent / 'config' / p_file)
            else:
                config.read_string(requests.get(
                    parent.file, allow_redirects=True).content.decode())
            return Namespace._pathconfig_ + json.loads(config['data']['namespace'])[name]
        #if module:
        #    return str(Path(json_ntv.__file__).parent / Namespace._global_)
        return Namespace._pathconfig_ + Namespace._global_

    @staticmethod
    def _content(file, name, custom, module):
        '''return the content of the Namespace configuration
        
        *parameters :*

        - **file** : string - file name of the parent Namespace
        - **name** : string - name of the Namespace
        - **custom** : boolean - if True, return empty dict (custom Namespace)
        - **module** : boolean (default False) - if True search data in the 
        local .ini file, else in the distant repository
        
        *return :*
        
        - dict : {'type': <list of ntv_type names>,  
                  'namespace': <list of namespace names>}
        '''
        if custom:
            return {'type': {}, 'namespace': {}}
        config = configparser.ConfigParser()
        if module:
            p_file = Path(file).stem + Path(file).suffix
            config.read(Path(json_ntv.__file__).parent / 'config' / p_file)
            #config.read(Path(json_ntv.__file__
            #    ).parent.joinpath(p_file))
            #print(p_file, Path(json_ntv.__file__).parent.joinpath(p_file))
        else:
            config.read_string(requests.get(
                file, allow_redirects=True).content.decode())
        config_name = config['data']['name']
        if config_name != name:
            raise NtvTypeError(file + ' is not correct')
        #name = 'data' if not name else name
        #return {'type': json.loads(config[name]['type']),
        return {'type': json.loads(config['data']['type']),
                'namespace': json.loads(config['data']['namespace'])}

    @property
    def long_name(self):
        '''return a string with the absolute name'''
        if self.parent is None or self.parent.name == '':
            return self.name
        return self.parent.long_name + self.name

    def is_child(self, nspace):
        '''return the number of level between self and nspace, -1 if None'''
        parent = self.parent
        if not self.name:
            return -1
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
        '''return the number of level between self and nspace, -1 if None'''
        return nspace.is_child(self)


class NtvTypeError(Exception):
    ''' NtvType or Namespace Exception'''
    # pass

nroot = Namespace(module=True)
for root_typ in nroot.content['type'].keys():
    typ = NtvType.add(root_typ, module=True)
typ_json = NtvType('json')
