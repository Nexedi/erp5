# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.CMFActivity.ActiveProcess import ActiveProcess

class SolverProcess(XMLObject, ActiveProcess):
  """
    Solver Process class represents the decision of the user
    to solve a divergence. The data structure is the following:

    Solver Process can contain:

    - Solver Decision documents which represent the decision
      of the user to solve a divergence on a given Delivery Line
      by using a certain heuristic

    - Target Solver documents which encapsulate the resolution
      heuristic in relation with DivergenceTester (ie. each
      DivergenceTester must provide a list of Target Solver portal 
      types whch are suitable to solve a given divergence) and
      which may eventually use a Delivery Solver each time divergence
      is related to quantities.

    Every Simulation Movement affected by a Solver Process has a relation
    to the solver process through the "solver" base category.         
  """
  meta_type = 'ERP5 Solver Process'
  portal_type = 'Solver Process'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isIndexable = 0 # We do not want to fill the catalog with objects on which we need no reporting

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    )