##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Guillaume Michon        <guillaume.michon@e-asc.com>
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

import zope.interface
from AccessControl import ClassSecurityInfo

from DateTime import DateTime
from string import capitalize

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.DateUtils import addToDate, getClosestDate, roundDate
from Products.ERP5Type.DateUtils import getRoundedMonthBetween, millis
from Products.ERP5Type.DateUtils import getAccountableYearFraction
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.Item import Item
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.ImmobilisationMovement import (
    UNIMMOBILISING_METHOD, NO_CHANGE_METHOD, AMORTISATION_METHOD_PREFIX )
from Products.ERP5.Document.ImmobilisationMovement import (
    IMMOBILISATION_NEEDED_PROPERTY_LIST,
    IMMOBILISATION_UNCONTINUOUS_NEEDED_PROPERTY_LIST,
    IMMOBILISATION_FACULTATIVE_PROPERTY_LIST )
from zLOG import LOG

NEGLIGEABLE_PRICE = 10e-8

from Products.ERP5Type.Errors import ImmobilisationValidityError
from Products.ERP5Type.Errors import ImmobilisationCalculationError

class ImmobilisableItem(Item, Amount):
    """
      An Immobilisable Item is an Item which can be immobilised
      and amortised in accounting
    """

    meta_type = 'ERP5 ImmobilisableItem'
    portal_type = 'Immobilisable Item'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Price
                      , PropertySheet.Item
                      , PropertySheet.Amount
                      , PropertySheet.Reference
                      , PropertySheet.Amortisation
                      )

    zope.interface.implements(interfaces.IImmobilisationItem)

    # IExpandableItem interface implementation
    def getSimulationMovementSimulationState(self, simulation_movement):
      """Returns the simulation state for this simulation movement.
      """
      portal = self.getPortalObject()
      draft_state_list = portal.getPortalDraftOrderStateList()
      # if we have an order which is not draft, we'll consider the generated
      # simulation movement are planned.
      # This is probably oversimplified implementation, as we may want to look
      # deliveries / invoices.
      for movement in self.getAggregateRelatedValueList(
          portal_type=portal.getPortalOrderMovementTypeList(),):
        if movement.getSimulationState() not in draft_state_list:
          return 'planned'
      return 'draft'

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getImmobilisationRelatedMovementList')
    def getImmobilisationRelatedMovementList(self,
                                             from_date = None,
                                             to_date = None,
                                             include_to_date = 0,
                                             filter_valid = 1,
                                             immobilisation_movement_list = None,
                                             owner_movement_list = None,
                                             **kw):
      """
      Returns a dictionary of lists containing movements related to amortisation
      system from_date is included, to_date is excluded filter_valid eliminates
      all invalid immobilisation movements in immobilisation movement list.
      Also, only movements in current_inventory state are returned
      if filter_valid is set.
      If filter_valid is set and some movements are in state 'calculating',
      a ImmobilisationValidityError is launch.
      Immobilisation_movement and owner_change specify which lists to return
      immobilisation_movement_list is the list of movements to use instead of
      looking in SQL. Warning : in the case of movement_list is provided,
      no filter is applied on it (unless looking at each movement validity) and
      movement_list is supposed to be well sorted.

      The search is based on catalog so you can use related keys
      """
      wf_tool = self.portal_workflow
      sim_tool = self.portal_simulation
      catalog = self.portal_catalog
      immo_list = []
      owner_change_list = []
      immo_and_owner_list = []
      if immobilisation_movement_list is None:
        # First build the SQL query
        sql_dict = self._getCleanSqlDict(**kw)
        sql_dict['aggregate_uid'] = self.getUid()
        if filter_valid:
          sql_dict['immobilisation_state'] = ['calculating','valid']
          sql_dict['simulation_state'] = self.getPortalCurrentInventoryStateList()
        portal_type = sql_dict.get('portal_type',None)
        if portal_type is None:
          portal_type = self.getPortalDeliveryMovementTypeList() + \
                          ('Immobilisation Line', 'Immobilisation Cell')
          sql_dict['portal_type'] = portal_type
        sql_dict['sort_on'] = [('movement.stop_date','ascending')]


        # Handle dates
        date_key = 'movement.stop_date'
        date_range = ''
        date_query = []
        if from_date is not None:
          date_query.append(DateTime(from_date))
          date_range += 'min'
        if to_date is not None:
          date_query.append(DateTime(to_date))
          if include_to_date:
            date_range += 'ngt'
          else:
            date_range += 'max'
        if len(date_query) != 0:
          sql_dict[date_key] = { 'range':date_range, 'query':date_query}
        # Then execute the query
        immobilisation_movement_list = catalog(**sql_dict)
        if kw.get('src__', 0) == 1:
          return immobilisation_movement_list
      # Then build immobilisation list
      for movement in immobilisation_movement_list:
        movement = movement.getObject()
        if movement.getStopDate() is not None:
          # Test immobilisation movement
          if filter_valid and movement.getImmobilisationState() in ('invalid',
                                                                    'calculating',):
            raise ImmobilisationValidityError, \
                  '%s : some preceding movements are still in calculating state' % self.getRelativeUrl()
          immo_list.append(movement)
      return immo_list

    def _ownerChange(self, first_section, second_section):
      """
      Tests if section 1 and section 2 are the same owner or not
      It is done by looking at the mapped organisations
      If a mapped organisation exists, and the social capital currency is not None,
      it is considered as an independant organisation
      """
      if first_section == second_section:
        return 0

      first_section = self._getFirstIndependantOrganisation(first_section)
      second_section = self._getFirstIndependantOrganisation(second_section)
      if first_section is None:
        if second_section is None:
          return 0
        else:
          return 1
      elif second_section is None:
        return 1
      else:
        if first_section == second_section:
          return 0
      return 1

    def _getFirstIndependantOrganisation(self, section):
      """
      Returns the first found independant organisation, looking at
      the group tree upward. An independant organisation is found when the
      category has a mapping related value, and this value has a social capital currency
      """
      if section in (None, ""):
        return None
      if section.getPortalType() not in ("Category","Base Category"):
        if hasattr(section, 'getMappingValue'):
          category = section.getMappingValue()
          organisation = section
        else:
          category = None
          organisation = section
      else:
        category = section
        try:
          organisation = category.getMappingRelatedValueList(strict_membership = 1)[0]
        except IndexError:
          organisation = section
      if organisation is None or \
         (not hasattr(organisation, 'getPriceCurrencyValue')) or \
         (not hasattr(organisation, 'getFinancialYearStopDate')) or \
         organisation.getPriceCurrencyValue() is None or \
         organisation.getFinancialYearStopDate() is None:
        if category is None: return None
        if category.getPortalType() != "Base Category":
          return self._getFirstIndependantOrganisation(category.getParentValue())
        else:
          return None
      return organisation

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getImmobilisationMovementValueList')
    def getImmobilisationMovementValueList(self,
                                           from_date=None,
                                           to_date=None,
                                           filter_valid=1,
                                           **kw):
      """
      Returns a list of immobilisation movements applied to current item from
      date to date
      Argument filter_valid allows to select only the valid immobilisation movements
      """
      return self.getImmobilisationRelatedMovementList(from_date=from_date,
                                                       to_date=to_date,
                                                       filter_valid=filter_valid,
                                                       **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getUnfilteredImmobilisationMovementValueList')
    def getUnfilteredImmobilisationMovementValueList(self, from_date=None, to_date=None, **kw):
      """
      Returns a list of immobilisation applied to the current item from date to date
      All of the movements are returned, not even those which are valid
      """
      return self.getImmobilisationMovementValueList(from_date=from_date,
                                                     to_date=to_date,
                                                     filter_valid=0, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getPastImmobilisationMovementValueList')
    def getPastImmobilisationMovementValueList(self, from_date=None, at_date=None, **kw):
       """
       Returns a list of immobilisation movements applied to current item
       before the given date, or now
       """
       if at_date is None: at_date = DateTime()
       result = self.getImmobilisationMovementValueList(from_date=from_date,
                                                        to_date=at_date, **kw )
       return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getFutureImmobilisationMovementValueList')
    def getFutureImmobilisationMovementValueList(self, to_date=None, at_date=None, from_movement=None, **kw):
      """
      Returns a list of immobilisation movements applied to current item
      after the given date (excluded), or now.
      If from_movement is set and the given movement is found, remove it from the list.
      """
      if at_date is None: at_date = DateTime()
      at_date = at_date + millis
      result = self.getImmobilisationMovementValueList(from_date=at_date,
                                                       to_date=to_date, **kw)
      if from_movement is not None and from_movement in result:
        result.remove(from_movement)
      return result


    security.declareProtected(Permissions.AccessContentsInformation,
                              'getLastImmobilisationMovementValue')
    def getLastImmobilisationMovementValue(self, at_date=None, **kw):
      """
      Returns the last immobilisation movement before the given date, or now
      """
      past_list = self.getPastImmobilisationMovementValueList(at_date=at_date, **kw)
      if len(past_list) > 0:
        return past_list[-1]
      return None

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getNextImmobilisationMovementValue')
    def getNextImmobilisationMovementValue(self, at_date=None, from_movement=None, **kw):
      """
      Returns the first immobilisation movement after the given date, or now
      If from_movement is set and the given movement is the next one, returns
      the second next movement
      """
      future_list = self.getFutureImmobilisationMovementValueList(
                                                            at_date=at_date,
                                                            from_movement=from_movement,
                                                            **kw)
      if len(future_list) > 0:
        return future_list[0]
      return None

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getImmobilisationPeriodList')
    def getImmobilisationPeriodList(self, from_date=None, to_date=None, **kw):
      """
      Returns a list of dictionaries representing immobilisation periods for the object
      from_date is included, to_date is excluded
      """
      kw_key_list = kw.keys()
      kw_key_list.sort()
      if kw_key_list.count('immo_cache_dict'):
        kw_key_list.remove('immo_cache_dict')
      immo_cache_dict = kw.get('immo_cache_dict', {'period':{},
                                                   'price':{},
                                                   'currency': {}})
      kw['immo_cache_dict'] = immo_cache_dict
      if immo_cache_dict['period'].has_key((self.getRelativeUrl(), from_date, to_date) +
            tuple([(key,kw[key]) for key in kw_key_list])) :
        return immo_cache_dict['period'][ (self.getRelativeUrl(), from_date, to_date) +
            tuple( [(key,kw[key]) for key in kw_key_list]) ]
      def setPreviousPeriodParameters(period_list,
                                      current_period,
                                      prefix = 'initial',
                                      keys=[]):
        if len(period_list) > 0:
          previous_period = period_list[-1]
          if previous_period['stop_date'] == current_period['start_date']:
            if len(keys) == 0:
              for key in previous_period.keys():
                if key.split('_')[0] == prefix:
                  current_period[key] = previous_period[key]
            else:
              for key in keys:
                current_period[key] = previous_period[key]
      """
      We need to separate immobilisation treatment from section_change
      movements treatment.
      An immobilisation is a movement which contains immobilisation data
      and MAY change the section.
      A section change movement DOES NOT contain immobilisation data
      """
      immobilisation_list = self.getImmobilisationMovementValueList(from_date=from_date,
                                                                    to_date=to_date,
                                                                    **kw)
      section_change_list = self.getSectionChangeList(from_date=from_date,
                                                      at_date=to_date,
                                                      **kw)
      # Sanity check
      section_movement_list = []
      date_list = [movement.getStopDate() for movement in immobilisation_list]
      for section_movement in [o['movement'] for o in section_change_list]:
        if section_movement.getStopDate() in date_list and \
            section_movement not in section_movement_list and \
            section_movement not in immobilisation_list:
          raise ImmobilisationCalculationError, \
              "Some movements related to item %s have the same date" % self.getRelativeUrl()
        elif section_movement.getStopDate() not in date_list and \
            section_movement not in section_movement_list:
          #The section movement is different from immobilisation movements
          date_list.append(section_movement.getStopDate())
          section_movement_list.append(section_movement)
        else:
          #It means the current section_movement is a movement in immobilisation_list
          if section_movement.getAmortisationMethod() in ("", None, NO_CHANGE_METHOD):
            section_movement_list.append(section_movement)
            immobilisation_list.remove(section_movement)
      """
      At this stade, section_movement_list contains the movements which only
      change the owner.
      Immobilisation_list contains movements with immobilisation data and which
      may change the owner, but it may contain some movements which does not
      change the owner but with a NO_CHANGE_METHOD.
      Such movements must not be took into account, because they do not define
      a new immobilisation period. So remove them.
      """
      for immobilisation in immobilisation_list[:]:
        if immobilisation.getAmortisationMethod() in ("", None, NO_CHANGE_METHOD):
          immobilisation_list.remove(immobilisation)
      immo_period_list = []
      current_immo_period = {}
      immo_cursor = 0
      section_cursor = 0
      while immo_cursor <= len(immobilisation_list) and\
            section_cursor <= len(section_movement_list) and \
            not (immo_cursor == len(immobilisation_list) and \
            section_cursor == len(section_movement_list)):
        immobilisation = None
        section_movement = None
        is_immo_movement = 0
        is_section_movement = 0
        if immo_cursor < len(immobilisation_list):
          immobilisation = immobilisation_list[immo_cursor]
        if section_cursor < len(section_movement_list):
          section_movement = section_movement_list[section_cursor]

        if (immobilisation is not None) and (section_movement is None or \
            section_movement.getStopDate() > immobilisation.getStopDate()):
          # immobilisation treatment
          immo_cursor += 1
          is_immo_movement = 1
          movement = immobilisation
          method = immobilisation.getAmortisationMethod()
          open_new_period = 1
        else:
          # section_change treatment
          section_cursor += 1
          is_section_movement = 1
          movement = section_movement
          method = NO_CHANGE_METHOD
          if len(immo_period_list)>0:
            previous_period = immo_period_list[-1]
          else:
            previous_period = None
          if current_immo_period not in ({},None) or (
              previous_period is not None and
              previous_period.get('stop_date', None) is not None and
              previous_period['stop_date'] == section_movement.getStopDate()
            ):
            open_new_period = 1
          else:
            open_new_period = 0
        # First close the previous immobilisation period
        if current_immo_period not in (None, {}):
          current_immo_period['stop_durability'] = self.getRemainingDurability(
                       at_date=movement.getStopDate(),
                       immo_period_list=immo_period_list+[current_immo_period],
                       immo_cache_dict=immo_cache_dict)
          current_immo_period['stop_duration'] = self.getRemainingAmortisationDuration(
                       at_date=movement.getStopDate(),
                       immo_period_list=immo_period_list+[current_immo_period],
                       immo_cache_dict=immo_cache_dict)
          current_immo_period['stop_movement'] = movement
          current_immo_period['stop_date'] = movement.getStopDate()
          immo_period_list.append(current_immo_period)
          current_immo_period = {}
        current_immo_period = {}

        # Then open the new one
        if open_new_period and method != UNIMMOBILISING_METHOD:
          # First check if there is a valid owner in this period
          section = self.getSectionValue(at_date=movement.getStopDate(),
                                         include_to_date=1)
          if (section is not None) and \
             (section.getPriceCurrencyValue() is not None) and \
             (section.getFinancialYearStopDate() is not None):
            # Fill data about this period
            if is_immo_movement:
              previous_period_method = None
              current_immo_period['continuous_movement'] = movement.getAmortisationMethodParameterForItem(self,"continuous")['continuous']
              """
              The current movement is an immobilisation movement.
              We fill each 'start' and 'initial' property by looking at the movement
              properties
              """
              property_list = IMMOBILISATION_NEEDED_PROPERTY_LIST + \
                              IMMOBILISATION_UNCONTINUOUS_NEEDED_PROPERTY_LIST + \
                              IMMOBILISATION_FACULTATIVE_PROPERTY_LIST
              property_list.extend(movement.getNeededSpecificParameterListForItem(self))
              property_list.extend(movement.getUncontinuousNeededSpecificParameterListForItem(self))
              property_list.extend(movement.getFacultativeSpecificParameterListForItem(self))
              for key,value,tag in property_list:
                value = 'get' + ''.join(map(capitalize, value.split('_')))
                value = getattr(movement, value, None)
                if value is not None:
                  value = value()
                current_immo_period['start_' + key] = value
                current_immo_period['initial_' + key] = value
            else:
              """
              The current movement is a section change movement.
              We get 'start' properties from previous period, and set some other
              'start' properties by calculation
              """
              current_immo_period['start_date'] = movement.getStopDate()
              setPreviousPeriodParameters(immo_period_list,
                                          current_immo_period,
                                          prefix='start')
              current_immo_period['start_date'] = movement.getStopDate()
              setPreviousPeriodParameters(immo_period_list,
                                          current_immo_period,
                                          keys=['continuous_movement'])
              current_immo_period['start_vat'] = 0
              current_immo_period['start_extra_cost_price'] = 0
              current_immo_period['start_main_price'] = self.getAmortisationPrice(
                                          at_date=movement.getStopDate(),
                                          immo_cache_dict=immo_cache_dict)
              current_immo_period['start_duration'] = self.getRemainingAmortisationDuration(
                                          at_date=movement.getStopDate(),
                                          immo_cache_dict=immo_cache_dict)
              current_immo_period['start_durability'] = self.getRemainingDurability(
                                          at_date=movement.getStopDate(),
                                          immo_cache_dict=immo_cache_dict)
              method = current_immo_period.get('start_method', "")
            # For both types of movement, set some properties
            extra_cost_price = current_immo_period.get('start_extra_cost_price')
            main_price = current_immo_period.get('start_main_price')
            current_immo_period['start_extra_cost_price'] = extra_cost_price or 0.
            current_immo_period['start_movement'] = movement
            current_immo_period['initial_movement'] = movement
            current_immo_period['start_price'] = (main_price or 0.) + (extra_cost_price or 0.)
            current_immo_period['initial_price'] = current_immo_period['start_price']
            current_immo_period['owner'] = section
            """
            Determine if this period continues a previous one.
            There are two concepts of 'continuing' :
              - "continuous" means the current period is continuing the previous
                immobilisation
              - "adjacent" means the current period will use previous period
                data but starts a new immobilisation
            """
            continuous = 0
            adjacent = 0
            if len(immo_period_list)>0:
              previous_period_method = immo_period_list[-1]["initial_method"]
              adjacent = \
                  current_immo_period['continuous_movement'] and \
                  (previous_period_method is not None) and (\
                      previous_period_method==method or \
                      method in ("", NO_CHANGE_METHOD) \
                  ) and \
                  immo_period_list[-1]['stop_date'] == movement.getStopDate()
              """
              We must check if the current owner is in the same group as
              the previous one, in order to know if this period is completely
              new or not
              """
              previous_section = self.getSectionValue(at_date = movement.getStopDate())
              continuous = adjacent and not (
                  previous_section is None or \
                  previous_section.getGroup() is None or \
                  section.getGroup() is None or \
                  previous_section.getGroup() != section.getGroup()
                 )
            current_immo_period['continuous'] = continuous
            current_immo_period['adjacent'] = adjacent

            if continuous:
              # A continuous period gets 'initial' data from previous period.
              setPreviousPeriodParameters(immo_period_list, current_immo_period)
            elif adjacent:
              """
              An adjacent period calculates some start values then copies them to
              initial values.
              These values overload 'initial' values acquired from previous period
              """
              setPreviousPeriodParameters(immo_period_list, current_immo_period)
              if is_immo_movement:
                #Calculation of start values is already done above for section change movements
                current_immo_period['start_vat'] = 0
                current_immo_period['start_extra_cost_price'] = 0
                current_immo_period['start_main_price'] = self.getAmortisationPrice(
                                          at_date=movement.getStopDate(),
                                          immo_cache_dict=immo_cache_dict)
                current_immo_period['start_duration'] = self.getRemainingAmortisationDuration(
                                          at_date=movement.getStopDate(),
                                          immo_cache_dict=immo_cache_dict)
                current_immo_period['start_durability'] = self.getRemainingDurability(
                                          at_date=movement.getStopDate(),
                                          immo_cache_dict=immo_cache_dict)
                extra_cost_price = current_immo_period.get('start_extra_cost_price')
                main_price = current_immo_period.get('start_main_price')
                current_immo_period['start_price'] = (main_price or 0.) + (extra_cost_price or 0.)
              key_list = current_immo_period.keys()
              for key in key_list:
                value = current_immo_period[key]
                if key.find('_') != -1:
                  if key.split('_')[0] == 'start' and value not in (None, '', NO_CHANGE_METHOD):
                    current_immo_period['initial_%s' % '_'.join(key.split('_')[1:])] = value
            else:
              # A period wich is alone only copies start values to initial ones
              # So it may be invalid later
              key_list = current_immo_period.keys()
              for key in key_list:
                value = current_immo_period[key]
                if key.find('_') != -1:
                  if key.split('_')[0] == 'start' and value is not None:
                    current_immo_period['initial_%s' % '_'.join(key.split('_')[1:])] = value

            # Finally check if this period is valid. If the method is still NO_CHANGE_METHOD,
            # it means there is an inconsistency, because there is no previous immobilisation period
            needed_property_list = IMMOBILISATION_NEEDED_PROPERTY_LIST + \
                           IMMOBILISATION_UNCONTINUOUS_NEEDED_PROPERTY_LIST + \
                           movement.getNeededSpecificParameterListForItem(self) + \
                           movement.getUncontinuousNeededSpecificParameterListForItem(self)
            for key, value, tag in needed_property_list:
              if current_immo_period.get('initial_%s' % key) in (None, '', NO_CHANGE_METHOD):
                current_immo_period = {}

      if current_immo_period not in (None, {}):
        immo_period_list.append(current_immo_period)
      # Round dates since immobilisation calculation is made on days
      for immo_period in immo_period_list:
        for property in ('start_date', 'stop_date', 'initial_date',):
          if immo_period.has_key(property):
            immo_period[property] = roundDate(immo_period[property])
      immo_cache_dict['period'][ (self.getRelativeUrl(), from_date, to_date) +
            tuple([(key,kw[key]) for key in kw_key_list]) ] = immo_period_list
      return immo_period_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getLastImmobilisationPeriod')
    def getLastImmobilisationPeriod(self, to_date=None, **kw):
      """
      Returns the current immobilisation period, or the last one if the
      item is not currently immobilised, at the given at_date (excluded)
      """
      period_list = self.getImmobilisationPeriodList(from_date=None,
                                                     to_date=to_date, **kw)
      if len(period_list) == 0:
        return None
      return period_list[-1]

    security.declareProtected(Permissions.AccessContentsInformation,
                              'isCurrentlyImmobilised')
    def isCurrentlyImmobilised(self, **kw):
      """ Returns true if the item is immobilised at this time """
      return self.isImmobilised(at_date = DateTime(), **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'isNotCurrentlyImmobilised')
    def isNotCurrentlyImmobilised(self, **kw):
      """ Returns true if the item is not immobilised at this time """
      return not self.isCurrentlyImmobilised(**kw)


    security.declareProtected(Permissions.AccessContentsInformation,
                              'isImmobilised')
    def isImmobilised(self, at_date=None, **kw):
      """
      Returns true if the item is immobilised at the given date.
      If at_date = None, returns true if the item has ever been immobilised.
      """
      immo_period_list = self.getImmobilisationPeriodList(to_date=at_date, **kw)
      if len(immo_period_list) == 0:
        return 0
      elif len(immo_period_list) > 0 and at_date is None:
        return 1
      immo_period = immo_period_list[-1]
      if immo_period.has_key('stop_date'):
        # It means the latest period is terminated before the current date
        return 0
      return 1

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentRemainingAmortisationDuration')
    def getCurrentRemainingAmortisationDuration(self, **kw):
      """ Returns the calculated remaining amortisation duration for this item
          at the current time.
      """
      return self.getRemainingAmortisationDuration(at_date=DateTime(), **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getRemainingAmortisationDuration')
    def getRemainingAmortisationDuration(self, at_date=None, immo_period_list=None, **kw):
      """
      Returns the calculated remaining amortisation duration for the item.
      It is based on the latest immobilisation period at given date, or now.
      """
      if at_date is None:
        at_date = DateTime()
      new_kw = dict(kw)
      if new_kw.has_key('to_date'):
        del new_kw['to_date']
      if new_kw.has_key('at_date'):
        del new_kw['at_date']
      if immo_period_list is None:
        immo_period_list = self.getImmobilisationPeriodList(to_date=at_date, **new_kw)
      if len(immo_period_list) > 0:
        immo_period = immo_period_list[-1]
        initial_date = immo_period['initial_date']
        initial_duration = immo_period.get('initial_duration',0)
        stop_date = immo_period.get('stop_date', at_date)
        calculate = 1
        consumpted_duration = getRoundedMonthBetween(initial_date, stop_date, True)
        remaining_duration = initial_duration - consumpted_duration
        if remaining_duration < 0:
          returned_value = 0
        return int(remaining_duration)
      return None

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getRemainingDurability')
    def getRemainingDurability(self, at_date=None, immo_period_list=None, **kw):
      """
      Returns the durability of the item at the given date, or now.
      The durability is quantity of something which corresponds to the 'life' of the item
      (ex : km for a car, or time for anything)

      Each Immobilisation Movement stores the durability at a given time,
      so it is possible to approximate the durability between two Immobilisation
      Movements by using a simple
      linear calculation.

      Note that durability has no sense for items which are immobilisated but not
      amortised (like grounds, etc...). Calculation is based on duration, so an item
      immobilised without amortisation duration will not decrease its durability.
      """
      if at_date is None:
        at_date = DateTime()

      new_kw = dict(kw)
      if new_kw.has_key('to_date'):
        del new_kw['to_date']
      if new_kw.has_key('at_date'):
        del new_kw['at_date']
      if immo_period_list is None:
        immo_period_list = self.getImmobilisationPeriodList(to_date=at_date, **new_kw)
      # First case : no data about immobilisation
      if len(immo_period_list) == 0:
        return None

      immo_period = immo_period_list[-1]
      # Second case : the item is not currently immobilised
      if immo_period.has_key('stop_date'):
        return immo_period['stop_durability']

      # Third case : the item is currently immobilised
      start_date = immo_period['start_date']
      start_durability = immo_period['start_durability']
      if start_durability is None:
        immo_cache_dict = kw.get('immo_cache_dict', {'period':{},
                                                     'price':{},
                                                     'currency': {}})
        start_durability = self.getRemainingDurability(at_date=start_date,
                                                       immo_cache_dict=immo_cache_dict)
        if start_durability is None:
          return None
      stop_date = None
      stop_durability = None
      next_movement = self.getNextImmobilisationMovementValue(at_date=at_date, **kw)
      while stop_durability is None and next_movement is not None:
        stop_date = next_movement.getStopDate()
        stop_durability = next_movement.getDurability()
        next_movement = self.getNextImmobilisationMovementValue(
                                                            at_date=stop_date,
                                                            from_movement=next_movement,
                                                            **kw)
      if stop_durability is None:
        # In this case, we take the end of life of the item and use
        # it like an immobilisation movement with values set to 0
        initial_date = immo_period['initial_date']
        initial_duration = immo_period['initial_duration']
        stop_date = addToDate(initial_date, month=initial_duration)
        stop_durability = 0

      consumpted_durability = start_durability - stop_durability
      consumpted_time = getRoundedMonthBetween(start_date, stop_date, True)
      current_consumpted_time = getRoundedMonthBetween(start_date, at_date, True)
      if consumpted_time <= 0 or current_consumpted_time <= 0:
        return start_durability
      else:
        return start_durability - consumpted_durability * current_consumpted_time / consumpted_time


    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentRemainingDurability')
    def getCurrentRemainingDurability(self, **kw):
      """
      Returns the remaining durability at the current date
      """
      return self.getRemainingDurability(at_date=DateTime(), **kw)


    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAmortisationPrice')
    def getAmortisationPrice(self, at_date=None, with_currency=0, **kw):
      """
      Returns the deprecated value of item at given date, or now.
      If with_currency is set, returns a string containing the value and the
      corresponding currency.
      """
      if at_date is None:
        at_date = DateTime()
      kw_key_list = kw.keys()
      kw_key_list.sort()

      if kw_key_list.count('immo_cache_dict'):
        kw_key_list.remove('immo_cache_dict')
      immo_cache_dict = kw.get('immo_cache_dict', {'period':{},
                                                   'price':{},
                                                   'currency': {}})
      kw['immo_cache_dict'] = immo_cache_dict

      immo_cache_dict_price_key = ((self.getRelativeUrl(), at_date) +
                                   tuple([(key,kw[key]) for key in kw_key_list]))
      if immo_cache_dict['price'].has_key(immo_cache_dict_price_key) :
        returned_price = immo_cache_dict['price'][immo_cache_dict_price_key]
        if with_currency:
          currency = immo_cache_dict['currency'][immo_cache_dict_price_key]
          return '%0.2f %s' % (returned_price, currency)
        return returned_price

      immo_period_list = self.getImmobilisationPeriodList(to_date=at_date, **kw)
      if len(immo_period_list) == 0:
        # Item has never been immobilised. We cannot get its price
        if with_currency:
          return "N/A"
        return None

      # Get data from the last immo period
      immo_period = immo_period_list[-1]
      initial_movement =      immo_period['initial_movement']
      start_date =            immo_period['start_date']
      disposal_price =        immo_period['initial_disposal_price']
      period_start_date =     immo_period['initial_date']
      period_start_price =    immo_period['initial_price']
      period_start_duration = immo_period['initial_duration']
      start_price =           immo_period['start_price']
      start_duration =        immo_period['start_duration']
      start_durability =      immo_period['start_durability']
      owner =                 immo_period['owner']
      # Calculate data if not found
      if start_price is None:
        start_price = self.getAmortisationPrice(at_date=start_date,
                                                immo_cache_dict=immo_cache_dict)
      if start_duration is None:
        start_duration = self.getRemainingAmortisationDuration(at_date=start_date,
                                                        immo_cache_dict=immo_cache_dict)
      if start_durability is None:
        start_durability = self.getRemainingDurability(at_date=start_date,
                                                       immo_cache_dict=immo_cache_dict)
      # Get the current period stop date, duration and durability
      if immo_period.has_key('stop_date'):
        stop_date = immo_period['stop_date']
        period_stop_date = stop_date
      else:
        stop_date = at_date
        next_movement = self.getNextImmobilisationMovementValue(at_date=at_date, **kw)
        if next_movement is not None:
          period_stop_date = next_movement.getStopDate()
        else:
          period_stop_date = addToDate(period_start_date, month=period_start_duration)
      if at_date > period_stop_date:
        return self.getAmortisationPrice(at_date=period_stop_date, **kw)
      stop_duration = self.getRemainingAmortisationDuration(
                                                    at_date=period_stop_date,
                                                    immo_period_list=immo_period_list,
                                                    immo_cache_dict=immo_cache_dict)
      stop_durability = self.getRemainingDurability(at_date=period_stop_date,
                                                    immo_period_list=immo_period_list,
                                                    immo_cache_dict=immo_cache_dict)

      section = owner
      currency = owner.getPriceCurrency()
      depreciable_price = period_start_price - disposal_price
      financial_date = section.getFinancialYearStopDate()
      amortisation_method = AMORTISATION_METHOD_PREFIX + immo_period['initial_method']

      # Get the amortisation method parameters
      amortisation_parameters = initial_movement.getAmortisationMethodParameterForItem(
                item=self, parameter_list = [
                "cut_annuities", "price_calculation_basis",
                "round_duration", "date_precision", "with_amortisation"])
      cut_annuities = amortisation_parameters["cut_annuities"]
      price_calculation_basis = amortisation_parameters["price_calculation_basis"]
      round_duration = amortisation_parameters["round_duration"]
      date_precision = amortisation_parameters["date_precision"]
      with_amortisation = amortisation_parameters["with_amortisation"]

      # Return the price if no amortisation is needed
      if not with_amortisation:
        return period_start_price

      ### Adjust some values according to the parameters
      # Adapt period bound dates according to date_precision
      period_start_date = getClosestDate(date=financial_date,
                                         target_date=period_start_date,
                                         precision=date_precision, before=1, strict=0)
      period_stop_date = getClosestDate(date=financial_date,
                                        target_date=period_stop_date,
                                        precision=date_precision, before=0, strict=0)
      # Calculate remaining annuities at bound dates
      local_stop_date = addToDate(period_start_date, month = period_start_duration)
      initial_remaining_annuities = getAccountableYearFraction(
                                                        from_date=period_start_date,
                                                        to_date=local_stop_date)

      start_remaining_annuities = getAccountableYearFraction(from_date=start_date,
                                                             to_date=local_stop_date)

      local_stop_date = addToDate(period_stop_date, month=stop_duration)
      stop_remaining_annuities = getAccountableYearFraction(from_date=period_stop_date,
                                                            to_date=local_stop_date)
      # Round annuities if needed
      if round_duration == "greater annuity":
        if start_remaining_annuities != int(start_remaining_annuities):
          start_remaining_annuities = int(start_remaining_annuities) + 1
        else:
          start_remaining_annuities = int(start_remaining_annuities)
      elif round_duration == "lower annuity":
        start_remaining_annuities = int(start_remaining_annuities)

      if cut_annuities:
        current_date = getClosestDate(date=financial_date,
                                      target_date=period_start_date,
                                      precision='year',
                                      before=0)
      else:
        current_date = period_start_date
      annuity_number = -1
      if period_start_date - current_date < 0:
        annuity_number += 1
      while current_date - at_date < 0:
        annuity_number += 1
        current_date = addToDate(current_date, year=1)
      if annuity_number < 0:
        return depreciable_price + disposal_price
      annuity_start_date = addToDate(current_date, year=-1)
      annuity_stop_date = current_date
      truncated_annuity_stop_date = annuity_stop_date
      truncated_annuity_start_date = annuity_start_date
      # Adjust dates if it is a bound annuity
      if period_stop_date < annuity_stop_date:
        truncated_annuity_stop_date = period_stop_date
      if truncated_annuity_stop_date > at_date:
        truncated_annuity_stop_date = at_date
      if period_start_date > annuity_start_date:
        truncated_annuity_start_date = period_start_date

      # Get the current ratio
      checked_remaining_annuities = initial_remaining_annuities
      if int(checked_remaining_annuities) != checked_remaining_annuities:
        checked_remaining_annuities += 1
      if annuity_number+1 > checked_remaining_annuities:
        current_ratio = 0
      else:
        ratio_params = dict(immo_period)
        ratio_params.update(
            {'initial_remaining_annuities': initial_remaining_annuities,
             'start_remaining_annuities':   start_remaining_annuities,
             'stop_remaining_annuities':    stop_remaining_annuities,
             'current_annuity':             annuity_number,
             'start_remaining_durability':  start_durability,
             'stop_remaining_durability':   stop_durability,
            #'annuity_start_date':          annuity_start_date,
            })
        try:
          ratio_script = self.unrestrictedTraverse(amortisation_method).ratioCalculation
        except KeyError:
          LOG('ERP5 Warning :', 0,
              'Unable to find the ratio calculation script %s for item %s at date %s' % (
                 '%s/ratioCalculation' % amortisation_method, self.getRelativeUrl(), repr(at_date)))
          raise ImmobilisationCalculationError, \
              'Unable to find the ratio calculation script %s for item %s at date %s' % (
                 '%s/ratioCalculation' % amortisation_method, self.getRelativeUrl(), repr(at_date))

        current_ratio = ratio_script(**ratio_params)
        if current_ratio is None:
          LOG("ERP5 Warning :",0,
              "Unable to calculate the ratio during the amortisation calculation on item %s at date %s : script %s returned None" % (
                  self.getRelativeUrl(), repr(at_date), '%s/ratioCalculation' % amortisation_method))
          raise ImmobilisationCalculationError, \
              "Unable to calculate the ratio during the amortisation calculation on item %s at date %s" % (
                  repr(self), repr(at_date))

      # Calculate the value at the beginning of the annuity
      annuity_start_price = depreciable_price
      local_period_start_price = annuity_start_price
      if annuity_number:
        if price_calculation_basis == "period recalculated start price":
          local_period_start_date = start_date
          local_period_start_price = self.getAmortisationPrice(
                                                  at_date=local_period_start_date,
                                                  immo_cache_dict=immo_cache_dict)
          if local_period_start_price is None:
            # It means no immobilisation period exists before ; we use real start date
            local_period_start_price = start_price
          if local_period_start_date > annuity_start_date:
            annuity_start_price = local_period_start_price
          else:
            annuity_start_price = self.getAmortisationPrice(
                                      at_date=annuity_start_date,
                                      immo_cache_dict=immo_cache_dict) - disposal_price
        else:
          annuity_start_price = self.getAmortisationPrice(
                                      at_date=annuity_start_date,
                                      immo_cache_dict=immo_cache_dict) - disposal_price

      # Calculate the raw annuity value
      if price_calculation_basis == "start price":
        raw_annuity_price = depreciable_price * current_ratio
      elif price_calculation_basis == "annuity start price":
        raw_annuity_price = annuity_start_price * current_ratio
      elif price_calculation_basis == "period recalculated start price":
        raw_annuity_price = local_period_start_price * current_ratio

      # Apply the prorata temporis on the raw annuity value
      if annuity_number and \
         price_calculation_basis == 'period recalculated start price' and \
         truncated_annuity_start_date < local_period_start_date:
        truncated_annuity_start_date = local_period_start_date
      if truncated_annuity_start_date <= annuity_start_date and \
         truncated_annuity_stop_date >= annuity_stop_date:
        annuity_value = raw_annuity_price
      else:
        local_stop_date = truncated_annuity_stop_date
        if local_stop_date > at_date:
          local_stop_date = at_date
        annuity_value = raw_annuity_price * getAccountableYearFraction(
                                                from_date=truncated_annuity_start_date,
                                                to_date=local_stop_date)
      if annuity_value < NEGLIGEABLE_PRICE:
        annuity_value = 0
      # Deduct the price at the given date
      returned_price = annuity_start_price - annuity_value
      if returned_price < NEGLIGEABLE_PRICE:
        returned_price = 0
      if returned_price is None:
        return None
      returned_price += disposal_price
      immo_cache_dict['price'][immo_cache_dict_price_key] = returned_price
      immo_cache_dict['currency'][immo_cache_dict_price_key] = currency
      if with_currency:
        return '%0.2f %s' % (returned_price, currency)
      return returned_price

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCurrentAmortisationPrice')
    def getCurrentAmortisationPrice(self, with_currency=0, **kw):
      """ Returns the deprecated value of item at current time """
      return self.getAmortisationPrice(at_date=DateTime(),
                                       with_currency=with_currency, **kw)

    def _createAmortisationRule(self):
      """
      Build or update the amortisation rule related to this item, then expand the rule
      SHOULD BE RUN AS MANAGER
      """
      applied_rule_list = self.getCausalityRelatedValueList(portal_type='Applied Rule')
      my_applied_rule_list = []
      for applied_rule in applied_rule_list:
        specialise_value = applied_rule.getSpecialiseValue()
        if specialise_value is not None and\
           specialise_value.getPortalType() == "Amortisation Rule":
          my_applied_rule_list.append(applied_rule)

      if len(my_applied_rule_list) == 0:
        # Create a new applied order rule (portal_rules.order_rule)
        portal_rules = getToolByName(self, 'portal_rules')
        portal_simulation = getToolByName(self, 'portal_simulation')
        my_applied_rule = portal_rules.default_amortisation_rule.constructNewAppliedRule(portal_simulation)
        # Set causality
        my_applied_rule.setCausalityValue(self)
        my_applied_rule.reindexObject(activate_kw={'tag':'expand_amortisation'})

      elif len(my_applied_rule_list) == 1:
        # Re expand the rule if possible
        my_applied_rule = my_applied_rule_list[0]
      else:
        # Delete first rules and re expand if possible
        for my_applied_rule in my_applied_rule_list[:-1]:
          my_applied_rule.getParentValue()._delObject(my_applied_rule.getId())
        my_applied_rule = my_applied_rule_list[-1]
      # We are now certain we have a single applied rule
      # It is time to expand it
      my_applied_rule.expand('immediate') # XXX: can it be done by activity ?

    security.declareProtected(Permissions.AccessContentsInformation,
                              'expandAmortisation')
    def expandAmortisation(self,**kw):
      """
      Calculate the amortisation annuities for the item
      in an activity
      SHOULD BE RUN AS MANAGER
      """
      # An item can be expanded for amortisation only when related deliveries
      # are no more in 'calculating' immobilisation_state
      related_packing_list_list = self.getAggregateRelatedValueList()
      for related_packing_list in related_packing_list_list:
        # XXX: Tagged reindexation added to replace after_path_and_method_id. May be unnecessary.
        related_packing_list.recursiveReindexObject(
          # Recycle a tag we must wait on anyway.
          # XXX: it would be better to have per-item tags...
          activate_kw={'tag': 'expand_amortisation'},
        )
      self.activate(
        after_path_and_method_id=(
          [x.getPath() for x in related_packing_list_list],
          ('updateImmobilisationState', ),
        ),
        after_tag='expand_amortisation'
      ).immediateExpandAmortisation()

    security.declareProtected(Permissions.AccessContentsInformation,
                              'immediateExpandAmortisation')
    def immediateExpandAmortisation(self):
      """
      Calculate the amortisation annuities for the item
      SHOULD BE RUN AS MANAGER
      """
      activate_kw = {'tag' : 'expand_amortisation'}
      try:
        self._createAmortisationRule()
      except ImmobilisationValidityError:
        delivery_list = self.getAggregateRelatedValueList()
        for delivery in delivery_list:
          if getattr(delivery, 'updateImmobilisationState', None) is not None:
            delivery.updateImmobilisationState()
        self.activate().expandAmortisation(activate_kw=activate_kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getSectionMovementValueList')
    def getSectionMovementValueList(self, include_to_date=0, **kw):
      """
      Return the list of successive movements affecting
      owners of the item. If at_date is None, return the result all the time
      Only the movements in current_inventory_state are taken into account
      """
      # Get tracking list
      sql_kw = self._getCleanSqlDict(**kw)
      sql_kw['item'] = self.getRelativeUrl()
      sql_kw['sort_on'] = [('item.date','ascending')]
      change_list = self.portal_simulation.getCurrentTrackingHistoryList(**sql_kw)
      to_date = kw.get('to_date')
      # Collect data
      movement_list = []
      for change in change_list:
        date = change['date']
        movement_uid = change['delivery_uid']
        if (date is not None) and \
            movement_uid is not None:
          movement = self.portal_catalog.getObject(movement_uid)
          movement_list.append(movement)
      if include_to_date:
        sql_kw['to_date'] = None
        sql_kw['at_date'] = to_date
        last_movement = self.portal_simulation.getCurrentTrackingList(**sql_kw)
        if len(last_movement) > 0:
          movement_uid = last_movement[-1]['delivery_uid']
          if movement_uid is not None:
            movement = self.portal_catalog.getObject(movement_uid)
            if len(movement_list) == 0 or movement_list[-1] != movement:
              movement_list.append(movement)
      return movement_list

    security.declareProtected(Permissions.AccessContentsInformation, 'getSectionChangeList')
    def getSectionChangeList(self, at_date=None, **kw):
      """
      Return the list of successive owners of the item with
      the corresponding ownership change dates
      If at_date is None, return the result all the time
      """
      new_kw = self._getCleanSqlDict(**kw)
      new_kw['to_date'] = at_date
      movement_list = self.getSectionMovementValueList(**new_kw)
      # Find ownership changes
      from_date = new_kw.get('from_date')
      if from_date is None:
        previous_section = None
      else:
        previous_section = self.getSectionValue(at_date=from_date)
      owner_change_list = []
      for movement in movement_list:
        new_section = movement.getDestinationSectionValue()
        if self._ownerChange(previous_section, new_section):
          # This movement is a ownership change movement
          owner_change_list.append(movement)
          previous_section = new_section
      owner_list = []
      for movement in owner_change_list:
        owner = movement.getDestinationSectionValue()
        owner = self._getFirstIndependantOrganisation(owner)
        owner_list.append( {'owner'    : owner,
                            'date'     : movement.getStopDate(),
                            'movement' : movement } )
      return owner_list

    security.declareProtected(Permissions.AccessContentsInformation, 'getSectionValue')
    def getSectionValue(self, at_date=None, **kw):
      """
      Return the owner of the item at the given date
      If at_date is None, return the last owner without time limit
      """
      owner_list = self.getSectionChangeList(at_date=at_date, **kw)
      if len(owner_list) > 0:
        return owner_list[-1]['owner']
      return None

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentSectionValue')
    def getCurrentSectionValue(self, **kw):
      """
      Return the current owner of the item
      """
      return self.getSectionValue(at_date=DateTime(), **kw)

    def _getCleanSqlDict(self, **kw):
      no_key_list = ('immo_cache_dict',)
      for key in no_key_list:
        if key in kw:
          del kw[key]
      return kw



