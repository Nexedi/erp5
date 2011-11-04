##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5TioSafe.Conduit.TioSafeResourceConduit import TioSafeResourceConduit
from lxml import etree
from zLOG import LOG

class OxatisProductConduit(TioSafeResourceConduit):
  """
    This is the conduit use to synchonize TioSafe Resources
  """

  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None,
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    LOG("OxatisProductConduit._createConten", 300, "xml = %s" %(etree.tostring(xml, pretty_print=1, encoding='utf-8'),))

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
      keyword[tag] = node.text.encode('utf-8')

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

    return object[new_id]


  def _deleteContent(self, object=None, object_id=None):
    """ This method allows to remove a product in the integration site """
    delete_method_id = "deleteProduct" # XXX-AUREL : must find a way to fix this
    delete_method = getattr(object, delete_method_id, None)
    if delete_method is not None:
      return delete_method(product_id=object_id)
    else:
      raise ValueError, 'Impossible to find a delete method named %s and object %s' %(delete_method_id, object.getPath(),)


  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, **kw):
    """
      This method is called in updateNode and allows to work on the update of
      elements.
    """
    conflict_list = []
    xpath_expression = xml.get('select')
    base_tag = None
    remaining_tag_list = []
    for tag in xpath_expression.split('/'):
      if len(tag) == 0 or tag == "resource":
        continue
      if not base_tag:
        base_tag = tag
      else:
        remaining_tag_list.append(tag)

    integration_site = document.context.getParentValue()
    new_value = xml.text
    # retrieve the previous xml etree through xpath
    previous_xml = previous_xml.xpath(xpath_expression)
    try:
      previous_value = previous_xml[0].text
    except IndexError:
      raise ValueError, 'Too little or too many value, only one is required for %s' % (
          previous_xml
      )

    if isinstance(previous_value, unicode):
      previous_value = previous_value.encode('utf-8')
    if isinstance(new_value, unicode):
      new_value = new_value.encode('utf-8')

    root_tag_list = ['title', 'description', 'reference']
    if base_tag in root_tag_list:
      # getter used to retrieve the current values and to check conflicts
      property_list = ['title', 'description',]
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
      if isinstance(current_value, unicode):
        current_value = current_value.encode('utf-8')

      if current_value not in [new_value, previous_value]:
        conflict_list.append(self._generateConflict(path=document.getPhysicalPath(),
                                                    tag=tag,
                                                    xml=etree.tostring(xml, encoding='utf-8'),
                                                    current_value=current_value,
                                                    new_value=value,
                                                    signature=kw["signature"],
                                                    ))
      else:
        keyword = {'product_id': document.getId(), tag: new_value , }
        if tag == "description":
          document.context.product_module.updateProductDescription(**keyword)
        elif tag == "title":
          document.context.product_module.updateProductTitle(**keyword)
        elif tag == "reference":
          document.context.product_module.updateProductReference(**keyword)
        else:
          raise ValueError, "Do not know how to update this property %s / %s for %s" %(tag, new_value, document.getId())

    elif base_tag.startswith("mapping"):
      index = int(base_tag[-2])
      if len(remaining_tag_list) > 1 or not(remaining_tag_list):
        raise NotImplementedError
      tag = remaining_tag_list[0]
      object_mapping = getattr(document, 'mapping_property_list')
      # sort categories
      def cat_cmp(a, b):
        return cmp(a['category_list'], b['category_list'])
      object_mapping.sort(cmp=cat_cmp)
      current_value = object_mapping[index-1][tag]
      if current_value not in [new_value, previous_value]:
        conflict_list.append(self._generateConflict(path=document.getPhysicalPath(),
                                                    tag=tag,
                                                    xml=etree.tostring(xml, encoding='utf-8'),
                                                    current_value=current_value,
                                                    new_value=value,
                                                    signature=kw["signature"],
                                                    ))
      else:
        # We must find the right product id
        real_document = document.context.product_module.getProductByReference(reference=current_value)[0]
        keyword = {'product_id': real_document.getId(), tag: new_value , }
        document.context.product_module.updateProductReference(**keyword)

    # Update properties of brain that will we stored into signature
    new_document = document.context.product_module[document.getId()]
    document.updateProperties(new_document)
    return conflict_list


  def _updateXupdateDel(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to remove elements. """
    raise NotImplementedError

  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to add elements. """
    raise NotImplementedError
