# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from erp5.component.document.Event import Event


class ArtificialTaskReportLine(Event):
  """One message of one conversation with a Large Language Model.

  A line in the state `draft` is a request. The `start` transition sends the
  request. A line in the state `stopped` holds an answer, or holds a request
  that has an answer.
  """
  meta_type = 'ERP5 Artificial Task Report Line'
  portal_type = 'Artificial Task Report Line'

  security = ClassSecurityInfo()

  # WARNING: no docstring, so Zope does not publish `<line>/send` to a GET.
  # Do not create `ArtificialTaskReportLine_send`: `script_Event_send` reads
  # that id as a type based method.
  security.declareProtected(Permissions.AccessContentsInformation, 'send')
  def send(self, *args, **kw):
    return self.ArtificialTaskReportLine_sendRequest()

  # The Alarm calls this method until the provider answers. No docstring.
  security.declareProtected(Permissions.AccessContentsInformation,
                            'checkResponse')
  def checkResponse(self):
    return self.ArtificialTaskReportLine_checkResponse()

  # Modify permission, because this method writes. No docstring.
  security.declareProtected(Permissions.ModifyPortalContent, 'cancelRequest')
  def cancelRequest(self, comment=None):
    return self.ArtificialTaskReportLine_checkResponse(
      is_cancel=1, comment=comment)


InitializeClass(ArtificialTaskReportLine)
