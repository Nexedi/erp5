#!/usr/bin/env python

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

from __future__ import print_function
import argparse
import os
import sys
import multiprocessing
import errno

from .argument import ArgumentType
from .process import BenchmarkProcess
from .result import ERP5BenchmarkResult, CSVBenchmarkResult

MAXIMUM_KEYBOARD_INTERRUPT = 5

class PerformanceTester(object):
  def __init__(self, namespace=None):
    if not namespace:
      self._argument_namespace = self._parse_arguments(argparse.ArgumentParser(
          description='Run ERP5 benchmarking suites.'))
    else:
      self._argument_namespace = namespace

  @staticmethod
  def _add_parser_arguments(parser):
    # Optional arguments
    parser.add_argument('--filename-prefix',
                        default='result',
                        metavar='PREFIX',
                        help='Filename prefix for results and logs files '
                             '(default: result)')

    parser.add_argument('--report-directory', '-r',
                        type=ArgumentType.directoryType,
                        default=os.getcwd(),
                        metavar='DIRECTORY',
                        help='Directory where the results and logs will be stored '
                             '(default: current directory)')

    parser.add_argument('--max-global-average',
                        type=float,
                        default=0,
                        metavar='N',
                        help='Stop when any suite operation is over this value '
                             '(default: disable)')

    parser.add_argument('--users-file',
                        dest='user_info_filename',
                        default='userInfo',
                        metavar='MODULE',
                        help="Import users from ``user_tuple'' in MODULE")

    parser.add_argument('--users-file-path',
                        metavar='USER_FILE_PATH',
                        help='User file path')

    parser.add_argument('--users-range-increment',
                        type=ArgumentType.checkIntValueWrapper(minimum=1),
                        default=1,
                        metavar='N',
                        help='Number of users being added after each repetition '
                             '(default: 1)')

    parser.add_argument('--max-errors',
                        dest='max_error_number',
                        type=ArgumentType.checkIntValueWrapper(minimum=0),
                        default=10,
                        help='Stop execution after N consecutive errors '
                             '(default: 10)')

    parser.add_argument('--enable-debug', '-d',
                        action='store_true',
                        default=False,
                        help='Enable debug messages')

    parser.add_argument('--enable-legacy-listbox',
                        dest='is_legacy_listbox',
                        action='store_true',
                        default=False,
                        help='Enable legacy listbox for Browser')

    parser.add_argument('--repeat',
                        type=ArgumentType.checkIntValueWrapper(minimum=1),
                        default=-1,
                        metavar='N',
                        help='Repeat the benchmark suite N times for a given '
                             'number of users (default: infinite)')

    parser.add_argument('--duration',
                        type=int,
                        default=0,
                        help='Repeat the benchmark suite until time duration is reached')

    parser.add_argument('--repeat-range',
                        type=ArgumentType.checkIntValueWrapper(minimum=1),
                        default=-1,
                        metavar='N',
                        help='Repeat the benchmark suite N times for the whole '
                             'range of users (default: infinite)')

    parser.add_argument('--user-index',
                        type=int,
                        default=0,
                        metavar='INDEX',
                        help='Index of the first user within userInfo '
                             '(default: 0)')

    parser.add_argument('--erp5-publish-url',
                        metavar='ERP5_PUBLISH_URL',
                        help='ERP5 URL to publish the results to '
                             '(default: disabled, thus writing to CSV files)')

    parser.add_argument('--erp5-publish-project',
                        metavar='ERP5_PUBLISH_PROJECT',
                        help='ERP5 publish project')


    parser.add_argument('--benchmark-path-list',
                        default=[],
                        nargs='+',
                        metavar='BENCHMARK_PATH',
                        help='Benchmark paths')

    # Mandatory arguments
    parser.add_argument('erp5_base_url', metavar='ERP5_URL')

    parser.add_argument('users',
                        type=ArgumentType.strictlyPositiveIntOrRangeType,
                        metavar='NB_USERS|MIN_NB_USERS,MAX_NB_USERS',
                        help='Number of users (fixed or a range)')

    parser.add_argument('benchmark_suite_list',
                        nargs='+',
                        metavar='BENCHMARK_SUITES',
                        help='Benchmark suite modules')


  @staticmethod
  def _check_parsed_arguments(namespace):
    if namespace.users_file_path:
      users_file_path_list = [namespace.users_file_path]
    else:
      users_file_path_list = []
    namespace.user_tuple = ArgumentType.objectFromModule(namespace.user_info_filename,
                                                         object_name='user_tuple',
                                                         searchable_path_list=users_file_path_list)

    namespace.benchmark_suite_list = namespace.benchmark_suite_list[0].split(" ")

    object_benchmark_suite_list = []
    for benchmark_suite in namespace.benchmark_suite_list:
      object_benchmark_suite_list.append(ArgumentType.objectFromModule(benchmark_suite,
                                                                       callable_object=True,
                                                                       searchable_path_list=namespace.benchmark_path_list))

    if namespace.repeat > 0:
      namespace.max_error_number = \
          min(len(namespace.benchmark_suite_list) * namespace.repeat,
              namespace.max_error_number)

    if isinstance(namespace.users, tuple) and namespace.repeat == -1:
        raise argparse.ArgumentTypeError("Repeat cannot be infinite for a "
                                         "range of users")

    namespace.benchmark_suite_name_list = namespace.benchmark_suite_list
    namespace.benchmark_suite_list = object_benchmark_suite_list

    max_nb_users = isinstance(namespace.users, tuple) and namespace.users[1] or \
        namespace.users

    namespace.user_tuple = namespace.user_tuple[namespace.user_index:]
    if max_nb_users > len(namespace.user_tuple):
      raise argparse.ArgumentTypeError("Not enough users in the given file")

    if (namespace.erp5_publish_url and not namespace.erp5_publish_project) or \
       (not namespace.erp5_publish_url and namespace.erp5_publish_project):
      raise argparse.ArgumentTypeError("Publish ERP5 URL and project must "
                                       "be specified")

    return namespace

  @staticmethod
  def _parse_arguments(parser):
    PerformanceTester._add_parser_arguments(parser)
    namespace = parser.parse_args()
    PerformanceTester._check_parsed_arguments(namespace)
    return namespace

  def getResultClass(self):
    if self._argument_namespace.erp5_publish_url:
      return ERP5BenchmarkResult
    else:
      return CSVBenchmarkResult

  def preRun(self):
    if not self._argument_namespace.erp5_publish_url:
      return

    self._argument_namespace.erp5_publish_url += \
        ERP5BenchmarkResult.createResultDocument(self._argument_namespace.erp5_publish_url,
                                                 self._argument_namespace.erp5_publish_project,
                                                 self._argument_namespace.repeat,
                                                 self._argument_namespace.users)

  def postRun(self, error_message_set):
    if not self._argument_namespace.erp5_publish_url:
      return

    ERP5BenchmarkResult.closeResultDocument(self._argument_namespace.erp5_publish_url,
                                            error_message_set)

  def _run_constant(self, nb_users, current_repeat_range=None):
    process_list = []
    exit_msg_queue = multiprocessing.Queue(nb_users)

    result_class = self.getResultClass()

    for user_index in range(nb_users):
      process = BenchmarkProcess(exit_msg_queue, result_class,
                                 self._argument_namespace, nb_users,
                                 user_index,
                                 current_repeat_range)

      process_list.append(process)

    for process in process_list:
      process.start()

    error_message_set = set()
    process_terminated_counter = 0

    # Ensure that SIGTERM signal (sent by terminate()) is not sent twice
    exit_status = 0

    while process_terminated_counter != len(process_list):
      try:
        error_message = exit_msg_queue.get()

      except KeyboardInterrupt as e:
        print("\nInterrupted by user, stopping gracefully...", file=sys.stderr)
        exit_status = 2

      # An IOError may be raised  when receiving a SIGINT which interrupts the
      # blocking system call above and the system call should not be restarted
      # (using siginterrupt), otherwise the  process will stall forever as its
      # child has already exited
      except IOError as e:
        if e.errno == errno.EINTR:
          continue

      else:
        if error_message is not None:
          error_message_set.add(error_message)
          exit_status = 1

        process_terminated_counter += 1

      # In case of  error or SIGINT, kill the other  children because they are
      # likely failing as well (especially  because a process only exits after
      # encountering 10 errors)
      if exit_status != 0:
        for process in process_list:
          if process.is_alive():
            process.terminate()
            process.join()

    return (error_message_set, exit_status)

  def run(self):
    error_message_set, exit_status = set(), 0
    self.preRun()

    if isinstance(self._argument_namespace.users, tuple):
      min_user_number, max_user_number = self._argument_namespace.users
      repeat_counter = 0
      error_counter = 0

      while (repeat_counter != self._argument_namespace.repeat_range and
             error_counter != self._argument_namespace.max_error_number and
             exit_status != 2):
        current_user_number = min_user_number

        while True:
          current_error_message_set, exit_status = \
              self._run_constant(current_user_number, repeat_counter)

          if exit_status != 0:
            error_counter += 1
            error_message_set.update(current_error_message_set)

          if (current_user_number == max_user_number or
              error_counter == self._argument_namespace.max_error_number or
              exit_status == 2):
            break

          current_user_number = \
              min((current_user_number +
                   self._argument_namespace.users_range_increment),
                  max_user_number)

        repeat_counter += 1

    else:
      error_message_set, exit_status = self._run_constant(
        self._argument_namespace.users)

    self.postRun(error_message_set)
    return error_message_set, exit_status

def main():
  error_message_set, exit_status = PerformanceTester().run()
  for error_message in error_message_set:
    print("ERROR: %s" % error_message, file=sys.stderr)

  sys.exit(exit_status)

if __name__ == '__main__':
  main()
