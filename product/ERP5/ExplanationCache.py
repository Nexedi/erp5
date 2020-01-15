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

from collections import defaultdict
from zLOG import LOG
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod


class treenode(defaultdict):

  def __init__(self):
    defaultdict.__init__(self, self.__class__)


class ExplanationCache:
  """ExplanationCache provides a central access to
  all parameters and values which are needed to process
  an explanation. It is based on the idea that a value is calculated
  once and once only, as a way to accelerate performance of algorithms
  related to an explanation.

  TODO:
  - implement property explanation calculation
    (with parent simulation movements, not only children)
  """

  def __init__(self, explanation):
    """Explanation cache keeps a handful list of caches
    to accelerate performance of business path browsing and
    business process algorithms
    """
    # Define share properties
    self.explanation = explanation
    self.portal_catalog = explanation.getPortalObject().portal_catalog
    self.simulation_movement_cache = {} # Simulation Movement Cache
    self.explanation_uid_cache = []
    self.explanation_path_pattern_cache = []
    self.reference_date_cache = {}
    self.closure_cache = {}
    self.union_cache = None

  def _getDeliveryMovementList(self):
    """Returns self if explanation is a delivery line
    or the list of explanation delivery lines if explanation
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
    for movement in self._getDeliveryMovementList():
      # For each simulation movement
      for simulation_movement in movement.getDeliveryRelatedValueList():
        result.add(simulation_movement.getExplanationUid()) # XXX-JPS use new API later
    # Return result
    self.explanation_uid_cache = tuple(result)
    return self.explanation_uid_cache

  def getSimulationPathPatternList(self):
    """Return the list of root path of simulation tree which are
    involved in the context of the explanation. This will be useful later
    in order to accelerate searches in the catalog.

    XXX-JPS: QUESTION: should we consider only patterns starting from
    the movement, or from the root delivery line related movement ?
    In one case, we must provided appropriate explanation for everything
    to work. In the other case, we can take any delivery line any where
    a explanation.
    """
    # Return cache if defined
    result = self.explanation_path_pattern_cache
    if not result:
      prefix = self.portal_catalog.getPortalObject().getPath() + '/'

      # path_dict is typically like this:
      #  {'portal_simulation': {'3': {'4': None}}}
      path_dict = treenode()
      simulation_movement_list = []
      for movement in self._getDeliveryMovementList():
        simulation_movement_list += movement.getDeliveryRelatedList()
      simulation_movement_list.sort()
      # Now it's sorted, we'll process parents before their children.
      for simulation_movement in simulation_movement_list:
        local_path_dict = path_dict
        container_path = simulation_movement.split('/')
        simulation_movement_id = container_path.pop()
        for path_id in container_path:
          local_path_dict = local_path_dict[path_id]
          if local_path_dict is None:
            break # A movement was already inserted
        else:
          # We have a real root
          local_path_dict[simulation_movement_id] = None
          simulation_movement = prefix + simulation_movement
          result.append(simulation_movement)
          result.append(simulation_movement.replace('_', r'\_')  + '/%')
          # XXX-JPS here we must add all parent movements XXX-JPS
    return result

  def getBusinessLinkRelatedSimulationMovementValueList(self, business_link):
    """Returns the list of simulation movements caused by a business_link
    in the context the our explanation.
    """
    return self.getSimulationMovementValueList(causality_uid=business_link.getUid())

  def getBusinessLinkRelatedMovementValueList(self, business_link):
    """Returns the list of delivery movements related to a business_link
    in the context the our explanation.
    """
    #XXXXXXXXXXX BAD
    return self.getSimulationMovementValueList(causality_uid=business_link.getUid())

  @UnrestrictedMethod
  def getSimulationMovementValueList(self, **kw):
    """Search Simulation Movements related to our explanation.
    Cache result so that the second time we saarch for the same
    list we need not involve the catalog again.

    NOTE:
    - this method can be made catalog independent
      in case explanation is an applied rule, we can
      browse parent and child movement
    """
    kw_tuple = tuple(kw.items()) # We hope that no sorting is needed

    def getParentSimulationMovementValueList(obj, movement_list, trade_phase):
      parent = obj.getParentValue()
      while parent.getPortalType() == "Simulation Movement":
        if parent.isMemberOf(trade_phase, strict_membership=1):
          movement_list.append(parent)
        parent = parent.getParentValue().getParentValue()

    def getChildSimulationMovementValueList(obj, movement_list, trade_phase):
      for child in obj.objectValues():
        if (child.getPortalType() == "Simulation Movement" and
            child.isMemberOf(trade_phase, strict_membership=1)):
          movement_list.append(child)
        getChildSimulationMovementValueList(child, movement_list, trade_phase)

    if kw_tuple not in self.simulation_movement_cache:
      if self.explanation.getPortalType() == "Applied Rule":
        movement_list = []
        getParentSimulationMovementValueList(self.explanation, movement_list, kw['trade_phase'])
        getChildSimulationMovementValueList(self.explanation, movement_list, kw['trade_phase'])
        self.simulation_movement_cache[kw_tuple] = movement_list
      else:
        # XXX-Aurel : the following code seems not working as expected, it returns
        # all simulation movements from a site
        if kw.get('path', None) is None:
          kw['path'] = self.getSimulationPathPatternList() # XXX-JPS Explicit Query is better
        # XXX-Seb It seems incompatible with the way explanation is working
        # Indeed, the explanation is not the same all other the simulation tree
        #      path                explanation
        # portal_simulation/91/1 testing_folder/17
        # portal_simulation/91/1/1 testing_folder/17
        # portal_simulation/91/1/1/1 testing_folder/18
        # portal_simulation/91/1/1/1/1 testing_folder/18
        # portal_simulation/91/1/1/1/1/1 testing_folder/17
        #if kw.get('explanation_uid', None) is None:
        #  kw['explanation_uid'] = self.getRootExplanationUidList()
        if 'trade_phase' in kw:
          kw['trade_phase_relative_url'] = kw.pop('trade_phase')
        self.simulation_movement_cache[kw_tuple] = self.portal_catalog(
          portal_type="Simulation Movement", **kw)

    return self.simulation_movement_cache[kw_tuple]

  def getBusinessLinkValueList(self, **kw):
    """Find all business path which are related to the simulation
    trees defined by the explanation.
    """
    business_type_list = self.getPortalBusinessLinkTypeList()
    simulation_movement_list = self.getSimulationMovementValueList()
    simulation_movement_uid_list = map(lambda x:x.uid, simulation_movement_list)
    # We could use related keys instead of 2 queries
    business_link_list = self.portal_catalog(
                      portal_type=business_type_list,
                      causality_related_uid=simulation_movement_uid_list,
                      **kw)
    return business_link_list

  def getBusinessLinkClosure(self, business_process, business_link):
    """Creates a Business Process by filtering out all Business Link
    in 'business_process' which are not related to a simulation movement
    which is either a parent or a child of explanation simulations movements
    caused by 'business_link'

    NOTE: Business Link Closure must be at least as "big" as composed
    business path. The appropriate calculation is still not clear.
    Options are:
      - take all link of composed business link (even not yet expanded)
      - take all link of composed business link which phase is not yet expanded
    """
    # Try to return cached value first
    new_business_process = self.closure_cache.get(business_link, None)
    if new_business_process is not None:
      return new_business_process

    # Build a list of path patterns which apply to current business_link
    path_list = iter(self.getSimulationPathPatternList())
    path_dict = {x: path_list.next() for x in path_list}
    # path_dict is like this;
    # {'/erp5/portal_simulation/3/4': r'/erp5/portal\_simulation/3/4/%'}
    path_list = []
    for simulation_movement in \
        self.getBusinessLinkRelatedSimulationMovementValueList(business_link):
      simulation_path = simulation_movement.getPath()
      if simulation_path in path_dict:
        path = simulation_path
      else:
        for path in path_dict:
          if simulation_path.startswith(path) and \
             simulation_path[len(path)] == '/':
            break
        else:
          continue
      # Only keep a path pattern which matches current simulation movement
      path_list.append(path)
      path_list.append(path_dict.pop(path))

    # Lookup in cache based on path_list
    path_list.sort()
    path_list = tuple(path_list)
    new_business_process = self.closure_cache.get(path_list)
    if new_business_process is None:
      business_link_list = []
      new_business_process = business_process
      for x in business_process.getBusinessLinkValueList():
        if self.getSimulationMovementValueList(path=path_list,
                                               causality_uid=x.getUid()):
          # We have matching movements.
          business_link_list.append(x)
        else:
          new_business_process = None
      if new_business_process is None:
        # Build a new closure business process.
        # Initially, business_process is often the result of
        # asComposedDocument() and business_process.getParentValue() is not a
        # module where newContent() allows creation of Business Processes.
        # XXX-JPS is this really OK with union business processes
        new_business_process = self.explanation.newContent(temp_object=True,
          portal_type='Business Process', id='closure_business_process')
        for i, x in enumerate(business_link_list):
          id = 'closure_path_%s' % i
          new_business_process._setOb(id, x.asContext(id=id))
      self.closure_cache[path_list] = new_business_process

    self.closure_cache[business_link] = new_business_process
    return new_business_process

  def getUnionBusinessProcess(self):
    """Return a Business Process made of all Business Link
    which are the cause of Simulation Movements in the simulation
    trees related to explanation.
    """
    # Try to return cached value first
    new_business_process = self.union_cache
    if new_business_process is not None:
      return new_business_process

    # Build Union Business Process
    new_business_process = self.explanation.newContent(temp_object=True,
      portal_type='Business Process', id='union_business_process')
    i = 0
    for business_link in self.getBusinessLinkValueList():
      i += 1
      id = 'union_path_%s' % i
      new_business_process._setOb(id, business_link.asContext(id=id))

    # Keep it in cache and return
    self.union_cache = new_business_process
    return new_business_process

  def getReferenceDate(self, business_process, trade_phase,
                       reference_date_method_id, delay_mode=None):
    """Browse parent similation movements until a movement with
    appropriate trade_phase is found.
    """
    cache = self.reference_date_cache
    reference_date_key = (business_process.getPhysicalPath(), trade_phase,
                          reference_date_method_id, delay_mode)
    try:
      result = cache[reference_date_key]
      if result is self: # use self as marker to detect infinite recursion
        __traceback_info__ = (business_process.getPath(), trade_phase,
                              reference_date_method_id, delay_mode)
        raise ValueError('No reference date is defined, probably due to missing Trade Model Path in Business Process')
      return result
    except KeyError:
      cache[reference_date_key] = self

    # Find simulation movements with appropriate trade_phase
    movement_list = self.getSimulationMovementValueList(trade_phase=trade_phase)

    # Case 1: some (parent) simulation movement with appropriate trade phase exists
    if len(movement_list):
      # XXX-JPS - for now take arbitrary one
      # but we should in reality some way to configure this
      movement = movement_list[0]
      method = getattr(movement, reference_date_method_id)
      cache[reference_date_key] = result = method()
      return result

    # Case 2: we must recursively find another trade phase
    # to find the value recursively
    # XXX-JPS this is only useful for production (MRP) in reality
    # whenever trade model path define time constraints within the same
    # movement generator (ie. transformation with multiple phases)
    path_list = business_process.getTradeModelPathValueList(trade_phase=trade_phase, context=business_process)
    if not len(path_list):
      raise ValueError('No Trade Model Path defines a reference data.')

    path = path_list[0]
    # XXX-JPS - for now take arbitrary one
    # but we should in reality some way to configure this
    start_date, stop_date = business_process.getExpectedTradeModelPathStartAndStopDate(
                                   self.explanation, path, delay_mode=delay_mode)

    # Create a fake simulation movement and lookup property
    movement = self.explanation.newContent(portal_type="Simulation Movement",
                                           temp_object=True,
                                           start_date=start_date, stop_date=stop_date,
                                           trade_phase=trade_phase, causality=path)
    method = getattr(movement, reference_date_method_id)
    cache[reference_date_key] = result = method()
    return result

_getExplanationCache = transactional_cached()(ExplanationCache)

def _getBusinessLinkClosure(business_process, explanation, business_link):
  """Returns a closure Business Process for given
  business_link and explanation. This Business Process
  contains only those Business Link which are related to business_link
  in the context of explanation.
  """
  if explanation.getPortalType() == "Applied Rule":
    # There is no way to guess the closure during expand
    # since some movements may not be generated. The resulting
    # closure might be smaller than expexted
    return business_process
  explanation_cache = _getExplanationCache(explanation)
  return explanation_cache.getBusinessLinkClosure(business_process, business_link)

def _getUnionBusinessProcess(explanation):
  """Build a Business Process by taking the union of Business Link
  which are involved in the simulation trees related to explanation
  """
  explanation_cache = _getExplanationCache(explanation)
  return explanation_cache.getUnionBusinessProcess()
