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

from json_ntv import NtvSingle, NtvList, NtvSet, Ntv, NtvError, NtvType, from_csv, to_csv, agreg_type
from shapely import geometry

from ntv_connector import to_csv, from_csv
from observation import Ilist


class Test_Ntv_creation(unittest.TestCase):

    def test_single_obj_name(self):
        list_obj = [['json', 4, ('', '', '')],
                    ['fr.', 4, ('', ':', 'json')],
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
                    #['', {"::json": [1, 2]}, ('', '::', 'json')],
                    ['', {"::json": [1, 2]}, ('', '', '')],
                    ['json', {"::json": [1, 2]}, ('', '', '')],
                    #['json', {"::": [1, 2]}, ('', '::', 'json')],
                    ['json', {"::": [1, 2]}, ('', '', '')],
                    ]
        for data in list_obj:
            ntv = Ntv.obj(data[1])
            #print(ntv)
            self.assertEqual(ntv.obj_name(data[0]), list(data[2]))

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
            # print(typ[0])
            if typ[0] == [None, None, False]:
                self.assertEqual(agreg_type(
                    typ[0][0], typ[0][1], typ[0][2]), typ[1])
            else:
                self.assertEqual(agreg_type(
                    typ[0][0], typ[0][1], typ[0][2]).long_name, typ[1])

    def test_from_obj_repr(self):
        list_repr = [[1, '"v"'],
                     [{"truc":  1}, '"vN"'],
                     [{":point": 1}, '"vT"'],
                     [{"truc:":  1}, '"vN"'],
                     [{":": 1}, '"v"'],
                     [[1, 2], '{"l": ["v", "v"]}'],
                     [{"truc": [1, 2]}, '{"lN": ["v", "v"]}'],
                     [{":point": [1, 2]}, '"vT"'],
                     [{"truc:":  [1, 2]}, '"vN"'],
                     [{":": [1, 2]}, '"v"'],
                     [{"::": [1, 2]}, '{"l": ["v", "v"]}'],
                     [{"::": {"a": 2}}, '{"s": ["vN"]}'],
                     [{"::": [[1, 2], [3, 4]]},
                         '{"l": [{"l": ["v", "v"]}, {"l": ["v", "v"]}]}'],
                     [{"::point": [[1, 2], [3, 4]]}, '{"lT": ["vT", "vT"]}'],
                     [{"a": 2}, '"vN"'],
                     #[{"truc": {"a": 2}}, '{"vN": "vN"}'],
                     [{":point": {"a": 2}}, '"vT"'],
                     [{"truc:": {"a": 2}}, '"vN"'],
                     [{":": {"a": 2}}, '"v"']]
        for test in list_repr:
            #print(test)
            self.assertEqual(repr(Ntv.from_obj(test[0])), test[1])

    def test_from_obj_ko(self):
        liststr = [{"::": 1}]
        for nstr in liststr:
            with self.assertRaises(NtvError):
                Ntv.from_obj(nstr)

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
            self.assertEqual(NtvSingle(obj).to_obj(encode_format='obj'), obj)

    def test_from_att(self):
        self.assertEqual(
            repr(Ntv.obj(([[1, 2], [3, 4]], None, 'point', 'single'))), '"vT"')
        self.assertEqual(
            repr(Ntv.obj(([[1, 2], [3, 4]], None, 'point', 'list'))), '{"lT": ["vT", "vT"]}')

    def test_from_obj(self):
        dictstr = {'0NtvSingle': None,
                   'oNtvSingle': {'none': None},
                   '1NtvSingle': 1,
                   '2NtvSingle': 'test',
                   '3NtvSingle': {'single': 1},
                   '4NtvSingle': {'ntv1:ntv': {'ntv2': 2}},
                   '5NtvSingle': {'ntv1:fr.reg': {'ntv2:fr.BAN.lon': 2}},
                   '6NtvSingle': {'ntv1': True},
                   '7NtvSingle': True,
                   '8NtvSingle': {'ntv1:dat': [1, 2]},
                   '9NtvSingle': {'ntv1': datetime.date(2021, 2, 1)},
                   'dNtvSingle': datetime.date(2021, 2, 1),
                   'aNtvSingle': '{ner',
                   'bNtvSingle': {':$point': {'a': [1, 2], 'b': [3, 4]}},
                   'cNtvSingle': {':': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]},
                   'eNtvSingle': {':': NtvSingle(1,'test')},
                   'hNtvSingle': {'set:': NtvSet([{'l1':21}, {'l2': [2,3]}])},
                   'fNtvSingle': {'set:': NtvSet([{'l1':21}, {'l2': datetime.date(2021, 2, 1)}])},
                   'gNtvSingle': {'lis:': NtvList([{'l1':21}, {'l2': datetime.date(2021, 2, 1)}])},
                   'iNtvSingle': {'lis:': NtvList([1,2,3])},
                   '1NtvList': [],
                   '2NtvList': [[4, [5, 6]], {'heure': [21, 22]}],
                   '3NtvList': [[4, 5], {'heure': 21}],
                   '4NtvList': [[4, 5], 21],
                   '5NtvList': [[4, 5], [1, 2, 3]],
                   '6NtvList': {'ntv1::fr.reg': [[4, [5, 6]], {'heure': [21, 22]}]},
                   '7NtvList': {'ntv1::fr.reg': [4]},
                   '8NtvList': {'ntv1::fr.': [4]},
                   '9NtvList': [[4, [5, 6]], {'heure': [datetime.time(10, 25, 10), 22]}],
                   'aNtvList': [[4, [5, 6]], {'heure': [datetime.time(10, 25, 10),
                                                        geometry.point.Point((3, 4))]}],
                   'bNtvList': {'::': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]},
                   'cNtvList': {'cities::point': [[2.1, 40.3], [2.1, 40.3]]},
                   '1NtvSet': {},
                   '2NtvSet': {'ntv1': 1, 'ntv2': '2'},
                   '3NtvSet': {'ntv3': {'ntv1': 1, 'ntv2': '2'}},
                   '4NtvSet': {'ntv3::fr.reg': {'ntv1': 1, 'ntv2:fr.reg': '2'}},
                   '5NtvSet': {'ntv3::fr.reg': {'ntv1': [1, 2], 'ntv2:fr.reg': '2'}},
                   '6NtvSet': {"::": {" a": 2}},
                   '7NtvSet': {"test::": {"a": 2}}
                   }
        liststr = list(dictstr.values())
        listtyp = list(dictstr.keys())
        for nstr, typ in zip(liststr, listtyp):
            #print('av', nstr, typ)
            ntv = Ntv.from_obj(nstr)
            ntv2 = Ntv.obj(nstr)
            self.assertEqual(ntv, ntv2)
            #print('ap', nstr, typ)
            if not typ in ['9NtvList', 'aNtvList', 'bNtvList', '9NtvSingle', 'eNtvSingle',
                           'dNtvSingle', 'fNtvSingle', 'gNtvSingle', 'hNtvSingle',
                           'iNtvSingle', '4NtvSet', '5NtvSet']:
                self.assertEqual(nstr, ntv.to_obj())
            if typ == 'bNtvList':
                self.assertEqual(nstr['::'], ntv.to_obj())
            if typ == '4NtvSet':
                self.assertEqual(
                    {'ntv3::fr.reg': {'ntv1': 1, 'ntv2': '2'}}, ntv.to_obj())
            if typ == '5NtvSet':
                self.assertEqual(
                    {'ntv3::fr.reg': {'ntv1': [1, 2], 'ntv2': '2'}}, ntv.to_obj())
            self.assertEqual(ntv, Ntv.from_obj(Ntv.to_obj(ntv)))
            # self.assertEqual(ntv, Ntv.from_obj(
            #    Ntv.to_obj(ntv, encode_format='cbor')))
            if not typ in ['9NtvList', 'aNtvList']:
                self.assertEqual(ntv, Ntv.from_obj(
                    Ntv.to_obj(ntv, encoded=True)))
            self.assertTrue(ntv.__class__.__name__ == typ[1:])

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
                test[1]).ntv_value[0].obj_name(), list(test[0]))
            self.assertEqual(
                Ntv.obj(test[1]).ntv_value[0].obj_name(), list(test[0]))

    def test_default_list(self):
        unic = NtvSingle({'un':1, 'deux':2}, 'param')
        lis1 = NtvList([1,2,3,4], 'lis1', 'int')
        lis2 = NtvList([10,2.5,30,40], 'lis2')
        il_lis1 = NtvList([lis1, lis2, unic], 'ilis1')
        il_lis2 = NtvList([lis2, lis1, unic], 'ilis2')
        self.assertEqual(il_lis2[0].ntv_type, il_lis1[1].ntv_type)
        self.assertEqual(il_lis2[1].ntv_type, il_lis1[0].ntv_type)
        self.assertNotEqual(il_lis2.ntv_type, il_lis1.ntv_type)
        
    def test_to_obj(self):
        nstr = {'cities': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]}
        self.assertEqual(Ntv.from_obj(nstr).to_obj(
            simpleval=True), [[2.1, 40.3], [2.1, 40.3]])

    def test_tab_field_pandas_ilist_Iindex(self):
        field = Ntv.obj({':field': 
                     {'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21']}})
        tab   = Ntv.obj({':tab'  :
                     {'index':           [1, 2, 3],
                      'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21'], 
                      'value':           [10, 20, 30],
                      'value32::int32':  [10, 20, 30],
                      'coord::point':    [[1,2], [3,4], [5,6]],
                      'names::string':   ['john', 'eric', 'judith']}})
        sr  = field.to_obj(encode_format='obj', dicobj={'field': 'SeriesConnec'})
        df  = tab.to_obj  (encode_format='obj', dicobj={'tab': 'DataFrameConnec'})
        il  = tab.to_obj  (encode_format='obj')
        idx = field.to_obj(encode_format='obj')
        self.assertEqual(idx, Ntv.obj(idx).to_obj(encode_format='obj'))
        self.assertEqual(il, Ntv.obj(il).to_obj(encode_format='obj'))
        self.assertTrue(df.equals(Ntv.obj(df).to_obj(encode_format='obj', dicobj={'tab': 'DataFrameConnec'})))
        self.assertTrue(sr.equals(Ntv.obj(sr).to_obj(encode_format='obj', dicobj={'field': 'SeriesConnec'})))

    def test_csv(self):
        tab   = Ntv.obj({':tab'  :
                     {'index':           [1, 2, 3],
                      'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21'], 
                      'value':           [10, 20, 30],
                      'value32::int32':  [10, 20, 30],
                      'coord::point':    [[1,2], [3,4], [5,6]],
                      'names::string':   ['john', 'eric', 'judith']}})        
        self.assertEqual(tab, from_csv(to_csv('test.csv', tab)))
        self.assertEqual(tab, from_csv(to_csv('test.csv', tab, quoting=csv.QUOTE_ALL)))
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
