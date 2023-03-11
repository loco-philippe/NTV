# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:57:26 2023

@author: Philippe@loco-labs.io

The `NTV.test_namespace` module contains the unit tests (class unittest) for the
`Namespace` and `Type` classes.
"""
import unittest
from namespace import Namespace, NtvTypeError, NtvType

class Test_Namespace(unittest.TestCase):
    
    def test_add(self):
        liststr = ['fr.BAN.test.', 'schemaorg.', 'fr.', 'fr.IRVE.', 'fr.IRVE.',
                   'fr.$IRVE.', '$a.', '$b.$c.', '$a.$c.']
        for nstr in liststr:
            self.assertTrue(Namespace.add(nstr).long_name == nstr)
    
    def test_add_ko(self):
        liststr = ['fr.BAN.lon', 'fr.BAN.teste.', 'fr', 'fr.BANN.test.']
        for nstr in liststr:
            with self.assertRaises(NtvTypeError):
                Namespace.add(nstr)

    def test_user_nsp(self):
        liststr = ['fr.$IRVE.', '$a.', '$b.$c.', '$a.$c.']
        for nstr in liststr:
            self.assertTrue(Namespace.add(nstr).file == None)        
            self.assertTrue(Namespace.add(nstr).content == {'type': {}, 'namespace': {}})        

class Test_NtvType(unittest.TestCase):
    
    def test_add(self):
        liststr = ['fr.BAN.lon', 'year', 'fr.reg', 'fr.BAN.numero', 'fr.reg', 
                   'fr.$IRVE.$a', '$a.$c', 'fr.$c']
        for tstr in liststr:
            self.assertTrue(NtvType.add(tstr).long_name == tstr)
    
    def test_add_ko(self):
        liststr = ['fr.BAN.test', 'fr', 'fr.BANN.lon']
        for tstr in liststr:
            with self.assertRaises(NtvTypeError):
                NtvType.add(tstr)        

    def test_isinNamespace(self):
        lon = NtvType.add("fr.BAN.lon")
        listnsp = ['fr.BAN.', 'fr.', '']
        listnotnsp = ['fr.IRVE.', 'fr.BAN.test.', 'schemaorg.']
        listkonsp = ['fr.BAN.lon', 'fr.BAN.teste.', 'fr', 'fr.BANN.test.']
        res = 0
        for nsp in listnsp:
            self.assertTrue(lon.isin_namespace(nsp) == res)
            res += 1
        for nsp in listnotnsp:
            self.assertTrue(lon.isin_namespace(nsp) == -1)            
        for nsp in listkonsp:
            with self.assertRaises(NtvTypeError):
                lon.isin_namespace(nsp)  
                
if __name__ == '__main__':
    unittest.main(verbosity=2)        