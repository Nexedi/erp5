# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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

import sys
from Products.ZSQLCatalog.ZSQLCatalog import ZCatalog
from Products.ERP5Type import Permissions
from Products.CMFCore.CatalogTool import CatalogTool as CMFCoreCatalogTool
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.CMFActivity.ActivityTool import GroupedMessage
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import PropertySheet
from AccessControl import ClassSecurityInfo

from zLOG import LOG, PROBLEM, WARNING, INFO
from Products.ERP5Catalog import CatalogTool as CMFCore_CatalogToolModule
from Products.ERP5Catalog.CatalogTool import IndexableObjectWrapper
from Products.ERP5Catalog.CatalogTool import RelatedBaseCategory

CMFCore_CatalogTool = CMFCore_CatalogToolModule.CatalogTool

class ERP5CatalogTool(BaseTool, CMFCore_CatalogTool):

    id = 'portal_catalog'
    title = 'Catalog Tool'
    meta_type = 'Catalog Tool'
    portal_type = 'Catalog Tool'
    allowed_types = ('Catalog',)

    # Declarative security
    security = ClassSecurityInfo()

    # Explicitly add tabs for manage_options
    manage_options = ({'label': 'View', 'action': 'view'},
                      {'label': 'Contents', 'action': 'manage_main'},
                      {'label': 'Security', 'action': 'manage_access'},
                      {'label': 'Undo', 'action': 'manage_UndoForm'},
                      {'label': 'Ownership', 'action': 'manage_owner'},
                      {'label': 'Interfaces', 'action': 'manage_interfaces'},
                      {'label': 'Find', 'action': 'manage_findForm'},
                      {'label': 'History', 'action': 'manage_change_history_page'},
                      {'label': 'Workflows', 'action': 'manage_workflowsTab'},
                     )

    property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    , PropertySheet.CategoryCore
                    , PropertySheet.CatalogTool
                    )

    # Use reindexObject method from BaseTool class and declare it public
    reindexObject = BaseTool.reindexObject
    security.declarePublic('reindexObject')
    # Security Declarations
    security.declarePublic('getSQLCatalogIdList')

    # Explicit Inheritance
    __url = CMFCoreCatalogTool._CatalogTool__url
    unindexObject = CMFCore_CatalogTool.unindexObject
    __call__  = CMFCore_CatalogTool.__call__
    _aq_dynamic = CMFCore_CatalogTool._aq_dynamic
    ZopeFindAndApply = CMFCore_CatalogTool.ZopeFindAndApply
    #_checkId = CMFCore_CatalogTool._checkId
    listDAVObjects = CMFCore_CatalogTool.listDAVObjects
    __class_init__ = CMFCore_CatalogTool.__class_init__

    security.declareProtected(Permissions.ManagePortal
                , 'manage_overview')
    manage_overview = DTMLFile('dtml/explainCatalogTool', globals())

    # IMPORTANT:Solve inheritance conflict, this is necessary as getObject from
    # Base gives the current object, which migth be harmful for CatalogTool as
    # we use this function here to sometimes get objects to delete which if
    # not solved of inheritance conflict might lead to catalog deletion.
    getObject = ZCatalog.getObject

    default_erp5_catalog_id = None

    def __init__(self, id=''):
        ZCatalog.__init__(self, self.getId())
        BaseTool.__init__(self, self.getId())

    def _isBootstrapRequired(self):
      return False

    def _bootstrap(self):
      pass

    def _setDefaultErp5CatalogId(self, value):
      """
      Override this setter function so as to keep default_sql_catalog_id
      and default_erp5_catalog_id same for portal_catalog after everyhting has
      been migrated to erp5 portal_catalog
      """
      self._baseSetDefaultErp5CatalogId(value)
      self._baseSetDefaultSqlCatalogId(value)

    def _edit(self, **kw):
      """
      Override to update both default_sql_catalog_id and default_erp5_catalog_id
      in same edit
      """
      BaseTool._edit(self, **kw)
      value = self.getDefaultErp5CatalogId()
      self._setDefaultErp5CatalogId(value)

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types for CatalogTool
        meta_types = []
        for meta_type in ERP5CatalogTool.inheritedAttribute('filtered_meta_types')(self):
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    allowedContentTypes = BaseTool.allowedContentTypes
    getVisibleAllowedContentTypeList = BaseTool.getVisibleAllowedContentTypeList

    # The functions 'getERP5CatalogIdList' and 'getERP5Catalog' are meant to
    # be used in restricted environment, cause the reason they were created is
    # the transition of Catalog from SQLCatalog to ERP5Catalog, which basically
    # means Catalog is going to be an ERP5 object, which is why we need these
    # functions to be declared public.

    security.declarePublic('getERP5CatalogIdList')
    def getERP5CatalogIdList(self):
      """
      Get ERP5 Catalog Ids
      """
      id_list = [l for l in self.objectIds(spec=('ERP5 Catalog',))]
      return id_list

    security.declarePublic('getERP5Catalog')
    def getERP5Catalog(self, id=None, default_value=None):
      """
      Get current ERP5 Catalog
      """
      if id is None:
        if not self.default_erp5_catalog_id:
          id_list = self.getERP5CatalogIdList()
          if len(id_list) > 0:
            self.default_erp5_catalog_id = id_list[0]
          else:
            return default_value
        id = self.default_erp5_catalog_id

      return self._getOb(id, default_value)

    security.declarePrivate('reindexCatalogObject')
    def reindexCatalogObject(self, object, idxs=None, sql_catalog_id=None,**kw):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        '''
        if idxs is None: idxs = []
        url = self.__url(object)
        self.catalog_object(object, url, idxs=idxs, sql_catalog_id=sql_catalog_id,**kw)

    security.declarePrivate('getCatalogUrl')
    def getCatalogUrl(self, object):
      return self.__url(object)

InitializeClass(ERP5CatalogTool)
