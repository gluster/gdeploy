#!/usr/bin/python
# -*- coding: utf-8 -*-

from gdeploy.gdeploy import main
import os, shutil, tempfile
from gdeploylib import Helpers, Global

class TestUtils(Helpers):
    def get_generated_commands(self, conf_file):
        # Chooses proper configuration file and playbook for testing
        Global.cmd = []
        Global.current_hosts = []
        Global.hosts = []
        Global.base_dir = tempfile.mkdtemp()
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        conf_file = self.get_file_dir_path(dir_path, conf_file)
        Global()
        args = ['-c' + conf_file, '-t', '-k']
        print "Yaml syntax checks:\n"
        ret = main(args)
        self.write_to_inventory('gluster_servers', Global.current_hosts)

        if ret == -1:
            return ret
        yamls = [self.get_file_dir_path(Global.base_dir, f) for f in
                os.listdir(Global.base_dir) if f.endswith('.yml')]
        for f in yamls:
            os.remove(f)
        self.copy_files(self.get_file_dir_path(dir_path, 'test_playbooks'))

    def test_cleanup(self):
        if os.path.isdir(Global.base_dir):
            shutil.rmtree(Global.base_dir)
