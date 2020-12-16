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

from erp5.component.interface.ITradeModelPathProcess import ITradeModelPathProcess
from erp5.component.interface.IBusinessLinkProcess import IBusinessLinkProcess
from erp5.component.interface.IBuildableBusinessLinkProcess import IBuildableBusinessLinkProcess
from erp5.component.interface.ITradeStateProcess import ITradeStateProcess
from erp5.component.interface.ITradePhaseProcess import ITradePhaseProcess
from erp5.component.interface.ISimulationMovementProcess import ISimulationMovementProcess

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
