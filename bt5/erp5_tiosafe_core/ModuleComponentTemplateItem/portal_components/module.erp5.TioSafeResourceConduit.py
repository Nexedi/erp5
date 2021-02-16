# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.Utils import cartesianProduct
from erp5.component.module.TioSafeBaseConduit import TioSafeBaseConduit
from lxml import etree
from zLOG import LOG

class TioSafeResourceConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize TioSafe Resources
  """
  def __init__(self):
    self.xml_object_tag = 'resource'

  def getObjectAsXML(self, object, domain): # pylint: disable=redefined-builtin
    return object.asXML()

  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None, # pylint: disable=redefined-builtin
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    LOG("TioSafeNodeConduit._createConten", 300, "xml = %s" %(etree.tostring(xml, pretty_print=1),))

    # if exist namespace retrieve only the tag
    index = 0
    if xml.nsmap not in [None, {}]:
      index = -1
    # init the new_id of the product and the checker of the creation
    new_id = None
    # this dict contains the element to set to the product
    keyword = {}
    # this dict will contains a list of tuple (base_category, vairiation)
    variation_dict = {}

    resource_type = self.getObjectType(xml=xml).strip()

    # browse the xml
    for node in xml:
      # works on tags, not on comments
      if not isinstance(node.tag, str):
        continue
      tag = node.tag.split('}')[index]
      LOG("browsing tag %s, value %s" %(tag, node.text), 300, "keyword = %s" %(keyword,))
      if tag == 'category':
        # retrieve through the mapping the base category and the variation
        mapping = object.getMappingFromCategory(node.text)
        base_category, variation = mapping.split('/', 1)
        variation_dict.setdefault(base_category, []).append(variation)
      else:
        keyword[tag] = node.text.encode('utf-8')

    # Create the product at the end of the xml browsing
    create_method_id = "create%s" %(resource_type,)
    create_method = getattr(object, create_method_id, None)
    if create_method is not None:
      create_result = create_method(**keyword)
    else:
      raise ValueError('Impossible to find a create method named %s and object %s' %(create_method_id, object.getPath(),))
    if len(create_result):
      # We suppose the id of the object created was returned by the plugin
      new_id = create_result[0].getId()
    else:
      # We must ask for the id of the object previously created
      # XXX-AUREL : this must be changed to use gid definition instead
      new_id = object.IntegrationSite_lastID(type=resource_type)[0].getId()

    # create the full variations in the integration site
    if variation_dict:
      # XXX-Aurel : This is too specific to prestashop, must be moved and
      # replaced by generic code

      # the cartesianProduct requires to build a list of list of variations
      builder_variation_list = []
      for key, value in variation_dict.items():
        variation_list = []
        for variation in value:
          variation_list.append((key, variation))
        builder_variation_list.append(variation_list)

      # build and browse the list of variations
      variation_list = cartesianProduct(builder_variation_list)
      for var_list in variation_list:
        object.createProductAttribute(id_product=new_id)
        id_product_attribute = object.IntegrationSite_lastID(
            type='Product Attribute',
        )[0].getId()
        for variation in var_list:
          object.createProductAttributeCombination(
              id_product_attribute=id_product_attribute,
              id_product=new_id,
              base_category=variation[0],
              variation=variation[1],
            )

    return object[new_id]


  def _deleteContent(self, object=None, object_id=None, **kw): # pylint: disable=redefined-builtin
    """ This method allows to remove a product in the integration site """
    delete_method_id = "deleteProduct" # XXX-AUREL : must find a way to fix this
    delete_method = getattr(object, delete_method_id, None)
    if delete_method is not None:
      return delete_method(product_id=object_id)
    else:
      raise ValueError('Impossible to find a delete method named %s and object %s' %(delete_method_id, object.getPath(),))


  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, **kw):
    """
      This method is called in updateNode and allows to work on the update of
      elements.
    """
    conflict_list = []
    xpath_expression = xml.get('select')
    tag = xpath_expression.split('/')[-1]
    new_value = xml.text

    # retrieve the previous xml etree through xpath
    previous_xml = previous_xml.xpath(xpath_expression)
    try:
      previous_value = previous_xml[0].text
    except IndexError:
      raise ValueError(
        'Too little or too many value, only one is required for %s'
        % previous_xml
      )

    if isinstance(previous_value, unicode):
      previous_value = previous_value.encode('utf-8')
    if isinstance(new_value, unicode):
      new_value = new_value.encode('utf-8')

    # check if it'a work on product or on categories
    if tag.split('[')[0] == 'category':
      # call the method which allows to work on a specific part, the update of
      # categories
      conflict_list += self._updateCategory(document, xml, previous_value, signature=kw['signature'])
    else:
      # getter used to retrieve the current values and to check conflicts
      property_list = ['sale_price', 'purchase_price', 'ean13']
      getter_value_dict = dict(zip(
        property_list, [
          getattr(document, prop, None)
          for prop in property_list
        ]
      ))

      # create and fill a conflict when the integration site value, the erp5
      # value and the previous value are differents
      current_value = getter_value_dict[tag]
      if isinstance(current_value, float):
        current_value = '%.6f' % current_value
      if isinstance(current_value, unicode):
        current_value = current_value.encode('utf-8')
      if current_value not in [new_value, previous_value]:
        conflict_list.append(self._generateConflict(path=document.getPhysicalPath(),
                                      tag=tag,
                                      xml=xml,
                                      current_value=current_value,
                                      new_value=new_value,
                                      signature=kw['domain'],
                                      ))
      else:
        keyword = {'product_id': document.getId(), tag: new_value , }
        document.context.product_module.updateProduct(**keyword)

    new_document = document.context.product_module[document.getId()]
    document.updateProperties(new_document)
    return conflict_list


  def _updateXupdateDel(self, document=None, object_xml=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to remove elements. """
    conflict_list = []
    tag = xml.get('select').split('/')[-1]
    integration_site = document.context.getParentValue()
    if tag.split('[')[0] == 'category':
      # retrieve the previous xml etree through xpath
      selected_previous_xml = previous_xml.xpath(tag)
      try:
        previous_value = integration_site.getMappingFromCategory(
            selected_previous_xml[0].text,
        )
      except IndexError:
        raise IndexError(
          'Too little or too many value, only one is required for %s'
          % previous_xml
        )
      LOG("TiosafeResourceConduit.del", 300, "will remove category %s from %s" %(tag, previous_xml.text))
      # retrieve the current value to check if exists a conflict
      current_value = etree.XML(object_xml).xpath(tag)[0].text
      mapped_current_value = integration_site.getMappingFromCategory(current_value)

      # work on variations
      variation_brain_list = document.context.getProductCategoryList()
      for brain in variation_brain_list:
        LOG("TioSafeResourceConduit.delete", 300,
            "comparing brain %s with current %s and previous %s" %(brain.category,
                                                                   mapped_current_value,
                                                                   previous_value),)
        if brain.category == mapped_current_value and previous_value == mapped_current_value:
          base_category, variation = mapped_current_value.split('/', 1)
          document.context.product_module.deleteProductAttributeCombination(
              product_id=document.getId(),
              base_category=base_category,
              variation=variation,
          )
          break
      else:
        # previous value different from current value
        self._generateConflict(document.getPhysicalPath(),
                               tag,
                               xml,
                               previous_value,
                               current_value,
                               kw["signature"])
    else:
      keyword = {'product_id': document.getId(), tag: 'NULL' , }
      document.context.product_module.updateProduct(**keyword)

    new_document = document.context.product_module[document.getId()]
    document.updateProperties(new_document)
    return conflict_list


  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to add elements. """
    conflict_list = []
    integration_site = document.context.getParentValue()

    # browse subnode of the insert and check what will be create
    for subnode in xml.getchildren():
      new_tag = subnode.attrib['name']
      new_value = subnode.text
      if new_tag == 'category':
        mapping = integration_site.getMappingFromCategory(new_value)
        base_category, variation = mapping.split('/', 1)
        # retrieve the variations which have a different axe from the updated
        # and build the cartesian variation for this new variations
        external_axe_list = [
            tuple(x.category.split('/', 1))
            for x in document.context.getProductCategoryList()
            if x.category.split('/', 1)[0] != base_category
        ]
        builder_variation_list = [
            [(base_category, variation)], external_axe_list,
        ]
        variation_list = cartesianProduct(builder_variation_list)
        for var_list in variation_list:
          document.context.product_module.createProductAttribute(
              id_product=document.getId(),
          )
          id_product_attribute = document.context.IntegrationSite_lastID(
              type='Product Attribute',
          )[0].getId()
          for variation in var_list:
            document.context.product_module.createProductAttributeCombination(
                id_product_attribute=id_product_attribute,
                id_product=document.getId(),
                base_category=variation[0],
                variation=variation[1],
              )
      else:
        keyword = {'product_id': document.getId(), new_tag: new_value, }
        document.context.product_module.updateProduct(**keyword)

    new_document = document.context.product_module[document.getId()]
    document.updateProperties(new_document)
    return conflict_list


  def _updateCategory(self, document=None, xml=None, previous_value=None, signature=None):
    """ This method allows to update a Category in the Integration Site. """
    conflict_list = []
    return conflict_list

