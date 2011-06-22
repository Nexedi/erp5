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
import functools

class ArgumentType(object):
  @classmethod
  def directoryType(cls, path):
    if not (os.path.isdir(path) and os.access(path, os.W_OK)):
      raise argparse.ArgumentTypeError("'%s' is not a valid directory or is "\
                                         "not writable" % path)

    return path

  @classmethod
  def objectFromModule(cls, module_name, object_name=None,
                       callable_object=False):
    if module_name.endswith('.py'):
      module_name = module_name[:-3]

    if not object_name:
      object_name = module_name

    import sys
    sys.path.append(os.getcwd())

    try:
      module = __import__(module_name, globals(), locals(), [object_name], -1)
    except Exception, e:
      raise argparse.ArgumentTypeError("Cannot import '%s.%s': %s" % \
                                         (module_name, object_name, str(e)))

    try:
      obj = getattr(module, object_name)
    except AttributeError:
      raise argparse.ArgumentTypeError("Could not get '%s' in '%s'" % \
                                         (object_name, module_name))

    if callable_object and not callable(obj):
      raise argparse.ArgumentTypeError(
        "'%s.%s' is not callable" % (module_name, object_name))

    return obj

  @classmethod
  def strictlyPositiveIntType(cls, value):
    try:
      converted_value = int(value)
    except ValueError:
      pass
    else:
      if converted_value > 0:
        return converted_value

    raise argparse.ArgumentTypeError('expects a strictly positive integer')

  @classmethod
  def strictlyPositiveIntOrRangeType(cls, value):
    try:
      return cls.strictlyPositiveIntType(value)
    except argparse.ArgumentTypeError:
      try:
        min_max_list = value.split(',')
      except ValueError:
        pass
      else:
        if len(min_max_list) == 2:
          minimum, maximum = cls.strictlyPositiveIntType(min_max_list[0]), \
              cls.strictlyPositiveIntType(min_max_list[1])

          if minimum >= maximum:
            raise argparse.ArgumentTypeError('%d >= %d' % (minimum, maximum))

          return (minimum, maximum)

    raise argparse.ArgumentTypeError(
      'expects either a strictly positive integer or a range of strictly '
      'positive integer separated by a comma')

  @classmethod
  def ERP5UrlType(cls, url):
    if url[-1] == '/':
      url_list = url.rsplit('/', 2)[:-1]
    else:
      url_list = url.rsplit('/', 1)

    url_list[0] = url_list[0] + '/'
    if len(url_list) != 2:
      raise argparse.ArgumentTypeError("Invalid URL given")

    return url_list

import sys
import math

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

  def add(self, value):
    if value == 0:
      self.error_sum += 1
      return

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

    self._log_level = self._argument_namespace.enable_debug and \
        logging.DEBUG or logging.INFO

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

  def getLogger(self):
    if not self._logger:
      logging.basicConfig(stream=self.log_file, level=self._log_level)
      return logging.getLogger('erp5.utils.benchmark')

    return self._logger

  def __enter__(self):
    return self

  def enterSuite(self, name):
    self._current_suite_name = name

  def __call__(self, label, value):
    self.result_list.append(value)
    if self._first_iteration:
      self._stat_list.append(BenchmarkResultStatistic(self._current_suite_name,
                                                      label))

    self._stat_list[self._result_idx].add(value)
    self._result_idx += 1

  def getLabelList(self):
    return [ stat.full_label for stat in self._stat_list ]

  def iterationFinished(self):
    self._all_result_list.append(self.result_list)
    if self._first_iteration:
      self.label_list = self.getLabelList()

    self.getLogger().debug("RESULTS: %s" % self.result_list)
    self.result_list = []
    self._first_iteration = False
    self._suite_idx = 0
    self._result_idx = 0

  def getStatList(self):
    return self._stat_list

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
        self._stat_list[self._result_idx].add(0)
        self._result_idx += 1

    self._suite_idx += 1

  @abc.abstractmethod
  def flush(self):
    self._all_result_list = []

  @abc.abstractmethod
  def __exit__(self, exc_type, exc_value, traceback):
    self.flush()
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

  def flush(self):
    if self._result_file.tell() == 0:
      self._csv_writer.writerow(self.label_list)

    self._csv_writer.writerows(self._all_result_list)
    self._result_file.flush()
    os.fsync(self._result_file.fileno())

    super(CSVBenchmarkResult, self).flush()

  def __exit__(self, exc_type, exc_value, traceback):
    super(CSVBenchmarkResult, self).__exit__(exc_type, exc_value, traceback)
    self._result_file.close()

    if exc_type:
      msg = "An error occured, see: %s" % self._log_filename_path
      self.getLogger().error("%s: %s\n%s" % (exc_type, exc_value, traceback))
      if isinstance(exc_type, StopIteration):
        raise StopIteration, msg
      else:
        raise RuntimeError, msg

from cStringIO import StringIO

import xmlrpclib

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

  def flush(self):
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

  def __exit__(self, exc_type, exc_value, traceback):
    super(ERP5BenchmarkResult, self).__exit__(exc_type, exc_value, traceback)

import multiprocessing
import csv
import traceback
import os
import logging
import signal
import sys

from erp5.utils.test_browser.browser import Browser

class BenchmarkProcess(multiprocessing.Process):
  def __init__(self, exit_msg_queue, result_klass, argument_namespace,
               nb_users, user_index, *args, **kwargs):
    self._exit_msg_queue = exit_msg_queue
    self._result_klass = result_klass
    self._argument_namespace = argument_namespace
    self._nb_users = nb_users
    self._user_index = user_index

    # Initialized when running the test
    self._browser = None
    self._current_repeat = 1

    super(BenchmarkProcess, self).__init__(*args, **kwargs)

  def stopGracefully(self, *args, **kwargs):
    raise StopIteration, "Interrupted by user"

  def getBrowser(self, log_file):
    info_list = tuple(self._argument_namespace.url) + \
        tuple(self._argument_namespace.user_tuple[self._user_index])

    return Browser(*info_list,
                   is_debug=self._argument_namespace.enable_debug,
                   log_file=log_file,
                   is_legacy_listbox=self._argument_namespace.is_legacy_listbox)

  def runBenchmarkSuiteList(self, result):
    for target_idx, target in enumerate(self._argument_namespace.benchmark_suite_list):
      self._logger.debug("EXECUTE: %s" % target)
      result.enterSuite(target.__name__)

      try:
        target(result, self._browser)
      except:
        msg = "%s: %s" % (target, traceback.format_exc())
        if self._current_repeat == 1:
          self._logger.error(msg)
          raise

        self._logger.warning(msg)

      for stat in result.getCurrentSuiteStatList():
        mean = stat.mean

        self._logger.info("%s: min=%.3f, mean=%.3f (+/- %.3f), max=%.3f" % \
                            (stat.full_label,
                             stat.minimum,
                             mean,
                             stat.standard_deviation,
                             stat.maximum))

        if self._argument_namespace.max_global_average and \
           mean > self._argument_namespace.max_global_average:
          self._logger.info("Stopping as mean is greater than maximum "
                            "global average")

          raise StopIteration

      result.exitSuite()

    result.iterationFinished()

  def run(self):
    result_instance = self._result_klass(self._argument_namespace,
                                         self._nb_users,
                                         self._user_index)

    self._logger = result_instance.getLogger()

    if self._argument_namespace.repeat != -1:
      signal.signal(signal.SIGTERM, self.stopGracefully)

    try:
      self._browser = self.getBrowser(result_instance.log_file)
    except:
      self._logger.error(traceback.format_exc())
      raise

    exit_status = 0
    exit_msg = None

    # Create the result CSV file
    try:
      with result_instance as result:
        while self._current_repeat != (self._argument_namespace.repeat + 1):
          self._logger.info("Iteration: %d" % self._current_repeat)
          self.runBenchmarkSuiteList(result)
          self._current_repeat += 1

          if self._current_repeat == 100:
            result.flush()

    except StopIteration, e:
      exit_msg = str(e)
      exit_status = 1

    except Exception, e:
      exit_msg = e
      exit_status = 2

    self._exit_msg_queue.put(exit_msg)
    sys.exit(exit_status)
