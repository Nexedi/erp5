# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from Globals import InitializeClass
from Products.PythonScripts.Utility import allow_class
from AccessControl import ClassSecurityInfo
from Persistence import Persistent

class DivergenceSolutionDecision(Persistent):
  """Decision class

    Represent decision took during solving divergence between reality and
    simulation

    Provides possibility to override movement's property value in case of
    accepting decision with forcing.

    Properties are two types - historical only and really used.

    Historical only are for information traceability:

      * delivery_solver_name
      * target_solver_name

    Really used shall impact property value of movement:

      * divergence
      * decision
      * force_property

    divergence
      instance of DivergenceMessage

    decision
      string representing took decision:
        * accept
        * adopt
        * split

    delivery_solver_name
      delivery solver used during taking decision

    target_solver_name
      target solver used during taking decision

    force_property
      If set, property on decision overrides

    split_kw
      Dictionary passed to TargetSolver in case of splitting.
  """
  meta_type = "DivergenceSolutionDecision"
  security = ClassSecurityInfo()
  security.declareObjectPublic() # FIXME need to be decided

  # XXX: Is there any place to know all possible decisions?
  ALLOWED_DECISION_TUPLE = ('accept', 'adopt', 'split')

  def __repr__(self):
    repr_str = '<%s object at 0x%x\n' % (self.__class__.__name__, id(self))
    for prop in 'divergence', 'decision', 'delivery_solver_name', \
                'target_solver_name', 'force_property':
      repr_str += '%s = %r\n' % (prop, getattr(self, prop))
    repr_str += '>'
    return repr_str

  def __init__(self, divergence, decision, delivery_solver_name=None,
      target_solver_name=None, force_property=False, split_kw=None):
    self.divergence = divergence
    self.decision = decision
    self.delivery_solver_name = delivery_solver_name
    self.target_solver_name = target_solver_name
    self.force_property = force_property
    self.split_kw = split_kw
    if not (self.decision in self.ALLOWED_DECISION_TUPLE):
      raise ValueError(
        'Decision %s is not supported' % self.decision)

InitializeClass(DivergenceSolutionDecision)
allow_class(DivergenceSolutionDecision)
