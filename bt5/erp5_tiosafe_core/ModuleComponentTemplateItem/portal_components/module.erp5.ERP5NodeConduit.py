##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#               Herve Poulain <herve@nexedi.com>
#               Aurelien Calonne <aurel@nexedi.com>
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

from erp5.component.module.TioSafeBaseConduit import TioSafeBaseConduit, \
     ADDRESS_TAG_LIST
from DateTime import DateTime
from lxml import etree
from zLOG import LOG, INFO, ERROR
from base64 import b16encode, b16decode
from zExceptions import BadRequest

DEBUG=True

class ERP5NodeConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize ERP5 Persons
  """

  def __init__(self):
    self.xml_object_tag = 'node'

  def getObjectAsXML(self, object, domain): # pylint: disable=redefined-builtin
    return object.Node_asTioSafeXML(context_document=domain)

  def _createSaleTradeCondition(self, object, **kw): # pylint: disable=redefined-builtin
    """ Link person to a sale trade condition so that
    we can filter person based on the plugin they came from
    """
    site = self.getIntegrationSite(kw['domain'])
    default_stc = site.getSourceTrade()
    # Create the STC
    stc = object.getPortalObject().sale_trade_condition_module.newContent(title="%s %s" %(site.getReference(), object.getTitle()),
                                                                          specialise=default_stc,
                                                                          destination_section=object.getRelativeUrl(),
                                                                          destination=object.getRelativeUrl(),
                                                                          destination_decision=object.getRelativeUrl(),
                                                                          destination_administration=object.getRelativeUrl(),
                                                                          version='001')
    stc.validate()

  def _updateSaleTradeCondition(self, object, **kw): # pylint: disable=redefined-builtin
    """ Link person to a sale trade condition so that
    we can filter person based on the plugin they came from
    """
    site = self.getIntegrationSite(kw['domain'])
    # try to find the corresponding STC
    stc_list = object.getPortalObject().sale_trade_condition_module.searchFolder(
      title="%s %s" %(site.getReference(), object.getTitle()),
      validation_state="validated")
    if len(stc_list) == 0:
      self._createSaleTradeCondition(object, **kw)
    elif len(stc_list) > 1:
      raise ValueError("Multiple trade condition (%s) retrieved for %s"
      % ([x.path for x in stc_list], object.getTitle()))
    else:
      stc = stc_list[0].getObject()
      stc.edit(
        destination_section=object.getRelativeUrl(),
        destination=object.getRelativeUrl(),
        destination_decision=object.getRelativeUrl(),
        destination_administration=object.getRelativeUrl(),)

  def _deleteSaleTradeCondition(self, object, **kw): # pylint: disable=redefined-builtin
    """ Unvalidate sale trade condition so that
    we can filter person based on the plugin they came from
    """
    stc_list = object.Base_getRelatedObjectList(portal_type="Sale Trade Condition",
                                                validation_state="validated")
    for stc in stc_list:
      stc = stc_list[0].getObject()
      stc.invalidate()

  def afterCreateMethod(self, object, **kw): # pylint: disable=redefined-builtin
    """ This method is for actions that has to be done just after object
    creation and which required to have synchronization parameters

    This is an example which create a sale trade condion for each person
    thus allowing an easy listing of person related to a plugin
    """
    self._createSaleTradeCondition(object, **kw)

  def afterUpdateMethod(self, object, **kw): # pylint: disable=redefined-builtin
    """ This method is for actions that has to be done just after object
    update and which required to have synchronization parameters

    This is an example which update a sale trade condion for each person
    thus allowing an easy listing of person related to a plugin
    """
    self._updateSaleTradeCondition(object, **kw)

  def afterDeleteMethod(self, object, **kw): # pylint: disable=redefined-builtin
    """ This method is for actions that has to be done just after object
    has been deleted and which required to have synchronization parameters

    This is an example which update a sale trade condion for each person
    thus allowing an easy listing of person related to a plugin
    """
    self._deleteSaleTradeCondition(object, **kw)

  def afterNewObject(self, object): # pylint: disable=redefined-builtin
    """ Realise actions after new object creation. """
    object.validate()
    object.updateLocalRolesOnSecurityGroups()

  def _setRelation(self, document, previous_value, organisation_gid, domain, xml, signature):
    """ Retrieve the organisation from its gid and do the link """
    # first check if there is any conflict
    synchronization_list = self.getSynchronizationObjectListForType(domain, 'Organisation', 'publication')
    if previous_value is not None and xml is not None:
      current_relation = document.getCareerSubordinationValue()
      if current_relation:
        for synchronization in synchronization_list:
          current_value = b16decode(synchronization.getGidFromObject(current_relation))
          if current_value:
            break
      else:
        current_value = ""
      if current_value not in [organisation_gid, previous_value]:
        return [self._generateConflict(document.getPhysicalPath(), 'relation', xml, current_value, organisation_gid, signature),]

    # now set the value
    if organisation_gid is None:
      document.setCareerSubordinationValue(None)
    else:
      for synchronization in synchronization_list:
        link_object = synchronization.getDocumentFromGid(b16encode(organisation_gid))
        if link_object is not None:
          break
      if link_object is not None:
        document.setCareerSubordinationValue(link_object)
      else:
        raise ValueError("Impossible to find organisation %s in %s"
                         % (organisation_gid, synchronization_list))
    document.reindexObject()
    return []

  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None, # pylint: disable=redefined-builtin
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    """ This is the method calling to create an object. """
    # if DEBUG:
    # LOG("ERP5NodeContuide._createContent", INFO, "xml = %s" %(etree.tostring(xml, pretty_print=True),))
    if True: # object_id is not None:
      sub_object = None
      if sub_object is None: # If so, it doesn't exist
        # Check if we can find it in module
        sub_object, reset_local_roles, reset_workflow = self.constructContent(
            object,
            object_id,
            self.getObjectType(xml),
        )

        # if exist namespace retrieve only the tag
        index = 0
        if xml.nsmap not in [None, {}]:
          index = -1

        default_address_created = False
        # browse the xml
        phone_list = []
        cellphone = None
        fax_list = []
        relation = None
        category_list = []
        role_list =[]
        address_tag_mapping = {"street" : "street_address",
                               "zip" : "zip_code",
                               "country" : "region",}
        address_int_index = 0
        for node in xml.getchildren():
          # works on tags, no on comments
          if not isinstance(node.tag, str):
            continue
          tag = node.tag.split('}')[index]

          # specific for phone
          if tag == "phone":
            phone_list.append(node.text)
          elif tag == "cellphone":
            cellphone = node.text
          elif tag == "fax":
            fax_list.append(node.text)
          elif tag == "relation":
            relation = node.text
          elif tag == "category":
            if node.text.startswith('role'):
              role_list.append(node.text[len("role/"):])
            else:
              category_list.append(node.text)
          elif tag == 'address':
            # Build dict of address properties
            address_data_dict = {}
            for element in node.getchildren():
              if not isinstance(element.tag, str):
                continue
              element_tag = element.tag.split('}')[index]
              address_data_dict[address_tag_mapping.get(element_tag, element_tag)] = element.text
            # Create the address once we are sure it is well defined
            if len(address_data_dict):
              # Define address id
              if not default_address_created:
                address_id = "default_address"
                default_address_created = True
              else:
                address_id = None
              # Create the address object
              address = sub_object.newContent(portal_type='Address',
                                              int_index=address_int_index,
                                              **address_data_dict)
              address_int_index += 1
              # Rename to default if necessary
              if address_id is not None:
                address.edit(int_index=0)
                sub_object.activate(activity="SQLQueue",
                                    after_method_id="immediateReindexObject",
                                    priority=5
                                    ).manage_renameObject(address.getId(), address_id)

        # Set telephone
        default_phone_set = False
        if cellphone is not None:
          sub_object.edit(mobile_telephone_text=cellphone)

        for phone in phone_list:
          if not default_phone_set:
            sub_object.edit(default_telephone_text=phone)
            default_phone_set = True
          else:
            # Create new subobject
            sub_object.newContent(portal_type="Telephone",
                                  telephone_number=phone)
        # Set fax
        default_fax_set = False
        for fax in fax_list:
          if not default_fax_set:
            sub_object.edit(default_fax_text=fax)
            default_fax_set = True
            continue
          # Create new subobject
          sub_object.newContent(portal_type="Fax",
                                telephone_number=fax)

        # Link to organisation
        if relation is not None:
          self._setRelation(sub_object, None, relation, kw.get('domain'), None, kw.get('signature'))

        # Set category
        if len(category_list):
          sub_object.setCategoryList(category_list)

        if len(role_list):
          if sub_object.getPortalType() == "Person":
            sub_object.edit(career_role_list=role_list)
          elif sub_object.getPortalType() == "Organisation":
            sub_object.edit(role_list=role_list)

      # build the content of the node
      self.newObject(
          object=sub_object,
          xml=xml,
          simulate=simulate,
          reset_local_roles=reset_local_roles,
          reset_workflow=reset_workflow,
          )
      self.afterCreateMethod(sub_object, **kw)
    return sub_object


  def _deleteContent(self, object=None, object_id=None, **kw): # pylint: disable=redefined-builtin
    """ We do not delete nodes """
    self.afterDeleteMethod(object[object_id])

  def editDocument(self, object=None, **kw): # pylint: disable=redefined-builtin
    """ This editDocument method allows to set attributes of the object. """
    # if DEBUG:
    #   LOG("ERP5NodeConduit.editDocument", INFO, "object = %s with %s" %(object.getPath(), kw))
    if kw.get('address_mapping') is None:
      mapping = {
          'title': 'title',
          'firstname': 'first_name',
          'lastname': 'last_name',
          'email': 'default_email_text',
          'reference' : 'reference',
          'birthday': 'start_date',
          'description': 'description',
          'phone' : 'default_telephone_text',
          'cellphone' : 'mobile_telephone_text',
          'fax' : 'default_fax_text',
      }
    else:
      mapping = {
          'street': 'street_address',
          'zip': 'zip_code',
          'city': 'city',
          'country': 'region',
      }
    # translate kw with the good PropertySheet
    property_ = {}
    for k, v in kw.items():
      k = mapping.get(k, k)
      property_[k] = v
    object._edit(**property_)

  def checkAddressConflict(self, document, tag, xml, previous_value, new_value, signature):
    """
    """
    xpath_expression = xml.get('select')
    try:
      # work on the case: "/node/address[x]"
      address_index = int(xpath_expression.split('address[')[-1].split(']')[0])
    except ValueError:
      # Work on the case: "/node/address"
      address_index = 1

    if address_index == 1:
      address = document.getDefaultAddressValue()
    else:
      # the XUPDATE begin by one, so one is default_address and the
      # first python index list is zero, so x-2
      address_index -= 2
      # address list of the person without default_address
      address_list = document.searchFolder(
          portal_type='Address',
          sort_on=(['id', 'ASC'],),
          id={
            'query': 'default_address',
            'operator': '!=',
          },
      )
      try:
        address = address_list[address_index].getObject()
      except IndexError:
        return [self._generateConflict(document.getPhysicalPath(), tag, xml, None, new_value, signature),]

    # getter used to retrieve the current values and to check conflicts
    getter_value_dict = {
        'street': address.getStreetAddress(),
        'zip': address.getZipCode(),
        'city': address.getCity(),
        'country': address.getRegion(),
    }

    # create and fill a conflict when the integration site value, the erp5
    # value and the previous value are differents
    try:
      current_value = getter_value_dict[tag].encode('utf-8')
    except UnicodeDecodeError:
      current_value = getter_value_dict[tag]
    if current_value not in [new_value, previous_value]:
      return [self._generateConflict(document.getPhysicalPath(), tag, xml, current_value, new_value, signature),]
    else:
      keyword = {'address_mapping': True, tag: new_value}
      self.editDocument(object=address, **keyword)
      return []


  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, **kw):
    """
      This method is called in updateNode and allows to work on the  update of
      elements.
    """
    if DEBUG:
      LOG("ERP5NodeConduit._updateXupdateUpdate", INFO, "doc = %s, xml = %s" %(document.getPath(),
                                                                               etree.tostring(xml, pretty_print=1),))
    xpath_expression = xml.get('select')
    tag = xpath_expression.split('/')[-1]
    new_value = xml.text.encode('utf-8')

    # retrieve the previous xml etree through xpath
    selected_previous_xml = previous_xml.xpath(xpath_expression)
    try:
      previous_value = selected_previous_xml[0].text.encode('utf-8')
    except IndexError:
      previous_value = None

    # check if it'a work on person or on address
    if tag in ADDRESS_TAG_LIST:
      conflict_list = self.checkAddressConflict(document, tag, xml, previous_value, new_value, kw.get('signature'))
    else:
      conflict_list = self.checkConflict(tag, document, previous_value, new_value, kw.get('domain'), xml, kw.get('signature'))
    self.afterUpdateMethod(document, **kw)

    return conflict_list

  def _updateXupdateDel(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to remove elements. """
    if DEBUG:
      LOG("ERP5NodeConduit._updateXupdateDel", INFO, "doc = %s, xml = %s" %(document.getPath(),
                                                                            etree.tostring(xml, pretty_print=1),))
    conflict_list = []
    tag = xml.get('select').split('/')[-1]
    # this variable is used to retrieve the id of address and to not remove the
    # orginal tag (address, street, zip, city or country)

    # retrieve the previous xml etree through xpath
    xpath_expression = xml.get('select')
    selected_previous_xml = previous_xml.xpath(xpath_expression)
    try:
      previous_value = selected_previous_xml[0].text.encode('utf-8')
    except (IndexError, AttributeError):
      previous_value = None

    # specific work for address and address elements
    address_tag = tag.split('[')[0]
    if address_tag == "address":
      try:
        # work on the case: "/node/address[x]"
        address_index = int(tag.split('[')[-1].split(']')[0])
      except ValueError:
        # Work on the case: "/node/address"
        address_index = 1

      if address_index == 1:
        address_id = "default_address"
      else:
        # the XUPDATE begin by one, so one is default_address and the
        # first python index list is zero, so x-2
        address_index -= 2
        # address list of the person without default_address
        address_list = document.searchFolder(
            portal_type='Address',
            sort_on=(['id', 'ASC'], ),
            id={
              'query': 'default_address',
              'operator': '!=',
            },
        )
        address_id = address_list[address_index].getId()
      try:
        document.manage_delObjects(address_id)
      except (IndexError, BadRequest):
        conflict_list.append(self._generateConflict(document.getPhysicalPath(), tag, xml, None, None, kw.get('signature')))
        return conflict_list

    elif address_tag in ADDRESS_TAG_LIST:
      return self.checkAddressConflict(document, address_tag, xml, previous_value, None, kw.get('signature'))
    else:
      return self.checkConflict(tag, document, previous_value, None, kw.get('domain'), xml, kw.get('signature'))

    return conflict_list

  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to add elements. """
    if DEBUG:
      LOG("ERP5NodeConduit._updateXupdateInsertOrAdd", INFO, "doc = %s, xml = %s" %(document.getPath(),
                                                                                    etree.tostring(xml, pretty_print=1),))
    conflict_list = []
    keyword = {}
    default_address_created = False
    previous_value = ""

    for subnode in xml.getchildren():
      tag = subnode.attrib['name']
      new_value = subnode.text
      if new_value:
        new_value.encode("utf-8")
      if tag == 'address':
        address = document.newContent(portal_type='Address', int_index=10)
        keyword['address_mapping'] = True
        for subsubnode in subnode.getchildren():
          keyword[subsubnode.tag] = subsubnode.text
        self.editDocument(object=address, **keyword)
        if getattr(document, "default_address", None) is None and not default_address_created:
          # This will become the default address
          default_address_created = True
          address.edit(int_index=0)
          document.activate(activity="SQLQueue",
                            after_method_id="immediateReindexObject",
                            priority=5
                            ).manage_renameObject(address.getId(), "default_address")
      elif tag in ADDRESS_TAG_LIST:
        return self.checkAddressConflict(document, tag, xml, previous_value, new_value, kw.get('signature'))
      else:
        return self.checkConflict(tag, document, previous_value, new_value, kw.get('domain'), xml, kw.get('signature'))

    return conflict_list



  def checkConflict(self, tag, document, previous_value, new_value, domain, xml, signature):
    """
    Check conflict for each tag
    """
    if tag == "relation":
      return self._setRelation(document, previous_value, new_value, domain, xml, signature)
    else:
      if tag == "phone":
        current_value = document.get('default_telephone', None) and \
                        document.default_telephone.getTelephoneNumber("")
      elif tag == "cellphone":
        current_value = document.get('mobile_telephone', None) and \
                        document.mobile_telephone.getTelephoneNumber("")
      elif tag == "fax":
        current_value = document.get('default_fax', None) and \
                        document.default_fax.getTelephoneNumber("")
      elif tag == "birthday":
        current_value = str(document.getStartDate(""))
      elif tag == "email":
        current_value = str(document.getDefaultEmailText(""))
      else:
        try:
          current_value = getattr(document, tag)
        except AttributeError:
          current_value = None

      if current_value:
        current_value = current_value.encode('utf-8')
      if current_value not in [new_value, previous_value, None]:
        LOG("ERP5NodeConduit.checkConflict", ERROR, "Generating a conflict for tag %s, current is %s, previous is %s, new is %s" %(tag, current_value, previous_value, new_value))
        return [self._generateConflict(document.getPhysicalPath(), tag, xml, current_value, new_value, signature),]
      else:
        if new_value is None:
          # We are deleting some properties
          if tag == "fax":
            if getattr(document, "default_fax", None):
              document.manage_delObjects("default_fax")
          elif tag == "phone":
            if getattr(document, "default_telephone", None):
              document.manage_delObjects("default_telephone")
          elif tag == "cellphone":
            if getattr(document, "mobile_telephone", None):
              document.manage_delObjects("mobile_telephone")
          elif tag == "email":
            if getattr(document, "default_email", None):
              document.manage_delObjects("default_email")
          else:
            kw = {tag : new_value}
            self.editDocument(object=document, **kw)
        else:
          if tag == 'birthday' and isinstance(new_value, str) \
                 and len(new_value):
            new_value = DateTime(new_value)
          kw = {tag : new_value}
          self.editDocument(object=document, **kw)
      return []
