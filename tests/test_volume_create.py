#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest, subprocess, os
from gdeploylib import Helpers, Global
from testutils import TestUtils

class TestVolumeCreate(unittest.TestCase, Helpers):

    @classmethod
    def setUpClass(cls):
        cls.t = TestUtils()
        ret = cls.t.get_generated_commands('volume_create.conf')



    def test_if_all_playbooks_are_present(self):
        #Test if all the necessary yamls are selected for execution
        yamls = [cmd[-1] for cmd in Global.cmd]

        necessary_yamls = ['service_management.yml',
        'gluster-peer-probe.yml', 'create-brick-dirs.yml',
        'gluster-volume-create.yml', 'gluster-volume-start.yml']

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
            if 'peer-probe' in yml:
                cmd.extend(['--extra-vars',
                    'command=\'gluster peer probe\''])


            # Test volume create command
            if 'volume-create' in yml:
                cmd.extend(['--extra-vars',
                    'command=\'gluster volume create gemvol   transport tcp  10.70.46.76:/brick/test_brick1   --mode=script\''])


            # Test volume start command
            if 'volume-start' in yml:
                cmd.extend(['--extra-vars',
                    'command=\'gluster volume start gemvol    --mode=script\''])
            ret = subprocess.call(cmd, shell=False)
            self.assertEqual(ret, 0)


    @classmethod
    def tearDownClass(cls):
        cls.t.test_cleanup()


if __name__ == '__main__':
    unittest.main()
