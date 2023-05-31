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

from json_ntv import NtvSingle, NtvList, Ntv, NtvError, from_csv, to_csv, agreg_type, NtvTree
from shapely import geometry


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
                    ['array', {":array": [1, 2]}, ('', '', '')],
                    ]
        for data in list_obj:
            ntv = Ntv.obj(data[1])
            # print(ntv)
            self.assertEqual(ntv.json_name(data[0]), list(data[2]))

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

    def test_address(self):
        a = Ntv.obj({'test': {'t1': 1, 't2': 2, 't3': [3, 4]}})
        self.assertTrue(a.parent is None)
        self.assertEqual(a.address, [0])
        self.assertEqual(a.address_name, '0')
        self.assertEqual(a['t3'].address, [0, 2])
        self.assertEqual(a['t3'].address_name, '0.2')
        self.assertEqual(a['t3'][0].parent.parent, a)
        self.assertEqual(a['t3'][0].address, [0, 2, 0])
        self.assertEqual(a['t3'][0].address_name, '0.2.0')

    def test_from_obj_repr(self):
        list_repr = [[1, '"s"'],
                     [{"truc":  1}, '"sN"'],
                     [{":point": 1}, '"sT"'],
                     [{"truc:":  1}, '"sN"'],
                     [{":": 1}, '"s"'],
                     [[1, 2], '{"l": ["s", "s"]}'],
                     [{"truc": [1, 2]}, '{"lN": ["s", "s"]}'],
                     [{":point": [1, 2]}, '"sT"'],
                     [{"truc:":  [1, 2]}, '"sN"'],
                     [{":": [1, 2]}, '"s"'],
                     [{"::": [1, 2]}, '{"l": ["s", "s"]}'],
                     [{"::": {"a": 2}}, '{"l": ["sN"]}'],
                     [{"::": [[1, 2], [3, 4]]},
                         '{"l": [{"l": ["s", "s"]}, {"l": ["s", "s"]}]}'],
                     [{"::point": [[1, 2], [3, 4]]}, '{"lT": ["sT", "sT"]}'],
                     [{"a": 2}, '"sN"'],
                     #[{"truc": {"a": 2}}, '{"sN": "sN"}'],
                     [{":point": {"a": 2}}, '"sT"'],
                     [{"truc:": {"a": 2}}, '"sN"'],
                     [{":": {"a": 2}}, '"s"']]
        for test in list_repr:
            # print(test)
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
            repr(Ntv.obj(([[1, 2], [3, 4]], None, 'point', 'single'))), '"sT"')
        self.assertEqual(
            repr(Ntv.obj(([[1, 2], [3, 4]], None, 'point', 'list'))), '{"lT": ["sT", "sT"]}')

    def test_from_obj(self):
        dictstr = [['NtvSingle', None],
                   ['NtvSingle', {'none': None}],
                   ['NtvSingle', 1],
                   ['NtvSingle', 'test'],
                   ['NtvSingle', {'Single': 1}],
                   ['NtvSingle', {'Ntv1:ntv': {'Ntv2': 2}}],
                   ['NtvSingle', {'Ntv1': {'Ntv2': 2}}],
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
                   ['NtvList', {"::": {" a": 2}}],
                   ['NtvList', {"test::": {"a": 2}}]]
        dictstr2 = [
                   ['NtvSingle', {':': NtvSingle(1, 'test')}, {
                       ':ntv': {'test': 1}}],
                   ['NtvSingle', {'set': NtvList([{'l1': 21}, {'l2': [2, 3]}])},
                    {'set:ntv': {'l1': 21, 'l2': [2, 3]}}],
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
                   ['NtvList', [[4, [5, 6]], {'heure': [datetime.time(10, 25, 10), 22]}],
                    [[4, [5, 6]], {'heure::time': ['10:25:10', {':json': 22}]}]],
                   ['NtvList', [[4, [5, 6]], {'heure': [datetime.time(10, 25, 10),
                                                        geometry.point.Point((3, 4))]}],
                    [[4, [5, 6]], {'heure::time': ['10:25:10', {':point': [3, 4]}]}]],
                   ['NtvList', [], {}],
                   ['NtvList', {'::': [{'paris': [2.1, 40.3]}, {'lyon': [2.1, 40.3]}]},
                    {'paris': [2.1, 40.3], 'lyon': [2.1, 40.3]}],
                   ['NtvList', {'Ntv3::fr.reg': {'Ntv1': 1, 'Ntv2:fr.reg': '2'}},
                    {'Ntv3::fr.reg': {'Ntv1': 1, 'Ntv2': '2'}}],
                   ['NtvList', {'Ntv3::fr.reg': {'Ntv1': [1, 2], 'Ntv2:fr.reg': '2'}},
                    {'Ntv3::fr.reg': {'Ntv1': [1, 2], 'Ntv2': '2'}}],
        ]
        lis = list(zip(*dictstr))
        liststr = list(lis[1])
        listtyp = list(lis[0])
        for nstr, typ in zip(liststr, listtyp):
            #print('av', nstr, typ)
            ntv = Ntv.from_obj(nstr)
            ntv2 = Ntv.obj(nstr)
            self.assertEqual(ntv, ntv2)
            #print('ap', nstr, typ)
            self.assertEqual(nstr, ntv.to_obj())
            self.assertTrue(ntv.__class__.__name__ == typ)
            self.assertEqual(ntv, Ntv.from_obj(Ntv.to_obj(ntv)))

        lis = list(zip(*dictstr2))
        listres = list(lis[2])
        liststr = list(lis[1])
        listtyp = list(lis[0])
        for nstr, typ, nres in zip(liststr, listtyp, listres):
            #print('av', nstr, typ)
            ntv = Ntv.from_obj(nstr)
            ntv2 = Ntv.obj(nstr)
            self.assertEqual(ntv, ntv2)
            #print('ap', nstr, typ)
            self.assertTrue(ntv.__class__.__name__ == typ)
            self.assertEqual(ntv, Ntv.from_obj(Ntv.to_obj(ntv)))
            self.assertEqual(nres, ntv.to_obj())

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
        self.assertEqual(il_lis2[0].ntv_type, il_lis1[1].ntv_type)
        self.assertEqual(il_lis2[1].ntv_type, il_lis1[0].ntv_type)
        self.assertNotEqual(il_lis2.ntv_type, il_lis1.ntv_type)

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
        self.assertEqual(Ntv.obj({'paris:point': 'null'}).to_obj(encode_format='obj'),
                         {'paris:point': None})

    def test_tab(self):
        tab = Ntv.obj({'index':           [1, 2, 3],
                       'dates::datetime': ['1964-01-01', '1985-02-05', '2022-01-21'],
                       'value':           [10, 20, 30],
                       'value32::int32':  [10, 20, 30],
                       'res':             {'res1': 10, 'res2': 20, 'res3': 30},
                       'coord::point':    [[1, 2], [3, 4], [5, 6]],
                       'names::string':   ['john', 'eric', 'judith']})
        self.assertEqual(tab[1][2], tab['dates'][2],
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
        sr = field.to_obj(encode_format='obj', dicobj={
                          'field': 'SeriesConnec'})
        df = tab.to_obj(encode_format='obj', dicobj={'tab': 'DataFrameConnec'})
        #il  = tab.to_obj  (encode_format='obj')
        #idx = field.to_obj(encode_format='obj')
        #self.assertEqual(idx, Ntv.obj(idx).to_obj(encode_format='obj'))
        #self.assertEqual(il, Ntv.obj(il).to_obj(encode_format='obj'))
        self.assertTrue(df.equals(Ntv.obj(df).to_obj(
            encode_format='obj', dicobj={'tab': 'DataFrameConnec'})))
        self.assertTrue(sr.equals(Ntv.obj(sr).to_obj(
            encode_format='obj', dicobj={'field': 'SeriesConnec'})))

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

    def test_NtvTree(self):
        ntv = Ntv.obj({'a': [1, [2, 3, 4], [5, 6]], 'b': 'ert'})
        tree = NtvTree(ntv)
        self.assertEqual(tree.nodes[0], tree.ntv)
        self.assertEqual(
            [node.address_name for node in tree.leaf_nodes][6], '0.1')
        self.assertEqual(tree.adjacency_list[ntv][0], ntv[0])
        self.assertEqual(tree.height, 3)
        self.assertEqual(tree.size, 11)
        self.assertEqual(tree.breadth, 7)
        self.assertEqual(len(tree.inner_nodes), 4)

    def test_iter(self):
        ntv = Ntv.obj(0)
        for int, val in enumerate(ntv):
            self.assertEqual(val, int)
        ntv = Ntv.obj([0, 1, 2, 3])
        for int, val in enumerate(ntv):
            self.assertEqual(val.val, int)


if __name__ == '__main__':
    unittest.main(verbosity=2)
