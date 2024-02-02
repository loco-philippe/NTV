# -*- coding: utf-8 -*-
"""
***JSON-NTV Package***

Created on Fri Dec 24 15:21:14 2021

@author: philippe@loco-labs.io

This package contains the following classes:

- `NTV.json_ntv.namespace` :
    - `NTV.json_ntv.namespace.Namespace`
    - `NTV.json_ntv.namespace.Datatype`

        
- `NTV.json_ntv.ntv` :
    - `NTV.json_ntv.ntv.NtvSingle`
    - `NTV.json_ntv.ntv.NtvList`
    - `NTV.json_ntv.ntv.Ntv` (abstract class)

- `NTV.json_ntv.ntv_patch` :
    
    - `NTV.json_ntv.ntv_patch.NtvOp`
    - `NTV.json_ntv.ntv_patch.NtvPatch`
    - `NTV.json_ntv.ntv_patch.NtvPointer`

- `NTV.json_ntv.ntv_comment` :
    
    - `NTV.json_ntv.ntv_comment.NtvComment`

- `NTV.json_ntv.ntv_util` :
    
    - `NTV.json_ntv.ntv_util.NtvTree`
    - `NTV.json_ntv.ntv_util.NtvJsonEncoder`
    - `NTV.json_ntv.ntv_util.NtvError`
    - `NTV.json_ntv.ntv_util.NtvConnector` (abstract class)    
    
- `NTV.json_ntv.ntv_connector` :
    
    - `NTV.json_ntv.ntv_connector.NfieldConnec`
    - `NTV.json_ntv.ntv_connector.SfieldConnec`
    - `NTV.json_ntv.ntv_connector.NdatasetConnec`
    - `NTV.json_ntv.ntv_connector.SdatasetConnec`
    - `NTV.json_ntv.ntv_connector.MermaidConnec`
    - `NTV.json_ntv.ntv_connector.CborConnec`
    - `NTV.json_ntv.ntv_connector.ShapelyConnec` 

- `NTV.json_ntv.ntv_validate` :
    
    - `NTV.json_ntv.ntv_validate.Validator`

Note: pandas connector is in another package `ntv-pandas.ntv_pandas.pandas_ntv_connector`      

For more information, see the 
[user guide](https://loco-philippe.github.io/NTV/documentation/user_guide.html) 
or the [github repository](https://github.com/loco-philippe/NTV).

"""
from json_ntv.namespace import Namespace, Datatype, str_type, relative_type, agreg_type
from json_ntv.ntv_patch import NtvOp, NtvPatch, NtvPointer
from json_ntv.ntv_comment import NtvComment
from json_ntv.ntv import Ntv, NtvSingle, NtvList
from json_ntv.ntv_util import NtvTree, NtvJsonEncoder, NtvConnector, NtvError
#from json_ntv.pandas_ntv_connector import DataFrameConnec, SeriesConnec, read_json, to_json, as_def_type
from json_ntv.ntv_connector import from_csv, to_csv
from json_ntv.ntv_connector import MermaidConnec, CborConnec, ShapelyConnec
from json_ntv.ntv_connector import NfieldConnec, SfieldConnec
from json_ntv.ntv_connector import NdatasetConnec, SdatasetConnec

#print('package :', __package__)