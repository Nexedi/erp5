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

from zope.interface import Interface

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
    completed and if the provided trade state is also completed
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
