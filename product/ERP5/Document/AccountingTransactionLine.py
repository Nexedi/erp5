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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.DeliveryLine import DeliveryLine

from zLOG import LOG

class AccountingTransactionLine(DeliveryLine):
  """
  Accounting Transaction Lines allow to move some quantity of money from a source to a destination
  """

  meta_type = 'ERP5 Accounting Transaction Line'
  portal_type = 'Accounting Transaction Line'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    )

  # Declarative interfaces
  __implements__ = ( )

  # Factory Type Information
  factory_type_information = \
    {    'id'             : portal_type
       , 'meta_type'      : meta_type
       , 'description'    : """\
Une ligne tarifaire."""
       , 'icon'           : 'accounting_transaction_line_icon.gif'
       , 'product'        : 'ERP5'
       , 'factory'        : 'addAccountingTransactionLine'
       , 'immediate_view' : 'accounting_transaction_line_view'
       , 'allow_discussion'     : 1
       , 'allowed_content_types': ('',
                                    )
       , 'filter_content_types' : 1
       , 'global_allow'   : 1
       , 'actions'        :
      ( { 'id'            : 'view'
        , 'name'          : 'View'
        , 'category'      : 'object_view'
        , 'action'        : 'accounting_transaction_line_view'
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
        , 'action'        : 'acccounting_transaction_line_print'
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


  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceDebit')
  def getSourceDebit(self):
    """
      Return the quantity
    """  
    quantity = self.getQuantity()
    
    try:
      quantity = float(quantity)
    except:
      quantity = 0.0

    if quantity < 0:
      return - quantity
    else:
      return 0.0

  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceCredit')
  def getSourceCredit(self):
    """
      Return the quantity
    """
    quantity = self.getQuantity()

    try:
      quantity = float(quantity)
    except:
      quantity = 0.0

    if quantity < 0:
      return 0.0
    else:
      return quantity

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationDebit')
  getDestinationDebit = getSourceCredit

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationCredit')
  getDestinationCredit = getSourceDebit

  security.declareProtected(Permissions.ModifyPortalContent, 'setSourceDebit')
  def setSourceDebit(self, source_debit):
    """
      Set the quantity
    """
    if source_debit in (None, ''):
      return 0.0
    try:
      source_debit = float(source_debit)
    except:
      source_debit = 0.0
    self.setQuantity(- source_debit)

  security.declareProtected(Permissions.ModifyPortalContent, 'setSourceCredit')
  def setSourceCredit(self, source_credit):
    """
      Set the quantity
    """
    if source_credit in (None, ''):
      return 0.0
    try:
      source_credit = float(source_credit)
    except:
      source_credit = 0.0
    self.setQuantity(source_credit)

  security.declareProtected(Permissions.ModifyPortalContent, 'setDestinationDebit')
  def setDestinationDebit(self, destination_debit):
    """
      Temp
    """
    return

  security.declareProtected(Permissions.ModifyPortalContent, 'setDestinationCredit')
  def setDestinationCredit(self, destination_credit):
    """
      Temp
    """
    return

  security.declarePrivate('_setSource')
  def _setSource(self, value):
    self._setCategoryMembership('source', value, base=0)
    source = self.restrictedTraverse(value)
    destination = self.getDestination()
    mirror_list = source.getDestinationList()
    #LOG('_setSource', 0, 'value = %s, mirror_list = %s, destination = %s' % (str(value), str(mirror_list), str(destination)))
    if len(mirror_list) > 0 and destination not in mirror_list:
      self._setCategoryMembership('destination', mirror_list[0], base=0)

  security.declareProtected(Permissions.ModifyPortalContent, 'setSource')
  def setSource(self, value):
    self._setSource(value)
    self.reindexObject()

  security.declarePrivate('_setDestination')
  def _setDestination(self, value):
    self._setCategoryMembership('destination', value, base=0)
    destination = self.restrictedTraverse(value)
    source = self.getSource()
    mirror_list = destination.getDestinationList()
    #LOG('_setDestination', 0, 'value = %s, mirror_list = %s, source = %s' % (str(value), str(mirror_list), str(source)))
    if len(mirror_list) > 0 and source not in mirror_list:
      self._setCategoryMembership('source', mirror_list[0], base=0)

  security.declareProtected(Permissions.ModifyPortalContent, 'setDestination')
  def setDestination(self, value):
    self._setDestination(value)
    self.reindexObject()

  security.declarePrivate('_edit')
  def _edit(self, REQUEST = None, force_update = 0, **kw):
    if kw.has_key('source'):
      self._setSource(kw['source'])
    if kw.has_key('destination'):
      self._setDestination(kw['destination'])
    DeliveryLine._edit(self, REQUEST=REQUEST, force_update = force_update, **kw)
