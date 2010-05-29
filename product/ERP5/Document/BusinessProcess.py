# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Yusuke Muraoka <yusuke@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Path import Path
from Products.ERP5.ExplanationCache import _getExplanationCache, _getBusinessPathClosure

import zope.interface

class BusinessProcess(Path, XMLObject):
  """The BusinessProcess class is a container class which is used
  to describe business processes in the area of trade, payroll
  and production. Processes consists of a collection of Business Path
  which define an arrow between a 'predecessor' trade_state and a 
  'successor' trade_state, for a given trade_phase_list.

  TODO:
  - add support to prevent infinite loop. (but beware, this notion has changed
    with Union of Business Process, since the loop should be detected only
    as part of a given business process closure)
  - handle all properties of PaymentCondition in date calculation
  - review getRemainingTradePhaseList
  - optimize performance so that the completion dates are calculated
    only once in a transaction thanks to caching (which could be 
    handled in coordination with ExplanationCache infinite loop
    detection)

  RENAMED:
    getPathValueList -> getBusinessPathValueList
  """
  meta_type = 'ERP5 Business Process'
  portal_type = 'Business Process'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Folder
                    , PropertySheet.Comment
                    , PropertySheet.Arrow
                    , PropertySheet.BusinessProcess
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.IBusinessProcess,
                            interfaces.IArrowBase)

  # IBusinessPathProcess implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'getBusinessPathValueList')
  def getBusinessPathValueList(self, trade_phase=None, context=None,
                               predecessor=None, successor=None, **kw):
    """Returns all Path of the current BusinessProcess which
    are matching the given trade_phase and the optional context.

    trade_phase -- filter by trade phase

    context -- a context to test each Business Path on
               and filter out Business Path which do not match

    predecessor -- filter by trade state predecessor

    successor -- filter by trade state successor

    **kw -- same arguments as those passed to searchValues / contentValues
    """
    if trade_phase is None:
      trade_phase = set()
    elif not isinstance(trade_phase, (list, tuple)):
      trade_phase = set((trade_phase,))
    else:
      trade_phase = set(trade_phase)
    result = []
    if kw.get('portal_type', None) is None:
      kw['portal_type'] = self.getPortalBusinessPathTypeList()
    if kw.get('sort_on', None) is None:
      kw['sort_on'] = 'int_index'
    original_business_path_list = self.objectValues(**kw), # Why Object Values ??? XXX-JPS
    if len(trade_phase) == 0:
      return original_business_path_list # If not trade_phase is specified, return all Business Path
    # Separate the selection of business paths into two steps
    # for easier debugging.
    # First, collect business paths which can be applicable to a given context.
    business_path_list = []
    for business_path in original_business_path_list:
      if predecessor is not None and business_path.getPredecessor() != predecessor:
        break # Filter our business path which predecessor does not match
      if successor is not None and business_path.getSuccessor() != successor:
        break # Filter our business path which predecessor does not match
      if trade_phase.intersection(business_path.getTradePhaseList()):
        business_path_list.append(business_path)
    # Then, filter business paths by Predicate API.
    # FIXME: Ideally, we should use the Domain Tool to search business paths,
    # and avoid using the low level Predicate API. But the Domain Tool does
    # support the condition above without scripting?
    for business_path in business_path_list:
      if business_path.test(context):
        result.append(business_path)
    return result

  def isBusinessPathCompleted(self, explanation, business_path):
    """Returns True if given Business Path document
    is completed in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    business_path -- a Business Path document
    """
    # Return False if Business Path is not completed
    if not business_path.isCompleted(explanation):
      return False
    predecessor_state = business_path.getPredecessor()
    if not predecessor_state:
      # This is a root business path, no predecessor
      # so no need to do any recursion
      return True
    if self.isTradeStateCompleted(explanation, predecessor_state):
      # If predecessor state is globally completed for the 
      # given explanation, return True
      # Please note that this is a specific case for a Business Process
      # built using asUnionBusinessProcess. In such business process
      # a business path may be completed even if its predecessor state
      # is not
      return True
    # Build the closure business process which only includes those business 
    # path wich are directly related to the current business path but DO NOT 
    # narrow down the explanation else we might narrow down so much that
    # it becomes an empty set
    closure_process = _getBusinessPathClosure(self, explanation, business_path)
    return closure_process.isTradeStateCompleted(explanation, predecessor_state)

  def isBusinessPathPartiallyCompleted(self, explanation, business_path):
    """Returns True if given Business Path document
    is partially completed in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    business_path -- a Business Path document
    """
    # Return False if Business Path is not partially completed
    if not business_path.isPartiallyCompleted(explanation):
      return False
    predecessor_state = business_path.getPredecessor()
    if not predecessor_state:
      # This is a root business path, no predecessor
      # so no need to do any recursion
      return True
    if self.isTradeStatePartiallyCompleted(explanation, predecessor_state):
      # If predecessor state is globally partially completed for the 
      # given explanation, return True
      # Please note that this is a specific case for a Business Process
      # built using asUnionBusinessProcess. In such business process
      # a business path may be partially completed even if its predecessor
      # state is not
      return True
    # Build the closure business process which only includes those business 
    # path wich are directly related to the current business path but DO NOT 
    # narrow down the explanation else we might narrow down so much that
    # it becomes an empty set
    closure_process = _getBusinessPathClosure(explanation, business_path)
    return closure_process.isTradeStatePartiallyCompleted(explanation, 
                                                           predecessor_state)

  def getExpectedBusinessPathCompletionDate(self, explanation, business_path, 
                                                       delay_mode=None):
    """Returns the expected completion date of given Business Path document
    in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    business_path -- a Business Path document

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay
    """
    closure_process = _getBusinessPathClosure(self, explanation, business_path)
    # XXX use explanatoin cache to optimize
    predecessor = business_path.getPredecessor()
    if closure_process.isTradeStateRootState(predecessor):
      return business_path.getCompletionDate(explanation)

    # Recursively find reference_date
    reference_date = closure_process.getExpectedTradeStateCompletionDate(explanation, predecessor)
    start_date = reference_date + business_path.getPaymentTerm() # XXX-JPS Until better naming
    if delay_mode == 'min':
      delay = business_path.getMinDelay()
    elif delay_mode == 'max':
      delay = business_path.getMaxDelay()
    else:
      delay = (business_path.getMaxDelay() + business_path.getMinDelay()) / 2.0
    stop_date = start_date + delay
    
    completion_date_method_id = business_path.getCompletionDateMethodId()
    if completion_date_method_id == 'getStartDate':
      return start_date
    elif completion_date_method_id == 'getStopDate':
      return stop_date
    
    raise ValueError("Business Path does not support %s complete date method" % completion_date_method_id)    

  def getExpectedBusinessPathStartAndStopDate(self, explanation, business_path,
                                                         delay_mode=None):
    """Returns the expected start and stop dates of given Business Path
    document in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    business_path -- a Business Path document

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay
    """
    closure_process = _getBusinessPathClosure(self, explanation, business_path)
    # XXX use explanatoin cache to optimize
    trade_date = self.getTradeDate()
    if trade_date is not None:
      reference_date = closure_process.gettExpectedTradePhaseCompletionDate(explanation, trade_date)
    else:
      predecessor = business_path.getPredecessor() # XXX-JPS they should all have
      reference_date = closure_process.getExpectedTradeStateCompletionDate(explanation, predecessor)

    # Recursively find reference_date
    reference_date = closure_process.getExpectedTradeStateCompletionDate(explanation, predecessor)
    start_date = reference_date + business_path.getPaymentTerm() # XXX-JPS Until better naming
    if delay_mode == 'min':
      delay = business_path.getMinDelay()
    elif delay_mode == 'max':
      delay = business_path.getMaxDelay()
    else:
      delay = (business_path.getMaxDelay() + business_path.getMinDelay()) / 2.0
    stop_date = start_date + delay
        
    return start_date, stop_date

  # IBuildableBusinessPathProcess implementation
  def getBuildableBusinessPathValueList(self, explanation):
    """Returns the list of Business Path which are buildable
    by taking into account trade state dependencies between
    Business Path.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    result = []
    for business_path in self.getBusinessPathValueList():
      if self.isBusinessPathBuildable(explanation, business_path):
        result.append(business_path)
    return result

  def getPartiallyBuildableBusinessPathValueList(self, explanation):
    """Returns the list of Business Path which are partially buildable
    by taking into account trade state dependencies between
    Business Path.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    result = []
    for business_path in self.getBusinessPathValueList():
      if self.isBusinessPathPartiallyBuildable(explanation, business_path):
        result.append(business_path)
    return result

  def isBusinessPathBuildable(self, explanation, business_path):
    """Returns True if any of the related Simulation Movement
    is buildable and if the predecessor trade state is completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    business_path -- a Business Path document
    """
    # If everything is delivered, no need to build
    if business_path.isDelivered(explanation):
      return False
    # We must take the closure cause only way to combine business process
    closure_process = _getBusinessPathClosure(self, explanation, business_path)
    predecessor = business_path.getPredecessor()
    return closure_process.isTradeStateCompleted(predecessor)

  def isBusinessPathPartiallyBuildable(self, explanation, business_path):
    """Returns True if any of the related Simulation Movement
    is buildable and if the predecessor trade state is partially completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    business_path -- a Business Path document
    """
    # If everything is delivered, no need to build
    if business_path.isDelivered(explanation):
      return False
    # We must take the closure cause only way to combine business process
    closure_process = _getBusinessPathClosure(self, explanation, business_path)
    predecessor = business_path.getPredecessor()
    return closure_process.isTradeStatePartiallyCompleted(predecessor)

  # ITradeStateProcess implementation
  def getTradeStateList(self):
    """Returns list of all trade_state of this Business Process
    by looking at successor and predecessor values of contained
    Business Path.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    result = set()
    for business_path in self.getBusinessPathValueList():
      result.add(business_path.getPredecessor())
      result.add(business_path.getSuccessor())
    return result

  def getSuccessorTradeStateList(self, explanation, trade_state):
    """Returns the list of successor states in the 
    context of given explanation. This list is built by looking
    at all successor of business path involved in given explanation
    and which predecessor is the given trade_phase.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """
    result = set()
    for business_path in self.getBusinessPathValueList():
      if business_path.getPredecessor() == trade_state:
        result.add(business_path.getSuccessor())
    return result

  def getPredecessorTradeStateList(self, explanation, trade_state):
    """Returns the list of predecessor states in the 
    context of given explanation. This list is built by looking
    at all predecessor of business path involved in given explanation
    and which sucessor is the given trade_phase.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """
    result = set()
    for business_path in self.getBusinessPathValueList():
      if business_path.getSuccessor() == trade_state:
        result.add(business_path.getPredecessor())
    return result

  def getCompletedTradeStateList(self, explanation):
    """Returns the list of Trade States which are completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    return filter(lambda x:self.isTradeStateCompleted(explanation, x), self.getTradeStateList())

  def getPartiallyCompletedTradeStateList(self, explanation):
    """Returns the list of Trade States which are partially 
    completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    return filter(lambda x:self.isTradeStatePartiallyCompleted(explanation, x), self.getTradeStateList())

  def getLatestCompletedTradeStateList(self, explanation):
    """Returns the list of completed trade states which predecessor
    states are completed and for which no successor state 
    is completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    result = set()
    for state in self.getCompletedTradeStateValue(explanation):
      for business_path in state.getPredecessorRelatedValueList():
        if not self.isBusinessPathCompleted(explanation, business_path):
          result.add(state)
    return result

  def getLatestPartiallyCompletedTradeStateList(self, explanation):
    """Returns the list of completed trade states which predecessor
    states are completed and for which no successor state 
    is partially completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    result = set()
    for state in self.getCompletedTradeStateValue(explanation):
      for business_path in state.getPredecessorRelatedValueList():
        if not self.isBusinessPathPartiallyCompleted(explanation, business_path):
          result.add(state)
    return result

  def isTradeStateCompleted(self, explanation, trade_state):
    """Returns True if all predecessor trade states are
    completed and if no successor trade state is completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """
    for business_path in self.getBusinessPathValueList(successor=trade_state):
      if not closure_process.isBusinessPathCompleted(explanation, business_path):
        return False
    return True      

  def isTradeStatePartiallyCompleted(self, explanation, trade_state):
    """Returns True if all predecessor trade states are
    completed and if no successor trade state is partially completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """
    for business_path in self.getBusinessPathValueList(successor=trade_state):
      if not self.isBusinessPathPartiallyCompleted(explanation, business_path):
        return False
    return True      

  def getExpectedTradeStateCompletionDate(self, explanation, trade_state,
                                                         delay_mode=None):
    """Returns the date at which the give trade state is expected
    to be completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    trade_state -- a Trade State category

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay
    """
    date_list = []
    for business_path in self.getBusinessPathValueList(successor=trade_state):
      date_list.append(self.getExpectedBusinessPathCompletionDate(explanation, business_path))
    return max(date_list) # XXX-JPS provide -infinite for...

  # ITradePhaseProcess implementation
  def getTradePhaseList(self):
    """Returns list of all trade_phase of this Business Process
    by looking at trade_phase values of contained Business Path.
    """
    result = set()
    for business_path in self.getBusinessPathValueList():
      result.union(business_path.getTradePhaseList())
    return result

  def getCompletedTradePhaseList(self, explanation):
    """Returns the list of Trade Phases which are completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    return filter(lambda x:self.isTradePhaseCompleted(explanation, x), self.getTradePhaseList())
    
  def getPartiallyCompletedTradePhaseList(self, explanation):
    """Returns the list of Trade Phases which are partially completed
    in the context of given explanation. 

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    return filter(lambda x:self.isTradePhasePartiallyCompleted(explanation, x), self.getTradePhaseList())

  def isTradePhaseCompleted(self, explanation, trade_phase):
    """Returns True all business path with given trade_phase
    applicable to given explanation are completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    trade_phase -- a Trade Phase category
    """
    for business_path in self.getBusinessPathValueList(trade_phase=trade_phase):
      if not self.isBusinessPathCompleted(explanation, business_path):
        return False
    return True

  def isTradePhasePartiallyCompleted(self, explanation, trade_phase):
    """Returns True at least one business path with given trade_phase
    applicable to given explanation is partially completed
    or completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    trade_phase -- a Trade Phase category
    """
    for business_path in self.getBusinessPathValueList(trade_phase=trade_phase):
      if not self.isBusinessPathPartiallyCompleted(explanation, business_path):
        return False
    return True

  def getExpectedTradePhaseCompletionDate(self, explanation, trade_phase,
                                                       delay_mode=None):
    """Returns the date at which the give trade phase is expected
    to be completed in the context of given explanation, taking
    into account the graph of date constraints defined by business path
    and business states.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree

    trade_phase -- a Trade Phase category

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay
    """
    date_list = []
    for business_path in self.getBusinessPathValueList(trade_phase=trade_phase):
      date_list.append(self.getExpectedTradePhaseCompletionDate(explanation, business_path, delay_mode=delay_mode))
    return max(date_list)

  def getRemainingTradePhaseList(self, business_path, trade_phase_list=None):
    """Returns the list of remaining trade phases which to be achieved
    as part of a business process. This list is calculated by analysing 
    the graph of business path and trade states, starting from a given
    business path. The result if filtered by a list of trade phases. This
    method is useful mostly for production and MRP to manage a distributed
    supply and production chain.

    business_path -- a Business Path document

    trade_phase_list -- if provided, the result is filtered by it after
                        being collected - ???? useful ? XXX-JPS ?

    NOTE: this code has not been reviewed and needs review

    NOTE: explanation is not involved here because we consider here that
    self is the result of asUnionBusinessProcess and thus only contains
    applicable Business Path to a given simulation subtree. Since the list
    of remaining trade phases does not depend on exact values in the
    simulation, we did not include the explanation. However, this makes the
    API less uniform.
    """
    remaining_trade_phase_list = []
    for path in [x for x in self.objectValues(portal_type="Business Path") \
        if x.getPredecessorValue() == trade_state]:
      # XXX When no simulations related to path, what should path.isCompleted return?
      #     if True we don't have way to add remaining trade phases to new movement
      if not (path.getRelatedSimulationMovementValueList(explanation) and
              path.isCompleted(explanation)):
        remaining_trade_phase_list += path.getTradePhaseValueList()

      # collect to successor direction recursively
      state = path.getSuccessorValue()
      if state is not None:
        remaining_trade_phase_list.extend(
          self.getRemainingTradePhaseList(explanation, state, None))

    # filter just at once if given
    if trade_phase_list is not None:
      remaining_trade_phase_list = filter(
        lambda x : x.getLogicalPath() in trade_phase_list,
        remaining_trade_phase_list)

    return remaining_trade_phase_list

  # IBusinessProcess global API
  def isCompleted(self, explanation):
    """Returns True is all applicable Trade States and Trade Phases
    are completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    for state in self.getTradeStateList():
      if not state.isTradeStateCompleted(explanation):
        return False
    return True

  def getExpectedCompletionDate(self, explanation, delay_mode=None):
    """Returns the expected date at which all applicable Trade States and
    Trade Phases are completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    date_list = []
    # This implementation looks completely silly in the sense that it does
    # not try to find a "final" state. However, it has the advantage to support
    # negative delays in business path and propper optimization of ExplanationCache
    # and completion methods should actually prevent calculating the same
    # thing multiple times
    for trade_state in self.getTradeStateList():
      date_list.append(self.getExpectedTradeStateCompletionDate(explanation, delay_mode=delay_mode))
    return max(date_list)
  
  def isBuildable(self, explanation):
    """Returns True is one Business Path of this Business Process
    is buildable in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    return len(self.getBuildableBusinessPathValueList(explanation)) != 0

  def isPartiallyBuildable(self, explanation):
    """Returns True is one Business Path of this Business Process
    is partially buildable in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree
    """
    return len(self.getPartiallyBuildableBusinessPathValueList(explanation)) != 0

  def build(self, explanation):
    """
      Build whatever is buildable
    """
    for business_path in self.getBuildableBusinessPathValueList(explanation):
      business_path.build(explanation)


  # GARBAGE - XXXXXXXXXXXXXXXXXXXXXXX - all code after here must be removed 
  # renamed with _LEGACY_ prefix to be sure that this code is not called by any method

  def _LEGACY_getExpectedStateBeginningDate(self, explanation, trade_state, *args, **kwargs):
    """
      Returns the expected beginning date for this
      state based on the explanation.

      explanation -- the document
    """
    # Should be re-calculated?
    # XXX : what is the purpose of the two following lines ? comment it until there is
    # good answer
    if 'predecessor_date' in kwargs:
      del kwargs['predecessor_date']
    predecessor_list = [x for x in self.objectValues(portal_type="Business Path") \
        if x.getPredecessorValue() == trade_state]
    date_list = self._getExpectedDateList(explanation,
                                          predecessor_list,
                                          self._getExpectedBeginningDate,
                                          *args,
                                          **kwargs)
    if len(date_list) > 0:
      return min(date_list)

  def _LEGACY_getExpectedBeginningDate(self, path, *args, **kwargs):
    expected_date = path.getExpectedStartDate(*args, **kwargs)
    if expected_date is not None:
      return expected_date - path.getWaitTime()

  def _LEGACY__getExpectedDateList(self, explanation, path_list, path_method,
                           visited=None, *args, **kwargs):
    """
      getExpected(Beginning/Completion)Date are same structure
      expected date of each path should be returned.

      explanation -- the document
      path_list -- list of target business path
      path_method -- used to get expected date on each path
      visited -- only used to prevent infinite recursion internally
    """
    if visited is None:
      visited = []

    expected_date_list = []
    for path in path_list:
      # filter paths without path of root explanation
      if path not in visited or path.isDeliverable():
        expected_date = path_method(path, explanation, visited=visited, *args, **kwargs)
        if expected_date is not None:
          expected_date_list.append(expected_date)

    return expected_date_list

  def _LEGACY_getRootExplanationPathValue(self): # XXX-JPS not in API
    """
      Returns a root path of this business process
    """
    path_list = self.objectValues(portal_type=self.getPortalBusinessPathTypeList())
    path_list = filter(lambda x: x.isDeliverable(), path_list)
    
    if len(path_list) > 1:
      raise Exception, "this business process has multi root paths"

    if len(path_list) == 1:
      return path_list[0]

  def _LEGACY_getHeadPathValueList(self, trade_phase_list=None): # XXX-JPS not in API
    """
      Returns a list of head path(s) of this business process

      trade_phase_list -- used to filtering, means that discovering
                          a list of head path with the trade_phase_list
    """
    head_path_list = list()
    for state in self.getStateValueList():
      if len(state.getSuccessorRelatedValueList()) == 0:
        head_path_list += state.getPredecessorRelatedValueList()

    if trade_phase_list is not None:
      _set = set(trade_phase_list)
      _list = list()
      # start to discover a head path with the trade_phase_list from head path(s) of whole
      for path in head_path_list:
        _list += self._getHeadPathValueList(path, _set)
      head_path_list = map(lambda t: t[0], filter(lambda t: t != (None, None), _list))

    return head_path_list

  def _LEGACY__getHeadPathValueList(self, path, trade_phase_set):
    # if the path has target trade_phase, it is a head path.
    _set = set(path.getTradePhaseList())
    if _set & trade_phase_set:
      return [(path, _set & trade_phase_set)]

    node = path.getSuccessorValue()
    if node is None:
      return [(None, None)]

    _list = list()
    for next_path in node.getPredecessorRelatedValueList():
      _list += self._getHeadPathValueList(next_path, trade_phase_set)
    return _list

  def _LEGACY__getExpectedCompletionDate(self, path, *args, **kwargs):
    return path.getExpectedStopDate(*args, **kwargs)


  # From Business Path
  def _LEGACY__getExplanationUidList(self, explanation):
    """
    Helper method to fetch really explanation related movements 
    """ # XXX-JPS this seems to be doing too much - why do you need many "explanations"
    explanation_uid_list = [explanation.getUid()]
    # XXX: getCausalityRelatedValueList is oversimplification, assumes
    #      that documents are sequenced like simulation movements, which
    #      is wrong
    if getattr(explanation, "getCausalityValueList", None) is None: 
      return explanation_uid_list
    for found_explanation in explanation.getCausalityRelatedValueList( # XXX-JPS this also seems exagerated, and breaking the APIs
        portal_type=self.getPortalDeliveryTypeList()) + \
        explanation.getCausalityValueList(): # Wrong if an item
      explanation_uid_list.extend(self._getExplanationUidList(
        found_explanation))
    return explanation_uid_list