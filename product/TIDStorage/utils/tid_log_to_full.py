#!/usr/bin/python
##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
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

# Transforms a TIDStorage TID log provided on stdin, which might contain
# full statuses and/or incremental changes, and provides a version on stdout
# containing only full statuses.
# Also, does sanity checks on the given file.
# Exit status:
#  0 Success
#  1 Failure

import sys
content = {}
last_timestamp = None

line = sys.stdin.readline()
while line != '':
  split_line = line.split(' ', 2)
  assert len(split_line) == 3, repr(split_line)
  line_timestamp, line_type, line_dict = split_line
  line_timestamp = float(line_timestamp)
  assert line_type in ('f', 'd'), repr(line_type)
  if last_timestamp is None:
    last_timestamp = line_timestamp
  else:
    assert last_timestamp < line_timestamp, '%r < %r' % (last_timestamp, line_timestamp)
  line_dict = eval(line_dict, None)
  assert isinstance(line_dict, dict), type(line_dict)
  assert len(line_dict), repr(line_dict)
  if line_type == 'd':
    for key, value in line_dict.iteritems():
      if key in content:
        assert content[key] < value, '%r < %r' % (content[key], value)
      content[key] = value
    print '%r f %r' % (line_timestamp, content)
  elif line_type == 'f':
    for key, value in content.iteritems():
      assert key in line_dict, repr(key)
      assert value <= line_dict[key], '%r <= %r' % (value, line_dict[key])
    content = line_dict
    print line.strip()
  line = sys.stdin.readline()

