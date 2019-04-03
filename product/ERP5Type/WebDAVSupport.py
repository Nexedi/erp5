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

import re
import transaction
from Acquisition import aq_parent, aq_inner, aq_base
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions, PropertySheet, Constraint
from Products.CMFCore.PortalContent import ResourceLockedError
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import parseHeadersBody
from Products.CMFDefault.utils import html_headcheck
from Products.CMFDefault.utils import bodyfinder
from Products.CMFDefault.utils import SimpleHTMLParser as CMFSimpleHTMLParser
from zLOG import LOG
from zExceptions import Forbidden

security = ModuleSecurityInfo( 'Products.ERP5Type.WebDAVSupport' )

class SimpleHTMLParser(CMFSimpleHTMLParser):

  def do_meta( self, attrs ):

    name = ''
    content = ''

    for attrname, value in attrs:
      value = value.strip()
      if attrname == "name":
          name = value.capitalize()
      if attrname == "content":
          content = value

    if name:
      if not self.metatags.has_key(name):
        self.metatags[ name ] = content
      elif type(self.metatags[ name ]) is type([]):
        self.metatags[ name ].append(content)
      else:
        self.metatags[ name ] = [self.metatags[ name ], content]

security.declarePublic('formatRFC822Headers')
def formatRFC822Headers( headers ):

  """ Convert the key-value pairs in 'headers' to valid RFC822-style
      headers, including adding leading whitespace to elements which
      contain newlines in order to preserve continuation-line semantics.

      This code is taken from Products.CMFDefault.utils and modified
      for ERP5 purpose
  """
  munged = []
  linesplit = re.compile( r'[\n\r]+?' )

  for key, value in headers:
    if value is not None:
      if type(value) in (type([]), type(())):
        vallines = map(lambda x: str(x), value)
      else:
        vallines = linesplit.split( str(value) )
      munged.append( '%s: %s' % ( key, '\r\n  '.join( vallines ) ) )

  return '\r\n'.join( munged )

class TextContent:
  """
      Implements GET and PUT for the text_content by
      mapping properties to meta tags in HTML or RFC822
      headers.

      This code is taken from Products.CMFDefault.Document and modified
      for ERP5 purpose
  """

  security = ClassSecurityInfo()

  security.declarePrivate('guessFormat')
  def guessFormat(self, text):
    """ Simple stab at guessing the inner format of the text """
    if html_headcheck(text):
      return 'text/html'
    else:
      return 'text/structured'

  security.declarePrivate('handleText')
  def handleText(self, text, format=None):
    """ Handles the raw text, returning headers, body, format """
    headers = {}
    if not format:
      format = self.guessFormat(text)
    if format == 'text/html':
      parser = SimpleHTMLParser()
      parser.feed(text)
      headers.update(parser.metatags)
      if parser.title:
        headers['title'] = parser.title
      body = bodyfinder(text)
    else:
      headers, body = parseHeadersBody(text, headers)
    return headers, text, format

  ## FTP handlers
  security.declareProtected(Permissions.ModifyPortalContent, 'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """ Handle HTTP (and presumably FTP?) PUT requests """
    self.dav__init(REQUEST, RESPONSE)
    self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
    if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
      raise Forbidden, 'REQUEST_METHOD should be PUT.'
    body = REQUEST.get('BODY', '')

    try:
      headers, body, format = self.handleText(text=body)
      content_type = REQUEST.get_header('Content-Type', '')
      headers.setdefault('content_type', content_type)
      headers['file'] = body
      self._edit(**headers)
    except 'EditingConflict' as msg:
      # XXX Can we get an error msg through?  Should we be raising an
      #     exception, to be handled in the FTP mechanism?  Inquiring
      #     minds...
      transaction.abort()
      RESPONSE.setStatus(450)
      return RESPONSE
    except ResourceLockedError as msg:
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
          if type(content) in (type(()), type([])):
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

from webdav.common import Locked, PreconditionFailed
from webdav.interfaces import IWriteLock
from webdav.NullResource import NullResource
NullResource_PUT = NullResource.PUT

def PUT(self, REQUEST, RESPONSE):
        """Create a new non-collection resource.
        """
        if getattr(self.__parent__, 'PUT_factory', None) is not None: # BBB
          return NullResource_PUT(self, REQUEST, RESPONSE)

        self.dav__init(REQUEST, RESPONSE)
        if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
          raise Forbidden, 'REQUEST_METHOD should be PUT.'

        name = self.__name__
        parent = self.__parent__

        ifhdr = REQUEST.get_header('If', '')
        if IWriteLock.providedBy(parent) and parent.wl_isLocked():
            if ifhdr:
                parent.dav__simpleifhandler(REQUEST, RESPONSE, col=1)
            else:
                # There was no If header at all, and our parent is locked,
                # so we fail here
                raise Locked
        elif ifhdr:
            # There was an If header, but the parent is not locked
            raise PreconditionFailed

        # <ERP5>
        # XXX: Do we really want to force 'id'
        #      when PUT is called on Contribution Tool ?
        kw = {'id': name, 'data': None, 'filename': name}
        contribution_tool = parent.getPortalObject().portal_contributions
        if aq_base(contribution_tool) is not aq_base(parent):
          kw.update(container=parent, discover_metadata=False)
        ob = contribution_tool.newContent(**kw)
        # </ERP5>

        ob.PUT(REQUEST, RESPONSE)
        RESPONSE.setStatus(201)
        RESPONSE.setBody('')
        return RESPONSE

NullResource.PUT = PUT
