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
from .result import CSVBenchmarkResult, NothingFlushedException

class CSVScalabilityBenchmarkResult(CSVBenchmarkResult):
  def flush(self, partial=True):
    try:
      super(CSVScalabilityBenchmarkResult, self).flush(partial)
    except NothingFlushedException:
      pass
    else:
      self._argument_namespace.notify_method(self._result_filename,
                                             self._result_file.tell(),
                                             partial=partial)

from .performance_tester import PerformanceTester

class ScalabilityTester(PerformanceTester):
  def preRun(self, *args, **kwargs):
    pass

  def postRun(self, error_message_set):
    from logging import Formatter
    import sys
    from six.moves.urllib.request import urlencode
    from six.moves.urllib.parse import urlopen

    try:
      urlopen("http://[%s]:%d/report" % \
                        (self._argument_namespace.manager_address,
                         self._argument_namespace.manager_port),
                      urlencode({'error_message_set': '|'.join(error_message_set)})).close()

    except Exception:
      print("ERROR: %s" % Formatter().formatException(sys.exc_info()), file=sys.stderr)

  def getResultClass(self):
    if not self._argument_namespace.erp5_publish_url:
      return CSVScalabilityBenchmarkResult

    return super(ScalabilityTester, self).getResultClass()

from slapos.tool.nosqltester import NoSQLTester

class RunScalabilityTester(NoSQLTester):
  def __init__(self):
    super(RunScalabilityTester, self).__init__()

  def _add_parser_arguments(self, parser):
    super(RunScalabilityTester, self)._add_parser_arguments(parser)
    ScalabilityTester._add_parser_arguments(parser)

  def _parse_arguments(self, parser):
    namespace = super(RunScalabilityTester, self)._parse_arguments(parser)
    ScalabilityTester._check_parsed_arguments(namespace)
    namespace.notify_method = self.send_result_availability_notification
    return namespace

  def run_tester(self):
    ScalabilityTester(self.argument_namespace).run()

def main():
  RunScalabilityTester().run()

if __name__ == '__main__':
  main()
