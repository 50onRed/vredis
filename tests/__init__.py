import unittest
from vredistest import VRedisTest

def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VRedisTest))
    return suite
