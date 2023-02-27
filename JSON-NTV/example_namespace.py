# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 20:37:06 2023

@author: a179227
"""
from namespace import Namespace
Nroot = Namespace()
Nfr = Namespace('fr.', Nroot)
NBAN = Namespace('BAN.', Nfr)
print(NBAN.cName)
print(Nroot.cName)
print(Namespace.namespaces())