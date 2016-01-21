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
import tempfile


class Global(object):

    ''' singleton class to store the
        shared varibles between the
        modules
    '''
    logger = None
    trace = False
    var_file = None
    master = None
    brick_hosts = []
    log_file = os.path.expanduser('~/.gdeploy/logs/gdeploy.log')
    hosts = []
    current_hosts = []
    current_host = None
    sections = {}
    playbooks = []
    host_vars = 'host_vars'
    group_vars = 'group_vars'
    group = 'gluster_servers'
    base_dir = tempfile.mkdtemp()
    group_vars_dir = os.path.join(os.path.realpath(base_dir), group_vars)
    host_vars_dir = os.path.join(os.path.realpath(base_dir), host_vars)
    inventory = os.path.join(os.path.realpath(base_dir), 'ansible_hosts')
    features_dir = os.path.join(os.path.realpath(base_dir), 'features')
    group_file = os.path.join(group_vars_dir, 'all')
    playbooks_file = os.path.join(os.path.realpath(base_dir),
                        'ansible_playbooks.yml')


