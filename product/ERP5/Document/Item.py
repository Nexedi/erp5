##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Guillaume Michon        <guillaume@nexedi.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from DateTime import DateTime
from string import capitalize

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.DateUtils import addToDate, getClosestDate, getIntervalBetweenDates 
from Products.ERP5Type.DateUtils import getMonthAndDaysBetween, getRoundedMonthBetween
from Products.ERP5Type.DateUtils import getMonthFraction, getYearFraction, getBissextilCompliantYearFraction
from Products.ERP5Type.DateUtils import same_movement_interval, number_of_months_in_year, centis, millis
from Products.ERP5.Document.Amount import Amount
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.Immobilisation import Immobilisation

from zLOG import LOG


NEGLIGEABLE_PRICE = 10e-8


class Item(XMLObject, Amount):
    """
      Items in ERP5 are intended to provide a way to track objects
    """

    meta_type = 'ERP5 Item'
    portal_type = 'Item'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Price
                      , PropertySheet.Resource
                      , PropertySheet.Item
                      , PropertySheet.Amount
                      , PropertySheet.Reference
                      , PropertySheet.Amortisation
                      )

    security.declareProtected(Permissions.ModifyPortalContent,'generateNewId')
    def generateNewId(self, id_group='item_id_group', default=None, method=None):
      """
      We want a different id for all Item
      """
      return XMLObject.generateNewId(self, id_group=id_group, default=default, method=method)

    ### Amortisation

    # _update_data and _get_data are used to implement a semi-cache system on
    # heavy calculation methods.
    def _update_data(self, cached_data, date, id, value):
      if getattr(cached_data, "cached_dict", None) is None:
        cached_data.cached_dict = {}
      if cached_data.cached_dict.get(date, None) is None:
        cached_data.cached_dict[date] = {}
      cached_data.cached_dict[date][id] = value
    
    
    def _get_data(self, cached_data, date, id):
      if cached_data:
        cached_dict = getattr(cached_data,"cached_dict", None)
        if cached_dict is not None:
          cached_date = cached_dict.get(date, None)
          if cached_date is not None:
            cached_value = cached_date.get(id, None)
            if cached_value is not None:
              return cached_value
      return None
    
    
    security.declareProtected(Permissions.View, 'getImmobilisationMovementValueList')
    def getImmobilisationMovementValueList(self, from_date=None, to_date=None, 
                                           sort_on="stop_date", filter_valid=1, 
                                           owner_change=1, single_from=0, single_to=0, 
                                           property_filter=['price', 'duration', 'durability'], **kw):
      """
      Returns a list of immobilisation movements applied to current item from date to date
      Argument filter_valid allows to select only the valid immobilisation movements
      Argument owner_change allows to create temporarily some immobilisation movements
        when the owner of the item changes.
      Arguments single_from and single_to (exclusive from each other) allow to dramatically
        reduce the calculation time, but it returns only one movement : the nearest from
        from_date or to_date.
      Argument property_filter has the same goal. Its role is to reduce the number of calculated
        properties when a temporary immobilisation movement is created
      """
      accessor = 'get'
      if sort_on is not None:
        word_list = sort_on.split('_')
        for i in range(len(word_list)):
          accessor += word_list[i].capitalize()

      def cmpfunc(a,b, accessor = accessor):
        """
        Compares the two objects according to the accessor value.
        """
        access_a = getattr(a, accessor, None)
        access_b = getattr(b, accessor, None)
        if access_a is None or access_b is None:
          return 0
        return cmp(access_a(), access_b())

      
      # Build the immobilisation movement list
      immobilisation_list = []
      for immobilisation in self.contentValues(filter = { 'portal_type':'Immobilisation' } ):
        if filter_valid:
          invalid = immobilisation.checkImmobilisationConsistency()
        else:
          invalid = 0
        if not invalid:
          immo_date = immobilisation.getStopDate()
          if ( to_date is None or immo_date - to_date <= 0 ) and \
             ( from_date is None or immo_date - from_date >= 0 ):
            immobilisation_list.append(immobilisation)


      # Look for each change of ownership and an immobilisation movement within 1 hour
      # If found, adapt the immobilisation date to be correctly interpreted
      # If not found, and owner_change set to 1, create a context immobilisation movement
      ownership_list = self.getSectionList(to_date)
      if single_from or single_to:
        immobilisation_list.sort(cmpfunc)
        if single_from:
          if len(immobilisation_list) > 0: immobilisation_list = immobilisation_list[:1]
          if len(ownership_list) > 0:      ownership_list = ownership_list[:1]
        else:
          if len(immobilisation_list) > 0: immobilisation_list = immobilisation_list[-1:]
          if len(ownership_list) > 0:      ownership_list = ownership_list[-1:]
        
      for ownership in ownership_list:
        owner_date = ownership['date']
        found_immo = None
        nearest_immo = None
        i = 0
        # Find the nearest immobilisation movement from the propertyship change
        # and an immobilisation movement within a tolerance interval
        while i < len(immobilisation_list) and found_immo is None:
          immobilisation = immobilisation_list[i]
          current_immo_stop_date = immobilisation.getStopDate()
          if (current_immo_stop_date is not None) and (current_immo_stop_date - owner_date < 0) \
                                                  and (nearest_immo is None \
                                                       or nearest_immo.getStopDate() - current_immo_stop_date < 0):
            nearest_immo = immobilisation
          if (current_immo_stop_date is not None) and abs(owner_date - current_immo_stop_date) < same_movement_interval:
            found_immo = immobilisation
          i += 1

        if found_immo is None and owner_change and nearest_immo is not None:
          # None immobilisation movement was found within the tolerance interval
          # and argument owner_change is set. So we need to create a temporary
          # immobilisation movement on the change date.
          # This has to be done only if nearest_immo is defined, since the temporary
          # movement gets most of its data on the previous movement, which is nearest_immo
          added_immo = None
          added_immo = nearest_immo.asContext()
          added_immo.setStopDate(owner_date + millis)
          if "durability" in property_filter:
            added_immo.setDurability(added_immo.getDefaultDurability(**kw))
          if added_immo.getImmobilisation():
            if 'price' in property_filter:
              vat = nearest_immo.getVat()
              previous_value = nearest_immo.getAmortisationOrDefaultAmortisationPrice(**kw)
              current_value = added_immo.getDefaultAmortisationPrice(**kw)
              added_immo.setAmortisationStartPrice(current_value)
              added_immo.setVat( vat * current_value / previous_value )
            if 'duration' in property_filter:
              added_immo.setAmortisationDuration(added_immo.getDefaultAmortisationDuration(**kw))
            added_immo.setInputAccount(added_immo.getOutputAccount())
          immobilisation_list.append(added_immo)
          found_immo = added_immo

        if found_immo is not None:
          # It means an immobilisation movement is located within the tolerance interval
          # Two cases :
          #  - An unimmobilising movement and ownership change are close :
          #        the unimmobilising movement has to be before the ownership change
          #  - An immobilising movement and ownership change are close :
          #        the immobilising movement has to be after the ownership change
          found_date = found_immo.getStopDate()
          if found_immo.getImmobilisation():
            if found_date - owner_date < 0:
              found_immo.setStopDate(owner_date + centis)
          else:
            if found_date - owner_date > 0:
              found_immo.setStopDate(owner_date - centis)

      if sort_on is not None:
        immobilisation_list.sort(cmpfunc)
        # Check if some movements have the same date. If it is the case, since
        # it is impossible to know which movement has to be before the other ones,
        # change arbitrarily the date of one of them, in order to at least
        # have always the same behavior
        for i in range(len(immobilisation_list)):
          immobilisation = immobilisation_list[i]
          ref_date = immobilisation.getStopDate()
          immobilisation_sublist = [immobilisation]
          j = 1
          while i+j < len(immobilisation_list) and immobilisation_list[i+j].getStopDate() == ref_date:
            immobilisation_sublist.append(immobilisation_list[i+j])
            j += 1
          for j in range(len(immobilisation_sublist)):
            immobilisation_sublist[j].setStopDate( ref_date + j * millis )
          
      return immobilisation_list


    security.declareProtected(Permissions.View, 'getUnfilteredImmobilisationMovementValueList')
    def getUnfilteredImmobilisationMovementValueList(self, from_date=None, to_date=None, sort_on="stop_date", owner_change=0, **kw):
      """
      Returns a list of immobilisation applied to the current item from date to date
      All of the movements are returned, not even those which are valid
      """
      return self.getImmobilisationMovementValueList(from_date=from_date,
                                                to_date=to_date,
                                                sort_on=sort_on,
                                                owner_change=owner_change,
                                                filter_valid=0, **kw)


    security.declareProtected(Permissions.View, 'getPastImmobilisationMovementValueList')
    def getPastImmobilisationMovementValueList(self, from_date=None, at_date=None, sort_on="stop_date", owner_change=1, **kw):
       """
       Returns a list of immobilisation movements applied to current item before the given date, or now
       """
       if at_date is None: at_date = DateTime()
       result = self.getImmobilisationMovementValueList(from_date = from_date,
                                                   to_date = at_date,
                                                   sort_on = sort_on,
                                                   owner_change = owner_change, **kw )
       return result


    security.declareProtected(Permissions.View, 'getFutureImmobilisationMovementValueList')
    def getFutureImmobilisationMovementValueList(self, to_date=None, at_date=None, sort_on="stop_date", owner_change=1, **kw):
      """
      Returns a list of immobilisation movements applied to current item after the given date, or now
      """
      if at_date is None: at_date = DateTime()
      result = self.getImmobilisationMovementValueList(from_date = at_date,
                                                  to_date = to_date,
                                                  sort_on = sort_on,
                                                  owner_change = owner_change, **kw)
      return result


    security.declareProtected(Permissions.View, 'getLastImmobilisationMovementValue')
    def getLastImmobilisationMovementValue(self, at_date=None, owner_change=1, **kw):
      """
      Returns the last immobilisation movement before the given date, or now
      """
      past_list = self.getPastImmobilisationMovementValueList(at_date = at_date,
                                                              owner_change=owner_change,
                                                              single_to = 1, **kw)

      if len(past_list) > 0:
        return past_list[-1]
      return None

    
    security.declareProtected(Permissions.View, 'getNextImmobilisationMovementValue')
    def getNextImmobilisationMovementValue(self, at_date=None, owner_change=1, **kw):
      """
      Returns the last immobilisation movement after the given date, or now
      """
      future_list = self.getFutureImmobilisationMovementValueList(at_date = at_date,
                                                                  owner_change = owner_change,
                                                                  single_from = 1, **kw)
      if len(future_list) > 0:
        return future_list[0]
      return None


    security.declareProtected(Permissions.View, 'getLastMovementAmortisationDuration')
    def getLastMovementAmortisationDuration(self, at_date=None, owner_change=1, **kw):
      """
        Returns total duration of amortisation for the item.
        It is the theorical lifetime of this type of item.
      """
      last_immobilisation_movement = self.getLastImmobilisationMovementValue(at_date = at_date, 
                                                                             owner_change=owner_change,
                                                                             property_filter = ['duration'],
                                                                             **kw)
      if last_immobilisation_movement is not None:
        return last_immobilisation_movement.getAmortisationOrDefaultAmortisationDuration(**kw)
      else:
        return None


    security.declareProtected(Permissions.View, 'isCurrentlyImmobilised')
    def isCurrentlyImmobilised(self, **kw):
      """ Returns true if the item is immobilised at this time """
      return self.isImmobilised(at_date = DateTime(), **kw)


    security.declareProtected(Permissions.View, 'isNotCurrentlyImmobilised')
    def isNotCurrentlyImmobilised(self, **kw):
      """ Returns true if the item is not immobilised at this time """
      return not self.isCurrentlyImmobilised(**kw)


    security.declareProtected(Permissions.View, 'isImmobilised')
    def isImmobilised(self, at_date=None, **kw):
      """
      Returns true if the item is immobilised at the given date.
      If at_date = None, returns true if the item has ever been immobilised.
      """
      if at_date is not None:
        is_immobilised = 0
        last_immobilisation_movement = self.getLastImmobilisationMovementValue(at_date = at_date, **kw)
        if last_immobilisation_movement is not None:
          is_immobilised = last_immobilisation_movement.getImmobilisation()
      else:
        past_immobilisation_movement_list = self.getPastImmobilisationMovementValueList(at_date = DateTime(), **kw)
        for past_immobilisation in past_immobilisation_movement_list:
          if past_immobilisation.getImmobilisation():
            return 1
      return is_immobilised


    security.declareProtected(Permissions.View, 'getCurrentAmortisationDuration')
    def getCurrentAmortisationDuration(self, **kw):
      """ Returns the total time the item has been amortised until now. """
      return self.getRemainingAmortisationDuration(at_date = DateTime(), **kw)


    security.declareProtected(Permissions.View, 'getRemainingAmortisationDuration')
    def getRemainingAmortisationDuration(self, at_date=None, from_immobilisation=0, **kw):
      """
      Returns the calculated remaining amortisation duration for the item.
      It is based on the latest immobilisation period at given date, or now.

      If from_immobilisation is set, we don't take the very last immobilisation movement
      at the date. It is needed if the function is called by this particular movement, unless
      the function will never end.
      """
      if at_date is None:
        at_date = DateTime()

      # Find the latest movement whose immobilisation is true
      if from_immobilisation:
        my_at_date = at_date - centis
      else:
        my_at_date = at_date
      
      cached_data = kw.get("cached_data", None)
      cached_duration = self._get_data(cached_data, my_at_date, 'duration')
      if cached_duration is not None:
        return cached_duration
      
      last_immobilisation_movement = self.getLastImmobilisationMovementValue(at_date = my_at_date,
                                                                             property_filter = ['duration'],
                                                                             **kw)
      previous_loop_movement = None
      start_movement = None
      stop_movement = None
      current_search_date = None
      while last_immobilisation_movement is not None and start_movement is None:
        if last_immobilisation_movement.getImmobilisation():
          start_movement = last_immobilisation_movement
          stop_movement = previous_loop_movement
        if not start_movement:
          previous_loop_movement = last_immobilisation_movement
          last_date = last_immobilisation_movement.getStopDate() - centis
          last_immobilisation_movement = self.getLastImmobilisationMovementValue(at_date = last_date,
                                                                                 property_filter = ['duration'],
                                                                                 **kw)
      
      if start_movement is None:
        # Neither of past immobilisation movements did immobilise the item...
        duration = self.getLastMovementAmortisationDuration(at_date=my_at_date, **kw)
        if duration is not None:
          if cached_data: self._update_data(cached_data, my_at_date, 'duration', int(duration))
          return int(duration)
        return None
      # We found the last immobilising movement
      # Two cases are possible : 
      #  - The item is still in an amortisation period (i.e. the immobilising movement is the latest)
      #  - The item is not in an amortisation period : in this case, we have to find the date of the unimmobilising movement
      if stop_movement is None:
        # Item is currently in an amortisation period
        immo_period_stop_date = at_date
      else:
        immo_period_stop_date = stop_movement.getStopDate()
      immo_period_start_date = start_movement.getStopDate()
      immo_period_remaining = start_movement.getAmortisationOrDefaultAmortisationDuration(**kw)
      immo_period_duration = getRoundedMonthBetween(immo_period_start_date, immo_period_stop_date)
      returned_value = immo_period_remaining - immo_period_duration
      if returned_value < 0:
        returned_value = 0
      if cached_data: self._update_data(cached_data, my_at_date, 'duration', returned_value)
      return int(returned_value)


    security.declareProtected(Permissions.View, 'getRemainingDurability')
    def getRemainingDurability(self, at_date=None, from_immobilisation=0, **kw):
      """
      Returns the durability of the item at the given date, or now.
      The durability is quantity of something which corresponds to the 'life' of the item
      (ex : km for a car, or time for anything)

      Each Immobilisation Movement stores the durability at a given time, so it is possible
      to approximate the durability between two Immobilisation Movements by using a simple
      linear calculation.
      """
      if at_date is None:
        at_date = DateTime()
      my_at_date = at_date
      if from_immobilisation:
        my_at_date -= centis
        
      cached_data = kw.get("cached_data", None)
      cached_durability = self._get_data(cached_data, my_at_date, "durability")
      if cached_durability is not None:
        return cached_durability
      
      last_movement = self.getLastImmobilisationMovementValue(at_date = my_at_date,
                                                              property_filter = ['durability', 'duration'],
                                                              **kw)
      if last_movement is not None:
        if not last_movement.getImmobilisation():
          # The item is not currently amortised
          # The current durability is the durability on
          # last immobilisation movement
          return_value = last_movement.getDurability()
          if cached_data: self._update_data(cached_data, my_at_date, 'durability', return_value)
          return return_value
        start_durability = last_movement.getDurability()
        start_date = last_movement.getStopDate()

        my_at_date = at_date
        if from_immobilisation:
          my_at_date += centis
          
        next_movement = self.getNextImmobilisationMovementValue(at_date = my_at_date + millis,
                                                                          property_filter = ['durability'],
                                                                          **kw)
        if next_movement is not None:
          stop_durability = next_movement.getDurability()
          stop_date = last_movement.getStopDate()
        else:
          # In this case, we take the end of life of the item and use
          # it like an immobilisation movement with values set to 0
          last_remaining_months = last_movement.getAmortisationOrDefaultAmortisationDuration(**kw)
          stop_date = addToDate(start_date, month=last_remaining_months)
          stop_durability = 0

        consumpted_durability = start_durability - stop_durability
        consumpted_time = getRoundedMonthBetween(start_date, stop_date)
        current_consumpted_time = getRoundedMonthBetween(start_date, at_date)
        if consumpted_time <= 0 or current_consumpted_time <= 0:
          return_value = start_durability
        else:
          return_value = start_durability - consumpted_durability * current_consumpted_time / consumpted_time
      else:
        return_value = None
     
      if cached_data: self._update_data(cached_data, my_at_date, 'durability', return_value)
      return return_value


    security.declareProtected(Permissions.View, 'getCurrentRemainingDurability')
    def getCurrentRemainingDurability(self, **kw):
      """
      Returns the remaining durability at the current date
      """
      return self.getRemainingDurability(at_date = DateTime(), **kw)
    

    security.declareProtected(Permissions.View, 'getAmortisationPrice')
    def getAmortisationPrice(self, at_date=None, from_immobilisation=0, with_currency=0, **kw):
      """
      Returns the deprecated value of item at given date, or now.

      If from_immobilisation is set, we don't take the very last immobilisation movement
      at the date. It is needed if the function is called by this particular movement, unless
      the function will never end.

      If with_currency is set, returns a string containing the value and the corresponding currency.
      """
      if at_date is None:
        at_date = DateTime()
      # Find the latest movement whose immobilisation is true
      if from_immobilisation:
        # We need to exclude the immobilisation movement which calls currently the method,
        # unless the method will never end
        my_at_date = at_date - centis
      else:
        my_at_date = at_date
      
      cached_data = kw.get("cached_data", None)
      cached_price = self._get_data(cached_data, my_at_date, 'price')
      if cached_price is not None:
        return cached_price
      
      last_immobilisation_movement = self.getLastImmobilisationMovementValue(at_date = my_at_date, 
                                                                             **kw)
      previous_loop_movement = None
      start_movement = None
      stop_movement = None
      current_search_date = None
      while last_immobilisation_movement is not None and start_movement is None:
        if last_immobilisation_movement.getImmobilisation():
          start_movement = last_immobilisation_movement
          stop_movement = previous_loop_movement
        if not start_movement:
          previous_loop_movement = last_immobilisation_movement
          last_date = last_immobilisation_movement.getStopDate() - millis
          last_immobilisation_movement = self.getLastImmobilisationMovementValue(at_date = last_date,
                                                                                 **kw)
        
      if start_movement is None:
        # Neither of past immobilisation movements did immobilise the item...
        LOG ('ERP5 Warning :',0,'Neither of past immobilisation movements did immobilise the item %s' % self.getTitle())
        last_immobilisation_movement = self.getLastImmobilisationMovementValue(at_date = my_at_date,
                                                                               **kw)
        if last_immobilisation_movement:
          returned_price = last_immobilisation_movement.getAmortisationOrDefaultAmortisationPrice(**kw)
          if with_currency:
            return '%s %s' % (repr(round(returned_price,2)), immobilisation_movements[-1].getPriceCurrency())
          if cached_data: self._update_data(cached_data, my_at_date, 'price', returned_price)
          return returned_price
        return None # XXX How to find the buy value ?

      # Find the latest immobilisation period and gather information
      currency = start_movement.getPriceCurrency()
      start_date = start_movement.getStopDate()
      if stop_movement is None:
        # Item is currently in an amortisation period
        stop_date = at_date
      else:
        # Item is not in an amortisation period
        stop_date = stop_movement.getStopDate()


      start_price = start_movement.getAmortisationOrDefaultAmortisationPrice(**kw)
      disposal_price = start_movement.getDisposalPrice()
      depreciable_price = start_price - disposal_price
      start_remaining_months = start_movement.getAmortisationOrDefaultAmortisationDuration(**kw)
      stop_remaining_months = 0
      start_durability = start_movement.getDurability(**kw)
      stop_durability = 0
      section = start_movement.getSectionValue()
      financial_date = section.getFinancialYearStopDate()
      amortisation_method = "erp5_accounting_" + start_movement.getAmortisationMethod()
      next_date = stop_date
      
      if stop_movement is not None:
        stop_remaining_months = stop_movement.getDefaultAmortisationDuration(**kw)
        stop_durability = stop_movement.getDurabilityOrDefaultDurability(**kw)
      else:
        next_movement = self.getNextImmobilisationMovementValue(at_date = my_at_date + millis,
                                                                property_filter = ['durability'],
                                                                **kw)
        if next_movement is not None:
          stop_durability = next_movement.getDurabilityOrDefaultDurability(**kw)
          stop_remaining_months = next_movement.getDefaultAmortisationDuration(**kw)
          next_date = next_movement.getStopDate()
        else:
          next_date = addToDate(start_date, month = start_remaining_months)
          
      # Get the amortisation method parameters
      amortisation_parameters = start_movement.getAmortisationMethodParameter(parameter_list = [
                "cut_annuities", "price_calculation_basis", "prorata_precision",
                "round_duration", "specific_parameter_list", "date_precision"])
      cut_annuities = amortisation_parameters["cut_annuities"]
      price_calculation_basis = amortisation_parameters["price_calculation_basis"]
      prorata_precision = amortisation_parameters["prorata_precision"]
      round_duration = amortisation_parameters["round_duration"]
      date_precision = amortisation_parameters["date_precision"]
      specific_parameter_list = amortisation_parameters["specific_parameter_list"]
      
      # Adjust some values according to the parameters 
      start_date = getClosestDate(date=financial_date, target_date=start_date,
                                  precision=date_precision, before=1, strict=0)
      stop_date = getClosestDate(date=financial_date, target_date=stop_date,
                                 precision=date_precision, before=0, strict=0)
      
      if prorata_precision == 'day':
        local_stop_date = addToDate(start_date, month = start_remaining_months)
        start_remaining_annuities = getBissextilCompliantYearFraction(from_date = start_date,
                                                                      to_date   = local_stop_date,
                                                                      reference_date = financial_date)
        local_stop_date = addToDate(next_date, month = stop_remaining_months)
        stop_remaining_annuities = getBissextilCompliantYearFraction(from_date = next_date,
                                                                     to_date   = local_stop_date,
                                                                     reference_date = financial_date)
      else:
        start_remaining_annuities = getYearFraction(months = start_remaining_months)
        stop_remaining_annuities  = getYearFraction(months = stop_remaining_months)
      
      
      if round_duration == "greater annuity":
        if start_remaining_annuities != int(start_remaining_annuities):
          start_remaining_annuities = int(start_remaining_annuities) + 1
        else:
          start_remaining_annuities = int(start_remaining_annuities)
      elif round_duration == "lower annuity":
        start_remaining_annuities = int(start_remaining_annuities)
      
      # Get specific parameters
      specific_parameter_dict = {}
      for specific_parameter in specific_parameter_list:
        getter = getattr(start_movement,
                         'get' + ''.join( [capitalize(x) for x in specific_parameter.split("_")] ),
                         None
                        )
        if getter is not None:
          specific_parameter_dict[specific_parameter] = getter()

      def calculatePrice(at_date):
        # First we calculate which is the current annuity
        annuity_number = 0
        if cut_annuities:
          current_date = getClosestDate(date = financial_date,
                                        target_date = start_date,
                                        precision = "year",
                                        before = 0)
          if getIntervalBetweenDates(current_date, start_date, keys={'day':1})['day'] == 0:
            current_date = addToDate(current_date, year=+1)
        else:
          current_date = addToDate(start_date, year=1)
        while current_date - at_date < 0:
          annuity_number += 1
          current_date = addToDate(current_date, year=1)
        annuity_start_date = addToDate(current_date, year=-1)
        annuity_stop_date = current_date
        current_annuity_stop_date = annuity_stop_date
        current_annuity_start_date = annuity_start_date
        if stop_date < annuity_stop_date:
          current_annuity_stop_date = stop_date
        if start_date > annuity_start_date:
          current_annuity_start_date = start_date

        # Get the current ratio
        current_ratio = self.restrictedTraverse(amortisation_method).ratioCalculation(
                                            start_remaining_annuities  = start_remaining_annuities
                                           ,stop_remaining_annuities   = stop_remaining_annuities
                                           ,current_annuity            = annuity_number
                                           ,start_remaining_durability = start_durability 
                                           ,stop_remaining_durability  = stop_durability
                                           ,**specific_parameter_dict)
        if current_ratio is None:
          LOG("ERP5 Warning :",0,"Unable to calculate the ratio during the amortisation calculation on item %s at date %s" % (
                  repr(self), repr(at_date)))
          return None
        
        # Calculate the value at the beginning of the annuity
        annuity_start_price = depreciable_price
        if annuity_number:
          annuity_start_price = calculatePrice(annuity_start_date)
          if annuity_start_price is None:
            return None
        
        # Calculate the raw annuity value
        if price_calculation_basis == "start price":
          raw_annuity_price = depreciable_price * current_ratio
        elif price_calculation_basis == "annuity start price":
          raw_annuity_price = annuity_start_price * current_ratio
          
        # Apply the prorata temporis on the raw annuity value
        if start_date <= annuity_start_date and stop_date >= annuity_stop_date:
          annuity_value = raw_annuity_price
        else:
          if prorata_precision == 'month':
            month_value = raw_annuity_price / number_of_months_in_year
            duration = getMonthAndDaysBetween(current_annuity_start_date, current_annuity_stop_date)
            month_number = duration['month']
            day_number = duration['day']
            annuity_value = month_value * (month_number + getMonthFraction(current_annuity_stop_date, day_number))
          elif prorata_precision == 'day':
            annuity_value = raw_annuity_price * getBissextilCompliantYearFraction(current_annuity_start_date,
                                                                                  current_annuity_stop_date,
                                                                                  reference_date=financial_date)
        # Deduct the price at the given date
        returned_price = annuity_start_price - annuity_value
        if returned_price < 0:
          returned_price = 0
        return returned_price
      ### End of calculatePrice()

      calculated_price = calculatePrice(at_date)
      if calculated_price is None:
        return None
      if calculated_price < NEGLIGEABLE_PRICE:
        calculated_price = 0.
      returned_price = calculated_price + disposal_price
      
      if cached_data: self._update_data(cached_data, my_at_date, 'price', returned_price)
      if with_currency:
        return '%0.2f %s' % (returned_price, currency)
      return returned_price 
    
    security.declareProtected(Permissions.View, 'getCurrentAmortisationPrice')
    def getCurrentAmortisationPrice(self, with_currency=0, **kw):
      """ Returns the deprecated value of item at current time """
      return self.getAmortisationPrice (at_date = DateTime(), with_currency=with_currency, **kw)

    security.declareProtected(Permissions.ModifyPortalContent, 'immobilise')
    def immobilise(self, **kw):
      """ Create the immobilisation movement to immobilise the item """
      return self._createImmobilisationMovement(immobilisation_state = 1, **kw)

    security.declareProtected(Permissions.ModifyPortalContent, 'unimmobilise')
    def unimmobilise(self, **kw):
      """ Create the immobilisation movement to unimmobilise the item """
      return self._createImmobilisationMovement(immobilisation_state = 0, **kw)

    security.declareProtected(Permissions.ModifyPortalContent, '_createImmobilisationMovement')
    def _createImmobilisationMovement(self, immobilisation_state, **kw):
      """ Build a new Immobilisation Movement into the current Item """
      new_id = str(self.generateNewId())
      self.newContent(portal_type = "Immobilisation", id=new_id)
      immobilisation = self[new_id]
      immobilisation.setStopDate(DateTime())
      immobilisation.setImmobilisation(immobilisation_state)
      self.expandAmortisation()
      return 1

    security.declareProtected(Permissions.ModifyPortalContent, '_createAmortisationRule')
    def _createAmortisationRule(self):
      applied_rule_list = self.getCausalityRelatedValueList(portal_type='Applied Rule')
      my_applied_rule_list = []
      for applied_rule in applied_rule_list:
        specialise_value = applied_rule.getSpecialiseValue()
        if specialise_value is not None and specialise_value.getPortalType() == "Amortisation Rule":
          my_applied_rule_list.append(applied_rule)
          
      if len(my_applied_rule_list) == 0:
        # Create a new applied order rule (portal_rules.order_rule)
        portal_rules = getToolByName(self, 'portal_rules')
        portal_simulation = getToolByName(self, 'portal_simulation')
        my_applied_rule = portal_rules.default_amortisation_rule.constructNewAppliedRule(portal_simulation)
        # Set causality
        my_applied_rule.setCausalityValue(self)

      elif len(my_applied_rule_list) == 1:
        # Re expand the rule if possible
        my_applied_rule = my_applied_rule_list[0]
      else:
        # Delete first rules and re expand if possible
        for my_applied_rule in my_applied_rule_list[:-1]:
          my_applied_rule.aq_parent._delObject(my_applied_rule.getId())
        my_applied_rule = my_applied_rule_list[-1]

      # We are now certain we have a single applied rule
      # It is time to expand it
      my_applied_rule.expand()

    def expandAmortisation(self):
      """
      Calculate the amortisation annuities for the item
      """
      self.activate().immediateExpandAmortisation()

    def immediateExpandAmortisation(self):
      """
      Calculate the amortisation annuities for the item
      """
      self._createAmortisationRule()

    security.declareProtected(Permissions.View, 'getSectionChangeValueList')
    def getSectionChangeValueList(self, at_date=None):
      """
      Return the list of deliveries which change the item ownership
      If at_date is None, return the result for all the time
      XXX To add : a verification on delivery state ; does an item belong to
        the destination section of a delivery if this delivery is on draft state ?
      """
      def cmpfunc(a,b):
         """
         Compares the objects on their stop_date
         """
         date_a = a.getStopDate()
         date_b = b.getStopDate()
         if date_a is None and date_b is None:
           return 0
         return cmp(date_a, date_b)

      raw_list = self.getAggregateRelatedValueList()
      delivery_list = []
      for movement in raw_list:
        if movement.getPortalType() in self.getPortalMovementTypeList():
          date = movement.getStopDate()
          if date is None:
            try:
              date = movement.getParent().getStopDate()
            except:
              pass
          if date is not None and (at_date is None or date - at_date <= 0):
            current_owner = movement.getDestinationSectionValue()
            previous_owner = movement.getSourceSectionValue()
            if current_owner is None:
              try:
                current_owner = movement.getParent().getDestinationSectionValue()
              except:
                pass
            if previous_owner is None:
              try:
                previous_owner = movement.getParent().getSourceSectionValue()
              except:
                pass
            if current_owner is not None and previous_owner != current_owner:
              delivery_list.append(movement)
      delivery_list.sort(cmpfunc)
      return delivery_list


    security.declareProtected(Permissions.View, 'getSectionList')
    def getSectionList(self, at_date=None):
      """
      Return the list of successive owners of the item with
      the corresponding dates
      If at_date is None, return the result all the time
      """
      delivery_list = self.getSectionChangeValueList(at_date = at_date)
      owner_list = []
      for delivery in delivery_list:
        owner_list.append( { 'owner' : delivery.getDestinationSectionValue(), 'date' : delivery.getStopDate() } )
      return owner_list


    security.declareProtected(Permissions.View, 'getSectionValue')
    def getSectionValue(self, at_date=None):
      """
      Return the owner of the item at the given date
      If at_date is None, return the last owner without time limit
      """
      owner_list = self.getSectionList(at_date = at_date)
      if len(owner_list) > 0:
        return owner_list[-1]['owner']
      return None


    security.declareProtected(Permissions.View, 'getCurrentSectionValue')
    def getCurrentSectionValue(self):
      """
      Return the current owner of the item
      """
      return self.getSectionValue( at_date = DateTime() )


    security.declareProtected(Permissions.View, 'isUsingAmortisationMethod')
    def isUsingAmortisationMethod(self, method):
      """
      Return true if this item is using the given method
      """
      if self.getAmortisationMethod() == method:
        return 1
      return 0

    security.declareProtected(Permissions.View, 'isUsingEuLinearAmortisationMethod')
    def isUsingEuLinearAmortisationMethod(self):
      """
      Return true if this item is using this method
      """
      return self.isUsingAmortisationMethod('eu/linear')

    security.declareProtected(Permissions.View, 'isUsingFrDegressiveAmortisationMethod')
    def isUsingFrDegressiveAmortisationMethod(self):
      """
      Return true if this item is using this method
      """
      return self.isUsingAmortisationMethod('fr/degressive')

    security.declareProtected(Permissions.View, 'isUsingFrActualUseAmortisationMethod')
    def isUsingFrActualUseAmortisationMethod(self):
      """
      Return true if this item is using this method
      """
      return self.isUsingAmortisationMethod('fr/actual_use')

