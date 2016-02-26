#!/usr/bin/python
# -*- coding: utf-8 -*-

from gdeploy.gdeploy import main, Global
import shutil

def get_playbook_name_and_brick_dir(self):
    args = ['-ctest', '-t']
    main(args)
    return Global.playbook, Global.inventory

def cleanup():
    shutil.rmtree(base_dir)
