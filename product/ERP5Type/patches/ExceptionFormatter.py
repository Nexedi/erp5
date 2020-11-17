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

from zExceptions.ExceptionFormatter import HTMLExceptionFormatter

HTMLExceptionFormatter_formatLine = HTMLExceptionFormatter.formatLine
def formatLine(self, tb, *args, **kwargs):
  """
  Monkey patched to add links to ZODB Components and Python Script. The
  regex part is a bit dirty but there is no other way besides of a copy/paste
  of formatLine()...
  """
  f = tb.tb_frame
  filename = f.f_code.co_filename.replace('<', '').replace('>', '')
  lineno = tb.tb_lineno
  f_globals = f.f_globals
  line_str = HTMLExceptionFormatter_formatLine(self, tb, *args, **kwargs)

  from Products.ERP5.ERP5Site import getSite
  try:
    portal_absolute_url = getSite().absolute_url()

    import re
    # Use the supplement defined in the module.
    # This is used by Scripts (Python).
    if '__traceback_supplement__' in f_globals:
      tbs = f_globals['__traceback_supplement__']
      line_str = re.sub(
        '^(<li>\s*)(Module script,[^<]*)(.*)$',
        r'\1<a href="%s/manage_main?line=%s">\2</a>\3' % (tbs[1].absolute_url(),
                                                          lineno),
        line_str,
        flags=re.DOTALL)

    else:
      line_str = re.sub(
        '^(<li>\s*)(Module erp5\.component\.[^<]*)(.*)$',
        r'\1<a href="/%s/%s?line=%s">\2</a>\3' % (portal_absolute_url,
                                                  filename,
                                                  lineno),
        line_str,
        flags=re.DOTALL)

  except Exception as e:
    pass

  return line_str

HTMLExceptionFormatter.formatLine = formatLine
