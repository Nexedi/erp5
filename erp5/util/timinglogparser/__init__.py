#!/usr/bin/python
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

from __future__ import division, print_function

import os
import sys
import imp
import gzip
import getopt
from time import time
import six

PROFILING_ENABLED = False
if PROFILING_ENABLED:
  from tiny_profiler import profiler_decorator, profiler_report
else:
  def profiler_decorator(funct):
    return funct

  def profiler_report():
    pass

usage = """
Usage:
  parse_timing_log.py [--prefix <prefix>] --config <config> [--debug]
                      [--no-average] [--sum] [--load <file>] [--save <file>]
                      [--decimate <int>] [file_1 [file_2 [...]]]

  Either --prefix or --save must be given.

  --prefix <prefix>
    <prefix> is a string which is used to prefix result file names.
    If ommited, no CSV will be generated.

  --no-average
    Disable the generation of CSV files with average values.

  --sum
    Generate CSV files with time sum as values.
    They use the same names as average files, suffixed with "_sum.csv"
    Ignored if --prefix was not given.

  --load <file>
    Load internal data dict from given file before processing any given file.
    If it's given multiple time, the content of all those files will be merged.

  --save <file>
    Save interal data dict to given file after processing all given files.

  --config <config>
    <config> is a python script defining 2 values:
      - a method called "processLine"
      - a compiled regex called "LINE_PATTERN"
      - a date list sort key computation function called "date_key"
  
  --debug
    Display missed and skipped lines.

  --decimate <int>
    Instead of generating a line per measure, generate one line per <int>
    measures.
    Remain of the integer division of the number of measures per decimate value
    are all put in latest output line.

  file_1 ...
    Log files to process.
    Order in which files are given does not matter.
    Files can be gzip or plain text.

Output files:
  CSV, one file per distinct processLine return value, one line per log day,
  one column per measure.
  First line contains column titles.
  First column contains measure date (first recognisable date in current file).
  Each other cell contains:
    =<value sum>/<value count>
  Example:
    =434/125
  Which means an average of 3.472s over 125 values.
  Empty clls means that there are no values for that measure in current file.
  Strings are surrounded by double quotes (").
  Fields are sparated by colons (,).
"""

@profiler_decorator
def parseFile(filename, measure_dict):
  date = None
  line_number = 0
  match_count = 0
  skip_count = 0
  logfile = gzip.open(filename, 'r')
  try:
    line = logfile.readline()
  except IOError:
    logfile = open(filename, 'r')
    line = logfile.readline()
  begin = time()
  while line != '':
    line_number += 1
    if line_number % 5000 == 0:
      sys.stderr.write('%i\r' % (line_number, ))
      sys.stderr.flush()
    match_list = LINE_PATTERN.findall(line)
    if len(match_list) != 1:
      print('Unparseable line: %s:%i %r' % (filename, line_number, line), file=sys.stderr)
    else:
      result, filter_id, date, duration = processLine(match_list[0], filename, line_number)
      # Possible result values & meaning:
      #  False: try next filter_method
      #  True: ignore & skip to next line
      #  (string): use & skip to next line
      if result is False:
        if debug:
          print('? %s:%i %r' % (filename, line_number, match_list[0]), file=sys.stderr)
      elif result is True:
        if debug:
          print('- %s:%i %r' % (filename, line_number, match_list[0]), file=sys.stderr)
        skip_count += 1
      else:
        measure_dict.setdefault(filter_id, {}).setdefault(result, {}).setdefault(date, []).append(int(duration))
        match_count += 1
    line = logfile.readline()
  print('%i' % (line_number, ), file=sys.stderr)
  if line_number > 0:
    duration = time() - begin
    print("Matched %i lines (%.2f%%), %i skipped (%.2f%%), %i unmatched (%.2f%%) in %.2fs (%i lines per second)." % \
      (match_count, (match_count / line_number) * 100, skip_count, (skip_count / line_number) * 100, (line_number - match_count - skip_count), (1 - (match_count + skip_count) / line_number) * 100, duration, line_number // duration),
      file=sys.stderr)

debug = False
outfile_prefix = None
configuration = None
do_average = True
do_sum = False
load_file_name_list = []
save_file_name = None
decimate_count = 1

try:
  opts, file_list = getopt.getopt(sys.argv[1:], '', ['debug', 'config=', 'prefix=', 'no-average', 'sum', 'load=', 'save=', 'decimate='])
except Exception as reason:
  print(reason, file=sys.stderr)
  print(usage, file=sys.stderr)
  sys.exit(1)

for name, value in opts:
  if name == '--debug':
    debug = True
  elif name == '--config':
    configuration = value
  elif name == '--prefix':
    outfile_prefix = value
  elif name == '--no-average':
    do_average = False
  elif name == '--sum':
    do_sum = True
  elif name == '--load':
    load_file_name_list.append(value)
  elif name == '--save':
    save_file_name = value
  elif name == '--decimate':
    decimate_count = int(value)

if configuration is None:
  raise ValueError('--config is mandatory')

config_file = os.path.splitext(os.path.basename(configuration))[0]
config_path = [os.path.dirname(os.path.abspath(configuration))] + sys.path
file, path, description = imp.find_module(config_file, config_path)
module = imp.load_module(config_file, file, path, description)
file.close()

processLine = module.processLine
LINE_PATTERN = module.LINE_PATTERN
date_key = module.date_key

file_count = len(file_list)
file_number = 0

measure_dict = {}
if len(load_file_name_list):
  for load_file_name in load_file_name_list:
    with open(load_file_name) as load_file:
      temp_measure_dict = eval(load_file.read(), {})
    assert isinstance(measure_dict, dict)
    for filter_id, result_dict in six.iteritems(temp_measure_dict):
      for result, date_dict in six.iteritems(result_dict):
        for date, duration_list in six.iteritems(date_dict):
          measure_dict.setdefault(filter_id, {}).setdefault(result, {}).setdefault(date, []).extend(duration_list)
    print('Previous processing result restored from %r' % (load_file_name, ), file=sys.stderr)

for filename in file_list:
  file_number += 1
  print('Processing %s [%i/%i]...' % (filename, file_number, file_count), file=sys.stderr)
  parseFile(filename, measure_dict)

if save_file_name is not None:
  with open(save_file_name, 'w') as save_file:
    save_file.write(repr(measure_dict))
  print('Processing result saved to %r' % (save_file_name, ), file=sys.stderr)

if outfile_prefix is not None:
  ## Generate a list of all measures and a 2-levels dictionnary with date as key and measure dictionnary as value
  measure_id_list = []
  append = measure_id_list.append
  sheet_dict = {}
  line_dict = {}
  for match_id, match_dict in six.iteritems(measure_dict):
    for result_id, result_dict in six.iteritems(match_dict):
      measure_id = (match_id, result_id)
      sheet_dict.setdefault(match_id, []).append((result_id, measure_id))
      append(measure_id)
      for date, measure_list in six.iteritems(result_dict):
        first_level_dict = line_dict.setdefault(date, {})
        assert measure_id not in first_level_dict
        first_level_dict[measure_id] = measure_list

  date_list = sorted(line_dict, key=date_key)

  def render_cell(value_list, format):
    if isinstance(value_list, (list, tuple)):
      return format % {'sum': sum(value_list), 'count': len(value_list)}
    else:
      return value_list

  def renderOutput(data_format, filename_suffix):
    for sheet_id, sheet_column_list in six.iteritems(sheet_dict):
      outfile_name = '%s_%s_%s.csv' % (outfile_prefix, sheet_id, filename_suffix)
      print('Writing to %r...' % (outfile_name, ), file=sys.stderr)
      with open(outfile_name, 'w') as outfile:
        print('"date",%s' % (','.join(['"%s"' % (x[0], ) for x in sheet_column_list]), ), file=outfile)
        decimate_dict = {}
        decimate = 0
        for date in date_list:
          for key, value in six.iteritems(line_dict[date]):
            decimate_dict.setdefault(key, []).extend(value)
          decimate += 1
          if decimate == decimate_count:
            print('"%s",%s' % (date, ','.join([render_cell(decimate_dict.get(x[1], ''), data_format) for x in sheet_column_list])), file=outfile)
            decimate_dict = {}
            decimate = 0
        if len(decimate_dict):
          print('"%s",%s' % (date, ','.join([render_cell(decimate_dict.get(x[1], ''), data_format) for x in sheet_column_list])), file=outfile)

  if do_average:
    renderOutput('=%(sum)i/%(count)i', 'avg')
  if do_sum:
    renderOutput('=%(sum)i', 'sum')

profiler_report()

