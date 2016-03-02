#!/usr/bin/python
# -*- coding: utf-8 -*-

from gdeploy.gdeploy import main, Global
import unittest, subprocess, os, shutil
from gdeploylib import Helpers

class TestHelpers(unittest.TestCase, Helpers):


    def testVolumeCreate(self):
        # Chooses proper configuration file and playbook for testing
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        conf_file = self.get_file_dir_path(dir_path, 'volume_create.conf')
        args = ['-c' + conf_file, '-t']
        print "Yaml syntax checks:\n"
        ret = main(args)

        yamls = [self.get_file_dir_path(Global.base_dir, f) for f in
                os.listdir(Global.base_dir) if f.endswith('.yml')]
        for f in yamls:
            os.remove(f)
        self.copy_files(self.get_file_dir_path(dir_path, 'test_playbooks'))
        self.assertEqual(1, 1)




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
                    'command=\'gluster peer probe 10.70.46.76   --mode=script\''])


            # Test volume create command
            if 'volume-create' in yml:
                cmd.extend(['--extra-vars',
                    'command=\'gluster volume create gemvol   transport tcp  10.70.47.3:/brick/test_brick1   --mode=script\''])


            # Test volume start command
            if 'volume-start' in yml:
                cmd.extend(['--extra-vars',
                    'command=\'gluster volume start gemvol    --mode=script\''])
            ret = subprocess.call(cmd, shell=False)
            self.assertEqual(ret, 0)
        if os.path.isdir(Global.base_dir):
            shutil.rmtree(Global.base_dir)




if __name__ == '__main__':
    unittest.main()
