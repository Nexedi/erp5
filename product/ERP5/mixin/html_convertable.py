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

# Mixin import
from Products.ERP5.mixin.convertable import ConvertableMixin
from Products.ERP5.mixin.cached_convertable import CachedConvertableMixin



class HTMLConvertableMixin(CachedConvertableMixin):
  """
  This class provides a generic implementation of IHTMLConvertable.

  """

  # Declarative security
  security = ClassSecurityInfo()


  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  
  security.declarePrivate('_asHTML')
  def _asHTML(self, **kw):
    """
      A private method which converts to HTML. This method
      is the one to override in subclasses.
    """
    if not self.hasBaseData():
      raise ConversionError('This document has not been processed yet.')
    try:
      # FIXME: no substitution may occur in this case.
      mime, data = self.getConversion(format='base-html')
      return data
    except KeyError:
      kw['format'] = 'html'
      mime, html = self.convert(**kw)
      return html

  security.declareProtected(Permissions.View, 'asEntireHTML')
  def asEntireHTML(self, **kw):
    """
      Returns a complete HTML representation of the document
      (with body tags, etc.). Adds if necessary a base
      tag so that the document can be displayed in an iframe
      or standalone.

      Actual conversion is delegated to _asHTML
    """
    html = self._asHTML(**kw)
    if self.getUrlString():
      # If a URL is defined, add the base tag
      # if base is defined yet.
      html = str(html)
      if not html.find('<base') >= 0:
        base = '<base href="%s">' % self.getContentBaseURL()
        html = html.replace('<head>', '<head>%s' % base)
      self.setConversion(html, mime='text/html', format='base-html')
    return html

  security.declareProtected(Permissions.View, 'asStrippedHTML')
  def asStrippedHTML(self, **kw):
    """
      Returns a stripped HTML representation of the document
      (without html and body tags, etc.) which can be used to inline
      a preview of the document.
    """
    if not self.hasBaseData():
      return ''
    try:
      # FIXME: no substitution may occur in this case.
      mime, data = self.getConversion(format='stripped-html')
      return data
    except KeyError:
      kw['format'] = 'html'
      mime, html = self.convert(**kw)
      return self._stripHTML(str(html))
  
  def _guessEncoding(self, string):
    """
      Try to guess the encoding for this string.
      Returns None if no encoding can be guessed.
    """
    try:
      import chardet
    except ImportError:
      return None
    return chardet.detect(string).get('encoding', None)

  def _stripHTML(self, html, charset=None):
    """
      A private method which can be reused by subclasses
      to strip HTML content
    """
    body_list = re.findall(self.body_parser, str(html))
    if len(body_list):
      stripped_html = body_list[0]
    else:
      stripped_html = html
    # find charset and convert to utf-8
    charset_list = self.charset_parser.findall(str(html)) # XXX - Not efficient if this
                                         # is datastream instance but hard to do better
    if charset and not charset_list:
      # Use optional parameter is we can not find encoding in HTML
      charset_list = [charset]
    if charset_list and charset_list[0] not in ('utf-8', 'UTF-8'):
      try:
        stripped_html = unicode(str(stripped_html),
                                charset_list[0]).encode('utf-8')
      except (UnicodeDecodeError, LookupError):
        return str(stripped_html)
    return stripped_html  