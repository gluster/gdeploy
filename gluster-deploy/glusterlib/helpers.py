#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Nandaja Varma <nvarma@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#    helpers.py
#    ---------
#    Helpers consists of a couple of general helper methods
#    called from various parts of the framework to create directories
#    and run commands
#

import os
import sys
from global_vars import Global

class Helpers(Global):

    def cleanup_and_quit(self):
        if os.path.isdir(Global.base_dir):
            self.exec_cmds('rm -rf', Global.base_dir)
        sys.exit(0)

    def mk_dir(self, direc):
        if os.path.isdir(direc):
            self.exec_cmds('rm -rf', direc)
        self.exec_cmds('mkdir', direc)

    def touch_file(self, filename):
        try:
            os.remove(filename)
        except OSError:
            pass
        self.exec_cmds('touch', filename)

    def get_file_dir_path(self, basedir, newdir):
        return os.path.join(os.path.realpath(basedir), newdir)

    def uppath(self, path, n):
        return os.sep.join(path.split(os.sep)[:-n])

    def exec_cmds(self, cmd, opts):
        try:
            os.system(cmd + ' ' + opts)
        except:
            print "Error: Command %s failed. Exiting!" % cmd
            sys.exit()
