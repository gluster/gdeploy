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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.
import os
from os.path import expanduser, dirname
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
    # Make logfile configurable
    try:
        log_file = os.environ['GDEPLOY_LOGFILE']
    except:
        log_file = expanduser('~/.gdeploy/logs/gdeploy.log')
    log_dir = dirname(log_file)
    log_dir = expanduser('~/.gdeploy/logs') if log_dir == '' else log_dir
    templates_dir = os.path.expanduser('~/.gdeploy/templates')
    extras = '/usr/share/gdeploy/extras/templates'
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
    features_dir = os.path.join(os.path.realpath(base_dir), 'gdeployfeatures')
    group_file = os.path.join(group_vars_dir, 'all')
    playbooks_file = os.path.join(os.path.realpath(base_dir),
                        'ansible_playbooks.yml')
    ignore_errors = 'yes'
    keep = False
    vdo_device = False
