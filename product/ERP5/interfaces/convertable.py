# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.ERP5.interfaces.format_convertable import IFormatConvertable

class IConvertable(IFormatConvertable):
  """
  Convertable interface specification

  Documents which implement IConvertable can be converted
  to multiple formats.
  """

  def convert(format, **kw):
    """
    Converts the current document to the specified format
    taking into account optional parameters. This method
    returns a tuple of two values: a mime type string and
    the converted data.

    This methods raises a ConversionError if the target format
    is not allowed, or an Unauthorized error if the target format
    is not permitted.

    format -- the target conversion format specified either as an
              extension (ex. 'png') or as a mime type
              string (ex. 'text/plain')

    kw -- optional parameters which can be passed to the
          conversion engine
    """
