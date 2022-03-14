# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################



from Products.ERP5Type.Core.Folder import Folder
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from zLOG import LOG, INFO, ERROR
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable


class IntegrationSite(Folder):
  """
  """

  meta_type = 'ERP5 Integration Site'
  portal_type = 'Integration Site'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.DublinCore
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Reference
                      , PropertySheet.Arrow
                      , PropertySheet.Task
                      , PropertySheet.DublinCore
                      )


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCategoryFromMapping')
  def getCategoryFromMapping(self, category, product=None, create_mapping=False,
                             create_mapping_line=False):
    """
      This method allows to retrieve the mapping in the integration site.
      args:
        category = string of the category we want the mapping
        product = product object that can hold categories not mapped
        create_mapping = boolean telling if we create an empty base mapping object if not found
        create_mapping_line = boolean telling if we create an empty mapping line object if not found
      return:
        mapped_category as string
        raise ValueError when not found
    """
    if not category:
      LOG("getCategoryFromMapping", ERROR, "empty category provided")
      raise ValueError("Empty category provided")

    # Split the category to have the base and the variation category
    _, variation_category = category.split('/', 1)

    # Check the product variations if exists the product
    if product is not None:
      for variation in product.contentValues(
          portal_type='Product Individual Variation'):
        if variation.getTitle() == variation_category:
          return '%s/%s' % (variation.getVariationBaseCategory(),
                            variation.getRelativeUrl(),
                            )

    # mapping is defined with ID
    # XXX-Aurel : replace should not be done here as title will not be well defined indeed
    current_object = self
    mapped_base_category = None
    mapped_variation_category = []
    missing_mapping = False
    for cat in category.split('/'):
      cat_id = cat.replace(' ', '').replace('-', '')
      try:
        cat_object = current_object[cat_id.encode('ascii', 'ignore')]
      except KeyError:
        #LOG("getCategoryFromMapping",  WARNING, "Nothing found for %s , %s on %s" %(category, cat_id, current_object.getPath()))
        if current_object.getPortalType() == "Integration Base Category Mapping":
          if create_mapping_line is False:
            # This is for the case of individual variation for example
            # only the base category has to be mapped
            if missing_mapping or current_object.getDestinationReference() is None:
              # We do not want the process to go on if base category mappings is missing
              raise ValueError("Mapping not defined for %s" % category)
            return current_object.getDestinationReference() +'/'+ category.split('/', 1)[1]
          else:
            # Create default line that has to be mapped by user later
            cat_object = current_object.newContent(id=cat_id.encode('ascii', 'ignore'), source_reference=cat, title=cat)
            LOG("getCategoryFromMapping", INFO, "created mapping %s - %s" %(cat, cat_object),)
            missing_mapping = True
        else:
          if create_mapping:
            cat_object = current_object.newContent(portal_type="Integration Base Category Mapping",
                                                   id=cat_id.encode('ascii', 'ignore'), source_reference=cat, title=cat)
            LOG("getCategoryFromMapping", INFO, "created base mapping %s - %s" %(cat, cat_object),)
            missing_mapping = True
          else:
            LOG("getCategoryFromMapping", ERROR, "Mapping object for %s not found" %(cat,))
            raise ValueError("Mapping object for %s not found" % cat)

      mapped_category = cat_object.getDestinationReference()
      if mapped_category in ("", None) and cat_object.getPortalType() == "Integration Category Mapping":
        LOG("getCategoryFromMapping", ERROR, "Mapping not defined for %s" % (cat,))
        raise ValueError("Mapping not defined for %s" % cat)
      if mapped_base_category is None:
        mapped_base_category = mapped_category
      else:
        mapped_variation_category.append(mapped_category)
      current_object = cat_object


##     LOG("getCategoryFromMapping", INFO, "mapped category returned is %s - %s for %s" %(mapped_base_category,
##                                                                                        mapped_variation_category,
##                                                                                        category))
    if missing_mapping:
      # We do not want the process to go on if mappings are missing
      raise ValueError("Mapping not defined for %s" % category)
    return mapped_variation_category[-1]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMappingFromCategory')
  def getMappingFromCategory(self, category):
    """
      This method allows to retrieve through the mapping in the integration
      site the corresponding value in the external site.
      args:
        category = string of the category we want the mapping
    """
    # FIXME: currently they have only two levels, the category integration
    # mapping and the category integration mapping line, if more levels are
    # provides this script must be updated !
    base_category, variation = category.split('/', 1)
    # retrieve the corresponding integration base category mapping
    mapping = self.searchFolder(
        portal_type='Integration Base Category Mapping',
        destination_reference=base_category,
    )
    if len(mapping) != 1:
      raise IndexError('The integration base category mapping %s must be mapped and with only one base_category' % base_category)

    mapping = mapping[0].getObject()
    # retrieve the corresponding category integration mapping
    mapping_line = mapping.searchFolder(
        portal_type='Integration Category Mapping',
        destination_reference=category,
    )
    if len(mapping_line) > 1:
      raise IndexError('The integration category mapping %s must be mapped with only one category' % variation)
    try:
      # shared variation
      return '/'.join(
          [mapping.getSourceReference(), mapping_line[0].getObject().getSourceReference()]
      )
    except IndexError:
      # individual variation
      return '/'.join([mapping.getSourceReference(), variation])

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMappingFromProperty')
  def getMappingFromProperty(self, base_mapping, property_name):
    """
      This method allows to retrieve throuhh the mapping in the integration
      site the corresponding value in the external site.
      args:
        base_mapping = the base property mapping
        property = string of the property we want the mapping
    """
    tv = getTransactionalVariable()
    key = "%s-%s" % (base_mapping.getPath(), property_name)
    try:
      mapping_line = tv[key]
    except KeyError:
      tv[key] = mapping_line = base_mapping.searchFolder(portal_type='Integration Property Mapping',
                                             path = "%s%%" %(base_mapping.getPath()),
                                             destination_reference=property_name,
                                             )
    if len(mapping_line) > 1:
      raise IndexError('The integration property mapping %s must be mapped with only one category' % property_name)
    elif len(mapping_line) == 0:
      return property_name
    else:
      return mapping_line[0].getObject().getSourceReference()

