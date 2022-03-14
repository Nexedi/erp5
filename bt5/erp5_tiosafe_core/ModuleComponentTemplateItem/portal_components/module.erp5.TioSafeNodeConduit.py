# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#               HervÃ© Poulain <herve@nexedi.com>
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

from erp5.component.module.TioSafeBaseConduit import TioSafeBaseConduit


class TioSafeNodeConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize TioSafe Persons
  """
  def __init__(self):
    self.xml_object_tag = 'node'

  def getObjectAsXML(self, object, domain): # pylint: disable=redefined-builtin
    return object.asXML()

  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None, # pylint: disable=redefined-builtin
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    # if exist namespace retrieve only the tag
    index = 0
    if xml.nsmap not in [None, {}]:
      index = -1
    # this dict contains the element to set to the person
    keyword = {}
    address_list = []
    # browse the xml
    for node in xml:
      # works on tags, no on comments
      if not isinstance(node.tag, str):
        continue
      # Retrieve the tag
      tag = node.tag.split('}')[index]
      if tag == 'address':
        # add the address
        address_keyword = {}
        for subnode in node.getchildren():
          # through the mapping retrieve the country
          if subnode.tag.split('{')[index] == 'country':
            mapping = object.getMappingFromCategory('region/%s' % subnode.text)
            country = mapping.split('/', 1)[-1]
            address_keyword[subnode.tag.split('{')[index]] = country
          else:
            address_keyword[subnode.tag.split('{')[index]] = subnode.text
        address_list.append(address_keyword)
      else:
        # XXX-AUREL : it might be necessary to use .encode('utf-8') here
        keyword[tag] = node.text

    # Create person once all xml has bee browsed
    object.person_module.createPerson(**keyword)
    # XXX-AUREL : following call must be changed
    new_id = object.IntegrationSite_lastID(type='Person')[0].getId()

    # Then create addresses
    for address_keyword in address_list:
      object.person_module.createPersonAddress(person_id=str(new_id), **address_keyword)

    return object.person_module(person_id=new_id)[0]


  def _deleteContent(self, object=None, object_id=None, **kw): # pylint: disable=redefined-builtin
    """ We do not delete nodes """
    pass


  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, **kw):
    """
      This method is called in updateNode and allows to work on the  update of
      elements.
    """
    conflict_list = []
    xpath_expression = xml.get('select')
    tag = xpath_expression.split('/')[-1]
    value = xml.text

    # retrieve the previous xml etree through xpath
    previous_xml = previous_xml.xpath(xpath_expression)
    try:
      previous_value = previous_xml[0].text
    except IndexError:
      raise IndexError(
        'Too little or too many value, only one is required for %s'
        % previous_xml
      )

    # check if it'a work on person or on address
    if tag in ['street', 'zip', 'city', 'country']:
      try:
        # work on the case: "/node/address[x]"
        address_index = \
            int(xpath_expression.split('address[')[-1].split(']')[0]) - 1
      except ValueError:
        # Work on the case: "/node/address"
        address_index = 0

      # build the address list
      address_list = document.context.person_module.getPersonAddressList(
          person_id=document.getId(),
      )
      # FIXME: Is the sort can be removed ???
      # Build a list of tuple which contains :
      #   - first, the title build to realise the sort
      #   - the second element is the brain itself
      sorted_address_list = [
          (' '.join([address.street,
                     address.zip,
                     address.city,
                     address.country]),
           address)
          for address in address_list]
      # sorted_address_list.sort()
      address_list = [t[1] for t in sorted_address_list]

      try:
        address = address_list[address_index]
      except IndexError:
        # create and fill a conflict when the integration site value, the erp5
        # value and the previous value are differents
        return self._generateConflict(path=document.getPhysicalPath(),
                                      tag=tag,
                                      xml=xml,
                                      current_value=None,
                                      new_value=value,
                                      signature=kw['domain'],
                                      )

      current_value = getattr(address, tag, None)
      if tag == 'country':
        current_value = document.context.getMappingFromCategory('region/%s' % current_value)
      if current_value not in [value, previous_value]:
        # create and fill a conflict when the integration site value, the erp5
        # value and the previous value are differents
        conflict_list.append(self._generateConflict(path=document.getPhysicalPath(),
                                      tag=tag,
                                      xml=xml,
                                      current_value=current_value,
                                      new_value=value,
                                      signature=kw['domain'],
                                      ))
      else:
        # set the keyword dict which defines what will be updated
        keyword = {
            'address_id': address.getId(),
            'person_id': document.getId(),
        }
        if tag == 'country':
          # through the mapping retrieve the country
          #mapping = document.context.getMappingFromCategory('region/%s' % value)
          value = current_value.split('/', 1)[-1]
        keyword[tag] = value
        document.context.person_module.updatePersonAddress(**keyword)
    else:
      assert tag == 'birthday', tag
      current_value = getattr(document, tag)
      assert current_value is not None, current_value

      # create and fill a conflict when the integration site value, the erp5
      # value and the previous value are differents
      if value != current_value != previous_value:
        conflict_list.append(self._generateConflict(path=document.getPhysicalPath(),
                                      tag=tag,
                                      xml=xml,
                                      current_value=current_value,
                                      new_value=value,
                                      signature=kw['domain'],
                                      ))
      else:
        # XXX: when the DateTime format will be required to sync date
        #   - 1 - retrieve the format through the integration site
        #   - 2 - through using of DateTime build the date and render it
#        if tag == 'birthday':
#          integration_site = self.getIntegrationSite(kw.get('domain'))
#          date_format = integration_site.getDateFormat()
#          # build the required format
#          format = dict_format[date_format] -> render "%Y/%m/%d", ...
#          value = DateTime(value).strftime(format)
        keyword = {'person_id': document.getId(), tag: value, }
        document.context.person_module.updatePerson(**keyword)

    new_document = document.context.person_module[document.getId()]
    document.updateProperties(new_document)
    return conflict_list


  def _updateXupdateDel(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to remove elements. """
    conflict_list = []
    tag = xml.get('select').split('/')[-1]
    # this variable is used to retrieve the id of address and to not remove the
    # orginal tag (address, street, zip, city or country)
    tag_for_id = tag

    # specific work for address and address elements
    if tag.split('[')[0] in ['address', 'street', 'zip', 'city', 'country']:
      # work on the good part of the xml to retrieve the address id
      if tag_for_id.split('[')[0] != 'address':
        tag_for_id = xml.get('select')

      try:
        # work on the case: "/node/address[x]"
        address_index = int(tag_for_id.split('[')[-1].split(']')[0]) - 1
      except ValueError:
        # Work on the case: "/node/address"
        address_index = 0

      # build the address list
      address_list = document.context.person_module.getPersonAddressList(
          person_id=document.getId(),
      )
      # FIXME: Is the sort can be removed ???
      # Build a list of tuple which contains :
      #   - first, the title build to realise the sort
      #   - the second element is the brain itself
      sorted_address_list = [
          (' '.join([
                  getattr(address, i, '')
                  for i in ['street', 'zip', 'city','country']]
          ), address)
          for address in address_list
      ]
      sorted_address_list.sort()
      address_list = [t[1] for t in sorted_address_list]

      try:
        address = address_list[address_index]
      except IndexError:
        # create and fill a conflict when the integration site value, the erp5
        # value and the previous value are differents
        # XXX-Aurel : is it necessary to generate a conflict as
        # it seems the address has already been deleted ?
        return self._generateConflict(path=document.getPhysicalPath(),
                                      tag=tag,
                                      xml=xml,
                                      current_value=None,
                                      new_value=None,
                                      signature=kw['domain'],
                                      )

      # remove the corresponding address or the element of the address
      keyword = {'person_id': document.getId(), 'address_id': address.getId()}
      if tag.split('[')[0] == 'address':
        document.context.person_module.deletePersonAddress(**keyword)
      else:
        # set the keyword dict which defines what will be updated
        keyword[tag] = 'NULL'
        document.context.person_module.updatePersonAddress(**keyword)
    else:
      keyword = {'person_id': document.getId(), tag: 'NULL', }
      document.context.person_module.updatePerson(**keyword)

    # it always return conflict_list but it's empty
    new_document = document.context.person_module[document.getId()]
    document.updateProperties(new_document)
    return conflict_list


  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to add elements. """
    conflict_list = []

    for subnode in xml.getchildren():
      tag = subnode.attrib['name']
      value = subnode.text

      if tag == 'address':
        keyword = {'person_id': document.getId(), }
        for subsubnode in subnode.getchildren():
          if subsubnode.tag == 'country':
            # through the mapping retrieve the country
            keyword[subsubnode.tag] = document.context.getMappingFromCategory(
                'region/%s' % subsubnode.text,
            ).split('/', 1)[-1]
          else:
            keyword[subsubnode.tag] = subsubnode.text
        document.context.person_module.createPersonAddress(**keyword)
      elif tag in ['street', 'zip', 'city', 'country']:
        try:
          # work on the case: "/node/address[x]"
          address_index = int(xml.get('select').split('address[')[-1].split(']')[0]) - 1
        except ValueError:
          # Work on the case: "/node/address"
          address_index = 0

        # build the address list
        address_list = document.context.person_module.getPersonAddressList(
            person_id=document.getId(),
        )
        # FIXME: Is the sort can be removed ???
        # Build a list of tuple which contains :
        #   - first, the title build to realise the sort
        #   - the second element is the brain itself
        sorted_address_list = [
            (' '.join([
                    getattr(address, i, '')
                    for i in ['street', 'zip', 'city','country']]
            ), address)
            for address in address_list
        ]
        sorted_address_list.sort()
        address_list = [t[1] for t in sorted_address_list]

        try:
          address = address_list[address_index]
        except IndexError:
          # create and fill a conflict when the integration site value, the erp5
          # value and the previous value are differents
          return self._generateConflict(path=document.getPhysicalPath(),
                                        tag=tag,
                                        xml=xml,
                                        current_value=None,
                                        new_value=value,
                                        signature=kw['domain'],
                                      )

        # set the keyword dict which defines what will be updated
        keyword = {
            'person_id': document.getId(),
            'address_id': address.getId(),
        }
        if tag == 'country':
          # through the mapping retrieve the country
          mapping = document.context.getMappingFromCategory('region/%s' % value)
          value = mapping.split('/', 1)[-1]
        keyword[tag] = value
        document.context.person_module.updatePersonAddress(**keyword)
      else:
        # XXX: when the DateTime format will be required to sync date
        #   - 1 - retrieve the format through the integration site
        #   - 2 - through using of DateTime build the date and render it
#        if tag == 'birthday':
#          integration_site = self.getIntegrationSite(kw.get('domain'))
#          date_format = integration_site.getDateFormat()
#          # build the required format
#          format = dict_format[date_format] -> render "%Y/%m/%d", ...
#          value = DateTime(value).strftime(format)
        keyword = {'person_id': document.getId(), tag:value, }
        document.context.person_module.updatePerson(**keyword)


    new_document = document.context.person_module[document.getId()]
    document.updateProperties(new_document)
    return conflict_list
