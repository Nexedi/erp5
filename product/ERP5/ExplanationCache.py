# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2O10 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import types

from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

class ExplanationCache:
  """ExplanationCache provides a central access to 
  all parameters and values which are needed to process 
  an explanation. It is based on the idea that a value is calculated
  once and once only, as a way to accelerate performance of algorithms
  related to an explanation.

        'explanation_uid': self._getExplanationUidList(explanation) # XXX-JPS why do we need explanation_uid ? and why a list
        'simulation_path': simulation_path,

    explanation_uid = self._getExplanationUidList(explanation) # A hint value to reduce the size of the tree
    simulation_path = '/erp5/p.../%' # A list of path

"""
  def __init__(self, explanation):
    """
    """
    # Define share properties
    self.explanation = explanation
    self.portal_catalog = getToolByName(explanation 'portal_catalog')
    self.simulation_movement_cache = {} # Simulation Movement Cache
    self.explanation_uid_cache = []
    self.explanation_path_pattern_cache = []

  def getDeliveryMovementList(self):
    """Returns self is explanation is a delivery line
    of the list of explanation delivery lines if explanation
    is a delivery
    """
    explanation = self.explanation
    if explanation.isDelivery():
      # Gather all movements of the delivery
      delivery_movement_list = explanation.getMovementList()
    else:
      # Only consider a single movement - XXX-JPS is this OK when we have lines in lines ?
      delivery_movement_list = [explanation]
    return delivery_movement_list

  def getRootExplanationUidList(self):
    """Return the list of explanation_uid values involved
    in the context of the explanation. This will be useful later
    in order to accelerate searches in the catalog.
    """
    # Return cache if defined
    if self.explanation_uid_cache:
      return self.explanation_uid_cache
    result = set()
    # For each delivery movement
    for movement in self.getDeliveryMovementList():
      # For each simulation movement
      for simulation_movement in movement.getDeliveryRelatedValueList():
        result.add(simulation_movement.getExplanationUid()) # XXX-JPS use new API later
    # Return result
    self.explanation_uid_cache = result
    return result

  def getSimulationPathPatternList(self):
    """Return the list of root path of simulation tree which are 
    involved in the context of the explanation. This will be useful later
    in order to accelerate searches in the catalog.
    """
    # Return cache if defined
    if self.explanation_path_pattern_cache:
      return self.explanation_path_pattern_cache

    # Helper method to update path_dict with
    # each key which forms the pay of the simulation_movement
    path_dict = {}
    def updatePathDict(simulation_movement):
      local_path_dict = path_dict
      container_path = simulation_movement.getParentValue().getPhysicalPath()
      simulation_movement_id = simulation_movement.getId()
      insert_movement = True
      for path_id in container_path:
        if local_path_dict.get(path_id, None) is None:
          local_path_dict[path_id] = dict()
        local_path_dict = local_path_dict[path_id]
        if type(local_path_dict) is not types.DictType:
          # A movement was already inserted
          insert_movement = False
          break
      if insert_movement:
        local_path_dict[simulation_movement_id] = simulation_movement

    # For each delivery movement
    for movement in self.getDeliveryMovementList():
      # For each simulation movement
      for simulation_movement in movement.getDeliveryRelatedValueList():
        updatePathDict(simulation_movement)
    
    # Build result by browsing path_dict and
    # assembling path '/erp5/portal_simulation/1/34/23/43%'
    result = []
    def browsePathDict(prefix, local_path_dict):
      for key, value in local_path_dict.items():
        if type(value) is not types.DictType:
          # We have a real root
          result.append('%s/%s%' % (prefix, key))
        else:
          browsePathDict('%s/%s' % (prefix, key), value) # Recursing with string append is slow XXX-JPS

    browsePathDict('', path_dict)
    self.explanation_path_pattern_cache = result
    return result

  def getBusinessPathRelatedSimulationMovementValueList(self, business_path):
    """Returns the list of simulation movements caused by a business_path
    in the context the our explanation.
    """
    return self.getSimulationMovementList(causality_uid=business_path.getUid())
    
  def getSimulationMovementList(self, **kw)
    """Search Simulation Movements related to our explanation.
    Cache result so that the second time we saarch for the same
    list we need not involve the catalog again.
    """
    kw_tuple = tuple(kw.items()) # We hope that no sorting is needed
    if self.simulation_movement_list.get(kw_tuple, None) is None:
      self.simulation_movement_cache[kw_tuple] = \
           self.portal_catalog(portal_type="Simulation Movement",
                               explanation_uid=self.getRootExplanationUidList(),
                               path=self.getSimulationPathPatternList(), # XXX-JPS Explicit Query is better
                               **kw)
    return self.simulation_movement_cache[kw_tuple]

def _getExplanationCache(explanation):
  # Return cached value if any
  tv = getTransactionalVariable(explanation)
  if tv.get('explanation_cache', None) is None:
    tv['explanation_cache'] =  ExplanationCache(explanation)
  return tv.get('explanation_cache')
