# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:57:26 2023

@author: Philippe@loco-labs.io

The `NTV.test_namespace` module contains the unit tests (class unittest) for the
`Namespace` and `Type` classes.
"""
import unittest
from namespace import Namespace

class Test_Namespace(unittest.TestCase):
    
    def test_add(self):
        liststr = ['fr.BAN.test.', 'schemaorg.', 'fr.', 'fr.IRVE.', 'fr.IRVE.']
        for str in liststr:
            self.assertTrue(Namespace.add(str).cName == str)

    @unittest.expectedFailure
    def test_addko(self):
        liststr = ['fr.BAN.test', 'fr.', 'fr.BANN.test', 'fr.']
        for str in liststr:
            self.assertTrue(Namespace.add(str).cName == str)        
        
if __name__ == '__main__':
    unittest.main(verbosity=2)        