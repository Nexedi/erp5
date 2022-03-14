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
