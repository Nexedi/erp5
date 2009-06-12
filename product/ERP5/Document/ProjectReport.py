##############################################################################
#
# Copyright (c) 2002 nSight SAS and Contributors. All Rights Reserved.
#                    Nicolas Lhoir <nicolas.lhoir@nsight.fr>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces

from Products.ERP5.Document.Delivery import Delivery

class ProjectReport(Delivery):
    """
    A project report allows to report times and expenses related to a project in
    a consulting firm. This project report has a starting and and finishing date,
    which is mainly used for information and classification.

    The time sheet and the expense sheet are both composed of billiable and non-
    billiable time and expense to the invoiced client.

    The amount of time on a particular project relates to a client.
    A expense relates to a project.

    OUTPHASED BY TASK REPORT
    """

    meta_type = 'ERP5 Project Report'
    portal_type = 'Project Report'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = (
                       PropertySheet.Base,
                       PropertySheet.DublinCore,
                       PropertySheet.XMLObject,
                       PropertySheet.CategoryCore,
                       PropertySheet.Task,
                      )

