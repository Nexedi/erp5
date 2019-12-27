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

from collections import defaultdict
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Path import Path
from Products.ERP5.ExplanationCache import _getExplanationCache, _getBusinessLinkClosure
from Products.ERP5.MovementCollectionDiff import _getPropertyAndCategoryList

import zope.interface

_marker = object()

class BusinessProcess(Path, XMLObject):
  """The BusinessProcess class is a container class which is used
  to describe business processes in the area of trade, payroll
  and production. Processes consists of a collection of Business Link
  which define an arrow between a 'predecessor' trade_state and a
  'successor' trade_state, for a given trade_phase_list.

  Core concepts in BusinessProcess are the notions of "explanation".
  Explanation represents the subtree of a simulation tree of all
  simulation movements related to an applied rule, a delivery line,
  a delivery, etc.

  Example:
    portal_simulation/2/sm1/a1/sm2/a2/sm3
    portal_simulation/2/sm1/a1/sm2/a2/sm4

    explanation(portal_simulation/2/sm1/a1/sm2/a2) is
      portal_simulation/2/sm1/a1/sm2/a2/sm3
      portal_simulation/2/sm1/a1/sm2/a2/sm4
      portal_simulation/2/sm1/a1/sm2
      portal_simulation/2/sm1

  Business Process completion, dates, etc. are calculated
  always in the context of an explanation. Sometimes,
  it is necessary to ignore certain business link to evaluate
  completion or completion dates. This is very true for Union
  Business Processes. This is the concept of Business Link closure,
  ie. filtering out all Business Link which are not used in an explanation.

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
  - fine a better way to narrow down paremeters to copy without
    using a rule parameter
  - should _getPropertyAndCategoryList remain a private method or
    become part of IMovement ?
  - add security declarations
  - why are we using objectValues in some places ?
  - add a property to rules in order to determine whether dates
    are provided by the rule or by business link / trade model path. This is an extension
    of the idea that root applied rules provide date information.
  - use explanation cache more to optimize speed
  - DateTime must be extended in ERP5 to support  +infinite and -infinite
    like floating points do
  - support conversions in trade model path

  RENAMED:
    getPathValueList -> getBusinessLinkValueList
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

  # ITradeModelPathProcess implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'getTradeModelPathValueList')
  def getTradeModelPathValueList(self, trade_phase=None, context=None, **kw):
    """Returns all Trade Model Path of the current Business Process which
    are matching the given trade_phase and the optional context.

    trade_phase -- filter by trade phase

    context -- a context to test each Business Link on
               and filter out Business Link which do not match

    **kw -- same arguments as those passed to searchValues / contentValues
    """
    if trade_phase is not None:
      if isinstance(trade_phase, basestring):
        trade_phase = (trade_phase,)
      trade_phase = {x.split('trade_phase/', 1)[-1] for x in trade_phase}
    kw.setdefault('portal_type', self.getPortalTradeModelPathTypeList())
    kw.setdefault('sort_on', 'int_index')
    original_path_list = self.objectValues(**kw) # Why Object Values ??? XXX-JPS
    # Separate the selection of trade model paths into two steps
    # for easier debugging.
    # First, collect trade model paths which can be applicable to a given context.
    path_list = []
    for path in original_path_list:
      # Filter our business path which trade phase does not match
      if trade_phase is None or trade_phase.intersection(path.getTradePhaseList()):
        path_list.append(path)
    # Then, filter trade model paths by Predicate API.
    # FIXME: Ideally, we should use the Domain Tool to search business paths,
    # and avoid using the low level Predicate API. But the Domain Tool does
    # support the condition above without scripting?
    return [path for path in path_list if path.test(context)]

  security.declareProtected(Permissions.AccessContentsInformation, 'getExpectedTradeModelPathStartAndStopDate')
  def getExpectedTradeModelPathStartAndStopDate(self, explanation, trade_model_path,
                                                      delay_mode=None):
    """Returns the expected start and stop dates of given Trade Model Path
    document in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_model_path -- a Trade Model Path document

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay
    """
    if explanation.getParentValue().getPortalType() == 'Simulation Tool':
      raise ValueError('explanation must not be a Root Applied Rule')

    trade_date = trade_model_path.getTradeDate()
    assert trade_date, 'a trade_date must be defined on the Trade Model Path'

    reference_date_method_id = trade_model_path.getReferenceDateMethodId()
    if not reference_date_method_id:
      raise ValueError('a reference date method must be defined on every Trade Model Path')

    explanation_cache = _getExplanationCache(explanation)
    reference_date = explanation_cache.getReferenceDate(self, trade_date, reference_date_method_id)

    # Computer start_date and stop_date (XXX-JPS this could be cached and accelerated)
    start_date = reference_date + trade_model_path.getPaymentTerm(0.0) # XXX-JPS Until better naming
    if delay_mode == 'min':
      delay = trade_model_path.getMinDelay(0.0)
    elif delay_mode == 'max':
      delay = trade_model_path.getMaxDelay(0.0)
    else:
      delay = (trade_model_path.getMaxDelay(0.0) + trade_model_path.getMinDelay(0.0)) / 2.0
    stop_date = start_date + delay

    return start_date, stop_date

  # IBusinessLinkProcess implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'getBusinessLinkValueList')
  def getBusinessLinkValueList(self, trade_phase=None, context=None,
                               predecessor=_marker, successor=_marker, **kw):
    """Returns all Business Links of the current BusinessProcess which
    are matching the given trade_phase and the optional context.

    trade_phase -- filter by trade phase

    context -- a context to test each Business Link on
               and filter out Business Link which do not match

    predecessor -- filter by trade state predecessor

    successor -- filter by trade state successor

    **kw -- same arguments as those passed to searchValues / contentValues
    """
    if trade_phase is not None:
      if isinstance(trade_phase, basestring):
        trade_phase = frozenset((trade_phase,))
      else:
        trade_phase = frozenset(trade_phase)
    kw.setdefault('portal_type', self.getPortalBusinessLinkTypeList())
    kw.setdefault('sort_on', 'int_index')
    original_business_link_list = self.objectValues(**kw) # Why Object Values ??? XXX-JPS
    # Separate the selection of business links into two steps
    # for easier debugging.
    # First, collect business links which can be applicable to a given context.
    business_link_list = []
    for business_link in original_business_link_list:
      if (predecessor is not _marker and
          business_link.getPredecessor() != predecessor):
        continue # Filter our business link which predecessor does not match
      if (successor is not _marker and
          business_link.getSuccessor() != successor):
        continue # Filter our business link which successor does not match
      if trade_phase is not None and trade_phase.isdisjoint(
                                   business_link.getTradePhaseList()):
        continue # Filter our business link which trade phase does not match
      business_link_list.append(business_link)
    # Then, filter business links by Predicate API.
    # FIXME: Ideally, we should use the Domain Tool to search business links,
    # and avoid using the low level Predicate API. But the Domain Tool does
    # support the condition above without scripting?
    if context is None:
      return business_link_list
    return [business_link for business_link in business_link_list
                if business_link.test(context)]

  security.declareProtected(Permissions.AccessContentsInformation, 'isBusinessLinkCompleted')
  def isBusinessLinkCompleted(self, explanation, business_link):
    """Returns True if given Business Link document
    is completed in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """
    # Return False if Business Link is not completed
    if not business_link.isCompleted(explanation):
      return False
    predecessor_state = business_link.getPredecessor()
    if not predecessor_state:
      # This is a root business links, no predecessor
      # so no need to do any recursion
      return True
    if self.isTradeStateCompleted(explanation, predecessor_state):
      # If predecessor state is globally completed for the
      # given explanation, return True
      # Please note that this is a specific case for a Business Process
      # built using asUnionBusinessProcess. In such business process
      # a business link may be completed even if its predecessor state
      # is not
      return True
    # Build the closure business process which only includes those business
    # links wich are directly related to the current business link but DO NOT
    # narrow down the explanation else we might narrow down so much that
    # it becomes an empty set
    closure_process = _getBusinessLinkClosure(self, explanation, business_link)
    return closure_process.isTradeStateCompleted(explanation, predecessor_state)

  security.declareProtected(Permissions.AccessContentsInformation, 'isBusinessLinkPartiallyCompleted')
  def isBusinessLinkPartiallyCompleted(self, explanation, business_link):
    """Returns True if given Business Link document
    is partially completed in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """
    # Return False if Business Link is not partially completed
    if not business_link.isPartiallyCompleted(explanation):
      return False
    predecessor_state = business_link.getPredecessor()
    if not predecessor_state:
      # This is a root business link, no predecessor
      # so no need to do any recursion
      return True
    if self.isTradeStatePartiallyCompleted(explanation, predecessor_state):
      # If predecessor state is globally partially completed for the
      # given explanation, return True
      # Please note that this is a specific case for a Business Process
      # built using asUnionBusinessProcess. In such business process
      # a business link may be partially completed even if its predecessor
      # state is not
      return True
    # Build the closure business process which only includes those business
    # links wich are directly related to the current business link but DO NOT
    # narrow down the explanation else we might narrow down so much that
    # it becomes an empty set
    closure_process = _getBusinessLinkClosure(self, explanation, business_link)
    return closure_process.isTradeStatePartiallyCompleted(explanation,
                                                           predecessor_state)

  # IBuildableBusinessLinkProcess implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'getBuildableBusinessLinkValueList')
  def getBuildableBusinessLinkValueList(self, explanation):
    """Returns the list of Business Link which are buildable
    by taking into account trade state dependencies between
    Business Link.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    result = []
    for business_link in self.getBusinessLinkValueList():
      if self.isBusinessLinkBuildable(explanation, business_link):
        result.append(business_link)
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getPartiallyBuildableBusinessLinkValueList')
  def getPartiallyBuildableBusinessLinkValueList(self, explanation):
    """Returns the list of Business Link which are partially buildable
    by taking into account trade state dependencies between
    Business Link.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    result = []
    for business_link in self.getBusinessLinkValueList():
      if self.isBusinessLinkPartiallyBuildable(explanation, business_link):
        result.append(business_link)
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'isBusinessLinkBuildable')
  def isBusinessLinkBuildable(self, explanation, business_link):
    """Returns True if any of the related Simulation Movement
    is buildable and if the predecessor trade state is completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """
    # If everything is delivered, no need to build
    if business_link.isDelivered(explanation):
      return False
    # We must take the closure cause only way to combine business process
    closure_process = _getBusinessLinkClosure(self, explanation, business_link)
    predecessor = business_link.getPredecessor()
    return closure_process.isTradeStateCompleted(explanation, predecessor)

  security.declareProtected(Permissions.AccessContentsInformation, 'isBusinessLinkPartiallyBuildable')
  def isBusinessLinkPartiallyBuildable(self, explanation, business_link):
    """Returns True if any of the related Simulation Movement
    is buildable and if the predecessor trade state is partially completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """
    # If everything is delivered, no need to build
    if business_link.isDelivered(explanation):
      return False
    # We must take the closure cause only way to combine business process
    closure_process = _getBusinessLinkClosure(self, explanation, business_link)
    predecessor = business_link.getPredecessor()
    return closure_process.isTradeStatePartiallyCompleted(predecessor)

  # ITradeStateProcess implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'getTradeStateList')
  def getTradeStateList(self):
    """Returns list of all trade_state of this Business Process
    by looking at successor and predecessor values of contained
    Business Link.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    result = set()
    for business_link in self.getBusinessLinkValueList():
      result.add(business_link.getPredecessor())
      result.add(business_link.getSuccessor())
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'isInitialTradeState')
  def isInitialTradeState(self, trade_state):
    """Returns True if given 'trade_state' has no successor related
    Business Link.

    trade_state -- a Trade State category
    """
    return not self.getBusinessLinkValueList(successor=trade_state)

  security.declareProtected(Permissions.AccessContentsInformation, 'isFinalTradeState')
  def isFinalTradeState(self, trade_state):
    """Returns True if given 'trade_state' has no predecessor related
    Business Link.

    trade_state -- a Trade State category
    """
    return not self.getBusinessLinkValueList(predecessor=trade_state)

  security.declareProtected(Permissions.AccessContentsInformation, 'getSuccessorTradeStateList')
  def getSuccessorTradeStateList(self, explanation, trade_state):
    """Returns the list of successor states in the
    context of given explanation. This list is built by looking
    at all successor of business link involved in given explanation
    and which predecessor is the given trade_phase.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """
    result = set()
    for business_link in self.getBusinessLinkValueList():
      if business_link.getPredecessor() == trade_state:
        result.add(business_link.getSuccessor())
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getPredecessorTradeStateList')
  def getPredecessorTradeStateList(self, explanation, trade_state):
    """Returns the list of predecessor states in the
    context of given explanation. This list is built by looking
    at all predecessor of business link involved in given explanation
    and which sucessor is the given trade_phase.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """
    result = set()
    for business_link in self.getBusinessLinkValueList():
      if business_link.getSuccessor() == trade_state:
        result.add(business_link.getPredecessor())
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getCompletedTradeStateList')
  def getCompletedTradeStateList(self, explanation):
    """Returns the list of Trade States which are completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    return filter(lambda x:self.isTradeStateCompleted(explanation, x), self.getTradeStateList())

  security.declareProtected(Permissions.AccessContentsInformation, 'getPartiallyCompletedTradeStateList')
  def getPartiallyCompletedTradeStateList(self, explanation):
    """Returns the list of Trade States which are partially
    completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    return filter(lambda x:self.isTradeStatePartiallyCompleted(explanation, x), self.getTradeStateList())

  security.declareProtected(Permissions.AccessContentsInformation, 'getLatestCompletedTradeStateList')
  def getLatestCompletedTradeStateList(self, explanation):
    """Returns the list of completed trade states which predecessor
    states are completed and for which no successor state
    is completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    result = set()
    for state in self.getCompletedTradeStateList(explanation):
      for business_link in state.getPredecessorRelatedValueList():
        if not self.isBusinessLinkCompleted(explanation, business_link):
          result.add(state)
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getLatestPartiallyCompletedTradeStateList')
  def getLatestPartiallyCompletedTradeStateList(self, explanation):
    """Returns the list of completed trade states which predecessor
    states are completed and for which no successor state
    is partially completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    result = set()
    for state in self.getCompletedTradeStateList(explanation):
      for business_link in state.getPredecessorRelatedValueList():
        if not self.isBusinessLinkPartiallyCompleted(explanation, business_link):
          result.add(state)
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'isTradeStateCompleted')
  def isTradeStateCompleted(self, explanation, trade_state):
    """Returns True if all predecessor trade states are
    completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """
    for business_link in self.getBusinessLinkValueList(successor=trade_state):
      if not self.isBusinessLinkCompleted(explanation, business_link):
        return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation, 'isTradeStatePartiallyCompleted')
  def isTradeStatePartiallyCompleted(self, explanation, trade_state):
    """Returns True if all predecessor trade states are
    completed and if no successor trade state is partially completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """
    for business_link in self.getBusinessLinkValueList(successor=trade_state):
      if not self.isBusinessLinkPartiallyCompleted(explanation, business_link):
        return False
    return True

  # ITradePhaseProcess implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'getTradePhaseList')
  def getTradePhaseList(self):
    """Returns list of all trade_phase of this Business Process
    by looking at trade_phase values of contained Business Link.
    """
    result = set()
    for business_link in self.getBusinessLinkValueList():
      result = result.union(business_link.getTradePhaseList())
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getCompletedTradePhaseList')
  def getCompletedTradePhaseList(self, explanation):
    """Returns the list of Trade Phases which are completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    return filter(lambda x:self.isTradePhaseCompleted(explanation, x), self.getTradePhaseList())

  security.declareProtected(Permissions.AccessContentsInformation, 'getPartiallyCompletedTradePhaseList')
  def getPartiallyCompletedTradePhaseList(self, explanation):
    """Returns the list of Trade Phases which are partially completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    return filter(lambda x:self.isTradePhasePartiallyCompleted(explanation, x), self.getTradePhaseList())

  security.declareProtected(Permissions.AccessContentsInformation, 'isTradePhaseCompleted')
  def isTradePhaseCompleted(self, explanation, trade_phase):
    """Returns True all business link with given trade_phase
    applicable to given explanation are completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_phase -- a Trade Phase category
    """
    for business_link in self.getBusinessLinkValueList(trade_phase=trade_phase):
      if not self.isBusinessLinkCompleted(explanation, business_link):
        return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation, 'isTradePhasePartiallyCompleted')
  def isTradePhasePartiallyCompleted(self, explanation, trade_phase):
    """Returns True at least one business link with given trade_phase
    applicable to given explanation is partially completed
    or completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_phase -- a Trade Phase category
    """
    for business_link in self.getBusinessLinkValueList(trade_phase=trade_phase):
      if not self.isBusinessLinkPartiallyCompleted(explanation, business_link):
        return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRemainingTradePhaseList')
  def getRemainingTradePhaseList(self, business_link):
    """Returns the list of remaining trade phases which to be achieved
    as part of a business process. This list is calculated by analysing
    the graph of business link and trade states, starting from a given
    business link. The result if filtered by a list of trade phases. This
    method is useful mostly for production and MRP to manage a distributed
    supply and production chain.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document

    NOTE: explanation is not involved here because we consider here that
    self is the result of asUnionBusinessProcess and thus only contains
    applicable Business Link to a given simulation subtree. Since the list
    of remaining trade phases does not depend on exact values in the
    simulation, we did not include the explanation. However, this makes the
    API less uniform.
    """
    remaining_trade_phase_list = []
    trade_state = business_link.getSuccessor()
    tv = getTransactionalVariable()
    # We might need a key which depends on the explanation
    key = 'BusinessProcess_predecessor_successor_%s' % self.getRelativeUrl()
    predecessor_successor_dict = tv.get(key, None)
    if predecessor_successor_dict is None:
      predecessor_successor_dict = {'predecessor':{},
                                    'successor':{}}
      for business_link in self.objectValues(portal_type="Business Link"):
        for property_name in ('predecessor', 'successor'):
          property_value = business_link.getProperty(property_name)
          if property_value:
            business_link_list = predecessor_successor_dict[property_name].\
                setdefault(property_value, [])
            business_link_list.append(business_link)
      tv[key] = predecessor_successor_dict

    business_link_list = predecessor_successor_dict['predecessor'].\
                           get(trade_state, [])
    assert len(business_link_list) <= 1, \
        "code is not able yet to manage this case"
    for link in business_link_list:
      remaining_trade_phase_list += link.getTradePhaseValueList()

      # collect to successor direction recursively
      state = link.getSuccessor()
      if state is not None:
        next_business_link_list = predecessor_successor_dict['successor'].\
                                    get(state, [])
        assert len(next_business_link_list) == 1, \
            "code is not able yet to manage this case"
        remaining_trade_phase_list.extend(
          self.getRemainingTradePhaseList(
          next_business_link_list[0]))

    return remaining_trade_phase_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getTradePhaseMovementList')
  def getTradePhaseMovementList(self, explanation, amount, trade_phase=None, delay_mode=None,
                                      update_property_dict=None):
    """Returns a list of movement with appropriate arrow and dates,
    based on the Business Link definitions, provided 'amount' and optional
    trade phases. If no trade_phase is provided, the trade_phase defined
    on the Amount is used instead.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    amount -- IAmount (quantity, resource) or IMovement

    trade_phase -- optional Trade Phase category

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay

    update_property_method --
    """
    if not trade_phase:
      trade_phase = amount.getTradePhaseList()
      if not trade_phase:
        raise ValueError("%s: a trade_phase must be defined on the " \
                         "Amount or provided to getTradePhaseMovementList" %
                          amount.getRelativeUrl())
    elif isinstance(trade_phase, basestring):
      trade_phase = trade_phase,

    # Build a list of temp movements
    newTempSimulationMovement = self.getPortalObject().portal_trash.newContent
    result = []
    id_index = 0
    base_id = amount.getId()
    if update_property_dict is None: update_property_dict = {}
    filter_trade_phase = frozenset(trade_phase).intersection
    for trade_model_path in self.getTradeModelPathValueList(context=amount, trade_phase=trade_phase):
      id_index += 1
      movement = newTempSimulationMovement(temp_object=True, portal_type='Simulation Movement',
        id='%s_%s' % (base_id, id_index), notify_workflow=False)
      kw = self._getPropertyAndCategoryDict(explanation, amount, trade_model_path, delay_mode=delay_mode)
      trade_phase = filter_trade_phase(trade_model_path.getTradePhaseList())
      try:
        kw['trade_phase'], = trade_phase
      except ValueError:
        pass
      kw.update(update_property_dict)
      movement._edit(force_update=True, **kw)
      business_link = self.getBusinessLinkValueList(trade_phase=trade_phase,
                                                    context=movement)
      movement._setCausalityList([trade_model_path.getRelativeUrl()]
        + [x.getRelativeUrl() for x in business_link]
        + movement.getCausalityList())
      result.append(movement)

    if not explanation.getSpecialiseValue().getSameTotalQuantity():
      return result

    # result can not be empty
    if not result:
      raise ValueError("A Business Process can not erase amounts:"
                       " no Trade Model Path found for %r"
                       " (rule=%s, trade_phase=%r)"
                       % (amount, explanation.getSpecialise(), trade_phase))

    # Sort movement list and make sure the total is equal to total_quantity
    total_quantity = amount.getQuantity()
    current_quantity = 0
    result.sort(key=lambda x:x.getStartDate())
    stripped_result = []
    for movement in result:
      stripped_result.append(movement)
      quantity = movement.getQuantity()
      current_quantity += quantity
      if current_quantity > total_quantity:
        # As soon as the current_quantity is greater than total_quantity
        # strip the result
        break

    # Make sure total_quantity is reached by changing last movement valye
    if current_quantity != total_quantity:
      movement._setQuantity(quantity + total_quantity - current_quantity)

    return stripped_result

  def _getPropertyAndCategoryDict(self, explanation, amount, trade_model_path, delay_mode=None):
    """A private method to merge an amount and a business_link and return
    a dict of properties and categories which can be used to create a
    new movement.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    amount -- an IAmount instance or an IMovement instance

    trade_model_path -- an ITradeModelPath instance

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay
    """
    if explanation.getPortalType() == "Applied Rule":
      rule = explanation.getSpecialiseValue()
    else:
      rule = None
    if rule is None:
      property_dict = _getPropertyAndCategoryList(amount)
    else:
      property_dict = {}
      for tester in rule._getUpdatingTesterList():
        property_dict.update(tester.getUpdatablePropertyDict(
          amount, None))

    # Arrow categories
    property_dict.update(trade_model_path.getArrowCategoryDict(context=amount))

    # More categories
    for base_category in ('delivery_mode', 'incoterm', 'payment_mode', 'ledger'):
      value = trade_model_path.getPropertyList(base_category)
      if value:
        property_dict[base_category] = value

    # Amount quantities - XXX-JPS maybe we should consider handling unit conversions here
    # and specifying units
    if trade_model_path.getQuantity():
      property_dict['quantity'] = trade_model_path.getQuantity()
    elif trade_model_path.getEfficiency():
      property_dict['quantity'] = amount.getQuantity() *\
        trade_model_path.getEfficiency()
    else:
      property_dict['quantity'] = amount.getQuantity()

    # Dates - the main concept of BPM is to search for reference dates
    # in parent simulation movements at expand time. This means that
    # a trade date which is based on a trade phase which is handled
    # by a child applied rule is not supported in ERP5 BPM.
    # In the same spirit, date calculation at expand time is local, not
    # global.
    if explanation.getPortalType() == 'Applied Rule':
      if explanation.getParentValue().getPortalType() != "Simulation Tool":
        # It only makes sense to search for start and stop dates for
        # applied rules which are not root applied rules.
        # Date calculation by Business Process can be also disabled by
        # leaving 'trade_date' unset (XXX: a separate boolean property,
        # on the TMP or the rule, may be better).
        if trade_model_path.getTradeDate():
          property_dict['start_date'], property_dict['stop_date'] = \
            self.getExpectedTradeModelPathStartAndStopDate(
              explanation, trade_model_path, delay_mode=delay_mode)
    # Else, nothing to do. This method can be used without Applied Rule.
    return property_dict

  # IBusinessProcess global API
  security.declareProtected(Permissions.AccessContentsInformation, 'isCompleted')
  def isCompleted(self, explanation):
    """Returns True is all applicable Trade States and Trade Phases
    are completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    for state in self.getTradeStateList():
      if not self.isTradeStateCompleted(explanation, state):
        return False
    return True

  security.declareProtected(Permissions.AccessContentsInformation, 'isBuildable')
  def isBuildable(self, explanation):
    """Returns True is one Business Link of this Business Process
    is buildable in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    return not not self.getBuildableBusinessLinkValueList(explanation)

  security.declareProtected(Permissions.AccessContentsInformation, 'isPartiallyBuildable')
  def isPartiallyBuildable(self, explanation):
    """Returns True is one Business Link of this Business Process
    is partially buildable in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """
    return not not self.getPartiallyBuildableBusinessLinkValueList(explanation)

  security.declareProtected(Permissions.AccessContentsInformation, 'build')
  def build(self, explanation):
    """
      Build whatever is buildable
    """
    for business_link in self.getBuildableBusinessLinkValueList(explanation):
      business_link.build(explanation=explanation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPreviousTradePhaseDict')
  def getPreviousTradePhaseDict(self, trade_phase_list=None):
    """Return a dict mapping each phase to a set of previous ones

    If trade_phase_list is given, the return graph is reduced to only keep
    phases in this list.
    """
    state_dict = defaultdict(set)
    phase_list = []
    for link in self.getBusinessLinkValueList(sort_on=None):
      phase, = link.getTradePhaseList() # BL must have exactly 1 TP
      phase_list.append((phase, link.getPredecessor()))
      state_dict[link.getSuccessor()].add(phase)
    result = dict((phase, state_dict[state]) for phase, state in phase_list)
    if trade_phase_list: # reduce graph
      next_dict = defaultdict(set)
      # build {phase: next_set} (i.e. reverse result)
      for next_, phase_set in result.iteritems():
        for phase in phase_set:
          next_dict[phase].add(next_)
      # for each phase to remove
      for phase in set(result).difference(trade_phase_list):
        # edit the graph like we would do for a doubly linked list
        previous_set = result.pop(phase)
        next_set = next_dict[phase]
        # i.e. edit next phases to replace current phase by previous ones
        for next_ in next_set:
          phase_set = result[next_]
          # Not remove() as it may have already been removed earlier
          # if >1 elements of next_set have the same parent
          phase_set.discard(phase)
          phase_set |= previous_set
        # and previous phases to replace current by next ones
        for previous in previous_set:
          phase_set = next_dict[previous]
          # Not remove() as it may have already been removed earlier
          # if >1 elements of previous_set have the same child
          phase_set.discard(phase)
          phase_set |= next_set
    return result
