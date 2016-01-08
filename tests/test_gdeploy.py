#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from gdeploy import *


class GDeployTest(unittest.TestCase):

    def test_parser_with_existing_file(self):
        print "Testing if argument parser succeeds if an existing "\
        "filename is given"
        parser = parse_arguments(['-ctest'])
        self.assertTrue(parser.config_file)

    def test_parser_with_nonexisting_file(self):
        print "Testing if argument parser succeeds if an non-existing "\
        "filename is given"
        self.assertRaises(IOError, parse_arguments(['-c', 'test4']))
        # self.assertFalse(parser.config_file)

if __name__=='__main__':
    unittest.main()
