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

import six
from hashlib import md5
from warnings import warn
import string

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from OFS.Image import Pdata, Image as OFSImage
from DateTime import DateTime

def makeSortedTuple(kw):
  items = kw.items()
  items.sort()
  return tuple(items)

def hashPdataObject(pdata_object):
  """Pdata objects are iterable, use this feature strongly
  to minimize memory footprint.
  """
  md5_hash = md5()
  while pdata_object is not None:
    chunk = pdata_object.aq_base
    md5_hash.update(chunk.data)
    pdata_object = chunk.next
    chunk._p_deactivate()
  return md5_hash.hexdigest()

class CachedConvertableMixin:
  """
  This class provides a generic implementation of IConvertable.

    This class provides a generic API to store using portal_caches plugin structure
    various converted versions of a file or of a string.

    Versions are stored in dictionaries; the class stores also
    generation time of every format and its mime-type string.
    Format can be a string or a tuple (e.g. format, resolution).
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getCacheFactory(self):
    """
    """
    # XXX: is this really needed ?
    if self.getOriginalDocument() is None:
      return None

    portal = self.getPortalObject()
    cache_factory_name = portal.portal_preferences.getPreferredConversionCacheFactory('document_cache_factory')
    if cache_factory_name is not None:
      return getattr(portal.portal_caches, cache_factory_name, None)


  security.declareProtected(Permissions.AccessContentsInformation,
                                                             'generateCacheId')
  def generateCacheId(self, **kw):
    """
    """
    return self._getCacheKey(**kw)

  def _getCacheKey(self, **kw):
    """
    Returns the key to use for the cache entries. For now,
    use the object uid.

    TODO: XXX-JPS use instance in the future
    http://pypi.python.org/pypi/uuid/ to generate
    a uuid stored as private property.
    """
    format_cache_id = str(makeSortedTuple(kw)).\
                             translate(string.maketrans('', ''), '[]()<>\'", ')
    return '%s:%s:%s' % (aq_base(self).getUid(), self.getRevision(),
                         format_cache_id)

  security.declareProtected(Permissions.AccessContentsInformation, 'hasConversion')
  def hasConversion(self, **kw):
    """
    """
    try:
      self.getConversion(**kw)
      return True
    except KeyError:
      return False

  security.declareProtected(Permissions.ModifyPortalContent, 'setConversion')
  def setConversion(self, data, mime=None, date=None, **kw):
    """
    """
    cache_id = self._getCacheKey(**kw)
    if data is None:
      cached_value = None
      conversion_md5 = None
      size = 0
    elif isinstance(data, Pdata):
      cached_value = aq_base(data)
      size = str(cached_value) # not a size but avoids a 'del' statement
      conversion_md5 = md5(size).hexdigest()
      size = len(size)
    elif isinstance(data, OFSImage):
      warn('Passing an OFS.Image to setConversion is deprecated', stacklevel=1)
      cached_value = data
      conversion_md5 = md5(str(data.data)).hexdigest()
      size = len(data.data)
    elif isinstance(data, six.string_types):
      cached_value = data
      conversion_md5 = md5(cached_value).hexdigest()
      size = len(cached_value)
    elif isinstance(data, dict):
      # Dict instance are used to store computed metadata
      # from actual content.
      # So this value is intimely related to cache of conversion.
      # As it should be cleared each time the document is edited.
      # Also may be a proper API should be used
      cached_value = data
      conversion_md5 = None
      size = len(cached_value)
    else:
      raise NotImplementedError('Not able to store type:%r' % type(data))
    if date is None:
      date = DateTime()
    stored_data_dict = {'content_md5': self.getContentMd5(),
                        'conversion_md5': conversion_md5,
                        'mime': mime,
                        'data': cached_value,
                        'date': date,
                        'size': size}
    cache_factory = self._getCacheFactory()
    if cache_factory is None:
      if getattr(aq_base(self), 'temp_conversion_data', None) is None:
        self.temp_conversion_data = {}
      self.temp_conversion_data[cache_id] = stored_data_dict
      return
    # The purpose of this transaction cache is to help calls
    # to the same cache value in the same transaction.
    tv = getTransactionalVariable()
    tv[cache_id] = stored_data_dict
    cache_factory.set(cache_id, stored_data_dict)

  def _getConversionDataDict(self, **kw):
    """
    """
    cache_id = self._getCacheKey(**kw)

    # The purpose of this cache is to help calls to the same cache value
    # in the same transaction.
    tv = getTransactionalVariable()
    try:
      return tv[cache_id]
    except KeyError:
      pass

    # get preferred cache factory or cache bag
    cache_factory = self._getCacheFactory()

    # volatile case
    if cache_factory is None:
      return getattr(aq_base(self), 'temp_conversion_data', {})[cache_id]

    else:
      data_dict = cache_factory.get(cache_id, None)
      if data_dict:
        if isinstance(data_dict, tuple):
          # Backward compatibility: if cached value is a tuple
          # as it was before refactoring
          # http://svn.erp5.org?rev=35216&view=rev
          # raise a KeyError to invalidate this cache entry and force
          # calculation of a new conversion
          raise KeyError('Old cache conversion format,'\
                       'cache entry invalidated for key:%r' % cache_id)
        content_md5 = data_dict['content_md5']
        if content_md5 != self.getContentMd5():
          raise KeyError('Conversion cache key is compromised for %r' % cache_id)
        # Fill transactional cache in order to help
        # querying real cache during same transaction
        tv[cache_id] = data_dict
        return data_dict

    raise KeyError('Conversion cache key does not exists for %r' % cache_id)

  security.declareProtected(Permissions.AccessContentsInformation, 'getConversion')
  def getConversion(self, **kw):
    """
    """
    cached_dict = self._getConversionDataDict(**kw)
    mime = cached_dict['mime']
    data = cached_dict['data']
    if isinstance(data, OFSImage):
      data = data.data
    if isinstance(data, Pdata):
      data = str(data)
    return mime, data

  security.declareProtected(Permissions.AccessContentsInformation, 'getConversionSize')
  def getConversionSize(self, **kw):
    """
    """
    return self._getConversionDataDict(**kw)['size']

  security.declareProtected(Permissions.AccessContentsInformation, 'getConversionDate')
  def getConversionDate(self, **kw):
    """
    """
    return self._getConversionDataDict(**kw)['date']

  security.declareProtected(Permissions.AccessContentsInformation, 'getConversionMd5')
  def getConversionMd5(self, **kw):
    """
    """
    return self._getConversionDataDict(**kw)['conversion_md5']

  security.declareProtected(Permissions.ModifyPortalContent, 'updateContentMd5')
  def updateContentMd5(self):
    """Update md5 checksum from the original file
    """
    data = self._baseGetData()
    if data:
      if isinstance(data, Pdata):
        self._setContentMd5(hashPdataObject(data))
      else:
        self._setContentMd5(md5(data).hexdigest()) # Reindex is useless
    else:
      self._setContentMd5(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTargetFormatItemList')
  def getTargetFormatItemList(self):
    """
      Returns a list of acceptable formats for conversion
      in the form of tuples (for listfield in ERP5Form)

      NOTE: it is the responsability of the respecive type based script
      to provide an extensive list of conversion formats.
    """
    method = self._getTypeBasedMethod('getTargetFormatItemList',
              fallback_script_id='Base_getTargetFormatItemList')
    return method()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTargetFormatTitleList')
  def getTargetFormatTitleList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return [x[0] for x in self.getTargetFormatItemList()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTargetFormatList')
  def getTargetFormatList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return [x[1] for x in self.getTargetFormatItemList()]

  security.declareProtected(Permissions.ModifyPortalContent,
                            'isTargetFormatAllowed')
  def isTargetFormatAllowed(self, format): # pylint: disable=redefined-builtin
    """
      Checks if the current document can be converted
      into the specified target format.
    """
    return format in self.getTargetFormatList()

InitializeClass(CachedConvertableMixin)
