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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE

class CachedConvertableMixin:
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

  def _getCacheFactory(self):
    """
    """
    if self.isTempObject():
      return
    cache_tool = getToolByName(self, 'portal_caches')
    preference_tool = getToolByName(self, 'portal_preferences')
    cache_factory_name = preference_tool.getPreferredConversionCacheFactory('document_cache_factory')
    cache_factory = cache_tool.getRamCacheRoot().get(cache_factory_name)
    #XXX This conditional statement should be remove as soon as
    #Broadcasting will be enable among all zeo clients.
    #Interaction which update portal_caches should interact with all nodes.
    if cache_factory is None and getattr(cache_tool, cache_factory_name, None) is not None:
      #ram_cache_root is not up to date for current node
      cache_tool.updateCache()
    return cache_tool.getRamCacheRoot().get(cache_factory_name)

  security.declareProtected(Permissions.ModifyPortalContent, 'clearConversionCache')
  def clearConversionCache(self):
    """
    """
    if self.isTempObject():
      self.temp_conversion_data = {}
      return
    for cache_plugin in self._getCacheFactory().getCachePluginList():
      cache_plugin.delete(self.getPath(), DEFAULT_CACHE_SCOPE)

  security.declareProtected(Permissions.View, 'hasConversion')
  def hasConversion(self, **kw):
    """
    If you want to get conversion cache value if exists, please write
    the code like:

      try:
        mime, data = getConversion(**kw)
      except KeyError:
        ...

    instead of:

      if self.hasConversion(**kw):
        mime, data = self.getConversion(**kw)
      else:
        ...

    for better performance.
    """
    try:
      self.getConversion(**kw)
      return True
    except KeyError:
      return False

  security.declareProtected(Permissions.ModifyPortalContent, 'setConversion')
  def setConversion(self, data, mime=None, calculation_time=None, **kw):
    """
    """
    cache_id = self.generateCacheId(**kw)
    if self.isTempObject():
      if getattr(aq_base(self), 'temp_conversion_data', None) is None:
        self.temp_conversion_data = {}
      self.temp_conversion_data[cache_id] = (mime, aq_base(data))
      return
    cache_factory = self._getCacheFactory()
    cache_duration = cache_factory.cache_duration
    if data is not None:
      for cache_plugin in cache_factory.getCachePluginList():
        try:
          cache_entry = cache_plugin.get(self.getPath(), DEFAULT_CACHE_SCOPE)
          cache_dict = cache_entry.getValue()
        except KeyError:
          cache_dict = {}
        cache_dict.update({cache_id: (self.getContentMd5(), mime, aq_base(data))})
        cache_plugin.set(self.getPath(), DEFAULT_CACHE_SCOPE,
                         cache_dict, calculation_time=calculation_time,
                         cache_duration=cache_duration)

  security.declareProtected(Permissions.View, 'getConversion')
  def getConversion(self, **kw):
    """
    """
    cache_id = self.generateCacheId(**kw)
    if self.isTempObject():
      return getattr(aq_base(self), 'temp_conversion_data', {})[cache_id]
    for cache_plugin in self._getCacheFactory().getCachePluginList():
      cache_entry = cache_plugin.get(self.getPath(), DEFAULT_CACHE_SCOPE)
      data_list = cache_entry.getValue().get(cache_id)
      if data_list:
        md5sum, mime, data = data_list
        if md5sum != self.getContentMd5():
          raise KeyError, 'Conversion cache key is compromised for %r' % cache_id
        return mime, data
    raise KeyError, 'Conversion cache key does not exists for %r' % cache_id

  security.declareProtected(Permissions.View, 'getConversionSize')
  def getConversionSize(self, **kw):
    """
    """
    try:
      return len(self.getConversion(**kw))
    except KeyError:
      return 0

  def generateCacheId(self, **kw):
    """Generate proper cache id based on **kw.
    Function inspired from ERP5Type.Cache
    """
    return str(makeSortedTuple(kw)).translate(string.maketrans('', ''), '[]()<>\'", ')

  security.declareProtected(Permissions.ModifyPortalContent, 'updateContentMd5')
  def updateContentMd5(self):
    """Update md5 checksum from the original file
    """
    data = self.getData()
    self._setContentMd5(md5.new(data).hexdigest()) #reindex is useless
