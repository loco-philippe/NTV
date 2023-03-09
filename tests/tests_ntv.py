# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:57:26 2023

@author: Philippe@loco-labs.io

The `NTV.test_ntv` module contains the unit tests (class unittest) for the
`NtvSingle`, `NtvList` and `NtvSet` classes.
"""
import unittest
import datetime
from ntv import NtvSingle, NtvList, NtvSet, Ntv
from shapely import geometry

class Test_Ntv_creation(unittest.TestCase):
    
    def test_cast(self):
        point = []
        line = []
        pol = []
        for i in range(6):
            point.append(geometry.point.Point((i, i+1)))
        for i in range(3):
            line.append(geometry.linestring.LineString((point[i], point[i+1], point[i+2])))
            pol.append(geometry.polygon.Polygon((line[i])))
        list_obj = [datetime.datetime(2021, 2, 1, 0, 0), datetime.time(21,2,1),
                    datetime.date(2021, 2, 1), point[0], line[0], pol[0],
                    geometry.multipoint.MultiPoint((point[0], point[1])),
                    geometry.multilinestring.MultiLineString((line[0], line[1])),                    
                    geometry.multipolygon.MultiPolygon((pol[0], pol[1]))]                                        
        for obj in list_obj:
            self.assertTrue(Ntv.from_obj(NtvSingle(obj).to_obj())==NtvSingle(obj))
            self.assertTrue(NtvSingle(obj).to_obj(json=False) == obj)

    def test_from_obj(self):
        dictstr = {'0NtvSingle': None, 'oNtvSingle': {'none': None}, 
                   '1NtvSingle': 1, '2NtvSingle': 'test', '3NtvSingle': {'single': 1},
                   '4NtvSingle': {'ntv1': {'ntv2': 2}},
                   '5NtvSingle': {'ntv1:fr.reg': {'ntv2:fr.BAN.lon': 2}},
                   '6NtvSingle': {'ntv1': True}, '7NtvSingle': True,
                   '8NtvSingle': {'ntv1:dat': [1,2]},
                   '9NtvSingle': {'ntv1': datetime.date(2021, 2, 1)},
                   '1NtvList': [], '2NtvList': [[4,[5,6]], {'heure':[21,22]}], 
                   '3NtvList': [[4,5], {'heure':21}], '4NtvList': [[4,5], 21], 
                   '5NtvList': [[4,5], [1,2,3]],
                   '6NtvList': {'ntv1::fr.reg':[[4,[5,6]], {'heure':[21,22]}]},
                   '7NtvList': {'ntv1::fr.reg':[4]},
                   '8NtvList': {'ntv1::fr.':[4]},
                   '9NtvList': [[4,[5,6]], {'heure':[datetime.time(10, 25, 10),22]}],
                   '1NtvSet': {}, '2NtvSet': {'ntv1': 1, 'ntv2':'2'},
                   '3NtvSet': {'ntv3': {'ntv1': 1, 'ntv2':'2'}},
                   '4NtvSet': {'ntv3::fr.reg': {'ntv1': 1, 'ntv2:fr.reg':'2'}},
                   '5NtvSet': {'ntv3::fr.reg': {'ntv1': [1,2], 'ntv2:fr.reg':'2'}}}
        liststr = list(dictstr.values())
        listtyp = list(dictstr.keys())
        for nstr, typ in zip(liststr, listtyp):
            ntv = Ntv.from_obj(nstr)
            #print(nstr, typ)
            self.assertTrue(ntv == Ntv.from_obj(Ntv.to_obj(ntv)))
            self.assertTrue(ntv == Ntv.from_obj(Ntv.to_obj(ntv, json=False)))
            self.assertTrue(ntv.__class__.__name__ == typ[1:])

    def test_default_type(self):
        list_test = [[':fr.BAN.lon', {'ntv1::fr.BAN.':[{':BAN.lon':4},5,6]}],
                     [':fr.BAN.lon', {'ntv1::fr.BAN.':[{':lon':4},5,6]}],
                     [':fr.reg', {'ntv1::fr.':[{':reg':4},5,6]}],
                     [':fr.reg', {'ntv1::fr.':[{':fr.reg':4},5,6]}],
                     [':fr.reg', {'ntv1::fr.reg':[{':fr.reg':4},5,6]}],
                     [':fr.reg', {'ntv1::fr.reg':[4,5,6]}],
                     [':fr.reg', {'ntv1::fr.BAN.lon':[{':fr.reg':4},5,6]}],
                     [':fr.reg', {'ntv1::fr.BAN.':[{':fr.reg':4},5,6]}] ]
        for test in list_test:
            self.assertEqual(Ntv.from_obj(test[1]).ntv_value[0].json_name, test[0])
                
if __name__ == '__main__':
    unittest.main(verbosity=2)        