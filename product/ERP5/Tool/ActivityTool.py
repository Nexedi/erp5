##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser
from Globals import InitializeClass
from Acquisition import aq_base
from DateTime import DateTime

from zLOG import LOG

class ActivityTool (UniqueObject):
    """
    The ActivityTool implement activities in ERP5
    (concurrency and autonomy).

    For safety reasons, all asynchronous messages
    are serialized on an object per object basis
    (this prevents many conflicts and is easier to
    manage).

    The ActivityTool keeps queues of reified methods
    which should be called on objects.

    The activity tool is either started by being called
    directly (ex. by the Interaction tool )
    or by schedules tasks documents.

    Examples of applications:

    - serialize async interactions

    - call tasks when required - tasks are considered
      as documents.... (indexed into databse of tasks...)

    ERP5 main purpose:

    - serialize interaction

    - execute schedules tasks

    What would be nice

    - to execute methods by launching multiple
      XML RPC clients

    - to regsiter methods by receive XML RPC calls

    XXXXXXXXXX
    """
    id = 'portal_activities'
    meta_type = 'ERP5 Activity Tool'
    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     ,
                     )

InitializeClass(ActivityTool)
