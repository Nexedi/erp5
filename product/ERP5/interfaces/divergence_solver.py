# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
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

class IDivergenceSolver(Interface):
  """Solves divergence between delivery line and related simulation movements"""

  def solve(decision_list):
    """Solves divergences on self according to decision_list

    decision_list is list of instances of DivergenceSolutionDecision class
    """

class IDeliverySolver(Interface):
  """Solves quantity values between delivery line and related simulation movements"""
  # placeholder to define
  pass

class ITargetSolver(Interface):
  """Solves changes of properties up to simulation tree with taking proper decisions"""
  # placeholder to define
  pass
