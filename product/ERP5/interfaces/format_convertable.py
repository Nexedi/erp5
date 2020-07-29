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

from zope.interface import Interface

class IFormatConvertable(Interface):
  """
  Format Convertable interface specification

  IFormatConvertable provides methods to list possible formats which documents can
  be converted to.
  """

  def isTargetFormatAllowed(format):
    """
    Checks if the current document can be converted
    to the specified target format.

    format -- the target conversion format specified either as an
              extension (ex. 'png') or as a mime type
              string (ex. 'text/plain')
    """

  def isTargetFormatPermitted(format):
    """
    Checks if the current user can convert the current
    document to the specified target format.
    This method can be used to restrict the list of possible
    formats to deliver a document to a certain group of
    users (ex. read-only PDF only for anonymous users)

    format -- the target conversion format specified either as an
              extension (ex. 'png') or as a mime type
              string (ex. 'text/plain')
    """

  def getTargetFormatItemList():
    """
    Returns the list of acceptable formats for conversion
    in the form of tuples which can be used for example for
    listfield in ERP5Form. Each tuple in the list has the form
    (title, format) where format is an extension (ex. 'png')
    which can be passed to IConvertable.convert or to
    IDownloadable.index_html and title is a string which
    can be translated and displayed to the user.

    Example of result:
        [('ODF Drawing', 'odg'), ('ODF Drawing Template', 'otg'),
        ('OpenOffice.org 1.0 Drawing', 'sxd')]
    """

  def getTargetFormatTitleList():
    """
    Returns the list of titles of acceptable formats for conversion
    as a list of strings which can be translated and displayed
    to the user.
    """

  def getTargetFormatList():
    """
    Returns the list of acceptable formats for conversion
    where format is an extension (ex. 'png') which can be
    passed to IConvertable.convert or to IDownloadable.index_html
    """
