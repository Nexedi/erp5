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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.CMFCore.PortalContent import NoWL, ResourceLockedError
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import parseHeadersBody
from Products.CMFDefault.utils import html_headcheck
from Products.CMFDefault.utils import bodyfinder
from Products.CMFDefault.utils import SimpleHTMLParser as CMFSimpleHTMLParser
from zLOG import LOG

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
    if html_headcheck(text): return 'html'
    else: return 'structured-text'

  security.declarePrivate('handleText')
  def handleText(self, text, format=None):
    """ Handles the raw text, returning headers, body, format """
    headers = {}
    if not format:
      format = self.guessFormat(text)
    if format == 'html':
      parser = SimpleHTMLParser()
      parser.feed(text)
      headers.update(parser.metatags)
      if parser.title:
        headers['title'] = parser.title
      body = bodyfinder(text)
    else:
      headers, body = parseHeadersBody(text, headers)
    return headers, body, format

  ## FTP handlers
  security.declareProtected(Permissions.ModifyPortalContent, 'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """ Handle HTTP (and presumably FTP?) PUT requests """
    if not NoWL:
      self.dav__init(REQUEST, RESPONSE)
      self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
    body = REQUEST.get('BODY', '')

    try:
      headers, body, format = self.handleText(text=body)
      if REQUEST.get_header('Content-Type', '') == 'text/html':
        text_format = 'html'
      else:
        text_format = format
      if not headers.has_key('text_format'): headers['text_format'] = text_format
      headers['text_content'] = body
      self._edit(**headers)
    except 'EditingConflict', msg:
      # XXX Can we get an error msg through?  Should we be raising an
      #     exception, to be handled in the FTP mechanism?  Inquiring
      #     minds...
      transaction.abort()
      RESPONSE.setStatus(450)
      return RESPONSE
    except ResourceLockedError, msg:
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
      if pid not in ('text_content',):
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
          'body': self.getTextContent(),
          }
    else:
      hdrtext = formatRFC822Headers( hdrlist )
      bodytext = '%s\r\n\r\n%s' % ( hdrtext, self.getTextContent() )

    return bodytext

  security.declareProtected(Permissions.View, 'get_size')
  def get_size( self ):
    """ Used for FTP and apparently the ZMI now too """
    return len(self.manage_FTPget())


class Folder:
  """
  Taken from CMFCore.PortalFolder
  """
  def PUT_factory( self, name, typ, body ):
    """ Factory for PUT requests to objects which do not yet exist.

    Used by NullResource.PUT.

    Returns -- Bare and empty object of the appropriate type (or None, if
    we don't know what to do)
    """
    findPortalTypeName = None
    registry = getToolByName(self, 'portal_contribution_registry', None)
    if registry is not None:
      findPortalTypeName = registry.findPortalTypeName
    else:
      # Keep backward compatibility
      registry = getToolByName(self, 'content_type_registry', None)
      if registry is None:
        return None
      findPortalTypeName = registry.findTypeName

    portal_type = findPortalTypeName(name, typ, body)
    if portal_type is None:
      return None

    # The code bellow is inspired from ERP5Type.Core.Folder.newContent
    pt = self._getTypesTool()
    myType = pt.getTypeInfo(self)
    if myType is not None and not myType.allowType( portal_type ) and \
       'portal_contributions' not in self.getPhysicalPath():
      raise ValueError('Disallowed subobject type: %s' % portal_type)
    pt.constructContent( type_name=portal_type,
                         container=self,
                         id=name,
                         is_indexable=0
                         )

    # constructContent does too much, so the object has to be removed again
    obj = aq_base( self._getOb( name ) )
    self._delObject( name ) # _delObject will not invoke the catalog since is_indexable was set to 0
    delattr(obj, 'isIndexable') # Allow indexing again (standard case)
    return obj
