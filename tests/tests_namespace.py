# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:57:26 2023

@author: Philippe@loco-labs.io

The `NTV.test_namespace` module contains the unit tests (class unittest) for the
`Namespace` and `Type` classes.
"""

import unittest
from json_ntv.namespace import Namespace, DatatypeError, Datatype, _join_type
# from observation import  Ilist


class TestNamespace(unittest.TestCase):
    """tests Namespace class"""

    def test_child_parent(self):
        """tests Namespace"""
        nroot = Namespace()
        nfr = Namespace("fr.", nroot)
        nban = Namespace("BAN.", nfr)
        self.assertEqual(nban.long_name, "fr.BAN.")
        self.assertEqual(nroot.long_name, "")
        self.assertNotEqual(nban, nfr)
        self.assertEqual(nban.is_child(nfr), 1)
        self.assertEqual(nban.is_child(nroot), 2)
        self.assertEqual(nroot.is_parent(nban), 2)
        self.assertEqual(nroot.is_child(nban), -1)

    def test_child_parent_module(self):
        """tests Namespace"""
        nroot = Namespace(module=True)
        # nfr = Namespace('fr.', nroot, module=True)
        nfr = Namespace("fr.", nroot)
        nban = Namespace("BAN.", nfr)
        # nban = Namespace('BAN.', nfr, module=True)
        self.assertEqual(nban.long_name, "fr.BAN.")
        self.assertEqual(nroot.long_name, "")
        self.assertNotEqual(nban, nfr)
        self.assertEqual(nban.is_child(nfr), 1)
        self.assertEqual(nban.is_child(nroot), 2)
        self.assertEqual(nroot.is_parent(nban), 2)
        self.assertEqual(nroot.is_child(nban), -1)

    def test_add(self):
        """tests Namespace"""
        # liststr = ['fr.BAN.test.', 'schemaorg.', 'fr.', 'fr.IRVE.', 'fr.IRVE.',
        liststr = [
            "fr.BAN.test.",
            "fr.",
            "fr.IRVE.",
            "fr.IRVE.",
            "fr.$IRVE.",
            "$a.",
            "$b.$c.",
            "$a.$c.",
        ]
        for nstr in liststr:
            self.assertEqual(Namespace.add(nstr).long_name, nstr)
        liststr = ["$a.c.c.", "fr.$a.b."]
        for nstr in liststr:
            self.assertEqual(Namespace.add(nstr, force=True).long_name, nstr)

    def test_add_ko(self):
        """tests Namespace"""
        liststr = ["fr.BAN.lon", "fr.BAN.teste.", "fr", "fr.BANN.test."]
        for nstr in liststr:
            with self.assertRaises(DatatypeError):
                Namespace.add(nstr)

    def test_user_nsp(self):
        """tests Namespace"""
        liststr = ["fr.$IRVE.", "$a.", "$b.$c.", "$a.$c.", "$a.c.c.", "fr.$a.b."]
        for nstr in liststr:
            self.assertEqual(Namespace.add(nstr).file, None)
            self.assertEqual(Namespace.add(nstr).content, {"type": {}, "namespace": {}})


class TestDatatype(unittest.TestCase):
    """tests Datatype class"""

    def test_self_init(self):
        """tests Datatype"""
        self.assertEqual(Datatype(Datatype("datetime")), Datatype("datetime"))

    def test_add(self):
        """tests Datatype"""
        liststr = [
            "fr.BAN.lon",
            "fr.BAN.$lon",
            "year",
            "fr.reg",
            "fr.BAN.numero",
            "fr.reg",
            "fr.$IRVE.$a",
            "$a.$c",
            "fr.$c",
        ]
        for tstr in liststr:
            self.assertEqual(Datatype(tstr).long_name, tstr)
            self.assertEqual(Datatype(tstr + "[kg]").long_name, tstr + "[kg]")
        liststr = ["$a.c.c.d", "fr.$a.b.d"]
        for tstr in liststr:
            self.assertEqual(Datatype(tstr, force=True).long_name, tstr)
            self.assertEqual(
                Datatype(tstr + "[kg]", force=True).long_name, tstr + "[kg]"
            )

    def test_add_ko(self):
        """tests Datatype"""
        liststr = ["fr.BAN.test", "fr", "fr.BANN.lon"]
        for tstr in liststr:
            with self.assertRaises(DatatypeError):
                Datatype(tstr)

    def test_isin_namespace(self):
        """tests Datatype"""
        lon = Datatype("fr.BAN.lon")
        listnsp = ["fr.BAN.", "fr.", ""]
        # listnotnsp = ['fr.IRVE.', 'fr.BAN.test.', 'schemaorg.']
        listnotnsp = ["fr.IRVE.", "fr.BAN.test."]
        listkonsp = ["fr.BAN.lon", "fr.BAN.teste.", "fr", "fr.BANN.test."]
        res = 0
        self.assertEqual(Datatype("int").isin_namespace(""), 0)
        self.assertEqual(Datatype("int[kg]").isin_namespace(""), 0)
        for nsp in listnsp:
            self.assertEqual(lon.isin_namespace(nsp), res)
            res += 1
        for nsp in listnotnsp:
            self.assertTrue(lon.isin_namespace(nsp) == -1)
        for nsp in listkonsp:
            with self.assertRaises(DatatypeError):
                lon.isin_namespace(nsp)

    def test_org(self):
        """tests Datatype"""
        liststr = ["org.House."]
        for nstr in liststr:
            self.assertEqual(Namespace.add(nstr).long_name, nstr)
        liststr = ["org.House.Country.name"]
        for nstr in liststr:
            self.assertEqual(Datatype(nstr).long_name, nstr)

    def test_join_type(self):
        """tests Datatype"""
        self.assertEqual(
            _join_type("$NTVschema.properties.prop", "property.prop.truc"),
            [
                "$NTVschema.properties.prop.property.prop.truc",
                "$NTVschema.properties.property.prop.truc",
                "$NTVschema.property.prop.truc",
            ],
        )
        self.assertEqual(
            _join_type("$NTVschema.properties.prop", "properties.prop.truc"),
            ["$NTVschema.properties.prop.truc"],
        )
        self.assertEqual(
            _join_type("$NTVschema.properties.prop", "prop.truc"),
            ["$NTVschema.properties.prop.truc", "$NTVschema.prop.truc"],
        )
        self.assertEqual(
            _join_type("$NTVschema.properties.prop", "prop.truc."),
            ["$NTVschema.properties.prop.truc.", "$NTVschema.prop.truc."],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
