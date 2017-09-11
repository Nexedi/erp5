# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.File import File, _MARKER
from ZPublisher import HTTPRangeSupport
from Products.CMFCore.utils import _setCacheHeaders, _ViewEmulator
from Products.CMFCore.utils import _checkConditionalGET

from zExceptions import Forbidden

class Sound(File):

  meta_type = 'ERP5 Sound'
  portal_type = 'Sound'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.Document
                    , PropertySheet.Data
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.Periodicity
    )

  security.declareProtected(Permissions.View, 'index_html')
  def index_html(self, REQUEST, RESPONSE, format=_MARKER, inline=_MARKER, **kw):
    """XXXXXX"""
    range = REQUEST.get_header('Range', None)
    if range is not None:
      ranges = HTTPRangeSupport.parseRange(range)
      (start, end) =  ranges[0]

    if (format is _MARKER) and (not kw) and (range is None):
      # conversion parameters is mandatory to download the converted content.
      # By default allways return view action.
      # for all WevDAV access return raw content.
      return self.view()

    if format is _MARKER:
      format = None

    web_cache_kw = kw.copy()
    if format:
      web_cache_kw['format'] = format
    view = _ViewEmulator().__of__(self)
    # If we have a conditional get, set status 304 and return
    # no content
    if _checkConditionalGET(view, web_cache_kw):
      return ''
    # call caching policy manager.
    _setCacheHeaders(view, web_cache_kw)

    if not self.checkConversionFormatPermission(format, **kw):
      raise Forbidden('You are not allowed to get this document in this ' \
                      'format')
    mime, data = self.convert(format, **kw)
    
    data = data[start:end-1]
    
    RESPONSE.setHeader('Content-Length', len(data))
    RESPONSE.setHeader('Content-Type', mime)
    filename = self.getStandardFilename(format=format)
    RESPONSE.setHeader('Cache-Control', 'Private') # workaround for Internet Explorer's bug
    # workaround for IE's bug to download files over SSL
    RESPONSE.setHeader('Pragma', '')
    RESPONSE.setHeader('Content-Disposition',
                       'attachment; filename="%s"' % filename)
    RESPONSE.setHeader('Accept-Ranges', 'bytes')
    RESPONSE.setStatus(206)
    return str(data)