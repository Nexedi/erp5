# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
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
"""
Products.ERP5.interfaces.business_process
"""

from zope.interface import Interface

class ITradeModelPathProcess(Interface):
  """Trade Model Path Process interface specification

  ITradeModelPathProcess defines Business Process APIs related
  to Trade Model Path access and to the evaluation of start_date,
  stop date, quantity shares and arrows of an Amount.
  """

  def getTradeModelPathValueList(trade_phase=None, context=None, **kw):
    """Returns all Trade Model Path of the current Business Process which
    are matching the given trade_phase and the optional context.

    trade_phase -- filter by trade phase

    context -- a context to test each Business Link on
               and filter out Business Link which do not match

    **kw -- same arguments as those passed to searchValues / contentValues
    """

  def getExpectedTradeModelPathStartAndStopDate(explanation, trade_model_path,
                                                delay_mode=None):
    """Returns the expected start and stop dates of given Trade Model Path
    document in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_model_path -- a Trade Model Path document

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay
    """

class IBusinessLinkProcess(Interface):
  """Business Link Process interface specification

  IBusinessLinkProcess defines Business Process APIs related
  to Business Link completion status and expected completion dates.

  IMPORTANT:
  - explanation implicitely defines a subtree of the simulation
    Order, Order Line, Delivery or Delivery Line are simple cases
    which consider all children of delivery related movements
    + all parent simulation movement
    Applied rule is another form of explanation, which defines
    implicitely all children + all parent simulation movements
     

  TODO:
  - find a way in getTradePhaseMovementList to narrow down
    parameters to be copied (this used to be done through rule 
    parameter in provivate method)
  - Is there a reason why trade_phase should be a list in
    getBusinessLinkValueList ? (for rules ?)
  """

  def getBusinessLinkValueList(trade_phase=None, context=None,
                               predecessor=None, successor=None, **kw):
    """Returns all Business Links of the current BusinessProcess which
    are matching the given trade_phase and the optional context.

    trade_phase -- filter by trade phase

    context -- a context to test each Business Link on
               and filter out Business Link which do not match

    predecessor -- filter by trade state predecessor

    successor -- filter by trade state successor

    **kw -- same arguments as those passed to searchValues / contentValues
    """

  def isBusinessLinkCompleted(explanation, business_link):
    """Returns True if given Business Link document
    is completed in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """

  def isBusinessLinkPartiallyCompleted(explanation, business_link):
    """Returns True if given Business Link document
    is partially completed in the context of provided explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """

class IBuildableBusinessLinkProcess(Interface):
  """Buildable Business Link Process interface specification

  IBuildableBusinessLinkProcess defines an API to build
  simulation movements related to business link in the context
  of a given explanation.
  """

  def getBuildableBusinessLinkValueList(explanation):
    """Returns the list of Business Link which are buildable
    by taking into account trade state dependencies between
    Business Link.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def getPartiallyBuildableBusinessLinkValueList(explanation):
    """Returns the list of Business Link which are partially buildable
    by taking into account trade state dependencies between
    Business Link.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def isBusinessLinkBuildable(explanation, business_link):
    """Returns True if any of the related Simulation Movement
    is buildable and if the predecessor trade state is completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """

  def isBusinessPatPartiallyBuildable(explanation, business_link):
    """Returns True if any of the related Simulation Movement
    is buildable and if the predecessor trade state is partially completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """

  def isBuildable(explanation):
    """Returns True is this business process has at least one
    Business Link which is buildable
    """

  def isPartiallyBuildable(explanation):
    """Returns True is this business process has at least one
    Business Link which is partially buildable
    """

class ITradeStateProcess(Interface):
  """Trade State Process interface specification

  ITradeStateProcess defines Business Process APIs related
  to Trade State completion status and expected completion dates.
  ITradeStateProcess APIs recursively browse trade states and business
  links to provide completion status and expected completion dates.

  For example, a complete trade state is a trade state for
  which all predecessor trade states are completed and for
  which all business links applicable to the given explanation
  are also completed.
  """

  def getTradeStateList():
    """Returns list of all trade_state of this Business Process
    by looking at successor and predecessor values of contained
    Business Link.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def isInitialTradeState(trade_state):
    """Returns True if given 'trade_state' has no successor related
    Business Link.

    trade_state -- a Trade State category
    """

  def isFinalTradeState(trade_state):
    """Returns True if given 'trade_state' has no predecessor related
    Business Link.

    trade_state -- a Trade State category
    """

  def getSuccessorTradeStateList(explanation, trade_state):
    """Returns the list of successor states in the 
    context of given explanation. This list is built by looking
    at all successor of business link involved in given explanation
    and which predecessor is the given trade_phase.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """

  def getPredecessorTradeStateList(explanation, trade_state):
    """Returns the list of predecessor states in the 
    context of given explanation. This list is built by looking
    at all predecessor of business link involved in given explanation
    and which sucessor is the given trade_phase.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """

  def getCompletedTradeStateList(explanation):
    """Returns the list of Trade States which are completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def getPartiallyCompletedTradeStateList(explanation):
    """Returns the list of Trade States which are partially 
    completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def getLatestCompletedTradeStateList(explanation):
    """Returns the list of completed trade states which predecessor
    states are completed and for which no successor state 
    is completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def getLatestPartiallyCompletedTradeStateList(explanation):
    """Returns the list of completed trade states which predecessor
    states are completed and for which no successor state 
    is partially completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def isTradeStateCompleted(explanation, trade_state):
    """Returns True if all predecessor trade states are
    completed and if no successor trade state is completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """

  def isTradeStatePartiallyCompleted(explanation, trade_state):
    """Returns True if all predecessor trade states are
    completed and if no successor trade state is partially completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_state -- a Trade State category
    """

class ITradePhaseProcess(Interface):
  """Trade Phase Process interface specification

  ITradePhaseProcess defines Business Process APIs related
  to Trade Phase completion status and expected completion dates.
  Unlike ITradeStateProcess, ITradePhaseProcess APIs related to completion
  do not take into account relations between trade states and
  business link.

  For example, a completed trade phase is a trade phase for which all
  business link applicable to the given explanation are completed. 
  It does not matter whether the predecessor trade state of related
  business link is completed or not.
  """

  def getTradePhaseList():
    """Returns list of all trade_phase of this Business Process
    by looking at trade_phase values of contained Business Link.
    """

  def getCompletedTradePhaseList(explanation):
    """Returns the list of Trade Phases which are completed
    in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def getPartiallyCompletedTradePhaseList(explanation):
    """Returns the list of Trade Phases which are partially completed
    in the context of given explanation. 

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def isTradePhaseCompleted(explanation, trade_phase):
    """Returns True if all business link with given trade_phase
    applicable to given explanation are completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_phase -- a Trade Phase category
    """

  def isTradePhasePartiallyCompleted(explanation, trade_phase):
    """Returns True at least one business link with given trade_phase
    applicable to given explanation is partially completed
    or completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_phase -- a Trade Phase category
    """

  def getRemainingTradePhaseList(business_link):
    """Returns the list of remaining trade phases which to be achieved
    as part of a business process. This list is calculated by analysing 
    the graph of business link and trade states, starting from a given
    business link. The result if filtered by a list of trade phases. This
    method is useful mostly for production and MRP to manage a distributed
    supply and production chain.

    business_link -- a Business Link document

    NOTE: explanation is not involved here because we consider here that
    self is the result of asUnionBusinessProcess and thus only contains
    applicable Business Link to a given simulation subtree. Since the list
    of remaining trade phases does not depend on exact values in the
    simulation, we did not include the explanation. However, this makes the
    API less uniform.
    """

  def getTradePhaseMovementList(explanation, amount, trade_phase=None, delay_mode=None):
    """Returns a list of movement with appropriate arrow and dates,
    based on the Business Link definitions, provided 'amount' and optional
    trade phases. If no trade_phase is provided, the trade_phase defined
    on the Amount is used instead.
    
    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    amount -- Amount (quantity, resource)

    trade_phase -- optional Trade Phase category

    delay_mode -- optional value to specify calculation mode ('min', 'max')
                  if no value specified use average delay
    """

class ISimulationMovementProcess(Interface):
  """Simulation Movemnt Process interface specification

  ISimulationMovementProcess provides help methods to 
  access simulation movements of an explanation and
  gather statistics about them. It is useful to find
  out min dates or max dates related to a business link,
  to a trade phase, to a trade model path, to a 
  trade_model_line, etc.
  """

  def getSimulationMovementList(explanation, trade_phase=None,
     business_link=None, trade_model_path=None, trade_model_line=None, **kw):

    """Returns a list of movement part of the simulation subtrees
    defined by explanation and which match provided parameters. This
    method can be useful for example to list all simulation movements
    related to a phase such as payment, and inspect them.
    
    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_phase -- optional Trade Phase category

    business_link -- optional Business Link document

    trade_model_path -- optional Trade Model Path document

    trade_model_line --optional Trade Model Line document

    **kw -- other optional parameters which are passed to Catalog API
    """

  def getSimulationMovementStat(explanation, trade_phase=None,
     business_link=None, trade_model_path=None, trade_model_line=None, **kw):

    """Returns statistics for movements part of the simulation subtrees
    defined by explanation and which match provided parameters. This
    method can be useful for example to find the max date of simulation movements
    related to a phase such as payment.
    
    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    trade_phase -- optional Trade Phase category

    business_link -- optional Business Link document

    trade_model_path -- optional Trade Model Path document

    trade_model_line --optional Trade Model Line document

    **kw -- other optional parameters which are passed to Catalog API
    """

class IBusinessProcess(ITradeModelPathProcess, IBusinessLinkProcess, IBuildableBusinessLinkProcess,
                       ITradeStateProcess, ITradePhaseProcess, ISimulationMovementProcess):
  """Business Process interface specification.

  Business Process APIs are used to manage the completion status,
  the completion dates, the start date and stop date, and trigger 
  build process of a complex simulation process in ERP5.
  """

  def isCompleted(explanation):
    """Returns True is all applicable Trade States and Trade Phases
    are completed in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def isBuildable(explanation):
    """Returns True is one Business Link of this Business Process
    is buildable in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def isPartiallyBuildable(explanation):
    """Returns True is one Business Link of this Business Process
    is partially buildable in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def build(explanation, include_partially_buildable=False):
    """Build whatever is buildable in the context of given explanation.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    include_partially_buildable -- if set to True, also build partially
                                   buildable business link. Else
                                   only build strictly buildable link.
    """
