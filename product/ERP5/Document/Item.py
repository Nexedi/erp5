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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.DateUtils import addToDate, getClosestDate, getIntervalBetweenDates, roundMonthToGreaterEntireYear
from Products.ERP5Type.DateUtils import getMonthAndDaysBetween, getCompletedMonthBetween, getRoundedMonthBetween
from Products.ERP5Type.DateUtils import getMonthFraction, getYearFraction, getDecimalNumberOfYearsBetween
from Products.ERP5Type.DateUtils import same_movement_interval, number_of_months_in_year, centis, millis
from Products.ERP5.Document.Amount import Amount
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.Immobilisation import Immobilisation
#from Products.ERP5.Document.AmortisationRule import AmortisationRule

from zLOG import LOG

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

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Items in ERP5 are intended to provide a way to track objects."""
         , 'icon'           : 'item_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addItem'
         , 'immediate_view' : 'item_edit'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'item_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'item_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_edit'
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

    security.declareProtected(Permissions.ModifyPortalContent,'generateNewId')
    def generateNewId(self, id_group='item_id_group', default=None, method=None):
      """
      We want a different id for all Item
      """
      return XMLObject.generateNewId(self, id_group=id_group, default=default, method=method)



    ### Amortisation
    security.declareProtected(Permissions.View, 'getImmobilisationMovementValueList')
    def getImmobilisationMovementValueList(self, from_date=None, to_date=None, sort_on="stop_date", filter_valid=1, owner_change=1, **kw):
      """
      Returns a list of immobilisation movements applied to current item from date to date
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

        value_a = access_a()
        value_b = access_b()

        if value_a is None and value_b is None:
          return 0

        if value_a is None or value_a < value_b:
          return -1
        if value_b is None or value_b < value_a:
          return 1
        return 0

      depth = kw.get('depth', None)
      if depth is None: depth = 0
      immobilisation_list = []
      for immobilisation in self.contentValues(filter = { 'portal_type':'Immobilisation' } ):
        LOG('Item, immobilisation.checkConsistency',0,immobilisation.checkConsistency())
        if filter_valid:
          invalid = immobilisation._checkConsistency() #
        else:
          invalid = 0
        if not invalid:
          immo_date = immobilisation.getStopDate()
          if ( to_date is None or immo_date - to_date <= 0 ) and \
             ( from_date is None or immo_date - from_date >= 0 ):
            immobilisation_list.append(immobilisation)
      LOG('Item.immobilisation_list',0,immobilisation_list)

      # Look for each change of ownership and an immobilisation movement within 1 hour
      # If found, adapt the immobilisation date to be correctly interpreted
      # If not found, and owner_change set to 1, create a context immobilisation movement
      ownership_list = self.getSectionList(to_date)
      for ownership in ownership_list:
        owner_date = ownership['date']
        found_immo = None
        nearest_immo = None
        i = 0
        while i < len(immobilisation_list) and found_immo is None:
          immobilisation = immobilisation_list[i]
          my_date = immobilisation.getStopDate()

          if (my_date is not None) and (my_date - owner_date < 0) and (nearest_immo is None or nearest_immo.getStopDate() - my_date < 0):
            nearest_immo = immobilisation

          if (my_date is not None) and abs(owner_date - my_date) < same_movement_interval:
            found_immo = immobilisation
          i += 1

        if found_immo is None and owner_change and nearest_immo is not None:
          immobilisation = nearest_immo
          if nearest_immo is not None:
            added_immo = None
            added_immo = immobilisation.asContext()
            added_immo.setStopDate(owner_date + millis)


            if added_immo.getImmobilisation():
              vat = immobilisation.getVat()
              previous_value = immobilisation.getAmortisationOrDefaultAmortisationPrice()
              current_value = added_immo.getDefaultAmortisationPrice(depth = depth + 1)

              added_immo.setInputAccount(added_immo.getOutputAccount())
              added_immo.setAmortisationBeginningPrice(current_value)
              added_immo.setAmortisationDuration(added_immo.getDefaultAmortisationDuration(depth = depth + 1))

              added_immo.setVat( vat * current_value / previous_value )
            immobilisation_list.append(added_immo)
            found_immo = added_immo

        if found_immo is not None:
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
      result_sql = self.getPastImmobilisationMovementValueList(at_date = at_date, owner_change=owner_change, **kw)

      result = None
      if len(result_sql) > 0:
        result = result_sql[-1]
      return result



    security.declareProtected(Permissions.View, 'getLastMovementAmortisationDuration')
    def getLastMovementAmortisationDuration(self, at_date=None, owner_change=1, **kw):
      """
        Returns total duration of amortisation for the item.
        It is the theorical lifetime of this type of item.
      """
      last_immobilisation_movement = self.getLastImmobilisationMovementValue(at_date = at_date, owner_change=owner_change, **kw)
      if last_immobilisation_movement is not None:
        return last_immobilisation_movement.getAmortisationOrDefaultAmortisationDuration()
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
      """ Returns true if the item is immobilised at the given date.
          If at_date = None, returns true if the item has ever been immobilised."""

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
      immobilisation_movements = self.getPastImmobilisationMovementValueList(at_date = my_at_date, **kw)
      i = len(immobilisation_movements) - 1
      while i >= 0 and not immobilisation_movements[i].getImmobilisation():
        i -= 1

      if i < 0:
        # Neither of past immobilisation movements did immobilise the item...
        duration = self.getLastMovementAmortisationDuration(at_date=my_at_date)
        if duration is not None:
          return int(duration)
        return None


      start_movement = immobilisation_movements[i]
      if i > len(immobilisation_movements) - 2:
        # Item is currently in an amortisation period
        immo_period_stop_date = at_date
      else:
        stop_movement = immobilisation_movements[i+1]
        immo_period_stop_date = stop_movement.getStopDate()


      immo_period_start_date = start_movement.getStopDate()
      immo_period_remaining = start_movement.getAmortisationOrDefaultAmortisationDuration()

      immo_period_duration = getRoundedMonthBetween(immo_period_start_date, immo_period_stop_date)
      returned_value = immo_period_remaining - immo_period_duration

      if returned_value < 0:
        returned_value = 0
      return int(returned_value)



    security.declareProtected(Permissions.View, 'getAmortisationPrice')
    def getAmortisationPrice(self, at_date=None, from_immobilisation=0, with_currency=0, **kw):
      """
      Returns the deprecated value of item at given date, or now.

      If from_immobilisation is set, we don't take the very last immobilisation movement
      at the date. It is needed if the function is called by this particular movement, unless
      the function will never end.

      If with_currency is set, returns a string containing the value and the corresponding currency.
      """
      def calculateProrataTemporis(immo_period_start_date, immo_period_stop_date, raw_annuity_value=0, amortisation_type='degressive', financial_date=None):
        """
        Returns the value of the annuity respecting to the amortisation
        duration during this annuity.
        """
        if amortisation_type == 'degressive':
          month_value = raw_annuity_value / number_of_months_in_year
          duration = getMonthAndDaysBetween(immo_period_start_date, immo_period_stop_date)
          month_number = duration['month']
          day_number = duration['day']

          annuity_value = month_value * (month_number + getMonthFraction(immo_period_stop_date, day_number))
          return annuity_value

        else:
          # Linear amortisation : it is calculated on days,
          # unlike degressive amortisation which is calculated on months
          return getDecimalNumberOfYearsBetween(immo_period_start_date, immo_period_stop_date, financial_date) * raw_annuity_value

      if at_date is None:
        at_date = DateTime()
      # Find the latest movement whose immobilisation is true
      if from_immobilisation:
        # We need to exclude the immobilisation movement which calls currently the method,
        # unless the method will never end
        my_at_date = at_date - centis
      else:
        my_at_date = at_date
      immobilisation_movements = self.getPastImmobilisationMovementValueList(at_date = my_at_date, **kw)

      length = len(immobilisation_movements)
      i = length - 1
      while i >= 0 and not immobilisation_movements[i].getImmobilisation():
        i -= 1

      if i < 0:
        # Neither of past immobilisation movements did immobilise the item...
        LOG ('ERP5 Warning :',0,'Neither of past immobilisation movements did immobilise the item %s' % self.getTitle())
        if length > 0:
          returned_value = immobilisation_movements[-1].getAmortisationOrDefaultAmortisationPrice()
          if with_currency:
            return '%s %s' % (repr(returned_value), immobilisation_movements[-1].getPriceCurrency())
          return returned_value
        return None # XXX How to find the buy value ?


      # Find the latest immobilisation period and gather information
      start_movement = immobilisation_movements[i]
      currency = start_movement.getPriceCurrency()
      if currency is not None:
        currency = currency.split('/')[-1]
      immo_period_start_date = start_movement.getStopDate()
      if i >= len(immobilisation_movements) - 1:
        # Item is currently in an amortisation period
        immo_period_stop_date = at_date
      else:
        stop_movement = immobilisation_movements[i+1]
        immo_period_stop_date = stop_movement.getStopDate()

      start_value = start_movement.getAmortisationOrDefaultAmortisationPrice()
      immo_period_remaining_months = start_movement.getAmortisationOrDefaultAmortisationDuration()

      section = start_movement.getSectionValue()
      financial_date = section.getFinancialYearStopDate()

      # Calculate the amortisation value
      amortisation_type = start_movement.getAmortisationType()
      if amortisation_type == "linear":
        # Linear amortisation prorata temporis calculation is made on a number of days
        # unlike degressive amortisation, made on a number of months
        raw_annuity_value = start_value / (immo_period_remaining_months / number_of_months_in_year)
        annuity_value = calculateProrataTemporis(raw_annuity_value=raw_annuity_value,
                                                 amortisation_type='linear',
                                                 immo_period_stop_date=immo_period_stop_date,
                                                 immo_period_start_date=immo_period_start_date,
                                                 financial_date=financial_date)
        new_value = start_value - annuity_value
        if new_value < 0:
          new_value = 0
        if with_currency:
          return '%s %s' % (repr(round(new_value,2)), currency)
        return round(new_value,2)


      elif amortisation_type == "degressive":
        if financial_date is None:
          LOG('ERP5 Warning :', 100, 'Organisation object "%s" has no financial date.' % (repr(section.getTitle()),))
          return None

        # Degressive amortisation is made on entire annuities, unless the first.
        # So, saying we immobilise on 114 months as degressive amortisation is meaningless :
        # in fact, we immobilise on 120 months.
        # So we need to round the remaining period to the just greater entire year
        # Normally, since amortisation is made as soon as the item acquisition for degressive
        # amortisation, the immobilisation can not be stopped and restarted.
        # However, if we immobilised the item during an incomplete year before, we also round the
        # remaining period of immobilisation
        immo_period_remaining_months = roundMonthToGreaterEntireYear(immo_period_remaining_months)

        # Degressive amortisation is taken in account on months, and not on days.
        # So we need to adjust the immobilisation period start and stop date so that
        # they are at the beginning of a month (a month of financial year - i.e. if
        # the financial year date end is March 15th, immobilisation start date is fixed
        # to previous 15th, and immobilisation stop date is fixed to next 15th
        immo_period_start_date = getClosestDate(target_date=immo_period_start_date, date=financial_date, precision='month')
        immo_period_stop_date = getClosestDate(target_date=immo_period_stop_date, date=financial_date, precision='month', before=0)
        # Get the first financial end date before the beginning of the immobilisation period
        # and the last financial date after the end of the immobilisation period.
        first_financial_date = getClosestDate(target_date=immo_period_start_date, date=financial_date, precision='year')
        last_financial_date = getClosestDate(target_date=immo_period_stop_date, date=financial_date, precision='year', before=0)
        is_last_amortisation_period = 0

        # Adjust the immobilisation period stop date and last financial date
        # if the current period exceeds the regular immobilisation period
        month_difference = getIntervalBetweenDates(first_financial_date, last_financial_date, {'month':1} )['month']
        if month_difference >= immo_period_remaining_months:
          last_financial_date = addToDate(last_financial_date, {'month':immo_period_remaining_months} )
          is_last_amortisation_period = 1
          immo_period_stop_date = last_financial_date

        #entire_annuities_duration = (last_financial_date.year() - first_financial_date.year()) * 365.25

        # Find the degressive coefficient
        fiscal_coef = start_movement.getFiscalCoefficient()
        normal_amortisation_coefficient = 1./ getYearFraction(first_financial_date, months=immo_period_remaining_months)
        degressive_coef = normal_amortisation_coefficient * fiscal_coef

        annuities = 0  # Cumulated annuities value
        if getIntervalBetweenDates(first_financial_date, last_financial_date, {'day':1})['day'] > 0:
          # First annuity is particular since we use prorata temporis ratio
          second_financial_date = addToDate(first_financial_date, {'year':1})
          if getIntervalBetweenDates(immo_period_stop_date, second_financial_date, {'days':1}) < 0:
            annuity_end_date = immo_period_stop_date
          else:
            annuity_end_date = second_financial_date
          if normal_amortisation_coefficient <= round(degressive_coef, 2):
            applied_coef = degressive_coef
          else:
            applied_coef = normal_amortisation_coefficient
          raw_annuity_value = start_value * applied_coef

          annuity_value = calculateProrataTemporis(immo_period_start_date, annuity_end_date, raw_annuity_value=raw_annuity_value)
          annuities += annuity_value
          linear_coef = 0
          current_financial_date = second_financial_date


          # Other annuities
          while current_financial_date < last_financial_date:
            remaining_months = immo_period_remaining_months - getIntervalBetweenDates(first_financial_date,
                               current_financial_date, {'month':1})['month']
            if not linear_coef:
              # Linear coef has not been set yet, so we have to check
              # if it is time to use it or not
              current_value = start_value - annuities
              linear_coef = 1./ getYearFraction(last_financial_date, months=remaining_months)
              if linear_coef <= round(degressive_coef, 2):
                applied_coef = degressive_coef
                linear_coef = 0
              else:
                applied_coef = linear_coef
            else:
              applied_coef = linear_coef

            raw_annuity_value = current_value * applied_coef
            if (not is_last_amortisation_period) and \
                  getIntervalBetweenDates(current_financial_date, last_financial_date, {'year':1} )['year'] == 1:
              # It is the last annuity of the period. If we enter in this statement, it means
              # the amortisation stops, but the item is not fully amortised
              annuity_value = calculateProrataTemporis(current_financial_date,immo_period_stop_date,raw_annuity_value=raw_annuity_value)
            else:
              annuity_value = raw_annuity_value

            annuities += annuity_value
            current_financial_date = addToDate(current_financial_date, {'year':1} )

        # Return the calculated value
        returned_value = start_value - annuities
        if returned_value < 0:
          returned_value = 0.
        if with_currency:
          return '%s %s' % (repr(round(returned_value, 2)), currency)
        return round(returned_value,2)

      else:
        # Unknown amortisation type
        LOG('ERP5 Warning :', 0, 'Unknown amortisation type. (%s)' % (repr(amortisation_type),))
        return None

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
      my_applied_rule_list = self.getCausalityRelatedValueList(portal_type='Applied Rule')
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

         if date_a is None or date_a < date_b:
           return -1
         if date_b is None or date_b < date_a:
           return 1
         return 0


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
      else:
        return None

    security.declareProtected(Permissions.View, 'getCurrentSectionValue')
    def getCurrentSectionValue(self):
      """
      Return the current owner of the item
      """
      return self.getSectionValue( at_date = DateTime() )
