# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 22:19:05 2023

@author: a lab in the Air
"""

from observation import Ilist, Iindex, Observation, util
from ntv import Namespace, NtvType
import pdoc 
from pathlib import Path

myscripts = ["../json_ntv/namespace.py", "../json_ntv/ntv.py"]
pdoc.pdoc(*myscripts, output_directory=Path("../../pdoc/NTV"))
#pdoc.pdoc("../json_ntv", output_directory=Path("../../pdoc"))