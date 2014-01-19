'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
import unittest

import test_decider

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromModule(test_decider))
    
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)