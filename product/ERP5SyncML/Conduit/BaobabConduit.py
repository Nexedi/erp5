##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kevin Deldycke <kevin@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import convertToUpperCase
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_inner, aq_chain, aq_acquire

from xml.dom import implementation
from xml.dom.ext import PrettyPrint
from xml.dom import Node

import random
import datetime
from cStringIO import StringIO

from zLOG import LOG



class BaobabConduit(ERP5Conduit):

  global property_map

  # Declarative security
  security = ClassSecurityInfo()


  # This data structure associate a xml property to an ERP5 object property in certain conditions
  property_map = \
    [ { 'xml_property' : 'nom'
      , 'erp5_property': 'first_name'
      , 'conditions'   : {'erp5_portal_type':'Person'}
      }
    , { 'xml_property' : 'nom'
      , 'erp5_property': 'title'
      , 'conditions'   : {'erp5_portal_type':'Organisation'}
      }
    , { 'xml_property' : 'adresse'
      , 'erp5_property': 'default_address_street_address'
      , 'conditions'   : [{'erp5_portal_type':'Organisation'}
                         ,{'erp5_portal_type':'Person'}]
      }
    , { 'xml_property' : 'zone_residence'
      , 'erp5_property': 'default_address_region'
      , 'conditions'   : [{'erp5_portal_type':'Organisation'}
                         ,{'erp5_portal_type':'Person'}]
      }
    , { 'xml_property' : 'titre'
      , 'erp5_property': 'prefix'
      , 'conditions'   : {'erp5_portal_type':'Person'}
      }
    , { 'xml_property' : 'telephone'
      , 'erp5_property': 'default_telephone_number'
      , 'conditions'   : [{'erp5_portal_type':'Organisation'}
                         ,{'erp5_portal_type':'Person'}]
      }
    , { 'xml_property' : 'telex'
      , 'erp5_property': 'default_fax_number'
      , 'conditions'   : [{'erp5_portal_type':'Organisation'}
                         ,{'erp5_portal_type':'Person'}]
      }
    , { 'xml_property' : 'prenom'
      , 'erp5_property': 'last_name'
      , 'conditions'   : {'erp5_portal_type':'Person'}
      }
    , { 'xml_property' : 'date_naissance'
      , 'erp5_property': 'birthday'
      , 'conditions'   : {'erp5_portal_type':'Person'}
      }
    , { 'xml_property' : 'code_bic'
      , 'erp5_property': 'bic_code'
      , 'conditions'   : {'erp5_portal_type':'Organisation'}
      }

    , { 'xml_property' : 'intitule'
      , 'erp5_property': 'title'
      , 'conditions'   : {'erp5_portal_type':'Bank Account'}
      }

    , { 'xml_property' : 'montant_maxi'
      , 'erp5_property': 'operation_upper_limit'
      , 'conditions'   : {'erp5_portal_type':'Agent Privilege'}
      }
    , { 'xml_property' : 'description'
      , 'erp5_property': 'description'
      , 'conditions'   : {'erp5_portal_type':'Agent Privilege'}
      }

    , { 'xml_property' : 'inventory_title'
      , 'erp5_property': 'title'
      , 'conditions'   : {'erp5_portal_type':'Cash Inventory'}
      }
    ]

  """
    Methods below are tools to use the property_map.
  """

  security.declarePrivate('buildConditions')
  def buildConditions(self, object):
    """
      Build a condition dictionnary
    """
    dict = {}
    dict['erp5_portal_type'] = object.getPortalType()
    return dict

  security.declarePrivate('findPropertyMapItem')
  def findPropertyMapItem(self, xml_property_name, conditions):
    """
      Find the property_map item that match conditions
    """
    for item in property_map:
      if item['xml_property'] == xml_property_name:
        c = item['conditions']
        if type(c) == type([]):
          if conditions in c:
            return item
        else:
          if conditions == c:
            return item
    return None



  security.declareProtected(Permissions.ModifyPortalContent, 'constructContent')
  def constructContent(self, object, object_id, docid, portal_type):
    """
      This is a redefinition of the original ERP5Conduit.constructContent function to create Baobab objects
    """
    erp5_site_path = object.absolute_url(relative=1)
    person_module         = object.restrictedTraverse(erp5_site_path + '/person')
    organisation_module   = object.restrictedTraverse(erp5_site_path + '/organisation')
    cash_inventory_module = object.restrictedTraverse(erp5_site_path + '/cash_inventory_module')
    currency_cash_module  = object.restrictedTraverse(erp5_site_path + '/currency_cash_module')

    subobject = None

    # Function to search the parent object where the new content must be construct
    # Given parameter is the special encoded portal type that represent the path to the wanted destination
    def findObjectFromSpecialPortalType(special_portal_type):
      source_portal_type = special_portal_type.split('_')[0]
      construction_location = '/'.join(special_portal_type.split('_')[1:][::-1])
      parent_object = None
      for search_folder in ('person', 'organisation'):
        path = '/' + search_folder + '/' + construction_location
        try:
          parent_object = object.restrictedTraverse(erp5_site_path + path)
        except:
          LOG('BaobabConduit:', 100, "parent object of '%s' not found in %s" % (source_portal_type, erp5_site_path + path))
      if parent_object == None:
        LOG('BaobabConduit:', 100, "parent object of '%s' not found !" % (source_portal_type))
      else:
        LOG('BaobabConduit:', 0,"parent object of '%s' found (%s)" % (source_portal_type, repr(parent_object)))
      return parent_object

    # handle client objects
    if portal_type.startswith('Client'):
      if portal_type[-3:] == 'PER':
        subobject = person_module.newContent( portal_type = 'Person'
                                            , id          = object_id
                                            )
        subobject.setCareerRole('client')
      else:
        subobject = organisation_module.newContent( portal_type = 'Organisation'
                                                  , id          = object_id
                                                  )
        subobject.setRole('client')

    # handle bank account objects
    elif portal_type.startswith('Compte'):
      owner = findObjectFromSpecialPortalType(portal_type)
      if owner == None: return None
      subobject = owner.newContent( portal_type = 'Bank Account'
                                  , id          = object_id
                                  )
      # set the bank account owner as agent with no-limit privileges (only for persons)
      if owner.getPortalType() == 'Person':
        new_agent = subobject.newContent( portal_type = 'Agent'
                                        , id          = 'owner'
                                        )
        new_agent.setAgent(owner.getRelativeUrl())
        privileges = ( 'circularization'
                     , 'cash_out'
                     , 'withdrawal_and_payment'
                     , 'account_document_view'
                     , 'signature'
                     , 'treasury'
                     )
        for privilege in privileges:
          new_priv = new_agent.newContent(portal_type = 'Agent Privilege')
          new_priv.setAgentPrivilege(privilege)

    # handle agent objects
    elif portal_type.startswith('Mandataire'):
      dest = findObjectFromSpecialPortalType(portal_type)
      if dest == None: return None
      subobject = dest.newContent( portal_type = 'Agent'
                                 , id          = object_id
                                 )
      # try to get the agent in the person module
      person = findObjectFromSpecialPortalType('Person_' + object_id)
      if person == None:
        person = person_module.newContent( portal_type = 'Person'
                                         , id          = object_id + 'a'
                                         )
      subobject.setAgent(person.getRelativeUrl())

    # handle privilege objects
    elif portal_type.startswith('Pouvoir'):
      dest = findObjectFromSpecialPortalType(portal_type)
      if dest == None: return None
      subobject = dest.newContent( portal_type = 'Agent Privilege'
                                 , id          = object_id
                                 )

    # handle inventory objects
    elif portal_type == 'Cash Inventory':
      if cash_inventory_module == None: return None
      subobject = cash_inventory_module.newContent( portal_type = 'Cash Inventory'
                                                  , id          = object_id
                                                  )

    # handle inventory details objects
    elif portal_type == 'Cash Inventory Detail':
      if currency_cash_module == None: return None

      ### get currency informations by analizing the id
      id_items = object_id.split('_')
      if len(id_items) != 4:
        LOG('BaobabConduit:', 100, "Cash Inventory Detail object has a wrong id (%s) !" % (object_id))
        return None
      cell_id       = id_items[0]
      resource_type = id_items[1]
      base_price    = float(id_items[2])
      currency_name = id_items[3]

      ### try to find an existing line with the same resource as the current cell
      # set the portal type of the searched object
      if resource_type in ['BIL']:
        currency_portal_type = 'Banknote'
      elif resource_type in ['MON']:
        currency_portal_type = 'Coin'
      else:
        LOG('BaobabConduit:', 100, "Cash Inventory Detail resource type can't be guess (%s) !" % (resource_type))
        return None
      # get the list of existing currency to find the currency of the line
      line_currency_cash = None
      currency_cash_list = currency_cash_module.contentValues(filter={'portal_type': currency_portal_type})
      for currency_cash in currency_cash_list:
        if currency_cash.getBasePrice()       == base_price    and \
           currency_cash.getPriceCurrencyId() == currency_name :
           line_currency_cash = currency_cash
           break
      # no currency found
      if line_currency_cash == None:
        LOG('BaobabConduit:', 100, "No currency found for the Cash Inventory Detail !")
        return None

      ### search for lines
      inventory_lines = object.contentValues(filter={'portal_type': 'Cash Inventory Line'})
      new_line = None
      for line in inventory_lines:
        if line.getResourceValue() == line_currency_cash:
          new_line = line
          break
      # no previous line found, create one
      if new_line == None:
        new_line = object.newContent( portal_type = 'Cash Inventory Line'
                                    , id          = random.randint(10000000, 99999999)
                                    )
        new_line.setResourceValue(line_currency_cash)
        new_line.setPrice(line_currency_cash.getBasePrice())
        object.setPriceCurrency(line_currency_cash.getPriceCurrency())
#         new_line.setVariationBaseCategoryList([ 'cash_status'
#                                               , 'emission_letter'
#                                               , 'variation'
#                                               ])
      subobject = new_line

    return subobject



### EXPERIMENTAL
#   security.declareProtected(Permissions.ModifyPortalContent, 'getProperty')
#   def getProperty(self, object, kw):
#     """
#     This is the default getProperty method. This method
#     can easily be overwritten.
#     """
#     # Try to find a translation rule in the property_map
#     cond = self.buildConditions(object)
#     map_item = self.findPropertyMapItem(kw, cond)
#     if map_item != None:
#       method_id = "get" + convertToUpperCase(map_item['erp5_property'])
#       LOG('BaobabConduit:',0,"try to call object method %s on %s" % (repr(method_id), repr(object)))
#       if v not in ('', None):
#         if hasattr(object, method_id):
#           method = getattr(object, method_id)
#           method(v)
#         else:
#           LOG('BaobabConduit:',100,'property map item don\'t match object properties')
#     return object.getProperty(kw)



  security.declareProtected(Permissions.ModifyPortalContent, 'editDocument')
  def editDocument(self, object=None, **kw):
    """
      This function transfer datas from the dictionary to the baobab document object given in parameters
    """

    ### EXPERIMENTAL
    # This message help to track in the log when an object is edited
    # It permit us to verify the consistency of a synchronisation process :
    #   1- Launch a normal synchronisation.
    #   2- When the syncho process is finished, launch (without reseting, it's important) an other synchronisation, the same way as above.
    #   3- Monitor the zope log.
    #   4- If the message log below appear it mean that a client piece of data is missing or wrong comparing to the master.
    #      In other words, it mean that the first synchronisation process didn't ensure the integrity of data.
    #LOG('BaobabConduit:',0, "An object need to be edited")

    if object == None: return

    # Cash Inventory Detail objects needs all properties to create the matrix
    if object.getPortalType() == 'Cash Inventory Line':
      category_list = []
      quantity = None
      cell_id  = None
      for k,v in kw.items():
        if k == 'quantity': quantity = float(v)
        if k == 'cell_id' : cell_id  = v
      # Get matrix variation values
      base_cat_map = { 'variation'  : 'variation'
                     , 'letter_code': 'emission_letter'
                     , 'status_code': 'cash_status'
                     }
      for base_key in base_cat_map.keys():
        if base_key in kw.keys() and kw[base_key] not in ('', None):
          if base_key == 'status_code':
            status_table = { 'TVA' : 'valid'
                           , 'NEE' : 'new_emitted'
                           , 'NEU' : 'new_not_emitted'
                           , 'RTC' : 'retired'
                           , 'ATR' : 'to_sort'
                           , 'MUT' : 'mutilated'
                           , 'EAV' : 'to_ventilate'
                           , 'TRC' : 'to_sort'
                           , 'ARE' : 'to_sort'
                           }
            category = status_table[kw[base_key]]
          else:
            category = kw[base_key]
        else:
          category = 'not_defined'
        category_list.append(base_cat_map[base_key] + '/' + category)

      # Update the matrix with this cell
      self.updateCashInventoryMatrix( line               = object
                                    , cell_category_list = category_list
                                    , quantity           = quantity
                                    , cell_description   = cell_id
                                    )

    # Set properties of the destination baobab object
    for k,v in kw.items():
      # Try to find a translation rule in the property_map
      cond = self.buildConditions(object)
      map_item = self.findPropertyMapItem(k, cond)
      # No translation rule found, try to find a hard-coded translation method in the conduit
      if map_item == None:
        method_id = "edit%s%s" % (kw['type'], convertToUpperCase(k))
        LOG('BaobabConduit:', 0, "try to call conduit method %s on %s" % (repr(method_id), repr(object)))
        if v not in ('', None):
          if hasattr(self, method_id):
            method = getattr(self, method_id)
            method(object, v)
          else:
            LOG('BaobabConduit:', 100, "there is no method to handle <%s>%s</%s> data" % (k,repr(v),k))

      # There is a translation rule, so call the right setProperty() method
      else:
        method_id = "set" + convertToUpperCase(map_item['erp5_property'])
        LOG('BaobabConduit:', 0, "try to call object method %s on %s" % (repr(method_id), repr(object)))
        if v not in ('', None):
          if hasattr(object, method_id):
            method = getattr(object, method_id)
            method(v)
          else:
            LOG('BaobabConduit:', 100, 'property map item don\'t match object properties')



  """
    All functions below are defined to set a document's property to a value given in parameters.
    The name of those functions are chosen to help the transfert of datas from a given XML format to standard Baobab objects.
  """

  # Client-related-properties functions
  def editClientCategorie(self, document, value):
    if document.getPortalType() == 'Organisation':
      id_table = { 'BIF': 'institution/world/bank'
                 , 'PFR': 'institution/world/institution'
                 , 'ICU': 'institution/local/common'
                 , 'BET': 'institution/local/institution'
                 , 'ETF': 'institution/local/bank'
                 , 'BTR': 'treasury/national'
                 , 'ORP': 'treasury/other'
                 , 'ORI': 'organism/international'
                 , 'ORR': 'organism/local'
                 , 'COR': 'intermediaries'
                 , 'DIV': 'depositories/various'
                 , 'DER': 'depositories/savings'
                 , 'DAU': 'depositories/other'
                 }
      document.setActivity('banking_finance/' + id_table[value])
    else:
      LOG('BaobabConduit:', 0, 'Person\'s category ignored')

  def editClientNatureEconomique(self, document, value):
    if document.getPortalType() == 'Organisation':
      # build the economical class category path
      c = ''
      path = ''
      for i in value[1:]:
        c += i
        if c == '13':
          path += '/S13'
          if value != 'S13':
            path += '/' + value
          break
        path += '/S' + c
      document.setEconomicalClass(path)
    else:
      LOG('BaobabConduit inconsistency:', 200, 'a non-Organisation client can\'t have an economical class')

  def editClientSituationMatrimoniale(self, document, value):
    if document.getPortalType() == 'Person':
      id_table = { 'VEU' : 'widowed'
                 , 'DIV' : 'divorced'
                 , 'MAR' : 'married'
                 , 'CEL' : 'never_married'
                 }
      document.setMaritalStatus(id_table[value])
    else:
      LOG('BaobabConduit inconsistency:', 200, 'a non-Person client can\'t have a marital status')



  # BankAccount-related-properties functions
  def editCompteDevise(self, document, value):
    document.setPriceCurrency('currency/' + value)

  def editCompteDateOuverture(self, document, value):
    if document.getStopDate() in ('', None):
      document.setStopDate(str(datetime.datetime.max))
    document.setStartDate(value)

  def editCompteDateFermeture(self, document, value):
    if document.getStartDate() in ('', None):
      document.setStartDate(str(datetime.datetime.min))
    document.setStopDate(value)

  def editCompteNumero(self, document, value):
    document.setBankCode(value[0])
    document.setBranch(value[1:3])
    document.setBankAccountNumber(value)



  # Agent-related-properties functions
  def editMandataireNom(self, document, value):
    old_value = document.getAgentValue().getFirstName()
    new_value = value
    if old_value != new_value:
      LOG('BaobabConduit:', 200, 'old value of agent first name (%s) was replaced by a new one (%s)' % (old_value, new_value))
      document.getAgentValue().setFirstName(new_value)

  def editMandatairePrenom(self, document, value):
    old_value = document.getAgentValue().getLastName()
    new_value = value
    if old_value != new_value:
      LOG('BaobabConduit:', 200, 'old value of agent last name (%s) was replaced by a new one (%s)' % (old_value, new_value))
      document.getAgentValue().setLastName(new_value)

  def editMandataireService(self, document, value):
    assignment = document.getAgentValue().newContent( portal_type = 'Assignment'
                                                    , id          = 'service'
                                                    )
    assignment.setGroup(value)
    return

  def editMandataireFonction(self, document, value):
    document.getAgentValue().setDefaultCareerGrade(value)
    return

  def editMandataireTelephone(self, document, value):
    old_value = document.getAgentValue().getDefaultTelephoneNumber()
    new_value = value
    if old_value != new_value:
      LOG('BaobabConduit:', 200, "old value of agent's telephone (%s) was replaced by a new one (%s)" % (old_value, new_value))
      document.getAgentValue().setDefaultTelephoneNumber(new_value)

  def editMandataireDateCreation(self, document, value):
    if document.getStopDate() in ('', None):
      document.setStopDate(str(datetime.datetime.max))
    document.setStartDate(value)



  # AgentPrivilege-related-properties functions
  def editPouvoirCategorie(self, document, value):
    id_table = { 'COM' : 'clearing'
               , 'CIR' : 'circularization'
               , 'REM' : 'cash_out'
               , 'RET' : 'withdrawal_and_payment'
               , 'RTE' : 'account_document_view'
               , 'SIG' : 'signature'
               , 'TRE' : 'treasury'
               }
    document.setAgentPrivilege(id_table[value])

  def editPouvoirDateDebut(self, document, value):
    if document.getStopDate() in ('', None):
      document.setStopDate(str(datetime.datetime.max))
    document.setStartDate(value)

  def editPouvoirDateFin(self, document, value):
    if document.getStartDate() in ('', None):
      document.setStartDate(str(datetime.datetime.min))
    document.setStopDate(value)



  # CashInventory-related-properties functions
  def editCashInventoryInventoryDate(self, document, value):
    if value in ('', None):
      date = str(datetime.datetime.max)
    else:
      # Convert french date to strandard date
      date_items = value.split('/')
      day   = date_items[0]
      month = date_items[1]
      year  = date_items[2]
      date  = '/'.join([year, month, day])
    document.setStopDate(date)



#   # CashInventoryDetail-related-properties functions
#   def editCashInventoryDetailVariation(self, document, value):
#     cell = document
#     line = document.aq_parent()
#     LOG('BaobabConduit:', 200, 'Line (%s) & Cell (%s)' % (line, cell))
#     year = value
#
#     # update line variation category list
#     line_category_list = line.getVariationBaseCategoryList() + [year_category]
#     line.setVariationBaseCategoryList(line_category_list)
#
#     # update cell variation category list
#     cell_category_list = cell.getCategoryList() + [year_category]
#     cell.edit( membership_criterion_category_list = category_list
#              , category_list                      = category_list
#              )


  # CashInventoryDetail-related-properties functions
#   def editCashInventoryDetailVaultCode(self, document, value):
#     line = document




  # CashInventoryDetail-related-properties functions
  def updateCashInventoryMatrix(self, line, cell_category_list, quantity, cell_description):

    # save line current properties value
    line_category_list = line.getVariationCategoryList()

    LOG('Kevloggg>>>>> Line before update',0, repr(line.__dict__))

    # set the new_line_category_list
    new_line_category_list = []
    for category in cell_category_list + line_category_list:
      if category not in new_line_category_list:
        new_line_category_list.append(category)

    # update the line
    line.setVariationCategoryList(new_line_category_list)

    # update the cell range
    base_id = 'movement'
    # cell_category_list must have the same base_category order of cell_range base category, so sort the category list   ->>>>>> must be verified

#     base_category_list = line.getVariationBaseCategoryList()
#     LOG('Kevloggg>>>>>',0, repr(base_category_list))
#     base_category_list.sort()
#     LOG('Kevloggg>>>>>',0, repr(base_category_list))


    base_category_list = [ 'cash_status'
                         , 'emission_letter'
                         , 'variation'
                         ]
    cell_category_list.sort()

    cell_range = []
    new_base_category_list = []
    for base_category in base_category_list:
      base_group = []
      for category in new_line_category_list:
        if category.startswith(base_category + '/') and category not in base_group:
          base_group.append(category)
      if len(base_group) > 0:
        new_base_category_list.append(base_category)
      cell_range.append(base_group)
    line.setVariationBaseCategoryList(new_base_category_list)
    line.setCellRange( base_id = base_id
                     , *cell_range
                     )

    # create the cell
    kwd = { 'base_id'    : base_id
          , 'portal_type': 'Cash Inventory Cell'
          }
    new_cell = line.newCell(*cell_category_list, **kwd)
    new_cell.edit( mapped_value_property_list         = ('price', 'inventory')
                 , force_update                       = 1
                 , inventory                          = quantity
                 , membership_criterion_category_list = cell_category_list
                 , category_list                      = cell_category_list
                 , description                        = cell_description
                 )

    LOG('Kevloggg>>>>> Line after update',0, repr(line.__dict__))

