#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# First version: ERP5Mechanize from Vincent Pelletier <vincent@nexedi.com>
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
import re
import six

def parseArguments():
  parser = argparse.ArgumentParser(
    description='Generate reports for ERP5 benchmarking suites.')

  parser.add_argument('--enable-debug',
                      dest='is_debug',
                      action='store_true',
                      default=False,
                      help='Enable debug messages')

  parser.add_argument('--filename-prefix',
                      default='result',
                      metavar='PREFIX',
                      help='Filename prefix for results CSV files '
                           '(default: result)')

  parser.add_argument('--output-filename',
                      default='results.pdf',
                      metavar='FILENAME',
                      help='PDF output file (default: results.pdf)')

  parser.add_argument('--merge-identical-labels',
                      dest='do_merge_label',
                      action='store_true',
                      default=False,
                      help='Merge identical labels (default: False)')

  parser.add_argument('--ignore-labels-regex',
                      dest='ignore_label_re',
                      type=re.compile,
                      help='Ignore labels with the specified regex')
  
  parser.add_argument('--only-average-plots',
                      dest='only_average',
                      action='store_true',
                      default=False,
                      help='Do not create maximum and minimum plots, '
                           'only average (with standard deviation)')

  parser.add_argument('report_directory',
                      help='Reports directory')

  namespace = parser.parse_args()

  return namespace

import csv
import collections

from .result import BenchmarkResultStatistic

def computeStatisticFromFilenameList(argument_namespace, filename_list,
                                     range_user_report_dict,
                                     is_range_user=False):
  reader_list = []
  ignore_result_set = set()
  stat_list = []
  use_case_suite_dict = collections.OrderedDict()
  row_use_case_mapping_dict = {}
  label_list = []
  merged_label_dict = {}

  for filename in filename_list:
    reader = csv.reader(open(filename, 'r'), delimiter=',',
                        quoting=csv.QUOTE_MINIMAL)
    reader_list.append(reader)

    # Get headers
    if str is bytes:
      row_list = [row.decode('utf-8') for row in next(reader)]
    else:
      row_list = [list(next(reader))]
    if not label_list:
      label_list = row_list
      label_merged_index = 0
      for index, label in enumerate(label_list):
        if (argument_namespace.ignore_label_re and
            argument_namespace.ignore_label_re.match(label)):
          ignore_result_set.add(index)
          continue

        try:
          suite_name, result_name = label.split(': ', 1)
        except ValueError:
          # This is an use case as all results are prefixed by the suite
          # name and they are two fields (count and time elapsed)
          #
          # TODO: Assuming that there was at least one test result
          #       before
          if suite_name in use_case_suite_dict:
            continue

          duration_stat_list = []

          use_case_suite_dict[suite_name] = {'duration_stats': duration_stat_list,
                                             'count_stats': []}

          row_use_case_mapping_dict[index] = suite_name

          if is_range_user:
            report_dict['use_cases'].append({
                'count': 0,
                'duration_stats': duration_stat_list})
        else:
          if argument_namespace.do_merge_label:
            if label in merged_label_dict:
              continue

            merged_label_dict[label] = label_merged_index
            label_merged_index += 1

          stat = BenchmarkResultStatistic(suite_name, result_name)
          stat_list.append(stat)

          if is_range_user:
            report_dict = range_user_report_dict.setdefault(
              suite_name,
              {'results': collections.OrderedDict(),
               'use_cases': []})          

            report_dict['results'].setdefault(stat.full_label, []).append(stat)

    if row_list != label_list:
      raise AssertionError("ERROR: Result labels: %s != %s" %
          (label_list, row_list))

    iteration_index = 0
    for row_list in reader:
      row_iter = iter(enumerate(row_list))
      for idx, row in row_iter:
        if idx in ignore_result_set:
          continue

        use_case_suite = row_use_case_mapping_dict.get(idx, None)
        if use_case_suite:
          current_count = int(row)
          current_duration = float(next(row_iter)[1]) / 3600
          if not current_count:
            continue

          # For stats by iteration, used later on to generate cases per
          # hours plot for a given number of users
          by_iteration_dict = use_case_suite_dict[use_case_suite]
          count_stat_list = by_iteration_dict['count_stats']
          duration_stat_list = by_iteration_dict['duration_stats']

          try:
            stat_count = count_stat_list[iteration_index]
            stat_duration = duration_stat_list[iteration_index]
          except IndexError:
            stat_count = BenchmarkResultStatistic(use_case_suite,
                                                  'Use cases count')

            count_stat_list.append(stat_count)

            stat_duration = BenchmarkResultStatistic(use_case_suite,
                                                     'Time elapsed')

            duration_stat_list.append(stat_duration)

          stat_count.add(current_count)
          stat_duration.add(current_duration)

          # For total stats, used later on to generate the number of
          # cases/hour per users
          if is_range_user:
            total_dict = range_user_report_dict[use_case_suite]['use_cases'][-1]
            total_dict['count'] += current_count
        else:
          index = merged_label_dict.get(label_list[idx], idx)
          stat_list[index].add(float(row))

      iteration_index += 1

  return stat_list, use_case_suite_dict

def formatFloatList(value_list):
  return [ format(value, ".3f") for value in value_list ]

import numpy
import pylab

from matplotlib import pyplot, ticker

def drawDecorator(xlabel, ylabel, with_table=False):
  def inner(f):
    def decorate(pdf, title, *args, **kwargs):
      # Create the figure
      figure = pyplot.figure(figsize=(11.69, 8.29))

      if with_table:
        figure.subplots_adjust(bottom=0.13, right=0.98, top=0.95)
      else:
        figure.subplots_adjust(bottom=0.1, right=0.98, left=0.07, top=0.95)

      pyplot.title(title)

      pyplot.grid(True, linewidth=1.5)

      # Create the axes
      axes = figure.add_subplot(111)

      x_major, x_minor, y_major, y_minor = f(axes, *args, **kwargs)

      if x_major:
        axes.xaxis.set_major_locator(x_major)
        axes.xaxis.grid(True, 'minor')
      if x_minor:
        axes.xaxis.set_minor_locator(x_minor)

      if y_major:
        axes.yaxis.set_major_locator(y_major)
        axes.yaxis.grid(True, 'minor')
      if y_minor:
        axes.yaxis.set_minor_locator(y_minor)

      # Display legend at the best position
      axes.legend(loc=0)

      # Add axes labels
      if xlabel:
        axes.set_xlabel(xlabel)
      if ylabel:
        axes.set_ylabel(ylabel)

      # Adjust X and Y axes automatically
      if not with_table:
        axes.relim()
        axes.autoscale_view(True, True, True)

      pdf.savefig()
      pylab.close()

    return decorate

  return inner

def forceZeroBarDrawing(result_list):
  """
  Dirty hack to draw a bar even if the value is zero, otherwise nothing is
  drawn and bars are not properly aligned
  """
  no_zero_list = []
  zero_count = 0
  for value in result_list:
    if value == 0:
      value = 1e-20
      zero_count += 1

    no_zero_list.append(value)

  if len(result_list) == zero_count:
    return result_list

  return no_zero_list

@drawDecorator(xlabel=None, ylabel='Seconds', with_table=True)
def drawBarDiagram(axes, stat_list, only_average=False):
  mean_list = []
  yerr_list = []
  minimum_list = []
  maximum_list = []
  label_list = []
  error_list = []

  for stat in stat_list:
    mean_list.append(stat.mean)
    yerr_list.append(stat.standard_deviation)
    minimum_list.append(stat.minimum)
    maximum_list.append(stat.maximum)
    label_list.append(stat.label)
    error_list.append(stat.error_sum)

  min_array = numpy.array(minimum_list)
  mean_array = numpy.array(mean_list)
  max_array = numpy.array(maximum_list)

  yerr_lower = numpy.minimum(mean_array - min_array, yerr_list)
  yerr_upper = numpy.minimum(max_array - mean_array, yerr_list)

  ## Draw diagrams
  axes.set_xticks([])

  # Create the bars
  ind = numpy.arange(len(label_list))

  if only_average:
    width = 1
    avg_rect_position = ind
  else:
    width = 0.33
    avg_rect_position = ind + width

  avg_rects = axes.bar(avg_rect_position, forceZeroBarDrawing(mean_list),
                       width, color='r', label='Mean')

  axes.errorbar(numpy.arange(0.5, len(stat_list)), mean_list,
                yerr=[yerr_lower, yerr_upper], fmt=None,
                label='Standard deviation')

  if not only_average:
    min_rects = axes.bar(ind, forceZeroBarDrawing(minimum_list),
                         width, color='y', label='Minimum')

    max_rects = axes.bar(ind + width * 2, forceZeroBarDrawing(maximum_list),
                         width, label='Maximum', color='g')

  axes.table(rowLabels=['Minimum', 'Average', 'Std. deviation', 'Maximum', 'Errors'],
             colLabels=label_list,
             cellText=[formatFloatList(minimum_list),
                       formatFloatList(mean_list),
                       formatFloatList(yerr_list),
                       formatFloatList(maximum_list),
                       error_list],
             rowColours=('y', 'r', 'b', 'g', 'w'),
             loc='bottom',
             colLoc='center',
             rowLoc='center',
             cellLoc='center')

  return (None, None,
          ticker.MaxNLocator(nbins=20), ticker.AutoMinorLocator())

@drawDecorator(xlabel='Time (in hours)',
               ylabel='Use cases')
def drawUseCasePerNumberOfUserPlot(axes,
                                   nb_users,
                                   use_case_count_list,
                                   time_elapsed_list,
                                   is_single_plot=False,
                                   only_average=False):
  def get_cum_stat(stat_list, process_function=lambda x: x):
    cum_min_list = []
    cum_min = 0
    cum_mean_list = []
    cum_mean = 0
    cum_max_list = []
    cum_max = 0
    for stat in stat_list:
      cum_min += process_function(stat.minimum)
      cum_min_list.append(cum_min)

      cum_mean += process_function(stat.mean)
      cum_mean_list.append(cum_mean)

      cum_max += process_function(stat.maximum)
      cum_max_list.append(cum_max)

    return cum_min_list, cum_mean_list, cum_max_list

  use_case_cum_min_list, use_case_cum_mean_list, use_case_cum_max_list = \
      get_cum_stat(use_case_count_list,
                   process_function=lambda x: x * nb_users)

  time_cum_min_list, time_cum_mean_list, time_cum_max_list = \
      get_cum_stat(time_elapsed_list)

  if is_single_plot:
    axes.plot(time_cum_max_list, use_case_cum_max_list, 'gs-')
  else:
    xerr_list = [stat.standard_deviation for stat in time_elapsed_list]

    xerr_left = numpy.minimum([(cum_mean - time_cum_min_list[i]) for i, cum_mean in \
                                 enumerate(time_cum_mean_list)],
                              xerr_list)

    xerr_right = numpy.minimum([(time_cum_max_list[i] - cum_mean) for i, cum_mean in \
                                  enumerate(time_cum_mean_list)],
                               xerr_list)

    axes.errorbar(time_cum_mean_list,
                  use_case_cum_min_list,
                  xerr=[xerr_left, xerr_right],
                  color='r',
                  ecolor='b',
                  label='Mean',
                  elinewidth=2,
                  fmt='D-',
                  capsize=10.0)

    if not only_average:
      axes.plot(time_cum_min_list, use_case_cum_min_list, 'yo-', label='Minimum')
      axes.plot(time_cum_max_list, use_case_cum_max_list, 'gs-', label='Maximum')

  return (ticker.MaxNLocator(nbins=20), ticker.AutoMinorLocator(),
          ticker.MaxNLocator(nbins=20), ticker.AutoMinorLocator())

@drawDecorator(xlabel='Concurrent Users',
               ylabel='Use cases/h')
def drawConcurrentUsersUseCasePlot(axes,
                                   nb_users_list,
                                   use_case_stat_list,
                                   only_average=False):
  use_case_per_hour_min_list = []
  use_case_per_hour_mean_list = []
  use_case_per_hour_max_list = []

  y_error_lower_list = []
  y_error_upper_list = []

  for use_case_stat in use_case_stat_list:
    count = use_case_stat['count']

    maximum_sum = 0
    mean_sum = 0
    minimum_sum = 0
    stddev = 0
    for stat in use_case_stat['duration_stats']:
      minimum_sum += stat.minimum
      mean_sum += stat.mean
      maximum_sum += stat.maximum
      stddev = max(stddev, stat.standard_deviation)

    use_case_per_hour_min = count / maximum_sum
    use_case_per_hour_min_list.append(use_case_per_hour_min)

    use_case_per_hour_mean = count / mean_sum
    use_case_per_hour_mean_list.append(use_case_per_hour_mean)

    use_case_per_hour_max = count / minimum_sum
    use_case_per_hour_max_list.append(use_case_per_hour_max)

    if stddev:
      y_error_lower = use_case_per_hour_mean - max(use_case_per_hour_min,
                                                   count / (mean_sum + stddev))

      y_error_upper = min(use_case_per_hour_max,
                          count / (mean_sum - stddev)) - use_case_per_hour_mean
    else:
      y_error_lower = y_error_upper = 0

    y_error_lower_list.append(y_error_lower)
    y_error_upper_list.append(y_error_upper)

  axes.errorbar(nb_users_list,
                use_case_per_hour_mean_list,
                yerr=[y_error_lower_list, y_error_upper_list],
                color='r',
                ecolor='b',
                label='Mean',
                elinewidth=2,
                fmt='D-',
                capsize=10.0)

  if not only_average:
    axes.plot(nb_users_list, use_case_per_hour_min_list, 'yo-', label='Minimum')
    axes.plot(nb_users_list, use_case_per_hour_max_list, 'gs-', label='Maximum')

  axes.set_xticks(nb_users_list)

  return (ticker.FixedLocator(nb_users_list), None,
          ticker.MaxNLocator(nbins=20), ticker.AutoMinorLocator()) 

@drawDecorator(xlabel='Concurrent users',
               ylabel='Seconds')
def drawConcurrentUsersPlot(axes, nb_users_list, stat_list, only_average=False):
  min_array = numpy.array([stat.minimum for stat in stat_list])
  mean_array = numpy.array([stat.mean for stat in stat_list])
  max_array = numpy.array([stat.maximum for stat in stat_list])

  yerr_list = [stat.standard_deviation for stat in stat_list]
  yerr_lower = numpy.minimum(mean_array - min_array, yerr_list)
  yerr_upper = numpy.minimum(max_array - mean_array, yerr_list)

  axes.errorbar(nb_users_list,
                mean_array,
                yerr=[yerr_lower, yerr_upper],
                color='r',
                ecolor='b',
                label='Mean',
                elinewidth=2,
                fmt='D-',
                capsize=10.0)

  if not only_average:
    axes.plot(nb_users_list, min_array, 'yo-', label='Minimum')
    axes.plot(nb_users_list, max_array, 'gs-', label='Maximum')

  axes.set_xticks(nb_users_list)

  return (ticker.FixedLocator(nb_users_list), None,
          ticker.MaxNLocator(nbins=20), ticker.AutoMinorLocator())

from matplotlib.backends.backend_pdf import PdfPages

import glob
import os
import sys
import re

user_re = re.compile('-(\d+)users-')

DIAGRAM_PER_PAGE = 6

def generateReport():
  argument_namespace = parseArguments()

  filename_iter = glob.iglob("%s-*repeat*-*users*-*process*.csv" % os.path.join(
      argument_namespace.report_directory,
      argument_namespace.filename_prefix))

  per_nb_users_report_dict = {}
  for filename in filename_iter:
    # There may be no results at all in case of errors
    if not os.stat(filename).st_size:
      print("Ignoring empty file %s" % filename, file=sys.stderr)
      continue

    report_dict = per_nb_users_report_dict.setdefault(
      int(user_re.search(filename).group(1)), {'filename': []})

    report_dict['filename'].append(filename)

  if not per_nb_users_report_dict:
    sys.exit("ERROR: No result file found, perhaps ``--filename-prefix'' should"
             "be specified?")

  pdf = PdfPages(argument_namespace.output_filename)

  is_range_user = len(per_nb_users_report_dict) > 1
  range_user_report_dict = {}

  for nb_users, report_dict in sorted(per_nb_users_report_dict.items(),
                                      key=lambda d: d[0]):
    stat_list, use_case_dict = computeStatisticFromFilenameList(
      argument_namespace, report_dict['filename'], range_user_report_dict,
      is_range_user)

    title = "Ran suites with %d users" % len(report_dict['filename'])
    for slice_start_idx in range(0, len(stat_list), DIAGRAM_PER_PAGE):
      if slice_start_idx == DIAGRAM_PER_PAGE:
        title += ' (Ctd.)'

      drawBarDiagram(pdf, title,
                     stat_list[slice_start_idx:slice_start_idx +
                               DIAGRAM_PER_PAGE],
                     only_average=argument_namespace.only_average)

    for suite_name, use_case_dict in use_case_dict.viewitems():
      drawUseCasePerNumberOfUserPlot(
        pdf,
        "Scalability for %s with %d users" % (suite_name, nb_users),
        nb_users,
        use_case_dict['count_stats'],
        use_case_dict['duration_stats'],
        is_single_plot=(nb_users == 1),
        only_average=argument_namespace.only_average)

  if is_range_user:
    nb_users_list = sorted(per_nb_users_report_dict.keys())
    title_fmt = "%%s from %d to %d users" % \
        (nb_users_list[0],
         nb_users_list[-1])

    for suite_name, report_dict in six.iteritems(range_user_report_dict):
      for label, stat_list in six.iteritems(report_dict['results']):
        drawConcurrentUsersPlot(
          pdf,
          title_fmt % label,
          nb_users_list,
          stat_list,
          only_average=argument_namespace.only_average)

      drawConcurrentUsersUseCasePlot(
        pdf,
        title_fmt % ("%s: Use cases" % suite_name),
        nb_users_list,
        report_dict['use_cases'],
        only_average=argument_namespace.only_average)

  pdf.close()

if __name__ == '__main__':
  generateReport()
