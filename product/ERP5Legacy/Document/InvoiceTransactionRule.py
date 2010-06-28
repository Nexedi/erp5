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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Legacy.Document.Rule import Rule
from Products.ERP5.Document.PredicateMatrix import PredicateMatrix

from zLOG import LOG, BLATHER, INFO, PROBLEM, WARNING

class InvoiceTransactionRule(Rule, PredicateMatrix):
  """
    Invoice Transaction Rule object generates accounting movements
    for each invoice movement based on category membership and
    other predicated. Template accounting movements are stored
    in cells inside an instance of the InvoiceTransactionRule.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Invoice Transaction Rule'
  portal_type = 'Invoice Transaction Rule'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

#### Helper method for expand
  def _generatePrevisionList(self, applied_rule, **kw):
    """
    Generate a list of movements, that should be children of this rule,
    based on its context (parent movement, delivery, configuration ...)

    These previsions are actually returned as dictionaries.
    """
    input_movement, business_path = self._getInputMovementAndPathTupleList(
        applied_rule)[0]
    prevision_list = []

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
            # 'order' category is deprecated. it is kept for compatibility.
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
          source = accounting_rule_cell_line.getSource(),
          destination = accounting_rule_cell_line.getDestination(),
          quantity = (input_movement.getCorrectedQuantity() *
            input_movement.getPrice(0.0)) *
            accounting_rule_cell_line.getQuantity(),
          resource = resource,
          price = 1,
        )
        if resource is not None:
          #set asset_price on movement when resource is different from price
          #currency of the source/destination section
          destination_exchange_ratio, precision = self \
              ._getCurrencyRatioAndPrecisionByArrow(
              'destination_section', prevision_line)
          if destination_exchange_ratio is not None:
            prevision_line.update(destination_total_asset_price=round(
             (destination_exchange_ratio*
              applied_rule.getParentValue().getTotalPrice()),precision))

          source_exchange_ratio, precision = self \
              ._getCurrencyRatioAndPrecisionByArrow(
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
    return Rule._expand(self, applied_rule, force=force, **kw)

  # Matrix related
  security.declareProtected( Permissions.ModifyPortalContent,
                              'newCellContent' )
  def newCellContent(self, id, portal_type='Accounting Rule Cell', **kw):
    """Overriden to specify default portal type
    """
    return self.newContent(id=id, portal_type=portal_type, **kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'solve')
  def solve(self, applied_rule, solution_list):
    """
      Solve inconsistency according to a certain number of solutions
      templates. This updates the

      -> new status -> solved

      This applies a solution to an applied rule. Once
      the solution is applied, the parent movement is checked.
      If it does not diverge, the rule is reexpanded. If not,
      diverge is called on the parent movement.
    """

  security.declareProtected(Permissions.ModifyPortalContent, 'diverge')
  def diverge(self, applied_rule):
    """
      -> new status -> diverged

      This basically sets the rule to "diverged"
      and blocks expansion process
    """

#   # Solvers
#   security.declareProtected(Permissions.View, 'isDivergent')
#   def isDivergent(self, applied_rule):
#     """
#       Returns 1 if divergent rule
#     """
#
#   security.declareProtected(Permissions.View, 'getDivergenceList')
#   def getDivergenceList(self, applied_rule):
#     """
#       Returns a list Divergence descriptors
#     """

  # Deliverability / orderability
  def isOrderable(self, m):
    return 1

  def isDeliverable(self, m):
    if m.getSimulationState() in self.getPortalDraftOrderStateList():
      return 0
    return 1

  def _getCurrencyRatioAndPrecisionByArrow(self, arrow, prevision_line):
    prevision_currency = prevision_line.get('resource', None)
    exchange_ratio = None
    precision = None
    section = prevision_line.get(arrow, None)
    if section is not None:
      section = self.restrictedTraverse(section)
      currency_url = section.getProperty('price_currency', None)
    else:
      currency_url = None
    if currency_url is not None and prevision_currency != currency_url:
      from Products.ERP5Type.Document import newTempSimulationMovement
      temporary_movement = newTempSimulationMovement(self.getPortalObject(),
                                                     '1', **prevision_line)
      precision = section.getPriceCurrencyValue() \
          .getQuantityPrecision()
      exchange_ratio = self.restrictedTraverse(currency_url).getPrice(
          context=temporary_movement.asContext(
        categories=['price_currency/%s' % currency_url,
                    'resource/%s' % prevision_currency],
        start_date=temporary_movement.getStartDate()))
    return exchange_ratio, precision

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getExpandablePropertyList')
  def getExpandablePropertyList(self, default=None):
    """
    Return a list of properties used in expand.
    """
    property_list = self._baseGetExpandablePropertyList()
    # For backward compatibility, we keep for some time the list
    # of hardcoded properties. Theses properties should now be
    # defined on the rule itself
    if len(property_list) == 0:
      LOG("Invoice Transaction Rule , getExpandablePropertyList", WARNING,
                 "Hardcoded properties set, please define your rule correctly")
      property_list = (
        'destination_administration',
        'destination_decision',
        'destination_function',
        'destination_payment',
        'destination_project',
        'destination_section',
        'source_administration',
        'source_decision',
        'source_function',
        'source_payment',
        'source_project',
        'source_section',
        'start_date',
        'stop_date',
      )
    return property_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMatchingPropertyList')
  def getMatchingPropertyList(self, default=None):
    """
    Return a list of properties used in expand.
    """
    property_list = self._baseGetMatchingPropertyList()
    # For backward compatibility, we keep for some time the list
    # of hardcoded properties. Theses properties should now be
    # defined on the rule itself
    if len(property_list) == 0:
      LOG("Invoice Transaction Rule , getMatchingPropertyList", WARNING,
          "Hardcoded properties set, please define your rule correctly")
      property_list=['resource', 'source', 'destination',
                     'destination_total_asset_price',
                     'source_total_asset_price']
    return property_list
