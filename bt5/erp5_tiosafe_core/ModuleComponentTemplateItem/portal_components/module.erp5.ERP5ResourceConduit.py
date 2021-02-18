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

from Products.CMFCore.WorkflowCore import WorkflowException
from erp5.component.module.TioSafeBaseConduit import TioSafeBaseConduit
from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

class ERP5ResourceConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize ERP5 Products
  """
  def __init__(self):
    # Define the object_tag element to add object
    self.xml_object_tag = 'resource'
    self.system_pref = None

  def getObjectAsXML(self, object, domain): # pylint: disable=redefined-builtin
    return object.Resource_asTioSafeXML(context_document=domain)

  def _createContent(self, xml=None, object=None, object_id=None, # pylint: disable=redefined-builtin
      sub_object=None, reset_local_roles=0, reset_workflow=0, simulate=0,
      **kw):
    """
      This is the method calling to create an object
    """
    if True: # object_id is not None:
      if sub_object is None:
        sub_object = object._getOb(object_id, None)
      if sub_object is None: # If so, it does not exist
        portal_type = ''
        portal_type = self.getObjectType(xml)
        # Create a product object
        sub_object, reset_local_roles, reset_workflow = self.constructContent(
            object,
            object_id,
            portal_type,
        )
        # The initialization here is used to define our own base category, we
        # don't want to use the default base categories
        sub_object.edit(
            variation_base_category_list = [],
            optional_variation_base_category_list = [],
            individual_variation_base_category = [],
        )
        # if exist namespace retrieve only the tag
        index = 0
        category_dict = {}
        if xml.nsmap not in [None, {}]:
          index = -1

        # Set the use value
        sub_object.setUse('sale')
        portal = object.getPortalObject()
        # Browse the list to work on categories
        mapping_list = []
        for node in xml.getchildren():

          # Only works on right tags, and no on the comments, ...
          if not isinstance(node.tag, str):
            continue
          # Build the tag (without is Namespace)
          tag = node.tag.split('}')[index]
          # Treat sub-element
          if tag == 'category':
            category_xml_value = node.text.encode('utf-8')
            category_split_list = category_xml_value.split('/')
            base_category = category_split_list[0]
            shared_variation = True
            try:
              # Try to access the category
              category = portal.portal_categories.restrictedTraverse(category_xml_value)
            except KeyError:
              # This is an individual variation
              shared_variation = False

            if shared_variation:
              if base_category not in sub_object._baseGetVariationBaseCategoryList():
                base_category_list = sub_object._baseGetVariationBaseCategoryList()
                base_category_list.append(base_category)
                sub_object.setVariationBaseCategoryList(base_category_list)
                self.updateSystemPreference(portal, base_category)

              variation_list = sub_object.getVariationCategoryList()
              if category_xml_value not in variation_list:
                variation_list.append(category_xml_value)
                sub_object.setVariationCategoryList(variation_list)
            else:
              if base_category not in sub_object.getIndividualVariationBaseCategoryList():
                base_category_list = sub_object.getIndividualVariationBaseCategoryList()
                base_category_list.append(base_category)
                sub_object.setIndividualVariationBaseCategoryList(base_category_list)
                self.updateSystemPreference(portal, base_category, True)

              variation_category = "/".join(category_split_list[1:])
              category = sub_object.newContent(
                portal_type='Product Individual Variation',
                title=variation_category,
                variation_base_category=base_category,
                )
            # Store a dict category_name -> category_path to use for mapping later
            category_dict[category_xml_value] = base_category+'/'+category.getRelativeUrl()

          elif tag == "mapping":
            # build mapping list here
            mapping_dict = {'category' : [],}
            for item in node.getchildren():
              # Build the tag (without is Namespace)
              tag = item.tag.split('}')[index]
              if tag == "category":
                mapping_dict['category'].append(category_dict[item.text.encode('utf-8')])
              else:
                mapping_dict[tag] = item.text.encode('utf-8')
            mapping_list.append(mapping_dict)

      conflict_list = self._createMapping(sub_object, mapping_list)
      if len(conflict_list):
        raise ValueError("Conflict on creation of resource, should not happen, conflict = %r" % conflict_list)

      self.newObject(
          object=sub_object,
          xml=xml,
          simulate=simulate,
          reset_local_roles=reset_local_roles,
          reset_workflow=reset_workflow,
      )


      # add to sale supply
      sync_name = self.getIntegrationSite(kw['domain']).getTitle()
      ss = self.getSaleSupply(sync_name, portal)
      if len(ss.searchFolder(resource_title=sub_object.getTitle())) == 0:
        ss.newContent(resource_value=sub_object)

    return sub_object

  def _getMappedPropertyLine(self, resource, prop):
    """
    Return the line, create it if it does not exits
    """
    # XXX-Aurel : Cache this method ?
    mapped_line = None
    for line in resource.contentValues(portal_type='Mapped Property Type'):
      if getattr(line, 'mapped_property', None) == prop:
        mapped_line = line
        break
    if not mapped_line:
      mapped_line = resource.newContent(portal_type='Mapped Property Type',
                                        mapped_property=prop)

    return mapped_line

  def _createMapping(self, resource, mapping_list):
    conflict_list = []
    for mapping in mapping_list:
      category_list = mapping.pop('category')
      base_category_list = [x.split('/', 1)[0] for x in category_list]
      property_list = mapping.keys()
      for prop in property_list:
        line = self._getMappedPropertyLine(resource, prop)
        line.edit(variation_base_category_list=base_category_list,
                  variation_category_list =line.getVariationCategoryList([]) + category_list,)
        line.updateCellRange(base_id=prop)
        # Try to get the cell
        try:
          cell = line.getCell(base_id=prop, *category_list)
        except KeyError:
          cell = None
        if cell is None:
          cell = line.newCell(
            base_id=prop,
            portal_type='Mapped Property Cell',
            *category_list
            )
        # set values on the cell
        cell.setCategoryList(category_list)
        cell.setMembershipCriterionCategoryList(category_list)
        cell.setMembershipCriterionBaseCategoryList(
          line.getVariationBaseCategoryList(),
          )
        cell.setMappedValuePropertyList([prop,])
        # Check possible conflict
        getter_id = "get%s" %(prop.capitalize())
        getter = getattr(cell, getter_id, None)
        if getter:
          current_value = getter()
        else:
          current_value = getattr(cell, prop)
        if current_value and current_value != mapping[prop]:
          conflict_list.append((cell, current_value, mapping[prop]))
          continue
        setter_id = "set%s" %(prop.capitalize())
        setter = getattr(cell, setter_id, None)
        if setter:
          setter(mapping[prop])
        else:
          setattr(cell, prop, mapping[prop])
    return conflict_list

  def getSaleSupply(self, name, portal):
    """
    Retrieve the sale supply for the given synchronization
    If not exist, create it
    """
    if getattr(self, 'sale_supply', None) is None:
      ss_list = portal.sale_supply_module.searchFolder(title=name,
                                                       validation_state='validated')
      if len(ss_list) > 1:
        raise ValueError("Too many sale supplies, does not know which to choose")
      if len(ss_list) == 0:
        # Create a new one
        ss = portal.sale_supply_module.newContent(title=name)
        ss.validate()
      else:
        ss = ss_list[0].getObject()
      self.sale_supply = ss
    return self.sale_supply

  def updateSystemPreference(self, portal, base_category, individual=False):
    """ Update the system preference according to categories set on products
    so that UI is well configured in the end """
    if self.system_pref is None:
      pref_list = [x for x in portal.portal_preferences.objectValues(portal_type="System Preference")\
                   if x.getPreferenceState()=="global"]
      if len(pref_list) > 1:
        raise ValueError("Too many system preferences, does not know which to choose")
      elif len(pref_list) == 0:
        pref = portal.portal_preferences.newContent(portal_type="System Preference",
                                             title="default system preference for TioSafe",
                                             priority=1)
        pref.enable()
      else:
        pref = pref_list[0].getObject()
      self.system_pref = pref

    if individual:
      cat_list = self.system_pref.getPreferredProductIndividualVariationBaseCategoryList()
      if base_category not in cat_list:
        cat_list.append(base_category)
        self.system_pref.edit(preferred_product_individual_variation_base_category_list = cat_list)
    else:
      cat_list = self.system_pref.getPreferredProductVariationBaseCategoryList()
      if base_category not in cat_list:
        cat_list.append(base_category)
        self.system_pref.edit(preferred_product_variation_base_category_list = cat_list)

  def afterNewObject(self, object): # pylint: disable=redefined-builtin
    object.validate()
    object.updateLocalRolesOnSecurityGroups()

  def _deleteContent(self, object=None, object_id=None, **kw): # pylint: disable=redefined-builtin
    """ Move the product into "invalidated" state. """
    document = object.product_module._getOb(object_id)
    # dict which provides the list of transition to move into invalidated state
    states_list_dict = {
        'draft': ['validated_action', 'invalidate_action', ],
        'validated': ['invalidate_action', ],
    }
    # move into the "invalidated" state
    current_state = document.getValidationState()
    if current_state in states_list_dict:
      for action in states_list_dict[current_state]:
        try:
          document.portal_workflow.doActionFor(document, action)
        except WorkflowException:
          if current_state == 'draft':
            document.activate().validate()
          document.activate().invalidate()

    # Remove related line from sale supply
    sync_name = self.getIntegrationSite(kw['domain']).getTitle()
    sale_supply_line_list = [x.getObject() for x in
                             object.Base_getRelatedObjectList(portal_type="Sale Supply Line")]
    for sale_supply_line in sale_supply_line_list:
      sale_supply = sale_supply_line.getParentValue()
      if sale_supply.getTitle() == sync_name:
        sale_supply.manage_delObjects(ids=[sale_supply_line.getId(),])

  def editDocument(self, object=None, **kw): # pylint: disable=redefined-builtin
    """
      This is the editDocument method inherit of ERP5Conduit. This method
      is used to save the information of a Product.
    """
    # Map the XML tags to the PropertySheet
    mapping = {
        'title': 'title',
        'reference': 'reference',
        'ean13': 'ean13_code',
        'description': 'description',
    }
    # Translate kw with the PropertySheet
    property_ = {}
    for k, v in kw.items():
      k = mapping.get(k, k)
      property_[k] = v
    object._edit(**property_)


  def _getPropertyMappingCell(self, resource, prop, index):
    cell_list = []
    for mapping in resource.contentValues(portal_type="Mapped Property Type"):
      if prop is not None and mapping.mapped_property != prop:
        continue
      else:
        cell_dict = {}
        for cell in mapping.contentValues():
          cat_list = cell.getCategoryList()
          lcat_list = []
          for cat in cat_list:
            base = cat.split('/', 1)[0]
            try:
              cat = resource.getPortalObject().portal_categories.restrictedTraverse(cat).getTitle()
            except KeyError:
              base, path = cat.split('/', 1)
              iv = resource.restrictedTraverse(path)
              cat = iv.getTitle()
            lcat_list.append(base+"/"+cat)
          cell_dict[str(lcat_list)] = cell
        ordered_key_list = cell_dict.keys()
        ordered_key_list.sort()
        cell_key = ordered_key_list[index-1]
        cell_list.append(cell_dict[cell_key])

    return cell_list

  def _updateXupdateUpdate(self, document=None, xml=None, previous_xml=None, **kw):
    """
      This method is called in updateNode and allows to work on the update of
      elements.
    """
    conflict_list = []
    xpath_expression = xml.get('select')
    tag_list = xpath_expression.split('/')

    base_tag = None
    remaining_tag_list = []
    for tag in tag_list:
      if not len(tag) or tag == "resource":
        continue
      elif base_tag is None:
        base_tag = tag
      else:
        remaining_tag_list.append(tag)

    new_value = xml.text
    keyword = {}

    # retrieve the previous xml etree through xpath
    previous_xml = previous_xml.xpath(xpath_expression)
    try:
      previous_value = previous_xml[0].text
    except IndexError:
      raise IndexError(
          'Too little or too many value, only one is required for %s'
          % previous_xml
      )

    if isinstance(previous_value, unicode):
      previous_value = previous_value.encode('utf-8')

    if isinstance(new_value, unicode):
      new_value = new_value.encode('utf-8')

    # check if it'a work on product or on categories
    if base_tag.startswith('category'):
      # init base category, variation and boolean which check update
      base_category, variation = new_value.split('/', 1)
      old_base_category, old_variation = previous_value.split('/', 1)
      # retrieve the base_categories and the variations
      base_category_list = document.getVariationBaseCategoryList()
      variation_list = document.getVariationCategoryList()

      # about shared and individual variations, it's necessary to check the
      # mapping existency
      shared_variation = True
      try:
        # Try to access the category
        document.getPortalObject().portal_categories.restrictedTraverse(new_value)
      except KeyError:
        # This is an individual variation
        shared_variation = False

      # the mapping of an element must only be defined one time
      individual_variation = document.searchFolder(
          portal_type='Product Individual Variation',
          title=old_variation,
          base_category=old_base_category,
      )
      # If this is badly defined, fix the objects
      if len(individual_variation) > 1:
        id_to_remove = []
        for individual in individual_variation[1:]:
          id_to_remove.append(individual.getId())
        document.manage_delObjects(id_to_remove)
      if len(individual_variation) and previous_value in variation_list:
        for individual in individual_variation:
          id_to_remove.append(individual.getId())
        document.manage_delObjects(id_to_remove)

      # Update variation
      if not shared_variation:
        # work on the cases :
        # new = individual variation
        #   old = individual variation -> update
        #   old = shared variation -> remoce shared and add individual

        # Fist check individual base
        if base_category not in document.getIndividualVariationBaseCategoryList():
          base_category_list = document.getIndividualVariationBaseCategoryList()
          base_category_list.append(base_category)
          document.setIndividualVariationBaseCategoryList(base_category_list)
          self.updateSystemPreference(document.getPortalObject(), base_category, True)

        # Then update or add variation
        if len(individual_variation):
          individual_variation = individual_variation[0].getObject()
          individual_variation.setTitle(variation)
          individual_variation.setVariationBaseCategory(base_category)
        else:
          # create the individual variation
          document.newContent(
              portal_type='Product Individual Variation',
              title=variation,
              base_category=base_category,
          )
      else:
        # work on the cases :
        # new = shared variation
        #   old = individual variation -> remove individual and add shared
        #   old = shared variation -> update shared
        if len(individual_variation):
          # remove individual if previous was that
          document.manage_delObjects([individual_variation[0].getId(), ])
        else:
          # remove the shared from the list if it's a shared
          variation_list.remove(previous_value)

        # set the base category and the variations
        if base_category not in document._baseGetVariationBaseCategoryList():
          base_category_list = document._baseGetVariationBaseCategoryList()
          base_category_list.append(base_category)
          document.setVariationBaseCategoryList(base_category_list)
          self.updateSystemPreference(document.getPortalObject(), base_category)

        if new_value not in variation_list:
          variation_list.append(new_value)
          document.setVariationCategoryList(variation_list)
    elif base_tag.startswith('mapping'):
      index_value = int(base_tag[-2]) # because it is tag[index]
      if len(remaining_tag_list) > 1 or not(remaining_tag_list):
        raise NotImplementedError
      tag = remaining_tag_list[0]
      # Retrieve the mapping cell
      cell = self._getPropertyMappingCell(resource=document, prop=tag,
                                          index=index_value)[0]
      getter_id = "get%s" %(tag.capitalize(),)
      getter = getattr(cell, getter_id)
      current_value = getter()
      if isinstance(current_value, unicode):
        current_value = current_value.encode('utf-8')
      if current_value not in [new_value, previous_value]:
        conflict_list.append(self._generateConflict(document.getPhysicalPath(),
                                                    base_tag+'/'+tag,
                                                    etree.tostring(xml, encoding='utf-8'),
                                                    current_value,
                                                    new_value,
                                                    kw['signature']))
      else:
        setter_id = "set%s" %(tag.capitalize(),)
        setter = getattr(cell, setter_id)
        current_value = setter(new_value)
    else:
      # getter used to retrieve the current values and to check conflicts
      getter_value_dict = {
          'title': document.getTitle(),
          'reference': document.getReference(),
          'ean13': document.getEan13Code(),
          'description': document.getDescription(),
      }

      # create and fill a conflict when the integration site value, the erp5
      # value and the previous value are differents
      current_value = getter_value_dict[base_tag]
      if isinstance(current_value, float):
        current_value = '%.6f' % current_value
      if isinstance(current_value, unicode):
        current_value = current_value.encode('utf-8')
      if current_value not in [new_value, previous_value]:
        conflict_list.append(self._generateConflict(document.getPhysicalPath(),
                                                    base_tag,
                                                    etree.tostring(xml, encoding='utf-8'),
                                                    current_value,
                                                    new_value,
                                                    kw['signature']))
      else:
        keyword[base_tag] = new_value
        self.editDocument(object=document, **keyword)

    return conflict_list


  def _updateXupdateDel(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to remove elements. """
    conflict_list = []
    base_tag = None
    remaining_tag_list = []
    tag_list = xml.get('select').split('/')
    for tag in tag_list:
      if not len(tag) or tag == "resource":
        continue
      elif base_tag is None:
        base_tag = tag
      else:
        remaining_tag_list.append(tag)
    keyword = {}

    if base_tag.startswith('category'):
      # retrieve the previous xml etree through xpath
      previous_xml = previous_xml.xpath(base_tag)
      try:
        previous_value = previous_xml[0].text
      except IndexError:
        raise IndexError(
          'Too little or too many value, only one is required for %s'
          % previous_xml
        )

      if isinstance(previous_value, unicode):
        previous_value = previous_value.encode('utf-8')

      # boolean which check update
      updated = False
      # check first in shared variations
      shared_variation_list = document.getVariationCategoryList()
      if previous_value in shared_variation_list:
        updated = True
        shared_variation_list.remove(previous_value)
        document.setVariationCategoryList(shared_variation_list)
      # if no update has occured, check in individual variations
      if not updated:
        individual_variation = document.portal_catalog(
            portal_type='Product Individual Variation',
            title=previous_value.split('/', 1)[-1],
            parent_uid=document.getUid(),
        )
        if len(individual_variation) == 1:
          individual_variation = individual_variation[0].getObject()
          document.manage_delObjects([individual_variation.getId(), ])
    elif base_tag.startswith('mapping'):
      index_value = int(base_tag[-2]) # because it is tag[index]
      if not len(remaining_tag_list):
        # We are deleting a cell
        cell_list = self._getPropertyMappingCell(resource=document, prop=None,
                                            index=index_value)
        for cell in cell_list:
          line = cell.getParentValue()
          line.manage_delObjects(cell.getId())
      else:
        # We are deleting a property only
        if len(remaining_tag_list) > 1:
          raise NotImplementedError
        tag = remaining_tag_list[0]
        cell = self._getPropertyMappingCell(resource=document, prop=tag,
                                            index=index_value)[0]
        getter_id = "get%s" %(tag.capitalize(),)
        getter = getattr(cell, getter_id)
        current_value = getter()
        if isinstance(current_value, unicode):
          current_value = current_value.encode('utf-8')
        if current_value not in [new_value, previous_value]: # pylint: disable=undefined-variable
          conflict_list.append(self._generateConflict(document.getPhysicalPath(),
                                                      base_tag+'/'+tag,
                                                      etree.tostring(xml, encoding='utf-8'),
                                                      current_value,
                                                      new_value, # pylint: disable=undefined-variable
                                                      kw['signature']))
        else:
          setter_id = "set%s" %(tag.capitalize(),)
          setter = getattr(cell, setter_id)
          current_value = setter(None)
    else:
      keyword[base_tag] = None
      self.editDocument(object=document, **keyword)
    return conflict_list


  def _getCategoryDict(self, resource=None):
    """
    Build a dict title -> path for variation categories of a resource
    """
    category_dict = {}
    for category in resource.getVariationRangeCategoryList(display_base_category=1,
                                                           omit_individual_variation=0):
      base = category.split("/", 1)[0]
      category_title = resource.portal_categories.restrictedTraverse(category).getTitle()
      category_dict[base+"/"+category_title] = category

    return category_dict

  def _updateXupdateInsertOrAdd(self, document=None, xml=None, previous_xml=None, **kw):
    """ This method is called in updateNode and allows to add elements. """
    conflict_list = []
    keyword = {}
    mapping_list = []
    category_dict = self._getCategoryDict(resource=document)
    # browse subnode of the insert and check what will be create
    for subnode in xml.getchildren():
      new_tag = subnode.attrib['name']
      new_value = subnode.text
      if new_tag == 'category':
        # init base category, variation and boolean which check update
        base_category, variation = new_value.split('/', 1)
        updated = False

        # check first in shared variations
        shared_variation_list = document.getVariationCategoryList()
        if new_value not in shared_variation_list:
          # set variation if it's an existing shared variation, else
          # it's an individual
          base_category_object = document.portal_categories[base_category]
          if getattr(base_category_object, variation, None) is not None:
            updated = True
            shared_variation_list.append(new_value)
            document.setVariationCategoryList(shared_variation_list)
        # if no update has occured, check in individual variations
        if not updated and \
            new_value not in document.getVariationCategoryList():
          # individual variation list filtered on base_category
          individual_variation = [individual
              for individual in document.contentValues(
                portal_type='Product Individual Variation',
              )
              if individual.getTitle() == variation and \
                  individual.getVariationBaseCategoryList() == \
                  [base_category, ]
          ]
          if not individual_variation: # empty list
            new_variation = document.newContent(
                portal_type='Product Individual Variation',
                title=variation,
            )
            new_variation.setVariationBaseCategoryList([base_category, ])
      elif new_tag == "mapping":
        # build mapping list here
        mapping_dict = {'category' : [],}
        for item in subnode.getchildren():
          # Build the tag (without is Namespace)
          tag = item.tag
          if tag == "category":
            # Retrieve the category path
            mapping_dict['category'].append(category_dict[item.text.encode('utf-8')])
          else:
            mapping_dict[tag] = item.text.encode('utf-8')
        mapping_list.append(mapping_dict)
      else:
        if len(subnode.getchildren()):
          raise NotImplementedError
        keyword[new_tag] = new_value
        self.editDocument(object=document, **keyword)
      if len(mapping_list):
        conflict_list = self._createMapping(document, mapping_list)
        for cell, current_value, new_value in conflict_list:
          conflict_list.append(self._generateConflict(cell.getPhysicalPath(),
                                                      'mapping',
                                                      etree.tostring(xml, encoding='utf-8'),
                                                      current_value,
                                                      new_value,
                                                      kw['signature']))

    return conflict_list

