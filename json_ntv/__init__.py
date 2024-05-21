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

from json_ntv.namespace import Namespace as Namespace
from json_ntv.namespace import Datatype as Datatype
from json_ntv.namespace import str_type as str_type
from json_ntv.namespace import relative_type as relative_type
from json_ntv.namespace import agreg_type as agreg_type
from json_ntv.ntv_patch import NtvOp as NtvOp
from json_ntv.ntv_patch import NtvPatch as NtvPatch
from json_ntv.ntv_patch import NtvPointer as NtvPointer
from json_ntv.ntv_comment import NtvComment as NtvComment
from json_ntv.ntv import Ntv as Ntv
from json_ntv.ntv import NtvSingle as NtvSingle
from json_ntv.ntv import NtvList as NtvList
from json_ntv.ntv_validate import Validator as Validator
from json_ntv.ntv_util import NtvTree as NtvTree
from json_ntv.ntv_util import NtvJsonEncoder as NtvJsonEncoder
from json_ntv.ntv_util import NtvConnector as NtvConnector
from json_ntv.ntv_util import NtvError as NtvError
from json_ntv.ntv_connector import from_csv as from_csv
from json_ntv.ntv_connector import to_csv as to_csv
from json_ntv.ntv_connector import MermaidConnec as MermaidConnec
from json_ntv.ntv_connector import CborConnec as CborConnec
from json_ntv.ntv_connector import ShapelyConnec as ShapelyConnec
from json_ntv.ntv_connector import NfieldConnec as NfieldConnec
from json_ntv.ntv_connector import SfieldConnec as SfieldConnec
from json_ntv.ntv_connector import NdatasetConnec as NdatasetConnec
from json_ntv.ntv_connector import SdatasetConnec as SdatasetConnec

# print('package :', __package__)
