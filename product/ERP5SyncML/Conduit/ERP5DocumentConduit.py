# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Danièle Vanbaelinghem <daniele@gmail.com>
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
from Products.ERP5SyncML.SyncCode import SyncCode
from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

# Declarative security
security = ClassSecurityInfo()

class ERP5DocumentConduit(ERP5Conduit):
  """
  ERP5DocumentConduit provides two methods who permit to have the GID
  The Gid is composed by the title : "Reference-Version-Language"
  this class is made for unit test
  """

  security.declareProtected(Permissions.ModifyPortalContent, 'applyXupdate')
  def applyXupdate(self, object=None, xupdate=None, conduit=None, force=0,
                   simulate=0, reset=0, **kw):
    """
    Parse the xupdate and then it will call the conduit
    """
    conflict_list = []
    if isinstance(xupdate, (str, unicode)):
      xupdate = etree.XML(xupdate, parser=parser)
    xupdate = self.manageDataModification(xml_xupdate=xupdate,\
                   previous_xml=kw['previous_xml'], object=object,
                   simulate=simulate, reset=reset)
    for subnode in xupdate:
      sub_xupdate = self.getSubObjectXupdate(subnode)
      if subnode.xpath('name()') in self.XUPDATE_INSERT_OR_ADD:
        conflict_list += conduit.addNode(xml=sub_xupdate, object=object,
                                         force=force, simulate=simulate,
                                         reset=reset, **kw)['conflict_list']
      elif subnode.xpath('name()') in self.XUPDATE_DEL:
        conflict_list += conduit.deleteNode(xml=sub_xupdate, object=object,
                                            force=force, simulate=simulate,
					    reset=reset, **kw)
      elif subnode.xpath('name()') in self.XUPDATE_UPDATE:
        conflict_list += conduit.updateNode(xml=sub_xupdate, object=object,
                                            force=force, simulate=simulate,
					    reset=reset, **kw)

    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent, 'manageDataModification')
  def manageDataModification(self, xml_xupdate, previous_xml, object,
      simulate=None, reset=None):
    data_change = {}
    if previous_xml is not None:
      previous_xml = etree.XML(previous_xml)
    else:
      previous_xml = etree.XML(object.asXML())
    from copy import deepcopy
    xml_previous = deepcopy(previous_xml)
    #retrieve new data
    for subnode in xml_xupdate:
      sub_xupdate = self.getSubObjectXupdate(subnode)
      attribute = sub_xupdate.attrib.get('select', None)
      if 'block_data' in attribute:
        #retrieve path for the element and use on previous_xml
        prop_list = attribute.split('/')
        prop_id = prop_list[1]
        path_prop_id = '//' + prop_id
        if data_change.has_key(prop_id):
          xml = data_change[prop_id]
        else:
          xml = xml_previous.xpath(path_prop_id)[0]
        num = prop_list[2].split('[')[1].rstrip(']')
        if subnode.xpath('name()') in self.XUPDATE_DEL:
          request = 'block_data[@num = $num]'
          xml.remove(xml.xpath(request, num=num)[0]) 
          data_change[prop_id] = xml
          xml_xupdate.remove(subnode)
        elif subnode.xpath('name()') in self.XUPDATE_UPDATE:
          #retrieve element in previous_xml
          request = 'block_data[@num = $num]'
          element = xml.xpath(request, num=num)[0]
          if element is not None:
           element.text = subnode.text
          data_change[prop_id] = xml
          xml_xupdate.remove(subnode)
      elif subnode.xpath('name()') in self.XUPDATE_INSERT_OR_ADD:
        if self.getSubObjectDepth(subnode[0]) == 0:
          #check element have not sub object
          attribute = subnode.attrib.get('select', None)
          if 'block_data' in attribute:
            prop_id = attribute.split('/')[2]
            if prop_id in self.data_type_tag_list:
              path_prop_id = '//' + prop_id
              if data_change.has_key(prop_id):
                xml = data_change[prop_id]
              else:
                xml = xml_previous.xpath(path_prop_id)[0]
              for element in self.getXupdateElementList(subnode):
                name_element = element.attrib.get('name', None)
                if name_element:
                  for sub_element in element:
                    if sub_element.xpath('name()') in 'xupdate:attribute':
                      name_attribute = sub_element.attrib.get('name')
                      value_attribute = sub_element.text
                  block = etree.SubElement(xml, name_element)
                  block.set(name_attribute, value_attribute)
                  #change structure in xupdate because is bad formed
                  value = etree.tostring(element).split('</')[1].split('>')[1]
                  block.text = value
              data_change[prop_id] = xml
              xml_xupdate.remove(subnode)

    #apply modification
    if len(data_change) != 0:
      args = {}
      for key in data_change.keys():
        node = data_change[key]
        node.text = None
        data = self.convertXmlValue(node)
        args[key] = data
        args = self.getFormatedArgs(args=args)
        #XXX manage conflict
        if args != {} and (not simulate or reset):
          self.editDocument(object=object, **args)
          # It is sometimes required to do something after an edit
          if getattr(object, 'manage_afterEdit', None) is not None:
            object.manage_afterEdit()

    return xml_xupdate

  # Declarative security
  security = ClassSecurityInfo()
  def getGidFromObject(self, object):
    """
    return the Gid generate with the reference, object, language of the object
    """
    return "%s-%s-%s" %\
      (object.getReference(), object.getVersion(), object.getLanguage())

#  def getGidFromXML(self, xml):
#    """
#    return the Gid composed of FirstName and LastName generate with a peace of
#    xml
#    """
#    #to be defined
