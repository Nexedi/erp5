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

import argparse
import os
import sys
import multiprocessing

from benchmark import ArgumentType, BenchmarkProcess

class PerformanceTester(object):
  def __init__(self, publish_method=None, namespace=None):
    if not namespace:
      self._argument_namespace = self._parse_arguments(argparse.ArgumentParser(
          description='Run ERP5 benchmarking suites.'))
    else:
      self._argument_namespace = namespace

    self._publish_method = publish_method

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

    parser.add_argument('--users-range-increment',
                        type=ArgumentType.strictlyPositiveIntType,
                        default=1,
                        metavar='N',
                        help='Number of users being added after each repetition '
                             '(default: 1)')

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
                        type=ArgumentType.strictlyPositiveIntType,
                        default=-1,
                        metavar='N',
                        help='Repeat the benchmark suite N times '
                             '(default: infinite)')

    parser.add_argument('--user-index',
                        type=int,
                        default=0,
                        metavar='INDEX',
                        help='Index of the first user within userInfo '
                             '(default: 0)')

    # Mandatory arguments
    parser.add_argument('url',
                        type=ArgumentType.ERP5UrlType,
                        metavar='URL',
                        help='ERP5 base URL')

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
    namespace.user_tuple = ArgumentType.objectFromModule(namespace.user_info_filename,
                                                         object_name='user_tuple')

    object_benchmark_suite_list = []
    for benchmark_suite in namespace.benchmark_suite_list:
      object_benchmark_suite_list.append(ArgumentType.objectFromModule(benchmark_suite,
                                                                       callable_object=True))

    namespace.benchmark_suite_list = object_benchmark_suite_list

    max_nb_users = isinstance(namespace.users, tuple) and namespace.users[1] or \
        namespace.users

    namespace.user_tuple = namespace.user_tuple[namespace.user_index:]
    if max_nb_users > len(namespace.user_tuple):
      raise argparse.ArgumentTypeError("Not enough users in the given file")

    return namespace

  @staticmethod
  def _parse_arguments(parser):
    PerformanceTester._add_parser_arguments(parser)
    namespace = parser.parse_args()
    PerformanceTester._check_parsed_arguments(namespace)
    return namespace

  def _run_constant(self, nb_users):
    process_list = []
    exit_msg_queue = multiprocessing.Queue(nb_users)

    for user_index in range(nb_users):
      process = BenchmarkProcess(exit_msg_queue, nb_users, user_index,
                                 self._argument_namespace,
                                 self._publish_method)
      process_list.append(process)

    for process in process_list:
      process.start()

    error_message_set = set()
    i = 0
    while i != len(process_list):
      try:
        msg = exit_msg_queue.get()
      except KeyboardInterrupt:
        if self._argument_namespace.repeat != -1:
          print >>sys.stderr, "Stopping gracefully"
          for process in process_list:
            process.terminate()

          i = 0
          continue

      if msg is not None:
        error_message_set.add(msg)
        for process in process_list:
          process.terminate()

        break

      i += 1

    if error_message_set:
      for error_message in error_message_set:
        print >>sys.stderr, "ERROR: %s" % error_message

      return 1

    return 0

  def run(self):
    if isinstance(self._argument_namespace.users, tuple):
      nb_users, max_users = self._argument_namespace.users
      while True:
        self._run_constant(nb_users)
        if nb_users == max_users:
          break

        nb_users = min(nb_users + self._argument_namespace.users_range_increment,
                       max_users)

      return 0
    else:
      return self._run_constant(self._argument_namespace.users)

def main():
  sys.exit(PerformanceTester().run())

if __name__ == '__main__':
  main()
