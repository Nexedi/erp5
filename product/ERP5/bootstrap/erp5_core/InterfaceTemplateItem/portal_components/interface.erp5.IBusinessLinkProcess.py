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
