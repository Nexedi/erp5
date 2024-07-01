##############################################################################
#
# Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
#                    Levin Zimmermann <levin.zimmermann@nexedi.com>
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
"""
Restricted pandas module.

From restricted python, use "import pandas" (see patches/Restricted.py).
"""

from pandas import *

# Add restricted versions of IO functions
import six as _six
from AccessControl.ZopeGuards import Unauthorized as _ZopeGuardsUnauthorized

from six.moves import cStringIO as _StringIO


def _addRestrictedPandasReadFunction(function_name):
  original_function = getattr(__import__('pandas'), function_name)

  def Pandas_read(data_string, *args, **kwargs):
    # Strict: don't use 'isinstance', only allow buildin str
    # objects
    if type(data_string) is not str:
      raise _ZopeGuardsUnauthorized(
        "Parsing object '%s' of type '%s' is prohibited!" % (data_string, type(data_string))
      )
    string_io = _StringIO(data_string)
    return original_function(string_io, *args, **kwargs)

  disclaimer = """\n
Disclaimer:

This function has been patched by ERP5 for zope sandbox usage.
Only objects of type 'str' are valid inputs, file paths, files,
urls, etc. are prohibited or ignored.
"""

  Pandas_read.__doc__ = original_function.__doc__ + disclaimer
  globals().update({function_name: Pandas_read})


def _addRestrictedPandasReadFunctionTuple():
  pandas_read_function_to_restrict_tuple = (
    "read_json",
    # "read_html",  # needs installation of additional dependency: html5lib
    "read_csv",
    "read_fwf",
    # "read_xml",  # only available for pandas version >= 1.3.0
  )

  for pandas_read_function_to_restrict in pandas_read_function_to_restrict_tuple:
    _addRestrictedPandasReadFunction(pandas_read_function_to_restrict)


_addRestrictedPandasReadFunctionTuple()