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
import os
import logging, datetime
from os.path import dirname, expanduser


class MyFormatter(logging.Formatter):

    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'gdeploy'

    try:
        log_file = os.environ['GDEPLOY_LOGFILE']
    except:
        log_file = expanduser('~/.gdeploy/logs/gdeploy.log')

    log_dir = dirname(log_file)
    log_dir = expanduser('~/.gdeploy/logs') if log_dir == '' else log_dir

    if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    logger = logging.getLogger("gdeploy")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_file)
    formatter = MyFormatter('[%(asctime)s] %(levelname)s ' \
                            '%(filename)s[%(lineno)s]: ' \
                            '%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)


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

        try:
            results = result._result['results']
        except KeyError:
            # For certain tasks the result format is different we deal
            # them in a separate function
            self.handle_special_results(result, status, color)
            return

        for res in results:
            if status == 'UNREACHABLE' or status == 'FAILED':
                if res['failed']:
                    # When the shell module is used there is no msg key
                    try:
                        msg = res['msg']
                    except KeyError:
                        msg = res['stderr']

                    self._display.display("[%s] %s (%s):  %s\nError: %s"%
                                          (result._host.get_name(),
                                           result._task.get_name(),
                                           res['item'], status, msg),
                                          color=color)
                    self.logger.error("[%s] %s (%s):  %s Error: %s"%
                                      (result._host.get_name(),
                                       result._task.get_name(),
                                       res['item'], status, msg))
                else:
                    status = 'SUCCESS'
                    color = C.COLOR_OK
                    self._display.display("[%s] %s (%s):  %s"%
                                          (result._host.get_name(),
                                           result._task.get_name(),
                                           res['item'], status),
                                          color=color)
                    self.logger.info("[%s] %s (%s):  %s"%
                                     (result._host.get_name(),
                                      result._task.get_name(),
                                      res['item'], status))
            else:
                self._display.display("[%s] %s (%s): %s"%(
                    result._host.get_name(), result._task.get_name(),
                    res['item'], status), color=color)
                self.logger.info("[%s] %s (%s): %s"%(
                    result._host.get_name(), result._task.get_name(),
                    res['item'], status))

    def handle_special_results(self, result, status, color):
        self._display.display("[%s] %s: %s"%(result._host.get_name(),
                                             result._task.get_name(),
                                             status),
                              color=color)
        if status == "FAILED":
            self.logger.error("[%s] %s: %s"%(result._host.get_name(),
                                             result._task.get_name(),
                                             status))
            self.logger.error("[%s] %s"%(result._host.get_name(),
                                          result._result['msg']))
        else:
            self.logger.info("[%s] %s: %s"%(result._host.get_name(),
                                            result._task.get_name(),
                                            status))

