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

from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Type.ObjectMessage import ObjectMessage
from Products.ERP5Type import Permissions

# Define legacy calls which are superceded by new calls
def getLegacyCallableIdItemList(self):
  return (
      ('WebSection_getPermanentURLForView', 'getPermanentURL'),
    )


@transactional_cached(key_method=lambda *args, **kw: None)
def getSkinPrefixList(self):
  """Return the list of acceptable prefixes for skins.
  """
  portal = self.getPortalObject()

  # Add portal types prefix
  portal_types = portal.portal_types
  skin_prefix_list = []
  for portal_type in portal_types.contentValues():
    portal_prefix = portal_type.getId().replace(' ', '')
    skin_prefix_list.append(portal_prefix)

  # Add document classes prefix
  skin_prefix_list.extend(portal_types.getDocumentTypeList())

  # Add mixins prefix
  skin_prefix_list.extend(portal_types.getMixinTypeList())

  # Add interfaces prefix, without the I prefix
  skin_prefix_list.extend([x[1:] for x in portal_types.getInterfaceTypeList()])

  # Add property sheets
  skin_prefix_list.extend([
      x.getId().replace(' ', '')
      for x in portal.portal_property_sheets.contentValues()])

  # Add other prefix
  skin_prefix_list.extend((
    'ERP5Type',

    # Modules (maybe should be interfaces)
    'Module',
    'InventoryModule',
    'OrderModule',
    'DeliveryModule',
    'PackingListModule',
    'SupplyModule',
    'ResourceModule',

    # Base classes (maybe should be interfaces)
    'Entity', # A base class for Person / Organisation
    'PackingListLine',
    'IndividualVariation',
    'ExternalLogin',

    # Catalog brains
    'Brain',
    'InventoryListBrain',
    'TrackingListBrain',
    'MovementHistoryListBrain',

    # Zope classes
    'DCWorkflow', # some workflow script use this, not sure it's correct.
    'SkinsTool',
    'MailHost',
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
  'connectorERP5',
  'resolveUid',
  'IndividualVariation_init',
  'QuantityUnitConversion_getQuantityUnitList',
  'PackingListContent_updateAfterEdit',
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
  'ERP5VCS_doCreateJavaScriptDiff.js',
  'ERP5VCS_doCreateJavaScriptStatus.js',
  'PdmZuite_CommonTemplate',
  'PdmZuite_checkStockBrowser',
  'PdmZuite_createDelivery',
  'PdmZuite_deleteData',
  'PdmZuite_reset',
  'PdmZuite_CommonTemplateForRenderjsUi',
  'PdmZuite_checkStockBrowserForRenderjsUi',
  'AdvancedInvoiceTransaction_postTransactionLineGeneration',
  'InvoiceTransaction_jumpToOrder',
  'InvoiceTransaction_jumpToPackingList',
  'TaskDistributorAlarm_optimize',
  'TestDocument_optimize',
  'TestResultAlarm_restartStuckTestResult',
  'ActivityTool_viewWatcher',
  'BaseWorkflow_viewWorkflowActionDialog',
  'Base_jumpToRelatedObjectList',
  'Base_viewHistory',
  'Base_viewZODBHistory',
  'BusinessTemplate_viewObjectsDiff',
  'CacheFactory_viewStatisticList',
  'Folder_deleteDocumentListStatusDialog',
  'Folder_generateWorkflowReportDialog',
  'Folder_modifyDocumentListStatusDialog',
  'PasswordTool_viewEmailPassword',
  'PasswordTool_viewResetPassword',
  'Base_FieldLibrary',
  'Base_viewDialogFieldLibrary',
  'ERP5Site_newCredentialRecoveryDialog',
  'ERP5Site_viewCredentialRequestForm',
  'Document_jumpToRelatedDocumentList',
  'FCKeditor_viewDocumentSelectionDialog',
  'FCKeditor_viewImageSelectionDialog',
  'BaseWorkflow_FieldLibrary',
  'BaseTradePurchase_FieldLibrary',
  'BaseTradeSale_FieldLibrary',
  'Order_viewDialogFieldLibrary',
  'PackingListLine_viewFieldLibrary',
  'Tester_view',
  'GenericSolver_viewConfigurationFormBox',
  'BaseTradeProject_FieldLibrary',
  'OrderMilestone_view',
  'TradeLine_viewProject',
  'ProductionDelivery_viewInventory',
  'FiscalReport_doReport',
  'FiscalReportCell_creditorAccountsSum',
  'FiscalReportCell_creditorBankAccountsBalance',
  'FiscalReportCell_debtorAccountsSum',
  'FiscalReportCell_debtorBankAccountsBalance',
  'FiscalReportCell_doGetInventory',
  'FiscalReportCell_formatCell',
  'FiscalReportCell_getBalance',
  'FiscalReportCell_getBankAccountBalance',
  'FiscalReportCell_getThirdPartyBalance',
  'FiscalReportCell_getThirdPartyCreditorBalance',
  'FiscalReportCell_getThirdPartyDebtorBalance',
  'FiscalReportCell_roundBalance',
  'GAPCategory_getURLFromId',
}

# TODO: ignore officejs skins for now, but these should probably be
# renamed
ignored_skin_id_set.update({
  # erp5_officejs
  'Base_cloneDocumentForCodemirrorEditor',
  'Base_viewNewContentDialogForCodemirror',
  'Base_cloneDocumentForSlideshowEditor',
  'Base_cloneNotebookForNotebookEditor',
  'Base_downloadDialogForNotebookEditor',
  'Base_downloadHtmlDialogForNotebookEditor',
  'Base_exportDialogForNotebookEditor',
  'Base_uploadDialogForNotebookEditor',
  'Notebook_previewViewForNotebookEditor',
  'Base_cloneDocumentForPDFViewer',
  'Base_viewNewContentDialogForPdfViewer',
  'WebSite_createAppConfigurationManifest',
  'Base_cloneDocumentForTextEditor',
  'Base_viewNewContentDialogForTextEditor',
  'Base_cloneDocumentForSvgEditor',
  'Base_viewNewContentDialogForSvgEditor',

  # erp5_officejs_jquery_app
  'Base_cloneDocumentForWebTable',
  'Base_viewNewContentDialogForWebTableEditor',
  'Base_cloneDocumentForImageEditor',
  'Base_viewNewContentDialogForImageEditor',

  # erp5_officejs_ooffice
 'Base_cloneDocumentForOofficeEditor',
 'Base_uploadDialogForOofficeEditor',
 'SpreadsheetDocument_viewAsJioForOofficeSpreadsheetEditor',
 'Base_downloadDialogForOofficeEditor',
 'PresentationDocument_viewAsJioForOofficePresentationEditor',
})

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
                      message='Wrong prefix %s for %s %s' % (prefix, self.meta_type, document_id)))

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

