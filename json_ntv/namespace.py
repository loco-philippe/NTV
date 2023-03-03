# -*- coding: utf-8 -*-
"""
Created on Feb 27 22:44:05 2023

@author: Philippe@loco-labs.io

The `namespace` module contains the Namespace and the NtvType classes for NTV entity.


# 1 - Data type

The structure of types by namespace makes it possible to have types corresponding to recognized standards at the global level.
Generic types can also be defined (calculation of the exact type when decoding the value).
    
The global namespace can include the following structures:

## 1.1 - Simple (JSON RFC8259)

| type (generic type)| value example                 |
|--------------------|-------------------------------|
| boolean (None)     | true                          |
| null (None)        | null                          |
| number (None)      | 45.2                          |
| string (None)      | "string"                      |
| array  (None)      | [1, 2, 3]                     |
| object (None)      | { "str": "test", "bool": true}|

## 1.2 - Datation (ISO8601 and Posix)

| type (generic type)| value example                 |
|--------------------|-------------------------------|
| year               | 1998                          |
| month              | 10                            |
| day                | 21                            |
| week               | 38                            |
| hour               | 20                            |
| minute             | 18                            |
| second             | 54                            |
| timeposix (dat)    | 123456.78                     |
| date (dat)         | “2022-01-28”                  |
| time (dat)         | “T18:23:54”,  “18:23”, “T18”  |
| datetime (dat)     | “2022-01-28T18-23-54Z”, “2022-01-28T18-23-54+0400”        |
| timearray (dat)    | [date1, date2]                |
| timeslot (dat)     | [timearray1, timearray2]      |   
    
## 1.3 - Duration (ISO8601 and Posix)

| type (generic type) | value example                                |
|---------------------|----------------------------------------------|
| timeinterval (dur)  | "2007-03-01T13:00:00Z/2008-05-11T15:30:00Z"  |
| durationiso (dur)   | "P0002-10- 15T10:30:20"                      |
| durposix (dur)      | 123456.78                                    |
     
## 1.4 - Location (RFC7946 and Open Location Code):

| type (generic type) | value example                                |
|---------------------|------------------------------|
| point (loc)         | [ 5.12, 45.256 ] (lon, lat)  |
| line (loc)          | [ point1, point2, point3 ]   |
| ring                | [ point1, point2, point3 ]   |
| multiline           | [ line1, line2, line3]       |
| polygon (loc)       | [ ring1, ring2, ring3]       |
| multipolygon (loc)  | [ poly1, poly2, poly3 ]      |
| bbox (loc)          | [ -10.0, -10.0, 10.0, 10.0 ] |
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

This namespace is dedicated to datasets associated with the France geopolitical namespace (see also the [presentation document](https://github.com/loco-philippe/Environmental-Sensing/blob/main/JSON-NTV/JSON-NTV-namespace-fr.pdf)).    
    
A namespace defines:
- identifiers used to access additional data,
- namespaces associated with catalogs or data sets,
- structured entities used to facilitate the use of data

## 2.1 - Identifiers
They could correspond to identifiers used in many referenced datasets (via a data schema or a data model).
   
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
Namespaces could correspond to catalogs or data sets whose data types are identified in data models or in referenced data schemas.

For example : 

|    type     | example JSON-NTV                                                                              |
|-------------|-----------------------------------------------------------------------------------------------|
| fr.sandre.  | <div>{ ":fr.sandre.CdStationHydro": K163 3010 01 }</div><div>{ ":fr.sandre.TypStationHydro": "standard" }</div>    |
| fr.synop.   | <div>{ ":fr.synop.numer_sta": 07130 }</div><div>{  ":fr.synop.t": 300, ":fr.synop.ff": 5 }</div>                   |
| fr.IRVE.    | <div>{ ":fr.IRVE.nom_station": "M2026" }</div><div>{ ":fr.IRVE.nom_operateur": "DEBELEC" }</div>                   |
| fr.BAN.     | <div>{ ":fr.BAN.numero": 54 }</div><div>{ ":fr.BAN.lon": 3.5124 }</div>                                            |

## 2.3 Entities
They could correspond to assemblies of data associated with a defined structure.
     
For example : 

|    type      | example JSON-NTV                                                                                                     |
|--------------|----------------------------------------------------------------------------------------------------------------------|
| fr.parcelle  | <div>{“maParcelle:fr.parcelle”: [ 84500, 0, I, 97]}</div><div><i>(fr.cp, fr.cadastre.préfixe, fr.cadastre.section, fr.cadastre.numéro)</i></div> |
| fr.adresse   | <div>{“monAdresse:fr.adresse”: [ 54, bis, rue de la mairie, 78730 ]</div><div><i>(fr.BAN.numero, fr.BAN.rep, fr.BAN.nom_voie, fr.cp)</i></div>  |

"""
import configparser
import requests
import json
import os


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
            raise NtvTypeError(long_name + ' is not a valid NTVtype')
        if len(split_name) == 1:
            return cls.add_ntv_type(split_name[0])
        if len(split_name) == 2:
            nspace = Namespace.add(split_name[0]+'.')
            return cls.add_ntv_type(split_name[1], nspace)
        raise NtvTypeError(long_name + ' is not a valid NTVtype')

    @classmethod
    def add_ntv_type(cls, name, nspace=None):
        '''activate and return a valid NtvType defined by a name and a Namespace'''
        if not nspace:
            nspace = Namespace()
        if not name in nspace.content['type']:
            raise NtvTypeError(name + ' is not defined in ' + nspace.long_name)
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
    _pathconfig_ = 'https://raw.githubusercontent.com/loco-philippe/NTV/master/config/'
    
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
            raise NtvTypeError(long_name + ' is not a valid classname')
        if len(split_name) == 2:
            return cls.add_namespace(split_name[0]+'.')
        if len(split_name) == 3:
            parent = Namespace.add(split_name[0]+'.')
            return cls.add_namespace(split_name[1]+'.', parent)
        raise NtvTypeError(long_name + ' is not a valid classname')

    @classmethod
    def add_namespace(cls, name, parent=None):
        '''activate and return a valid Namespace defined by a name and a parent Namespace'''
        if parent is None:
            parent = cls._namespaces_['']
        if not name in parent.content['namespace']:
            raise NtvTypeError(name + ' is not defined in ' + parent.long_name)
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
        if self.parent:
            config = configparser.ConfigParser()
            config.read_string(requests.get(self.parent.file, allow_redirects=True).content.decode())
            return Namespace._pathconfig_ + json.loads(config['data']['namespace'])[self.name]
        return Namespace._pathconfig_ +"NTV_global_namespace.ini"

    @property
    def content(self):
        '''return the content of the Namespace configuration'''
        config = configparser.ConfigParser()
        config.read_string(requests.get(self.file, allow_redirects=True).content.decode())
        config_name = config['data']['name']
        if config_name != self.name:
            raise NtvTypeError(self.file + ' is not correct')
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


class NtvTypeError(Exception):
    ''' Type Exception'''
    # pass


Nroot = Namespace()
