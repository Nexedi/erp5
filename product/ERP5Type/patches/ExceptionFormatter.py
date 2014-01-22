# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from zExceptions.ExceptionFormatter import TextExceptionFormatter

TextExceptionFormatter_formatLine = TextExceptionFormatter.formatLine
def formatLine(self, tb, *args, **kwargs):
  """
  Monkey patched to display source code lines when an Exception traceback is
  displayed in Zope
  """
  f = tb.tb_frame
  filename = f.f_code.co_filename
  lineno = tb.tb_lineno
  f_globals = f.f_globals
  line_str = TextExceptionFormatter_formatLine(self, tb, *args, **kwargs)
  try:
    import linecache
    source_code_line = linecache.getline(filename, lineno, f_globals)
    line_str += self.line_sep + '    ' + self.escape(source_code_line.strip())
  except Exception:
    pass

  return line_str

TextExceptionFormatter.formatLine = formatLine
