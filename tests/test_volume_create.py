#!/usr/bin/python
# -*- coding: utf-8 -*-

from gdeploy.gdeploy import main, Global
import unittest

class TestHelpers(unittest.TestCase):

    def testVolumeCreate(self):
        args = ['-ctests/volume_create.conf', '-t']
        ret = main(args)
        self.assertEqual(Global.command, 'gluster volume create')

if __name__ == '__main__':
    unittest.main()
