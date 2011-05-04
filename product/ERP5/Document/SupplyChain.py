##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Path import Path

class SupplyChainError(Exception): pass

class SupplyChain(Path, XMLObject):
  """
    SupplyChain defines the route used to produced a resource.
  """
  # CMF Type Definition
  meta_type = 'ERP5 Supply Chain'
  portal_type = 'Supply Chain'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Reference
                    , PropertySheet.Comment
                    , PropertySheet.Movement
                    , PropertySheet.Delivery
                    , PropertySheet.Path
                    , PropertySheet.FlowCapacity
                    )

  # Class variable
  supply_link_portal_type="Supply Link"

  security.declareProtected(Permissions.AccessContentsInformation, 'getLastLink')
  def getLastLink(self):
    """
      Return the SupplyLink representing the last ridge of the 
      SupplyChain (if this one is correctly defined...).
    """
    # Result value
    result = None
    # Get all lines.
    supply_link_list = self.objectValues(
                               portal_type=self.supply_link_portal_type)
    # Last line is defined by deliverable=1
    last_supply_link_list = [x for x in supply_link_list if\
                              x.getDeliverable()]
    # Check if user did not define multiple last links
    last_list_len = len(last_supply_link_list)
    if (last_list_len == 1):
      result = last_supply_link_list[0]
    else:
      raise SupplyChainError,\
            "Unable to get the last link of SupplyChain %s" %\
            str(self.getRelativeUrl())
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getNextSupplyLinkList')
  def getNextSupplyLinkList(self, current_supply_link):
    """
      Return the previous SupplyLink  list.
    """
    supply_link_list = self.objectValues(
                                 portal_type=self.supply_link_portal_type)
    # Search next link
    next_node_value = current_supply_link.getNextNodeValue()

    next_supply_link_list = []
    next_production_list = []
    for supply_link in supply_link_list:
      if supply_link != current_supply_link and \
          supply_link.getCurrentNodeValue() == next_node_value:
        next_supply_link_list.append(supply_link)
        if supply_link.isProductionSupplyLink():
          next_production_list.append(supply_link)

    if next_production_list != []:
      return next_production_list
    return next_supply_link_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getNextProductionSupplyLinkList')
  def getNextProductionSupplyLinkList(self, current_supply_link):
    """
      Return the next SupplyLink which represents a production,
      if there is one.
      No recursion is done.
    """
    next_supply_link_list = self.getNextSupplyLinkList(current_supply_link)
    return [x for x in next_supply_link_list if x.isProductionSupplyLink()]
    
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getNextProductionIndustrialPhaseList')
  def getNextProductionIndustrialPhaseList(self, current_supply_link):
    """
      Return all next industrial phase representing a production.
    """
    ind_phase_dict = {}
    for link in self.getNextProductionSupplyLinkList(current_supply_link):
      for ind_phase in link.getIndustrialPhaseValueList():
        ind_phase_dict[ind_phase] = 1
    # Remove None value, and generate the list
    ind_phase_dict.pop(None, None)
    return ind_phase_dict.keys()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPreviousSupplyLinkList')
  def getPreviousSupplyLinkList(self, current_supply_link):
    """
      Return the previous SupplyLink  list.
    """
    if current_supply_link is None:
      # No current_supply_link defined, we need to return the last SupplyLink
      return [self.getLastLink()]

    # Get all SupplyLink in the SupplyChain
    supply_link_list = self.objectValues(
                               portal_type=self.supply_link_portal_type)
    # Destination of valid link must be the source of the current link.
    current_node_value = current_supply_link.getCurrentNodeValue()

    previous_supply_link_list = []
    previous_production_list = []
    for supply_link in supply_link_list:
      if supply_link != current_supply_link and \
        supply_link.getNextNodeValue() == current_node_value:
        previous_supply_link_list.append(supply_link)
        if supply_link.isProductionSupplyLink():
          previous_production_list.append(supply_link)

    if previous_production_list != []:
      return previous_production_list
    return previous_supply_link_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPreviousProductionSupplyLinkList')
  def getPreviousProductionSupplyLinkList(self, current_supply_link, 
                                          recursive=False, all=False,
                                          checked_link_list=None):
    """
      Return the previous SupplyLink which represents a production.
      If recursive, browse the SupplyChain until a valid link is found.
      checked_link_list is used to prevent infinite loop.
    """
    # XXX document "all" parameter if you can

    # Initialize checked_link_list parameter...
    if checked_link_list is None:
      checked_link_list = []
    # Checked if we already tested this link 
    # to prevent infinite loop
    if current_supply_link in checked_link_list:
      raise SupplyChainError,\
            "SupplyLink %r is in a loop." % current_supply_link

    transformation_link_list = []
    checked_link_list.append(current_supply_link)
    # Get the previous link list
    previous_link_list = self.getPreviousSupplyLinkList(current_supply_link)
    # Test each link
    for previous_link in previous_link_list:
      if not previous_link.isProductionSupplyLink():
        # current is invalid
        if not recursive:
          continue
      else:
        # Great, we found a valid one
        transformation_link_list.append(previous_link)
        # Prevent infinite loop when 2 production_link have the same
        # destination
        if (current_supply_link is not None) and \
           (current_supply_link.isProductionSupplyLink()):
          raise SupplyChainError,\
                "Those SupplyLinks are in conflict: %r and %r" %\
                (current_supply_link.getRelativeUrl(),\
                 previous_link.getRelativeUrl())
        if not recursive and not all:
          continue

      # Browse the previous link
      transformation_link_list.extend(
        self.getPreviousProductionSupplyLinkList(
                                     previous_link, 
                                     recursive=recursive, all=all,
                                     checked_link_list=checked_link_list))
    # Return result
    return transformation_link_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPreviousPackingListSupplyLinkList')
  def getPreviousPackingListSupplyLinkList(self, current_supply_link, 
                                           recursive=False, all=False,
                                           checked_link_list=None,
                                           movement=None):
    """
      Return the previous SupplyLink which represents a production.
      If recursive, browse the SupplyChain until a valid link is found.
      checked_link_list is used to prevent infinite loop.
    """
    # XXX document "all" parameter

    # Initialize checked_link_list parameter...
    if checked_link_list is None:
      checked_link_list = []
    # Checked if we already tested this link 
    # to prevent infinite loop
    if current_supply_link in checked_link_list:
      raise SupplyChainError,\
            "SupplyLink %r is in a loop." % current_supply_link

    packing_list_link_list = []
    checked_link_list.append(current_supply_link)
    # Get the previous link list
    previous_link_list = self.getPreviousSupplyLinkList(current_supply_link)
    # Test each link
    for previous_link in previous_link_list:
      concurrent_list = previous_link_list[:]
      concurrent_list.remove(previous_link)
      # Great, we find a valid one
      if previous_link.isPackingListSupplyLink():
        if (movement is None) or\
           (previous_link.test(movement, concurrent_list)):
          packing_list_link_list.append(previous_link)
        # Browse the previous link
        if recursive:
          packing_list_link_list.extend(
            self.getPreviousPackingListSupplyLinkList(
                                       previous_link,
                                       recursive=recursive,
                                       checked_link_list=checked_link_list))
    # Return result
    return packing_list_link_list

  def getPreviousIndustrialPhaseList(self, current_supply_link, method_id,
                                     include_current=False, all=False):
    """
      Return recursively all previous industrial phase.
    """
    method = getattr(self, method_id)
    previous_supply_link_list = method(current_supply_link, recursive=1,
                                       all=all)
    # Add the current industrial phase
    if include_current:
      previous_supply_link_list.append(current_supply_link)
    # Generate the industrial phase list, and remove double
    ind_phase_dict = {}
    for supply_link in previous_supply_link_list:
      ind_phase_value_list = supply_link.getIndustrialPhaseValueList()
      for ind_phase in ind_phase_value_list:
        ind_phase_dict[ind_phase] = 1
    # Remove None value, and generate the list
    ind_phase_dict.pop(None, None)
    ind_phase_list = ind_phase_dict.keys()
    return ind_phase_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPreviousProductionIndustrialPhaseList')
  def getPreviousProductionIndustrialPhaseList(self, current_supply_link,
                                               all=False):
    """
      Return recursively all previous industrial phase representing 
      a production.
    """
    return self.getPreviousIndustrialPhaseList(
                                   current_supply_link,
                                   "getPreviousProductionSupplyLinkList",
                                   all=all)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPreviousPackingListIndustrialPhaseList')
  def getPreviousPackingListIndustrialPhaseList(self, current_supply_link):
    """
      Return recursively all previous industrial phase representing 
      a packing list.
    """
    return self.getPreviousIndustrialPhaseList(
                                   current_supply_link,
                                   "getPreviousPackingListSupplyLinkList",
                                   include_current=True)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'test')
  def test(self, current_supply_link, movement):
    """
      Test if the resource on the movement can be delivered by 
      the previous supply link of the current one.
    """
    result = 0
    previous_packing_link_list = self.\
                   getPreviousPackingListSupplyLinkList(current_supply_link)
    for previous_supply_link in previous_packing_link_list:
      concurrent_list = previous_packing_link_list[:]
      concurrent_list.remove(previous_supply_link)
      if previous_supply_link.test(movement, concurrent_list):
        result = 1
        break
    return result
