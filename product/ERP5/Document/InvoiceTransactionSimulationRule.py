# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.mixin.rule import RuleMixin
from Products.ERP5.mixin.movement_generator import MovementGeneratorMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin
from Products.ERP5.Document.PredicateMatrix import PredicateMatrix


class InvoiceTransactionSimulationRule(RuleMixin,
    MovementCollectionUpdaterMixin, PredicateMatrix):
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

  def _isProfitAndLossMovement(self, movement):
    # For a kind of trade rule, a profit and loss movement lacks source
    # or destination.
    return (movement.getSource() is None or movement.getDestination() is None)

class InvoiceTransactionRuleMovementGenerator(MovementGeneratorMixin):

  def _getUpdatePropertyDict(self, input_movement):
    # get the resource (in that order):
    #  * resource from the invoice (using deliveryValue)
    #  * price_currency from the invoice
    #  * price_currency from the parents simulation movement's
    # deliveryValue
    #  * price_currency from the top level simulation movement's
    # orderValue
    resource = input_movement.getPriceCurrency()
    portal = input_movement.getPortalObject()
    if resource is None:
      invoice_line = input_movement.getDeliveryValue()
      if invoice_line is None:
        resource = None
      else:
        invoice = invoice_line.getExplanationValue()
        resource = invoice.getProperty('resource',
                    invoice.getProperty('price_currency', None))
      if resource is None:
        # search the resource on parents simulation movement's deliveries
        simulation_movement = input_movement
        portal_simulation = portal.portal_simulation
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

    kw = {'delivery': None, 'resource': resource, 'price': 1}

    if resource is not None:
      #set asset_price on movement when resource is different from price
      #currency of the source/destination section
      for arrow in 'destination', 'source':
        section = input_movement.getDefaultAcquiredValue(arrow + '_section')
        if section is not None:
          try:
            currency_url = section.getPriceCurrency()
          except AttributeError:
            currency_url = None
          if currency_url not in (None, resource):
            currency = portal.unrestrictedTraverse(currency_url)
            exchange_ratio = currency.getPrice(
              context=input_movement.asContext(
                categories=('price_currency/' + currency_url,
                            'resource/' + resource)))
            if exchange_ratio is not None:
              kw[arrow + '_total_asset_price'] = round(
                exchange_ratio * input_movement.getQuantity(),
                currency.getQuantityPrecision())

    return kw

  def _getInputMovementList(self, movement_list=None, rounding=False):
    simulation_movement = self._applied_rule.getParentValue()
    quantity = simulation_movement.getCorrectedQuantity() * \
               simulation_movement.getPrice(0.0)
    return (simulation_movement.asContext(quantity=quantity),)
