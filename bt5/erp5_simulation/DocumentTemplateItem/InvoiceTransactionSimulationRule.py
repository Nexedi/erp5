# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
"""
XXX This file is experimental for new simulation implementation, and
will replace InvoicingRule.
"""

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.mixin.rule import RuleMixin, MovementGeneratorMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin
from Products.ERP5.Document.PredicateMatrix import PredicateMatrix


class InvoiceTransactionSimulationRule(RuleMixin, MovementCollectionUpdaterMixin, Predicate, PredicateMatrix):
  """
  Invoice Transaction Rule object generates accounting movements for
  each invoice movement based on category membership and other
  predicated. Template accounting movements are stored in cells inside
  an instance of the InvoiceTransactionRule.
  """
  # CMF Type Definition
  meta_type = 'ERP5 Invoice Transaction Simulation Rule'
  portal_type = 'Invoice Transaction Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IRule,
                            interfaces.IDivergenceController,
                            interfaces.IMovementCollectionUpdater,)

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Task,
    PropertySheet.Predicate,
    PropertySheet.Reference,
    PropertySheet.Version,
    PropertySheet.Rule
    )

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return InvoiceTransactionRuleMovementGenerator(applied_rule=context, rule=self)

  def _getMovementGeneratorContext(self, context):
    """
    Return the movement generator context to use for expand
    """
    return context

  def _getMovementGeneratorMovementList(self, context):
    """
    Return the movement lists to provide to the movement generator
    """
    return []

  def _isProfitAndLossMovement(self, movement):
    # For a kind of trade rule, a profit and loss movement lacks source
    # or destination.
    return (movement.getSource() is None or movement.getDestination() is None)

class InvoiceTransactionRuleMovementGenerator(MovementGeneratorMixin):
  def getGeneratedMovementList(self, movement_list=None, rounding=False):
    """
    Input movement list comes from order

    XXX This implementation is very primitive, and does not support BPM,
    i.e. business paths are not taken into account.
    """
    ret = []

    rule = self._rule
    # input_movement, business_path = rule._getInputMovementAndPathTupleList(
    #   applied_rule)[0]
    input_movement = self._applied_rule.getParentValue()
    parent_movement = self._applied_rule.getParentValue()

    # Find a matching cell
    cell = rule._getMatchingCell(input_movement)

    if cell is not None:
      for accounting_rule_cell_line in cell.objectValues():
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
          simulation_movement = parent_movement
          portal_simulation = self._applied_rule.getPortalObject().portal_simulation
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
        # XXX we need business path here?
        kw = self._getPropertyAndCategoryList(input_movement, None, rule)

        kw.update(
          delivery=None,
          source=[accounting_rule_cell_line.getSource()],
          destination=[accounting_rule_cell_line.getDestination()],
          quantity=(input_movement.getCorrectedQuantity() *
            input_movement.getPrice(0.0)) *
            accounting_rule_cell_line.getQuantity(),
          resource=[resource],
          price=1,
        )
        if resource is not None:
          #set asset_price on movement when resource is different from price
          #currency of the source/destination section
          destination_exchange_ratio, precision = self \
              ._getCurrencyRatioAndPrecisionByArrow(
              rule, 'destination_section', kw)
          if destination_exchange_ratio is not None:
            kw.update(destination_total_asset_price=round(
             (destination_exchange_ratio*
              parent_movement.getTotalPrice()),precision))

          source_exchange_ratio, precision = self \
              ._getCurrencyRatioAndPrecisionByArrow(
              rule, 'source_section', kw)
          if source_exchange_ratio is not None:
            kw.update(source_total_asset_price=round(
             (source_exchange_ratio*
              parent_movement.getTotalPrice()),precision))

        if accounting_rule_cell_line.hasProperty(
            'generate_prevision_script_id'):
          generate_prevision_script_id = \
                accounting_rule_cell_line.getGeneratePrevisionScriptId()
          kw.update(getattr(input_movement,
                            generate_prevision_script_id)(kw))
        simulation_movement = self._applied_rule.newContent(
          portal_type=RuleMixin.movement_type,
          temp_object=True,
          **kw)
        ret.append(simulation_movement)
    return ret

  def _getCurrencyRatioAndPrecisionByArrow(self, rule, arrow, prevision_line):
    from Products.ERP5Type.Document import newTempSimulationMovement
    try:
      prevision_currency = prevision_line['resource'][0]
    except IndexError:
      prevision_currency = None
    exchange_ratio = None
    precision = None
    try:
      section = prevision_line.get(arrow, [])[0]
    except IndexError:
      section = None
    if section is not None:
      currency_url = rule.restrictedTraverse(section).getProperty(
          'price_currency', None)
    else:
      currency_url = None
    if currency_url is not None and prevision_currency != currency_url:
      precision = section.getPriceCurrencyValue() \
          .getQuantityPrecision()
      temporary_movement = newTempSimulationMovement(rule.getPortalObject(),
          '1', **prevision_line)
      exchange_ratio = rule.restrictedTraverse(currency_url).getPrice(
          context=temporary_movement.asContext(
        categories=['price_currency/%s' % currency_url,
                    'resource/%s' % prevision_currency],
        start_date=temporary_movement.getStartDate()))
    return exchange_ratio, precision
