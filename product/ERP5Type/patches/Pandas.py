##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

try:
  import pandas as pd
# pandas is optional, see
# commit 020b1ea39b06f09e6bf493f9083566b43f43b074
# (https://lab.nexedi.com/nexedi/erp5/commit/020b1ea39b06f09e6bf493f9083566b43f43b074)
except ImportError:
  pass
else:
  import six

  if six.PY2:
    from StringIO import StringIO
  else:
    from io import StringIO

  from AccessControl.ZopeGuards import Unauthorized as ZopeGuardsUnauthorized

  def restrictPandasReadFunction(function_name):
    original_function = getattr(pd, function_name)

    def Pandas_read(data_string, *args, **kwargs):
      # Strict: don't use 'isinstance', only allow buildin str
      # objects
      if type(data_string) is not str:
        raise ZopeGuardsUnauthorized(
          "Parsing object '%s' of type '%s' is prohibited!" % (data_string, type(data_string))
        )
      string_io = StringIO(data_string)
      return original_function(string_io, *args, **kwargs)

    disclaimer = """\n
Disclaimer:

This function has been patched by ERP5 for zope sandbox usage.
Only objects of type 'str' are valid inputs, file paths, files,
urls, etc. are prohibited or ignored.
"""

    Pandas_read.__doc__ = original_function.__doc__ + disclaimer
    setattr(pd, function_name, Pandas_read)

  pandas_read_function_to_restrict_tuple = (
    "read_json",
    # "read_html",  # needs installation of additional dependency: html5lib
    "read_csv",
    "read_fwf",
    # "read_xml",  # only available for pandas version >= 1.3.0
  )

  for pandas_read_function_to_restrict in pandas_read_function_to_restrict_tuple:
    restrictPandasReadFunction(pandas_read_function_to_restrict)
