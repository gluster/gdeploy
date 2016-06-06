# -*- coding: utf-8 -*-
#
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.

from gdeploylib import Helpers
from gdeploylib import defaults

helpers = Helpers()

def snapshot_create(section_dict):
    global helpers
    section_dict = helpers.volname_formatter(section_dict)
    return section_dict, defaults.SNAPSHOT_CREATE

def snapshot_delete(section_dict):
    global helpers
    section_dict = helpers.volname_formatter(section_dict)
    return section_dict, defaults.SNAPSHOT_DELETE


def snapshot_clone(section_dict):
    return section_dict, defaults.SNAPSHOT_CLONE

def snapshot_restore(section_dict):
    return section_dict, defaults.SNAPSHOT_RESTORE

def snapshot_activate(section_dict):
    return section_dict, defaults.SNAPSHOT_ACTIVATE

def snapshot_deactivate(section_dict):
    return section_dict, defaults.SNAPSHOT_DEACTIVATE

def snapshot_config(section_dict):
    return section_dict, defaults.SNAPSHOT_CONFIG

