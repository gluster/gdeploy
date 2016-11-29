# Copyright 2016 Red Hat, Inc. <http://www.redhat.com>
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

# TODO: Do better error handling.
# Handle the dictionary and key errors.

from ansible.plugins.callback import CallbackBase
from ansible import constants as C

class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'gdeploy'

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if 'exception' in result._result:
            if self._display.verbosity < 3:
                # extract just the actual error message from the exception text
                error = result._result['exception'].strip().split('\n')[-1]
                msg = "An exception occurred during task execution. "
                "To see the full traceback, use -vvv. The error was: %s"%error
            else:
                msg = "An exception occurred during task execution. "
                "The full traceback is:\n" + result._result['exception']
            self._display.display(msg, color=C.COLOR_ERROR)

        self._process_results(result, 'FAILED', C.COLOR_ERROR)

    def v2_runner_on_ok(self, result):
        if 'changed' in result._result and result._result['changed']:
            self._process_results(result, 'SUCCESS', C.COLOR_CHANGED)
        else:
            self._process_results(result, 'SUCCESS', C.COLOR_OK)

    def v2_runner_on_skipped(self, result):
        self._process_results(result, 'SKIPPED', C.COLOR_SKIP)

    def v2_runner_on_unreachable(self, result):
        self._process_results(result, 'UNREACHABLE', C.COLOR_UNREACHABLE)

    def _process_results(self, result, status, color):
        # One of the result items could be the status of ansible facts.
        # We ignore them for now
        if result._result.has_key('ansible_facts'):
            return

        results = result._result['results']
        for res in results:
            if status == 'UNREACHABLE' or status == 'FAILED':
                if res['failed']:
                    self._display.display("[%s] %s (%s):  %s\nError: %s"%
                                          (result._host.get_name(),
                                           result._task.get_name(),
                                           res['item'], status, res['msg']),
                                          color=color)
                else:
                    status = 'SUCCESS'
                    color = C.COLOR_OK
                    self._display.display("[%s] %s (%s):  %s"%
                                          (result._host.get_name(),
                                           result._task.get_name(),
                                           res['item'], status),
                                          color=color)
            else:
                self._display.display("[%s] %s (%s): %s"%(
                    result._host.get_name(), result._task.get_name(),
                    res['item'], status), color=color)

    def _get_field(self, result, field):
        """Porcesses the result and returns the requested field"""

        if field == 'item':
            pass
        if field == 'msg':
            pass
