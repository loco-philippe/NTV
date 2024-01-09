# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:31:23 2024

@author: phili
"""

import json
from copy import copy
import pathlib

import json_ntv
from json_ntv.ntv import Ntv
from json_ntv.namespace import from_file

file = pathlib.Path(json_ntv.__file__).parent.parent / "RFC" / "NTV_NTVschema_namespace.ini"
from_file(file, '$openAPI.')


