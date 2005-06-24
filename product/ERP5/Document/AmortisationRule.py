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
from DateTime import DateTime
from copy import deepcopy
from string import lower, capitalize

from Products.ERP5Type.DateUtils import centis, getClosestDate, addToDate
from Products.ERP5Type.DateUtils import getDecimalNumberOfYearsBetween
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule
from Products.CMFCore.utils import getToolByName

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


    movement_name_dict = { 'immobilisation':   { 'immo':  'start_immo',
                                                 'amo':   'start_amo',
                                                 'vat':   'start_vat',
                                                 'in_out':'start_in_out' },
                           'unimmobilisation': { 'immo':  'stop_immo',
                                                 'amo':   'stop_amo',
                                                 'vat':   'stop_vat',
                                                 'in_out':'stop_in_out' },
                           'annuity':          { 'depr':  'annuity_depr',
                                                 'amo':   'annuity_amo' },
                           'correction':         'correction'
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
      valid_state_list = ['delivered']
      to_aggregate_movement_list = []
                                                 
      class CachedValues:
        """
        This empty class is used to pass an object through the heavy price calculation,
        in order to cache already calculated results, so the calculation is shorter
        """
        pass
        

      def updateSimulationMovementProperties(simulation_movement, calculated_movement, set_ratio=0):
        """
        Update the properties of the given simulation movement according
        to the given calculated_movement.
        WARNING : This method does not check if the state of the Amortisation
        Transaction corresponding to the Simulation Movement makes it uneditable
        set_ratio is used to force the delivery_ratio property update
        Return a list of the properties which have been modified
        """
        modified_properties = []
        for (key, value) in calculated_movement.items():
          #if value != None and key not in ('name','status','id','divergent'):
          if key not in ('name','status','id','divergent'):
            getter_name = 'get%s' % ''.join([capitalize(o) for o in key.split('_')])
            getter = getattr(simulation_movement, getter_name)
            previous_value = getter()
            # Check if this property changes
            if (previous_value is None and value is not None) or \
               (previous_value is not None and previous_value != value):
                modified_properties.append(key)
           
            if value is None and key.split('_')[-1] == 'value':
              key = '_'.join(key.split('_')[:-1])
            setter_name = 'set%s' % ''.join([capitalize(o) for o in key.split('_')])
            setter = getattr(simulation_movement, setter_name)
            setter(value)
        simulation_movement.setStartDate(simulation_movement.getStopDate())
        if set_ratio:
          simulation_movement.setDefaultDeliveryProperties()
        simulation_movement.immediateReindexObject()
        return modified_properties
     
      def updateSimulationMovement(aggregated_movement, calculated_movement,
                                   correction_number, aggregated_period_number,
                                   correction_movement_dict):
        """
        Update the Simulation Movement corresponding to aggregated_movement.
        Modify it to respect calculated_movement values.
        If the corresponding Amortisation Transaction is already validated,
        create a corrective Simulation Movement, since a validated Transaction
        must not be modified.
        If a correction movement already exists, the new movement takes care of it.
        correction_number is the id number for new movements.
        Return the number of new Simulation Movements created
        """
        def createMovement(property_dict, correction_number):
          new_id = '%s_%i_%i' % (self.movement_name_dict['correction'], aggregated_period_number, correction_number)
          simulation_movement = applied_rule.newContent(portal_type=delivery_line_type, id=new_id)
          updateSimulationMovementProperties(simulation_movement = simulation_movement,
                                             calculated_movement = property_dict)
        if aggregated_movement['status'] in valid_state_list:
          # The Simulation Movement corresponds to an Amortisation Transaction Line
          # whose Amortisation Transaction is in a valid state, so we cannot modify
          # the Simulation Movement. Some new Simulation Movements are so created
          # to correct the Simulation state.
          same_path = 1
          for property in ("source", "destination",
                           "source_section_value",
                           "destination_section_value",
                           "resource_value", "stop_date", "start_date"):
            if aggregated_movement[property] != calculated_movement[property]:
              same_path = 0

          # Determine the list of correction movement for this aggregated movement.
          # It is done only for a validated aggregated movement, since a non-validated
          # one should have been modified, rather than corrected by a correction movement
          path_tuple = (aggregated_movement['source'],
                        aggregated_movement['destination'],
                        aggregated_movement['source_section_value'],
                        aggregated_movement['destination_section_value'],
                        aggregated_movement['resource_value'],
                        aggregated_movement['stop_date'],
                        aggregated_movement['start_date'])
          correction_movement_list = correction_movement_dict.get(path_tuple, [])
          already_corrected_quantity = 0
          for correction_movement in correction_movement_list:
            already_corrected_quantity += correction_movement['quantity']
          if len(correction_movement_list) != 0:
            del correction_movement_dict[path_tuple]
              
          if same_path:
            # We only need to create a new Simulation Movement to correct the amount
            correction_quantity = calculated_movement['quantity'] - aggregated_movement['quantity']
            correction_quantity -= already_corrected_quantity
            property_dict = dict(aggregated_movement)
            if correction_quantity != 0:
              property_dict['quantity'] = correction_quantity
              createMovement(property_dict, correction_number)
              return 1
          else:
            # We need to create two new Simulation Movements : one to annulate the
            # aggregated amount, and one to correct the value according to the calculated movements
            property_dict = dict(aggregated_movement)
            correction_quantity = - property_dict['quantity']
            correction_quantity -= already_corrected_quantity
            if correction_quantity != 0:
              property_dict['quantity'] = correction_quantity
              createMovement(property_dict, correction_number)
              correction_number += 1
              createMovement(calculated_movement, correction_number)
              return 2
        else:
          # The Simulation Movement corresponds to an Amortisation Transaction Line
          # whose Amortisation Transaction is not in a valid state, so we can
          # modify the Simulation Movement. It introduces an inconsistency the user
          # will have to solve.
          simulation_movement = getattr(applied_rule, aggregated_movement['id'], None)
          modified_properties = updateSimulationMovementProperties(simulation_movement = simulation_movement,
                                                                   calculated_movement = calculated_movement)
          # If anything else the quantity has changed, the movement is disconnected and re-aggregated
          if ('quantity' in modified_properties and len(modified_properties)>1) or \
              ('quantity' not in modified_properties and len(modified_properties)>0):
            to_aggregate_movement_list.append(simulation_movement)
            simulation_movement.setDelivery('')
           
        return 0
   
      def updateSimulationMovementToZero(aggregated_movement,
                                         correction_number,
                                         aggregated_period_number,
                                         correction_movement_dict):
        """
        Set the quantity value of the given aggregated movement to 0.
        This method takes care of the validated aggregated movements
        Return the number of new movements created
        """
        property_list = dict(aggregated_movement)
        if aggregated_movement['quantity'] != 0:
          property_list['quantity'] = 0
          return updateSimulationMovement(aggregated_movement = aggregated_movement,
                                          calculated_movement = property_list,
                                          correction_number   = correction_number,
                                          aggregated_period_number = aggregated_period_number,
                                          correction_movement_dict = correction_movement_dict)
        return 0

                                          
      def setRemainingAggregatedMovementsToZero(aggregated_movement_dict,
                                                correction_number,
                                                aggregated_period_number,
                                                correction_movement_dict):
        """
        The remaining aggregation movements in aggregated_movement_dict
        are set to quantity 0, taking care of their validation state and
        the already made correction
        """
        method_movements_created = 0
        for (type, aggregated_movement_list) in aggregated_movement_dict.items():
          if type != self.movement_name_dict['correction']:
            for aggregated_movement in aggregated_movement_list:
              movements_created = updateSimulationMovementToZero(aggregated_movement = aggregated_movement,
                                                                 correction_number   = correction_number,
                                                                 aggregated_period_number = aggregated_period_number,
                                                                 correction_movement_dict = correction_movement_dict)
              correction_number += movements_created 
              method_movements_created += movements_created
        # Some correction movements may still be unused, we need to set them to 0
        unused_correction_list = []
        for correction_movement_list_list in correction_movement_dict.values():
          for correction_movement_list in correction_movement_list:
            for correction_movement in correction_movement_list:
              unused_correction_list.append(correction_movement)
        correction_movement_list = aggregated_movement_dict.get( self.movement_name_dict['correction'], [] )
        for correction_movement in correction_movement_list:
          if correction_movement in unused_correction_list:
            movements_created = updateSimulationMovementToZero(aggregated_movement = correction_movement,
                                                               correction_number   = correction_number,
                                                               aggregated_period_number = aggregated_period_number,
                                                               correction_movement_dict = {}) 
            correction_number += movements_created
            method_movements_created += movements_created

        return method_movements_created
            
          
          
      ### Start of expand() ###
        
      delivery_line_type = 'Simulation Movement'
      # Get the item we come from
      my_item = applied_rule.getCausalityValue()
      # Only expand if my_item is not None
      if my_item is None:
        return

      ### First, plan the theorical accounting movements
      cached_values = CachedValues()
      accounting_movement_list = []
      immobilisation_movement_list = my_item.getImmobilisationMovementValueList(cached_data=cached_values)
      period_number = 0
      current_immo_movement = None
      for mvt_number in range(len(immobilisation_movement_list)):
        # Update previous, current and next movement variables
        prev_immo_movement = current_immo_movement
        current_immo_movement = immobilisation_movement_list[mvt_number]
        if current_immo_movement.getImmobilisation():
          period_number += 1
        next_immo_movement = None
        if mvt_number < len(immobilisation_movement_list) - 1:
          next_immo_movement = immobilisation_movement_list[mvt_number + 1]
        # Calculate the accounting movements
        accounting_movements = self._getAccountingMovement(current_immo_movement=current_immo_movement,
                                                          next_immo_movement=next_immo_movement,
                                                          previous_immo_movement=prev_immo_movement,
                                                          period_number = period_number,
                                                          cached_data = cached_values)
        accounting_movement_list.extend(accounting_movements)

      ### The next step is to create the simulation movements
      # First, we delete all of the simulation movements which are children
      # of the applied rule, but which have not been aggregated.
      to_delete_id_list = []
      aggregated_period_dict = {}
      portal_workflow = getToolByName(self, 'portal_workflow')
      for movement in applied_rule.contentValues():
        movement_id = movement.getId()
        movement_id_name = '_'.join( movement_id.split('_')[:-2] )
        movement_id_period_number = int(movement_id.split('_')[-2])
        delivery_value = movement.getDeliveryValue()
        if delivery_value is None:
          # This movement is not already used by the accounting module,
          # we can add it to the list to delete
          to_delete_id_list.append(movement_id)
        else:
          # This movement is already used by the accounting module,
          # we store it according to the state of the corresponding
          # Amortisation Transaction. We also make a data structure
          # to make easier the future work of correspondance
          accounting_status = portal_workflow.getStatusOf('amortisation_transaction_workflow', delivery_value.getParent())
          accounting_status = accounting_status['amortisation_transaction_state']
          movement_dict = { 'stop_date':                movement.getStopDate(),
                            'start_date':               movement.getStartDate(),
                            'quantity':                 movement.getQuantity(),
                            'source_section_value':     movement.getSourceSectionValue(),
                            'destination_section_value':movement.getDestinationSectionValue(),
                            'source':                   movement.getSource(),
                            'destination':              movement.getDestination(),
                            'resource_value':           movement.getResourceValue(),
                            'id':                       movement.getId(),
                            'status':                   accounting_status,
                            'divergent':                movement.isDivergent() }
          self._placeMovementInStructure(aggregated_period_dict, movement_dict, movement_id_period_number, movement_id_name)
          # Add the delivery to the list to be notified (since each aggregated movement will be modified)
          parent = delivery_value.getParent()
          if parent:
            path = parent.getPhysicalPath()
            if not path in self._v_notify_dict.keys():
              self._v_notify_dict[path] = None
      # Deletion of non-aggregated movements
      applied_rule.deleteContent(to_delete_id_list)


      # Re-handle data of calculated movements to make easier the future
      # work of correspondance
      calculated_period_dict = {}
      for movement in accounting_movement_list:
        # Round date
        stop_date = movement['stop_date']
        if stop_date.latestTime() - stop_date < centis:
          stop_date = stop_date + 1
        stop_date = DateTime(stop_date.Date())
        movement['stop_date'] = stop_date
        movement['start_date'] = stop_date
        
        splitted_name = movement['name'].split('_')
        movement_name = '_'.join( splitted_name[:-2] )
        movement_period = int(splitted_name[-2])
        if movement['quantity'] != 0:
          self._placeMovementInStructure(calculated_period_dict, movement, movement_period, movement_name)
        
      # Then, we need to make a correspondance between aggregated movements and calculated ones
      for current_dict in (aggregated_period_dict, calculated_period_dict):
        for type_dict in current_dict.values():
          for movement_list in type_dict.values():
            movement_list.sort( lambda a,b: cmp(a['stop_date'], b['stop_date']) )
      matched_dict = self._matchAmortisationPeriods(calculated_period_dict, aggregated_period_dict)
      
      # We can now apply the calculated movements on the applied rule
      try:
        new_period = max(aggregated_period_dict.keys()) + 1
      except:
        new_period = 0
      for (c_period_number, calculated_dict) in calculated_period_dict.items():
        # First, look for a potential found match
        match = matched_dict.get(c_period_number, None)
        if match is None:
          # We did not find any match for this calculated period, so we
          # simply add the Simulation Movements into the Simulation
          for (type, movement_list) in calculated_dict.items():
            for movement_number in range(len(movement_list)):
              movement = movement_list[movement_number]
              if movement['quantity'] != 0:
                new_id = '%s_%i_%i' % (type, new_period, movement_number)
                simulation_movement = applied_rule.newContent(portal_type=delivery_line_type, id=new_id)
                # Set the properties
                updateSimulationMovementProperties(simulation_movement = simulation_movement,
                                                   calculated_movement = movement)
          new_period += 1
        else:
          # A match has been found between this calculated period, and
          # an already aggregated one. In this case, there can be orphaned
          # calculated movements, and orphaned aggregated movements.
          relocate = match['relocate']
          aggregated_period_number = match['aggregated']
          aggregated_movement_dict = aggregated_period_dict[aggregated_period_number]
          correction_data = self._getCorrectionMovementData(aggregated_movement_dict)
          correction_number = correction_data['correction_number']
          correction_movement_dict = correction_data['correction_movement_dict']
          for (type, calculated_movement_list) in calculated_dict.items():
            aggregated_movement_list = aggregated_movement_dict.get(type, [])
            new_aggregated_number = 0
            for aggregated_movement in aggregated_movement_list:
              movement_id = int( aggregated_movement['id'].split('_')[-1] )
              if movement_id + 1 > new_aggregated_number:
                new_aggregated_number = movement_id + 1

            if type in self.movement_name_dict['annuity'].values():
              # Annuity movement
              # We use relocate to match the movements.
              to_delete_from_aggregated = []
              for i in range(len(calculated_movement_list)):
                calculated_movement = calculated_movement_list[i]
                if not (i + relocate < 0 or i + relocate > len(aggregated_movement_list) - 1):
                  # We have two annuities to match
                  aggregated_movement = aggregated_movement_list[i + relocate]
                  movements_created = updateSimulationMovement(aggregated_movement = aggregated_movement,
                                                               calculated_movement = calculated_movement,
                                                               correction_number   = correction_number,
                                                               aggregated_period_number = aggregated_period_number,
                                                               correction_movement_dict = correction_movement_dict)
                  correction_number += movements_created
                  to_delete_from_aggregated.append(aggregated_movement)
                else:
                  # No matching found. We simply create the annuity
                  new_id = '%s_%i_%i' % (type, aggregated_period_number, new_aggregated_number)
                  simulation_movement = applied_rule.newContent(portal_type=delivery_line_type, id=new_id)
                  updateSimulationMovementProperties(simulation_movement = simulation_movement,
                                                     calculated_movement = calculated_movement)
                  new_aggregated_number += 1
              # There is no calculated movement left. We set the remaining aggregated movements to zero
              for movement in to_delete_from_aggregated:
                aggregated_movement_list.remove(movement)
              for aggregated_movement in aggregated_movement_list:
                movements_created = updateSimulationMovementToZero(aggregated_movement = aggregated_movement,
                                                                   correction_number   = correction_number,
                                                                   aggregated_period_number = aggregated_period_number,
                                                                   correction_movement_dict = correction_movement_dict)
                correction_number += movements_created
            else:
              # Immobilisation or unimmobilisation movement
              # If there are more than one of such movements (this should
              # occur quite rarely), the matching process has found
              # the most matching ones
              non_annuity_match = match['non-annuity'].get(type, None)
              if non_annuity_match is not None:
                aggregated_movement = aggregated_movement_list[non_annuity_match[1]]
                calculated_movement = calculated_movement_list[non_annuity_match[0]]
                movements_created = updateSimulationMovement(aggregated_movement = aggregated_movement,
                                                             calculated_movement = calculated_movement,
                                                             correction_number   = correction_number,
                                                             aggregated_period_number = aggregated_period_number,
                                                             correction_movement_dict = correction_movement_dict)
                correction_number += movements_created
                aggregated_movement_list.remove(aggregated_movement)
                calculated_movement_list.remove(calculated_movement)
              # Then the remaining movements are arbitratry matched
              for calculated_movement in calculated_movement_list:
                if len(aggregated_movement_list) > 0:
                  aggregated_movement = aggregated_movement_list[0]
                  movements_created = updateSimulationMovement(aggregated_movement = aggregated_movement,
                                                               calculated_movement = calculated_movement,
                                                               correction_number   = correction_number,
                                                               aggregated_period_number = aggregated_period_number,
                                                               correction_movement_dict = correction_movement_dict)
                  correction_number += movements_created
                  aggregated_movement_list.remove(aggregated_movement)
                else:
                  # There is no aggregated movement left. We simply create the remaining calculated movements
                  new_id = '%s_%i_%i' % (type, aggregated_period_number, new_aggregated_number)
                  simulation_movement = applied_rule.newContent(portal_type=delivery_line_type, id=new_id)
                  updateSimulationMovementProperties(simulation_movement = simulation_movement,
                                                     calculated_movement = calculated_movement)
                  new_aggregated_number += 1
              for aggregated_movement in aggregated_movement_list:
                # There is no calculated movement left. We set the remaining aggregated movements to zero.
                movements_created = updateSimulationMovementToZero(aggregated_movement = aggregated_movement,
                                                                   correction_number   = correction_number,
                                                                   aggregated_period_number = aggregated_period_number,
                                                                   correction_movement_dict = correction_movement_dict)
                correction_number += movements_created
        
            # We delete this movement type from aggregation, in order to determine
            # the types which have not been matched later
            try:
              del aggregated_movement_dict[type]
            except:
              pass
         
          movements_created = setRemainingAggregatedMovementsToZero(aggregated_movement_dict = aggregated_movement_dict,
                                                                    correction_number        = correction_number,
                                                                    aggregated_period_number = aggregated_period_number,
                                                                    correction_movement_dict = correction_movement_dict)
          correction_number += movements_created
          
          # This aggregated period handling is finished. We delete it from the dictionary
          # in order to determine the non-matched aggregated periods later.
          del aggregated_period_dict[aggregated_period_number]

          
      # The matching process is finished. Now we set to 0 each remaining aggregated movement
      for (aggregated_period_number, aggregated_movement_dict) in aggregated_period_dict.items():
        correction_data = self._getCorrectionMovementData(aggregated_movement_dict)
        correction_number = correction_data['correction_number']
        correction_movement_dict = correction_data['correction_movement_dict']
        movements_created = setRemainingAggregatedMovementsToZero(aggregated_movement_dict = aggregated_movement_dict,
                                                                  correction_number        = correction_number,
                                                                  aggregated_period_number = aggregated_period_number,
                                                                  correction_movement_dict = correction_movement_dict)
        correction_number += movements_created

      # Re-aggregate disconnected movements. These movements were already aggregated, but their properties
      # have been changed, and they have been disconnected so.
      if len(to_aggregate_movement_list) > 0:
        self.portal_deliveries.amortisation_transaction_builder.build(
            movement_relative_url_list = [m.getRelativeUrl() for m in to_aggregate_movement_list])
            

        
    def _getCorrectionMovementData(self, aggregated_movement_dict):
      """
      Return a dictionary containing the first id number for a new correction movement,
      and a re-handled structure containing the correction movements, in order to make
      easier their search
      It is needed to reduce the number of correction movements. If we can notice that
      an aggregated movement is already corrected by a correction movement, we do not
      have to correct it again
      """
      correction_movement_list = aggregated_movement_dict.get(self.movement_name_dict['correction'], [])[:]
      correction_number = 0
      for correction_movement in correction_movement_list:
        movement_id = int( correction_movement['id'].split('_')[-1] )
        if movement_id + 1 > correction_number:
          correction_number = movement_id + 1

      correction_movement_dict = {}
      for correction_movement in correction_movement_list:
        path_tuple = (correction_movement['source'],
                      correction_movement['destination'],
                      correction_movement['source_section_value'],
                      correction_movement['destination_section_value'],
                      correction_movement['resource_value'],
                      correction_movement['stop_date'],
                      correction_movement['start_date'])
        if correction_movement_dict.get(path_tuple, None) is None:
          correction_movement_dict[path_tuple] = []
        correction_movement_dict[path_tuple].append(correction_movement)
      return { 'correction_number':correction_number, 'correction_movement_dict':correction_movement_dict }
    
        
    def _matchAmortisationPeriods(self, calculated_period_dict, aggregated_period_dict):
      """
      Try to match each period in calculated_period_dict with a period in
      aggregated_period_dict.
      It is done by using a "matching ratio" : when two movements of both dictionaries
      have a identical property (source, destination, quantity, resource, ...), the
      matching ratio is incremented for the correspondance between the both corresponding
      periods.
      Then, periods are matched in order of priority of the matching ratio.
      """
      def calculateMovementMatch(movement_a, movement_b, parameter_list = ['source_section_value',
                          'destination_section_value', 'source', 'destination', 'resource_value', 'quantity'],
                          compare_dates=0 ):
        if compare_dates:
          parameter_list.append('stop_date')
        matching = { 'max':0, 'score':0 }
        for matching_parameter in parameter_list:
          matching['max'] = matching['max'] + 1
          if movement_a[matching_parameter] == movement_b[matching_parameter]:
            matching['score'] = matching['score'] + 1
        return matching
            
      matching_ratio_list = []
      for (calculated_period_number,calculated_dict) in calculated_period_dict.items():
        calculated_immobilisation = calculated_dict.get(self.movement_name_dict['immobilisation']['immo'], [])
        for (aggregated_period_number, aggregated_dict) in aggregated_period_dict.items():
          # We first compare the dates of immobilisation, so we can compare the annuity suit
          # first directly, and then by relocating in time
          relocate_list = [0, 1, -1]
          aggregated_immobilisation = calculated_dict.get(self.movement_name_dict['immobilisation']['immo'], [])
          if len(calculated_immobilisation) != 0 and len(aggregated_immobilisation) != 0:
            c_immobilisation_movement = calculated_immobilisation[-1]
            a_immobilisation_movement = aggregated_immobilisation[-1]
            c_date = c_immobilisation_movement['stop_date']
            a_date = a_immobilisation_movement['stop_date']
            if a_date < c_date:
              date_difference = int(getDecimalNumberOfYearsBetween(a_date, c_date))
            else:
              date_difference = int(- getDecimalNumberOfYearsBetween(c_date, a_date))
            if abs(date_difference) >= 1:
              relocate_list.extend(date_difference-1, date_difference, date_difference+1)
              for o in relocate_list[:]:
                while relocate_list.count(o) > 1:
                  relocate_list.remove(o)
                  
          # Then we try to effectively match some data in these two periods, by relocating in time
          # Annuities
          current_matching = {'score':0, 'max':0, 'relocate':0, 'non-annuity':{}}
          for relocate in relocate_list:
            relocate_matching = {'score':0, 'max':0, 'relocate':relocate, 'non-annuity':{}}
            a_annuity_list = aggregated_dict.get(self.movement_name_dict['annuity']['amo'], [])
            c_annuity_list = calculated_dict.get(self.movement_name_dict['annuity']['amo'], [])
            for i in range(len(a_annuity_list)):
              if not (i + relocate < 0 or i + relocate > len(c_annuity_list) - 1):
                a_annuity = a_annuity_list[i]
                c_annuity = c_annuity_list[i + relocate]
                this_matching = calculateMovementMatch(a_annuity, c_annuity)
                relocate_matching['score'] = relocate_matching['score'] + this_matching['score']
                relocate_matching['max'] = relocate_matching['max'] + this_matching['max']
            # Compare the current relocated matching with the best relocated matching found until now
            if current_matching['max'] == 0:
              current_matching_ratio = 0
            else:
              current_matching_ratio = current_matching['score'] / (current_matching['max']+0.)
            if relocate_matching['max'] == 0: relocate_matching['max'] = 1
            relocate_matching_ratio = relocate_matching['score'] / (relocate_matching['max']+0.)
            if relocate_matching_ratio >= current_matching_ratio:
              if relocate_matching_ratio > current_matching_ratio or abs(relocate) < abs(current_matching['relocate']):
                current_matching = relocate_matching
              
          # Immobilisation and unimmobilisation ; normally, there should only be one or
          # two movements of each type here, so we can compare each movement with all
          # of the others without losing much time
          for movement_type in ('immobilisation', 'unimmobilisation'):
            for immobilisation_type in self.movement_name_dict['immobilisation'].values():
              a_movement_list = aggregated_dict.get(immobilisation_type, [])
              c_movement_list = calculated_dict.get(immobilisation_type, [])
              local_best_matching = {'score':0, 'max':0, 'non-annuity':{} }
              local_current_matching = {'score':0, 'max':0}
              for a_number in range(len(a_movement_list)):
                a_movement = a_movement_list[a_number]
                for c_number in range(len(c_movement_list)):
                  c_movement = c_movement_list[c_number]
                  local_current_matching = calculateMovementMatch(a_movement, c_movement, compare_dates=1)
                  if local_best_matching['max'] == 0: local_best_matching['max'] = 1
                  local_best_ratio = local_best_matching['score'] / (local_best_matching['max']+0.)
                  if local_current_matching['max'] == 0: local_current_matching['max'] = 1
                  local_current_ratio = local_current_matching['score'] / (local_current_matching['max']+0.)
                  if local_current_ratio > local_best_ratio:
                    local_best_matching = local_current_matching
                    local_best_matching['non-annuity'] = { immobilisation_type: [a_number, c_number] }
              # Add the best found matching to the current matching score
              current_matching['score'] = current_matching['score'] + local_best_matching['score']
              current_matching['max'] = current_matching['max'] + local_best_matching['max']
              current_matching['non-annuity'].update( local_best_matching['non-annuity'] )
          
          # We found a matching ratio for this aggregated-calculated periods pair, with a particular
          # relocating. We add the ratio in the list in order to be able to retrieve it later
          if current_matching['max'] == 0:
            ratio = 0
          else:
            ratio = current_matching['score'] / (current_matching['max']+0.)
          matching_ratio_list.append( { 'calculated_period' : calculated_period_number,
                                        'aggregated_period' : aggregated_period_number,
                                        'ratio'             : ratio,
                                        'relocate'          : current_matching['relocate'],
                                        'non-annuity'       : current_matching['non-annuity'] } )

      # We have each matching ratio. Now we need to match each amortisation period
      # according to these ratio : the highest ratio gets the priority, then the next
      # highest is taken into account if corresponding resources are free, and so on
      matching_ratio_list.sort(lambda a, b: - cmp(a['ratio'], b['ratio']))
      calculated_to_match = calculated_period_dict.keys()
      aggregated_to_match = aggregated_period_dict.keys()
      match_dict = {}
      for matching_ratio in matching_ratio_list:
        calculated  = matching_ratio['calculated_period']
        aggregated  = matching_ratio['aggregated_period']
        relocate    = matching_ratio['relocate']
        non_annuity = matching_ratio['non-annuity']
        if calculated in calculated_to_match and aggregated in aggregated_to_match:
          match_dict[calculated] = { 'aggregated':aggregated, 'relocate':relocate, 'non-annuity':non_annuity }
          calculated_to_match.remove(calculated)
          aggregated_to_match.remove(aggregated)

      return match_dict
        
        
        
    def _placeMovementInStructure(self, structure, movement_dict, period_number, name):
      """
      Used to sort aggregated and calculated movements in a structure
      to make easier the correspondance work
      """
      period_dict = structure.get(period_number, None)
      if period_dict is None:
        structure[period_number] = {}
        period_dict = structure[period_number]
      movement_list = period_dict.get(name, None)
      if movement_list is None:
        period_dict[name] = []
        movement_list = period_dict[name]
      movement_list.append( movement_dict )


    security.declareProtected(Permissions.View, '_getAccountingMovement')
    def _getAccountingMovement(self,current_immo_movement,next_immo_movement=None, previous_immo_movement=None,
                               period_number=0, **kw):
      """
      Calculates the value of accounting movements during the period
      between the two given immobilisation movements.
      If next_immo_movement is None, accounting movements are made at infinite.
      """
      # These methods are used to create dictionaries containing data to return
      def buildImmobilisationCalculatedMovementList(date, period, source_section, destination_section, 
                                                    currency, movement_list=[]):
        return buildSpecificCalculatedMovementList(date, period, 0, source_section, destination_section,
                                                   currency, movement_list, 'immobilisation')
      
      def buildUnimmobilisationCalculatedMovementList(date, period, source_section, destination_section,
                                                      currency, movement_list=[]):
        return buildSpecificCalculatedMovementList(date, period, 0, source_section, destination_section,
                                                   currency, movement_list, 'unimmobilisation')

      def buildAnnuityCalculatedMovementList(date, period, annuity, source_section, destination_section,
                                             currency, movement_list=[]):
        return buildSpecificCalculatedMovementList(date, period, annuity, source_section, destination_section,
                                                   currency, movement_list, 'annuity')

      def buildSpecificCalculatedMovementList(date, period, annuity, source_section, destination_section,
                                              currency, movement_list, name):
        for movement in movement_list:
          movement['name'] = self.movement_name_dict[name][movement['name']]
        return buildCalculatedMovementList(date, period, annuity, source_section, 
                                           destination_section, currency, movement_list)

      def buildCalculatedMovementList(date, period, annuity, source_section, 
                                      destination_section, currency, movement_list = []):
        return_list = []
        for movement in movement_list:
          return_list.append(
                { 'stop_date'          : date,
                  'name'               : '%s_%i_%i' % (movement['name'], period, annuity),
                  'quantity'           : movement['quantity'],
                  'source'             : movement['source'],
                  'destination'        : movement['destination'],
                  'source_section_value'      : source_section,
                  'destination_section_value' : destination_section,
                  'resource_value'     : currency } )
        return return_list

      
      item = current_immo_movement.getParent()
      if item is not None:
        # Get some variables
        disposal_price = current_immo_movement.getDisposalPrice()
        begin_price = current_immo_movement.getAmortisationOrDefaultAmortisationPrice(**kw)
        begin_remaining = current_immo_movement.getAmortisationOrDefaultAmortisationDuration(**kw)
        section = current_immo_movement.getSectionValue()
        currency = current_immo_movement.getPriceCurrency()
        if currency is not None:
          currency = self.currency[currency.split('/')[-1]]
        start_date = current_immo_movement.getStopDate()
        stop_date = None
        if next_immo_movement is not None:
          stop_date = next_immo_movement.getStopDate()
        returned_list = []
        
        # Calculate particular accounting movements (immobilisation beginning, end, ownership change...)
        immobilised_before = item.isImmobilised(at_date = start_date - centis)
        immobilised_after = current_immo_movement.getImmobilisation()
        replace = 0  # replace is used to know if we need to reverse an one-side movement
                     # in order to have a one-side movement whose destination side is unset
        if immobilised_before and previous_immo_movement is not None:
          immo_begin_price = previous_immo_movement.getAmortisationOrDefaultAmortisationPrice(**kw)
          immo_end_price = current_immo_movement.getDefaultAmortisationPrice(**kw) # We use this method in order
                                                      # to get the calculated value of the item, and not the
                                                      # value entered later by the user
          if immo_end_price is not None:
            # Set "end of amortisation period" data
            amortisation_price = immo_begin_price - immo_end_price
            end_vat = previous_immo_movement.getVat() * immo_end_price / immo_begin_price
            immo_end_price_vat = immo_end_price + end_vat
            returned_list.extend( 
                buildUnimmobilisationCalculatedMovementList(date = start_date,
                                                            period = period_number - 1,
                                                            source_section = None,
                                                            destination_section = previous_immo_movement.getSectionValue(),
                                                            currency = currency,
                                                            movement_list=[
                            { 'name'               : 'immo',
                              'quantity'           : -immo_begin_price,
                              'source'             : None,
                              'destination'        : previous_immo_movement.getImmobilisationAccount() },
                            { 'name'               : 'vat',
                              'quantity'           : -end_vat,
                              'source'             : None,
                              'destination'        : previous_immo_movement.getVatAccount() },
                            { 'name'               : 'amo',
                              'quantity'           : amortisation_price,
                              'source'             : None,
                              'destination'        : previous_immo_movement.getAmortisationAccount() },
                            { 'name'               : 'in_out',
                              'quantity'           : immo_end_price_vat,
                              'source'             : None,
                              'destination'        : previous_immo_movement.getOutputAccount() }
                     ] ) )
            replace = 1

        if immobilised_after:
          # Set "begin of amortisation" data
          immo_begin_price = begin_price
          begin_vat = current_immo_movement.getVat()
          if len(returned_list) > 0 and round(immo_begin_price,2) == round(immo_end_price,2) and round(begin_vat,2) == round(end_vat,2):
            # Gather data into a single movement
            returned_list[0]['source'] = current_immo_movement.getImmobilisationAccount()
            returned_list[1]['source'] = current_immo_movement.getVatAccount()
            returned_list[2]['source'] = current_immo_movement.getAmortisationAccount()
            returned_list[3]['source'] = current_immo_movement.getInputAccount()
            for i in range(4):
              returned_list[i]['source_section_value'] = section
            replace = 0
          else:
            # Create another movement
            returned_list.extend( 
                buildImmobilisationCalculatedMovementList(date = start_date,
                                                          period = period_number,
                                                          source_section = section,
                                                          destination_section = None,
                                                          currency = currency,
                                                          movement_list=[
                            { 'name'               : 'immo',
                              'quantity'           : - immo_begin_price,
                              'source'             : current_immo_movement.getImmobilisationAccount(),
                              'destination'        : None },
                            { 'name'               : 'vat',
                              'quantity'           : - begin_vat,
                              'source'             : current_immo_movement.getVatAccount(),
                              'destination'        : None },
                            { 'name'               : 'amo',
                              'quantity'           : 0,
                              'source'             : current_immo_movement.getAmortisationAccount(),
                              'destination'        : None },
                            { 'name'               : 'in_out',
                              'quantity'           : immo_begin_price + begin_vat,
                              'source'             : current_immo_movement.getInputAccount(),
                              'destination'        : None }
                         ] ) )
        if replace:
          # Replace destination by source on the immobilisation-ending writings
          for i in range(4):
            returned_list[i]['source']               = returned_list[i]['destination']
            returned_list[i]['source_section_value'] = returned_list[i]['destination_section_value']
            returned_list[i]['destination']               = None
            returned_list[i]['destination_section_value'] = None
            returned_list[i]['quantity'] = - returned_list[i]['quantity']

        # Calculate the annuities
        current_price = begin_price
        if immobilised_after:
          # Search for the first financial end date after the first immobilisation movement
          end_date = getClosestDate(target_date=start_date,
                                    date=section.getFinancialYearStopDate(),
                                    precision='year',
                                    before=0)
          annuity_number = 0
          while (stop_date is None and current_price > disposal_price) or \
                (stop_date is not None and end_date - stop_date < 0):
            annuity_end_price = item.getAmortisationPrice(at_date=end_date, **kw)
            if annuity_end_price is None:
              break
            if annuity_end_price is not None:
              annuity_price = current_price - annuity_end_price
              if annuity_price < 0:
                break
              if annuity_price != 0:
                returned_list.extend( 
                    buildAnnuityCalculatedMovementList(date = end_date,
                                                       period = period_number,
                                                       annuity = annuity_number,
                                                       source_section = section,
                                                       destination_section = None,
                                                       currency = currency,
                                                       movement_list=[
                                { 'name'               : 'depr',
                                  'quantity'           : - annuity_price,
                                  'source'             : current_immo_movement.getDepreciationAccount(),
                                  'destination'        : None },
                                { 'name'               : 'amo',
                                  'quantity'           : annuity_price,
                                  'source'             : current_immo_movement.getAmortisationAccount(),
                                  'destination'        : None }
                          ] ) )
            current_price -= annuity_price
            end_date = addToDate(end_date, {'year':1})
            annuity_number += 1

          # Proceed the last annuity (incomplete, from financial year end date to stop_date)
          if stop_date is not None:
            # We use getDefaultAmortisationPrice in order to get the calculated value of the item,
            # and not the value entered later by the user for the next immobilisation period
            annuity_end_price = next_immo_movement.getDefaultAmortisationPrice(**kw)
            if annuity_end_price is not None and annuity_end_price < current_price:
              annuity_price = current_price - annuity_end_price
              if annuity_price != 0:
                returned_list.extend( 
                    buildAnnuityCalculatedMovementList(date = end_date,
                                                       period = period_number,
                                                       annuity = annuity_number,
                                                       source_section = section,
                                                       destination_section = None,
                                                       currency = currency,
                                                       movement_list=[
                                { 'name'               : 'depr',
                                  'quantity'           : - annuity_price,
                                  'source'             : current_immo_movement.getDepreciationAccount(),
                                  'destination'        : None },
                                { 'name'               : 'amo',
                                  'quantity'           : annuity_price,
                                  'source'             : current_immo_movement.getAmortisationAccount(),
                                  'destination'        : None }
                          ] ) )
                
          # Construct an unimmobilisation set of movements if the disposal value
          # is greater than 0
          if stop_date is None and disposal_price and current_price <= disposal_price:
            end_date = addToDate(end_date, year=-1)
            amortisation_price = begin_price - current_price
            end_vat = current_immo_movement.getVat() * current_price / begin_price
            immo_end_price_vat = current_price + end_vat
            returned_list.extend( 
                buildUnimmobilisationCalculatedMovementList(date = end_date,
                                                            period = period_number,
                                                            source_section = current_immo_movement.getSectionValue(),
                                                            destination_section = None,
                                                            currency = currency,
                                                            movement_list=[
                            { 'name'               : 'immo',
                              'quantity'           : begin_price,
                              'source'             : current_immo_movement.getImmobilisationAccount(),
                              'destination'        : None },
                            { 'name'               : 'vat',
                              'quantity'           : end_vat,
                              'source'             : current_immo_movement.getVatAccount(),
                              'destination'        : None },
                            { 'name'               : 'amo',
                              'quantity'           : - amortisation_price,
                              'source'             : current_immo_movement.getAmortisationAccount(),
                              'destination'        : None },
                            { 'name'               : 'in_out',
                              'quantity'           : - immo_end_price_vat,
                              'source'             : current_immo_movement.getOutputAccount(),
                              'destination'        : None }
                     ] ) )
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
      if m.getSimulationState() in self.getPortalDraftOrderStateList():
        return 0
      return 1
