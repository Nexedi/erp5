# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
#                    Fabien Morin <fabien@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Transformation import Transformation
from Products.ERP5.Document.Path import Path
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
from Products.ERP5Type.XMLMatrix import XMLMatrix

import zope.interface

# XXX TODO : getTradeModelLineComposedList and findSpecialiseValueList should
# probably move to Transformation (better names should be used)
# XXX TODO: review naming of new methods
# XXX WARNING: current API naming may change although model should be stable.

class CircularException(Exception): pass

class TradeCondition(Path, Transformation, XMLMatrix):
    """
      Trade Conditions are used to store the conditions (payment, logistic,...)
      which should be applied (and used in the orders) when two companies make
      business together
    """
    edited_property_list = ['price', 'resource', 'quantity',
        'reference', 'base_application_list', 'base_contribution_list']

    meta_type = 'ERP5 Trade Condition'
    portal_type = 'Trade Condition'
    model_line_portal_type_list = ('Trade Model Line',)
    isPredicate = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Folder
                      , PropertySheet.Comment
                      , PropertySheet.Arrow
                      , PropertySheet.TradeCondition
                      , PropertySheet.Order
                      )

    zope.interface.implements(interfaces.ITransformation)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'updateAggregatedAmountList')
    def updateAggregatedAmountList(self, context, movement_list=None, rounding=None, **kw):
      existing_movement_list = context.getMovementList()
      aggregated_amount_list = self.getAggregatedAmountList(context=context,
          movement_list=movement_list, **kw)
      modified_reference_list = []
      normal_use_list = self.getPortalObject().portal_preferences\
              .getPreferredNormalResourceUseCategoryList()
      # check if the existing movements are in aggregated movements
      movement_to_delete_list = []
      movement_to_add_list = []
      for movement in existing_movement_list:
        keep_movement = False
        # check if the movement is a generated one or entered by the user.
        # If it has been entered by user, keep it.
        resource = movement.getResourceValue()
        if resource is not None and \
            len(set(normal_use_list).intersection(set(resource\
            .getUseList()))):
          keep_movement = True
          break
        for amount in aggregated_amount_list:
          # if movement is generated and if not exist, append to delete list
          update_kw = {}
          for p in self.edited_property_list:
            update_kw[p] = amount.getProperty(p)
          if movement.getProperty('reference') == update_kw['reference'] and\
              movement.getVariationCategoryList() == \
              amount.getVariationCategoryList():
            movement.edit(**update_kw)
            modified_reference_list.append(update_kw['reference'])
            keep_movement = True
        if not keep_movement:
          movement_to_delete_list.append(movement)
      movement_to_add_list = [amount for amount in aggregated_amount_list if
          amount.getReference() not in modified_reference_list]
      return {'movement_to_delete_list' : movement_to_delete_list,
              'movement_to_add_list': movement_to_add_list}

    security.declareProtected(Permissions.AccessContentsInformation,
        'findSpecialiseValueList')
    def findSpecialiseValueList(self, context, portal_type_list=None):
      """Returns a list of specialised objects representing inheritance tree.

         Uses Breadth First Search.
      """
      if portal_type_list is None:
        portal_type_list = [self.getPortalType()]
      if context.getPortalType() in portal_type_list:
        specialise_value_list = [context]
        visited_trade_condition_list = [context]
      else:
        specialise_value_list = context.getSpecialiseValueList(\
            portal_type=portal_type_list)
        visited_trade_condition_list = context.getSpecialiseValueList(\
            portal_type=portal_type_list)
      while len(specialise_value_list) != 0:
        specialise = specialise_value_list.pop(0)
        children = specialise.getSpecialiseValueList(\
            portal_type=portal_type_list)
        specialise_value_list.extend(children)
        if not set(children).intersection(visited_trade_condition_list):
          visited_trade_condition_list.extend(children)
        else:
          raise CircularException
      return visited_trade_condition_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTradeModelLineComposedList')
    def getTradeModelLineComposedList(self, context=None, portal_type_list=None):
      """Returns list of Trade Model Lines using composition.

      Reference of Trade Model Line is used to hide other Trade Model Line
      In chain first found Trade Model Line has precedence
      Context's, if not None, Trade Model Lines have precedence
      Result is sorted in safe order to do one time pass - movements which
      applies are before its possible contributions.
      """
      if portal_type_list is None:
        portal_type_list = self.model_line_portal_type_list

      reference_list = []
      trade_model_line_composed_list = []
      containting_object_list = []
      start_date = None
      stop_date = None
      if context is not None:
        document = context
        if getattr(context, 'getExplanationValue', None) is not None:
          # if context is movement it is needed to ask its explanation
          # for contained Trade Model Lines
          document = context.getExplanationValue()
        containting_object_list.append(document)
        start_date = document.getStartDate()
        stop_date = document.getStartDate()
      containting_object_list.extend(\
          self.findEffectiveSpecialiseValueList(context=self,
            start_date=start_date, stop_date=stop_date))

      for specialise in containting_object_list:
        for trade_model_line in specialise.contentValues(
            portal_type=portal_type_list):
          reference = trade_model_line.getReference()
          if reference not in reference_list or reference is None:
            reference_list.append(reference)
            base_contribution_list = trade_model_line \
              .getBaseContributionList()
            if len(base_contribution_list) == 0:
              # when movement will not generate anything which contributes
              # it is safe to be last on list
              trade_model_line_composed_list.append(trade_model_line)
            else:
              # if movements contributes to anything it have to be placed
              # just before to what it contributes
              index = 0
              inserted = False
              for old_trade_model_line in trade_model_line_composed_list:
                for base_application in old_trade_model_line \
                  .getBaseApplicationList():
                  if base_application in base_contribution_list:
                    trade_model_line_composed_list.insert(index,
                        trade_model_line)
                    inserted = True
                    break
                if inserted:
                  break
                index += 1
              if not inserted:
                # last resort - nothing was found, it is safe to put movement
                # in beginning of list
                trade_model_line_composed_list.insert(0, trade_model_line)

      return trade_model_line_composed_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAggregatedAmountList')
    def getAggregatedAmountList(self, context, movement_list=None, **kw):
      if movement_list is None:
        movement_list = []
      result = AggregatedAmountList()

      trade_model_line_composed_list = \
          self.getTradeModelLineComposedList(context)

      # initialise run then rerun only once, as trade_model_line_composed_list
      # is sorted in good way to have simple algorithm
      for pass_type in ['initialise', 'rerun']:
        for model_line in trade_model_line_composed_list:
          result.extend(model_line.getAggregatedAmountList(context,
            movement_list=movement_list,
            current_aggregated_amount_list=result,
            **kw))
        movement_list = result # apply model again on generated movements

      # remove movement that should not be created
      movement_list = []
      for movement in result:
        movement_ref = movement.getReference()
        for model_line in trade_model_line_composed_list:
          if model_line.getReference() == movement_ref and\
              model_line.isCreateLine():
            movement_list.append(movement)
      return movement_list

    security.declareProtected( Permissions.AccessContentsInformation, 'getCell')
    def getCell(self, *kw , **kwd):
      '''Overload the function getCell to be able to search a cell on the
      inheritance model tree if the cell is not found on current one.
      '''
      cell = XMLMatrix.getCell(self, *kw, **kwd)
      if cell is None:
        # if cell not found, look on the inherited models
        start_date = kwd.has_key('paysheet') and \
            kwd['paysheet'].getStartDate() or None
        stop_date = kwd.has_key('paysheet') and \
            kwd['paysheet'].getStopDate() or None
        model_list = self.findEffectiveSpecialiseValueList(\
            context=self, start_date=start_date, stop_date=stop_date)
        for specialised_model in model_list:
          cell = XMLMatrix.getCell(specialised_model, *kw, **kwd)
          if cell is not None:
            return cell
      return cell

    security.declareProtected(Permissions.AccessContentsInformation,
        'getReferenceDict')
    def getReferenceDict(self, portal_type_list, property_list=None):
      '''Return a dict containing all id's of the objects contained in
      this model and corresponding to the given portal_type. The key of the dict
      are the reference (or id if no reference)
      '''
      if property_list is None:
        property_list=[]
      reference_dict = {}
      object_list = self.contentValues(portal_type=portal_type_list,
          sort_on='id')
      for obj in object_list:
        keep = (len(property_list) == 0)
        for property_ in property_list:
          if obj.hasProperty(property_):
            keep = 1
            break
        if keep:
          reference_dict[obj.getProperty('reference', obj.getId())] = obj.getId()
      return reference_dict

    security.declareProtected(Permissions.AccessContentsInformation,
        'findEffectiveSpecialiseValueList')
    def findEffectiveSpecialiseValueList(self, context, start_date=None,
        stop_date=None, portal_type_list=None, effecive_model_list=None):
      '''Returns a list of effective specialised objects representing
      inheritance tree.
      An effective object is an object which start and stop_date are equal (or
      included) to the range of the given start and stop_date.
      If no start date and stop date are provided, findSpecialiseValueList is
      returned
      '''
      if start_date is None and stop_date is None:
        # if dates are not defined, return the specalise_value_list
        return self.findSpecialiseValueList(context=context)
      if effecive_model_list is None:
        effecive_model_list=[]
      if portal_type_list is None:
        portal_type_list = [self.getPortalType()]

      new_model = self.getEffectiveModel(start_date, stop_date)
      model_list = new_model.getSpecialiseValueList(portal_type=\
          portal_type_list)
      effecive_model_list.append(new_model)
      for model in model_list:
        model.findEffectiveSpecialiseValueList(context=context,
            start_date=start_date, stop_date=stop_date,
            portal_type_list=portal_type_list,
            effecive_model_list=effecive_model_list)
      return effecive_model_list

    security.declareProtected(Permissions.AccessContentsInformation,
        'getInheritanceReferenceDict')
    def getInheritanceReferenceDict(self, portal_type_list,
        property_list=None):
      '''Returns a dict with the model url as key and a list of reference as
      value. A Reference can appear only one time in the final output.
      If property_list is not empty, documents which don't have any of theses
      properties will be skipped.
      '''
      if property_list is None:
        property_list=[]
      model_list = self.findSpecialiseValueList(context=self)
      reference_list = []
      model_reference_dict = {}
      for model in model_list:
        id_list = []
        model_reference_list = model.getReferenceDict(
                             portal_type_list, property_list=property_list)
        for reference in model_reference_list.keys():
          if reference not in reference_list:
            reference_list.append(reference)
            id_list.append(model_reference_list[reference])
        if len(id_list) != 0:
          model_reference_dict[model.getRelativeUrl()]=id_list
      return model_reference_dict

    security.declareProtected(Permissions.AccessContentsInformation,
        'getEffectiveModel')
    def getEffectiveModel(self, start_date=None, stop_date=None):
      '''Return the more appropriate model using effective_date, expiration_date
      and version number.
      An effective model is a model which start and stop_date are equal (or
      excluded) to the range of the given start and stop_date and with the
      higher version number (if there is more than one)
      '''
      reference = self.getReference()
      if not reference:
        return self
      effective_model_list = []
      model_object_list = [result.getObject() for result in \
          self.portal_catalog(portal_type=self.portal_type,
                              reference=reference,
                              sort_on=(('version','descending'),))]

      # if there is model which has effective period containing
      # the start_date and the stop date of the paysheet, return it
      for current_model in model_object_list:
        if current_model.getEffectiveDate() <= start_date and \
            current_model.getExpirationDate() >= stop_date:
          effective_model_list.append(current_model)
      if len(effective_model_list):
        return effective_model_list[0]
      # if no effective model are found (ex. because dates are None), return self
      return self

    security.declareProtected(Permissions.AccessContentsInformation,
        'getModelIneritanceEffectiveProperty')
    def getModelIneritanceEffectiveProperty(self, paysheet, property_name):
      """Get a property from an effective model
      """
      v = self.getProperty(property_name)
      if v:
        return v
      model_list = self.findEffectiveSpecialiseValueList(context=self,
          start_date=paysheet.getStartDate(), stop_date=paysheet.getStopDate())
      for specialised_model in model_list:
        v = specialised_model.getProperty(property_name)
        if v:
          return v
