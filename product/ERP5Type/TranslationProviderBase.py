from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#               2006 Nexedi
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from .Permissions import AccessContentsInformation, ManagePortal, \
  ModifyPortalContent
from OFS.SimpleItem import SimpleItem
from Acquisition import aq_base
from Products.ERP5Type.Globals import PersistentMapping, Persistent
from Products.ERP5Type.Accessor.Translation import \
  TRANSLATION_DOMAIN_CONTENT_TRANSLATION
import six

class TranslationProviderBase(object):
  """
  Provide Translation Tabs and management methods for PropertyTranslationDomain
  """
  security = ClassSecurityInfo()

  security.declareProtected(AccessContentsInformation,
                            'getPropertyTranslationDomainDict')
  def getPropertyTranslationDomainDict(self):
    """
    Return all translations defined by a provider.
    """
    property_domain_dict = {}
    for prop in self._getPropertyHolder().getAccessorHolderPropertyList():
      if prop.get('translatable'):
        prop_id = prop['id']
        property_domain_dict[prop_id] = TranslationInformation(
          prop_id,
          prop.get('translation_domain'),
        )
    try:
      my_property_domain_dict = aq_base(self)._property_domain_dict
    except AttributeError:
      pass
    else:
      property_domain_dict.update(my_property_domain_dict)
    return {k: v.__of__(self) for k, v in six.iteritems(property_domain_dict)}

  security.declarePublic('getContentTranslationDomainPropertyNameList')
  def getContentTranslationDomainPropertyNameList(self):
    return [x for x, y in six.iteritems(self.getPropertyTranslationDomainDict())
      if y.getDomainName() == TRANSLATION_DOMAIN_CONTENT_TRANSLATION]

  security.declareProtected(ManagePortal, 'setTranslationDomain')
  def setTranslationDomain(self, prop_name, domain):
    """
    Set a translation domain for given property.
    """
    try:
      property_domain_dict = aq_base(self)._property_domain_dict
    except AttributeError:
      self._property_domain_dict = property_domain_dict = PersistentMapping()
    else:
      # BBB: If domain dict is not a stand-alone peristent object, changes made
      # to it won't be persistently stored. It used to work because the whole
      # dict was replaced, hence triggering a change on self. But this creates
      # an inconvenient API. For the sake of keeping BT diffs quiet, don't cast
      # that dict into a PersistentMapping.
      if not isinstance(property_domain_dict, Persistent):
        self._p_changed = 1
    property_domain_dict[prop_name] = TranslationInformation(prop_name, domain)
    # Reset accessor cache
    self.getPortalObject().portal_types.\
      resetDynamicDocumentsOnceAtTransactionBoundary()

InitializeClass(TranslationProviderBase)

class TranslationInformation(SimpleItem):
  """
  This class represent the association between a property of a portal type and
  the domain name used to translate this property
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  def __init__(self, property_name='', domain_name=None):
    """
    Set up an instance
    """
    self.property_name = property_name
    self.domain_name = domain_name

  security.declareProtected(AccessContentsInformation, 'getPropertyName')
  def getPropertyName(self):
    """
    Return the property name
    """
    return self.property_name

  security.declareProtected(AccessContentsInformation, 'getDomainName')
  def getDomainName(self):
    """
    Return the domain name
    """
    return self.domain_name

  security.declareProtected(ModifyPortalContent, 'edit')
  def edit(self, edit_order=(), **kw):
    self._p_changed = 1
    self.__dict__.update((k, v or None) for k, v in six.iteritems(kw))

InitializeClass(TranslationInformation)
