# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

class ISolver(Interface):
  """Target Solver interface specification

  This interface must be implemented by all target solvers
  which are used to solve divergences in ERP5 simulation. Documents
  which implement ISolver provide a solve method.

  Besides ISolver static interface definition, target solvers
  must support IDeliveryGetter to access simulation movements to solve.

  TODO-XXX:
    - find a way to make static interfaces inherit from
      dynamic interfaces in ERP5 (ex. solver process workflow)
    - IDeliveryGetter is not appropriate name / interface
    - find a way to define at which level to solve divergences
      (ex. line, delivery)
  """
  def solve(activate_kw=None):
    """
    Start the solving process (and trigger the workflow method
    in solver_process_workflow). At the end the solving process,
    appropriate methods of the solver_process_workflow must be invoked
    (ex. succeed, fail, abort).

    NOTE: the solve method is invoked to solve divergences or to
    optimize movements. Examples include: Adopt, Accept, Reduce,
    Postpone, Optimize Critical Path,
    """

  def isSolving():
    """
    Returns True if the solver processing in ongoing. False else.
    """

  def isSolved():
    """
    Returns True if all divergences are solved, False else.
    """

  def isFailed():
    """
    Returns True if divergence resolution fails. False else.
    """

  def isAborted():
    """
    Returns True if divergence resolution was aborted. False else.
    """
