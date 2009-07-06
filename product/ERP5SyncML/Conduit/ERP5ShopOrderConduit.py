##############################################################################
# -*- coding: utf-8 -*-
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_inner, aq_chain, aq_acquire

from xml.dom import implementation
from xml.dom.ext import PrettyPrint
from xml.dom import Node

import random
from cStringIO import StringIO

from zLOG import LOG



class ERP5ShopOrderConduit(ERP5Conduit):
  """
  This conduit is used in the synchronisation process of Storever and ERP5 to convert
  a Storever Shop Order to a ERP5 Sale Order.
  Don't forget to add this base categories in portal_category :
      'hd_size', 'memory_size', 'optical_drive', 'keyboard_layout', 'cpu_type'
  """


#   TODO: tester ce script sur le serveur de backup (qui semble être different)


  # Declarative security
  security = ClassSecurityInfo()

  # Initialize the random function
  random.seed()



  security.declareProtected(Permissions.ModifyPortalContent, 'constructContent')
  def constructContent(self, object, object_id, docid, portal_type):
    """
    This is a redefinition of the original ERP5Conduit.constructContent function to
    allow the creation of a ERP5 Sale Order instead of a Storever Shop Order.
    """
    portal_types = getToolByName(object, 'portal_types')
    subobject = None
    new_object_id = object_id
    if portal_type == 'Shop Order':
      # The random part of the id can be removed. It's only used for the developpement
      #new_object_id = 'storever-' + object_id  + '-' + str(random.randint(1000, 9999))
      #new_object_id = 'storever-' + object_id
      subobject = object.newContent( portal_type = 'Sale Order'
                                   , id          = new_object_id)
      # And we must set the destination and destination_section to Nexedi
      nexedi = object.getPortalObject().organisation.nexedi
      subobject.setSourceValue(nexedi)
      subobject.setSourceSectionValue(nexedi)
    if portal_type == 'Order Line':
      last_line_num = self.getLastOrderLineNumber(object)
      new_object_id = "storever-" + str(last_line_num + 1) + "-" + object_id
      subobject = object.newContent( portal_type = 'Sale Order Line'
                                   , id          = new_object_id)
    return subobject



#   # Not needed yet
#   security.declareProtected(Permissions.ModifyPortalContent, 'addWorkflowNode')
#   def addWorkflowNode(self, object, xml, simulate):
#     """
#     This is a redefinition of the original ERP5Conduit.addWorkflowNode function to
#     allow the translation of a Storever Shop Order workflow to a ERP5 Sale Order one.
#     """
#     conflict_list = []
#     status = self.getStatusFromXml(xml)
# #     if status['action'] == 'ship':
# #       status['time']
#     return conflict_list



  security.declarePrivate('dom2str')
  def dom2str(self, xml_root=None):
    """
    This function transform a DOM tree to string.
    This function is only usefull for debugging.
    """
    xml_str = StringIO()
    PrettyPrint(xml_root, xml_str)
    xml_string = xml_str.getvalue()
    LOG('XML output: ', 0, xml_string)
    return xml_string



  security.declarePrivate('str2id')
  def str2id(self, string=None):
    """
    This function transform a string to a safe id.
    It is also used here to create a safe category id from a string.
    """
    out = ''
    if string == None:
      return None
    string = string.lower()
    # We ignore the discontinued information to allow the use of the same category
    # even if the option is discontinued on the storever side
    string = string.replace('discontinued', '')
    string = string.strip()
#     # TODO: manage accent
    for char in string:
      if char == '_' or char.isalnum():
        pass
      elif char.isspace() or char in ('+', '-'):
        char = '_'
      else:
        char = None
      if char != None:
        out += char
    # LOG('Category name output (using str2id) >>>>>>> ', 0, out)
    out = out.strip('_')
    return out



  security.declarePrivate('countrySearch')
  def countrySearch(self, site_root, category_path=None, country=None):
    """
    This recursive function try to find the region category from the name of a country
    """
    if country.lower()=='suisse':
      country='switzerland'
    if country.lower()=='united kingdom':
      country='uk'
    if country.lower()=='united states of america':
      country='usa'
    if category_path == None:
      portal_categories = getToolByName(site_root, 'portal_categories')
      categories_path = portal_categories.absolute_url(relative=1)
      category_path = categories_path + '/region'
    region_folder = site_root.restrictedTraverse(category_path)
    for region_id in region_folder.objectIds():
      region_path = category_path + '/' + region_id
      splitted_path = region_path.split("/")
      cat_region = "/".join(splitted_path[3:])
      if region_id.lower() == country.lower():
        return cat_region
      find_path = self.countrySearch(site_root, region_path, country)
      if find_path != None:
        return find_path
    return None



  security.declarePrivate('createOrFindProduct')
  def createOrFindProduct(self, erp5_site, erp5_product_id):
    """
    This function try to find a previous product with the same id,
    and create it if the search is unsuccessful
    """
    erp5_site_path = erp5_site.absolute_url(relative=1)
    product_path = erp5_site_path + '/product'
    product_folder = erp5_site.restrictedTraverse(product_path)
    product = None
    # Try to find a previous product
    for product_id in product_folder.objectIds():
      if product_id == erp5_product_id:
        product = erp5_site.restrictedTraverse(erp5_site_path + '/product/' + erp5_product_id)
    # We have to create a new product
    if product is None:
      product = product_folder.newContent( portal_type = 'Product'
                                         , id          = erp5_product_id)
    if len(product.getProductLineValueList())==0:
      #storever_product_line = erp5_site.portal_categories.product_line.storever
      product.setProductLine('storever')
    return product



  security.declarePrivate('setProductWorkflow')
  def setProductWorkflow(self, product_object, product_title):
    """
    This function set the validation workflow to indicate if a product
    is discontinued (workflow state = invalidate) or not (workflow state = validate)
    """
    #!!!!!!!!!!!!!!!!!!!!!!!!!!
#     return
    #!!!!!!!!!!!!!!!!!!!!!!!!!!
    action = None
    if hasattr(product_object, 'workflow_history'):
      LOG('Info needed from portal_workflow >>>>>>>>> ', 0, '')
      workflow_state = product_object.portal_workflow.getInfoFor(product_object, 'validation_state')
      LOG('workflow_state is >>>>>>>>> ', 0, repr(workflow_state))
    if product_title.lower().find('discontinued') != -1:
      #if workflow_state != 'invalidated':
      #  action = 'invalidate_action'
      if workflow_state == 'draft':
        LOG('workflow_state we will validate ', 0, repr(workflow_state))
        #product_object.portal_workflow.doActionFor( product_object
        #                                          , 'validate_action'
        #                                          , wf_id = 'validation_workflow')
        product_object.validate()
        new_workflow_state = product_object.portal_workflow.getInfoFor(product_object, 'validation_state')
        LOG('workflow_state we will new_workflow_state ', 0, repr(new_workflow_state))
      product_object.invalidate()
    elif workflow_state in ('draft', 'invalidated'):
      #action = 'validate_action'
      product_object.validate()
    LOG('action is >>>>>>>>> ', 0, repr(action))
    LOG('product_object.portal_type is >>>>>>>>> ', 0, product_object.getPortalType())
    LOG('productobject.getPhysicalPath is >>>>>>>>> ', 0, product_object.getPhysicalPath())
    LOG('productobject.title is >>>>>>>>> ', 0, product_object.getTitle())
    LOG('productobject.  product_title is >>>>>>>>> ', 0, product_title)
    #if action != None:
    #  if action ==
    #  product_object.invalidate()
      #product_object.portal_workflow.doActionFor( product_object
      #                                          , action
      #                                          , wf_id = 'validation_workflow')
    LOG('end of workflow action >>>>>>>>> ', 0, repr(action))



  security.declarePrivate('niceTitle')
  def niceTitle(self, title):
    """
    This function create a nice title without the discontinued information
    """
    splitted_title = title.strip().split(" ")
    nice_title = ''
    for string in splitted_title:
      if string.lower().find('discontinued') == -1:
        nice_title += string + ' '
    return nice_title.strip()



  security.declarePrivate('getLastOrderLineNumber')
  def getLastOrderLineNumber(self, order_object):
    """
    This function give the number of the last Storever Shop Order Line processed
    """
    # Scan existing order line id to get the last order line number
    maximum_order_num = 0
    LOG('order_object.objectIds',0,order_object.objectIds())
    LOG('order_object.objectIds',0,[x for x in order_object.objectIds()])
    for order_line_id in order_object.objectIds():
      splitted_line_id = order_line_id.split("-")
      current_line_num = int(splitted_line_id[1])
      if current_line_num > maximum_order_num:
        maximum_order_num = current_line_num
    LOG('getLastOrderLineNumber return  >>>>>>>> ', 0, repr(maximum_order_num))
    return int(maximum_order_num)



#     # Not needed yet because we prefer using my own owner_account_id property
#   security.declareProtected(Permissions.ModifyPortalContent, 'addLocalRoleNode')
#   def addLocalRoleNode(self, object, xml):
#     """
#     """
#     conflict_list = []
#     LOG('object >>>>>>>> ', 0, object)
#     LOG('xml >>>>>>>> ', 0, self.dom2str(xml))
#     return conflict_list



  security.declarePrivate('updateObjProperty')
  def updateObjProperty(self, object, property, kw, key):
    """
    This function update the property of an object with a given value stored in a dictionnary. This function help the Conduit to make decision about the synchronisation of values.

    Example of call : self.updateObjProperty(person_object, 'DefaultAddressStreetAddress', kw, 'address')

    Solution (d'apres seb) :
      * machin = getattr (object, methos)
      * machin()
    """
    if kw.has_key(key):
      new_value = kw[key]
      if new_value != None:
        if type(new_value) is type('s'):
          new_value = new_value.title()

        current_value = eval('object.get' + property + '()')
        LOG("I have to run this >>>>>>>> ", 0, 'object.get' + property + '()')
        LOG("current_value >>>>>>>> ", 0, repr(current_value))

        # The current property value is not consistent
        if current_value == None or len(current_value) == 0:
          # Erase the current value with the new one

          LOG("I have to run this to set the property >>>>>>>> " + 'object.set' + str(property) + '(' + str(new_value) + ')' + str(current_value), 0, '')

        # A previous consistent value exist
        elif current_value.strip().lower() != new_value.strip().lower():
          # TODO : We need to choose if we replace it or not, or mix the current with the new one
          LOG('We have to make the fusion of previous address with the current one  >>>>>>>', 0, '')
          return False
        return True
    return False



  security.declareProtected(Permissions.ModifyPortalContent, 'editDocument')
  def editDocument(self, object=None, **kw):
    """
    This function use the properties of the object to convert a Storever ShopOrder to an ERP5 SaleOrder.
    """
    if object == None:
      return

    LOG('KW >>>>>>>> ', 0, kw)

    # This list contain a list of object to check to know if their workflow need to be mofified
    # We store these objects into a list and we will apply modification at the end to avoid mysql lock problem
    workflow_joblist = []

    # Get the ERP5 root object
    portal_types = getToolByName(object, 'portal_types')
    erp5_site = portal_types.getPortalObject()
    erp5_site_path = erp5_site.absolute_url(relative=1)

    # The object is a ShopOrder
    if kw.has_key('country'):
      object.setStartDate(kw['target_start_date'])
      object.setStopDate(kw['target_stop_date'])
      # Find the organisation and the person folder
      person_path = erp5_site_path + '/person'
      person_folder = erp5_site.restrictedTraverse(person_path)
      organisation_path = erp5_site_path + '/organisation'
      org_folder = erp5_site.restrictedTraverse(organisation_path)
      # Find the service folder
      service_path = erp5_site_path + '/service'
      service_folder = erp5_site.restrictedTraverse(service_path)

#       # TODO : if storever-id exist dans ERP5 --> prendre en charge l'update de la facture

      # Get the id of the owner account in storever
      owner_account_id = kw['owner_account_id']
      # Set the id of the owner in ERP5 (the owner could be an Organisation or a Person)
      owner_id = "storever-" + owner_account_id

      # Try to find the identity created for a previous ShopOrder of the same Storever member account
      person_object = None
      org_object = None
      for person_id in person_folder.objectIds():
        if person_id == owner_id:
          person_object = erp5_site.restrictedTraverse(erp5_site_path + '/person/' + person_id)
          LOG("Previous person found ! >>>>>>>>",0,repr(person_object))
          break
      for organisation_id in org_folder.objectIds():
        if organisation_id == owner_id:
          org_object = erp5_site.restrictedTraverse(erp5_site_path + '/organisation/' + organisation_id)
          LOG("Previous organisation found ! >>>>>>>>",0,repr(org_object))
          break

      # Define the previous customer structure
      previous_owner_type = ''
      if person_object != None:
        previous_owner_type = 'p'
      if org_object != None:
        previous_owner_type = 'o' # Organisation is more important than the person
        # This is a particular case where the user put 
        # the name of an organisation in his own name
        if not kw.has_key('organisation'):
          kw['organisation'] = org_object.getId()
      #if len(previous_owner_type) == 0:
      #  previous_owner_type = None
      LOG("Previous customer structure >>>>>>>>",0,repr(previous_owner_type))

      # Try to know the type of the current storever customer
      owner_type = ''
      if kw.has_key('name') and kw['name'] not in (None, ''):
        owner_type += 'p'
      if kw.has_key('organisation') and kw['organisation'] not in (None, '', 'none'):
        owner_type += 'o'
      if kw.has_key('eu_vat') and kw['eu_vat'] not in (None, '') and owner_type.find('o') == -1:
        owner_type += 'o'
      if len(owner_type) == 0:
        owner_type = None
      LOG("Current customer structure >>>>>>>>",0,repr(owner_type))

#       # TODO : in this part of the script, add the possibility to find an existing
#       # ERP5 person/organisation according to the name of that person/organisation
      # Compare the current representation of the member account with the previous one
      #if previous_owner_type != owner_type: # XXX Seb: I guess it's quite strange to compare "po" to "poo"
                                             # There is probably an error here, so I changed it but 
                                             # I'm sure I'm not really doing what it was intended for
      if previous_owner_type is None and owner_type is not None:
        # There is difference between the two (previous and current) representation of the customer
        # We have to manage the differences to create a unique customer representation
        LOG("There is difference between previous and current >>>>>>>>",0,'')
        if previous_owner_type == None:
          # No previous customer found, create one
          if owner_type.find('o') != -1:
            org_object = org_folder.newContent( portal_type = 'Organisation'
                                              , id          = owner_id)
            LOG("new organisation created >>>>>>>>",0,repr(org_object))
          if owner_type.find('p') != -1:
            person_object = person_folder.newContent( portal_type = 'Person'
                                                    , id          = owner_id)
            LOG("new person created >>>>>>>>",0,repr(person_object))
        else:
          if owner_type == None:
            # Use the previous Structure
            owner_type = previous_owner_type
            LOG("Use the previous Structure >>>>>>>>",0,'')
          else:
            LOG("We have to convert the structure >>>>>>>>",0,'')
#         #  XXX Be aware of that problem: the invoice for a sale order must look the same (I mean when we generate the pdf version)
#           Case to process :
#           previous current
#           o  -->   p
#           o  -->   op
#           p  -->   o
#           op -->   o
#           op -->   p
#           p  -->   op  - in progress

            # The previous customer was detected as a person only
            if previous_owner_type.find('p') != -1 and previous_owner_type.find('o') == -1:
#             Case to process :
#             previous current
#             p  -->   o
#             p  -->   op  - in progress
              # The customer has now an organisation, we have to create this organisation and link the person to
              if owner_type.find('p') != -1 and owner_type.find('o') != -1:
                # Create a new organisation
#                 # TODO : factorise this code with the same above
                org_object = org_folder.newContent( portal_type = 'Organisation'
                                                  , id          = owner_id)
              else:
#                 # TODO : Transform a person to an organisation ? Is it a good idea ?
                pass
            # The previous customer was detected as an organisation only
            elif previous_owner_type.find('p') == -1 and previous_owner_type.find('o') != -1:
#             Case to process :
#             previous current
#             o  -->   p
#             o  -->   op
              pass
            # The previous customer was detected as a person in an organisation
            else:
#             Case to process :
#             previous current
#             op -->   o
#             op -->   p
              pass
      else:
        if owner_type == None:
          # There is not enough informations to know if the customer is an organisation or
          # a person and there is no previous record
          # By default, we consider the customer as a person, so we have to force to create one
          owner_type = 'p'
          person_object = person_folder.newContent( portal_type = 'Person'
                                                  , id          = owner_id)
          LOG("Create a person by default  >>>>>>>>",0,repr(person_object))
        else:
          # The structure is the same
          # We only need to be aware of data fusion between the previous and the current representation
          # So we don't need to do something because the information fusion process take place below
          LOG("The structure is the same. don't do anything >>>>>>>>",0,'')
          pass

      LOG("Person object >>>>>>>>",0,repr(person_object))
      LOG("Organisation object >>>>>>>>",0,repr(org_object))

      # Copy informations related to the customer in the ERP5 representation of the customer
      # Be carefull because all informations from the storever ShopOrder are optionnals
      if owner_type.find('p') != -1:
        # Link the customer with the Sale Order
        object.setDestination("person/" + owner_id)
        object.setDestinationSection("person/" + owner_id)

#         # TODO : do the same things for each single information
#         # TODO : before doing something working well in every case, copy the previou value in the comment field to traceback the modification and let me evaluate the solidity of my algorithm
#         # TODO : perhaps it's possible to factorize the code using a generic function
        # Synchronise the street address

        # Solution (d'apres seb)
        # machin = getattr (object, methos)
        # method(machin)

        if person_object is None:
          person_object = person_folder.newContent( portal_type = 'Person'
                                            , id          = owner_id)
          LOG("new person created >>>>>>>>",0,repr(org_object))
        #machin = self.updateObjProperty(person_object, 'DefaultAddressStreetAddress', kw, 'address')
        #LOG("My new updateObjProperty() return >>>>>>>>",0,repr(machin))

#         if kw.has_key('address') and kw['address'] != None:
#           previous_address = person_object.getDefaultAddressStreetAddress()
#           if len(previous_address) == 0:
#             person_object.setDefaultAddressStreetAddress(kw['address'].title())
#           elif previous_address.strip().lower() != kw['address'].strip().lower():
#             LOG('We have to make the fusion of previous address with the current one  >>>>>>>', 0, '')

        if kw.has_key('city') and kw['city']!=None:
          person_object.setDefaultAddressCity(kw['city'].title())
        if kw.has_key('address') and kw['address'] != None:
          person_object.setDefaultAddressStreetAddress(kw['address'].title())
        if kw.has_key('zipcode') and kw['zipcode']!=None:
          person_object.setDefaultAddressZipCode(kw['zipcode'])
#         # TODO : set the person products interest (storever, etc)
        # Search the country in the region category
        if kw['country'] != None:
          region_path = self.countrySearch(erp5_site, None, kw['country'])
          if region_path != None:
            person_object.setDefaultAddressRegion(region_path)
#           else:
#             # TODO : Ask the user to select an appropriate region
        if kw.has_key('email') and kw['email'] != None:
          person_object.setDefaultEmailText(kw['email'])
        if kw.has_key('phone') and kw['phone'] != None:
          person_object.setDefaultTelephoneText(kw['phone'])
#         # TODO : Don't work
#         person_object.setDefaultCareerRole("client")
        # Split the name to give at least a required LastName
        # Then the title will be automaticaly created by the Person object from this data
        if kw.has_key('name') and kw['name'] != None:
          splitted_name = kw['name'].strip().split(" ")
          person_object.setLastName((splitted_name[-1]).title())
          if len(splitted_name) > 1:
            person_object.setFirstName((" ".join(splitted_name[:-1])).title())
        else:
          # We have to find a title to have something to show in the RelationField of the SaleOrderForm
          person_object.setTitle(owner_account_id.title())
        # The Person is subordinated to an Organisation ?
        if owner_type.find('o') != -1 and  previous_owner_type =='o':
#           # TODO : fix this
#           person_object.setSubordination("organisation/" + owner_id)
          if kw.has_key('organisation') and kw['organisation'] != None:
            org_object.setTitle(kw['organisation'].title())
            org_object.setCorporateName(kw['organisation'].title())
          if kw.has_key('eu_vat') and kw['eu_vat'] != None:
            org_object.setVatCode(kw['eu_vat'])
          # Test for debug
          if (not (kw.has_key('organisation')) or (kw.has_key('organisation') and kw['organisation'] != None)) and (not (kw.has_key('eu_vat')) or (kw.has_key('eu_vat') and kw['eu_vat'] != None)):
            LOG("AARRGG ! Big conflict detected : this organisation has no title or eu_vat. These properties are primary key to deduced that the storever member account was an organisation >>>>>>>>>>", 0, '')
          org_object.setRole("client")

      # The customer is not a person or a person of an organisation, so the customer is an organisation...
      # XXX Seb: So like it was defined, if we have a person from an organisation, then 
      # the organisation is not modified, so the vat is not defined!!
      # This is good to replace the person with an organisation, because vat is only
      # defined on organisation. An update would be to define when we have both organisation
      # and person the destination_administration XXX
      if owner_type.find('o') != -1:
        if org_object is None:
          org_object = org_folder.newContent( portal_type = 'Organisation'
                                            , id          = owner_id)
          LOG("new organisation created >>>>>>>>",0,repr(org_object))
        # Link the customer with the Sale Order
        object.setDestination("organisation/" + owner_id)
        object.setDestinationSection("organisation/" + owner_id)
        # All informations describe the organisation
        if kw.has_key('organisation') and kw['organisation'] != None:
          org_object.setTitle(kw['organisation'].title())
          org_object.setCorporateName(kw['organisation'].title())
        org_object.setRole("client")
        if kw.has_key('eu_vat') and kw['eu_vat'] != None:
          org_object.setVatCode(kw['eu_vat'])
        if kw.has_key('address') and kw['address'] != None:
          org_object.setDefaultAddressStreetAddress(kw['address'].title())
        if kw.has_key('city') and kw['city'] != None:
          org_object.setDefaultAddressCity(kw['city'].title())
        if kw.has_key('zipcode') and kw['zipcode'] != None:
          org_object.setDefaultAddressZipCode(kw['zipcode'])
        # Search the country in the region category
        if kw['country'] != None:
          region_path = self.countrySearch(erp5_site, None, kw['country'])
          if region_path != None:
            org_object.setDefaultAddressRegion(region_path)
#           else:
#             # TODO : Ask the user to select an appropriate region
        if kw.has_key('email') and kw['email'] != None:
          org_object.setDefaultEmailText(kw['email'])
        if kw.has_key('phone') and kw['phone'] != None:
          org_object.setDefaultTelephoneText(kw['phone'])

      # Save the billing address in the description, because there is no dedicated place for it
      if kw.has_key('billing_address') and len(kw['billing_address']) > 0:
        object.setDescription("Send the bill to : " + kw['billing_address'])
      # Set the Title because its required
      object.setTitle("Storever Order " + str(kw['order_id']))

#       # ONLY for information (will be used in the future)
      object.setDescription(str(object.getDescription()) + "\n\nTotal Price (with transport fees) :" + str(kw['total_price']))

      # Add a new orderLine for the shipment
      stor_ship_title = kw['send_fee_title'].strip()
      erp5_ship_title = stor_ship_title + ' Shipment'
      my_shipment_id = 'storever-' + self.str2id(stor_ship_title)

      # Try to find an existing shipment service using several methods
      shipment_id = None
      for service_id in service_folder.objectIds():
        service_object = erp5_site.restrictedTraverse(erp5_site_path + '/service/' + service_id)
        # First method: compare the id with my standard layout
        if service_id.strip() == my_shipment_id:
          shipment_id = my_shipment_id
          LOG("Service found with method 1 ! >>>>>>>>", 0, repr(shipment_id))
          break
        # Second method: use a standard title layout
        if service_object.getTitle().lower().strip() == erp5_ship_title.lower().strip():
          shipment_id = service_id
          LOG("Service found with method 2 ! >>>>>>>>", 0, repr(shipment_id))
          break
        # Third method: compare words
        erp5_ship_id_word_list = self.str2id(service_id).split("_")
        stor_ship_id_word_list = self.str2id(stor_ship_title).split("_")
        erp5_ship_title_word_list = self.str2id(erp5_ship_title).split("_")
        erp5_ship_id_word_list.sort(key=lambda x: str(x))
        stor_ship_id_word_list.sort(key=lambda x: str(x))
        erp5_ship_title_word_list.sort(key=lambda x: str(x))
        if stor_ship_id_word_list in (erp5_ship_id_word_list, erp5_ship_title_word_list):
          shipment_id = service_id
          LOG("Service found with method 3 ! >>>>>>>>", 0, repr(shipment_id))
          break

      # No previous shipment service found, so create a new one
      if shipment_id == None:
#         TODO : implement the code here to follow the comment in the LOG below
        LOG("We have to create the shipping service with this id >>>>>>>>", 0, repr(my_shipment_id))
        # Create a new shipment service
        shipment_id = my_shipment_id

      # Get the object of the shipment service
#       shipment_path = erp5_site_path + '/service/' + shipment_id
#       shipment_object = erp5_site.restrictedTraverse(shipment_path)

      # Create a new order line in this order to represent the shipment service
      last_line_num = self.getLastOrderLineNumber(object)
      ship_order_line_id = "storever-" + str(last_line_num +1 ) # XXX This may fail.
                                            # It is possible to already have
                                            # a line with this id
      LOG('ERP5ShopOrderConduit, object',0,object.getPath())
      LOG('ERP5ShopOrderConduit, objectIds',0,[x for x in object.objectIds()])
      LOG('ERP5ShopOrderConduit, will create ship_order_line_id',0,ship_order_line_id)
      ship_order_object = object.newContent( portal_type = 'Sale Order Line'
                                           , id          = ship_order_line_id)
                                           # Don't give id, it will be set
                                           # automatically.
      ship_order_object.setQuantity(1.0)
      ship_order_object.setPrice(kw['send_fee'])
      ship_order_object.setQuantityUnit('unit')
      ship_order_object.setResource("service/" + shipment_id)










    # The object is an OrderLine
    else:
      # Find the product folder
      product_path = erp5_site_path + '/product'
      product_folder = erp5_site.restrictedTraverse(product_path)

      # Find the parent order object
      parent_order_object = object.aq_parent

      # Get the id of the product in storever
      storever_product_id = kw['product_id']

      # Set the id of the product in ERP5
      erp5_product_id = "storever-" + storever_product_id

      # Try to find a previous product or create a new one
      product_object = self.createOrFindProduct(erp5_site, erp5_product_id)

      # Create a nice title (without discontinued) from the product title
      product_title = self.niceTitle(kw['product_title'])

      # Synchronise every data
      product_object.setDescription(kw['product_description'])
      product_object.setTitle(product_title)
#       # TODO : I don't know where to put this value,
#       #   because there is no "delivery days"-like property for a product
#       product_object.setDeliveryDays(kw['product_delivery_days'])
      if kw['product_expiration_date'] != None:
        product_object.setSourceBasePriceValidity(kw['product_expiration_date'])
      product_object.setBasePrice(kw['product_price'])
      product_object.setQuantityUnit('unit')
      # Save the worflow status for later modification
      workflow_joblist.append((product_object, kw['product_title']))
      # In storever, every option are set as string in the title of the OrderLine
      # This part of code create a list of all options choosen by the customer for this product
      splitted_title = kw['title'].strip().split(":")
      option_list = (":".join(splitted_title[1:])).split("/")
      LOG('Customer option list >>>>>> ', 0, repr(option_list))

      # Now, we will find the price of each option
      option_classes = [ kw['product_disk_price']
                       , kw['product_memory_price']
                       , kw['product_option_price']
                       , kw['product_processor_price']
                       ]
      priced_list = {}
      for option_item in option_list:
        option = option_item.strip()
        for option_class in option_classes:
          for option_key in option_class.keys():
            if option == option_key.strip():
              priced_list[option] = option_class[option_key]
#       # TODO : there is no default options in the final priced_list. Is the option 'default' important ?
      LOG('Customer option priced list >>>>>>>>> ', 0, repr(priced_list))

      # In ERP5, we have decided to represent some options as variation of a product
      #   and some options as new order line of product
      # Now we will update or create the variation categories related to the initial product
      # Don't forget to add this base categories in portal_category :
      #   'hd_size', 'memory_size', 'optical_drive', 'keyboard_layout', 'cpu_type'
      portal_cat = product_object.portal_categories

      # Get all keyboard related options and all optical drive related options
      keyboard_options = {}
      optical_options = {}
      options_prices = kw['product_option_price']
      for option_key in options_prices.keys():
        if option_key.lower().find("keyboard") != -1:
          keyboard_options[option_key] = options_prices[option_key]
        elif option_key.lower().find("cd") != -1 or option_key.lower().find("dvd") != -1:
          optical_options[option_key] = options_prices[option_key]
      LOG('Product keyboard layout priced list >>>>>>>>> ', 0, repr(keyboard_options))
      LOG('Product optical drive priced list >>>>>>>>> ', 0, repr(optical_options))

      # Create a data structure containing all allowed variations
      variant_category_list = [ ('hd_size',        kw['product_disk_price'])
                              , ('memory_size',    kw['product_memory_price'])
                              , ('cpu_type',       kw['product_processor_price'])
                              , ('optical_drive',  optical_options)
                              , ('keyboard_layout', keyboard_options)]
      # Create or update every category representing all variantions
      base_cat_list = []
      cat_list = []
      for (cat_base, cat_data) in variant_category_list:
        if len(cat_data) > 0 and portal_cat.resolveCategory(cat_base) != None:
          base_cat_list.append(cat_base)
          for disk_variant_key in cat_data.keys():
            cat_id = self.str2id(disk_variant_key)
            cat_path = cat_base + '/' + cat_id
            cat_list.append(cat_path)
            if portal_cat.resolveCategory(cat_path) == None:
              cat_base_object = portal_cat._getOb(cat_base)
              cat_base_object.newContent ( portal_type = 'Category'
                                         , id          = cat_id)
              LOG("New created category >>>>>>>>>>> ", 0, cat_path)

      # Set the base variation of the product
      product_object.setVariationBaseCategoryList(base_cat_list)

      # Set the variation range of the product
      product_object.setVariationCategoryList(cat_list)

      LOG("cat_list >>>>>>>>>>", 0, repr(cat_list))

      # Now we seperate options and variations of the initial product ordered by the customer
      customer_product_option_list = {}
      customer_product_variation_list = {}
      customer_product_base_variation_list = []
      for option in priced_list:
        option_is_variant = None
        for (cat_base, cat_data) in variant_category_list:
          LOG('editDocument, cat_base',0,cat_base)
          base_cat_object = portal_cat.resolveCategory(cat_base)
          cat_list = base_cat_object.getCategoryChildIdItemList()
          for (category, category_bis) in cat_list:
            if self.str2id(option) == category:
              customer_product_variation_list[category] = cat_base + '/' + category
              if cat_base not in customer_product_base_variation_list:
                customer_product_base_variation_list.append(cat_base)
              option_is_variant = 1
              break
          if option_is_variant == 1:
            break
        if option_is_variant == None:
          customer_product_option_list[option] = priced_list[option]
      if len(customer_product_option_list) + len(customer_product_variation_list) != len(priced_list):
        LOG('>>>>>>> Wrong repartition of the customer priced list', 200)
      LOG('>>>>>> Customer product option priced list: ', 0, repr(customer_product_option_list))
      LOG('>>>>>> Customer product variation priced list: ', 0, repr(customer_product_variation_list))
      LOG('>>>>>> Customer product base variation list: ', 0, repr(customer_product_base_variation_list))

      # This variable repesent the sum of every option prices
      options_price_sum = 0.0

      # We have to create a new product for every option not included in the variation system
      for opt_prod_key in customer_product_option_list.keys():
        opt_prod_price = customer_product_option_list[opt_prod_key]

        # Set the id of the optionnal product
        opt_prod_key = self.str2id(opt_prod_key)
        opt_prod_id = "storever-" + opt_prod_key

        # Create the optionnal product or get it if it already exist
        opt_prod_object = self.createOrFindProduct(erp5_site, opt_prod_id)

        # Remove the "discontinued" string in the title
        opt_prod_title = self.niceTitle(opt_prod_key)
        # Set some properties of the optionnal product
        opt_prod_object.setTitle(opt_prod_title.title())
        opt_prod_object.setBasePrice(opt_prod_price)
        opt_prod_object.setQuantityUnit('unit')
        # Save the workflow state changing for later modification
        workflow_joblist.append((opt_prod_object, opt_prod_key))

        # Get the last number of order lines
        # This process is needed to distinguish the same option created for two different product
        #   and avoid problem when a new Order line is created for an option product already used
        #   inside the same Sale Order
        last_line_num = self.getLastOrderLineNumber(parent_order_object)
        opt_prod_line_id = "storever-" + str(last_line_num) + "-" + opt_prod_key
        # Create an order line for the product
        opt_order_line_object = parent_order_object.newContent( portal_type = 'Sale Order Line'
                                                              , id          = opt_prod_line_id)
        # Set several properties of the new orderLine
        opt_order_line_object.setQuantityUnit('unit')
        opt_order_line_object.setPrice(opt_prod_price)
        # There is the same quantity of the base product
        opt_order_line_object.setQuantity(kw['quantity'])
        # Link the Order Line with the product
        opt_order_line_object.setResource("product/" + opt_prod_id)

        # Calcul the sum of option prices
        options_price_sum += float(opt_prod_price)

#       # TODO: don't forget to manage the VAT values

#      TODO: # Try to find a previous OrderLine to update
#       line_object = None
#       for product_id in product_folder.objectIds():
#         if product_id == erp5_product_id:
#           product_object = erp5_site.restrictedTraverse(erp5_site_path + '/product/' + erp5_product_id)
#           break

      # Migrate the line informations
      object.setQuantity(kw['quantity'])
      object.setDescription(kw['title'])
      object.setQuantityUnit('unit')

      # Substract to the product price the sum of options prices
      initial_prod_price = float(kw['price']) - options_price_sum
      object.setPrice(initial_prod_price)

      # Link the Order Line with the product
      object.setResource("product/" + erp5_product_id)

      # Set variations of the order line product choosen by the customer
      category_list = []
      for variation_key in customer_product_variation_list.keys():
        category_list.append(customer_product_variation_list[variation_key])
      #object.setVariationBaseCategoryList(customer_product_base_variation_list)
#       # TODO : fix this
      #object.setVariationCategoryList(category_list)
      previous_category_list = object.getCategoryList()
      LOG('ERP5ShopOrderConduit, previous_category_list',0,previous_category_list)
      category_list = list(previous_category_list) + list(category_list)
      object.setCategoryList(category_list)

    # Do all workflow change at the end
    LOG("enter workflow loop >>>>>>>>",0,repr(workflow_joblist))
    for (object, object_title) in workflow_joblist:
      LOG("Workflow to change :: >>>>>>>>",0,repr((object, object_title)))
      self.setProductWorkflow(object, object_title)

    return
