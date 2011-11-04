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

from hashlib import md5
import string

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
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
  next = pdata_object
  while next is not None:
    md5_hash.update(next.data)
    next = next.next
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
    if self.getOriginalDocument() is None:
      return None
    portal = self.getPortalObject()
    cache_tool = portal.portal_caches
    preference_tool = portal.portal_preferences
    cache_factory_name = preference_tool.getPreferredConversionCacheFactory('document_cache_factory')
    cache_factory = cache_tool.getRamCacheRoot().get(cache_factory_name)
    #XXX This conditional statement should be remove as soon as
    #Broadcasting will be enable among all zeo clients.
    #Interaction which update portal_caches should interact with all nodes.
    if cache_factory is None and getattr(cache_tool, cache_factory_name, None) is not None:
      #ram_cache_root is not up to date for current node
      cache_tool.updateCache()
    return cache_tool.getRamCacheRoot().get(cache_factory_name)

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

  security.declareProtected(Permissions.View, 'hasConversion')
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
      conversion_md5 = hashPdataObject(cached_value)
      size = len(cached_value)
    elif isinstance(data, OFSImage):
      cached_value = data
      conversion_md5 = md5(str(data.data)).hexdigest()
      size = len(data.data)
    elif isinstance(data, (str, unicode,)):
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
      raise NotImplementedError, 'Not able to store type:%r' % type(data)
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
    cache_duration = cache_factory.cache_duration
    # The purpose of this transaction cache is to help calls
    # to the same cache value in the same transaction.
    tv = getTransactionalVariable()
    tv[cache_id] = stored_data_dict
    for cache_plugin in cache_factory.getCachePluginList():
      cache_plugin.set(cache_id, DEFAULT_CACHE_SCOPE,
                       stored_data_dict, cache_duration=cache_duration)

  security.declareProtected(Permissions.View, '_getConversionDataDict')
  def _getConversionDataDict(self, **kw):
    """
    """
    cache_id = self._getCacheKey(**kw)
    cache_factory = self._getCacheFactory()
    if cache_factory is None:
      return getattr(aq_base(self), 'temp_conversion_data', {})[cache_id]
    # The purpose of this cache is to help calls to the same cache value
    # in the same transaction.
    tv = getTransactionalVariable()
    try:
      return tv[cache_id]
    except KeyError:
      pass
    for cache_plugin in cache_factory.getCachePluginList():
      cache_entry = cache_plugin.get(cache_id, DEFAULT_CACHE_SCOPE)
      if cache_entry is not None:
        data_dict = cache_entry.getValue()
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
            raise KeyError, 'Conversion cache key is compromised for %r' % cache_id
          # Fill transactional cache in order to help
          # querying real cache during same transaction
          tv[cache_id] = data_dict
          return data_dict
    raise KeyError, 'Conversion cache key does not exists for %r' % cache_id

  security.declareProtected(Permissions.View, 'getConversion')
  def getConversion(self, **kw):
    """
    """
    cached_dict = self._getConversionDataDict(**kw)
    return cached_dict['mime'], cached_dict['data']

  security.declareProtected(Permissions.View, 'getConversionSize')
  def getConversionSize(self, **kw):
    """
    """
    try:
      return self._getConversionDataDict(**kw)['size']
    except KeyError:
      # If conversion doesn't exists return 0
      return 0

  security.declareProtected(Permissions.View, 'getConversionDate')
  def getConversionDate(self, **kw):
    """
    """
    return self._getConversionDataDict(**kw)['date']

  security.declareProtected(Permissions.View, 'getConversionMd5')
  def getConversionMd5(self, **kw):
    """
    """
    return self._getConversionDataDict(**kw)['conversion_md5']

  security.declareProtected(Permissions.ModifyPortalContent, 'updateContentMd5')
  def updateContentMd5(self):
    """Update md5 checksum from the original file
    """
    data = self.getData()
    if data is not None:
      if isinstance(data, Pdata):
        self._setContentMd5(hashPdataObject(aq_base(data)))
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
    return map(lambda x: x[0], self.getTargetFormatItemList())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTargetFormatList')
  def getTargetFormatList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return map(lambda x: x[1], self.getTargetFormatItemList())

  security.declareProtected(Permissions.ModifyPortalContent,
                            'isTargetFormatAllowed')
  def isTargetFormatAllowed(self, format):
    """
      Checks if the current document can be converted
      into the specified target format.
    """
    return format in self.getTargetFormatList()
