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
from Products.ERP5.Document.Movement import Movement

from zLOG import LOG

class OrderLine(DeliveryLine):
    """
      Une ligne de commande d?init ?alement un prix
      Un element de tarif est un prix pour un ensemble de conditions d'application...
    """

    meta_type = 'ERP5 Order Line'
    portal_type = 'Order Line'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.DublinCore
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.VariationRange
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Une ligne tarifaire."""
         , 'icon'           : 'order_line_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addOrderLine'
         , 'immediate_view' : 'order_line_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'order_line_view'
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
          , 'action'        : 'order_line_print'
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

    security.declarePrivate( '_edit' )
    def _edit(self, REQUEST=None, force_update = 0, **kw):
      DeliveryLine._edit(self, REQUEST=REQUEST, force_update = force_update, **kw)
      # We must expand our applied rule if needed
      self.updateAppliedRule() # Actually called on parent

    # For generation of matrix lines
    security.declareProtected( Permissions.ModifyPortalContent, '_setVariationCategoryList' )
    def _setVariationCategoryList(self, value):
      """
          Define the indices provided
          one list per index (kw)

          Any number of list can be provided
      """
      Movement._setVariationCategoryList(self, value)
      # Update the cell range automatically
      # This is far from easy and requires some specific wizzardry
      base_id = 'movement'
      kwd = {'base_id': base_id}
      new_range = self.DeliveryLine_asCellRange() # This is a site dependent script
      self._setCellRange(*new_range, **kwd )
      #LOG('After _setCellRange in OrderLine',0,'')
      cell_range_key_list = self.getCellRangeKeyList(base_id = base_id)
      if cell_range_key_list <> [[None, None]] :
        for k in cell_range_key_list:
          c = self.newCell(*k, **kwd)
          #LOG('OrderLine _setVariationCategoryList', 0, 'k = %s, c = %s, self.getVariationBaseCategoryList() = %s' % (repr(k), repr(c), repr(self.getVariationBaseCategoryList())))
          c.edit( domain_base_category_list = self.getVariationBaseCategoryList(),
                  mapped_value_property_list = ('quantity', 'price',),
                  predicate_operator = 'SUPERSET_OF',
                  predicate_value = filter(lambda k_item: k_item is not None, k),
                  variation_category_list = filter(lambda k_item: k_item is not None, k),
                  force_update = 1
                )
        #LOG('After edit cells in OrderLine',0,'')
      else:
        # If only one cell, delete it
        cell_range_id_list = self.getCellRangeIdList(base_id = base_id)
        for k in cell_range_id_list:
          if self.get(k) is not None:
            self[k].flushActivity(invoke=0)
            self[k].immediateReindexObject() # We are forced to do this is url is changed (not uid)
            self._delObject(k)

    security.declarePrivate('_checkConsistency')
    def _checkConsistency(self, fixit=0, mapped_value_property_list = ('quantity', 'price')):
      """
        Check the constitency of transformation elements
      """
      return DeliveryLine._checkConsistency(self, fixit=fixit, mapped_value_property_list=mapped_value_property_list)

    def applyToOrderLineRelatedMovement(self, portal_type='Simulation Movement', method_id = 'expand'):
      """
        Warning: does not work if it was not catalogued immediately
      """
      # Find related in simulation
      for my_simulation_movement in self.getOrderRelatedValueList(
                                              portal_type = 'Simulation Movement'):
        # And apply
        getattr(my_simulation_movement, method_id)()
      for c in self.contentValues(filter={'portal_type': 'Delivery Cell'}):
        for my_simulation_movement in c.getOrderRelatedValueList(
                                              portal_type = 'Simulation Movement'):
          # And apply
          getattr(my_simulation_movement, method_id)()

    def reindexObject(self, *k, **kw):
      """
        Reindex children and simulation
      """
      if self.isIndexable:
        # Reindex children
        self.activate().recursiveImmediateReindexObject()
        #self.activate().applyToOrderLineRelatedMovement(method_id = 'expand')
        # We do it at Order level through edit
        # This logic should actually be put in worklow

    def manage_afterAdd(self, item, container):
      """
          Add self to the catalog.
          (Called when the object is created or moved.)
      """
      DeliveryLine.manage_afterAdd(self, item, container)
      if self.aq_parent.getSimulationState() not in self.getPortalDraftOrderStateList():
        # Only reexpand order rule when we add lines
        self.aq_parent.activate()._createOrderRule()

    # Simulation Consistency Check
    def getSimulationQuantity(self):
      """
          Computes the target quantities in the simulation
      """
      result = self.OrderLine_zGetRelatedQuantity(uid=self.getUid())
      if len(result) > 0:
        return result[0].quantity
      return None
