# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

from zope.interface import Interface

class IDownloadable(Interface):
  """
  Downloadable interface specification

  Documents which implement IDownloadable can be downloaded
  directly from their URL using any format specified as a parameter.
  """

  def index_html(REQUEST, RESPONSE, format=None, **kw): # pylint: disable=redefined-builtin
    """
    Download the document in the specified format with
    optional conversion parameters.

    REQUEST -- HTTP REQUEST handle

    REQUEST -- HTTP RESPONSE handle

    format -- optional target format specified as
              an extension string (ex. doc, png, pdf, etc.)

    kw -- optional conversion parameters
    """

  def getStandardFilename(format=None): # pylint: disable=redefined-builtin
    """
    Returns a standard file name for the document to download.
    This method is the reverse of
    IDiscoverable.getPropertyDictFromFilename.

    format -- extension of returned file name
    """
