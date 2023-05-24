# -*- coding: utf-8 -*-
"""
Created on Wed May 24 22:25:17 2023

@author: Philippe@loco-labs.io

convert Json_mermaid to mermaid code
"""
from json_ntv.ntv import Ntv

def diagram(json_diag):
    '''create a mermaid code from a mermaid json'''
    ntv = Ntv.obj(json_diag)
    diag_type = ntv.type_str[1:]
    diag_txt = '---\ntitle: ' + ntv.name + '\n---\n' if ntv.name else ''
    diag_txt += diag_type
    match diag_type:
        case 'erDiagram':
            diag_txt += _erDiagram(ntv)
        case 'flowchart':
            diag_txt += _flowchart(ntv)
    return diag_txt

def _flowchart(ntv):
    orientation  = {'top-down' : 'TD', 'top-bottom' : 'TB','bottom-top': 'BT', 'right-left': 'RL', 'left-right': 'LR'}
    fc = Ntv.obj(ntv.val)
    diag_txt = ' ' + orientation[fc['orientation'].val]
    for node in fc['node']:
        diag_txt += _fcNode(node)
    for link in fc['link']:
        diag_txt += _fcLink(link)
    return diag_txt + '\n'    

def _fcLink(link):
    link_t  = {'normal' : ' ---', 'normalarrow': ' -->', 'dotted': ' -.-', 'dottedarrow': ' -.->'}
    link_txt = '\n    ' + str(link[0].val) + link_t[link[1].val]
    if len(link) == 4:
        link_txt += '|' + link[3].val + '|'
    return link_txt + ' ' + str(link[2].val)

def _fcNode(node):
    shape_l  = {'rectangle' : '[', 'roundedge': '(', 'stadium': '(['}
    shape_r  = {'rectangle' : ']', 'roundedge': ')', 'stadium': '])'}
    return '\n    ' + node.name + shape_l[node[0].val] + '"' + node[1].val + '"' + shape_r[node[0].val]

def _erDiagram(ntv):
    diag_txt = ''
    er = Ntv.obj(ntv.val)
    for entity in er['entity']:
        diag_txt += _erEntity(entity)
    for relation in er['relationship']:
        diag_txt += _erRelation(relation)
    return diag_txt

def _erEntity(entity):
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

def _erRelation(rel):
    rel_left  = {'exactly one' : ' ||', 'zero or one': ' |o', 'zero or more': ' }o', 'one or more': ' }|'}
    rel_right = {'exactly one' : '|| ', 'zero or one': 'o| ', 'zero or more': 'o{ ', 'one or more': '|{ '}
    identif   = {'identifying' : '--', 'non-identifying' : '..'}
    rel_txt = '\n    ' + rel[0].val + rel_left[rel[1].val] + identif[rel[2].val] + rel_right[rel[3].val] + rel[4].val
    if len(rel) > 5:
        rel_txt += ' : ' + rel[5].val
    return rel_txt