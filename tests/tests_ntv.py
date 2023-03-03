# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:57:26 2023

@author: Philippe@loco-labs.io

The `NTV.test_ntv` module contains the unit tests (class unittest) for the
`NtvSingle`, `NtvList` and `NtvSet` classes.
"""
import unittest
from ntv import NtvSingle, NtvList, NtvSet, Ntv

class Test_Ntv_creation(unittest.TestCase):
    
    def test_from_obj(self):
        dictstr = {'1NtvSingle': 1, '2NtvSingle': 'test', '3NtvSingle': {'single': 1}, 
                   '4NtvSingle': {'ntv1': {'ntv2': 2}},
                   '5NtvSingle': {'ntv1:fr.reg': {'ntv2:fr.BAN.lon': 2}},
                   '1NtvList': [], '2NtvList': [[4,[5,6]], {'heure':[21,22]}], 
                   '3NtvList': [[4,5], {'heure':21}], '4NtvList': [[4,5], 21], 
                   '5NtvList': [[4,5], [1,2,3]],
                   '6NtvList': {'ntv1::fr.reg':[[4,[5,6]], {'heure':[21,22]}]},
                   '7NtvList': {'ntv1::fr.reg':[4]},
                   '8NtvList': {'ntv1::fr.':[4]},
                   '1NtvSet': {}, '2NtvSet': {'ntv1': 1, 'ntv2':'2'},
                   '3NtvSet': {'ntv3': {'ntv1': 1, 'ntv2':'2'}},
                   '4NtvSet': {'ntv3::fr.reg': {'ntv1': 1, 'ntv2::fr.reg':'2'}},
                   '5NtvSet': {'ntv3::fr.reg': {'ntv1': [1,2], 'ntv2::fr.reg':'2'}}}
        liststr = list(dictstr.values())
        listtyp = list(dictstr.keys())
        for nstr, typ in zip(liststr, listtyp):
            ntv = Ntv.from_obj(nstr)
            self.assertTrue(ntv == Ntv.from_obj(Ntv.to_obj(ntv)))
            self.assertTrue(ntv.__class__.__name__ == typ[1:])

                
if __name__ == '__main__':
    unittest.main(verbosity=2)        