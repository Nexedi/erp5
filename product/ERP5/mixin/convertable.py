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

import md5
import string
import xmlrpclib, base64, re, zipfile, cStringIO
from xmlrpclib import Fault
from xmlrpclib import Transport
from xmlrpclib import SafeTransport
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
from Products.ERP5Type.Base import WorkflowMethod
from zLOG import LOG
from Products.ERP5Type.Cache import CachingMethod



def makeSortedTuple(kw):
  items = kw.items()
  items.sort()
  return tuple(items)


class ConvertableMixin:
  """
  This class provides a generic implementation of IConvertable.

    This class provides a generic API to store in the ZODB
    various converted versions of a file or of a string.

    Versions are stored in dictionaries; the class stores also
    generation time of every format and its mime-type string.
    Format can be a string or a tuple (e.g. format, resolution).
  """

  # Declarative security
  security = ClassSecurityInfo()


  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  
  # Conversion methods
  security.declareProtected(Permissions.AccessContentsInformation, 'convert')
  def convert(self, format, **kw):
    """
      Main content conversion function, returns result which should
      be returned and stored in cache.
      format - the format specied in the form of an extension
      string (ex. jpeg, html, text, txt, etc.)
      **kw can be various things - e.g. resolution

      Default implementation returns an empty string (html, text)
      or raises an error.

      TODO:
      - implement guards API so that conversion to certain
        formats require certain permission
    """
    # Raise an error if the format is not permitted
    if not self.isTargetFormatPermitted(format):
      raise Unauthorized("User does not have enough permission to access document"
	      " in %s format" % (format or 'original'))
    if format == 'html':
      return 'text/html', '' # XXX - Why ?
    if format in ('text', 'txt'):
      return 'text/plain', '' # XXX - Why ?
    raise NotImplementedError
   
  security.declareProtected(Permissions.View,'isTargetFormatAllowed')
  def isTargetFormatAllowed(self,format):
    """
    Checks if the current document can be converted
    to the specified target format.

    format -- the target conversion format specified either as an
              extension (ex. 'png') or as a mime type
              string (ex. 'text/plain')
    """
    return format in self.getTargetFormatList()


  security.declareProtected(Permissions.View,'isTargetFormatPermitted')
  def isTargetFormatPermitted(self, format):
    """
      Checks if the current user can convert the current document
      into the specified target format.
    """
    method = self._getTypeBasedMethod('isTargetFormatPermitted', 
                 fallback_script_id='Document_isTargetFormatPermitted')
    return method(format)
  
  security.declareProtected(Permissions.View,'getTargetFormatItemList') 
  def getTargetFormatItemList(self):
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
    return self.getAllowedTargetItemList()

  security.declareProtected(Permissions.View,'getTargetFormatTitleList')
  def getTargetFormatTitleList(self):
    """
    Returns the list of titles of acceptable formats for conversion 
    as a list of strings which can be translated and displayed 
    to the user.
    """
    return map(lambda x: x[0], self.getTargetFormatItemList())

  security.declareProtected(Permissions.View,'getTargetFormatList')
  def getTargetFormatList(self):
    """
    Returns the list of acceptable formats for conversion
    where format is an extension (ex. 'png') which can be 
    passed to IConvertable.convert or to IDownloadable.index_html
    """
    return map(lambda x: x[1], self.getTargetFormatItemList())
  
  security.declareProtected(Permissions.View,'getPermittedTargetFormatItemList') 
  def getPermittedTargetFormatItemList(self):
    """
    Returns the list of authorized formats for conversion
    in the form of tuples. For each format, checks
    if the current user can convert the current 
    document into that format.
 
    """
    authorized_format_list = []
    format_list = self.getTargetFormatItemList()
    for format in format_list:
      if self.isTargetFormatPermitted(format[1]):
       authorized_format_list.append(format)
    return authorized_format_list