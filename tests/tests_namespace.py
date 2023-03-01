# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:57:26 2023

@author: Philippe@loco-labs.io

The `NTV.test_namespace` module contains the unit tests (class unittest) for the
`Namespace` and `Type` classes.
"""
import unittest
from namespace import Namespace, NtvError, NtvType

class Test_Namespace(unittest.TestCase):
    
    def test_add(self):
        liststr = ['fr.BAN.test.', 'schemaorg.', 'fr.', 'fr.IRVE.', 'fr.IRVE.']
        for nstr in liststr:
            self.assertTrue(Namespace.add(nstr).long_name == nstr)
    
    def test_add_ko(self):
        liststr = ['fr.BAN.lon', 'fr.BAN.test', 'fr', 'fr.BANN.test']
        for nstr in liststr:
            with self.assertRaises(NtvError):
                Namespace.add(nstr)

class Test_NtvType(unittest.TestCase):
    
    def test_add(self):
        liststr = ['fr.BAN.lon', 'year', 'fr.reg', 'fr.BAN.numero', 'fr.reg']
        for tstr in liststr:
            self.assertTrue(NtvType.add(tstr).long_name == tstr)
    
    def test_add_ko(self):
        liststr = ['fr.BAN.test', 'fr', 'fr.BANN.lon']
        for tstr in liststr:
            with self.assertRaises(NtvError):
                NtvType.add(tstr)        

if __name__ == '__main__':
    unittest.main(verbosity=2)        