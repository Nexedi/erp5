# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL. All Rights Reserved.
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import collections
import email
import transaction
from lxml import html
from Products.ERP5Type.Utils import formatRFC822Headers
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.CMFCore.PortalContent import ResourceLockedError
from zExceptions import Forbidden
from io import BytesIO
import six

security = ModuleSecurityInfo(__name__)


class TextContent:
  """
      Implements GET and PUT for the text_content by
      mapping properties to meta tags in HTML or RFC822
      headers.

      This code is taken from Products.CMFDefault.Document and modified
      for ERP5 purpose
  """

  security = ClassSecurityInfo()

  security.declarePrivate('parseHeadersFromText')
  def parseHeadersFromText(self, text):
    """ Handles the raw text, returning headers """
    try:
      tree = html.fromstring(text)
      if tree.tag != "html":
        raise ValueError
    except Exception:
      # this is probably not html code, try rfc822 parsing
      if six.PY3:
        message = email.message_from_bytes(text)
      else:
        message = email.message_from_string(text)
      return {k.capitalize(): '\n'.join(message.get_all(k))
              for k in message.keys()}

    headers = collections.defaultdict(list)
    for meta in tree.iterfind(".//meta"):
      name = meta.get("name")
      if name:
        headers[name.capitalize()].append(meta.get("content"))
    title = tree.find("head/title")
    if title is not None:
      headers["title"] = title.text
    return {k: v if len(v) > 1 else v[0] for k, v in six.iteritems(headers)}

  ## FTP handlers
  security.declareProtected(Permissions.ModifyPortalContent, 'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """ Handle HTTP (and presumably FTP?) PUT requests """
    self.dav__init(REQUEST, RESPONSE)
    self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
    if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
      raise Forbidden('REQUEST_METHOD should be PUT.')
    body = REQUEST.get('BODY', '')

    try:
      headers = self.parseHeadersFromText(body)
      content_type = REQUEST.get_header('Content-Type', '')
      headers.setdefault('content_type', content_type)
      headers['file'] = BytesIO(body)
      self._edit(**headers)
    except ResourceLockedError:
      transaction.abort()
      RESPONSE.setStatus(423)
      return RESPONSE

    RESPONSE.setStatus(204)
    self.reindexObject()
    return RESPONSE

  _htmlsrc = (
      '<html>\n <head>\n'
      ' <title>%(title)s</title>\n'
      '%(metatags)s\n'
      ' </head>\n'
      ' <body>\n%(body)s\n </body>\n'
      '</html>\n'
      )

  security.declareProtected(Permissions.View, 'getMetadataHeaderList')
  def getMetadataHeaderList(self):
    hdrlist = []
    for p in self.getPropertyMap():
      pid = p.get('base_id', p['id'])
      if pid not in ('text_content', 'data', 'base_data'):
        hdrlist.append((pid, self.getProperty(p['id'])))
    return hdrlist

  security.declareProtected(Permissions.View, 'manage_FTPget')
  def manage_FTPget(self):
    "Get the document body for FTP download (also used for the WebDAV SRC)"
    hdrlist = self.getMetadataHeaderList()
    if self.getFormat() == 'text/html':
      hdrtext = ''
      for name, content in hdrlist:
        if name.lower() == 'title':
          continue
        elif content is not None:
          # XXX - Bad algorithm - we should use getPropertyMap directly
          if isinstance(content, (list, tuple)):
            for content_item in content:
              hdrtext = '%s\n <meta name="%s" content="%s" />' % (
                         hdrtext, name, content_item)
          else:
            hdrtext = '%s\n <meta name="%s" content="%s" />' % (
                       hdrtext, name, content)

      bodytext = self._htmlsrc % {
          'title': self.getTitle(),
          'metatags': hdrtext,
          'body': self.asStrippedHTML(''),
          }
    else:
      hdrtext = formatRFC822Headers( hdrlist )
      bodytext = '%s\r\n\r\n%s' % ( hdrtext, self.getTextContent('') )

    return bodytext

  security.declareProtected(Permissions.View, 'get_size')
  def get_size( self ):
    """ Used for FTP and apparently the ZMI now too """
    return len(self.manage_FTPget())

InitializeClass(TextContent)
