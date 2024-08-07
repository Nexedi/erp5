# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Acquisition import Implicit
from BTrees.OOBTree import OOBTree
from warnings import warn
from six.moves import range
import six

ACTIVITY_GROUPING_COUNT = 200

class UrlRegistryTool(BaseTool):
  """
  """
  title = 'Url Registry Tool'
  id = 'portal_url_registry'
  meta_type = 'ERP5 Url Registry Tool'
  title = 'Contribution URLs'
  portal_type = 'Url Registry Tool'

  # Declarative Security
  security = ClassSecurityInfo()
  # How manage security to avoid clearing content by disallowed users ?

  _url_reference_mapping = 'url_reference_mapping'

  def __init__(self, id=None): # pylint: disable=redefined-builtin, super-init-not-called
    if id is not None:
      self.id = id
    self._initBTree()

  def _initBTree(self):
    """
    Initialise a HBTree like object.
    The first level of BTrees has namespace value as key.
    BTree{
           namespace: BTree{key: value},
           namespace: BTree{key: value}
         }
    """
    self._global_mapping_storage = OOBTree()

  def _getMappingDict(self):
    """
    Return a dict like object.
    """
    portal_preferences = self.getPortalObject().portal_preferences
    reference_mapping_namespace = self._url_reference_mapping
    preferred_namespace = portal_preferences.getPreferredIngestionNamespace('')
    namespace = reference_mapping_namespace + preferred_namespace
    return BTreeMappingDict(namespace).__of__(self)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getURLMappingContainerFromContext')
  def getURLMappingContainerFromContext(self, context):
    """
    Return the container of mapping according given context.
    This will interrogate crawling policy (based on predicate)
    and return an persistent object.
    It can be an external_source, a module, a tool, or any document.

    context - a context to test predicates
    """
    warn('context argument ignored', DeprecationWarning)
    return self


  security.declareProtected(Permissions.ManagePortal,
                            'clearUrlRegistryTool')
  def clearUrlRegistryTool(self, context=None):
    """
    Unregister all namespaces.
    """
    if context is not None:
      warn('context argument ignored', DeprecationWarning)
    self._initBTree()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'registerURL')
  def registerURL(self, url, reference, context=None):
    """
    Compute namespace key.
    Then associate url with reference in Persistent Mapping
    in context of user system preference.
    """
    if context is not None:
      warn('context argument ignored', DeprecationWarning)
    mapping = self._getMappingDict()
    if url in mapping.keys() and mapping[url] == reference:
      # No need to update mapping
      return
    mapping[url] = reference

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getReferenceFromURL')
  def getReferenceFromURL(self, url, context=None):
    """
    Return reference according provided url,
    in context of user's system preference.
    """
    if context is not None:
      warn('context argument ignored', DeprecationWarning)
    return self._getMappingDict()[url]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getReferenceList')
  def getReferenceList(self, context=None):
    """
    Return all references according to the given context.
    """
    if context is not None:
      warn('context argument ignored', DeprecationWarning)
    return self._getMappingDict().values()


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getURLListFromReference')
  def getURLListFromReference(self, reference, context=None):
    """
    """
    if context is not None:
      warn('context argument ignored', DeprecationWarning)
    mapping = self._getMappingDict()
    url_list = []
    for url, stored_reference in six.iteritems(mapping):
      if reference == stored_reference:
        url_list.append(url)
    return url_list

  security.declareProtected(Permissions.ModifyPortalContent,
                            'updateUrlRegistryTool')
  def updateUrlRegistryTool(self):
    """
    Fetch all document path, then call in activities
    Base_registerUrl on all of them (grouped by reference)
    to fill in portal_url_registry.
    """
    portal = self.getPortalObject()
    portal_type_list = portal.getPortalDocumentTypeList()
    if portal_type_list:
      object_list = portal.portal_catalog(portal_type=portal_type_list,
                                          group_by='reference',
                                          limit=None)
      object_list_len = len(object_list)
      portal_activities = portal.portal_activities
      object_path_list = [x.path for x in object_list]
      for i in range(0, object_list_len, ACTIVITY_GROUPING_COUNT):
        current_path_list = object_path_list[i:i+ACTIVITY_GROUPING_COUNT]
        portal_activities.activate(activity='SQLQueue', priority=3)\
                                    .callMethodOnObjectList(current_path_list,
                                                            'Base_registerUrl')


class BTreeMappingDict(Implicit):
  """
  Strictly follows dict API
  """
  def __init__(self, namespace):
    self.namespace = namespace
    Implicit.__init__(self)

  def _getStorage(self):
    """
    return the BTree sub-level
    create it if does not exists.
    """
    btree = self.aq_parent._global_mapping_storage
    if self.namespace not in btree:
      btree[self.namespace] = OOBTree()
    return btree[self.namespace]

  def __len__(self):
    return len(self._getStorage())

  def keys(self):
    return self._getStorage().keys()

  def values(self):
    return self._getStorage().values()

  def items(self):
    return self._getStorage().items()

  def __getitem__(self, key):
    if key is None:
      raise KeyError(key)
    return self._getStorage()[key]

  def __contains__(self, key):
    return key in self._getStorage().keys()

  def get(self, key, default=None):
    if key is None:
      return default
    return self._getStorage().get(key, default)

  def __setitem__(self, key, value):
    self._getStorage()[key] = value

  def __delitem__(self, key):
    if key is None:
      raise KeyError(key)
    del self._getStorage()[key]

InitializeClass(UrlRegistryTool)
