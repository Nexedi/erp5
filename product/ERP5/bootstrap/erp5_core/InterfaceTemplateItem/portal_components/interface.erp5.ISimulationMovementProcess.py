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
