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

from slapos.tool.nosqltester import NoSQLTester
from erp5.utils.benchmark.performance_tester import PerformanceTester

class ScalabilityTester(NoSQLTester):
  def __init__(self):
    super(ScalabilityTester, self).__init__()

  def _add_parser_arguments(self, parser):
    super(ScalabilityTester, self)._add_parser_arguments(parser)
    PerformanceTester._add_parser_arguments(parser)

  def _parse_arguments(self, parser):
    namespace = super(ScalabilityTester, self)._parse_arguments(parser)
    PerformanceTester._check_parsed_arguments(namespace)
    return namespace

  def run_tester(self):
    performance_tester = PerformanceTester(
      self.send_result_availability_notification,
      self.argument_namespace)

    performance_tester.run()

def main():
  ScalabilityTester().run()

if __name__ == '__main__':
  main()
