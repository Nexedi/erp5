##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Guillaume MICHON <guillaume@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.ERP5Globals import movement_type_list, order_movement_type_list, reserved_inventory_state_list, current_inventory_state_list, draft_order_state
from DateTime import DateTime
from copy import deepcopy
from string import lower

from zLOG import LOG

class AmortisationRule(Rule):
    """
      Amortisation Rule object plans an item amortisation
    """

    # CMF Type Definition
    meta_type = 'ERP5 Amortisation Rule'
    portal_type = 'Amortisation Rule'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      )

    # CMF Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
An ERP5 Rule..."""
         , 'icon'           : 'rule_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addAmortisationRule'
         , 'immediate_view' : 'rule_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ()
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'rule_view'
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
          , 'action'        : 'rule_print'
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

    def test(self, movement):
      """
        Tests if the rule (still) applies
      """
      # An order rule never applies since it is always explicitely instanciated
      # XXX And if it is an amortisation rule ?
      return 0
    

    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, force=0, **kw):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      delivery_line_type = 'Simulation Movement'
      
      # Get the item we come from
      my_item = applied_rule.getDefaultCausalityValue()
      
      # Only expand if my_item is not None
      if my_item is not None:
        
        ### First, plan the theorical accounting movements
        
        accounting_movement_list = []
        immobilisation_movement_list = my_item.getImmobilisationMovementList()
        LOG('AmortisationRule :', 0, 'immobilisation_movement_list = %s' % repr(immobilisation_movement_list))
        
        current_immo_movement = None
        for mvt_number in range(len(immobilisation_movement_list)):
          # Get processed immobilisation movements
          prev_immo_movement = current_immo_movement
          current_immo_movement = immobilisation_movement_list[mvt_number]
          if mvt_number < len(immobilisation_movement_list) - 1:
            next_immo_movement = immobilisation_movement_list[mvt_number + 1]
          else:
            next_immo_movement = None
            
          # Calculate the accounting movements
          accounting_movements = self._getAccountingMovement(current_immo_movement=current_immo_movement,
                                                            next_immo_movement=next_immo_movement,
                                                            previous_immo_movement=prev_immo_movement)
          
          accounting_movement_list.extend(accounting_movements)
          
      
      ### The next step is to create the simulation movements
      # First, we delete all of the simulation movements which are children
      # of the applied rule : the entire simulation for this item has been
      # re-calculated, so old values are necessary wrong
      # However, the simulation movements already used to make accounting
      # are not deleted.
      movement_id_list = []
      movement_last_id_list = {}
      for movement in applied_rule.contentValues():
        movement_id = movement.getId()
        movement_id_name = '_'.join( movement_id.split('_')[:-1] )
        movement_id_number = int(movement_id.split('_')[-1])
        if movement.getDeliveryValue() is None:
          movement_id_list.append(movement_id)
        else:
          if movement_last_id_list.get( movement_id_name, None) is None or movement_id_number > movement_last_id_list[movement_id_name]:
            movement_last_id_list[movement_id_name] = movement_id_number
          
            
      applied_rule.deleteContent(movement_id_list)
      ids = {}
      for accounting_movement in accounting_movement_list:
        if accounting_movement['quantity'] != 0:
          my_type = accounting_movement['type']
          if ids.get(my_type) is None:
            LOG('AmortisationRule :', 0, 'ids has no attribute %s' % repr(my_type))
            ids[my_type] = movement_last_id_list.get(my_type, None)
            if ids[my_type] is None:
              ids[my_type] = -1
            
          ids[my_type] = ids[my_type] + 1
          new_id = my_type + '_' + str(ids[my_type])
          LOG('AmortisationRule :', 0, 'ids[my_type] = %s after incrementing' % repr(ids[my_type]))
          
          LOG('AmortisationRule :', 0, 'creating simulation movement %s...' % repr(new_id))
          
          # Round date
          stop_date = accounting_movement['stop_date']
          if stop_date.latestTime() - stop_date < 1/24.:
            stop_date = stop_date + 1
          stop_date = DateTime('%s/%s/%s' % (repr(stop_date.year()), repr(stop_date.month()), repr(stop_date.day())))
          accounting_movement['stop_date'] = stop_date
          
          simulation_movement = applied_rule.newContent(portal_type=delivery_line_type, id=new_id )
          simulation_movement.setStartDate(stop_date)
          simulation_movement.setTargetStartDate(stop_date)
          simulation_movement.setTargetStopDate(stop_date)
          for (key, value) in accounting_movement.items():
            if key != 'type' and value != None:
              setter_name = 'set'
              tokens = key.split('_')
              for i in range(len(tokens)):
                setter_name += tokens[i].capitalize()
              setter = getattr(simulation_movement, setter_name)
              setter(value)
          
      
              
      
    security.declareProtected(Permissions.View, '_getAccountingMovement')
    def _getAccountingMovement(self,current_immo_movement,next_immo_movement=None, previous_immo_movement=None):
      """
      Calculates the value of accounting movements during the period
      between the two given immobilisation movements.
      If next_immo_movement is None, accounting movements are made at infinite. 
      """
      
      def changeDateYear(date, new_year):
        """
        Return the given date modified so that its year is new_year
        """
        if new_year is not None:
          return DateTime( str(int(new_year)) + "/" + str(date.month()) + "/" + str(date.day()) )
        else:
          return date
        
      
      item = current_immo_movement.getParent()
      if item is not None:
        # First we need to calculate the item value at the first immobilisation movement date
        begin_value = current_immo_movement.getAmortisationOrDefaultAmortisationValue()
        begin_remaining = current_immo_movement.getAmortisationOrDefaultAmortisationDuration()
        
        # To find financial end date, we need to know the company
        organisation = current_immo_movement.getOrganisation()
        currency = current_immo_movement.getCurrency()
        if currency is not None:
          currency = self.currency[currency.split('/')[-1]]
                
        start_date = current_immo_movement.getStopDate()
        if next_immo_movement is not None:
          stop_date = next_immo_movement.getStopDate()
        else:
          stop_date = None
        
        returned_list = []
        # Calculate particular accounting movements (immobilisation beginning, end, ownership change...)
        immobilised_before = item.isImmobilised(at_date = start_date - 0.00001)
        immobilised_after = current_immo_movement.getImmobilisation()
        replace = 0
        
        if immobilised_before and previous_immo_movement is not None:
          immo_begin_value = previous_immo_movement.getAmortisationOrDefaultAmortisationValue()
          immo_end_value = current_immo_movement.getDefaultAmortisationValue() # We use this method in order to get the calculated value
                                                                          # of the item, and not the value entered later by the user
          if immo_end_value is not None:
            amortisation_value = immo_begin_value - immo_end_value
            end_vat = previous_immo_movement.getVat() * immo_end_value / immo_begin_value
            immo_end_value_vat = immo_end_value + end_vat
            
            returned_list.extend([{ 'stop_date'           : start_date,
                                    'type'                : 'immo',
                                    'quantity'            : -immo_begin_value,
                                    'source'              : None,
                                    'destination'         : previous_immo_movement.getImmobilisationAccount(),
                                    'source_section_value'      : None,
                                    'destination_section_value' : previous_immo_movement.getOrganisation(),
                                    'resource_value'     : currency },
                                  { 'stop_date'           : start_date,
                                    'type'                : 'vat',
                                    'quantity'            : -end_vat,
                                    'source'              : None,
                                    'destination'         : previous_immo_movement.getVatAccount(),
                                    'source_section_value'      : None,
                                    'destination_section_value' : previous_immo_movement.getOrganisation(),
                                    'resource_value'     : currency },
                                  { 'stop_date'           : start_date,
                                    'type'                : 'amo',
                                    'quantity'            : amortisation_value,
                                    'source'              : None,
                                    'destination'         : previous_immo_movement.getAmortisationAccount(),
                                    'source_section_value'      : None,
                                    'destination_section_value' : previous_immo_movement.getOrganisation(),
                                    'resource_value'     : currency },
                                  { 'stop_date'           : start_date,
                                    'type'                : 'in_out',
                                    'quantity'            : immo_end_value_vat,
                                    'source'              : None,
                                    'destination'         : previous_immo_movement.getOutputAccount(),
                                    'source_section_value'      : None,
                                    'destination_section_value' : previous_immo_movement.getOrganisation(),
                                    'resource_value'     : currency } ] )
            replace = 1
        
          
        if immobilised_after:
          immo_begin_value = begin_value
          begin_vat = current_immo_movement.getVat()
          if len(returned_list) > 0 and immo_begin_value == immo_end_value and round(begin_vat,2) == round(end_vat,2):
            # Gather data into a single movement
            returned_list[0]['source'] = current_immo_movement.getImmobilisationAccount()
            returned_list[1]['source'] = current_immo_movement.getVatAccount()
            returned_list[2]['source'] = current_immo_movement.getAmortisationAccount()
            returned_list[3]['source'] = current_immo_movement.getInputAccount()
            for i in range(4):
              returned_list[i]['source_section_value'] = organisation
            replace = 0
          else:
            returned_list.extend([{ 'stop_date'           : start_date,
                                    'type'                : 'immo',
                                    'quantity'            : - immo_begin_value,
                                    'source'              : current_immo_movement.getImmobilisationAccount(),
                                    'destination'         : None,
                                    'source_section_value'      : organisation,
                                    'destination_section_value' : None,
                                    'resource_value'     : currency },
                                  { 'stop_date'           : start_date,
                                    'type'                : 'vat',
                                    'quantity'            : - begin_vat,
                                    'source'              : current_immo_movement.getVatAccount(),
                                    'destination'         : None,
                                    'source_section_value'      : organisation,
                                    'destination_section_value' : None,
                                    'resource_value'     : currency },
                                  { 'stop_date'           : start_date,
                                    'type'                : 'amo',
                                    'quantity'            : 0,
                                    'source'              : current_immo_movement.getAmortisationAccount(),
                                    'destination'         : None,
                                    'source_section_value'      : organisation,
                                    'destination_section_value' : None,
                                    'resource_value'     : currency },
                                  { 'stop_date'           : start_date,
                                    'type'                : 'in_out',
                                    'quantity'            : immo_begin_value + begin_vat,
                                    'source'              : current_immo_movement.getInputAccount(),
                                    'destination'         : None,
                                    'source_section_value'      : organisation,
                                    'destination_section_value' : None,
                                    'resource_value'     : currency } ] )
            
              
        if replace:
          # Replace destination by source on the immobilisation-ending writings
          for i in range(4):
            returned_list[i]['source']               = returned_list[i]['destination']
            returned_list[i]['source_section_value'] = returned_list[i]['destination_section_value']
            returned_list[i]['destination']               = None
            returned_list[i]['destination_section_value'] = None
            returned_list[i]['quantity'] = - returned_list[i]['quantity']
              
        
        # Calculate the annuities
        current_value = begin_value
        if immobilised_after:
          
          # Search for the first financial end date after the first immobilisation movement
          end_date = organisation.getFinancialYearEndDate()
          end_date = changeDateYear(end_date, start_date.year() )
          if end_date - start_date <= 0:
            end_date = changeDateYear(end_date, end_date.year()+1)
          
          while (stop_date is None and current_value > 0) or (stop_date is not None and end_date - stop_date < 0):
            annuity_end_value = item.getAmortisationPrice(at_date=end_date)
            LOG('AmortisationRule :',0,'annuity_end_value=%s, current_value=%s' % (repr(annuity_end_value), repr(current_value)))
            if annuity_end_value is not None:
              annuity_value = current_value - annuity_end_value
              if annuity_value != 0:
                LOG('AmortisationRule :', 0, 'annuity until %s ; value = %s, organisation = %s' % (repr(end_date), repr(annuity_value), repr(organisation)))
                returned_list.extend([{ 'stop_date'          : end_date,
                                        'type'               : 'annuity_depr',
                                        'quantity'           : (- annuity_value),
                                        'source'             : current_immo_movement.getDepreciationAccount(),
                                        'destination'        : None,
                                        'source_section_value'     : organisation,
                                        'destination_section_value': None,
                                        'resource_value'    : currency },
                                      { 'stop_date'          : end_date,
                                        'type'               : 'annuity_amo',
                                        'quantity'           : annuity_value,
                                        'source'             : current_immo_movement.getAmortisationAccount(),
                                        'destination'        : None,
                                        'source_section_value'     : organisation,
                                        'destination_section_value': None,
                                        'resource_value'    : currency } ] )
            
            current_value -= annuity_value
            end_date = changeDateYear(end_date, end_date.year()+1)
            
          # Get the last period until the next immobilisation movement
          if stop_date is not None:
            # We use DefaultAmortisationValue in order to get the calculated value of the item,
            # and not the value entered later by the user for the next immobilisation period
            annuity_end_value = next_immo_movement.getDefaultAmortisationValue()
            if annuity_end_value is not None:
              annuity_value = current_value - annuity_end_value
              if annuity_value != 0:
                LOG('AmortisationRule :', 0, 'annuity until %s ; value = %s, organisation = %s' % (repr(next_immo_movement.getStopDate()), repr(annuity_value), repr(organisation)))
                returned_list.extend([{ 'stop_date'          : end_date,
                                        'type'               : 'annuity_depr',
                                        'quantity'           : (- annuity_value),
                                        'source'             : current_immo_movement.getDepreciationAccount(),
                                        'destination'        : None,
                                        'source_section_value'     : organisation,
                                        'destination_section_value': None,
                                        'resource_value'    : currency },
                                      { 'stop_date'          : end_date,
                                        'type'               : 'annuity_amo',
                                        'quantity'           : annuity_value,
                                        'source'             : current_immo_movement.getAmortisationAccount(),
                                        'destination'        : None,
                                        'source_section_value'     : organisation,
                                        'destination_section_value': None,
                                        'resource_value'    : currency } ] )
                
        return returned_list
            
    
            
    security.declareProtected(Permissions.ModifyPortalContent, 'solve')
    def solve(self, applied_rule, solution_list):
      """
        Solve inconsitency according to a certain number of solutions
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

    # Solvers
    security.declareProtected(Permissions.View, 'isDivergent')
    def isDivergent(self, applied_rule):
      """
        Returns 1 if divergent rule
      """

    security.declareProtected(Permissions.View, 'getDivergenceList')
    def getDivergenceList(self, applied_rule):
      """
        Returns a list Divergence descriptors
      """

    security.declareProtected(Permissions.View, 'getSolverList')
    def getSolverList(self, applied_rule):
      """
        Returns a list Divergence solvers
      """

    # Deliverability / orderability
    def isOrderable(self, m):
      return 1

    def isDeliverable(self, m):
      return 1
      # XXX ?
      if m.getSimulationState() in draft_order_state:
        return 0
      return 1
