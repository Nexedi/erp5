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

import argparse

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

  parser.add_argument('report_directory',
                      help='Reports directory')

  namespace = parser.parse_args()

  return namespace

import csv

from .result import BenchmarkResultStatistic

def computeStatisticFromFilenameList(argument_namespace, filename_list):
  reader_list = []
  stat_list = []
  label_list = []
  merged_label_dict = {}

  for filename in filename_list:
    reader = csv.reader(open(filename, 'rb'), delimiter=',',
                        quoting=csv.QUOTE_MINIMAL)

    reader_list.append(reader)

    # Get headers
    row_list = reader.next()
    if not label_list:
      label_list = row_list
      label_merged_index = 0
      for label in label_list:
        if argument_namespace.do_merge_label:
          if label in merged_label_dict:
            continue

          merged_label_dict[label] = label_merged_index
          label_merged_index += 1

        stat_list.append(BenchmarkResultStatistic(*label.split(': ', 1)))

    if row_list != label_list:
      raise AssertionError, "ERROR: Result labels: %s != %s" % \
          (label_list, row_list)

    for row_list in reader:
      for idx, row in enumerate(row_list):
        index = merged_label_dict.get(label_list[idx], idx)
        stat_list[index].add(float(row))

  return stat_list

def formatFloatList(value_list):
  return [ format(value, ".3f") for value in value_list ]

import numpy
import pylab

from matplotlib import pyplot, ticker

def drawBarDiagram(pdf, title, stat_list):
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
  # Create the figure
  figure = pyplot.figure(figsize=(11.69, 8.29))
  figure.subplots_adjust(bottom=0.13, right=0.98, top=0.95)
  pyplot.title(title)

  # Create the axes along with their labels
  axes = figure.add_subplot(111)
  axes.set_ylabel('Seconds')
  axes.set_xticks([])

  axes.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
  axes.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))
  axes.yaxis.grid(True, 'major', linewidth=1.5)
  axes.yaxis.grid(True, 'minor')
 
  # Create the bars
  ind = numpy.arange(len(label_list))
  width = 0.33

  min_rects = axes.bar(ind, minimum_list, width, color='y', label='Minimum')

  avg_rects = axes.bar(ind + width, mean_list, width, color='r', label='Mean')

  axes.errorbar(numpy.arange(0.5, len(stat_list)), mean_list,
                yerr=[yerr_lower, yerr_upper], fmt=None,
                label='Standard deviation')

  max_rects = axes.bar(ind + width * 2, maximum_list, width, label='Maximum',
                       color='g')

  # Add the legend of bars
  axes.legend(loc=0)

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

  pdf.savefig()
  pylab.close()

def drawConcurrentUsersPlot(pdf, title, nb_users_list, stat_list):
  figure = pyplot.figure(figsize=(11.69, 8.29), frameon=False)
  figure.subplots_adjust(bottom=0.1, right=0.98, left=0.07, top=0.95)
  pyplot.title(title)
  pyplot.grid(True, linewidth=1.5)

  axes = figure.add_subplot(111)

  min_array = numpy.array([stat.minimum for stat in stat_list])
  mean_array = numpy.array([stat.mean for stat in stat_list])
  max_array = numpy.array([stat.maximum for stat in stat_list])

  yerr_list = [stat.standard_deviation for stat in stat_list]
  yerr_lower = numpy.minimum(mean_array - min_array, yerr_list)
  yerr_upper = numpy.minimum(max_array - mean_array, yerr_list)

  axes.plot(nb_users_list, min_array, 'yo-', label='Minimum')

  axes.errorbar(nb_users_list,
                mean_array,
                yerr=[yerr_lower, yerr_upper],
                color='r',
                ecolor='b',
                label='Mean',
                elinewidth=2,
                fmt='D-',
                capsize=10.0)

  axes.plot(nb_users_list, max_array, 'gs-', label='Maximum')

  axes.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
  axes.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))
  axes.yaxis.grid(True, 'minor')

  axes.xaxis.set_major_locator(ticker.FixedLocator(nb_users_list))

  axes.set_xticks(nb_users_list)
  axes.legend(loc=0)
  axes.set_xlabel('Concurrent users')
  axes.set_ylabel('Seconds')

  pyplot.xlim(xmin=nb_users_list[0])
  pdf.savefig()
  pylab.close()

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
      print >>sys.stderr, "Ignoring empty file %s" % filename
      continue

    report_dict = per_nb_users_report_dict.setdefault(
      int(user_re.search(filename).group(1)), {'filename': []})

    report_dict['filename'].append(filename)

  pdf = PdfPages(argument_namespace.output_filename)

  for nb_users, report_dict in per_nb_users_report_dict.items():
    stat_list = computeStatisticFromFilenameList(
      argument_namespace, report_dict['filename'])

    title = "Ran suites with %d users" % len(report_dict['filename'])
    for slice_start_idx in range(0, len(stat_list), DIAGRAM_PER_PAGE):
      if slice_start_idx == DIAGRAM_PER_PAGE:
        title += ' (Ctd.)'

      drawBarDiagram(pdf, title,
                     stat_list[slice_start_idx:slice_start_idx +
                               DIAGRAM_PER_PAGE])

    report_dict['stats'] = stat_list

  if len(per_nb_users_report_dict) != 1:
    for i in range(len(report_dict['stats'])):
      stat_list = []
      nb_users_list = per_nb_users_report_dict.keys()
      for report_dict in per_nb_users_report_dict.values():
        stat_list.append(report_dict['stats'][i])

      drawConcurrentUsersPlot(
        pdf,
        "%s from %d to %d users (step: %d)" % (stat_list[0].full_label,
                                               nb_users_list[0],
                                               nb_users_list[-1],
                                               nb_users_list[1] - nb_users_list[0]),
        nb_users_list,
        stat_list)

  pdf.close()

if __name__ == '__main__':
  generateReport()
