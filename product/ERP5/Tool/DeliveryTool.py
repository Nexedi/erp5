##############################################################################
#
# Copyright (c) 2005-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5.Tool.BuilderTool import BuilderTool
from Products.ERP5Type import Permissions

from Products.ERP5 import _dtmldir

class DeliveryTool(BuilderTool):
    """
    The DeliveryTool implements portal object
    deliveries building policies.
    """
    id = 'portal_deliveries'
    meta_type = 'ERP5 Delivery Tool'
    portal_type = 'Delivery Tool'
    allowed_types = ('ERP5 Delivery Buider',)

    # Declarative Security
    security = ClassSecurityInfo()

    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainDeliveryTool', _dtmldir )

InitializeClass(DeliveryTool)
