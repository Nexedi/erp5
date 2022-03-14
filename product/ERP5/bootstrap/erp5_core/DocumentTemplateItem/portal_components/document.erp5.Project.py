# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 nSight SAS and Contributors. All Rights Reserved.
#                    Nicolas Lhoir <nicolas.lhoir@nsight.fr>
#               2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Jérome Perrin <jerome@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5.Document.Node import Node
from erp5.component.document.Movement import Movement
from erp5.component.interface.IMovement import IMovement
from Products.ERP5Type.XMLMatrix import XMLMatrix

@zope.interface.implementer(interfaces.INode, IMovement)
class Project(Node, Movement, XMLMatrix):
  """
  Project is a class which describes a typical project in consulting firm.
  A project has a client, an invoiced client. A project has also a start
  date and a stop date. It is composed of several tasks.

  Each task has a person to perform it, a certain amount of time, a date,
  a place, a description. For each person and each task, there is dedicated
  time rate.
  """
  meta_type = 'ERP5 Project'
  portal_type = 'Project'
  add_permission = Permissions.AddPortalContent
  # XXX to index start_date and stop_date in delivery table:
  isDelivery = ConstantGetter('isDelivery', value=True)
  isAccountable = ConstantGetter('isAccountable', value=False)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (
                     PropertySheet.Base,
                     PropertySheet.DublinCore,
                     PropertySheet.XMLObject,
                     PropertySheet.CategoryCore,
                     PropertySheet.Arrow,
                     PropertySheet.Task,
                     PropertySheet.Reference,
                     )