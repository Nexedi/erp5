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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
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
  isPredicate = 1

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
  def getPathValueList(self, trade_phase, context=None, **kw):
    """
      Returns all Path of the current BusinessProcess which
      are matching the given trade_phase and the optional context.

      trade_phase -- a single trade phase category or a list of
                      trade phases

      context -- the context to search matching predicates for

      **kw -- same parameters as for searchValues / contentValues
    """
    # Naive implementation to redo XXX using contentValues
    if trade_phase is None:
      trade_phase=[]
    if not isinstance(trade_phase, (list, tuple)):
      trade_phase = (trade_phase,)
    result = []
    for document in self.contentValues(portal_type="Business Path"):
      for phase in trade_phase:
        if document.isMemberOf('trade_phase/' + phase): # XXX - not so good, use filter if possible
          result.append(document)
          break
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getStateValueList')
  def getStateValueList(self, *args, **kw):
    """
      Returns all states of the business process. The method
      **kw parameters follows the API of searchValues / contentValues
    """
    # Naive implementation to redo XXX
    kw['portal_type'] = "Business State"
    return self.contentValues(*args, **kw)

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
    return filter(lambda x:x.isBuildable(explanation), self.getPathValueList())

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
    for state in self.getCompletedStateValueList(explanation):
      for path in state.getPredecessorRelatedValueList():
        if not path.isCompleted(explanation):
          return state
    return None

  def getLatestPartiallyCompletedStateValue(self, explanation):
    for state in self.getCompletedStateValueList(explanation):
      for path in state.getPredecessorRelatedValueList():
        if not path.isPartiallyCompleted(explanation):
          return state
    return None

  def getLatestCompletedStateValueList(self, explanation):
    result = []
    for state in self.getCompletedStateValueList(explanation):
      for path in state.getPredecessorRelatedValueList():
        if not path.isCompleted(explanation):
          result.append(state)
    return result

  def getLatestPartiallyCompletedStateValueList(self, explanation):
    result = []
    for state in self.getCompletedStateValueList(explanation):
      for path in state.getPredecessorRelatedValueList():
        if not path.isPartiallyCompleted(explanation):
          result.append(state)
    return result

  def build(self, explanation):
    """
      Build whatever is buildable
    """
    for path in self.getBuildablePathValueList(explanation):
      path.build(explanation)

  def isStartDateReferential(self): # XXX - not in interface
    return self.getReferentialDate() == 'start_date'

  def isStopDateReferential(self): # XXX - not in interface
    return self.getReferentialDate() == 'stop_date'

  def getTradePhaseList(self):
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

      trade_phase_list -- used to filterring, means that discovering
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
