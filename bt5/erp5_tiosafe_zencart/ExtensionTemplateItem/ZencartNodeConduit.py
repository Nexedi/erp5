# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Aurélien Calonne <aurel@nexedi.com>
#               Mohamadou Mbengue <mohamadou@nexedi.com>
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

from Products.ERP5SyncML.SyncMLConstant import XUPDATE_ELEMENT,\
     XUPDATE_INSERT_OR_ADD_LIST, XUPDATE_DEL, XUPDATE_UPDATE
from Products.ERP5TioSafe.Conduit.TioSafeNodeConduit import TioSafeNodeConduit
from Products.ERP5SyncML.Document.Conflict import Conflict
from zLOG import LOG
from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

ADDRESS_TAG_LIST = ['street', 'zip', 'city', 'country']
BILLING_TAG_LIST = ["fax", "phone", "cellphone"]

class ZencartNodeConduit(TioSafeNodeConduit):
  """
    This is the conduit use to synchonize TioSafe Persons
  """

  def applyXupdate(self, object=None, xupdate=None, previous_xml=None, request_parameter_dict=None,**kw):
    """ Parse the xupdate and then it will call the conduit. """
    LOG("calling applyXupdate", 300, request_parameter_dict)

    conflict_list = []
    request_parameter_dict = {}
    if isinstance(xupdate, (str, unicode)):
      xupdate = etree.XML(xupdate, parser=parser)
    if kw.get('conduit', None) is not None:
      if request_parameter_dict is None:
        request_parameter_dict = {'person_id': object.getId(), }
      if not request_parameter_dict.has_key("person_id"):
        request_parameter_dict['person_id'] = object.getId()
      for subnode in xupdate:
        LOG("calling applyXupdate", 300, request_parameter_dict)

        sub_conflict_list, sub_param_dict = self.updateNode(xml=self.getContextFromXpath(subnode, subnode.get('select')),
                                                            object=object,
                                                            previous_xml=previous_xml,
                                                            request_parameter_dict=request_parameter_dict,
                                                            **kw
                                                            )
        conflict_list += sub_conflict_list
        request_parameter_dict.update(sub_param_dict)

    if len(request_parameter_dict):
      if not request_parameter_dict.has_key('country'):
        # Always include country so that it does not get remove automatically
        request_parameter_dict["country"] = object.country

      # Once we got everything, call web service request
      LOG("calling update", 300, request_parameter_dict)
      object.context.person_module.updatePerson(**request_parameter_dict)
      # Update the brain as xml put in signature is generating from it
      new_document = object.context.person_module[object.getId()]
      object.updateProperties(new_document)
    LOG("returning the conflict_list", 300, [x.__dict__ for x in conflict_list])
    return conflict_list


  def updateNode(self, xml=None, object=None, previous_xml=None, force=False,
      simulate=False, reset=False, xpath_expression=None, request_parameter_dict=None, **kw):
    """
      This method browse the xml which allows to update data and update the
      correpsonging object.
    """
    LOG("calling updateNode", 300, request_parameter_dict)

    conflict_list = []
    if simulate or xml is None:
      return conflict_list

    xml = self.convertToXml(xml)
    # we have an xupdate xml
    if xml.xpath('name()') == 'xupdate:modifications':
      conflict_list += self.applyXupdate(
          object=object,
          xupdate=xml,
          conduit=self,
          previous_xml=previous_xml,
          force=force,
          simulate=simulate,
          reset=reset,
          request_parameter_dict=request_parameter_dict,
          **kw
      )
      return conflict_list
    # we may have only the part of an xupdate
    else:
      # previous_xml is required as an etree type
      if type(previous_xml) == str:
        previous_xml = etree.XML(previous_xml, parser=parser)

      if self.isProperty(xml):
        xpath = xml.xpath('name()')
        # XUPDATE_UPDATE -> update data or sub-object
        if xpath in XUPDATE_UPDATE:
          sub_conflict_list, sub_param_dict = self._updateXupdateUpdate(
              document=object,
              xml=xml,
              previous_xml=previous_xml,
              request_parameter_dict=request_parameter_dict,
              **kw
          )
        # XUPDATE_DEL -> delete data or sub-object
        elif xpath in XUPDATE_DEL:
          sub_conflict_list, sub_param_dict = self._updateXupdateDel(
              document=object,
              xml=xml,
              previous_xml=previous_xml,
              request_parameter_dict=request_parameter_dict,
              **kw
          )
        # XUPDATE_INSERT_OR_ADD_LIST -> add data or sub-object
        elif xpath in XUPDATE_INSERT_OR_ADD_LIST:
          sub_conflict_list, sub_param_dict = self._updateXupdateInsertOrAdd(
              document=object,
              xml=xml,
              previous_xml=previous_xml,
              request_parameter_dict=request_parameter_dict,
              **kw
          )
        conflict_list += sub_conflict_list

      return conflict_list, sub_param_dict


  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None,
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    """ We are not suppose to create new person into the plugin """
    LOG("_createContent", 300, "XXX")
    return None

  def _deleteContent(self, object=None, object_id=None):
    """ We do not delete person """
    raise NotImplementedError

  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, request_parameter_dict=None, **kw):
    """
      This method is called in updateNode and allows to work on the  update of
      elements.
    """
    LOG("calling updateXupdateUpdate", 300, request_parameter_dict)

    conflict_list = []
    xpath_expression = xml.get('select')
    tag = xpath_expression.split('/')[-1]
    value = xml.text

    # retrieve the previous xml etree through xpath
    previous_xml = previous_xml.xpath(xpath_expression)
    try:
      previous_value = previous_xml[0].text
    except IndexError:
      raise IndexError('Too little or too many value, only one is required for %s' % (
          previous_xml
      ))

    if previous_value is None:
      previous_value = ""

    conflicted = False

    if tag in ADDRESS_TAG_LIST:
      LOG("updating tag %s to %s" %(tag, value), 300, "")
      # There is just one address in oxatis, it is the billing one
      current_value = getattr(document, tag, '')
      if current_value not in [value, previous_value]:
        conflicted = True
      else:
        if tag == "country":
          mapping = document.context.getMappingFromCategory('region/%s' % value)
          value = mapping.split('/', 1)[-1]
          request_parameter_dict['country'] = value
        else:
          request_parameter_dict["%s" %(tag)] = value

    else:
      # Not specific tags
      current_value = getattr(document, tag, '')
      if current_value not in [value, previous_value]:
        conflicted = True
      # Update tag to specific name
      if tag in BILLING_TAG_LIST:
        tag = "%s" %(tag)
      request_parameter_dict[tag] = value

    # Return conflict if any
    if conflicted:
      conflict = Conflict(
          object_path=document.getPhysicalPath(),
          keyword=tag,
      )
      conflict.setXupdate(etree.tostring(xml, encoding='utf-8'))
      conflict.setLocalValue(current_value)
      conflict.setRemoteValue(value)
      conflict_list.append(conflict)
    LOG("update returns %s / %s" %(conflict_list, request_parameter_dict), 300, "")
    return conflict_list, request_parameter_dict


  def _updateXupdateDel(self, document=None, xml=None, previous_xml=None, request_parameter_dict=None, **kw):
    """ This method is called in updateNode and allows to remove elements. """
    tag = xml.get('select').split('/')[-1]
    LOG("calling updateXupdateDel", 300, request_parameter_dict)

    # specific work for address and address elements
    if tag in ADDRESS_TAG_LIST:
      # remove the corresponding address or the element of the address
      request_parameter_dict["%s" %(tag)] = ""
    elif tag in BILLING_TAG_LIST:
      request_parameter_dict["%s" %(tag)] = ""
    else:
      request_parameter_dict[tag] = ''
    LOG("delete returns %s / %s" %([], request_parameter_dict), 300, "")
    return [], request_parameter_dict


  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, request_parameter_dict=None, **kw):
    """ This method is called in updateNode and allows to add elements. """
    conflict_list = []
    
    for subnode in xml.getchildren():
      tag = subnode.attrib['name']
      value = subnode.text

      if tag == 'address':
        # We create a new address so telephones & fax must be resetted
        for tag in BILLING_TAG_LIST:
          if not request_parameter_dict.has_key("%s" %(tag)):
            request_parameter_dict["%s" %(tag)] = ""
        for subsubnode in subnode.getchildren():
          if subsubnode.tag == 'country':
            # through the mapping retrieve the country
            value = document.context.getMappingFromCategory(
                'region/%s' % subsubnode.text,
            ).split('/', 1)[-1]
          else:
            value = subsubnode.text
          request_parameter_dict["%s" %(subsubnode.tag)] = value
      elif tag in ADDRESS_TAG_LIST:
        # We only have one address in oxatis
        if tag == 'country':
          # through the mapping retrieve the country
          mapping = document.context.getMappingFromCategory('region/%s' % value)
          value = mapping.split('/', 1)[-1]
        request_parameter_dict["%s" %(tag)] = value
      elif tag in BILLING_TAG_LIST:
        tag = "%s" %(tag,)
        request_parameter_dict[tag] = value
      else:
        request_parameter_dict[tag] = value
    LOG("insert returns %s / %s" %(conflict_list, request_parameter_dict), 300, "")
    return conflict_list, request_parameter_dict


