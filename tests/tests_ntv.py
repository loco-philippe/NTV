# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:57:26 2023

@author: Philippe@loco-labs.io

The `NTV.test_ntv` module contains the unit tests (class unittest) for the
`NtvSingle`, `NtvList` and `NtvSet` classes.
"""
import unittest
import datetime
import csv
from itertools import product
import json

from json_ntv import NtvSingle, NtvList, Ntv, NtvError, from_csv, to_csv, NtvComment
from json_ntv.ntv_util import NtvUtil
from json_ntv import agreg_type, NtvTree, NtvConnector, NtvOp, NtvPatch, Datatype
import ntv_pandas as npd #used to update NtvConnector.dic_connec()
from shapely import geometry
from jsonpointer import resolve_pointer

class Test_Ntv_fast(unittest.TestCase):

    def test_from_obj_repr(self):
        list_repr = [[1, "s"],
                     [{"truc":  1}, "sN"],
                     [{":point": 1}, "sT"],
                     [[1, 2], {"l": ["s", "s"]}],
                     [{"truc": [1, 2]}, {"lN": ["s", "s"]}],
                     [{":point": [1, 2]}, "sT"],
                     [{"truc:":  [1, 2]}, "sN"],
                     [{":": [1, 2]}, "s"],
                     [{"::point": [[1, 2], [3, 4]]}, {"lT": ["sT", "sT"]}],
                     [{"::array": [[1, 2], [3, 4]]}, {"lT": ["sT", "sT"]}],
                     [{"::array": [{'a': 3, 'e':5}, {'a': 4, 'e':6}]}, {"lT": ["sT", "sT"]}],
                     [{"a": 2}, "sN"],
                     [{":point": {"a": 2}}, "sT"]
                     ]
        for test in list_repr:
            #print(test)
            self.assertEqual(Ntv.fast(test[0]).to_repr(False, False, False, 10), test[1])
            self.assertEqual(json.loads(repr(Ntv.fast(test[0]))), test[0])
        list_repr = [[{"truc:":  1}, "sN"],
                     [{":": 1}, "s"],
                     [{"::": [1, 2]}, {"l": ["s", "s"]}],
                     [{"::": {"a": 2}}, {"l": ["sN"]}],
                     [{"::": [[1, 2], [3, 4]]},
                         {"l": [{"l": ["s", "s"]}, {"l": ["s", "s"]}]}],
                     [{"truc": {"a": 2}}, {'lN': ['sN']}], #"sN"],
                     [{"truc:": {"a": 2}}, "sN"],
                     [{":": {"a": 2}}, "s"]
                     ]
        for test in list_repr:
            #print(test)
            self.assertEqual(Ntv.fast(test[0]).to_repr(False, False, False, 10), test[1])
            
    def test_from_obj_json_txt(self):
        dictstr = [['NtvSingle', 'null'],
                   ['NtvSingle', '{"none": null}'],
                   ['NtvSingle', '1'],
                   ['NtvSingle', '"test"'],
                   ['NtvSingle', '{"Single": 1}'],
                   ['NtvSingle', '{"Ntv1:ntv": {"Ntv2": 2}}'],
                   ['NtvSingle', '{"Ntv1": true}'],
                   ['NtvSingle', 'true'],
                   ['NtvSingle', '{"Ntv1:array": [1, 2]}'],
                   ['NtvSingle', '"{ner"'],
                   ['NtvList', '{}'],
                   ['NtvList', '[{" a": 2}]'],
                   #['NtvList', '{"test": [{"a": 2}]}']
                   ['NtvList', '{"test": {"a": 2}}'],
                   ['NtvList', '{"test": [{"a": 1, "b": 2}]}']
                   ]

        lis = list(zip(*dictstr))
        liststr = list(lis[1])
        listtyp = list(lis[0])
        for nstr, typ in zip(liststr, listtyp):
            #print('av', nstr, typ)
            ntv = Ntv.fast(nstr)
            #print('ap', nstr, typ)
            self.assertEqual(nstr, ntv.to_fast(encoded=True))
            self.assertTrue(ntv.__class__.__name__ == typ)
            self.assertEqual(ntv, Ntv.fast(ntv.to_fast()))

    def test_from_obj_json(self):
        dictstr = [['NtvSingle', None],
                   ['NtvSingle', {'none': None}],
                   ['NtvSingle', 1],
                   ['NtvSingle', 'test'],
                   ['NtvSingle', {'Single': 1}],
                   ['NtvSingle', {'Ntv1:ntv': {'Ntv2': 2}}],
                   #['NtvSingle', {'Ntv1': {'Ntv2': 2}}],
                   ['NtvList', {'Ntv1': {'Ntv2': 2}}],
                   ['NtvSingle', {'Ntv1:fr.reg': {'Ntv2:fr.BAN.lon': 2}}],
                   ['NtvSingle', {'Ntv1': True}],
                   ['NtvSingle', True],
                   ['NtvSingle', {'Ntv1:array': [1, 2]}],
                   ['NtvSingle', {'Ntv1:dat': [1, 2]}],
                   ['NtvSingle', '{ner'],
                   ['NtvSingle', {':$point': {'a': [1, 2], 'b': [3, 4]}}],
                   ['NtvSingle', {
                       ':': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]}],
                   ['NtvList', [[4, [5, 6]], {'heure': [21, 22]}]],
                   ['NtvList', [[4, 5], {'heure': 21}]],
                   ['NtvList', [[4, 5], 21]],
                   ['NtvList', [[4, 5], [1, 2, 3]]],
                   ['NtvList', {'Ntv1::fr.reg': [
                       [4, [5, 6]], {'heure': [21, 22]}]}],
                   ['NtvList', {'Ntv1::fr.reg': [4]}],
                   ['NtvList', {'Ntv1::fr.': [4]}],
                   ['NtvList', {'cities::point': [[2.1, 40.3], [2.1, 40.3]]}],
                   ['NtvList', {}],
                   ['NtvList', {'Ntv1': 1, 'Ntv2': '2'}],
                   ['NtvList', {'Ntv3': {'Ntv1': 1, 'Ntv2': '2'}}],
                   ['NtvList', [{" a": 2}]],
                   #['NtvList', {"test": [{"a": 2}]}]
                   ['NtvList', {"test": {"a": 2}}]
                   ]

        lis = list(zip(*dictstr))
        liststr = list(lis[1])
        listtyp = list(lis[0])
        for nstr, typ in zip(liststr, listtyp):
            #print('av', nstr, typ)
            ntv = Ntv.fast(nstr)
            #print('ap', nstr, typ)
            self.assertEqual(nstr, ntv.to_fast())
            self.assertTrue(ntv.__class__.__name__ == typ)
            self.assertEqual(ntv, Ntv.fast(ntv.to_obj()))

    def test_equivalence(self):
        str2 = [({'Ntv1': datetime.date(2021, 2, 1)}, {'Ntv1:date': datetime.date(2021, 2, 1)}),
                ({'Ntv2': [datetime.date(2020, 2, 4), [datetime.date(2020, 3, 4), datetime.date(2020, 4, 4)]]},
                 {'Ntv2:date': [datetime.date(2020, 2, 4), [datetime.date(2020, 3, 4), datetime.date(2020, 4, 4)]]}),
                ]
        for js1, js2 in str2:
            self.assertEqual(Ntv.fast(js1).to_json_ntv(), Ntv.fast(js1).to_json_ntv())
            
    def test_from_obj_fast(self):
        self.assertNotEqual(Ntv.fast({':': NtvSingle(1, 'test')}), Ntv.fast(NtvSingle(1, 'test')))
        dictstr2 = [
                   #['NtvSingle', {':': NtvSingle(1, 'test')}, {
                   #    ':ntv': {'test': 1}}],
                   ['NtvSingle', {'set': NtvList([{'l1': 21}, {'l2': [2, 3]}])},
                    {'set:ntv': {'l1': 21, 'l2:': [2, 3]}}],
                   ['NtvSingle', {'lis:': NtvList([1, 2, 3])}, {
                       'lis:ntv': [1, 2, 3]}],
                   ['NtvSingle', {'Ntv1:date': datetime.date(2021, 2, 1)},
                    {'Ntv1:date': '2021-02-01'}],
                   ['NtvSingle', {'Ntv1:date': datetime.date(2021, 2, 1)},
                    {'Ntv1:date': '2021-02-01'}],
                   ['NtvSingle', {'Ntv2:': [datetime.date(2020, 2, 4), 
                                                [datetime.date(2020, 3, 4), 
                                                 datetime.date(2020, 4, 4)]]},
                    {'Ntv2:date': ['2020-02-04', ['2020-03-04', '2020-04-04']]}],
                   ['NtvSingle', {'Ntv2:date': [datetime.date(2020, 2, 4), 
                                                {'a': datetime.date(2020, 3, 4), 
                                                 'b': datetime.date(2020, 4, 4)}]},
                    {'Ntv2:date': ['2020-02-04', {'a': '2020-03-04', 'b': '2020-04-04'}]}],
                   ['NtvSingle', datetime.date(2021, 2, 1), {
                       ':date': '2021-02-01'}],
                   ['NtvSingle', {'set:': NtvList([{'l1': 21}, {'l2': datetime.date(2021, 2, 1)}])},
                    {'set:ntv': {'l1': 21, 'l2:date': '2021-02-01'}}],
                   ['NtvList', [[4, [5, 6]], {'heure': [datetime.time(10, 25, 10), 22]}],
                    [[4, [5, 6]], {'heure': [{':time': '10:25:10'}, 22]}]],
                   ['NtvList', [[4, [5, 6]], {'heure': [datetime.time(10, 25, 10),
                                                        geometry.point.Point((3, 4))]}],
                    [[4, [5, 6]], {'heure': [{':time': '10:25:10'}, {':point': [3.0, 4.0]}]}]],
                   ['NtvList', [], {}],
                   ['NtvList', {'::': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]},
                    {'paris': [2.1, 40.3], 'lyon': [2.1, 40.3]}],
                   ['NtvList', {'Ntv3::fr.reg': {'Ntv1': 1, 'Ntv2:fr.reg': '2'}},
                    {'Ntv3::fr.reg': {'Ntv1': 1, 'Ntv2': '2'}}],
                   ['NtvList', {'Ntv3::fr.reg': {'Ntv1': [1, 2], 'Ntv2:fr.reg': '2'}},
                    {'Ntv3::fr.reg': {'Ntv1': [1, 2], 'Ntv2': '2'}}],
        ]
        lis = list(zip(*dictstr2))
        listres = list(lis[2])
        liststr = list(lis[1])
        listtyp = list(lis[0])
        for nstr, typ, nres in zip(liststr, listtyp, listres):
            #print('av', nstr, typ)
            ntv = Ntv.fast(nstr)
            #print('ap', nstr, typ)
            self.assertTrue(ntv.__class__.__name__ == typ)
            self.assertEqual(ntv.to_obj_ntv(), Ntv.fast(ntv.to_fast()).to_obj_ntv())
            self.assertEqual(ntv.to_json_ntv(), Ntv.obj(nstr))
            self.assertEqual(ntv.to_json_ntv().to_obj_ntv(), ntv.to_obj_ntv())
            
    def test_to_json_ntv_to_obj_ntv(self):
        js_obj = [{'test': [datetime.date(2020, 1, 2), 45, {'paris': geometry.Point(4,5)}]},
                  {'test': [datetime.date(2020, 1, 2), 45, {'paris': geometry.Point(4,5), 
                            'dates': [datetime.date(2021, 1, 2), datetime.date(2022, 1, 2)]}]}]
        for js in js_obj:
            self.assertEqual(Ntv.fast(js).to_json_ntv(), Ntv.obj(js))
            self.assertEqual(Ntv.fast(js).to_json_ntv().to_obj_ntv(), Ntv.fast(js).to_obj_ntv() )
        
class Test_Ntv_creation(unittest.TestCase):

    def test_from_obj_repr(self):
        list_repr = [[1, "s"],
                     [{"truc":  1}, "sN"],
                     [{":point": 1}, "sT"],
                     [[1, 2], {"l": ["s", "s"]}],
                     [{"truc": [1, 2]}, {"lN": ["s", "s"]}],
                     [{":point": [1, 2]}, "sT"],
                     [{"truc:":  [1, 2]}, "sN"],
                     [{":": [1, 2]}, "s"],
                     [{"::point": [[1, 2], [3, 4]]}, {"lT": ["sT", "sT"]}],
                     [{"::array": [[1, 2], [3, 4]]}, {"lT": ["sT", "sT"]}],
                     [{"::array": [{'a': 3, 'e':5}, {'a': 4, 'e':6}]}, {"lT": ["sT", "sT"]}],
                     [{"a": 2}, "sN"],
                     [{":point": {"a": 2}}, "sT"]
                     ]
        for test in list_repr:
            #print(test)
            self.assertEqual(Ntv.from_obj(test[0]).to_repr(False, False, False, 10), test[1])
            self.assertEqual(json.loads(repr(Ntv.fast(test[0]))), test[0])
        list_repr = [[{"truc:":  1}, "sN"],
                     [{":": 1}, "s"],
                     [{"::": [1, 2]}, {"l": ["s", "s"]}],
                     [{"::": {"a": 2}}, {"l": ["sN"]}],
                     [{"::": [[1, 2], [3, 4]]},
                         {"l": [{"l": ["s", "s"]}, {"l": ["s", "s"]}]}],
                     [{"truc": {"a": 2}}, {'lN': ['sN']}], # "sN"],
                     [{"truc:": {"a": 2}}, "sN"],
                     [{":": {"a": 2}}, "s"]
                     ]
        for test in list_repr:
            #print(test)
            self.assertEqual(Ntv.from_obj(test[0]).to_repr(False, False, False, 10), test[1])
            
    def test_from_obj_ko(self):
        liststr = [{"::": 1}]
        for nstr in liststr:
            with self.assertRaises(NtvError):
                Ntv.from_obj(nstr)

    def test_from_att(self):
        self.assertEqual(repr(Ntv.obj(([[1, 2], [3, 4]], None, 'point', 'single'))), 
                         '{":point": [[1, 2], [3, 4]]}')
        self.assertEqual(repr(Ntv.obj(([[1, 2], [3, 4]], None, 'point', 'list'))),
                         '{"::point": [[1, 2], [3, 4]]}')

    def test_from_obj_json_txt(self):
        dictstr = [['NtvSingle', 'null'],
                   ['NtvSingle', '{"none": null}'],
                   ['NtvSingle', '1'],
                   ['NtvSingle', '"test"'],
                   ['NtvSingle', '{"Single": 1}'],
                   ['NtvSingle', '{"Ntv1:ntv": {"Ntv2": 2}}'],
                   ['NtvSingle', '{"Ntv1": true}'],
                   ['NtvSingle', 'true'],
                   ['NtvSingle', '{"Ntv1:array": [1, 2]}'],
                   ['NtvSingle', '"{ner"'],
                   ['NtvList', '{}'],
                   ['NtvList', '[{" a": 2}]'],
                   #['NtvList', '{"test": [{"a": 2}]}']
                   ['NtvList', '{"test": {"a": 2}}'],
                   ['NtvList', '{"test": [{"a": 1, "b": 2}]}']
                   ]

        lis = list(zip(*dictstr))
        liststr = list(lis[1])
        listtyp = list(lis[0])
        for nstr, typ in zip(liststr, listtyp):
            #print('av', nstr, typ)
            ntv = Ntv.obj(nstr)
            #print('ap', nstr, typ)
            self.assertEqual(nstr, ntv.to_obj(encoded=True))
            self.assertTrue(ntv.__class__.__name__ == typ)
            self.assertEqual(ntv, Ntv.obj(Ntv.to_obj(ntv)))
            self.assertEqual(ntv, Ntv.obj(ntv.to_obj()))

    def test_single(self):
        self.assertEqual(Ntv.obj({'b': {"a": 2}}).to_obj(), {'b': {"a": 2}})
        self.assertEqual(Ntv.obj([{"a": 2}]).to_obj(), [{"a": 2}])
        self.assertEqual(Ntv.obj([2]).to_obj(), [2])
        self.assertEqual(Ntv.obj({'::': {"a": 2}}).to_obj(), [{"a": 2}])
        self.assertEqual(Ntv.obj({'::': {':json':2}}).to_obj(), [2])
        self.assertEqual(Ntv.obj({'::': {':':2}}).to_obj(), [2])

    def test_separator(self):
        sings =[{'test::string:int32': [2,21]}, 
                {'test::string::int32': [2,21]},
                {'test:string:int32': [2,21]},
                {'test:string::int32': [2,21]},
                {'::string:int32': [2,21]},
                {':string:int32': [2,21]},
                {':int32': [2,21]},
                {'::int32': [2,21]}]
        for sing in sings:
            self.assertEqual(Ntv.obj(sing).to_obj(), sing)
            self.assertEqual(Ntv.obj(sing).type_str, 'int32')
            
    def test_from_obj_json(self):
        dictstr = [['NtvSingle', None],
                   ['NtvSingle', {'none': None}],
                   ['NtvSingle', 1],
                   ['NtvSingle', 'test'],
                   ['NtvSingle', {'Single': 1}],
                   ['NtvSingle', {'Ntv1:ntv': {'Ntv2': 2}}],
                   ['NtvList', {'Ntv1': {'Ntv2': 2}}],
                   ['NtvSingle', {'Ntv1:fr.reg': {'Ntv2:fr.BAN.lon': 2}}],
                   ['NtvSingle', {'Ntv1': True}],
                   ['NtvSingle', True],
                   ['NtvSingle', {'Ntv1:array': [1, 2]}],
                   ['NtvSingle', {'Ntv1:dat': [1, 2]}],
                   ['NtvSingle', '{ner'],
                   ['NtvSingle', {':$point': {'a': [1, 2], 'b': [3, 4]}}],
                   ['NtvSingle', {
                       ':': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]}],
                   ['NtvList', [[4, [5, 6]], {'heure': [21, 22]}]],
                   ['NtvList', [[4, 5], {'heure': 21}]],
                   ['NtvList', [[4, 5], 21]],
                   ['NtvList', [[4, 5], [1, 2, 3]]],
                   ['NtvList', {'Ntv1::fr.reg': [
                       [4, [5, 6]], {'heure': [21, 22]}]}],
                   ['NtvList', {'Ntv1::fr.reg': [4]}],
                   ['NtvList', {'Ntv1::fr.': [4]}],
                   ['NtvList', {'cities::point': [[2.1, 40.3], [2.1, 40.3]]}],
                   ['NtvList', {}],
                   ['NtvList', {'Ntv1': 1, 'Ntv2': '2'}],
                   ['NtvList', {'Ntv3': {'Ntv1': 1, 'Ntv2': '2'}}],
                   ['NtvList', [{" a": 2}] ],
                   #['NtvList', {"test": [{"a": 2}]}]
                   ['NtvList', {"test": {"a": 2}}],
                   ['NtvList', {'::json': [[1, 2], [3, 4]]}],
                   ['NtvList', {'::json': [1, 2]}],
                   ['NtvList', [{":": [1, 2]}, {":": [3, 4]}]]
                   ]

        lis = list(zip(*dictstr))
        liststr = list(lis[1])
        listtyp = list(lis[0])
        for nstr, typ in zip(liststr, listtyp):
            #print('av', nstr, typ)
            ntv = Ntv.obj(nstr)
            #print('ap', nstr, typ)
            self.assertEqual(nstr, ntv.to_obj())
            self.assertTrue(ntv.__class__.__name__ == typ)
            self.assertEqual(ntv, Ntv.obj(Ntv.to_obj(ntv)))
            self.assertEqual(ntv, Ntv.obj(ntv.to_obj()))

    def test_from_obj_obj(self):
        self.assertEqual(NtvSingle(datetime.date(2021, 10, 1), None, Datatype('datetime')).type_str, 'date')
        self.assertNotEqual(Ntv.obj({':': NtvSingle(1, 'test')}), Ntv.obj(NtvSingle(1, 'test')))

        dictstr2 = [
                   ['NtvSingle', {':': NtvSingle(1, 'test')}, {':ntv': {'test': 1}}],
                   ['NtvSingle', {'set': NtvList([{'l1': 21}, {'l2': [2, 3]}])},
                    #{'set:ntv': {'l1': 21, 'l2': [2, 3]}}],
                    {'set:ntv': {'l1': 21, 'l2:': [2, 3]}}],
                   ['NtvSingle', {'lis:': NtvList([1, 2, 3])}, {
                       'lis:ntv': [1, 2, 3]}],
                   ['NtvSingle', {'Ntv1': datetime.date(2021, 2, 1)},
                    {'Ntv1:date': '2021-02-01'}],
                   ['NtvSingle', {'Ntv1:date': datetime.date(2021, 2, 1)},
                    {'Ntv1:date': '2021-02-01'}],
                   ['NtvSingle', datetime.date(2021, 2, 1), {
                       ':date': '2021-02-01'}],
                   ['NtvSingle', {'set:': NtvList([{'l1': 21}, {'l2': datetime.date(2021, 2, 1)}])},
                    {'set:ntv': {'l1': 21, 'l2:date': '2021-02-01'}}],
                   ['NtvSingle', {'Ntv2:date': [datetime.date(2020, 2, 4), 
                       [datetime.date(2020, 3, 4), datetime.date(2020, 4, 4)]]},
                               {'Ntv2:date': ['2020-02-04', ['2020-03-04', '2020-04-04']]}],
                   ['NtvSingle', {'Ntv2:date': [datetime.date(2020, 2, 4), 
                        {'a': datetime.date(2020, 3, 4), 'b': datetime.date(2020, 4, 4)}]},
                    {'Ntv2:date': ['2020-02-04', {'a': '2020-03-04', 'b': '2020-04-04'}]}],
                   ['NtvList', [[4, [5, 6]], {'heure': [datetime.time(10, 25, 10), 22]}],
                    [[4, [5, 6]], {'heure': [{':time': '10:25:10'}, 22]}]],
                   ['NtvList', [[4, [5, 6]], {'heure': [datetime.time(10, 25, 10),
                                                        geometry.point.Point((3, 4))]}],
                    [[4, [5, 6]], {'heure': {':time': '10:25:10', ':point': [3.0, 4.0]}}]],
                   ['NtvList', [], {}],
                   ['NtvList', {'::': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]},
                    {'paris': [2.1, 40.3], 'lyon': [2.1, 40.3]}],
                   ['NtvList', {'Ntv3::fr.reg': {'Ntv1': 1, 'Ntv2:fr.reg': '2'}},
                    {'Ntv3::fr.reg': {'Ntv1': 1, 'Ntv2': '2'}}],
                   ['NtvList', {'Ntv3::fr.reg': {'Ntv1': [1, 2], 'Ntv2:fr.reg': '2'}},
                    {'Ntv3::fr.reg': {'Ntv1': [1, 2], 'Ntv2': '2'}}],
        ]
        
        lis = list(zip(*dictstr2))
        listres = list(lis[2])
        liststr = list(lis[1])
        listtyp = list(lis[0])
        for nstr, typ, nres in zip(liststr, listtyp, listres):
            #print('av', nstr, typ)
            ntv = Ntv.obj(nstr)
            ntvf = Ntv.fast(nstr).to_json_ntv()
            #print('ap', nstr, typ)
            #print(ntv, ntv.val, ntv.name, ntv.type_str)
            #print(Ntv.obj(Ntv.to_obj(ntv)))
            self.assertTrue(ntv.__class__.__name__ == typ)
            self.assertEqual(ntv, Ntv.obj(Ntv.to_obj(ntv)))
            self.assertEqual(ntv, ntvf)
            self.assertEqual(nres, ntv.to_obj())

    def test_to_obj(self):
        nstr = {'cities': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]}
        nstr2 = {'cities':  {'paris': [2.1, 40.3],   'lyon': [2.1, 40.3]}}
        nstr3 = {'cities': [[2.1, 40.3],           [2.1, 40.3]]}
        self.assertTrue(Ntv.from_obj(nstr).to_obj(simpleval=True) ==
                        Ntv.from_obj(nstr2).to_obj(simpleval=True) ==
                        Ntv.from_obj(nstr3).to_obj(simpleval=True) ==
                        [[2.1, 40.3], [2.1, 40.3]])
        self.assertEqual(Ntv.obj(nstr), Ntv.obj(nstr2))
        self.assertEqual(Ntv.obj(nstr).to_obj(json_array=True), nstr)
        self.assertEqual(Ntv.obj(nstr).to_obj(json_array=False), nstr2)
        self.assertEqual(Ntv.obj({'paris:point': 'null'}).to_obj(format='obj'),
                         {'paris:point': None})

class Test_Ntv_compare(unittest.TestCase):

    def test_lt(self):
        self.assertTrue(Ntv.obj(False) > Ntv.obj(None))
        self.assertTrue(Ntv.obj(None) < Ntv.obj(False))
        self.assertTrue(Ntv.obj(False) < Ntv.obj(True))
        self.assertTrue(Ntv.obj(1) < Ntv.obj(2))
        self.assertFalse(Ntv.obj(2) < Ntv.obj(2))
        self.assertFalse(Ntv.obj(2) < Ntv.obj('er'))
        self.assertFalse(Ntv.obj(2) < Ntv.obj(None))
        self.assertTrue(Ntv.obj(2) < Ntv.obj({'test':3}))
        self.assertFalse(Ntv.obj(2) < Ntv.obj({'test':1}))
        self.assertFalse(Ntv.obj({'test':2}) < Ntv.obj({'test':1}))
        self.assertTrue(Ntv.obj({'test':2, 'r':4}) < Ntv.obj({'test':3}))
        self.assertTrue(Ntv.obj({'test':2, 'r':4}) < Ntv.obj({'test':2, 'res':5}))
        self.assertFalse(Ntv.obj({'test':2, 'r':4}) < Ntv.obj({'test':2, 'res':1}))
        self.assertFalse(Ntv.obj({'test':2, 'r':4}) < Ntv.obj({'test':2}))
        self.assertTrue(Ntv.obj({'test':2}) < Ntv.obj({'test':2, 'res':1}))
        self.assertTrue(Ntv.obj({'test':2, 'tr':4}) > Ntv.obj({'test':{'truc':2}}))
        self.assertTrue(Ntv.obj([1,4]) < Ntv.obj({'test':{'truc':2}}))
        self.assertTrue(Ntv.obj([1,4]) < Ntv.obj([[2]]))
        
class Test_Ntv_pointer(unittest.TestCase):
    
    def test_pointer_RFC(self):
        ntv = Ntv.obj({'a': [1, [2, 3, 4], [5, 6]], 
                       'b': 'ert',
                       'dic': {'v1': 'val1', 'v2': 'val2'}})
        self.assertTrue(ntv['#/a'] == ntv['#/0'] == ntv[0] == ntv['a'])
        self.assertTrue(ntv['#/a/1/1'] == ntv['#/0/1/1'] == ntv[0][1][1] == ntv['a'][1][1])
        self.assertTrue(ntv['#/dic/v1'] == ntv['#/2/0'] == ntv[2][0] == ntv['dic']['v1'])
        js = { "foo": ["bar", "baz"], " ": 0, "a/b": 1, "c%d": 2,
               "e^f": 3, "g|h": 4, "i\\j": 5, "k\"l": 6, "m~n": 7 }
        ntv = Ntv.obj(js)
        self.assertTrue(ntv['#/foo/0'] == ntv[0][0])
        self.assertTrue(ntv['#/a~0b'] == ntv[2])
        self.assertTrue(ntv['#/m~n'] == ntv[8])

    def test_json_pointer(self):
        ntv = Ntv.obj({'a': [1, [2, 3, 4], [5, 6]], 
                       'b': 'ert',
                       'dic': {'v1': 'val1', 'v2': 'val2'},
                       'dicsingle': {'sing': 1}})
        pointers = ['/a/1/1', '', '/dicsingle', '/dicsingle/sing']
        self.assertTrue(ntv['#/dicsingle/0'] == ntv['#/dicsingle/sing'] ==
                        ntv['dicsingle'][0] == ntv['dicsingle']['sing'])
        for pointer in pointers:
            #self.assertEqual(pointer, ntv[pointer].json_pointer())
            self.assertEqual(pointer, str(ntv['#'+pointer].pointer()))

    def test_pointer(self):
        a = Ntv.obj({'test': {'t1': 1, 't2': 2, 't3': [3, 4]}})
        self.assertTrue(a.parent is None)
        self.assertEqual(list(a.pointer()), ['test'])
        self.assertEqual(str(a.pointer()), 'test')
        self.assertEqual(list(a['t3'].pointer(index=True))[1], 2)
        self.assertEqual(str(a['t3'].pointer(True)), '0/2')
        self.assertEqual(a['t3'][0].parent.parent, a)
        self.assertEqual(list(a['t3'][0].pointer(index=True)), [0, 2, 0])
        self.assertEqual(str(a['t3'][0].pointer(index=True)), '0/2/0')

    def test_json_ntv_pointer(self):
        examples = [ {'data': {'a': 1, 'test': 'ok'}, 'pointer': '/test', 'canonical': '/1'},
                     {'data': [{'a': 1}, 'ok'],       'pointer': '/1',    'canonical': '/1'},
                     {'data': {'a': 1, '1': 'ok'},    'pointer': '/1',    'canonical': '/1'},
                     {'data': ['a', 'ok'],            'pointer': '/1',    'canonical': '/1'}]
        for example in examples:
            data      = example['data']
            pointer   = example['pointer']
            canonical = example['canonical']
        
            ntv = Ntv.obj(data)
            self.assertEqual(ntv['#'+canonical], ntv['#'+pointer])
            self.assertEqual(ntv['#'+pointer].val, 'ok')
            self.assertEqual(ntv['#'+pointer].val, resolve_pointer(data, pointer))

    def test_conversion_json_ntv_pointer(self):
        examples = [ {'data': {'test': 'ok'},                    'pointer': 'test' ,     'pointer json': '/test'},
                     {'data': [1, {'test': 'ok'}],               'pointer': '/test',     'pointer json': '/1/test'},
                     {'data': [1, [2, {'test': 'ok'}]],          'pointer': '/1/test',   'pointer json': '/1/1/test'},
                     {'data': [1, {'a': {'test': 'ok'}}],        'pointer': '/a/test',   'pointer json': '/1/a/test'},
                     {'data': {'b': [1, {'a': {'test': 'ok'}}]}, 'pointer': 'b/a/test',  'pointer json': '/b/1/a/test'},
                     {'data': {'b': [1, {'a': {'test': 'ok'}}]}, 'pointer': '0/a/test',  'pointer json': '/b/1/a/test'},
                     {'data': {'b': {'a': 1, 'test': 'ok'}},     'pointer': 'b/test',    'pointer json': '/b/test'},
                     {'data': {'a': 1, 'test': 'ok'},            'pointer': '/test',     'pointer json': '/test'},
                     {'data': [1, {'a': {'test': [1,'ok']}}],    'pointer': '/a/test/1', 'pointer json': '/1/a/test/1'},
                     {'data': {'b': [1, {'a': {'test': 'ok'}}]}, 'pointer': 'b/a/test',  'pointer json': '/b/1/a/test'}]
        for example in examples:
            data         = example['data']
            pointer      = example['pointer']
            pointer_json = example['pointer json']
            unique_root  = len(data) == 1
        
            ntv = Ntv.obj(data)
            self.assertEqual(ntv['#'+pointer].val, resolve_pointer(data, pointer_json))
            self.assertEqual(ntv['#'+pointer].pointer(), 
                             ntv['#'+NtvUtil.to_ntvpointer(pointer_json, unique_root)].pointer())
            if pointer[0] != '0':
                self.assertEqual(NtvUtil.to_ntvpointer(pointer_json, unique_root), pointer)

    def test_type_ntv_pointer(self):
        ntv = Ntv.obj([{':int32': 4}, {':int64': 8}, {':int64':12}])
        self.assertEqual(str(ntv[1].pointer()), '/1')
        self.assertEqual(str(ntv[2].pointer()), '/2')
        self.assertEqual(ntv[1].json_name_str, ntv[2].json_name_str)               
        
class Test_Ntv_tabular(unittest.TestCase):

    def test_tab(self):
        tab = Ntv.obj({'index':           [1, 2, 3],
                       'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21'],
                       'value':           [10, 20, 30],
                       'value32::int32':  [10, 20, 30],
                       'res':             {'res1': 10, 'res2': 20, 'res3': 30},
                       'coord::point':    [[1, 2], [3, 4], [5, 6]],
                       'names::string':   ['john', 'eric', 'judith']})
        self.assertEqual(tab[1][2], tab['dates::datetime'][2],
                         Ntv.obj({":datetime": "2022-01-21"}))
        self.assertEqual(tab[4][2], tab['res']['res3'], Ntv.obj(30))

    def test_tab_field_pandas_ilist_Iindex(self):
        field = Ntv.obj({':field':
                         {'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21']}})
        tab = Ntv.obj({':tab':
                       {'index':           [1, 2, 3],
                        'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21'],
                        'value':           [10, 20, 30],
                        'value32::int32':  [10, 20, 30],
                        'res':             {'res1': 10, 'res2': 20, 'res3': 30},
                        'coord::point':    [[1, 2], [3, 4], [5, 6]],
                        'names::string':   ['john', 'eric', 'judith']}})
        sr = field.to_obj(format='obj', dicobj={
                          'field': 'SeriesConnec'})
        self.assertTrue(sr.equals(Ntv.obj(sr).to_obj(
            format='obj', dicobj={'field': 'SeriesConnec'})))
        df = tab.to_obj(format='obj', dicobj={'tab': 'DataFrameConnec'})
        #il  = tab.to_obj  (format='obj')
        #idx = field.to_obj(format='obj')
        #self.assertEqual(idx, Ntv.obj(idx).to_obj(format='obj'))
        #self.assertEqual(il, Ntv.obj(il).to_obj(format='obj'))
        self.assertTrue(df.equals(Ntv.obj(df).to_obj(
            format='obj', dicobj={'tab': 'DataFrameConnec'})))

    def test_csv(self):
        tab = Ntv.obj({':tab':
                       {'index':           [1, 2, 3],
                        'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21'],
                        'value':           [10, 20, 30],
                        'value32::int32':  [10, 20, 30],
                        'coord::point':    [[1, 2], [3, 4], [5, 6]],
                        'names::string':   ['john', 'eric', 'judith']}})
        self.assertEqual(tab, from_csv(to_csv('test.csv', tab)))
        self.assertEqual(tab, from_csv(
            to_csv('test.csv', tab, quoting=csv.QUOTE_ALL)))

class Test_Ntv_function(unittest.TestCase):

    def test_obj_ntv(self):
        l_val_s = [{'tst':[1,2,3]}, {'tst': 1},  {'tst':[1,2,3], 'tst2':5}, [1,2,3], 5, 'test']
        l_name = ['tst', '']
        l_typ = ['int32', '']
        test_s = list(product(l_val_s, l_name, l_typ))
        for tst in test_s:
            self.assertEqual(Ntv.obj_ntv(*tst, True), NtvSingle(*tst).to_obj(), 
                             Ntv.obj({tst[1]+':'+tst[2]:tst[0]}).to_obj())
        l_val_l = [{}, {'tst': 1}, {'tst':1, 'tst2':5}, [], [1,2]]
        test_l = list(product(l_val_l, l_name, l_typ))
        for tst in test_l:
            #print(tst)
            self.assertEqual(Ntv.obj_ntv(*tst, False), NtvList(*tst).to_obj(), 
                             Ntv.obj({tst[1]+'::'+tst[2]:tst[0]}).to_obj())
            
    def test_single_obj_name(self):
        list_obj = [['json', 4, ('', '', '')],
                    ['fr.', 4, ('', '', '')],
                    ['point', 4, ('', ':', 'json')],
                    ['', 4, ('', '', '')],
                    ['point', {":point": [1, 2]}, ('', '', '')],
                    ['', {":point": [1, 2]}, ('', ':', 'point')],
                    ['fr.', {":point": [1, 2]}, ('', ':', 'point')],
                    ['json', {":": [1, 2]}, ('', '', '')],
                    ['', {":fr.reg": [1, 2]}, ('', ':', 'fr.reg')],
                    ['fr.', {":fr.reg": [1, 2]}, ('', ':', 'reg')],
                    ['json', {":fr.reg": [1, 2]}, ('', ':', 'fr.reg')],
                    ['point', {":fr.reg": [1, 2]}, ('', ':', 'fr.reg')],
                    ['point', {"::point": [1, 2]}, ('', '', '')],
                    ['', {"::point": [1, 2]}, ('', '::', 'point')],
                    ['fr.', {"::fr.reg": [1, 2]}, ('', '::', 'reg')],
                    ['', {"::json": [1, 2]}, ('', '::', 'json')],
                    ['json', {"::json": [1, 2]}, ('', '', '')],
                    ['json', {"::": [1, 2]}, ('', '', '')],
                    ['array', {":array": [1, 2]}, ('', '', '')],
                    ]
        for data in list_obj:
            ntv = Ntv.obj(data[1])
            #print(ntv, data[0], data[1], data[2])
            self.assertEqual(ntv.json_name(data[0]), list(data[2]))

    def test_cast(self):
        point = []
        line = []
        pol = []
        for i in range(6):
            point.append(geometry.point.Point((i, i+1)))
        for i in range(3):
            line.append(geometry.linestring.LineString(
                (point[i], point[i+1], point[i+2])))
            pol.append(geometry.polygon.Polygon((line[i])))
        list_obj = [datetime.datetime(2021, 2, 1, 0, 0), datetime.time(21, 2, 1),
                    datetime.date(2021, 2, 1), point[0], line[0], pol[0],
                    geometry.multipoint.MultiPoint((point[0], point[1])),
                    geometry.multilinestring.MultiLineString(
                        (line[0], line[1])),
                    geometry.multipolygon.MultiPolygon((pol[0], pol[1]))]
        for obj in list_obj:
            self.assertEqual(Ntv.from_obj(
                NtvSingle(obj).to_obj()), NtvSingle(obj))
            self.assertEqual(NtvSingle(obj).to_obj(format='obj'), obj)

    def test_agreg_type(self):
        list_type = [[[None, None, True], 'json'],
                     [['point', None, True], 'point'],
                     [[None, 'fr.', True], 'json'],
                     [['json', None, True], 'json'],
                     [['point', 'date', True], 'point'],
                     [['fr.reg', 'fr.', True], 'fr.reg'],
                     [['point', 'fr.', True], 'point'],

                     [[None, None, False], None],
                     [['point', None, False], 'point'],
                     [[None, 'fr.', False], 'fr.'],
                     [['json', None, False], 'json'],
                     [['point', 'date', False], 'point'],
                     [['fr.reg', 'fr.', False], 'fr.reg'],
                     [['reg', 'fr.', False], 'fr.reg'],
                     [['point', 'fr.', False], 'point']]
        for typ in list_type:
            #print(typ[0])
            if typ[0] == [None, None, False]:
                self.assertEqual(agreg_type(
                    typ[0][0], typ[0][1], typ[0][2]), typ[1])
            else:
                self.assertEqual(agreg_type(
                    typ[0][0], typ[0][1], typ[0][2]).long_name, typ[1])
    
    def test_default_type(self):
        list_test = [[('', ':', 'fr.BAN.lon'), {'ntv1::fr.BAN.': [{':BAN.lon': 4}, 5, 6]}],
                     [('', ':', 'fr.BAN.lon'), {
                         'ntv1::fr.BAN.': [{':lon': 4}, 5, 6]}],
                     [('', ':', 'fr.reg'), {'ntv1::fr.': [{':reg': 4}, 5, 6]}],
                     [('', ':', 'fr.reg'), {
                         'ntv1::fr.': [{':fr.reg': 4}, 5, 6]}],
                     [('', ':', 'fr.reg'), {
                         'ntv1::fr.reg': [{':fr.reg': 4}, 5, 6]}],
                     [('', ':', 'fr.reg'), {'ntv1::fr.reg': [4, 5, 6]}],
                     [('', ':', 'fr.reg'), {
                         'ntv1::fr.BAN.lon': [{':fr.reg': 4}, 5, 6]}],
                     [('', ':', 'fr.reg'), {'ntv1::fr.BAN.': [{':fr.reg': 4}, 5, 6]}]]
        for test in list_test:
            # print(test[1])
            self.assertEqual(Ntv.from_obj(
                test[1]).ntv_value[0].json_name(), list(test[0]))
            self.assertEqual(
                Ntv.obj(test[1]).ntv_value[0].json_name(), list(test[0]))                

    def test_default_list(self):
        unic = NtvSingle({'un': 1, 'deux': 2}, 'param')
        lis1 = NtvList([1, 2, 3, 4], 'lis1', 'int')
        lis2 = NtvList([10, 2.5, 30, 40], 'lis2')
        il_lis1 = NtvList([lis1, lis2, unic], 'ilis1')
        il_lis2 = NtvList([lis2, lis1, unic], 'ilis2')
        il_lis1_a = NtvList([lis1, lis2, unic], 'ilis1', typ_auto=True)
        il_lis2_a = NtvList([lis2, lis1, unic], 'ilis2', typ_auto=True)
        self.assertEqual(il_lis2[0].ntv_type, il_lis1[1].ntv_type)
        self.assertEqual(il_lis2[1].ntv_type, il_lis1[0].ntv_type)
        self.assertEqual(il_lis2.ntv_type, il_lis1.ntv_type)
        self.assertNotEqual(il_lis2_a.ntv_type, il_lis1_a.ntv_type)
        
    def test_iter(self):
        ntv = Ntv.obj(0)
        for int, val in enumerate(ntv):
            self.assertEqual(val.val, int)
        ntv = Ntv.obj([0, 1, 2, 3])
        for int, val in enumerate(ntv):
            self.assertEqual(val.val, int)

class Test_NtvTree(unittest.TestCase):

    def test_NtvTree(self):
        ntv = Ntv.obj({'a': [1, [2, 3, 4], [{'c': 5}, 6]], 'b': 'ert'})
        tree = NtvTree(ntv)
        self.assertEqual(tree.nodes[0], tree._ntv)
        self.assertEqual(
            #[node.json_pointer() for node in tree.leaf_nodes][6], '/b')
            #[node.pointer().json() for node in tree.leaf_nodes][6], '/b')
            [str(node.pointer()) for node in tree.leaf_nodes][6], '/b')
        self.assertEqual(tree.adjacency_list[ntv][0], ntv[0])
        self.assertEqual(tree.height, 3)
        self.assertEqual(tree.size, 11)
        self.assertEqual(tree.breadth, 7)
        self.assertEqual(len(tree.inner_nodes), 4)
        
class Test_NtvConnector(unittest.TestCase):
    
    def test_is_json(self):
        is_json = NtvConnector.is_json
        self.assertTrue(is_json({'tst':[1, 2, 'test', None, True, {'test': 1}, [1, 'tst']]}))
        self.assertFalse(is_json({'tst':[1, 2, 'test', None, True, {'test': datetime.time()}, 
                              [1, 'tst', geometry.Point(1,2)]]}))
        with self.assertRaises(NtvError):
            is_json({'tst':[1, 2, 'test', None, True, {23: 1}, [1, 'tst']]})
        with self.assertRaises(NtvError):
            is_json({'tst':[1, 2, 'test', None, True, {'test': NtvTree(None)}, [1, 'tst']]})

    def test_cast_uncast(self):
        self.assertEqual(NtvConnector._typ_obj([21, ['ser', 25],
                         [datetime.date(2020, 3, 4), datetime.date(2020, 4, 4)]]),
                         NtvConnector._typ_obj(datetime.date(2020, 3, 4)), 'date')
        self.assertEqual(NtvConnector._typ_obj([21, ['ser', 25],
                         {'a': datetime.date(2020, 3, 4), 'b': datetime.date(2020, 4, 4)}]),
                         NtvConnector._typ_obj(datetime.date(2020, 3, 4)), 'date')        

        list_obj = [datetime.date(2020, 1,1), geometry.point.Point((3, 4)),
                    datetime.time(10,3,30)]
        for obj in list_obj:
            self.assertEqual(obj, NtvConnector.uncast(*NtvConnector.cast(obj))[0])

class Test_NtvPatch(unittest.TestCase):
    
    def test_init_op(self):
        js_cop = {'op': 'remove', 'path': '/0/1/-'}
        self.assertEqual(NtvOp(NtvOp(js_cop)), NtvOp(js_cop))
        self.assertTrue(NtvOp('test') == NtvOp({'comment': 'test'}))

    def test_op(self):
        a = Ntv.obj({'test': [[1, 2, 3], {'liste': [0,1,2,0,1,{'val':[1,2]}]}],'truc':1})
        entity = {'new': 'entity'}
        add = NtvOp({'op': 'add', 'path': '/0/liste/-', 'entity': entity})
        test = NtvOp({'op': 'test', 'path': '/0/1/-', 'entity': entity})
        remove = NtvOp({'op': 'remove', 'path': '/0/1/-'})
        self.assertEqual(NtvPatch([add, test, remove]).exe(a), a)
        add = NtvOp({'op': 'add', 'path': '/0/1/0', 'entity': entity})
        test = NtvOp({'op': 'test', 'path': '/0/1/0', 'entity': entity})
        remove = NtvOp({'op': 'remove', 'path': '/0/1/0'})
        self.assertEqual(remove.exe(test.exe(add.exe(a))), a)
        repl = NtvOp({'op': 'replace', 'path': '/0/1/1', 'entity': entity})
        test = NtvOp({'op': 'test', 'path': '/0/1/-', 'entity': entity})
        invr = NtvOp({'op': 'replace', 'path': '/0/1/1', 'entity': 1})
        self.assertEqual(invr.exe(test.exe(repl.exe(a))), a)
        move = NtvOp({'op': 'move', 'from': '/0/1/1', 'path': '/0/1/2'})
        test = NtvOp({'op': 'test', 'path': '/0/1/2', 'entity': 1})
        invm = NtvOp({'op': 'move', 'from': '/0/liste/2', 'path': '/0/1/1'})
        self.assertEqual(invm.exe(test.exe(move.exe(a))), a)        
        cop = NtvOp({'op': 'copy', 'from': '/0/1/1', 'path': '/0/1/3'})
        test = NtvOp({'op': 'test', 'path': '/0/liste/3', 'entity': 1})
        remove = NtvOp({'op': 'remove', 'path': '/0/1/3'})
        self.assertEqual(remove.exe(test.exe(cop.exe(a))), a)
        self.assertTrue( NtvOp(remove.json) == NtvOp(remove) == remove)

    def test_init_patch(self):
        js_cop = {'op': 'copy', 'from': '/0/1/1', 'path': '/0/1/3'}
        js_cop_com = {'op': 'copy', 'from': '/0/1/1', 'path': '/0/1/3', 'comment': 'test'}
        js_tst = {'op': 'test', 'path': '/0/liste/3', 'entity': 1}
        js_del = {'op': 'remove', 'path': '/0/1/3'}
        pat1 = NtvPatch([js_cop], 'test')
        pat2 = NtvPatch([NtvOp(js_cop)], 'test')
        pat3 = NtvPatch(NtvOp(js_cop_com))
        pat4 = NtvPatch({'list-op': [NtvOp(js_cop)], 'comment':'test'})
        pat5 = NtvPatch({'list-op': [js_cop], 'comment':'test'})
        pat6 = NtvPatch(pat1)
        self.assertTrue(pat1 == pat2 == pat3 == pat4 == pat5 == pat6)
        pat1 = NtvPatch([js_cop])
        pat2 = NtvPatch([NtvOp(js_cop)])
        pat3 = NtvPatch(NtvOp(js_cop))
        pat4 = NtvPatch({'list-op': [NtvOp(js_cop)]})
        self.assertTrue(pat1 == pat2 == pat3 == pat4)
        pat1 = NtvPatch([js_cop, js_tst, js_del])
        pat2 = NtvPatch([NtvOp(js_cop), NtvOp(js_tst), NtvOp(js_del)])
        pat3 = NtvPatch({'list-op': [NtvOp(js_cop), NtvOp(js_tst), NtvOp(js_del)]})
        self.assertTrue(pat1 == pat2 == pat3)
        pat1 = NtvPatch('test')
        pat2 = NtvPatch({'comment': 'test'})
        self.assertTrue(pat1 == pat2)
        pat1 = NtvPatch([js_cop, js_tst, js_del], comment='test')
        pat2 = NtvPatch({'list-op': [NtvOp(js_cop), NtvOp(js_tst), js_del],
                         'comment': 'test'})
        self.assertTrue(pat1 == pat2)
        
    def test_patch(self):
        cop = NtvOp({'op': 'copy', 'from': '/0/1/1', 'path': '/0/1/3'})
        test = NtvOp({'op': 'test', 'path': '/0/liste/3', 'entity': 1})
        remove = NtvOp({'op': 'remove', 'path': '/0/1/3'})        
        pat = NtvPatch([cop, test, remove])
        pat.append(test)
        del pat[3]
        self.assertEqual(pat, NtvPatch([cop, test, remove]))

class Test_Ntv_comment(unittest.TestCase):

    def test_comment(self):
        data = {'index':    [1, 2, 3],
         'dates::date':     ['1964-01-01', '1985-02-05', '2022-01-22'],
         'value':           [10, 20, 30],
         'value32::int32':  [10, 20, 30],
         'res':             {'res1': 10, 'res2': 20, 'res3': 30},
         'coord::point':    [[1, 2], [3, 4], [5, 6]],
         'names::string':   ['john', 'eric', 'judith']}
        ntv = Ntv.obj(data)
        com = NtvComment(ntv)
        com.add('bof')
        com.add('bof suite')
        com2 = com.accept()
        self.assertEqual(ntv, com2._ntv)
        com3 = com.reject(True)
        self.assertEqual(ntv, com3._ntv)
        op = NtvOp({'op': 'replace', 'path': '/dates/1', 
                    'entity': {':date':'1995-02-05'}, 'comment': 'a corriger'})
        com = NtvComment(ntv, op)
        com.add('bof')
        com.add({'comment': 'a corriger suite', 'list-op': [
            {'op': 'replace', 'path': '/dates/1', 'entity': {':date':'1998-02-05'}}]})
        com.add('bof suite')
        com_r = com.reject(all_comment=True)
        self.assertEqual(ntv, com_r._ntv)
        com_a = com.accept(all_comment=True)
        ntv['dates'][1].set_value('1998-02-05')
        self.assertEqual(ntv, com_a._ntv)
        #print(com.json(ntv=True))

"""    def test_json_sfield_full(self):

        # json interface ok
        for a in [{'test::int32': [1,2,3]},
                  {'test': [1,2,3]},
                  [1.0, 2.1, 3.0],
                  ['er', 'et', 'ez'],
                  [True, False, True],
                  {'::boolean': [True, False, True]},
                  {'::string': ['er', 'et', 'ez']},
                  {'test::float32': [1.0, 2.5, 3.0]},
                  {'::int64': [1,2,3]},
                  {'::datetime': ["2021-12-31T23:00:00.000","2022-01-01T23:00:00.000"] },
                  {'::date': ["2021-12-31", "2022-01-01"] },
                  {'::time': ["23:00:00", "23:01:00"] },
                  {'::object': [{'a': 3, 'e':5}, {'a': 4, 'e':6}]},
                  {'::array': [[1,2], [3,4], [5,6]]},
                  True,
                  {':boolean': True}
                 ]:
            ntv = Ntv.from_obj({':field': a})
            #print(ntv)
            self.assertEqual(Ntv.obj(ntv.to_obj(format='obj')), ntv)            
            
    def test_json_sfield_default(self):

        # json interface ok (categorical data)
        for a in [{'test': [{'::int32': [1, 2, 3]}, [0,1,2,0,1]]},
                  {'test': [[1, 2, 3], [0,1,2,0,1]]},
                  [[1.0, 2.1, 3.0], [0,1,2,0,1]],
                  [['er', 'et', 'ez'], [0,1,2,0,1]],
                  [[True, False], [0,1,0,1,0]],
                  [{'::string': ['er', 'et', 'ez']}, [0,1,2,0,1]],
                  {'test':[{'::float32': [1.0, 2.5, 3.0]}, [0,1,2,0,1]]},
                  [{'::int64': [1, 2, 3]}, [0,1,2,0,1]],
                  [{'::datetime': ["2021-12-31T23:00:00.000", "2022-01-01T23:00:00.000"] }, [0,1,0,1,0]],
                  [{'::date': ["2021-12-31", "2022-01-01"] }, [0,1,0,1,0]],
                  [{'::time': ["23:00:00", "23:01:00"] }, [0,1,0,1,0]],
                  {'test_date': [{'::datetime': ["2021-12-31T23:00:00.000", "2022-01-01T23:00:00.000"] }, [0,1,0,1,0]]},
                  [{'::boolean': [True, False]}, [0,1,0,1,0]],
                  [[True], [2]], # periodic Series
                  {'quantity': [['1 kg', '10 kg'], [4]]}]:  # periodic Series
            ntv = Ntv.from_obj({':field': a})
            #print(ntv)
            self.assertEqual(Ntv.obj(ntv.to_obj(format='obj')), ntv) """           

        
if __name__ == '__main__':
    
    unittest.main(verbosity=2)
