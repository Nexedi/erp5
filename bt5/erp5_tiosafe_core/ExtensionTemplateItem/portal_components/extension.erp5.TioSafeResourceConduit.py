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
from erp5.component.document.SyncMLConflict import SyncMLConflict as Conflict
from lxml import etree
from zLOG import LOG
class TioSafeResourceConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize TioSafe Products
  """
  def __init__(self):
    self.xml_object_tag = 'resource'


  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None,
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    LOG("TioSafeNodeConduit._createConten", 300, "xml = %s" %(etree.tostring(xml, pretty_print=1),))

    # if exist namespace retrieve only the tag
    index = 0
    if xml.nsmap not in [None, {}]:
      index = -1
    # init the new_id of the product and the checker of the creation
    new_id = None
    product_created = False
    # this dict contains the element to set to the product
    keyword = {}
    # this dict will contains a list of tuple (base_category, vairiation)
    variation_dict = {}

    # browse the xml
    for node in xml:
      # works on tags, no on comments
      if type(node.tag) is not str:
        continue
      tag = node.tag.split('}')[index]
      LOG("browsing tag %s, value %s" %(tag, node.text), 300, "keyword = %s" %(keyword,))
      if tag == 'category':
        # retrieve through the mapping the base category and the variation
        mapping = object.getMappingFromCategory(node.text)
        base_category, variation = mapping.split('/', 1)
        category_params = {
            'document': object,
            'base_category': base_category,
            'variation': variation,
        }
        # if exists the variation set it to the builder dict
        if self.checkCategoryExistency(**category_params):
          variation_dict.setdefault(base_category, []).append(variation)
      else:
        keyword[tag] = node.text

    # Create the product at the end of the xml browsing
    object.product_module.createProduct(**keyword)
    # XXX-AUREL : this must be changed to use gid definition instead
    new_id = object.IntegrationSite_lastID(type='Product')[0].getId()

    # create the full variations in the integration site
    if variation_dict:
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
        object.product_module.createProductAttribute(id_product=new_id)
        id_product_attribute = object.IntegrationSite_lastID(
            type='Product Attribute',
        )[0].getId()
        for variation in var_list:
          object.product_module.createProductAttributeCombination(
              id_product_attribute=id_product_attribute,
              id_product=new_id,
              base_category=variation[0],
              variation=variation[1],
            )

    return object.product_module(id=new_id)[0]


  def checkCategoryExistency(self, document, **kw):
    """
      This method allows to check the category existency in the integration
      site.
      It coulds create the element required to the calling of the category
      creation.
    """
    # retrieve from the kw dict the base, the variation and the id_product
    variation = kw.get('variation')
    base_category = kw.get('base_category')
    id_product = kw.get('id_product')
    # Check the base_category -> raise if not exists (base_category not mapped)
      # Done in Document/IntegrationSite.py into method getMappingFromCategory
    # Check the variation ->
    #   raise if multiple
    #   raise if not exists or create it ?
    variation_list = document.IntegrationSite_checkCategoryExistency(
        variation=variation,
        base_category=base_category,
    )
    if not variation_list:
      # TODO: is it requires to create the variation in the integration site ?
      pass
    elif len(variation_list) > 1:
      raise "Variation %s/%s counted %d time(s) in the Integration Site" % (
          base_category,
          variation,
          len(variation_list),
      )
    return True


  def _deleteContent(self, object=None, object_id=None):
    """ This method allows to remove a product in the integration site """
    return object.product_module.deleteProduct(product_id=object_id)


  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, **kw):
    """
      This method is called in updateNode and allows to work on the update of
      elements.
    """
    conflict_list = []
    xpath_expression = xml.get('select')
    tag = xpath_expression.split('/')[-1]
    integration_site = document.context.getParentValue()
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

    # check if it'a work on product or on categories
    if tag.split('[')[0] == 'category':
      # init the base category and the variation through the mapping
      mapping = integration_site.getMappingFromCategory(new_value)
      base_category, variation = mapping.split('/', 1)
      updated = False
      # init the previous value through the mapping
      previous_value = integration_site.getMappingFromCategory(previous_value)

      # work on variations
      variation_brain_list = document.context.getProductCategoryList()
      for brain in variation_brain_list:
        if brain.category == previous_value:
          old_base_category, old_variation = previous_value.split('/', 1)
          # remove all variations
          document.context.product_module.deleteProductAttributeCombination(
              product_id=document.getId(),
              base_category=old_base_category,
              variation=old_variation,
          )
          # retrieve the variations which have a different axe from the updated
          # and build the cartesian variation for this new variations
          external_axe_list = [
              tuple(x.category.split('/', 1))
              for x in document.context.getProductCategoryList()
              if x.category.split('/', 1)[0] != brain.category.split('/', 1)[0]
          ]
          builder_variation_list = [
              [tuple(mapping.split('/', 1))], external_axe_list,
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
        # previous value not find, so multiple update on the same product
        conflict = Conflict(
            object_path=document.getPhysicalPath(),
            keyword=tag,
        )
        conflict.setXupdate(etree.tostring(xml, encoding='utf-8'))
        conflict.setLocalValue(previous_value)
        conflict.setRemoteValue(new_value)
        conflict_list.append(conflict)
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
      if type(current_value) == float:
        current_value = '%.6f' % current_value
      if current_value not in [new_value, previous_value]:
        conflict = Conflict(
            object_path=document.getPhysicalPath(),
            keyword=tag,
        )
        conflict.setXupdate(etree.tostring(xml, encoding='utf-8'))
        conflict.setLocalValue(current_value)
        conflict.setRemoteValue(new_value)
        conflict_list.append(conflict)
      else:
        keyword = {'product_id': document.getId(), tag: new_value , }
        document.context.product_module.updateProduct(**keyword)

    return conflict_list


  def _updateXupdateDel(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to remove elements. """
    conflict_list = []
    tag = xml.get('select').split('/')[-1]
    integration_site = document.context.getParentValue()

    if tag.split('[')[0] == 'category':
      # retrieve the previous xml etree through xpath
      previous_xml = previous_xml.xpath(tag)
      try:
        previous_value = integration_site.getMappingFromCategory(
            previous_xml[0].text,
        )
      except IndexError:
        raise IndexError(
            'Too little or too many value, only one is required for %s'
            % previous_xml
        )

      # retrieve the current value to check if exists a conflict
      current_value = etree.XML(document.asXML()).xpath(tag)[0].text
      current_value = integration_site.getMappingFromCategory(current_value)

      # work on variations
      variation_brain_list = document.context.getProductCategoryList(product_id=document.getId())
      for brain in variation_brain_list:
        if brain.category == current_value and previous_value == current_value:
          base_category, variation = current_value.split('/', 1)
          document.context.product_module.deleteProductAttributeCombination(
              product_id=document.getId(),
              base_category=base_category,
              variation=variation,
          )
      else:
        # previous value different from current value
        conflict = Conflict(
            object_path=document.getPhysicalPath(),
            keyword=tag,
        )
        conflict.setXupdate(etree.tostring(xml, encoding='utf-8'))
        conflict.setLocalValue(previous_value)
        conflict.setRemoteValue(current_value)
        conflict_list.append(conflict)
    else:
      keyword = {'product_id': document.getId(), tag: 'NULL' , }
      document.context.product_module.updateProduct(**keyword)
    return conflict_list


  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to add elements. """
    conflict_list = []
    integration_site = document.context.getParentValue()

    # browse subnode of the insert and check what will be create
    for subnode in xml.getchildren():
      new_tag = subnode.attrib['name']
      new_value = subnode.text.encode('utf-8')
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
    return conflict_list

