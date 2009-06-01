##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ben Mayhew <maybewhen@gmx.net>
#                    Sebastien Robin <seb@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
##############################################################################
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces

from Products.ERP5.Document.EmailDocument import EmailDocumentProxyMixin
from Products.ERP5.Document.Event import Event

class Acknowledgement(EmailDocumentProxyMixin, Event):
  """
    goal : 

    Acts as a proxy to the message in the case of
    - private email
    - message displayed to the user ?

    We need this proxy because the user might not have the right to access
    to the original message, and we don't wish to duplicate the content of
    the original message (which can use attachements).
    
    Use Case:

      - A Site Notification is created in order to notify to all people of a
      company. Then every time an user will acknowledge the notification,
      a new Acknowledgement is created.
  """

  meta_type = 'ERP5 Acknowledgement'
  portal_type = 'Acknowledgement'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isDelivery = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Document
                    , PropertySheet.DublinCore
                    , PropertySheet.Snapshot
                    , PropertySheet.Task
                    , PropertySheet.Url
                    , PropertySheet.Arrow
                    , PropertySheet.Event
                    , PropertySheet.Delivery
                    , PropertySheet.DocumentProxy
                   )


