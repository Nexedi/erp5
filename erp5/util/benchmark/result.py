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

import sys
import math
import os
import csv
import logging
import signal
import traceback

class BenchmarkResultStatistic(object):
  def __init__(self, suite, label):
    self.suite = suite
    self.label = label

    self.full_label = '%s: %s' % (self.suite, self.label)

    self.minimum = sys.maxint
    self.maximum = -1
    self.n = 0
    self.error_sum = 0

    # For calculating the mean
    self._value_sum = 0

    # For calculating the standard deviation
    self._variance_sum = 0
    self._mean = 0

  def add_error(self):
    self.error_sum += 1

  def add(self, value):
    if value < self.minimum:
      self.minimum = value
    if value > self.maximum:
      self.maximum = value

    self._value_sum += value
    self.n += 1

    delta = value - self._mean
    self._mean += delta / self.n
    self._variance_sum += delta * (value - self._mean)

  @property
  def mean(self):
    return self._value_sum / self.n

  @property
  def standard_deviation(self):
    return math.sqrt(self._variance_sum / self.n)

import abc

class BenchmarkResult(object):
  __metaclass__ = abc.ABCMeta

  def __init__(self, argument_namespace, nb_users, user_index):
    self._argument_namespace = argument_namespace
    self._nb_users = nb_users
    self._user_index = user_index
    self._stat_list = []
    self._suite_idx = 0
    self._result_idx = 0
    self.result_list = []
    self._all_result_list = []
    self._first_iteration = True
    self._current_suite_name = None
    self._result_idx_checkpoint_list = []
    self.label_list = []
    self._logger = None

  @property
  def logger(self):
    if not self._logger:
      logging.basicConfig(stream=self.log_file,
                          level=(self._argument_namespace.enable_debug and
                                 logging.DEBUG or logging.INFO))

      self._logger = logging.getLogger('erp5.util.benchmark')
      return self._logger

    return self._logger

  def __enter__(self):
    return self

  def enterSuite(self, name):
    self._current_suite_name = name

  def __call__(self, label, value):
    self.result_list.append(value)

    try:
      result_statistic = self._stat_list[self._result_idx]
    except IndexError:
      result_statistic = BenchmarkResultStatistic(self._current_suite_name,
                                                  label)

      self._stat_list.append(result_statistic)

    result_statistic.add(value)
    self._result_idx += 1

  def getLabelList(self):
    return [ stat.full_label for stat in self._stat_list ]

  def iterationFinished(self):
    self._all_result_list.append(self.result_list)
    if self._first_iteration:
      self.label_list = self.getLabelList()

    self.logger.debug("RESULTS: %s" % self.result_list)
    self.result_list = []
    self._first_iteration = False
    self._suite_idx = 0
    self._result_idx = 0

  def getCurrentSuiteStatList(self):
    start_index = self._suite_idx and \
        self._result_idx_checkpoint_list[self._suite_idx - 1] or 0

    return self._stat_list[start_index:self._result_idx]

  def exitSuite(self):
    if self._first_iteration:
      self._result_idx_checkpoint_list.append(self._result_idx)
    else:
      expected_result_idx = self._result_idx_checkpoint_list[self._suite_idx]
      while self._result_idx != expected_result_idx:
        self.result_list.append(0)
        self._stat_list[self._result_idx].add_error()
        self._result_idx += 1

    self._suite_idx += 1

  @abc.abstractmethod
  def flush(self, partial=True):
    self._all_result_list = []

  @abc.abstractmethod
  def __exit__(self, exc_type, exc_value, traceback_object):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    self.flush(partial=False)
    return True

class CSVBenchmarkResult(BenchmarkResult):
  def __init__(self, *args, **kwargs):
    super(CSVBenchmarkResult, self).__init__(*args, **kwargs)

    filename_prefix = self._getFilenamePrefix()

    self._result_filename = "%s.csv" % filename_prefix
    self._result_filename_path = os.path.join(
      self._argument_namespace.report_directory, self._result_filename)

    self._log_filename = "%s.log" % filename_prefix
    self._log_filename_path = os.path.join(
      self._argument_namespace.report_directory, self._log_filename)

    self.log_file = open(self._log_filename_path, 'w')

  def _getFilenamePrefix(self):
    max_nb_users = isinstance(self._argument_namespace.users, int) and \
        self._argument_namespace.users or self._argument_namespace.users[1]

    fmt = "%%s-%%drepeat-%%0%ddusers-process%%0%dd" % \
        (len(str(max_nb_users)), len(str(self._nb_users)))

    return fmt % (self._argument_namespace.filename_prefix,
                  self._argument_namespace.repeat,
                  self._nb_users,
                  self._user_index)

  def __enter__(self):
    self._result_file = open(self._result_filename_path, 'wb')
    self._csv_writer = csv.writer(self._result_file, delimiter=',',
                                  quoting=csv.QUOTE_MINIMAL)

    return self

  def flush(self, partial=True):
    if self._result_file.tell() == 0:
      self._csv_writer.writerow(self.label_list)

    self._csv_writer.writerows(self._all_result_list)
    self._result_file.flush()
    os.fsync(self._result_file.fileno())

    super(CSVBenchmarkResult, self).flush(partial)

  def __exit__(self, exc_type, exc_value, traceback_object):
    super(CSVBenchmarkResult, self).__exit__(exc_type, exc_value,
                                             traceback_object)
    self._result_file.close()

    if exc_type and not issubclass(exc_type, StopIteration):
      msg = "An error occured, see: %s" % self._log_filename_path
      self.logger.error("%s:\n%s" % (exc_value,
                                     ''.join(traceback.format_tb(traceback_object))))
      raise RuntimeError(msg)

from cStringIO import StringIO

import xmlrpclib
import datetime

class ERP5BenchmarkResult(BenchmarkResult):
  def __init__(self, *args, **kwargs):
    self.log_file = StringIO()
    self._log_buffer_list = []

    super(ERP5BenchmarkResult, self).__init__(*args, **kwargs)

  def iterationFinished(self):
    super(ERP5BenchmarkResult, self).iterationFinished()

    # TODO: garbage?
    self._log_buffer_list.append(self.log_file.getvalue())
    self.log_file.seek(0)

  def flush(self, partial=True):
    benchmark_result = xmlrpclib.ServerProxy(
      self._argument_namespace.erp5_publish_url,
      verbose=True,
      allow_none=True)

    benchmark_result.BenchmarkResult_addResultLineList(
      self._argument_namespace.user_tuple[self._user_index][0],
      self._argument_namespace.repeat,
      self._nb_users,
      self._argument_namespace.benchmark_suite_name_list,
      self.getLabelList(),
      self._all_result_list,
      self._log_buffer_list)

    super(ERP5BenchmarkResult, self).flush()

  def __exit__(self, exc_type, exc_value, traceback_object):
    super(ERP5BenchmarkResult, self).__exit__(exc_type, exc_value,
                                              traceback_object)

  @staticmethod
  def createResultDocument(publish_url, publish_project, repeat, nb_users):
    test_result_module = xmlrpclib.ServerProxy(publish_url,
                                               verbose=True,
                                               allow_none=True)

    if isinstance(nb_users, tuple):
      nb_users_str = '%d to %d' % nb_users
    else:
      nb_users_str = '%d' % nb_users

    benchmark_result = test_result_module.TestResultModule_addBenchmarkResult(
      '%d repeat with %s concurrent users' % (repeat, nb_users_str),
      publish_project, ' '.join(sys.argv), datetime.datetime.now())

    return benchmark_result['id']

  @staticmethod
  def closeResultDocument(publish_document_url, error_message_set):
    result = xmlrpclib.ServerProxy(publish_document_url,
                                   verbose=True,
                                   allow_none=True)

    result.BenchmarkResult_completed(error_message_set and 'FAIL' or 'PASS',
                                     error_message_set)
