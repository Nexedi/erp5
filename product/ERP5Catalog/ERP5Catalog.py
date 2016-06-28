# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SARL. All Rights Reserved.
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

from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.patches.PropertyManager import PropertyManager

import OFS.History
from Products.ZSQLCatalog.SQLCatalog import Catalog, CatalogError
from AccessControl import ClassSecurityInfo, getSecurityManager

manage_addERP5CatalogForm = DTMLFile('dtml/addERP5Catalog',globals())

def manage_addERP5Catalog(self, id, title,
             vocab_id='create_default_catalog_', # vocab_id is a strange name - not abbreviation
             REQUEST=None,
             **kw):
  """Add a Catalog object
  """
  id = str(id)
  title = str(title)
  vocab_id = str(vocab_id)
  if vocab_id == 'create_default_catalog_':
    vocab_id = None

  c = ERP5Catalog(id, title, self)
  self._setObject(id, c)
  c = self._getOb(id)
  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect( 'manage_main' )
  return c

class ERP5Catalog(Folder, Catalog):
  """
  Catalog Folder inside ERP5 to store indexes
  """

  meta_type = "ERP5 Catalog"
  portal_type = 'Catalog'
  allowed_types = ('Python Script', 'SQL Method',)
  #TODO(low priority): Add an icon to display at ERP5 Zope interface
  icon = None
  # Activate isRADContent cause we need to generate accessors and default values
  isRADContent = 1
  global valid_method_meta_type_list_new
  valid_method_meta_type_list_new = ('ERP5 SQL Method', 'ERP5 Python Script')

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  security.declareProtected(Permissions.ManagePortal,
                              'manage_editProperties',
                              'manage_changeProperties',
                              'manage_propertiesForm',
                                )

  manage_options = ( Folder.manage_options+
                     OFS.History.Historical.manage_options
                   )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    , PropertySheet.CategoryCore
                    , PropertySheet.Catalog
                    )

  # Declarative Constructors
  constructors = (manage_addERP5CatalogForm, manage_addERP5Catalog,)

  # Use functions inherited from SQLCatalog for property setters
  _setPropValue = Catalog._setPropValue

  def __init__(self, id, title='', container=None):
    # Initialize both SQLCatalog as well as Folder
    Catalog.__init__(self, id, title='', container=None)
    Folder.__init__(self, id)
    self.id = id
    self.title = title

  # Filter content (ZMI))
  def filtered_meta_types(self, user=None):
    # Filters the list of available meta types.
    all = Folder.filtered_meta_types(self)
    meta_types = []
    for meta_type in self.all_meta_types():
      if meta_type['name'] in self.allowed_types:
        meta_types.append(meta_type)
    return meta_types

  security.declarePrivate('getCatalogMethodIds')
  def getCatalogMethodIds(self,
      valid_method_meta_type_list=valid_method_meta_type_list_new):
    """Find ERP5 SQL methods in the current folder and above
    This function return a list of ids.
    """
    return super(ERP5Catalog, self).getCatalogMethodIds(
      valid_method_meta_type_list=valid_method_meta_type_list_new)

InitializeClass(ERP5Catalog)

class ERP5CatalogError(CatalogError): pass
