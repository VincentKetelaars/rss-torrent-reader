'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
import unittest

import test_decider
import test_downloader
import test_item

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromModule(test_decider))
    suite.addTest(unittest.TestLoader().loadTestsFromModule(test_downloader))
    suite.addTest(unittest.TestLoader().loadTestsFromModule(test_item))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)