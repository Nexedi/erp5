##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.Utils import cartesianProduct

from Amount import Amount

from Products.ERP5.ERP5Globals import resource_type_list

from zLOG import LOG

class TransformedResource(XMLObject, XMLMatrix, Amount):
    """
        TransformedResource defines which
        resource is being transformed

        - variation
        - quantity

        Maybe defined by mapped values inside the transformed resource

        WARNING: the notion of category range is quite complex in this case.
           getVariationRangeCategoryList -> possible variations of the transformed
                                            resource ie. getVariationCategoryList
                                            of the resource
           getVariationCategoryList      -> variation value of the transformed
                                            resource (ie. default variation)

           getVariationRangeBaseCategoryList -> possible variation base categories
                                                of the transformed resource
                                                (ie. getVariationBaseCategoryList
                                                of the resource)
           getVariationBaseCategoryList      -> choice of variation base categories
                                                defined by the transformed resource
                          (should be the same as getVariationRangeBaseCategoryList)

           getTransformationVariationRangeBaseCategoryList OK
                                              -> possible variation base categories
                                                  which can be used the the
                                                 transformation matrix
                                                 (based on resource)
           getTransformationVariationBaseCategoryList OK
                                              -> choice of variation base categories
                                                  which can be used the the
                                                 transformation matrix
                                                 (based on resource)

           getTransformationVariationRangeCategoryList OK
                                              -> possible category values
                                                 which can be used in the
                                                 transformation matrix
                                                 (based on resource)
           getTransformationVariationCategoryList OK
                                              -> choice of category values
                                                 which can be used in the
                                                 transformation matrix

           XXX WE HAVE an issue here:
           - the variation range of the transformation
             defines both the variation range of the main resource
             and the variation range for matrices

           - where do we define default variation value
             for the resource produced by the transformation ?
             (probably in the domain fields)

           - where do we define selection parameters ?

           getResourceVariationCategoryList
           getResourceVariationRangeCategoryList

    """

    meta_type = 'ERP5 Transformed Resource'
    portal_type = 'Transformed Resource'
    add_permission = Permissions.AddERP5Content
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
                      , PropertySheet.TransformedResource
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Local property sheet
    _properties = (
      { 'id'          : 'variation_base_category',
        'storage_id'  : 'variation_base_category_list', # Coramy Compatibility
        'description' : "",
        'type'        : 'tokens',
        'acquisition_base_category' : ('resource',),
        'acquisition_portal_type'   : resource_type_list,
        'acquisition_copy_value'    : 0,
        'acquisition_mask_value'    : 0,
        'acquisition_sync_value'    : 0,
        'acquisition_accessor_id'   : 'getVariationBaseCategoryList', ### XXX BUG
        'acquisition_depends'       : None,
        'mode'        : 'w' },
    )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
A bank account number holds a collection of numbers
and codes (ex. SWIFT, RIB, etc.) which may be used to
identify a bank account."""
         , 'icon'           : 'transformed_resource_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addTransformedResource'
         , 'immediate_view' : 'transformed_resource_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'transformed_resource_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'transformed_resource_print'
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

    ### Variation matrix definition
    #
    security.declareProtected(Permissions.ModifyPortalContent, '_setQVariationBaseCategoryList')
    def _setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on
      """
      self._baseSetQVariationBaseCategoryList(value)
      kwd = {}
      kwd['base_id'] = 'quantity'
      kw = []
      transformation = self.aq_parent
      line_id = transformation.getVariationBaseCategoryLine()
      column_id = transformation.getVariationBaseCategoryColumn()
      line = [[None]]
      column = [[None]]
      for v in value:
        if v == line_id:
          line = [transformation.getCategoryMembershipList(v,base=1)]
        elif v == column_id:
          column = [transformation.getCategoryMembershipList(v,base=1)]
        else:
          kw += [transformation.getCategoryMembershipList(v,base=1)]
      kw = line + column + kw
      self.setCellRange(*kw, **kwd)
      # Empty cells if no variation
      if line == [[None]] and column == [[None]]:
        self.delCells(base_id='quantity')
      # And fix it in case the cells are not renamed (XXX this will be removed in the future)
      self._checkConsistency(fixit=1)

    security.declareProtected(Permissions.ModifyPortalContent, 'setQVariationBaseCategoryList')
    def setQVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on and reindex the object
      """
      self._setQVariationBaseCategoryList(value)
      self.reindexObject()

    security.declareProtected(Permissions.ModifyPortalContent, '_setVVariationBaseCategoryList')
    def _setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on
      """
      self._baseSetVVariationBaseCategoryList(value)
      kwd = {}
      kwd['base_id'] = 'variation'
      kw = []
      transformation = self.aq_parent
      line_id = transformation.getVariationBaseCategoryLine()
      column_id = transformation.getVariationBaseCategoryColumn()
      line = [[None]]
      column = [[None]]
      for v in value:
        if v == line_id:
          line = [transformation.getCategoryMembershipList(v,base=1)]
        elif v == column_id:
          column = [transformation.getCategoryMembershipList(v,base=1)]
        else:
          kw += [transformation.getCategoryMembershipList(v,base=1)]
      kw = line + column + kw
      self.setCellRange(*kw, **kwd)
      # Empty cells if no variation
      if line == [[None]] and column == [[None]]:
        self.delCells(base_id='variation')
      # And fix it in case the cells are not renamed (XXX this will be removed in the future)
      self._checkConsistency(fixit=1)

    security.declareProtected(Permissions.ModifyPortalContent, 'setVVariationBaseCategoryList')
    def setVVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Variation value (V)
        variate on and reindex the object
      """
      self._setVVariationBaseCategoryList(value)
      self.reindexObject()

    # Methods for matrix UI widgets
    security.declareProtected(Permissions.AccessContentsInformation, 'getQLineItemList')
    def getQLineItemList(self):
      base_category = self.aq_parent.getVariationBaseCategoryLine()
      if base_category in self.getQVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]

      result.sort() # XXX Temp until set / list issue solved
                    # solution is to use sets in some places and lists in others
                    # default and sets are used together
                    # list overrides default

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getQColumnItemList')
    def getQColumnItemList(self):
      base_category = self.aq_parent.getVariationBaseCategoryColumn()
      if base_category in self.getQVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]

      result.sort() # XXX Temp until set / list issue solved

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getQTabItemList')
    def getQTabItemList(self):
      """
        Returns a list of items which can be used as index for
        each tab of a matrix or to define a cell range.
      """
      transformation = self.aq_parent
      line_id = transformation.getVariationBaseCategoryLine()
      column_id = transformation.getVariationBaseCategoryColumn()
      base_category_list = transformation.getVariationBaseCategoryList()
      base_category = []
      # Accumulate in base_category a list of list of relative_url
      # which correspond to category memberships not taken into
      # account in lines of columns
      for c in base_category_list:
        if not c in (line_id, column_id):
          if c in self.getQVariationBaseCategoryList():
            base_category += [transformation.getCategoryMembershipList(c, base=1)]
      if len(base_category) > 0:
        # Then make a cartesian product
        # to calculate all possible combinations
        clist = cartesianProduct(base_category)
        result = []
        for c in clist:
          result += [(c,c)]
      else:
        result = [(None,'')]

      result.sort() # XXX Temp until set / list issue solved

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getVLineItemList')
    def getVLineItemList(self):
      base_category = self.aq_parent.getVariationBaseCategoryLine()
      if base_category in self.getVVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getVColumnItemList')
    def getVColumnItemList(self):
      base_category = self.aq_parent.getVariationBaseCategoryColumn()
      if base_category in self.getVVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]

      result.sort() # XXX Temp until set / list issue solved

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getVTabItemList')
    def getVTabItemList(self):
      transformation = self.aq_parent
      line_id = transformation.getVariationBaseCategoryLine()
      column_id = transformation.getVariationBaseCategoryColumn()
      base_category_list = transformation.getVariationBaseCategoryList()
      base_category = []
      for c in base_category_list:
        if not c in (line_id, column_id):
          if c in self.getVVariationBaseCategoryList():
            base_category += [transformation.getCategoryMembershipList(c, base=1)]
      if len(base_category) > 0:
        clist = cartesianProduct(base_category)
        result = []
        for c in clist:
          result += [(c,c)]
      else:
        result = [(None,'')]

      result.sort() # XXX Temp until set / list issue solved

      return result

    security.declareProtected( Permissions.ModifyPortalContent, 'newCell' )
    def newCell(self, *kw, **kwd):
      result = XMLMatrix.newCell(self, *kw, **kwd)
      result._setPredicateOperator("SUPERSET_OF")
      membership_list = []
      for c in kw:
        if c is not None:
          membership_list += [c]
      result._setPredicateValueList(membership_list)
      base_id = kwd.get('base_id', 'cell')
      if base_id == 'quantity':
        result._setDomainBaseCategoryList(self.getQVariationBaseCategoryList())
      elif base_id == 'variation':
        result._setDomainBaseCategoryList(self.getVVariationBaseCategoryList())

      return result

    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name="Set Mapped Value",id=id)
      return self.get(id)

    security.declarePrivate('_checkConsistency')
    def _checkConsistency(self, fixit=0):
      """
        Check the constitency of transformation elements
      """
      error_list = XMLMatrix._checkConsistency(self, fixit=fixit)

      # Quantity should be empty if no variation
      q_range = self.getCellRange(base_id = 'quantity')
      if q_range is not None:
        if q_range[0] == [None] and q_range[1] == [None]:
          matrix_is_not_empty = 0
          for k in self.getCellIds(base_id = 'quantity'):
            if hasattr(self, k):matrix_is_not_empty = 1
          if matrix_is_not_empty:
            if fixit:
              self.delCells(base_id = 'quantity')
              error_message =  "Variation cells for quantity should be empty (fixed)"
            else:
              error_message =  "Variation cells for quantity should be empty"
            error_list += [(self.getRelativeUrl(),
                          'TransformedResource inconsistency', 100, error_message)]

      # Quantity should be empty if no variation
      v_range = self.getCellRange(base_id = 'variation')
      if v_range is not None:
        if v_range[0] == [None] and v_range[1] == [None]:
          matrix_is_not_empty = 0
          for k in self.getCellIds(base_id = 'variation'):
            if hasattr(self, k):matrix_is_not_empty = 1
          if matrix_is_not_empty:
            if fixit:
              self.delCells(base_id = 'variation')
              error_message =  "Variation cells for variation should be empty (fixed)"
            else:
              error_message =  "Variation cells for variation should be empty"
            error_list += [(self.getRelativeUrl(),
                          'TransformedResource inconsistency', 100, error_message)]

      # First quantity
      # We build an attribute equality and look at all cells
      q_constraint = Constraint.AttributeEquality(
        domain_base_category_list = self.getQVariationBaseCategoryList(),
        predicate_operator = 'SUPERSET_OF',
        mapped_value_property_list = ['quantity'] )
      for k in self.getCellKeys(base_id = 'quantity'):
        kw={}
        kw['base_id'] = 'quantity'
        c = self.getCell(*k, **kw)
        if c is not None:
          predicate_value = []
          for p in k:
            if p is not None: predicate_value += [p]
          q_constraint.edit(predicate_value_list = predicate_value)
          if fixit:
            error_list += q_constraint.fixConsistency(c)
          else:
            error_list += q_constraint.checkConsistency(c)

      # Then variation
      # We build an attribute equality and look at all cells
      v_constraint = Constraint.AttributeEquality(
        domain_base_category_list = self.getVVariationBaseCategoryList(),
        predicate_operator = 'SUPERSET_OF',
        mapped_value_base_category_list = self.getVariationBaseCategoryList() )
      LOG("Before checkConsistency", 0, str(self.getVariationBaseCategoryList()))
      for k in self.getCellKeys(base_id = 'variation'):
        kw={}
        kw['base_id'] = 'variation'
        c = self.getCell(*k, **kw)
        if c is not None:
          predicate_value = []
          for p in k:
            if p is not None: predicate_value += [p]
          v_constraint.edit(predicate_value_list = predicate_value)
          if fixit:
            error_list += v_constraint.fixConsistency(c)
          else:
            error_list += v_constraint.checkConsistency(c)

      return error_list
