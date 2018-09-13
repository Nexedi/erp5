##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import multiprocessing
import traceback
import signal
import sys
import socket
import time

from ..testbrowser.browser import Browser
from .result import NothingFlushedException

REPEAT_NUMBER_BEFORE_FLUSHING = 1

class BenchmarkProcess(multiprocessing.Process):
  def __init__(self, exit_msg_queue, result_klass, argument_namespace,
               nb_users, user_index, current_repeat_range, *args, **kwargs):
    self._exit_msg_queue = exit_msg_queue
    self._result_klass = result_klass
    self._argument_namespace = argument_namespace
    self._nb_users = nb_users
    self._user_index = user_index
    self._current_repeat_range = current_repeat_range

    try:
      self._username, self._password, self._source_ip = \
          argument_namespace.user_tuple[user_index]
    except ValueError:
      self._source_ip = None
      self._username, self._password = argument_namespace.user_tuple[user_index]

    # Initialized when running the test
    self._browser = None
    self._current_repeat = 1

    # TODO: Per target error counter instead of global one?
    self._error_counter = 0

    super(BenchmarkProcess, self).__init__(*args, **kwargs)

  def stopGracefully(self, *args, **kwargs):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    raise StopIteration("Interrupted by user or because of an error from "
                        "another process, flushing remaining results...")

  def getBrowser(self, log_file):
    self._logger.info("[BenchmarkProcess] Browser username and password: %s - %s" % (self._username, self._password))
    return Browser(self._argument_namespace.erp5_base_url,
                   self._username,
                   self._password,
                   log_file,
                   self._argument_namespace.enable_debug,
                   self._argument_namespace.is_legacy_listbox)

  def runBenchmarkSuiteList(self, result):
    for target_idx, target in enumerate(self._argument_namespace.benchmark_suite_list):
      self._logger.debug("EXECUTE: %s" % target)
      result.enterSuite(target.__name__)
      with_error = False

      try:
        target(result, self._browser)
      except StopIteration:
        raise
      except Exception as e:
        self._logger.info("Exception while running target suite for user %s: %s" % (self._browser._username, str(e)))
        msg = "%s: %s" % (target, traceback.format_exc())
        try:
          msg += "Last response headers:\n%s\nLast response contents:\n%s" % \
              (self._browser.headers, self._browser.contents)
        except Exception:
          pass

        self._error_counter += 1
        if self._error_counter >= self._argument_namespace.max_error_number:
          raise RuntimeError(msg)

        self._logger.warning(msg)
        with_error = True

      else:
        for stat in result.getCurrentSuiteStatList():
          self._logger.info(str(stat))

          if (self._argument_namespace.max_global_average and
              stat.mean > self._argument_namespace.max_global_average):
            raise RuntimeError("Stopping as mean is greater than maximum "
                               "global average")

      finally:
        # Clear the Browser history (which keeps (request, response))
        # otherwise it will consume a lot of memory after some time. Also it
        # does make sense to keep it as suites are independent of each other
        self._browser._history.clear()

      result.exitSuite(with_error)

      try:
        self._logger.info(str(result.getCurrentSuiteUseCaseStat()))
      except Exception:
        pass

    result.iterationFinished()

  def run(self):
    result_instance = self._result_klass(self._argument_namespace,
                                         self._nb_users,
                                         self._user_index,
                                         self._current_repeat_range)

    self._logger = result_instance.logger

    # Set up the source IP address in order to be more realistic (can be given
    # as the third element in userInfo.user_tuple) by monkey-patching
    # socket.socket() as mechanize doesn't provide a way to call bind after
    # creating the new socket and before calling connect()
    if self._source_ip:
      _socket = socket.socket
      def _patched_socket(*args, **kwargs):
        new_socket = _socket(*args, **kwargs)
        new_socket.bind((self._source_ip, 0))
        return new_socket

      socket.socket = _patched_socket

    # Ensure the data are flushed before exiting, handled by Result class 
    # __exit__ block
    signal.signal(signal.SIGTERM, self.stopGracefully)
 
    # Ignore KeyboardInterrupt as it is handled by the parent process
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    exit_status = 0
    exit_msg = None

    def runIteration(result):
      self._logger.info("Iteration: %d" % self._current_repeat)
      self.runBenchmarkSuiteList(result)
      if not self._current_repeat % REPEAT_NUMBER_BEFORE_FLUSHING:
        try:
          result.flush()
        except NothingFlushedException:
          pass

    try:
      with result_instance as result:
        self._browser = self.getBrowser(result_instance.log_file)
        if self._argument_namespace.duration > 0:
          self._logger.info("Iterate until duration %d" % self._argument_namespace.duration)
          start_time = time.time()
          while self._argument_namespace.duration > (time.time()-start_time):
            runIteration(result)
            self._current_repeat += 1
        else:
          self._logger.info("Iterate until repeat %d" % self._argument_namespace.repeat)
          while self._current_repeat != (self._argument_namespace.repeat + 1):
            runIteration(result)
            self._current_repeat += 1

    except StopIteration as e:
      self._logger.error(e)

    except RuntimeError as e:
      exit_msg = str(e)
      exit_status = 1

    except BaseException as e:
      exit_msg = traceback.format_exc()
      self._logger.error(exit_msg)
      exit_status = 2

    self._exit_msg_queue.put(exit_msg)
    sys.exit(exit_status)
