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

class BenchmarkResult(object):
  def __init__(self):
    self._stat_list = []
    self._suite_idx = 0
    self._result_idx = 0
    self._result_list = []
    self._first_iteration = True
    self._current_suite_name = None
    self._result_idx_checkpoint_list = []

  def enterSuite(self, name):
    self._current_suite_name = name

  def __call__(self, label, value):
    self._result_list.append(value)
    if self._first_iteration:
      self._stat_list.append(BenchmarkResultStatistic(self._current_suite_name,
                                                      label))

    self._stat_list[self._result_idx].add(value)
    self._result_idx += 1

  def exitSuite(self):
    if self._first_iteration:
      self._result_idx_checkpoint_list.append(self._result_idx)
    else:
      expected_result_idx = self._result_idx_checkpoint_list[self._suite_idx]
      while self._result_idx != expected_result_idx:
        self._result_list.append(0)
        self._stat_list[self._result_idx].add(0)
        self._result_idx += 1

    self._suite_idx += 1

  def getLabelList(self):
    self._first_iteration = False
    return [ stat.full_label for stat in self._stat_list ]

  def getResultList(self):
    self._suite_idx = 0
    self._result_idx = 0

    result_list = self._result_list
    self._result_list = []
    return result_list

  def getStatList(self):
    return self._stat_list

  def getCurrentSuiteStatList(self):
    start_index = self._suite_idx and \
        self._result_idx_checkpoint_list[self._suite_idx - 1] or 0

    return self._stat_list[start_index:self._result_idx]

import multiprocessing
import csv
import traceback
import os
import logging
import signal
import sys

from erp5.utils.test_browser.browser import Browser

class BenchmarkProcess(multiprocessing.Process):
  def __init__(self, exit_msg_queue, nb_users, user_index,
               argument_namespace, publish_method, *args, **kwargs):
    self._exit_msg_queue = exit_msg_queue
    self._nb_users = nb_users
    self._user_index = user_index
    self._argument_namespace = argument_namespace

    filename_prefix = self.getFilenamePrefix()

    self._result_filename = "%s.csv" % filename_prefix
    self._result_filename_path = os.path.join(
      self._argument_namespace.report_directory, self._result_filename)

    self._log_filename = "%s.log" % filename_prefix
    self._log_filename_path = os.path.join(
      self._argument_namespace.report_directory, self._log_filename)

    # Initialized when running the test
    self._csv_writer = None
    self._browser = None

    self._current_repeat = 1
    self._current_result = BenchmarkResult()
    self._publish_method = publish_method

    super(BenchmarkProcess, self).__init__(*args, **kwargs)

  def getFilenamePrefix(self):
    max_nb_users = isinstance(self._argument_namespace.users, int) and \
        self._argument_namespace.users or self._argument_namespace.users[1]

    fmt = "%%s-%%drepeat-%%0%ddusers-process%%0%dd" % \
        (len(str(max_nb_users)), len(str(self._nb_users)))

    return fmt % (self._argument_namespace.filename_prefix,
                  self._argument_namespace.repeat,
                  self._nb_users,
                  self._user_index)

  def stopGracefully(self, *args, **kwargs):
    raise StopIteration, "Interrupted by user"

  def getBrowser(self):
    info_list = tuple(self._argument_namespace.url) + \
        tuple(self._argument_namespace.user_tuple[self._user_index])

    return Browser(*info_list,
                   is_debug=self._argument_namespace.enable_debug,
                   log_filename=self._log_filename_path,
                   is_legacy_listbox=self._argument_namespace.is_legacy_listbox)

  def runBenchmarkSuiteList(self):
    for target_idx, target in enumerate(self._argument_namespace.benchmark_suite_list):
      self._logger.debug("EXECUTE: %s" % target)
      self._current_result.enterSuite(target.__name__)

      try:
        target(self._current_result, self._browser)
      except:
        msg = "%s: %s" % (target, traceback.format_exc())
        if self._current_repeat == 1:
          self._logger.error(msg)
          raise

        self._logger.warning(msg)

      for stat in self._current_result.getCurrentSuiteStatList():
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

          raise StopIteration, "See: %s" % self._log_filename_path

      self._current_result.exitSuite()

    if self._current_repeat == 1:
      self._csv_writer.writerow(self._current_result.getLabelList())

    result_list = self._current_result.getResultList()
    self._logger.debug("RESULTS: %s" % result_list)
    self._csv_writer.writerow(result_list)

  def getLogger(self):
    logging.basicConfig(filename=self._log_filename_path, filemode='w',
                        level=self._argument_namespace.enable_debug and \
                          logging.DEBUG or logging.INFO)

    return logging.getLogger('erp5.utils.benchmark')

  def run(self):
    self._logger = self.getLogger()

    if self._argument_namespace.repeat != -1:
      signal.signal(signal.SIGTERM, self.stopGracefully)

    try:
      self._browser = self.getBrowser()
    except:
      self._logger.error(traceback.format_exc())
      raise

    exit_status = 0
    exit_msg = None

    # Create the result CSV file
    with open(self._result_filename_path, 'wb') as result_file:
      self._csv_writer = csv.writer(result_file, delimiter=',',
                                    quoting=csv.QUOTE_MINIMAL)

      try:
        while self._current_repeat != (self._argument_namespace.repeat + 1):
          self._logger.info("Iteration: %d" % self._current_repeat)
          self.runBenchmarkSuiteList()
          self._current_repeat += 1

          if self._current_repeat == 5 and self._publish_method:
            result_file.flush()
            os.fsync(result_file.fileno())
            self._publish_method(self._result_filename, result_file.tell())

      except StopIteration, e:
        exit_msg = str(e)
        exit_status = 1

      except:
        self._logger.error(traceback.format_exc())
        exit_msg = "An error occured, see: %s" % self._log_filename_path
        exit_status = 2

      else:
        if self._publish_method:
          result_file.flush()
          os.fsync(result_file.fileno())
          self._publish_method(self._result_filename, result_file.tell())

    self._exit_msg_queue.put(exit_msg)
    sys.exit(exit_status)
