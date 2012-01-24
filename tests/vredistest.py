#!/usr/bin/env python
import unittest
import random
import string
from vredis import VRedis
from mockredis import MockConnectionPool

class VRedisTest(unittest.TestCase):
    def setUp(self):
        # setup VRedis 
        self.vr = VRedis(
            hosts=[
                ('1', 1, 85),
                ('2', 2, 170),
                ('3', 3, 255)
            ],
            cls=MockConnectionPool
        )

    def tearDown(self):
        self.vr.flushall()

    def testhash(self):
        results = {}
        for i in range(256):
            results[i] = 0
        for i in range(256 * 1000):
            # hash a random string
            hash = self.vr.hash(''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10)))
            results[hash] += 1
        for i in range(256):
            self.assertIn(results[i], range(800, 1200))

    def test_get_server(self):
        s = self.vr.get_server("1") # hash starts with c4 - 196
        self.assertEquals(s, "3:3")
        s = self.vr.get_server("2") # hash starts with c8 - 200
        self.assertEquals(s, "3:3")
        s = self.vr.get_server("3") # hash starts with ec - 236
        self.assertEquals(s, "3:3")
        s = self.vr.get_server("4") # hash starts with a8 - 168
        self.assertEquals(s, "2:2")
        s = self.vr.get_server("6") # hash starts with 16 - 22
        self.assertEquals(s, "1:1")
    
    def test_get(self):
        self.vr.set("test", "1")
        self.assertEquals(self.vr.get("test"), "1")
        self.assertEquals(self.vr.dbsize(), 1)

    def test_mget(self):
        data = {
            "1": 1, # server 3
            "2": 2, # server 3
            "3": 3, # server 3
            "4": 4, # server 2
            "6": 6  # server 1
        }
        self.assertEquals(self.vr.mset(data), True)
        self.assertEquals(self.vr.dbsize(), len(data))
        self.assertEquals(self.vr.mget(data.keys()), data.values())
        for i in data:
            self.assertEquals(self.vr.get(i), data[i])
    
    def test_mget_individual(self):
        data = {
            "1": 1, # server 3
            "2": 2, # server 3
            "3": 3, # server 3
            "4": 4, # server 2
            "6": 6  # server 1
        }
        for i in data:
            self.assertEquals(self.vr.set(i, data[i]), True)
        self.assertEquals(self.vr.mget(data.keys()), data.values())
        for i in data:
            self.assertEquals(self.vr.get(i), data[i])
        self.assertEquals(self.vr.dbsize(), len(data))
    
    def test_keys(self):
        data = {
            "1": 1, # server 3
            "2": 2, # server 3
            "3": 3, # server 3
            "4": 4, # server 2
            "6": 6  # server 1
        }
        self.assertEquals(self.vr.mset(data), True)
        self.assertEquals(self.vr.dbsize(), len(data))
        keys = self.vr.keys("*")
        self.assertEquals(len(keys), len(data.keys()))
        for key in data.keys():
            self.assertTrue(key in keys)
    
if __name__ == '__main__':
    unittest.main()
