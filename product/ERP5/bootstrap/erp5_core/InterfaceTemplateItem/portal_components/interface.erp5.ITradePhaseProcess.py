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
