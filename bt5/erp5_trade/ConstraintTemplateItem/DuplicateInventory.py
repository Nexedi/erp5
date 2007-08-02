##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.Constraint import Constraint
from zLOG import LOG

class DuplicateInventory(Constraint):
  """
    We want to check here that there is not 2 or more inventories with:
    - the same resource
    - the same date
    - the same node
  """

  def generateDuplicateError(self, portal, obj, resource, variation_text):
    """
      Use a single method in order to generate the message
    """
    resource_value = portal.restrictedTraverse(resource)
    resource_title = resource_value.getTitle()
    variation_description = ''
    variation_title = ''
    if len(variation_text) > 0:
      variation_title_list = []
      for variation in variation_text.split('\n'):
        variation_value = portal.portal_categories\
                                 .getCategoryValue(variation)
        variation_title_list.append(variation_value.getTitle())
      variation_title = ("(%s)" % ''.join(variation_title_list))
      variation_description = "and variation $variation_title "
    error_message = "%s%s%s" % \
        ("There is already an inventory for $resource_title ",
         variation_description, "on this node and date")
    return self._generateError(obj, error_message,
        mapping={'variation_title' : variation_title,
                 'resource_title' : resource_title})

  def checkConsistency(self, obj, fixit = 0):
    """
      Implement here the consistency checker
      whenever fixit is not 0, object data should be updated to 
      satisfy the constraint
    """

    errors = []

    inventory = obj
    node = inventory.getDestination()
    node_value = inventory.getDestinationValue()
    # Make sure to raise conflict error when two inventories are
    # validated in the same time for the same node, this is the only
    # way to make sure that it is impossible to validate two inventories
    # in the same time (required because we have message with right tags
    # only when the transaction is finished)
    node_value.serialize()

    # For each resource, we look that there is not any inventory for
    # the same date, the same resource and the same node, or if there
    # is already such kind of inventories being indexed
    resource_and_variation_list = []
    date = inventory.getStartDate()
    date_string = repr(date)
    countMessageWithTag = inventory.portal_activities.countMessageWithTag
    portal = inventory.getPortalObject()
    getObjectFromUid = portal.portal_catalog.getObject
    getCurrentInventoryList = portal.portal_simulation.getCurrentInventoryList
    resource_and_variation_list = []
    for movement in inventory.getMovementList():
      resource =  movement.getResource()
      if resource is not None and movement.getQuantity() not in (None,''):
        variation_text = movement.getVariationText()
        if (resource,variation_text) not in resource_and_variation_list:
          resource_and_variation_list.append((resource,variation_text))
          tag = '%s_%s_%s' % (date_string, resource, variation_text)
          if countMessageWithTag(tag) > 0 :
            errors.append(self.generateDuplicateError(portal, obj, resource,
                                  variation_text))
          # Call sql request in order to see if there is another inventory
          # for this node, resource, variation_text and date
          inventory_list = getCurrentInventoryList(resource=resource,
                                   variation_text=variation_text,
                                   from_date=date, at_date=date,
                                   node=node)
          LOG('inventory_list sql src', 0, getCurrentInventoryList(resource=resource,
            variation_text=variation_text,
            from_date=date, at_date=date,
            node=node, src__=1))
          LOG('len inventory_list',0,len(inventory_list))
          for inventory in inventory_list:
            movement = getObjectFromUid(inventory.stock_uid)
            if movement.getPortalType().find('Inventory') >= 0:
              errors.append(self.generateDuplicateError(portal, obj, resource,
                                  variation_text))
        # Now we must reindex with some particular tags
        activate_kw = {'tag': tag}
        movement.reindexObject(activate_kw=activate_kw)
    
    return errors
