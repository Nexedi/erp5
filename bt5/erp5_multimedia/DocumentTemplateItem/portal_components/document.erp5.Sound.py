# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.File import File, _MARKER
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
    if range is None:
      start = None
      end = None
    else:
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
    # call caching policy manager.
    _setCacheHeaders(view, web_cache_kw)
    # If we have a conditional get, set status 304 and return
    # no content
    if _checkConditionalGET(view, web_cache_kw):
      return ''

    if not self.checkConversionFormatPermission(format, **kw):
      raise Forbidden('You are not allowed to get this document in this ' \
                      'format')
    mime, data = self.convert(format, **kw)
    total_length = len(data)
    if end is None:
      end = total_length
    if start is not None:
      data = data[start:end-1]

    RESPONSE.setHeader('Content-Length', len(data))
    RESPONSE.setHeader('Content-Type', mime)
    filename = self.getStandardFilename(format=format)
    # workaround for IE's bug to download files over SSL
    RESPONSE.setHeader('Pragma', '')
    RESPONSE.setHeader('Content-Disposition',
                       'attachment; filename="%s"' % filename)
    RESPONSE.setHeader('Accept-Ranges', 'bytes')
    if start is None:
      RESPONSE.setStatus(200)
    else:
      RESPONSE.setHeader('Content-Range',
                         'bytes %s-%s/%s' % (start, end-1, total_length))
      RESPONSE.setStatus(206)
    return bytes(data)