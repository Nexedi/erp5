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
from string import capitalize

from Products.ERP5Type.DateUtils import centis, getClosestDate, addToDate
from Products.ERP5Type.DateUtils import getDecimalNumberOfYearsBetween
from Products.ERP5Type import Permissions
from Products.ERP5.mixin.rule import RuleMixin
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.ImmobilisationMovement import NO_CHANGE_METHOD

class AmortisationRule(RuleMixin):
    """
      Amortisation Rule object plans an item amortisation
    """

    # CMF Type Definition
    meta_type = 'ERP5 Amortisation Rule'
    portal_type = 'Amortisation Rule'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    movement_name_dict = { 'immobilisation':   { 'immo':  'start_immo',
                                                 'amo':   'start_amo',
                                                 'vat':   'start_vat',
                                                 'input': 'start_input',
                                                 'extra_input':'start_extra_input' },
                           'unimmobilisation': { 'immo':  'stop_immo',
                                                 'amo':   'stop_amo',
                                                 'output':'stop_output' },
                           'annuity':          { 'depr':  'annuity_depr',
                                                 'amo':   'annuity_amo',
                                                 'temp_amo':'annuity_temp_amo',
                                                 'temp_depr':'annuity_temp_depr' },
                           'transfer':         { 'immo':  'transfer_immo',
                                                 'amo':   'transfer_amo',
                                                 'in_out':'transfer_in_out',
                                                 'depr':  'transfer_depr'},
                           'correction':         'correction'
                         }


    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, expand_policy=None, activate_kw={}):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      assert expand_policy == "immediate" and not activate_kw

      invalid_state_list = self.getPortalUpdatableAmortisationTransactionStateList()
      to_aggregate_movement_list = []

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
        simulation_movement.edit(start_date=simulation_movement.getStopDate())
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
          simulation_movement = applied_rule.newContent(portal_type=self.movement_type, id=new_id)
          updateSimulationMovementProperties(simulation_movement = simulation_movement,
                                             calculated_movement = property_dict)
        if aggregated_movement['status'] not in invalid_state_list:
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
            simulation_movement.edit(delivery='', profit_quantity=0,
                  activate_kw={'tag':'disconnect_amortisation_transaction'})

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
        for (m_type, aggregated_movement_list) in aggregated_movement_dict.items():
          if m_type != self.movement_name_dict['correction']:
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
          for correction_movement_list in correction_movement_list_list:
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

      to_notify_delivery_list = []
      # Get the item we come from
      my_item = applied_rule.getCausalityValue()
      # Only expand if my_item is not None
      if my_item is None:
        return

      ### First, plan the theorical accounting movements
      accounting_movement_list = []
      immo_cache_dict = {'period':{}, 'price':{}, 'currency': {}}
      immo_period_list = my_item.getImmobilisationPeriodList(immo_cache_dict=immo_cache_dict)
      for period_number in range(len(immo_period_list)):
        immo_cache_dict['price'] = {}
        immo_cache_dict['currency'] = {}
        previous_period = None
        next_period = None
        immo_period = immo_period_list[period_number]
        if period_number != 0: previous_period=immo_period_list[period_number-1]
        if period_number != len(immo_period_list)-1: next_period=immo_period_list[period_number+1]
        accounting_movements = self._getAccountingMovement(immo_period=immo_period,
                                                           previous_period=previous_period,
                                                           next_period=next_period,
                                                           period_number=period_number,
                                                           item=my_item,
                                                           immo_cache_dict=immo_cache_dict)
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
          movement_dict = { 'stop_date':                movement.getStopDate(),
                            'start_date':               movement.getStartDate(),
                            'quantity':                 movement.getQuantity(),
                            'source_section_value':     movement.getSourceSectionValue(),
                            'destination_section_value':movement.getDestinationSectionValue(),
                            'source':                   movement.getSource(),
                            'destination':              movement.getDestination(),
                            'resource_value':           movement.getResourceValue(),
                            'id':                       movement.getId(),
                            'status':                   delivery_value.getRootDeliveryValue().getSimulationState(),
                            'divergent':                movement.isDivergent() }
          self._placeMovementInStructure(aggregated_period_dict, movement_dict, movement_id_period_number, movement_id_name)
          # Add the delivery to the list to be notified (since each aggregated movement will be modified)
          parent = delivery_value.getRootDeliveryValue()
          if parent is not None:
            to_notify_delivery_list.append(parent)
      # Deletion of non-aggregated movements
      applied_rule.manage_delObjects(to_delete_id_list)

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
            movement_list.sort(key=lambda x: x['stop_date'])
      matched_dict = self._matchAmortisationPeriods(calculated_period_dict, aggregated_period_dict)

      # We can now apply the calculated movements on the applied rule
      new_period=0
      try:
        if aggregated_period_dict != {}:
          new_period = max(aggregated_period_dict.keys()) + 1
      except TypeError:
        pass
      for (c_period_number, calculated_dict) in calculated_period_dict.items():
        # First, look for a potential found match
        match = matched_dict.get(c_period_number, None)
        if match is None:
          # We did not find any match for this calculated period, so we
          # simply add the Simulation Movements into the Simulation
          for (mov_type, movement_list) in calculated_dict.items():
            for movement_number in range(len(movement_list)):
              movement = movement_list[movement_number]
              if movement['quantity'] != 0:
                new_id = '%s_%i_%i' % (mov_type, new_period, movement_number)
                simulation_movement = applied_rule.newContent(portal_type=self.movement_type, id=new_id)
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
          for (mov_type, calculated_movement_list) in calculated_dict.items():
            aggregated_movement_list = aggregated_movement_dict.get(mov_type, [])
            new_aggregated_number = 0
            for aggregated_movement in aggregated_movement_list:
              movement_id = int( aggregated_movement['id'].split('_')[-1] )
              if movement_id + 1 > new_aggregated_number:
                new_aggregated_number = movement_id + 1

            if mov_type in self.movement_name_dict['annuity'].values():
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
                  new_id = '%s_%i_%i' % (mov_type, aggregated_period_number, new_aggregated_number)
                  simulation_movement = applied_rule.newContent(portal_type=self.movement_type, id=new_id)
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
                  new_id = '%s_%i_%i' % (mov_type, aggregated_period_number, new_aggregated_number)
                  simulation_movement = applied_rule.newContent(portal_type=self.movement_type, id=new_id)
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
              del aggregated_movement_dict[mov_type]
            except KeyError:
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

      # Finally notify modified deliveries in order to update causality state
      for delivery_value in to_notify_delivery_list:
        delivery_value.activate(
            after_tag='disconnect_amortisation_transaction'
            ).AmortisationTransaction_afterBuild()
        delivery_value.edit()


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
          if movement_a.get(matching_parameter) == movement_b.get(matching_parameter):
            matching['score'] = matching['score'] + 1
        return matching

      matching_ratio_list = []
      for (calculated_period_number,calculated_dict) in calculated_period_dict.items():
        calculated_immobilisation = calculated_dict.get(self.movement_name_dict['immobilisation']['immo'], [])
        for (aggregated_period_number, aggregated_dict) in aggregated_period_dict.items():
          # We first compare the dates of immobilisation, so we can compare the annuity suit
          # first directly, and then by relocating in time
          relocate_list = [0, 1, -1]
          aggregated_immobilisation = aggregated_dict.get(self.movement_name_dict['immobilisation']['immo'], [])
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
              relocate_list.extend([date_difference-1, date_difference, date_difference+1])
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
              a_annuity = a_annuity_list[i]
              if not (i + relocate < 0 or i + relocate > len(c_annuity_list) - 1):
                c_annuity = c_annuity_list[i + relocate]
              else:
                # Simulate an empty c_annuity to take into account non-matched movements
                c_annuity = {}
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
                                        'max'               : current_matching['max'],
                                        'relocate'          : current_matching['relocate'],
                                        'non-annuity'       : current_matching['non-annuity'] } )

      # We have each matching ratio. Now we need to match each amortisation period
      # according to these ratio : the highest ratio gets the priority, then the next
      # highest is taken into account if corresponding resources are free, and so on
      matching_ratio_list.sort(key=lambda x: x['ratio'], reverse=True)
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
    def _getAccountingMovement(self, immo_period, previous_period, next_period, period_number=0, item=None, **kw):
      """
      Calculates the value of accounting movements during the given period
      between the two given immobilisation movements.
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
      def buildTransferCalculatedMovementList(date, period, source_section, destination_section,
                                                    currency, movement_list=[]):
        return buildSpecificCalculatedMovementList(date, period, 0, source_section, destination_section,
                                                   currency, movement_list, 'transfer')
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
          return_list.append(dict(movement))
          return_list[-1].update(
                { 'stop_date'          : date,
                  'name'               : '%s_%i_%i' % (movement['name'], period, annuity),
                  'source_section_value'      : source_section,
                  'destination_section_value' : destination_section,
                  'resource_value'     : currency } )
        return return_list

      returned_list = []
      if item is not None:
        if immo_period is not None:
          # Get some variables
          start_movement =       immo_period.get('start_movement')
          start_date =           immo_period.get('start_date')
          start_method =         immo_period.get('start_method')
          initial_method =       immo_period.get('initial_method')
          initial_date =         immo_period.get('initial_date')
          initial_duration =     immo_period.get('initial_duration')
          disposal_price =       immo_period.get('initial_disposal_price')
          initial_price =        immo_period.get('initial_price')
          section =              immo_period.get('owner')
          continuous =           immo_period.get('continuous')
          new_owner = section
          currency = section.getPriceCurrency()
          if currency is not None:
          # XXX FIXME : do something if currency is None
            currency = self.currency_module[currency.split('/')[-1]]
          stop_date = immo_period.get('stop_date', addToDate(initial_date, month=initial_duration))

        # Period start and previous period stop
        # Possible cases :
        # 1) Item is unimmobilised before : start immobilisation
        # 2) Item is immobilised before :
        # ----------------------------------------------------------------------------------------------
        # |                   | Owner does not change |  Owner changes but the  | Actual owner changes |
        # |                   |                       |  actual owner does not  |                      |
        # ----------------------------------------------------------------------------------------------
        # |NO_CHANGE movement |     Nothing to do     |        Transfer         |Stop immo - start immo|
        # |Continuous movement|   Optional transfer   |        Transfer         |Stop immo - start immo|
        # |       Other       | Stop immo - start immo| Stop immo - start immo  |Stop immo - start immo|
        # ----------------------------------------------------------------------------------------------
        # "Optional Transfer" means "transfer from old accounts to new ones if they change"
        # "Transfer" means "transfer all non-solded accounts from a section to another"
        # "Continuous movement" means "same method as previous period and method is continuous"
        # Note that section can change without changing owner.
        # "Actual owner changes" means "the 'group' property of both owners differ"

        build_unimmo = 0
        build_immo = 0
        build_transfer = 0
        build_optional_transfer = 0
        previous_method = None
        previous_stop_date = None
        previous_owner = None
        if immo_period is None:
          if previous_period is not None:
            build_unimmo = 1
        else:
          if previous_period is not None:
            previous_method = previous_period['initial_method']
            previous_stop_date = previous_period['stop_date']
            previous_owner = previous_period['owner']
          if previous_stop_date is None or previous_stop_date != start_date:
            build_unimmo = 1
            build_immo = 1
          else:
            previous_group = previous_owner.getGroup()
            new_group = new_owner.getGroup()
            if previous_group is None or \
               new_group is None or \
               previous_group != new_group:
              build_unimmo = 1
              build_immo = 1
            else:
              if start_method not in ("",NO_CHANGE_METHOD) and (\
                   previous_method is None or \
                   start_method != previous_method or \
                   not start_movement.getAmortisationMethodParameterForItem(item, "continuous")["continuous"]):
                build_unimmo = 1
                build_immo = 1
              else:
                if previous_owner != new_owner:
                  build_transfer = 1
                else:
                  if start_movement.getAmortisationMethodParameterForItem(item, "continuous")["continuous"]:
                    build_optional_transfer = 1
                  #else nothing to do
        if previous_period is None:
          build_unimmo = 0
          build_transfer = 0
          build_optional_transfer = 0

        # Build previous period unimmobilisation
        if build_unimmo:
          previous_initial_price = previous_period['initial_price']
          previous_start_date = previous_period['start_date']
          previous_stop_date = previous_period['stop_date']
          previous_start_movement = previous_period['start_movement']
          previous_section = previous_owner
          previous_currency = previous_section.getPriceCurrency()
          if previous_currency is not None:
            # XXX FIXME : do something if currency is None
            previous_currency = self.currency_module[previous_currency.split('/')[-1]]
          previous_stop_price = item.getAmortisationPrice(at_date=previous_stop_date, **kw)
          if previous_stop_price is not None:
            previous_amortised_price = previous_initial_price - previous_stop_price
            returned_list.extend(
                buildUnimmobilisationCalculatedMovementList(date = previous_stop_date,
                                                            period = period_number - 1,
                                                            source_section = previous_section,
                                                            destination_section = None,
                                                            currency = previous_currency,
                                                            movement_list=[
                            { 'name'               : 'immo',
                              'quantity'           : previous_initial_price,
                              'source'             : previous_period['start_immobilisation_account']
                                                  or previous_period['initial_immobilisation_account'],
                              'destination'        : None, },
                            { 'name'               : 'amo',
                              'quantity'           : -previous_amortised_price,
                              'source'             : previous_period['start_amortisation_account']
                                                  or previous_period['initial_amortisation_account'],
                              'destination'        : None, },
                            { 'name'               : 'output',
                              'quantity'           : previous_amortised_price - previous_initial_price,
                              'source'             : previous_period['start_output_account']
                                                  or previous_period['initial_output_account'],
                              'destination'        : None, }
                     ] ) )


        # Build current period immobilisation
        if build_immo:
          initial_vat = immo_period.get("initial_vat") or 0
          returned_list.extend(
              buildImmobilisationCalculatedMovementList(date = start_date,
                                                        period = period_number,
                                                        source_section = section,
                                                        destination_section = None,
                                                        currency = currency,
                                                        movement_list=[
                          { 'name'               : 'immo',
                            'quantity'           : - initial_price,
                            'source'             : immo_period.get('start_immobilisation_account')
                                                or immo_period.get('initial_immobilisation_account'),
                            'destination'        : None },
                          { 'name'               : 'vat',
                            'quantity'           : - initial_vat,
                            'source'             : immo_period.get('start_vat_account')
                                                or immo_period.get('initial_vat_account'),
                            'destination'        : None },
                          { 'name'               : 'amo',
                            'quantity'           : 0,
                            'source'             : immo_period.get('start_amortisation_account')
                                                or immo_period.get('initial_amortisation_account'),
                            'destination'        : None },
                          { 'name'               : 'input',
                            'quantity'           : immo_period.get('initial_main_price') + initial_vat,
                            'source'             : immo_period.get('start_input_account')
                                                or immo_period.get('initial_input_account'),
                            'destination'        : None },
                          { 'name'               : 'extra_input',
                            'quantity'           : immo_period.get('initial_extra_cost_price') or 0,
                            'source'             : immo_period.get('start_extra_cost_account')
                                                or immo_period.get('initial_extra_cost_account'),
                            'destination'        : None }
                      ] ) )

        # Build accounts transfer if the owner changes
        # XXX FIXME : do something if currency != previous currency
        if build_transfer:
          transfer_line_list = []
          for name, key in (('immo','immobilisation_account'),
                            ('amo', 'amortisation_account')):
            previous_account = previous_period.get('start_'+ key) or previous_period['initial_'+key]
            new_account = immo_period.get('start_' + key) or immo_period.get('initial_'+key)
            cumulated_price = previous_period.get('cumulated_price_dict',{}).get( (previous_account,previous_owner), 0)
            if cumulated_price != 0:
              transfer_line_list.append({ 'name'               : name,
                                          'quantity'           : cumulated_price,
                                          'source'             : new_account,
                                          'destination'        : previous_account })
          returned_list.extend(
              buildTransferCalculatedMovementList(date = start_date,
                                                  period = period_number,
                                                  source_section = new_owner,
                                                  destination_section = previous_owner,
                                                  currency = currency,
                                                  movement_list = transfer_line_list))

        # Build accounts transfer if they change
        # XXX FIXME : do something if currency != previous currency
        if build_optional_transfer:
          transfer_line_list = []
          for name, key in (('immo','immobilisation_account'),
                            ('amo', 'amortisation_account'),
                            ('depr', 'depreciation_account')):
            previous_account = previous_period.get('start_'+ key) or previous_period['initial_'+key]
            new_account = immo_period.get('start_' + key) or immo_period['initial_'+key]
            cumulated_price = previous_period.get('cumulated_price_dict',{}).get( (previous_account, previous_owner), 0)
            if previous_account != new_account and cumulated_price != 0:
              transfer_line_list.append({ 'name'               : name,
                                          'quantity'           : cumulated_price,
                                          'source'             : new_account,
                                          'destination'        : previous_account })
          returned_list.extend(
              buildTransferCalculatedMovementList(date = start_date,
                                                  period = period_number,
                                                  source_section = new_owner,
                                                  destination_section = previous_owner,
                                                  currency = currency,
                                                  movement_list = transfer_line_list))
        # Calculate the annuities
        def buildAnnuity(from_date, to_date, depr_account, amo_account, precision, depr_name, amo_name):
          # Search for the first financial end date after the first immobilisation movement
          end_date = getClosestDate(target_date=from_date,
              date=section.getFinancialYearStopDate(),
                                    precision=precision,
                                    before=0)
          adding_dict = {precision:1}
          if end_date == initial_date:
            end_date = addToDate(end_date, **adding_dict)
          annuity_number = 0
          if continuous:
            current_price = item.getAmortisationPrice(at_date=from_date, **kw)
            if current_price is None:
              current_price = initial_price
          else:
            current_price = initial_price
          # Proceed for each annuity
          while end_date - to_date < 0:
            annuity_price = 0
            annuity_end_price = item.getAmortisationPrice(at_date=end_date, **kw)
            if annuity_end_price is None:
              break
            # Count this annuity only if it is in the current period
            if end_date - from_date > 0:
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
                                { 'name'               : depr_name,
                                  'quantity'           : - annuity_price,
                                  'source'             : depr_account,
                                  'destination'        : None },
                                { 'name'               : amo_name,
                                  'quantity'           : annuity_price,
                                  'source'             : amo_account,
                                  'destination'        : None }
                          ] ) )
            current_price -= annuity_price
            end_date = addToDate(end_date, **adding_dict)
            annuity_number += 1

          # Proceed the last annuity (maybe incomplete, from financial year end date to to_date)
          annuity_end_price = item.getAmortisationPrice(at_date=to_date, **kw)
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
                            { 'name'               : depr_name,
                              'quantity'           : - annuity_price,
                              'source'             : depr_account,
                              'destination'        : None },
                            { 'name'               : amo_name,
                              'quantity'           : annuity_price,
                              'source'             : amo_account,
                              'destination'        : None }
                        ] ) )

       #######
        if immo_period is not None:
          monthly_account = immo_period.get('start_monthly_amortisation_account') \
                         or immo_period.get('initial_monthly_amortisation_account')
          final_depreciation_account = immo_period.get('start_depreciation_account') \
                                    or immo_period.get('initial_depreciation_account')
          amortisation_account = immo_period.get('start_amortisation_account') \
                              or immo_period.get('initial_amortisation_account')
          # Build monthly annuities
          if monthly_account is not None:
            buildAnnuity(from_date=start_date,
                         to_date=stop_date,
                         depr_account=monthly_account,
                         amo_account=amortisation_account,
                         precision='month',
                         depr_name='temp_depr',
                         amo_name='temp_amo')
            inter_depreciation_account = monthly_account
          else:
            inter_depreciation_account = amortisation_account

          # Build yearly annuities
          buildAnnuity(from_date=start_date,
                       to_date=stop_date,
                       depr_account=final_depreciation_account,
                       amo_account=inter_depreciation_account,
                       precision='year',
                       depr_name='depr',
                       amo_name='amo')

          # Accumulate quantities and add them to the period dict
          if previous_period is not None:
            cumulated_price_dict = dict(previous_period.get('cumulated_price_dict',{}))
          else:
            cumulated_price_dict = {}
          for line in returned_list:
            quantity = line['quantity']
            if quantity != 0:
              source = line['source']
              destination = line['destination']
              source_section_value = line['source_section_value']
              destination_section_value = line['destination_section_value']
              if source is not None and source_section_value is not None:
                cumulated_source = cumulated_price_dict.get( (source, source_section_value), 0)
                cumulated_source += quantity
                cumulated_price_dict[(source, source_section_value)] = cumulated_source
              if destination is not None and destination_section_value is not None:
                cumulated_destination = cumulated_price_dict.get( (destination, destination_section_value), 0)
                cumulated_destination -= quantity
                cumulated_price_dict[(destination_section_value)] = cumulated_destination
          immo_period['cumulated_price_dict'] = cumulated_price_dict
      return returned_list

    # Deliverability / orderability
    def isOrderable(self, m):
      return 1

    def isDeliverable(self, m):
      return 1
      # XXX ?
      if m.getSimulationState() in self.getPortalDraftOrderStateList():
        return 0
      return 1
