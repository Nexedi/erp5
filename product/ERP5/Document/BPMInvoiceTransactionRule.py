# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
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
from Products.ERP5.Document.BPMRule import BPMRule
from Products.ERP5.Document.PredicateMatrix import PredicateMatrix

class BPMInvoiceTransactionRule(BPMRule, PredicateMatrix):
  """
    DISCLAIMER: Refer to BPMRule docstring disclaimer.

    This is BPM enabled Invoice Transaction Rule.
  """

  # CMF Type Definition
  meta_type = 'ERP5 BPM Invoice Transaction Rule'
  portal_type = 'BPM Invoice Transaction Rule'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.AppliedRule
                    )

#### Helper method for expand
  def _generatePrevisionList(self, applied_rule, **kw):
    """
    Generate a list of movements, that should be children of this rule,
    based on its context (parent movement, delivery, configuration ...)

    These previsions are actually returned as dictionaries.
    """
    prevision_list = []
    context_movement = applied_rule.getParentValue()

    business_process = applied_rule.getBusinessProcessValue()

    movement_and_path_list = []
    for business_path in business_process.getPathValueList(
                        self.getProperty('trade_phase_list'),
                        context_movement):
      movement_and_path_list.append((context_movement, business_path))

    if len(movement_and_path_list) > 1:
      raise NotImplementedError

    # Find a matching cell
    cell = self._getMatchingCell(context_movement)

    if cell is not None : # else, we do nothing
      for accounting_rule_cell_line in cell.objectValues() :
        # get the resource (in that order):
        #  * resource from the invoice (using deliveryValue)
        #  * price_currency from the invoice
        #  * price_currency from the parents simulation movement's
        # deliveryValue
        #  * price_currency from the top level simulation movement's
        # orderValue
        resource = None
        invoice_line = context_movement.getDeliveryValue()
        if invoice_line is not None :
          invoice = invoice_line.getExplanationValue()
          resource = invoice.getProperty('resource',
                     invoice.getProperty('price_currency', None))
        if resource is None :
          # search the resource on parents simulation movement's deliveries
          simulation_movement = applied_rule.getParentValue()
          portal_simulation = self.getPortalObject().portal_simulation
          while resource is None and \
                      simulation_movement != portal_simulation :
            delivery = simulation_movement.getDeliveryValue()
            if delivery is not None:
              resource = delivery.getProperty('price_currency', None)
            if (resource is None) and \
               (simulation_movement.getParentValue().getParentValue() \
                                      == portal_simulation) :
              # we are on the first simulation movement, we'll try
              # to get the resource from it's order price currency.
              order = simulation_movement.getOrderValue()
              if order is not None:
                resource = order.getProperty('price_currency', None)
            simulation_movement = simulation_movement\
                                        .getParentValue().getParentValue()
        if resource is None :
          # last resort : get the resource from the rule
          resource = accounting_rule_cell_line.getResource() \
              or cell.getResource()
        # XXX Harcoded list
        prevision_line = {
            'source': accounting_rule_cell_line.getSource(),
            'source_section': context_movement.getSourceSection(),
            'source_decision': context_movement.getSourceDecision(),
            'source_administration': context_movement \
                .getSourceAdministration(),
            'source_project': context_movement.getSourceProject(),
            'source_function': context_movement.getSourceFunction(),
            'source_payment': context_movement.getSourcePayment(),
            'destination': accounting_rule_cell_line.getDestination(),
            'destination_section': context_movement.getDestinationSection(),
            'destination_decision': context_movement.getDestinationDecision(),
            'destination_administration': context_movement \
                .getDestinationAdministration(),
            'destination_project': context_movement.getDestinationProject(),
            'destination_function': context_movement.getDestinationFunction(),
            'destination_payment': context_movement.getDestinationPayment(),
            'start_date': context_movement.getStartDate(),
            'stop_date': context_movement.getStopDate(),
            'resource': resource,
            'quantity': (context_movement.getCorrectedQuantity() *
              context_movement.getPrice(0.0)) *
              accounting_rule_cell_line.getQuantity(),
            'price': 1,
            'force_update': 1,
            'causality_value': business_path,
            }

        if accounting_rule_cell_line.hasProperty(
            'generate_prevision_script_id'):
          generate_prevision_script_id = \
                accounting_rule_cell_line.getGeneratePrevisionScriptId()
          prevision_line.update(getattr(context_movement,
                              generate_prevision_script_id)(prevision_line))
        prevision_list.append(prevision_line)
    return prevision_list

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, force=0, **kw):
    """
    Expands the rule:
    - generate a list of previsions
    - compare the prevision with existing children
      - get the list of existing movements (immutable, mutable, deletable)
      - compute the difference between prevision and existing (add,
        modify, remove)
    - add/modify/remove child movements to match prevision
    """
    add_list, modify_dict, \
        delete_list = self._getCompensatedMovementList(applied_rule,
        matching_property_list=['resource', 'source',
               'destination','destination_total_asset_price',
              'source_total_asset_price'],**kw)

    if len(add_list) or len(modify_dict):
      pass#import pdb; pdb.set_trace()

    for movement_id in delete_list:
      applied_rule._delObject(movement_id)

    for movement, prop_dict in modify_dict.items():
      applied_rule[movement].edit(**prop_dict)

    for movement_dict in add_list:
      if 'id' in movement_dict.keys():
        mvmt_id = applied_rule._get_id(movement_dict.pop('id'))
        new_mvmt = applied_rule.newContent(id=mvmt_id,
            portal_type=self.movement_type)
      else:
        new_mvmt = applied_rule.newContent(portal_type=self.movement_type)
      new_mvmt.edit(**movement_dict)
      #set asset_price on movement when resource is different from price
      #currency of the source/destination section
      currency = new_mvmt.getResourceValue()
      if currency is not None:
        currency_url = currency.getRelativeUrl()
        dest_section = new_mvmt.getDestinationSectionValue()
        if dest_section is not None:
          dest_currency_url = dest_section.getProperty('price_currency', None)
        else:
          dest_currency_url = None
        if dest_currency_url is not None \
            and currency_url != dest_currency_url:
          precision = dest_section.getPriceCurrencyValue() \
              .getQuantityPrecision()
          dest_exchange_ratio = currency.getPrice(context=new_mvmt.asContext(
            categories=['price_currency/%s' % dest_currency_url,
                        'resource/%s' % currency_url],
            start_date=new_mvmt.getStartDate()))
          if dest_exchange_ratio is not None:
            new_mvmt.edit(destination_total_asset_price=round(
             (dest_exchange_ratio*
              applied_rule.getParentValue().getTotalPrice()),precision))

        source_section = new_mvmt.getSourceSectionValue()
        if source_section is not None:
          source_currency_url = source_section.getProperty(
              'price_currency', None)
        else:
          source_currency_url = None
        if source_currency_url is not None \
            and currency_url != source_currency_url:
          precision = source_section.getPriceCurrencyValue() \
              .getQuantityPrecision()
          source_exchange_ratio = currency.getPrice(context=new_mvmt\
              .asContext(
            categories=['price_currency/%s' % source_currency_url,
                        'resource/%s' % currency_url],
            start_date=new_mvmt.getStartDate()))
          if source_exchange_ratio is not None:
            new_mvmt.setSourceTotalAssetPrice(round(
       source_exchange_ratio*applied_rule.getParentValue().getTotalPrice(),
            precision))

    # Pass to base class
    BPMRule.expand(self, applied_rule, force=force, **kw)

  # Matrix related
  security.declareProtected( Permissions.ModifyPortalContent,
                              'newCellContent' )
  def newCellContent(self, id, portal_type='Accounting Rule Cell', **kw):
    """
      Creates a new Cell.
    """
    self.invokeFactory(type_name=portal_type, id=id)
    new_cell = self.get(id)
    return new_cell

  # Deliverability / orderability
  def isOrderable(self, m):
    return 1

  def isDeliverable(self, m):
    if m.getSimulationState() in self.getPortalDraftOrderStateList():
      return 0
    return 1
