#!/usr/bin/python
# -*- coding: utf-8 -*-

from gdeploylib import Helpers, Global
import unittest, subprocess, os
from testutils import TestUtils

class TestBackendSetup(unittest.TestCase, Helpers):

    @classmethod
    def setUpClass(cls):
        cls.t = TestUtils()
        ret = cls.t.get_generated_commands('backend_setup.conf')

    def test_if_all_playbooks_are_present(self):
        #Test if all the necessary yamls are selected for execution
        yamls = [cmd[-1] for cmd in Global.cmd]

        necessary_yamls = ['pvcreate.yml',
        'vgcreate.yml', 'auto_lvcreate_for_gluster.yml',
        'fscreate.yml', 'mount.yml']

        yaml_paths = [self.get_file_dir_path(Global.base_dir, yml) for yml
                in necessary_yamls]
        self.assertTrue(set(yaml_paths) == set(yamls))


    def test_if_commands_are_proper(self):
        yamls = [cmd[-1] for cmd in Global.cmd]
        for cmd, yml in zip(Global.cmd, yamls):
            if not os.path.exists(cmd[-1]):
                continue
            cmd.append('--check')
            cmd.append('--connection=local')


            #Test peer probe command
            if 'pvcreate' in yml:
                cmd.extend(['--extra-vars',
                    'command=\'All items completed\''])


            # Test volume create command
            if 'vgcreate' in yml:
                cmd.extend(['--extra-vars',
                    'command=\'All items completed\''])


            # Test volume start command
            # if 'auto_lvcreate_for_gluster' in yml:
                # cmd.extend(['--extra-vars',
                    # 'command=\'All items completed\''])
            # ret = subprocess.call(cmd, shell=False)
            # self.assertEqual(ret, 0)


    @classmethod
    def tearDownClass(cls):
        cls.t.test_cleanup()


if __name__ == '__main__':
    unittest.main()
