# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Aurelien Calonne <aurel@nexedi.com>
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
from zLOG import LOG, INFO
from erp5.component.module.ERP5Conduit import ERP5Conduit
from lxml import etree
from copy import deepcopy
parser = etree.XMLParser(remove_blank_text=True)

XUPDATE_INSERT_LIST = ('xupdate:insert-after', 'xupdate:insert-before')

class TioSafeBaseConduit(ERP5Conduit):
  """
    This class provides some tools used by different TioSafe Conduits.
  """

  def addNode(self, xml=None, object=None, sub_object=None, reset=None,
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
    LOG('TioSafeBaseConduit.addNode', INFO, '\n%s' % etree.tostring(xml, pretty_print=True))
    if xml is None:
      return {'conflict_list': conflict_list, 'object': sub_object}
    # In the case where this new node is a object to add
    xpath_expression = xml.get('select')
    if xml.xpath('name()') in XUPDATE_INSERT_OR_ADD_LIST and\
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

  def replaceIdFromXML(self, xml, attribute_name, new_id, as_string=True):
    """
      return a xml with id replace by a new id
    """
    if isinstance(xml, str):
      xml = etree.XML(xml, parser=parser)
    else:
      xml = deepcopy(xml)
    if as_string:
      return etree.tostring(xml)
    return xml

  def applyXupdate(self, object=None, xupdate=None, previous_xml=None, **kw):
    """ Parse the xupdate and then it will call the conduit. """
    conflict_list = []
    if isinstance(xupdate, (str, unicode)):
      xupdate = etree.XML(xupdate, parser=parser)
    if kw.get('conduit', None) is not None:
      for subnode in xupdate:
        conflict_list += self.updateNode(
            xml=self.getContextFromXpath(subnode, subnode.get('select')),
            object=object,
            previous_xml=previous_xml,
            **kw
        )
    return conflict_list

  def getIntegrationSite(self, sync_object):
    """
    Return the integration site based on the link with the pub/sub
    """
    if getattr(self, 'integration_site', None) is None:
      related_object_list = [x.getObject() for x in sync_object.Base_getRelatedObjectList()]
      if len(related_object_list) != 1:
        raise ValueError("Impossible to find related object to %s : %s" %(sync_object.getPath(), related_object_list))
      integration_site = related_object_list[0].getParentValue()
      if integration_site.getPortalType() != "Integration Site":
        raise ValueError("Did not get an Integration Site object instead %s : %s" %(integration_site.getPortalType(),
                                                                                     integration_site.getPath()))
      self.integration_site = integration_site
    return self.integration_site

  def getSynchronizationObjectForType(self, sync_object, object_type, synchronization_type):
    """
      This method provides a Publication or Subscription base on the relation
      set in integration site
    """
    site = self.getIntegrationSite(sync_object)
    module_id = "%s_module" %(object_type.lower())
    module = getattr(site, module_id, None)
    if module is None:
      raise ValueError("Impossible to find integration module object on %s for %s" %(site.getPath(), object_type))

    if synchronization_type == "publication":
      return module.getSourceSectionValue()
    elif synchronization_type == "subscription":
      return module.getDestinationSectionValue()
    else:
      raise ValueError('Unknown type %s' %(synchronization_type,))

  def updateNode(self, xml=None, object=None, previous_xml=None, force=False,
      simulate=False, reset=False, xpath_expression=None, **kw):
    """
      This method browse the xml which allows to update data and update the
      correpsonging object.
    """
    conflict_list = []
    if simulate:
      return conflict_list
    if xml is None:
      return {'conflict_list': conflict_list, 'object': object}
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
          **kw
      )
    # we may have only the part of an xupdate
    else:
      # previous_xml is required as an etree type
      if type(previous_xml) == str:
        previous_xml = etree.XML(previous_xml, parser=parser)

      if self.isProperty(xml):
        xpath = xml.xpath('name()')
        # XUPDATE_UPDATE -> update data or sub-object
        if xpath in XUPDATE_UPDATE:
          conflict_list += self._updateXupdateUpdate(
              document=object,
              xml=xml,
              previous_xml=previous_xml,
              **kw
          )
        # XUPDATE_DEL -> delete data or sub-object
        elif xpath in XUPDATE_DEL:
          conflict_list += self._updateXupdateDel(
              document=object,
              xml=xml,
              previous_xml=previous_xml,
              **kw
          )
        # XUPDATE_INSERT_OR_ADD_LIST -> add data or sub-object
        elif xpath in XUPDATE_INSERT_OR_ADD_LIST:
          conflict_list += self._updateXupdateInsertOrAdd(
              document=object,
              xml=xml,
              previous_xml=previous_xml,
              **kw
          )
    return conflict_list

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

