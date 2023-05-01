# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 22:05:08 2021

@author: Philippe@loco-labs.io

The `observation.test_mongo` module contains the tests (class unittest) for the
`observation.essearch` methods.
The dataset used is defined in `observation.Tests.data.py` 
"""
import unittest
import datetime
#from tabulate import tabulate
import requests as rq
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pprint import pprint
from ntv import Ntv

# Requires the PyMongo package# https://api.mongodb.com/python/current
# pathClient = 'mongodb+srv://ESobsUser:observation@esobs.gwpay.mongodb.net/test'
# uri = "mongodb+srv://Filip:<password>@loco0.tw1oroh.mongodb.net/?retryWrites=true&w=majority"

def clientMongo(user='Filip', pwd='Filip1202!', site='loco0.tw1oroh.mongodb.net/'):
    auth = 'authSource=admin'
    replicaSet = 'replicaSet=atlas-13vws6-shard-0'
    readPref = 'readPreference=primary'
    appName = 'appname=MongoDB%20Compass'
    ssl = 'ssl=true'
    retry = 'retryWrites=true'
    w = 'w=majority'
    st = 'mongodb+srv://' + user + ':' + pwd + '@' + site + \
        '?' + retry + \
        '&' + w
    return MongoClient(st, server_api=ServerApi('1'))
"""'?' + auth + \
        '&' + replicaSet + \
        '&' + readPref + \
        '&' + appName + \
        '&' + ssl
    return MongoClient(st)"""

def envoi_mongo_url(data):
    url = "https://webhooks.mongodb-realm.com/api/client/v2.0/app/observation_app-wsjge/service/postObs/incoming_webhook/api?secret=10minutes"
    r = rq.post(url, data=data)
    print("réponse : ", r.text, "\n")
    return r.status_code

client = clientMongo()
collec = client['NTV']['test']

def envoi_mongo_python(data, client, baseMongo='NTV', collection='test'):
    collec = client[baseMongo][collection]
    return collec.insert_one(data).inserted_id
    # try : return collec.insert_one(data).inserted_id
    # ou bien coll.insert_many()
    # except : return None


class Test_ntv_py(unittest.TestCase):

    def test_insert(self):
        ntv = Ntv.obj({'ntv':'essai1', 'test': {'date': datetime.datetime(2010,2,10), 'coord:point': [42.1, 3.2]}})
        collec.insert_one(ntv.to_obj(encode_format='cbor'))
        js = collec.find_one({'ntv':'essai1'})
        collec.delete_one({'_id': js['_id']})
        js.pop('_id')
        self.assertEqual(Ntv.obj(js), ntv)
        
"""    def test_param_name(self):
        srch = ESSearch(Test_jeu_data_py.collec)
        for typ, nam, leno, lis in zip(type0, name0, len_ob, ob_liste): 
            srch.addCondition(path='_metadata.param.type', operand=typ, comparator='==')
            result = srch.execute('idfused')
            #print(len(result))
            self.assertTrue(len(result) == leno and result == lis)
            srch.clearConditions()
        srch.addCondition(path='_metadata.name', comparator='regex', operand='mesures')
        result = srch.execute('idfused')
        self.assertTrue(result == ob_tests[40:52])
        srch.addCondition(path='_metadata.name', comparator='regex', operand='polluant')
        result = srch.execute('idfused')
        self.assertTrue(result == ob_tests[40:48] + ob_tests[50:52])

    def test_datation(self):
        srch = ESSearch(Test_jeu_data_py.collec)
        srch.addCondition('datation', comparator='>=', operand=datetime(2022, 1, 2, 0, 0))
        srch.addCondition('datation', comparator='<=', operand=datetime(2022, 1, 4, 0, 0))

        srch.addCondition(path='_metadata.name', comparator='regex', operand='mobile')
        result = srch.execute('idfused')
        self.assertTrue(len(result) == 1)
        self.assertTrue(ob_tests[42].loc(result[0][0], row=True) == [1])
        self.assertTrue(ob_tests[42].loc(result[0][1], row=True) == [2])
        self.assertTrue(result[0].idxlen == [2, 2, 2, 2, 2, 1, 1, 1])"""

if __name__ == '__main__':
    unittest.main(verbosity=2)
