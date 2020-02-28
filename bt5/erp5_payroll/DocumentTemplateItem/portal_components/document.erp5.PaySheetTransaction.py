# -*- coding: utf-8 -*-
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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.Invoice import Invoice

#XXX TODO: review naming of new methods

class PaySheetTransaction(Invoice):
  """
  A paysheet will store data about the salary of an employee
  """
  meta_type = 'ERP5 Pay Sheet Transaction'
  portal_type = 'Pay Sheet Transaction'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Delivery
                    , PropertySheet.Movement
                    , PropertySheet.Amount
                    , PropertySheet.XMLObject
                    , PropertySheet.TradeCondition
                    , PropertySheet.DefaultAnnotationLine
                    )


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRatioQuantityFromReference')
  def getRatioQuantityFromReference(self, ratio_reference=None):
    """
    return the ratio value correponding to the ratio_reference,
    None if ratio_reference not found
    """
    # get ratio lines
    portal_type_list = ['Pay Sheet Model Ratio Line']
    object_ratio_list = self.contentValues(portal_type=portal_type_list)
    # look for ratio lines on the paysheet
    if object_ratio_list:
      for obj in object_ratio_list:
        if obj.getReference() == ratio_reference:
          return obj.getQuantity()
    # if not find in the paysheet, look on dependence tree
    sub_object_list = self.getInheritedObjectValueList(portal_type_list)
    object_ratio_list = sub_object_list
    for document in object_ratio_list:
      if document.getReference() == ratio_reference:
        return document.getQuantity()
    return None

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRatioQuantityList')
  def getRatioQuantityList(self, ratio_reference_list):
    """
    Return a list of reference_ratio_list correponding values.
    reference_ratio_list is a list of references to the ratio lines
    we want to get.
    """
    if not isinstance(ratio_reference_list, (list, tuple)):
      return [self.getRatioQuantityFromReference(ratio_reference_list)]
    return [self.getRatioQuantityFromReference(reference) \
        for reference in ratio_reference_list]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAnnotationLineFromReference')
  def getAnnotationLineFromReference(self, reference=None):
    """Return the annotation line corresponding to the reference.
    Returns None if reference not found
    """
    # look for annotation lines on the paysheet
    annotation_line_list = self.contentValues(portal_type=['Annotation Line'])
    if annotation_line_list:
      for annotation_line in annotation_line_list:
        if (annotation_line.getReference() or annotation_line.getId()) == reference :
          return annotation_line
    # if not find in the paysheet, look on dependence tree
    for annotation_line in self.getInheritedObjectValueList(['Annotation Line']):
      if (annotation_line.getReference() or annotation_line.getId()) == reference:
        return annotation_line
    return None

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAnnotationLineListList')
  def getAnnotationLineListList(self, reference_list):
    """Return a list of annotation lines corresponding to the reference_list
    reference_list is a list of references to the Annotation Line we want
    to get.
    """
    if not isinstance(reference_list, (list, tuple)):
      return [self.getAnnotationLineFromReference(reference_list)]
    return [self.getAnnotationLineFromReference(reference) \
        for reference in reference_list]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInheritedObjectValueList')
  def getInheritedObjectValueList(self, portal_type_list, property_list=()):
    '''Return a list of all subobjects of the herited model (incuding the
      dependencies).
      If property_list is provided, only subobjects with at least one of those
      properties will be taken into account
    '''
    model = self.getSpecialiseValue()
    sub_object_list = []
    if model is not None:
      # if there is an effective model
      model_reference_dict = model.getInheritanceReferenceDict(self,
                                     portal_type_list=portal_type_list,
                                     property_list=property_list)
      traverse = self.getPortalObject().unrestrictedTraverse
      for model_url, id_list in model_reference_dict.items():
        model = traverse(model_url)
        sub_object_list.extend([model._getOb(x) for x in id_list])
    return sub_object_list

  security.declarePrivate('updateAggregatedAmountList')
  def updateAggregatedAmountList(self, *args, **kw):
    amount_dict = {(x.getReference(),
                    tuple(x.getVariationCategoryList())): x
                   for x in self.getAggregatedAmountList(*args, **kw)
                   if x.getResource()}
    movement_to_delete_list = []
    for movement in self.getMovementList():
      if movement.getBaseApplication():
        amount = amount_dict.pop((movement.getReference(),
                                  tuple(movement.getVariationCategoryList())),
                                 None)
        if amount is None:
          movement_to_delete_list.append(movement)
        else:
          movement.edit(**{x: amount.getProperty(x)
              for x in ('price', 'resource', 'quantity',
                        'base_application_list', 'base_contribution_list')})

    return {'movement_to_delete_list': movement_to_delete_list,
            'movement_to_add_list': amount_dict.values()}

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applyTransformation')
  def applyTransformation(self):
    '''use a delivery builder to create all the paysheet lines using
      movements return by updateAggregatedAmountList
    '''
    portal = self.getPortalObject()
    paysheet_model = self.getSpecialiseValue()
    movement_dict = self.updateAggregatedAmountList()
    for movement in movement_dict['movement_to_delete_list']:
      parent = movement.getParentValue()
      if parent.getPortalType() in ['Pay Sheet Line', 'Pay Sheet Transaction']:
        parent.manage_delObjects(movement.getId())
      if parent.getPortalType() == 'Pay Sheet Line' and \
             len(parent.contentValues(portal_type='Pay Sheet Cell')) == 0:
        # the line contain no movements, remove it
        self.manage_delObjects(parent.getId())
    business_process_list = paysheet_model.findEffectiveSpecialiseValueList(
        self, portal_type_list=['Business Process'])
    if len(business_process_list):
      # XXX currently, we consider that is to complicated to use more than one
      # Business Process, so we take the first (wich is the nearest from
      # the paysheet)
      business_process = business_process_list[0]
      movement_list_trade_phase_dic = {}
      for movement in movement_dict['movement_to_add_list']:
        if movement.getTotalPrice() not in (0, None):
          # remove movement with 0 total_price
          trade_phase = movement.getTradePhase()
          if not movement_list_trade_phase_dic.has_key(trade_phase):
            movement_list_trade_phase_dic[trade_phase] = []
          movement_list_trade_phase_dic[trade_phase].append(movement)
      for trade_phase in movement_list_trade_phase_dic.keys():
        business_link_list = business_process.getBusinessLinkValueList(trade_phase=\
            trade_phase)
        # convert Amount into Simulation Movement with Business Link
        movement_list = []
        for amount in movement_list_trade_phase_dic[trade_phase]:
          variation_dict = dict(x.split('/', 1)
                                for x in amount.getVariationCategoryList())
          movement_list.extend(
            business_process.getTradePhaseMovementList(
              self, amount, trade_phase, update_property_dict=variation_dict))
        for business_link in business_link_list:
          builder_list = [portal.restrictedTraverse(url) for url in\
                          business_link.getDeliveryBuilderList()]
          for builder in builder_list:
            builder.build(delivery_relative_url_list=[self.getRelativeUrl(),],
                          movement_list = movement_list)
