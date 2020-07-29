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

class ICachedConvertable(Interface):
  """
  Cached Convertable interface specification

  The conversion of documents which implement the ICachedConvertable
  interface can be cached efficiently and querried.
  """

  def generateCacheId(**kw):
    """Return string to identify Document in cache pool with
    all arguments used to convert the document
    """

  def hasConversion(**kw):
    """
    Return True if the conversion is already cache, False else.

    **kw -- conversion parameters
    """

  def setConversion(data, mime=None, date=None, **kw):
    """
    Saves in the cache the converted data and mime type of a document,
    and records the date of conversion.

    data -- the converted data (string or Pdata)

    mime -- the mime type of the converted data (string)

    date -- conversion date

    **kw -- conversion parameters
    """

  def getConversion(**kw):
    """
    Returns a tuple containing converted mime type and data of a document if
    any, otherwise, raises an KeyError exception.
    mime type is a string.
    data is a string.

    **kw -- conversion parameters
    """

  def getConversionSize(**kw):
    """
    Returns the size (in bytes) of the converted document if any,
    otherwise, raises an KeyError exception.

    **kw -- conversion parameters
    """

  def getConversionDate(**kw):
    """
    Returns the date of conversion of the document if any,
    otherwise, raises an KeyError exception.

    **kw -- conversion parameters
    """

  def getConversionMd5(**kw):
    """
    Returns the MD5 hash of the converted document if any,
    otherwise, raises an KeyError exception.

    **kw -- conversion parameters
    """

  def updateContentMd5():
    """
    Udpate MD5 hash of non converted data in order
    to check that returned cached result was computed from same origin.
    """
