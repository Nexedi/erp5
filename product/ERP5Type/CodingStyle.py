# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Jean-Paul Smets <jp@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.ObjectMessage import ObjectMessage
from Products.ERP5Type import Permissions

# Define legacy calls which are superceded by new calls
def getLegacyCallableIdItemList(self):
  return (
      ('WebSection_getPermanentURLForView', 'getPermanentURL'),
    )

# Define acceptable prefix list for skin folder items
skin_prefix_list = None
def getSkinPrefixList(self):
  """
  Return the list of acceptable prefix. Cache the result.

  TODO: make the cache more efficient (read-only transaction
  cache)
  """
  global skin_prefix_list
  if skin_prefix_list:
    return skin_prefix_list

  portal = self.getPortalObject()

  # Add portal types prefix
  portal_types = portal.portal_types
  skin_prefix_list = []
  for portal_type in portal_types.contentValues():
    portal_prefix = portal_type.getId().replace(' ', '')
    skin_prefix_list.append(portal_prefix)

  # Add document classes prefix
  skin_prefix_list.extend(self.portal_types.getDocumentTypeList())

  # Add mixins prefix
  skin_prefix_list.extend(self.portal_types.getMixinTypeList())

  # Add interfaces prefix
  # XXX getInterfaceTypeList does not include file system interfaces ... keep this low-level way for now.
  from Products.ERP5Type import interfaces
  for interface_name in (
      list(interfaces.__dict__.keys())
      + list(self.portal_types.getInterfaceTypeList())):
    if interface_name.startswith('I'):
      skin_prefix_list.append(interface_name[1:])
    # XXX do we really add with the I prefix ?
    skin_prefix_list.append(interface_name)

  # Add other prefix
  skin_prefix_list.extend((
    'ERP5Type',
    'Module',
    'Brain', # Catalog brains

    'DCWorkflow', # some workflow script use this, not sure it's correct.
    'SkinsTool',
    'MailHost',

    'Entity', # A base class for Person / Organisation
    'Zuite', # Products.Zelenium test suites

    # ERP5Form
    'Form',
    'ListBox',
    'PlanningBox',
    'OOoChart',
  ))

  return set(skin_prefix_list)


# Some skin names that does not respect our conventions but are ignored, for example
# when this naming is used by zope or scripts that changing would be too hard.
ignored_skin_id_set = {
  'twiddleAuthCookie',
  'setAuthCookie',
  'ERP5Document_getHateoas',
  'Script_getParams',
  'AccessTabZuite_disablePreference',
  'AccessTabZuite_setPreference',
  'BTZuite_CommonTemplate',
  'BTZuite_reset',
  'FooViewDummyMultiListFieldDialog_setFieldPropertyList',
  'FooView_setFieldsProperties',
  'ListBoxDialogModeZuite_CommonTemplate',
  'ListBoxDialogModeZuite_reset',
  'ListBoxZuite_CommonTemplate',
  'ListBoxZuite_getSelectionCheckedUidsAsHtml',
  'ListBoxZuite_reset',
  'ListBoxZuite_resetReportSelections',
  'ListBoxZuite_setPreferredListboxViewModeLineCount',
  'MatrixBoxZuite_CommonTemplate',
  'OOoImportZuite_importFile',
  'OOoImportZuite_reset',
  'PTZuite_CommonTemplate',
  'PortalType_addAction',
  'PortalType_deleteAction',
  'RelationFieldZuite_CommonTemplate',
  'Field_getDescription',
  'ERP5XhtmlStyle_redirect',
  'connectorCPS.py',
  'connectorERP5',
  'connectorPlone.py',
  'resolveUid',
  'IndividualVariation_init',
  'QuantityUnitConversion_getQuantityUnitList',
  'ResourceModule_getConvertedInventoryList',
  'ResourceModule_getConvertedInventoryStat',
  'ResourceModule_getSelection',
  'DeliveryModule_getDeliveryLineList',
  'DeliveryModule_getDeliveryLineReportSectionList',
  'DeliveryModule_getMovementPortalTypeItemList',
  'DeliveryModule_getShipmentDeliveryList',
  'DeliveryModule_getShipmentLineData',
  'DeliveryModule_getShipmentLineList',
  'DeliveryModule_getShipmentReportSectionList',
  'OrderModule_activateGetOrderStatList',
  'OrderModule_deleteAutoPlannedOrderList',
  'OrderModule_filterOrderStatResul',
  'OrderModule_getOrderReport',
  'OrderModule_getOrderReportParameterDict',
  'OrderModule_getOrderReportSectionList',
  'OrderModule_getOrderStatList',
  'OrderModule_launchOrderReport',
  'OrderModule_processOrderStat',
  'OrderModule_statOrderStatList',
  'PackingListContent_updateAfterEdit',
  'PackingListModule_getPackingListReport',
  'Builder_selectAutoPlannedOrderList',
  'Builder_updateManufacturingOrderAfterBuild',
  'ManufacturingOrderBuilder_selectSimulationMovement',
  'ProductionDelivery_copyOrderProperties',
  'ProductionDelivery_generateReference',
  'ProductionDelivery_getFutureInventoryList',
  'ProductionDelivery_getSimulationStateColorText',
  'CurrencyExchange_getExchangeRateList',
  'ERP5Folder_getUnrestrictedContentTypeList',
  'FCKeditor_getDocumentList',
  'FCKeditor_getDocumentListQuery',
  'FCKeditor_getImageList',
  'FCKeditor_getSetReferenceUrl',
  'Credential_accept',
  'Credential_checkConsistency',
  'Credential_copyRegistredInformation',
  'Credential_updatePersonPassword',
  'InvoiceTransaction_postGeneration',
  'InvoiceTransaction_postTransactionLineGeneration',
  'InvoiceTransaction_selectDelivery',
  'InvoiceTransaction_selectInvoiceMovement',
  'PurchaseInvoice_selectTradeModelMovementList',
  'SaleInvoice_selectTradeModelMovementList',
  'SaleInvoiceTransaction_selectTaskReportMovement',
  'TaskListOverviewGadget_setPreferences',
  'TaskListsGadgetListbox_getLineCss',
  'InventoryModule_reindexMovementList',
  'DeliveryModule_mergeDeliveryList',
}

# Generic method to check consistency of a skin item
def checkConsistency(self, fixit=0, source_code=None):
  """
  Make sure skin folder item has appropriate prefix
  and that its source code, if any, does not contain
  calls to legacy methods
  """
  if fixit: raise NotImplementedError
  message_list = []
  portal_path = self.getPortalObject().getPath()
  portal_path_len = len(portal_path)

  # Make sure id is acceptable
  document_id = self.id
  if document_id != document_id.lower() and document_id not in ignored_skin_id_set:
    # Only test prefix with big caps
    prefix = document_id.split('_')[0]
    if prefix not in getSkinPrefixList(self):
      message_list.append(
        ObjectMessage(object_relative_url='/'.join(self.getPhysicalPath())[portal_path_len:],
                      message='Wrong prefix %s for python script %s' % (prefix, document_id)))

  # Make sure source code does not contain legacy callables
  if source_code:
    for legacy_string, new_string in getLegacyCallableIdItemList(self):
      if source_code.find(legacy_string) >= 0:
        message_list.append(
          ObjectMessage(object_relative_url='/'.join(self.getPhysicalPath())[portal_path_len:],
                        message='Source code of %s contains legacy call to %s' % (document_id, legacy_string)))

  return message_list

# Add checkConsistency to Python Scripts
def checkPythonScriptConsistency(self, fixit=0, filter=None, **kw):
  return checkConsistency(self, fixit=fixit, source_code=self.body())

from Products.PythonScripts.PythonScript import PythonScript
PythonScript.checkConsistency= checkPythonScriptConsistency
PythonScript.checkConsistency__roles__ = ('Manager',) # A hack to protect the method

# Add checkConsistency to Page Templates
def checkPageTemplateConsistency(self, fixit=0, filter=None, **kw):
  return checkConsistency(self, fixit=fixit, source_code=self.read())

from Products.PageTemplates.PageTemplate import PageTemplate
PageTemplate.checkConsistency= checkPageTemplateConsistency
PageTemplate.checkConsistency__roles__ = ('Manager',) # A hack to protect the method

