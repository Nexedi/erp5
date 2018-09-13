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
    self._variance_mean = 0

  def __str__(self):
    return "%s: min=%.3f, mean=%.3f (+/- %.3f), max=%.3f" % \
        (self.full_label,
         self.minimum,
         self.mean,
         self.standard_deviation,
         self.maximum)

  def add(self, value):
    if value < 0:
      self.error_sum += 1
      return

    if value < self.minimum:
      self.minimum = value
    if value > self.maximum:
      self.maximum = value

    self._value_sum += value
    self.n += 1

    delta = value - self._variance_mean
    self._variance_mean += delta / self.n
    self._variance_sum += delta * (value - self._variance_mean)

  @property
  def mean(self):
    if self.n == 0:
      self.n = 1
    return self._value_sum / self.n

  @property
  def standard_deviation(self):
    if self.n == 0:
      self.n = 1
    return math.sqrt(self._variance_sum / self.n)

class NothingFlushedException(Exception):
  pass

import abc
import time

class BenchmarkResult(object):
  __metaclass__ = abc.ABCMeta

  def __init__(self, argument_namespace, nb_users, user_index,
               current_repeat_range):
    self._argument_namespace = argument_namespace
    self._nb_users = nb_users
    self._user_index = user_index
    self._current_repeat_range = current_repeat_range

    self._logger = None
    self._label_list = None

    self._all_suite_list = []
    self._current_suite_index = 0
    self._all_result_list = []
    self._current_suite_dict = None
    self._current_result_list = None

  @property
  def logger(self):
    if not self._logger:
      logging.basicConfig(
        stream=self.log_file,
        level=(self._argument_namespace.enable_debug and
               logging.DEBUG or logging.INFO),
        format='%(asctime)s: %(levelname)s: %(message)s [%(name)s]')

      self._logger = logging.getLogger('erp5.util.benchmark')
      return self._logger

    return self._logger

  def __enter__(self):
    return self

  def enterSuite(self, name):
    self._current_use_case_elapsed_time = time.time()
    self._current_use_case_counter = 0

    try:
      self._current_suite_dict = self._all_suite_list[self._current_suite_index]

    except IndexError:
      self._current_suite_dict = {
        'name': name,
        'all_result_list': [],
        'stat_list': [],
        # Number of expected results
        'expected': -1,
        'all_use_case_result_list': [],
        'use_case_stat': BenchmarkResultStatistic(name, 'Use cases/minutes')}

      self._all_suite_list.append(self._current_suite_dict)

    self._current_result_list = []

  def __call__(self, label, value):
    try:
      result_statistic = \
          self._current_suite_dict['stat_list'][len(self._current_result_list)]
    except IndexError:
      result_statistic = BenchmarkResultStatistic(
        self._current_suite_dict['name'], label)

      self._current_suite_dict['stat_list'].append(result_statistic)

    result_statistic.add(value)
    self._current_result_list.append(value)

  def incrementCurrentSuiteUseCase(self):
    self._current_use_case_counter += 1

  @property
  def label_list(self):
    if self._label_list:
      return self._label_list

    # TODO: Should perhaps be cached...
    label_list = []
    for suite_dict in self._all_suite_list:
      if suite_dict['expected'] == -1:
        return None

      suite_label_list = [ stat.full_label for stat in suite_dict['stat_list']]
      suite_label_list.extend(('Use cases', 'Use cases seconds elapsed'))

      label_list.extend(suite_label_list)

    self._label_list = label_list
    return label_list

  def getCurrentSuiteStatList(self):
    return self._current_suite_dict['stat_list']

  def getCurrentSuiteUseCaseStat(self):
    return self._current_suite_dict['use_case_stat']

  @staticmethod
  def _addResultWithError(result_list, expected_len):
    missing_result_n = expected_len - len(result_list)
    if missing_result_n > 0:
      result_list.extend(missing_result_n * [-1])

  def exitSuite(self, with_error=False):
    elapsed_time = time.time() - self._current_use_case_elapsed_time

    if with_error:
      if self._current_suite_dict['expected'] != -1:
        self._addResultWithError(self._current_result_list,
                                 self._current_suite_dict['expected'])

    else:
      if self._current_use_case_counter == 0:
        self._current_use_case_counter = 1

      if self._current_suite_dict['expected'] == -1:
        self._current_suite_dict['expected'] = len(self._current_result_list)

        # Fix previous results
        for result_list in self._current_suite_dict['all_result_list']:
          self._addResultWithError(result_list,
                                   self._current_suite_dict['expected'])

    self._current_suite_dict['all_use_case_result_list'].append(
      (self._current_use_case_counter, elapsed_time))

    if self._current_use_case_counter != 0:
      self._current_suite_dict['use_case_stat'].add(
        self._current_use_case_counter / (elapsed_time / 60.0))

    self._current_suite_dict['all_result_list'].append(self._current_result_list)
    self._current_suite_index += 1

  def iterationFinished(self):
    self._current_suite_index = 0

  @abc.abstractmethod
  def flush(self, partial=True):
    # TODO: Should perhaps be cached...
    all_result_list = []
    for result_dict in self._all_suite_list:
      if result_dict['expected'] == -1:
        raise NothingFlushedException()

      for index, result_list in enumerate(result_dict['all_result_list']):
        result_list.extend(result_dict['all_use_case_result_list'][index])

        try:
          all_result_list[index].extend(result_list)
        except IndexError:
          all_result_list.append(result_list)

      result_dict['all_result_list'] = []
      result_dict['all_use_case_result_list'] = []

    return all_result_list

  @abc.abstractmethod
  def __exit__(self, exc_type, exc_value, traceback_object):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    try:
      self.flush(partial=False)
    except NothingFlushedException:
      pass

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
    if isinstance(self._argument_namespace.users, int):
      max_nb_users = self._argument_namespace.users
      suffix = ''
    else:
      max_nb_users = self._argument_namespace.users[1]
      suffix = '-rrepeat%%0%dd' % len(str(self._argument_namespace.repeat_range))

      suffix = suffix % self._current_repeat_range

    fmt = "%%s-%%drepeat-%%0%ddusers-process%%0%dd%s" % \
        (len(str(max_nb_users)), len(str(self._nb_users)),
         suffix)

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
    result_list = super(CSVBenchmarkResult, self).flush(partial)

    if self._result_file.tell() == 0:
      self._csv_writer.writerow(self.label_list)

    self._csv_writer.writerows(result_list)
    self._result_file.flush()
    os.fsync(self._result_file.fileno())

  def __exit__(self, exc_type, exc_value, traceback_object):
    super(CSVBenchmarkResult, self).__exit__(exc_type, exc_value,
                                             traceback_object)
    self._result_file.close()

    if exc_type and not issubclass(exc_type, StopIteration):
      msg = "An error occured, see: %s" % self._log_filename_path

      logged_msg = str(exc_value)
      if not issubclass(exc_type, RuntimeError):
        logged_msg += ''.join(traceback.format_tb(traceback_object))

      self.logger.error(logged_msg)
      raise RuntimeError(msg)

from cStringIO import StringIO

from six.moves import xmlrpc_client as xmlrpclib
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
    result_list = super(ERP5BenchmarkResult, self).flush()

    benchmark_result = xmlrpclib.ServerProxy(
      self._argument_namespace.erp5_publish_url,
      verbose=True,
      allow_none=True)

    benchmark_result.BenchmarkResult_addResultLineList(
      self._argument_namespace.user_tuple[self._user_index][0],
      self._argument_namespace.repeat,
      self._nb_users,
      self._argument_namespace.benchmark_suite_name_list,
      self.label_list,
      result_list,
      self._log_buffer_list)

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
