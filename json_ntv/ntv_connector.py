# -*- coding: utf-8 -*-
"""
Created on Feb 27 2023

@author: Philippe@loco-labs.io

The `NTV.ntv_connector` module is part of the `NTV.json_ntv` package ([specification document](
https://github.com/loco-philippe/NTV/blob/main/documentation/JSON-NTV-standard.pdf)).

A NtvConnector is defined by:
- clas_obj: str - define the class name of the object to convert
- clas_typ: str - define the NTVtype of the converted object
- to_obj_ntv: method - converter from JsonNTV to the object
- to_json_ntv: method - converter from the object to JsonNTV
    
It contains :

- methods `from_csv` and `to_csv` to convert CSV files and 'tab' NTV entity
- the child classes of `NTV.json_ntv.ntv.NtvConnector` abstract class:
    - `SfieldConnec`:    'field' connector
    - `SdatasetConnec`:  'tab' connector
    - `NfieldConnec`:    'field' connector
    - `NdatasetConnec`:  'tab' connector
    - `MermaidConnec`:   '$mermaid' connector
    - `ShapelyConnec`:   'geometry' connector
    - `CborConnec`:      '$cbor' connector


"""
import datetime
import csv
import json

from json_ntv.ntv import Ntv, NtvConnector, NtvList, NtvSingle, NtvTree
#from observation import Sfield


def from_csv(file_name, single_tab=True, dialect='excel', **fmtparams):
    ''' return a 'tab' NtvSingle from a csv file

    *parameters*

    - **file_name** : name of the csv file
    - **single_tab** : boolean (default True) - if True return a 'tab' NtvSingle,
    else return a NtvSet.
    - **dialect, fmtparams** : parameters of csv.DictReader object'''
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile, dialect=dialect, **fmtparams)
        names = reader.fieldnames
        list_ntv_value = [[] for nam in names]
        for row in reader:
            for ind_field, val in enumerate(list(row.values())):
                list_ntv_value[ind_field].append(json.loads(val))
    list_ntv = []
    for ind_field, field in enumerate(names):
        list_ntv.append(
            NtvList(list_ntv_value[ind_field], *Ntv.from_obj_name(field)[:2]))
    if single_tab:
        return NtvSingle(NtvList(list_ntv, None, None).to_obj(), None, 'tab')
    return NtvList(list_ntv, None, None)


def to_csv(file_name, ntv, *args, restval='', extrasaction='raise', dialect='excel', **kwds):
    ''' convert a 'tab' NtvSingle into csv file and return the file name

    *parameters*

    - **file_name** : name of the csv file
    - **ntv** : 'tab' NtvSingle to convert
    - **args, restval, extrasaction, dialect, kwds** : parameters of csv.DictWriter object'''
    if isinstance(ntv, NtvSingle):
        ntv_set = Ntv.obj(ntv.ntv_value)
    else:
        ntv_set = ntv
    list_ntv = [Ntv.obj(field) for field in ntv_set]
    fieldnames = [ntv_field.json_name(string=True) for ntv_field in list_ntv]
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=restval,
                                extrasaction=extrasaction, dialect=dialect, *args, **kwds)
        writer.writeheader()
        for i in range(len(list_ntv[0])):
            writer.writerow({name: field_ntv[i].to_obj(field_ntv.ntv_type, encoded=True)
                             for name, field_ntv in zip(fieldnames, list_ntv)})
    return file_name


class ShapelyConnec(NtvConnector):
    '''NTV connector for geographic location'''

    clas_obj = 'geometry'
    clas_typ = 'geometry'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into a shapely geometry object defined by 'type_geo'.

        *Parameters*

        - **type_geo** : type of geometry (point, multipoint, line, multiline',
        polygon, multipolygon)
        - **ntv_value** : array - coordinates'''
        from shapely import geometry
        type_geo = ShapelyConnec.type_geo(ntv_value) if not 'type_geo' in kwargs \
            or kwargs['type_geo'] == 'geometry' else kwargs['type_geo']
        return geometry.shape({"type": type_geo, "coordinates": ntv_value})

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert NTV object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - NTV type of geometry (point, multipoint,
        line, multiline', polygon, multipolygon),
        - **name** : string (default None) - name of the NTV object
        - **value** : shapely geometry'''
        return (Ntv._listed(value.__geo_interface__['coordinates']), name, typ)

    @staticmethod
    def to_coord(geom):
        ''' convert shapely geometry into geojson coordinates.'''
        return Ntv._listed(geom.__geo_interface__['coordinates'])

    @staticmethod
    def to_geojson(geom):
        ''' convert shapely geometry into geojson string'''
        return json.dumps(geom.__geo_interface__)

    @staticmethod
    def from_geojson(geojson):
        ''' convert geojson string into shapely geometry.'''
        from shapely import geometry
        return geometry.shape(json.loads(geojson))
    
    @staticmethod 
    def to_geometry(value):
        '''convert geojson coordinates into shapely geometry'''
        return ShapelyConnec.to_obj_ntv(value, type_geo=ShapelyConnec.type_geo(value))
    
    @staticmethod 
    def type_geo(value):
        '''return geometry type of the value'''
        if not value or not isinstance(value, list):
            return 'not a geometry'
        val = value[0]
        if not isinstance(val, list):
            return 'point'
        val = val[0]
        if not isinstance(val, list):
            return 'line'        
        return 'polygon'
    
class CborConnec(NtvConnector):
    '''NTV connector for binary data'''

    clas_obj = 'bytes'
    clas_typ = '$cbor'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a binary CBOR object (no parameters).'''
        import cbor2
        return cbor2.dumps(ntv_value, datetime_as_timestamp=True,
                           timezone=datetime.timezone.utc, canonical=False,
                           date_as_datetime=True)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert NTV binary object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : binary data'''
        import cbor2
        return (cbor2.loads(value), name, typ)


class NfieldConnec(NtvConnector):
    '''NTV connector for NTV Field data'''

    clas_obj = 'Nfield'
    clas_typ = 'field'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a NTV Field object (no parameters).'''
        from observation.fields import Nfield
        ntv = Ntv.obj(ntv_value)
        return Nfield.from_ntv(ntv)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert NTV Field object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : NTV Field values (default format)'''
        return (value.to_ntv(name=True).to_obj(), name,
                NfieldConnec.clas_typ if not typ else typ)


class SfieldConnec(NtvConnector):
    '''NTV connector for simple Field data'''

    clas_obj = 'Sfield'
    clas_typ = 'field'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a simple Field object (no parameters).'''
        from observation.fields import Sfield
        ntv = Ntv.obj(ntv_value)
        return Sfield.from_ntv(ntv)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert simple Field object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : simple Field values (default format)'''
        return (value.to_ntv(name=True).to_obj(), name,
                NfieldConnec.clas_typ if not typ else typ)


class NdatasetConnec(NtvConnector):
    '''NTV connector for NTV Dataset data'''

    clas_obj = 'Ndataset'
    clas_typ = 'tab'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a NTV Dataset object (no parameters).'''
        from observation.datasets import Ndataset

        ntv = Ntv.obj(ntv_value)
        return Ndataset.from_ntv(ntv)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert NTV Dataset object (value, name, type) into NTV json (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : NTV Dataset values'''
        return (value.to_ntv().to_obj(), name,
                NdatasetConnec.clas_typ if not typ else typ)


class SdatasetConnec(NtvConnector):
    '''NTV connector for simple Dataset data'''

    clas_obj = 'Sdataset'
    clas_typ = 'tab'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert json ntv_value into a simple Dataset object (no parameters).'''
        from observation.datasets import Sdataset

        ntv = Ntv.obj(ntv_value)
        return Sdataset.from_ntv(ntv)

    @staticmethod
    def to_json_ntv(value, name=None, typ=None):
        ''' convert simple Dataset object (value, name, type) into NTV json
        (json-value, name, type).

        *Parameters*

        - **typ** : string (default None) - type of the NTV object,
        - **name** : string (default None) - name of the NTV object
        - **value** : simple Dataset values'''
        return (value.to_ntv().to_obj(), name,
                SdatasetConnec.clas_typ if not typ else typ)

class MermaidConnec(NtvConnector):
    '''NTV connector for Mermaid diagram'''

    clas_obj = 'Mermaid'
    clas_typ = '$mermaid'

    @staticmethod
    def to_obj_ntv(ntv_value, **kwargs):
        ''' convert ntv_value into a mermaid flowchart

        *Parameters*

        - **title**: String (default '') - title of the flowchart
        - **disp**: Boolean (default False) - if true, return a display else return
        a mermaid text diagram
        - **row**: Boolean (default False) - if True, add the node row
        - **leaves**: Boolean (default False) - if True, add the leaf row
        '''
        from base64 import b64encode
        from IPython.display import Image, display

        option = {'title': '', 'disp': False, 'row': False,
                  'leaves': False} | kwargs
        diagram = MermaidConnec.diagram
        link = MermaidConnec._mermaid_link
        ntv = Ntv.obj(ntv_value)
        node_link = {'nodes': [], 'links': []}
        dic_node = {}
        if option['leaves']:
            nodes = [node for node in NtvTree(
                ntv) if not isinstance(node.val, list)]
            dic_node = {node: row for row, node in enumerate(nodes)}
        link(ntv, None, node_link, option['row'], dic_node, None)
        mermaid_json = {option['title'] + ':$flowchart': {
            'orientation': 'top-down',
            'node::': {node[0]: node[1] for node in node_link['nodes']},
            'link::': node_link['links']}}
        if option['disp']:
            return display(Image(url="https://mermaid.ink/img/" +
                                 b64encode(diagram(mermaid_json).encode("ascii")).decode("ascii")))
        return diagram(mermaid_json)

    @staticmethod
    def diagram(json_diag):
        '''create a mermaid code from a mermaid json'''
        ntv = Ntv.obj(json_diag)
        erdiagram = MermaidConnec._er_diagram
        flowchart = MermaidConnec._flowchart
        diag_type = ntv.type_str[1:]
        diag_txt = '---\ntitle: ' + ntv.name + '\n---\n' if ntv.name else ''
        diag_txt += diag_type
        match diag_type:
            case 'erDiagram':
                diag_txt += erdiagram(ntv)
            case 'flowchart':
                diag_txt += flowchart(ntv)
        return diag_txt

    @staticmethod
    def _mermaid_node(ntv, def_typ_str, num, dic_node, ind):
        '''create and return a node'''
        j_name, j_sep, j_type = ntv.json_name(def_typ_str)
        name = ''
        if j_name:
            name += '<b>' + j_name + '</b>\n'
        if j_type:
            name += j_type + '\n'
        if ntv in dic_node:
            num += ' ' + str(dic_node[ntv])
        if num:
            name += '<i>' + num + '</i>\n'
        elif isinstance(ntv, NtvSingle):
            if isinstance(ntv.val, str):
                name += '<i>' + ntv.val + '</i>\n'
            else:
                name += '<i>' + json.dumps(ntv.val) + '</i>\n'
            return [ntv.pointer(index=True, item_idx=ind).json(default='/'), 
                    ['rectangle', name[:-1]]]
        if not name:
            name = '<b>::</b>\n'
        name = name.replace('"', "'")
        return [ntv.pointer(index=True, item_idx=ind).json(default='/'), 
                ['roundedge', name[:-1]]]

    @staticmethod
    def _mermaid_link(ntv, def_typ_str, node_link, row, dic_node, ind):
        '''add nodes and links from ntv in node_link '''
        num = str(len(node_link['nodes'])) if row else ''
        node_link['nodes'].append(MermaidConnec._mermaid_node(
            ntv, def_typ_str, num, dic_node, ind))
        if isinstance(ntv, NtvList):
            for ind, ntv_val in enumerate(ntv):
                MermaidConnec._mermaid_link(ntv_val, ntv.type_str,
                                            node_link, row, dic_node, ind)
                node_link['links'].append(
                    [ntv.pointer(index=True).json(default='/'), 'normalarrow',
                     ntv_val.pointer(index=True, item_idx=ind).json(default='/')])

    @staticmethod
    def _flowchart(ntv):
        orientation = {'top-down': 'TD', 'top-bottom': 'TB',
                       'bottom-top': 'BT', 'right-left': 'RL', 'left-right': 'LR'}
        fcnode = MermaidConnec._fc_node
        fclink = MermaidConnec._fc_link
        flc = Ntv.obj(ntv.val)
        diag_txt = ' ' + orientation[flc['orientation'].val]
        for node in flc['node']:
            diag_txt += fcnode(node)
        for link in flc['link']:
            diag_txt += fclink(link)
        return diag_txt + '\n'

    @staticmethod
    def _fc_link(link):
        link_t = {'normal': ' ---', 'normalarrow': ' -->',
                  'dotted': ' -.-', 'dottedarrow': ' -.->'}
        link_txt = '\n    ' + str(link[0].val) + link_t[link[1].val]
        if len(link) == 4:
            link_txt += '|' + link[3].val + '|'
        return link_txt + ' ' + str(link[2].val)

    @staticmethod
    def _fc_node(node):
        shape_l = {'rectangle': '[', 'roundedge': '(', 'stadium': '(['}
        shape_r = {'rectangle': ']', 'roundedge': ')', 'stadium': '])'}
        return '\n    ' + node.name + shape_l[node[0].val] + '"' + \
               node[1].val.replace('"', "'") + '"' + shape_r[node[0].val]

    @staticmethod
    def _er_diagram(ntv):
        erentity = MermaidConnec._er_entity
        errelation = MermaidConnec._er_relation
        diag_txt = ''
        erd = Ntv.obj(ntv.val)
        for entity in erd['entity']:
            diag_txt += erentity(entity)
        for relation in erd['relationship']:
            diag_txt += errelation(relation)
        return diag_txt

    @staticmethod
    def _er_entity(entity):
        ent_txt = '\n    ' + entity.name + ' {'
        for att in entity:
            ent_txt += '\n        ' + att[0].val + ' ' + att[1].val
            if len(att) > 2:
                if att[2].val in ('PK', 'FK', 'UK'):
                    ent_txt += ' ' + att[2].val
                else:
                    ent_txt += ' "' + att[2].val + '"'
            if len(att) > 3:
                ent_txt += ' "' + att[3].val + '"'
        return ent_txt + '\n    }'

    @staticmethod
    def _er_relation(rel):
        rel_left = {'exactly one': ' ||', 'zero or one': ' |o',
                    'zero or more': ' }o', 'one or more': ' }|'}
        rel_right = {'exactly one': '|| ', 'zero or one': 'o| ',
                     'zero or more': 'o{ ', 'one or more': '|{ '}
        identif = {'identifying': '--', 'non-identifying': '..'}
        rel_txt = '\n    ' + rel[0].val + rel_left[rel[1].val] + \
            identif[rel[2].val] + rel_right[rel[3].val] + rel[4].val
        if len(rel) > 5:
            rel_txt += ' : ' + rel[5].val
        return rel_txt
