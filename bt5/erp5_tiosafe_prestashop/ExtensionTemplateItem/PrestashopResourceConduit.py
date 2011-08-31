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
from Products.ERP5TioSafe.Conduit.TioSafeResourceConduit import TioSafeResourceConduit
from lxml import etree
from zLOG import LOG

class PrestashopResourceConduit(TioSafeResourceConduit):
  """
    This is the conduit use to synchonize TioSafe Resources
  """
  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None,
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    LOG("TioSafeNodeConduit._createContent", 300, "xml = %s" %(etree.tostring(xml, pretty_print=1),))

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

    resource_type = self.getObjectType(xml=xml).strip()

    # browse the xml
    for node in xml:
      # works on tags, not on comments
      if type(node.tag) is not str:
        continue
      tag = node.tag.split('}')[index]
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
    create_method_id = "create%s" %(resource_type,)
    create_method = getattr(object, create_method_id, None)
    if create_method is not None:
      create_result = create_method(**keyword)
    else:
      raise ValueError, 'Impossible to find a create method named %s and object %s' %(create_method_id, object.getPath(),)
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


  def _updateCategory(self, document=None, xml=None, previous_value=None, signature=None):
    """ This method allows to update a Category in the Integration Site. """
    LOG("_updateCategory", 300, "previous_value = %s, new_value = %s" %(previous_value, xml.text))
    conflict_list = []
    integration_site = document.context.getParentValue()
    new_value = xml.text

    # init the base category and the variation through the mapping
    mapping = integration_site.getMappingFromCategory(new_value)
    base_category, variation = mapping.split('/', 1)
    # init the previous value through the mapping
    mapped_previous_value = integration_site.getMappingFromCategory(previous_value)

    # work on variations
    variation_brain_list = document.context.getProductCategoryList()
    for brain in variation_brain_list:
      if brain.category == mapped_previous_value:
        old_base_category, old_variation = mapped_previous_value.split('/', 1)
        # remove old variation
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
        break
    else:
      # previous value not find, so multiple update on the same product
      conflict = signature.newContent(portal_type='SyncML Conflict',
                                      origin=document.getPhysicalPath(),
                                      property_id=xml.get('select').split('/')[-1],
                                      diff_chunk=etree.tostring(xml, encoding='utf-8'),
                                      local_value=previous_value,
                                      remove_value=new_value
                                      )
      conflict_list.append(conflict)

    return conflict_list


