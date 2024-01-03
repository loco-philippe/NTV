# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:57:26 2023

@author: Philippe@loco-labs.io

The `NTV.test_namespace` module contains the unit tests (class unittest) for the
`Namespace` and `Type` classes.
"""
import unittest
from namespace import Namespace, DatatypeError, Datatype
#from observation import  Ilist

class Test_Namespace(unittest.TestCase):
    
    def test_child_parent(self):
        Nroot = Namespace()
        Nfr = Namespace('fr.', Nroot)
        NBAN = Namespace('BAN.', Nfr)     
        self.assertEqual(NBAN.long_name, 'fr.BAN.')
        self.assertEqual(Nroot.long_name, '')
        self.assertNotEqual(NBAN, Nfr)
        self.assertEqual(NBAN.is_child(Nfr), 1)
        self.assertEqual(NBAN.is_child(Nroot), 2)
        self.assertEqual(Nroot.is_parent(NBAN), 2)
        self.assertEqual(Nroot.is_child(NBAN), -1)
        
    def test_child_parent_module(self):
        Nroot = Namespace(module=True)
        #Nfr = Namespace('fr.', Nroot, module=True)
        Nfr = Namespace('fr.', Nroot)
        NBAN = Namespace('BAN.', Nfr)     
        #NBAN = Namespace('BAN.', Nfr, module=True)     
        self.assertEqual(NBAN.long_name, 'fr.BAN.')
        self.assertEqual(Nroot.long_name, '')
        self.assertNotEqual(NBAN, Nfr)
        self.assertEqual(NBAN.is_child(Nfr), 1)
        self.assertEqual(NBAN.is_child(Nroot), 2)
        self.assertEqual(Nroot.is_parent(NBAN), 2)
        self.assertEqual(Nroot.is_child(NBAN), -1)

    def test_add(self):
        #liststr = ['fr.BAN.test.', 'schemaorg.', 'fr.', 'fr.IRVE.', 'fr.IRVE.',
        liststr = ['fr.BAN.test.', 'fr.', 'fr.IRVE.', 'fr.IRVE.',
                   'fr.$IRVE.', '$a.', '$b.$c.', '$a.$c.']
        for nstr in liststr:
            self.assertEqual(Namespace.add(nstr).long_name, nstr)
        liststr = ['$a.c.c.', 'fr.$a.b.']
        for nstr in liststr:
            self.assertEqual(Namespace.add(nstr, force=True).long_name, nstr)
    
    def test_add_ko(self):
        liststr = ['fr.BAN.lon', 'fr.BAN.teste.', 'fr', 'fr.BANN.test.']
        for nstr in liststr:
            with self.assertRaises(DatatypeError):
                Namespace.add(nstr)

    def test_user_nsp(self):
        liststr = ['fr.$IRVE.', '$a.', '$b.$c.', '$a.$c.', '$a.c.c.', 'fr.$a.b.']
        for nstr in liststr:
            self.assertEqual(Namespace.add(nstr).file, None)        
            self.assertEqual(Namespace.add(nstr).content, {'type': {}, 'namespace': {}})        

class Test_Datatype(unittest.TestCase):
    
    def test_self_init(self):
        self.assertEqual(Datatype(Datatype('datetime')), Datatype('datetime'))
        
    def test_add(self):
        liststr = ['fr.BAN.lon', 'fr.BAN.$lon', 'year', 'fr.reg', 'fr.BAN.numero',
                   'fr.reg', 'fr.$IRVE.$a', '$a.$c', 'fr.$c']
        for tstr in liststr:
            self.assertEqual(Datatype.add(tstr).long_name, tstr)
        liststr = ['$a.c.c.d', 'fr.$a.b.d']
        for tstr in liststr:
            self.assertEqual(Datatype.add(tstr, force=True).long_name, tstr)    
    def test_add_ko(self):
        liststr = ['fr.BAN.test', 'fr', 'fr.BANN.lon']
        for tstr in liststr:
            with self.assertRaises(DatatypeError):
                Datatype.add(tstr)        

    def test_isinNamespace(self):
        lon = Datatype.add("fr.BAN.lon")
        listnsp = ['fr.BAN.', 'fr.', '']
        #listnotnsp = ['fr.IRVE.', 'fr.BAN.test.', 'schemaorg.']
        listnotnsp = ['fr.IRVE.', 'fr.BAN.test.']
        listkonsp = ['fr.BAN.lon', 'fr.BAN.teste.', 'fr', 'fr.BANN.test.']
        res = 0
        for nsp in listnsp:
            self.assertEqual(lon.isin_namespace(nsp), res)
            res += 1
        for nsp in listnotnsp:
            self.assertTrue(lon.isin_namespace(nsp) == -1)            
        for nsp in listkonsp:
            with self.assertRaises(DatatypeError):
                lon.isin_namespace(nsp)  
                
if __name__ == '__main__':
    unittest.main(verbosity=2)        