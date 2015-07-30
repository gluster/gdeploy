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
import os


class Global(object):

    ''' singleton class to store the
        shared varibles between the
        modules
    '''
    #Truth value of basic ops: backend setup, volume create and mount
    do_setup_backend = True
    do_volume_create = False
    do_volume_delete = False
    do_volume_mount = False

    #Features:
    create_snapshot = False
    setup_ganesha = False
    volume_set = False
    shell_cmd = False

    #Required filenames and dir names
    master = None
    host_vars = 'host_vars'
    group_vars = 'group_vars'
    group = 'rhs_servers'
    base_dir = '/tmp/playbooks'
    group_vars_dir = os.path.join(os.path.realpath(base_dir), group_vars)
    host_vars_dir = os.path.join(os.path.realpath(base_dir), host_vars)
    inventory = os.path.join(os.path.realpath(base_dir), 'ansible_hosts')
    group_file = os.path.join(group_vars_dir, 'all')
