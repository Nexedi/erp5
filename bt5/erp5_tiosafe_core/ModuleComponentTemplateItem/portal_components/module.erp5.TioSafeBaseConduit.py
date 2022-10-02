# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Aurélien Calonne <aurel@nexedi.com>
#               Hervé Poulain <herve@nexedi.com>
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

from erp5.component.module.SyncMLConstant import XUPDATE_INSERT_OR_ADD_LIST, \
     XUPDATE_DEL, XUPDATE_UPDATE
from Products.ERP5Type.XMLExportImport import MARSHALLER_NAMESPACE_URI
from zLOG import LOG, INFO, WARNING
from erp5.component.module.ERP5Conduit import ERP5Conduit
from lxml import etree
from copy import deepcopy
from six import string_types as basestring
parser = etree.XMLParser(remove_blank_text=True)

XUPDATE_INSERT_LIST = ('xupdate:insert-after', 'xupdate:insert-before')

ADDRESS_TAG_LIST = ('street', 'zip', 'city', 'country')

class TioSafeBaseConduit(ERP5Conduit):
  """
    This class provides some tools used by different TioSafe Conduits.
  """

  def replaceIdFromXML(self, xml, attribute_name, new_id, as_string=True):
    """XXX argument old_attribute_name is missing
    XXX name of method is not good, because content is not necessarily XML
    return a xml with id replaced by a new id
    """
    if isinstance(xml, unicode):
      xml = xml.encode("utf-8")
    if isinstance(xml, basestring):
      xml = etree.XML(str(xml), parser=parser)
    else:
      # copy of xml object for modification
      xml = deepcopy(xml)
    object_element = xml.find('object')
    if object_element and object_element != -1:
      if attribute_name == 'id':
        del object_element.attrib['gid']
      else:
        del object_element.attrib['id']
      object_element.attrib[attribute_name] = new_id
    if as_string:
      return etree.tostring(xml, pretty_print=True, encoding="utf-8")
    return xml

  def _generateConflict(self, path, tag, xml, current_value, new_value, signature):
    """
    Generate the conflict object
    """
    LOG("_generateConflict", 300, "path %s\n, tag %s\n, xml %s\n, current_value %s\n, new_value %s\n" %(path, tag, xml, current_value, new_value))
    conflict = signature.newContent(portal_type='SyncML Conflict',
                                    origin=path,
                                    property_id=tag,
                                    local_value=current_value,
                                    remote_value=new_value,
                                    diff_chunk=etree.tostring(xml, encoding='utf-8')
                                    )
    return conflict

  def addNode(self, xml=None, object=None, sub_object=None, reset=None, # pylint: disable=redefined-builtin
              simulate=None, **kw):
    """
    A node is added

    xml : the xml wich contains what we want to add

    object : from where we want to add something

    previous_xml : the previous xml of the object, if any

    force : apply updates even if there's a conflict

    This fucntion returns conflict_list, wich is of the form,
    [conflict1,conflict2,...] where conclict1 is of the form :
    [object.getPath(),keyword,local_and_actual_value,subscriber_value]
    """
    conflict_list = []
    xml = self.convertToXml(xml)
    LOG('TioSafeBaseConduit.addNode', INFO, 'object path:%r' %(object.getPath(),))
    LOG('TioSafeBaseConduit.addNode', INFO, '\n%s' % etree.tostring(xml, pretty_print=True))
    if xml is None:
      return {'conflict_list': conflict_list, 'object': sub_object}
    # In the case where this new node is a object to add
    xpath_expression = xml.get('select')
    if xml.xpath('name()') in XUPDATE_INSERT_OR_ADD_LIST and \
           MARSHALLER_NAMESPACE_URI not in xml.nsmap.values():
      # change the context according select expression
      get_target_parent = xml.xpath('name()') in XUPDATE_INSERT_LIST
      context = self.getContextFromXpath(object, xpath_expression,
                                         get_target_parent=get_target_parent)
      for element in xml.findall('{%s}element' % xml.nsmap['xupdate']):
        xml = self.getElementFromXupdate(element)
        conflict_list += self.addNode(xml=xml, object=context, **kw)\
                                                              ['conflict_list']
    elif xml.xpath('local-name()') == self.xml_object_tag:
      sub_object = self._createContent(xml=xml,
                                      object=object,
                                      sub_object=sub_object,
                                      reset=reset,
                                      simulate=simulate,
                                      **kw)
    else:
      conflict_list += self.updateNode(xml=xml, object=object, reset=reset,
                                                       simulate=simulate, **kw)
    # We must returns the object created
    return {'conflict_list':conflict_list, 'object': sub_object}


  def applyXupdate(self, object=None, object_xml=None, xupdate=None, previous_xml=None, **kw): # pylint: disable=redefined-builtin
    """ Parse the xupdate and then it will call the conduit. """
    conflict_list = []
    if isinstance(xupdate, unicode):
      xupdate = xupdate.encode("utf-8")
    if isinstance(xupdate, basestring):
      xupdate = etree.XML(xupdate, parser=parser)
    if kw.get('conduit', None) is not None:
      for subnode in xupdate:
        conflict_list += self.updateNode(
            xml=self.getContextFromXpath(subnode, subnode.get('select')),
            object=object,
            object_xml=object_xml,
            previous_xml=previous_xml,
            **kw
        )
    return conflict_list

  def getIntegrationSite(self, sync_object):
    """
    Return the integration site based on the link with the pub/sub
    """
    if getattr(self, 'integration_site', None) is None:
      if sync_object.getParentValue().getPortalType() == 'SyncML Publication':
        related_object_list = [x.getObject() for x in sync_object.getParentValue().Base_getRelatedObjectList()]
      else:
        related_object_list = [x.getObject() for x in sync_object.Base_getRelatedObjectList()]
      if len(related_object_list) != 1:
        raise ValueError("Impossible to find related object to %s : %s" %(sync_object.getPath(), related_object_list))
      integration_site = related_object_list[0].getParentValue()
      if integration_site.getPortalType() != "Integration Site":
        raise ValueError("Did not get an Integration Site object instead %s : %s" %(integration_site.getPortalType(),
                                                                                     integration_site.getPath()))
      self.integration_site = integration_site
    return self.integration_site

  def getSynchronizationObjectListForType(self, sync_object, object_type, synchronization_type):
    """
      This method provides a Publication or Subscription base on the relation
      set in integration site
    """
    site = self.getIntegrationSite(sync_object)
    module_id = "%s_module" %(object_type.lower())
    module_list = []
    for module in site.contentValues(portal_type="Integration Module"):
      if module_id in module.getId():
        module_list.append(module)

    result_list = []
    for module in module_list:
      if synchronization_type == "publication":
        result_list.append(module.getSourceSectionValue())
      elif synchronization_type == "subscription":
        result_list.append(module.getDestinationSectionValue())
      else:
        raise ValueError('Unknown type %s' %(synchronization_type,))

    return result_list

  def getObjectAsXML(self, object, domain): # pylint: disable=redefined-builtin
    """
    This method must be implemented by subclasses as the way to generate the
    XML is specific to each side

    XML of document must be generated at the beginning as the xml exchanged
    by syncml always refer to it (exemple of item in a list of tag). So if
    it has to be regenerated later, generated XML might differ from the original
    """
    raise NotImplementedError

  def updateNode(self, xml=None, object=None, object_xml=None, previous_xml=None, force=False, # pylint: disable=redefined-builtin
      simulate=False, reset=False, xpath_expression=None, **kw):
    """
      This method browse the xml which allows to update data and update the
      correpsonging object.
    """
    conflict_list = []
    if xml is None:
      return {'conflict_list': conflict_list, 'object': object}
    xml = self.convertToXml(xml)
    if object_xml is None:
      object_xml = self.getObjectAsXML(object, kw["domain"].getPath())
    # we have an xupdate xml
    if xml.xpath('name()') == 'xupdate:modifications':
      conflict_list += self.applyXupdate(
          object=object,
          object_xml=object_xml,
          xupdate=xml,
          conduit=self,
          previous_xml=previous_xml,
          force=force,
          simulate=simulate,
          reset=reset,
          **kw
      )
    # we may have only the part of an xupdate
    else:
      # previous_xml is required as an etree type
      if isinstance(previous_xml, str):
        previous_xml = etree.XML(previous_xml, parser=parser)

      if self.isProperty(xml):
        xpath = xml.xpath('name()')
        # XUPDATE_UPDATE -> update data or sub-object
        if xpath in XUPDATE_UPDATE:
          conflict_list += self._updateXupdateUpdate(
              document=object,
              object_xml=object_xml,
              xml=xml,
              previous_xml=previous_xml,
              **kw
          )
        # XUPDATE_DEL -> delete data or sub-object
        elif xpath in XUPDATE_DEL:
          conflict_list += self._updateXupdateDel(
              document=object,
              object_xml=object_xml,
              xml=xml,
              previous_xml=previous_xml,
              **kw
          )
        # XUPDATE_INSERT_OR_ADD_LIST -> add data or sub-object
        elif xpath in XUPDATE_INSERT_OR_ADD_LIST:
          conflict_list += self._updateXupdateInsertOrAdd(
              document=object,
              object_xml=object_xml,
              xml=xml,
              previous_xml=previous_xml,
              **kw
          )
    self.afterUpdateMethod(object, **kw)
    return conflict_list

  def afterUpdateMethod(self, object, **kw): # pylint: disable=redefined-builtin
    """ This method is for actions that has to be done just after object
    update and which required to have synchronization parameters
    """
    pass

  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, **kw):
    """
      This method is called in updateNode and allows to work on the update of
      elements.
    """
    return []

  def _updateXupdateDel(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to remove elements. """
    return []

  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to add elements. """
    return []

  def getObjectType(self, xml):
    """ Return the portal type from the xml. """
    try:
      return xml.attrib['type'].split('/')[-1]
    except KeyError:
      LOG("TioSafeBaseConduit.getObjectType", WARNING, "No type attribute for the xml : %s" % (
        etree.tostring(xml,pretty_print=True),))
      return

