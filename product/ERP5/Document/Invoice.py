##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.AccountingTransaction import AccountingTransaction

class Invoice(AccountingTransaction):
    # CMF Type Definition
    meta_type = 'ERP5 Invoice'
    portal_type = 'Invoice'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Delivery
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Amount
                      , PropertySheet.Reference
                      , PropertySheet.PaymentCondition
                      , PropertySheet.ValueAddedTax
                      , PropertySheet.EcoTax
                      , PropertySheet.CopyrightTax
                      )

    # CMF Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
An order..."""
         , 'icon'           : 'invoice_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addInvoice'
         , 'immediate_view' : 'invoice_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Movement', 'Order Line',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'invoice_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'invoice_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
    def getTotalPrice(self):
      """
        Returns the total price for this invoice
      """
      aggregate = self.Invoice_zGetTotal()[0]
      return aggregate.total_price

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
    def getTotalQuantity(self):
      """
        Returns the total quantity for this invoice
      """
      aggregate = self.Invoice_zGetTotal()[0]
      return aggregate.total_quantity
    
    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalNetPrice')
    def getTotalNetPrice(self):
      """
        Returns the total net price for this invoice
      """
      return self.Invoice_zGetTotalNetPrice()
      
    security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationSate')
    def getSimulationState(self, id_only=1):
      """
        Returns the current state in simulation
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf = portal_workflow.getWorkflowById('accounting_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only )
