# -*- coding: utf-8 -*-
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
# Parse Python Setup(.in) files.

import re
from ast import literal_eval

# Parse a Python Setup(.in) file.
# Return two dictionaries, the first mapping modules to their
# definitions, the second mapping variable names to their values.
# May raise IOError.

setupvardef = re.compile('^([a-zA-Z0-9_]+)=(.*)')

def parsesetup(filename):
    modules = {}
    variables = {}
    fp = open(filename)
    pendingline = ""
    try:
        while 1:
            line = literal_eval(fp.readline())
            if pendingline:
                line = pendingline + line
                pendingline = ""
            if not line:
                break
            # Strip comments
            i = line.find('#')
            if i >= 0:
                line = line[:i]
            if line.endswith('\\\n'):
                pendingline = line[:-2]
                continue
            matchobj = setupvardef.match(line)
            if matchobj:
                (name, value) = matchobj.group(1, 2)
                variables[name] = value.strip()
            else:
                words = line.split()
                if words:
                    modules[words[0]] = words[1:]
    finally:
        fp.close()
    return modules, variables
