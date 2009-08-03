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

  def _getCurrencyRatioByArrow(self, arrow, prevision_line):
    from Products.ERP5Type.Document import newTempSimulationMovement
    temporary_movement = newTempSimulationMovement(self.getPortalObject(),
        '1', **prevision_line)
    exchange_ratio = None
    try:
      section = prevision_line['%s_list' % arrow][0]
    except IndexError:
      section = None
    if section is not None:
      currency_url = self.restrictedTraverse(section).getProperty(
          'price_currency', None)
    else:
      currency_url = None
    if currency_url is not None and self.getResource() != currency_url:
      precision = section.getPriceCurrencyValue() \
          .getQuantityPrecision()
      exchange_ratio = currency.getPrice(
          context=temporary_movement.asContext(
        categories=['price_currency/%s' % currency_url,
                    'resource/%s' % self.getResource()],
        start_date=temporary_movement.getStartDate()))
    return exchange_ratio

#### Helper method for expand
  def _generatePrevisionList(self, applied_rule, **kw):
    """
    Generate a list of movements, that should be children of this rule,
    based on its context (parent movement, delivery, configuration ...)

    These previsions are actually returned as dictionaries.
    """
    prevision_list = []
    input_movement = applied_rule.getParentValue()

    business_process = applied_rule.getBusinessProcessValue()

    movement_and_path_list = []
    for business_path in business_process.getPathValueList(
                        self.getProperty('trade_phase_list'),
                        input_movement):
      movement_and_path_list.append((input_movement, business_path))

    if len(movement_and_path_list) > 1:
      raise NotImplementedError

    # Find a matching cell
    cell = self._getMatchingCell(input_movement)

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
        invoice_line = input_movement.getDeliveryValue()
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
        prevision_line = {}
        prevision_line.update(**self._getExpandablePropertyDict(applied_rule,
          input_movement, business_path))

        prevision_line.update(
          source_list = [accounting_rule_cell_line.getSource()],
          destination_list = [accounting_rule_cell_line.getDestination()],
          quantity = (input_movement.getCorrectedQuantity() *
            input_movement.getPrice(0.0)) *
            accounting_rule_cell_line.getQuantity(),
          resource_list = [resource],
          price = 1,
        )
        if resource is not None:
          #set asset_price on movement when resource is different from price
          #currency of the source/destination section
          destination_exchange_ratio = self._getCurrencyRatioByArrow(
              'destination_section', prevision_line)
          if destination_exchange_ratio is not None:
            prevision_line.update(destination_total_asset_price=round(
             (destination_exchange_ratio*
              applied_rule.getParentValue().getTotalPrice()),precision))

          source_exchange_ratio = self._getCurrencyRatioByArrow(
              'source_section', prevision_line)
          if source_exchange_ratio is not None:
            prevision_line.update(source_total_asset_price=round(
             (source_exchange_ratio*
              applied_rule.getParentValue().getTotalPrice()),precision))

        if accounting_rule_cell_line.hasProperty(
            'generate_prevision_script_id'):
          generate_prevision_script_id = \
                accounting_rule_cell_line.getGeneratePrevisionScriptId()
          prevision_line.update(getattr(input_movement,
                              generate_prevision_script_id)(prevision_line))
        prevision_list.append(prevision_line)
    return prevision_list

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
