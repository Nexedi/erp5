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
from Products.ERP5.Document.Amount import Amount
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.Immobilisation import Immobilisation
from Products.ERP5.Document.AmortisationRule import AmortisationRule
from Products.ERP5.ERP5Globals import movement_type_list

from DateTime import DateTime
from zLOG import LOG

INFINITESIMAL_DELAY = 0.00001


class Item(XMLObject, Amount):
    """
      Items in ERP5 are intended to provide a way to track objects
      
      XXX All constants should be first moved into central place
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

    security.declareProtected(Permissions.View, 'getImmobilisationMovementList')
    def getImmobilisationMovementList(self, from_date=None, to_date=None, sort_on="stop_date", filter_valid=1, owner_change=1, **kw):
      """ Returns a list of immobilisation movements applied to current item from date to date
          XXX Remove LOGs please
          XXX Rename using ValueList
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
      LOG('Item :', 0, 'getImmobilisationMovementList called. from_date = %s, to_date = %s, owner_change = %s' % (repr(from_date), repr(to_date), repr(owner_change)))
      immobilisation_list = []
      for immobilisation in self.contentValues(filter = { 'portal_type':'Immobilisation' } ):
        if filter_valid:
          invalid = immobilisation.isNotValid()
          LOG('Item :', 0, 'immobilisation %s ; filter_valid = 1, invalid=%s' % (repr(immobilisation), repr(invalid)))
        else:
          invalid = 0
          LOG('Item :', 0, 'immobilisation %s ; filter_valid = 0, invalid=0' % repr(immobilisation))
        if not invalid:
          LOG('Item :', 0, 'immobilisation %s is not invalid' % repr(immobilisation))
          immo_date = immobilisation.getStopDate()
          if ( to_date is None or immo_date - to_date <= 0 ) and \
             ( from_date is None or immo_date - from_date >= 0 ):
            immobilisation_list.append(immobilisation)
            LOG('Item :', 0, 'immobilisation %s appended' % repr(immobilisation))
        else:
          LOG('Item %s :' % repr(self), 0, 'Immobilisation movement %s is not valid : %s' % (repr(immobilisation), repr(invalid)))
      
      
      # Look for each change of ownership and an immobilisation movement within 1 hour
      # If found, adapt the immobilisation date to be correctly interpreted
      # If not found, and owner_change set to 1, create a context immobilisation movement
      ownership_list = self.getOwnerList(to_date)
      LOG('Item :', 0, 'ownership list at date %s = %s' % (repr(to_date), repr(ownership_list)))
      for ownership in ownership_list:
        owner_date = ownership['date']
        found_immo = None
        nearest_immo = None
        i = 0
        while i < len(immobilisation_list) and found_immo is None:
          immobilisation = immobilisation_list[i]
          my_date = immobilisation.getStopDate()
          
#           if nearest_immo is None:
#             nearest_immo = immobilisation
#           nearest_date = nearest_immo.getStopDate()
          if (my_date is not None) and (my_date - owner_date < 0) and (nearest_immo is None or nearest_immo.getStopDate() - my_date < 0):
            nearest_immo = immobilisation
          
          if (my_date is not None) and abs(owner_date - my_date) < 1/24.:
            found_immo = immobilisation
          i += 1
            
        LOG('Item :', 0, 'ownership %s... found_immo = %s, owner_change = %s, nearest_immo = %s' % (repr(ownership), repr(found_immo), repr(owner_change), repr(nearest_immo)))
        if found_immo is None and owner_change and nearest_immo is not None:
          immobilisation = nearest_immo
          if nearest_immo is not None:
            added_immo = None
            LOG('Item :', 0, 'immobilisation_list before asContext = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
            added_immo = immobilisation.asContext()
            LOG('Item :', 0, 'immobilisation_list after asContext = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
            added_immo.setStopDate(owner_date + 0.000001) # XXX constant in code
            
            
            if added_immo.getImmobilisation():
              vat = immobilisation.getVat()
              LOG('Item :', 0, 'immobilisation_list before subcall = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
              previous_value = immobilisation.getAmortisationOrDefaultAmortisationValue()
              LOG('Item :', 0, 'immobilisation_list between subcalls = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
              current_value = added_immo.getDefaultAmortisationValue(depth = depth + 1)
              LOG('Item :', 0, 'immobilisation_list after subcall = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
              
              added_immo.setInputAccount(added_immo.getOutputAccount())
              added_immo.setAmortisationValue(current_value)
              LOG('Item :', 0, 'immobilisation_list before 2nd subcall = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
              added_immo.setAmortisationDuration(added_immo.getDefaultAmortisationDuration(depth = depth + 1))
              LOG('Item :', 0, 'immobilisation_list after 2nd subcall = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
              
              added_immo.setVat( vat * current_value / previous_value )
            LOG('Item :', 0, 'immobilisation_list before append = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
            immobilisation_list.append(added_immo)
            found_immo = added_immo
            LOG('Item :', 0, 'added immobilisation %s : %s (depth %s)' % (repr(added_immo), repr(added_immo.showDict()), repr(depth)))
            LOG('Item :', 0, 'immobilisation_list = %s (depth %s)' % (repr(immobilisation_list), repr(depth)))
           
           
           
        if found_immo is not None:
          # Two cases :
          #  - An unimmobilising movement and ownership change are close :
          #        the unimmobilising movement has to be before the ownership change
          #  - An immobilising movement and ownership change are close :
          #        the immobilising movement has to be after the ownership change
          found_date = found_immo.getStopDate()
          if found_immo.getImmobilisation():
            if found_date - owner_date < 0:
              found_immo.setStopDate(owner_date + 0.00001) # XXX Is this good ?
          else:
            if found_date - owner_date > 0:
              found_immo.setStopDate(owner_date - 0.00001)
              
          
      if sort_on is not None:
        immobilisation_list.sort(cmpfunc)
      
      LOG('Item :', 0, 'returned immobilisation movement list = %s' % repr(immobilisation_list))
      return immobilisation_list
       

    security.declareProtected(Permissions.View, 'getUnfilteredImmobilisationMovementList')
    def getUnfilteredImmobilisationMovementList(self, from_date=None, to_date=None, sort_on="stop_date", owner_change=0, **kw):
      """
      Returns a list of immobilisation applied to the current item from date to date
      All of the movements are returned, not even those which are valid
          XXX Rename using ValueList
      """
      return self.getImmobilisationMovementList(from_date=from_date,
                                                to_date=to_date,
                                                sort_on=sort_on,
                                                owner_change=owner_change,
                                                filter_valid=0, **kw)
    
    
    security.declareProtected(Permissions.View, 'getPastImmobilisationMovementList')              
    def getPastImmobilisationMovementList(self, from_date=None, at_date=None, sort_on="stop_date", owner_change=1, **kw):
       """ Returns a list of immobilisation movements applied to current item before the given date, or now
          XXX Rename using ValueList
       """
       if at_date is None: at_date = DateTime()
       result = self.getImmobilisationMovementList(from_date = from_date,
                                                   to_date = at_date,
                                                   sort_on = sort_on,
                                                   owner_change = owner_change, **kw )
       return result

           
    security.declareProtected(Permissions.View, 'getFutureImmobilisationMovementList')
    def getFutureImmobilisationMovementList(self, to_date=None, at_date=None, sort_on="stop_date", owner_change=1, **kw):
      """ Returns a list of immobilisation movements applied to current item after the given date, or now
          XXX Rename using ValueList
      
      """
      if at_date is None: at_date = DateTime()
      result = self.getImmobilisationMovementList(from_date = at_date,
                                                  to_date = to_date,
                                                  sort_on = sort_on,
                                                  owner_change = owner_change, **kw)
      return result

     
    
    security.declareProtected(Permissions.View, 'getLastImmobilisationMovement')
    def getLastImmobilisationMovement(self, at_date=None, owner_change=1, **kw):
      """ Returns the last immobilisation movement before the given date, or now
          XXX Rename using Value
      """
      result_sql = self.getPastImmobilisationMovementList(at_date = at_date, owner_change=owner_change, **kw)
       
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
      last_immobilisation_movement = self.getLastImmobilisationMovement(at_date = at_date, owner_change=owner_change, **kw)
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
        last_immobilisation_movement = self.getLastImmobilisationMovement(at_date = at_date, **kw)
        
        if last_immobilisation_movement is not None:
          is_immobilised = last_immobilisation_movement.getImmobilisation()
        
      else:
        past_immobilisation_movement_list = self.getPastImmobilisationMovementList(at_date = DateTime(), **kw)
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
        my_at_date = at_date - INFINITESIMAL_DELAY
      else:
        my_at_date = at_date
      immobilisation_movements = self.getPastImmobilisationMovementList(at_date = my_at_date, **kw)
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
      
      immo_period_duration = immo_period_stop_date - immo_period_start_date
      remaining_time = (immo_period_remaining * 30.4375) - immo_period_duration # XXXX
      returned_value = round(remaining_time / 30.4375) # XXXX
      
      
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
      def changeDateYear(date, new_year):
        """
        Return the given date modified so that its year is new_year
        """
        if new_year is not None:
          return DateTime( str(int(new_year)) + "/" + str(date.month()) + "/" + str(date.day()) )
        else:
          return date
        
        
      def calculateProrataTemporis(annuity_duration=0, raw_annuity_value=0, amortisation_type='degressive', immo_period_stop_date=None, immo_period_start_date=None, financial_date=None):
        """
        Returns the value of the annuity respecting to the amortisation
        duration during this annuity.
        For linear amortisation, immo_period_start_date and immo_period_stop_date
        are absolutely needed
        
        XXX Please define a generic function which calculates number of months
        between 2 dates according to fiscal rules
        
        XXX Please put duration calculation code oustide calculation - such 
        methods might be useful in other places and might be different 
        from one fiscal system to another
        """
        if (immo_period_stop_date is not None) and (immo_period_start_date is not None):
          annuity_duration = immo_period_stop_date - immo_period_start_date
        
        if amortisation_type == 'degressive':
          month_value = raw_annuity_value / 12. # XXX  Same code seems repeated many times 
          month_number = round(annuity_duration / 30.4375,1)
          if abs(month_number - round(month_number)) <= 0.15:
            month_number = round(month_number)
          else:
            month_number = int(month_number)
          
          # days_remaining should always be 0
          days_remaining = int(annuity_duration - month_number * 30.4375)
          if days_remaining < 3:
            days_remaining = 0
        
          annuity_value = month_value * month_number + (raw_annuity_value * days_remaining / 365.25)
          return annuity_value
        
        else:
          # Linear amortisation : it is calculated on days,
          # unlike degressive amortisation which is calculated on months
          # immo_period_stop_date, financial_date AND immo_period_start_date MUST NOT be None
          years = 0
          current_date = changeDateYear(financial_date, immo_period_start_date.year())
          if current_date - immo_period_start_date < 0:
            current_date = changeDateYear(current_date, current_date.year() + 1)
          if immo_period_stop_date - current_date < 0:
            current_date = immo_period_stop_date
          annuity_duration = round(current_date - immo_period_start_date)
          
          current_date = changeDateYear(current_date, current_date.year() + 1)
          while immo_period_stop_date - current_date >= 0:
            years += 1
            current_date = changeDateYear(current_date, current_date.year() + 1)
          
          current_date = changeDateYear(current_date, current_date.year() - 1)
          annuity_duration += round(immo_period_stop_date - current_date)
          
          prorata_temporis = annuity_duration / 365.
          LOG('Item :', 0, 'prorata_temporis = %s, annuity_duration = %s, start_date=%s, stop_date=%s' % (repr(prorata_temporis), repr(annuity_duration), repr(immo_period_start_date), repr(immo_period_stop_date)))
          if abs(prorata_temporis - 1.) < .003: prorata_temporis = 1.
          annuity_value = (years + prorata_temporis) * raw_annuity_value
          return annuity_value
          

      if at_date is None:
        at_date = DateTime()
      # Find the latest movement whose immobilisation is true
      if from_immobilisation:
        # We need to exclude the immobilisation movement which calls currently the method,
        # unless the method will never end
        my_at_date = at_date - 0.00001
      else:
        my_at_date = at_date
        
      immobilisation_movements = self.getPastImmobilisationMovementList(at_date = my_at_date, **kw)
      
      length = len(immobilisation_movements)
      i = length - 1
      while i >= 0 and not immobilisation_movements[i].getImmobilisation():
        i -= 1
        
      if i < 0:
        # Neither of past immobilisation movements did immobilise the item...
        LOG ('ERP5 Warning :',0,'Neither of past immobilisation movements did immobilise the item %s' % self.getTitle())
        if length > 0:
          returned_value = immobilisation_movements[-1].getAmortisationOrDefaultAmortisationValue()
          if with_currency:
            return '%s %s' % (repr(returned_value), immobilisation_movements[-1].getCurrency())
          return returned_value
        return None # XXX How to find the buy value ?
      
      
      # Find the latest immobilisation period and gather information
      start_movement = immobilisation_movements[i]
      currency = start_movement.getCurrency()
      if currency is not None:
        currency = currency.split('/')[-1]
      immo_period_start_date = start_movement.getStopDate()
      if i >= len(immobilisation_movements) - 1:
        # Item is currently in an amortisation period
        immo_period_stop_date = at_date
      else:
        stop_movement = immobilisation_movements[i+1]
        immo_period_stop_date = stop_movement.getStopDate()
     
      start_value = start_movement.getAmortisationOrDefaultAmortisationValue()
      immo_period_remaining_months = start_movement.getAmortisationOrDefaultAmortisationDuration()
      immo_period_remaining = immo_period_remaining_months * 30.4375
      raw_immo_period_duration = immo_period_stop_date - immo_period_start_date
      immo_period_duration = round( (raw_immo_period_duration) / 365.25, 2 ) * 365.25
      
      organisation = start_movement.getOrganisation()
      LOG('Item :', 0, 'organisation for item %s on date %s is %s' % (repr(self), repr(immo_period_start_date), repr(organisation)))
      financial_date = organisation.getFinancialYearEndDate()
        
      
      # Calculate the amortisation value
      amortisation_type = start_movement.getAmortisationType()
      if amortisation_type == "linear":
        # Linear amortisation prorata temporis calculation is made on a number of days
        # unlike degressive amortisation, made on a number of months
        raw_annuity_value = start_value / (immo_period_remaining_months / 12.)
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
        # Degressive amortisation is made on entire annuities, unless the first.
        # So, saying we immobilise on 114 months as degressive amortisation is meaningless :
        # in fact, we immobilise on 120 months.
        # So we need to round the remaining period to the just greater entire year
        # Normally, since amortisation is made as soon as the item acquisition for degressive
        # amortisation, the immobilisation can not be stopped and restarted.
        # However, if we immobilised the item during an incomplete year before, we also round the
        # remaining period of immobilisation
        if int(immo_period_remaining_months / 12) != immo_period_remaining_months / 12.:
          immo_period_remaining = ( int(immo_period_remaining/365.25) + 1 ) * 365.25
          immo_period_remaining_months = (int(immo_period_remaining_months / 12) + 1) * 12
          
          
        # Degressive amortisation is taken in account on months, and not on days.
        # So we need to adjust the immobilisation period start and stop date so that
        # they are at the beginning of a month (a month of financial year - i.e. if
        # the financial year date end is March 15th, immobilisation start date is fixed
        # to previous 15th, and immobilisation stop date is fixed to next 15th
        
        financial_day = financial_date.day()
        start_day = immo_period_start_date.day()
        stop_day = immo_period_stop_date.day()
        fiscal_coef = start_movement.getFiscalCoefficient()
        
        if start_day != financial_day:
          if start_day > financial_day:
            immo_period_start_date = immo_period_start_date - (start_day - 1)
          start_month = immo_period_start_date.month()
          start_year = immo_period_start_date.year()
          immo_period_start_date = DateTime(str(start_year) + '/' + str(start_month) + '/' + str(financial_day))
          
        if stop_day != financial_day:
          if stop_day > financial_day:
            immo_period_stop_date = immo_period_stop_date + (32 - stop_day)
          stop_month = immo_period_stop_date.month()
          stop_year = immo_period_stop_date.year()
          immo_period_stop_date = DateTime(str(stop_year) + '/' + str(stop_month) + '/' + str(financial_day))
        raw_immo_period_duration = immo_period_stop_date - immo_period_start_date
        immo_period_duration = round( (raw_immo_period_duration) / 365.25, 2 ) * 365.25
        
        # Get the first financial end date before the beginning of the immobilisation period
        if financial_date is None:
          LOG('ERP5 Warning :', 100, 'Organisation object "%s" has no financial date.' % (repr(organisation.getTitle()),))
          return None
        financial_date = changeDateYear(financial_date, immo_period_start_date.year())
        if DateTime(financial_date.Date()) - DateTime(immo_period_start_date.Date()) > 0:
          financial_date = changeDateYear(financial_date, financial_date.year()-1)
          
        first_financial_date = financial_date
        financial_date = changeDateYear(financial_date, financial_date.year()+1)
        is_last_amortisation_period = 0
          
        
        # Get the last financial date before the end of the immobilisation period.
        # Since we are in degressive amortisation, the total time of annuities is less than
        # the total time of immobilisation, so we use the financial date BEFORE the end
        # of the amortisation
        last_financial_date = changeDateYear(financial_date, immo_period_stop_date.year())
        if DateTime(last_financial_date.Date()) - DateTime(immo_period_stop_date.Date()) > 0:
          last_financial_date = changeDateYear(last_financial_date, last_financial_date.year()-1)
        
        # Adjust the immobilisation period stop date and last financial date
        # if the current period exceeds the regular immobilisation period
        if last_financial_date.year() - first_financial_date.year() >= immo_period_remaining_months / 12.:
          financial_date_difference = int(immo_period_remaining_months/12)
          last_financial_date = changeDateYear(financial_date, first_financial_date.year() + financial_date_difference)
          is_last_amortisation_period = 1
          immo_period_stop_date = last_financial_date
          
        entire_annuities_duration = (last_financial_date.year() - first_financial_date.year()) * 365.25
        
        
        
        # Find the degressive coefficient
        if immo_period_remaining:
          normal_amortisation_coefficient = 365.25 / immo_period_remaining
        else:
          normal_amortisation_coefficient = 1
          
        degressive_coef = normal_amortisation_coefficient * fiscal_coef 
        
        
        # Find the duration on which we calculate amortisation
        immo_period_duration = last_financial_date - immo_period_start_date
        duration_difference = entire_annuities_duration - immo_period_duration
        if duration_difference > 0:
          if immo_period_stop_date != last_financial_date and entire_annuities_duration > 0 and not is_last_amortisation_period:
            remaining_duration = changeDateYear(last_financial_date, last_financial_date.year()+1) - immo_period_start_date
          else:
            remaining_duration = immo_period_duration
        else:
          remaining_duration = entire_annuities_duration
          
          
        # First annuity is particular since we use prorata temporis ratio
        annuities = 0  # Cumulated annuities value
        if DateTime(financial_date.Date()) - DateTime(immo_period_stop_date.Date()) < 0:
          annuity_end_date = financial_date
        else:
          annuity_end_date = immo_period_stop_date
          
        if normal_amortisation_coefficient <= round(degressive_coef, 2):
          applied_coef = degressive_coef
        else:
          applied_coef = normal_amortisation_coefficient
        
        raw_annuity_value = start_value * applied_coef
        
        
        first_annuity_duration = annuity_end_date - immo_period_start_date
        annuity_value = calculateProrataTemporis(annuity_duration=first_annuity_duration, raw_annuity_value=raw_annuity_value)
        annuities += annuity_value
        remaining_duration -= first_annuity_duration
        remaining_duration = round(remaining_duration / 365.25, 2) * 365.25 # XXX PLEASE MOVE TO GLOBALS OR BETTER
        remaining_immobilisation = immo_period_remaining - 365.25
        linear_coef = 0
        
        
        # Other annuities  
        if remaining_duration > remaining_immobilisation:
          remaining_duration = remaining_immobilisation
        if remaining_duration >= 365.25:
          while remaining_duration > 0:
            
            
            if not linear_coef:
              # Linear coef has not been set yet, so we have to check
              # if it is time to use it or not
              current_value = start_value - annuities
              linear_coef = 365.25 / remaining_immobilisation
              if linear_coef <= round(degressive_coef, 2):
                applied_coef = degressive_coef
                linear_coef = 0
              else:
                applied_coef = linear_coef
            else:
              applied_coef = linear_coef
            
            
            raw_annuity_value = current_value * applied_coef
            if remaining_duration <= 365.25:
              # It is the last annuity of the period. If we enter in this statement, it means
              # the amortisation stops, but the item is not fully amortised
              my_financial_date = changeDateYear(last_financial_date, last_financial_date.year()-1)
              annuity_duration = immo_period_stop_date - my_financial_date
              if annuity_duration > 366:
                annuity_duration = immo_period_stop_date - last_financial_date
              annuity_value = calculateProrataTemporis(annuity_duration=annuity_duration, raw_annuity_value=raw_annuity_value)
            else:
              annuity_value = raw_annuity_value
            
            annuities += annuity_value
            remaining_duration -= 365.25
            remaining_immobilisation -= 365.25
            
        
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

    
    
    security.declareProtected(Permissions.ModifyPortalContent, '_createAmortisationSimulation')      
    def _createAmortisationSimulation(self):
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
          #my_applied_rule.flushActivity(invoke=0)  XXX FORBIDDEN, now we use hasActivity to verify,
                                                  # but we don't flush
          my_applied_rule.aq_parent._delObject(my_applied_rule.getId())
        my_applied_rule = my_applied_rule_list[-1]
        
      # We are now certain we have a single applied rule
      # It is time to expand it
      LOG('Item :',0, 'expanding applied rule %s... causality=%s' % (repr(my_applied_rule), repr(my_applied_rule.getCausalityValue())))
      LOG('Item :',0, 'item %s : causality related value list = %s' % (repr(self), repr(self.getCausalityRelatedValueList())))
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
      self._createAmortisationSimulation()
      
      
    
    security.declareProtected(Permissions.View, 'getOwnershipChangeList')
    def getOwnershipChangeList(self, at_date=None):
      """
      Return the list of deliveries which change the item ownership
      If at_date is None, return the result for all the time
      XXX To add : a verification on delivery state 
      XXX JPS : please explain in detail above XXX
      XXX PLease rename to getSectionChangeList or getSectionChangeValueList            
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
      LOG('Item.getOwnershipChangeList :', 0, "raw_list = %s" % repr(raw_list))
      delivery_list = []
      for movement in raw_list:
        if movement.getPortalType() in movement_type_list:
          date = movement.getStopDate()
          if date is None:
            try:
              date = movement.getParent().getStopDate()
            except:
              pass
          LOG('Item.getOwnershipChangeList :', 0, 'movement %s, date is %s (at_date=%s)' % (repr(movement), repr(date), repr(at_date)))
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
            
            LOG('Item :', 0, 'ownership... current_owner = %s, previous_owner = %s' % (repr(current_owner), repr(previous_owner)))
            if current_owner is not None and previous_owner != current_owner:
              delivery_list.append(movement)
              
      delivery_list.sort(cmpfunc)
      
      return delivery_list
        
    
    
    security.declareProtected(Permissions.View, 'getOwnerList')
    def getOwnerList(self, at_date=None):
      """
      Return the list of successive owners of the item with
      the corresponding dates
      If at_date is None, return the result all the time
      
      XXX getSectionValueList
      """
      delivery_list = self.getOwnershipChangeList(at_date = at_date)
      
      owner_list = []
      for delivery in delivery_list:
        owner_list.append( { 'owner' : delivery.getDestinationSectionValue(), 'date' : delivery.getStopDate() } )
        
      LOG('Item :', 0, 'owner list at date %s = %s' % (repr(at_date), repr(owner_list)))
      return owner_list
            
            
    security.declareProtected(Permissions.View, 'getOwner')
    def getOwner(self, at_date=None):
      """
      Return the owner of the item at the given date
      If at_date is None, return the last owner without time limit
      
      XXX getSectionValue
      """
      owner_list = self.getOwnerList(at_date = at_date)
      
      if len(owner_list) > 0:
        LOG('Item :', 0, 'owner at date %s is %s' % (repr(at_date), repr(owner_list[-1]['owner'])))
        return owner_list[-1]['owner']
      else:
        return None
    
      
        
    security.declareProtected(Permissions.View, 'getCurrentOwner')
    def getCurrentOwner(self):
      """
      Return the current owner of the item
      
      XXX getCurrentSectionValue
      """
      return self.getOwner( at_date = DateTime() )
