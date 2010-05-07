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

import zope.interface

class BusinessProcess(Path, XMLObject):
  """
    The BusinessProcess class is a container class which is used
    to describe business processes in the area of trade, payroll
    and production.

    TODO:
      - finish interface implementation
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

  # Access to path and states of the business process
  security.declareProtected(Permissions.AccessContentsInformation, 'getPathValueList')
  def getPathValueList(self, trade_phase=None, context=None, **kw):
    """
      Returns all Path of the current BusinessProcess which
      are matching the given trade_phase and the optional context.

      trade_phase -- a single trade phase category or a list of
                      trade phases

      context -- the context to search matching predicates for

      **kw -- same parameters as for searchValues / contentValues
    """
    if trade_phase is None:
      trade_phase = set()
    elif not isinstance(trade_phase, (list, tuple)):
      trade_phase = set((trade_phase,))
    else:
      trade_phase = set(trade_phase)
    result = []
    if len(trade_phase) == 0:
      return result
    # Separate the selection of business paths into twp steps
    # for easier debugging.
    # First, collect business paths which can be applicable to a given context.
    business_path_list = []
    for business_path in self.objectValues(portal_type='Business Path',
                                           sort_on='int_index'):
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

  security.declareProtected(Permissions.AccessContentsInformation, 'getStateValueList')
  def getStateValueList(self, *args, **kw):
    """
      Returns all states of the business process. The method
      **kw parameters follows the API of searchValues / contentValues
    """
    # Naive implementation to redo XXX
    kw['portal_type'] = "Business Path"
    return [x for x in [y.getSuccessorValue() for y in \
            self.contentValues(*args, **kw)] if x is not None]

  # Access to path and states of the business process
  def isCompleted(self, explanation):
    """
      True if all states are completed
    """
    for state in self.getStateValueList():
      if not state.isCompleted(explanation):
        return False
    return True
  
  def isBuildable(self, explanation):
    """
      True if all any path is buildable
    """
    return len(self.getBuildablePathValueList(explanation)) != 0

  def getBuildablePathValueList(self, explanation):
    """
      Returns the list of Business Path which are ready to 
      be built
    """
    return filter(lambda x:x.isBuildable(explanation),
                  self.objectValues(portal_type='Business Path'))

  def getCompletedStateValueList(self, explanation):
    """
      Returns the list of Business States which are finished
    """
    return filter(lambda x:x.isCompleted(explanation), self.getStateValueList())

  def getPartiallyCompletedStateValueList(self, explanation):
    """
      Returns the list of Business States which are finished
    """
    return filter(lambda x:x.isPartiallyCompleted(explanation), self.getStateValueList())

  def getLatestCompletedStateValue(self, explanation):
    """
      Returns the most advanced completed state
    """
    for state in self.getCompletedStateValueList(explanation):
      for path in state.getPredecessorRelatedValueList():
        if not path.isCompleted(explanation):
          return state
    return None

  def getLatestPartiallyCompletedStateValue(self, explanation):
    """
      Returns the most advanced completed state
    """
    for state in self.getCompletedStateValueList(explanation):
      for path in state.getPredecessorRelatedValueList():
        if not path.isPartiallyCompleted(explanation):
          return state
    return None

  def getLatestCompletedStateValueList(self, explanation):
    """
      Returns the most advanced completed state
    """
    result = []
    for state in self.getCompletedStateValueList(explanation):
      for path in state.getPredecessorRelatedValueList():
        if not path.isCompleted(explanation):
          result.append(state)
    return result

  def getLatestPartiallyCompletedStateValueList(self, explanation):
    """
      Returns the most advanced completed state
    """
    result = []
    for state in self.getCompletedStateValueList(explanation):
      for path in state.getPredecessorRelatedValueList():
        if not path.isPartiallyCompleted(explanation):
          result.append(state)
    return result

  def build(self, explanation_relative_url):
    """
      Build whatever is buildable
    """
    explanation = self.restrictedTraverse(explanation_relative_url)
    for path in self.getBuildablePathValueList(explanation):
      path.build(explanation)

  def isStartDateReferential(self): # XXX - not in interface
    return self.getReferentialDate() == 'start_date'

  def isStopDateReferential(self): # XXX - not in interface
    return self.getReferentialDate() == 'stop_date'

  def getTradePhaseList(self):
    """
      Returns all trade_phase of this business process
    """
    path_list = self.objectValues(portal_type=self.getPortalBusinessPathTypeList())
    return filter(None, [path.getTradePhase()
                         for path in path_list])

  def getRootExplanationPathValue(self):
    """
      Returns a root path of this business process
    """
    path_list = self.objectValues(portal_type=self.getPortalBusinessPathTypeList())
    path_list = filter(lambda x: x.isDeliverable(), path_list)
    
    if len(path_list) > 1:
      raise Exception, "this business process has multi root paths"

    if len(path_list) == 1:
      return path_list[0]

  def getHeadPathValueList(self, trade_phase_list=None):
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

  def _getHeadPathValueList(self, path, trade_phase_set):
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

  def getRemainingTradePhaseList(self, explanation, trade_state, trade_phase_list=None):
    """
      Returns the list of remaining trade phase for this
      state based on the explanation.

      trade_phase_list -- if provide, the result is filtered by it after collected
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

  def isStatePartiallyCompleted(self, explanation, trade_state):
    """
      If all path which reach this state are partially completed
      then this state is completed
    """
    for path in [x for x in self.objectValues(portal_type="Business Path") \
        if x.getSuccessorValue() == trade_state]:
      if not path.isPartiallyCompleted(explanation):
        return False
    return True

  def getExpectedStateCompletionDate(self, explanation, trade_state, *args, **kwargs):
    """
      Returns the expected completion date for this
      state based on the explanation.

      explanation -- the document
    """
    # Should be re-calculated?
    # XXX : what is the purpose of the two following lines ? comment it until there is
    # good answer
    if 'predecessor_date' in kwargs:
      del kwargs['predecessor_date']
    successor_list = [x for x in self.objectValues(portal_type="Business Path") \
        if x.getSuccessorValue() == trade_state]
    date_list = self._getExpectedDateList(explanation,
                                          successor_list,
                                          self._getExpectedCompletionDate,
                                          *args,
                                          **kwargs)
    if len(date_list) > 0:
      return min(date_list)

  def getExpectedStateBeginningDate(self, explanation, trade_state, *args, **kwargs):
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

  def _getExpectedBeginningDate(self, path, *args, **kwargs):
    expected_date = path.getExpectedStartDate(*args, **kwargs)
    if expected_date is not None:
      return expected_date - path.getWaitTime()

  def _getExpectedDateList(self, explanation, path_list, path_method,
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

  def _getExpectedCompletionDate(self, path, *args, **kwargs):
    return path.getExpectedStopDate(*args, **kwargs)

