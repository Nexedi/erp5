# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from Acquisition import aq_base
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import setSecurityManager
from Products.ERP5.mixin.base_extensible_traversable import BaseExtensibleTraversableMixin
from Products.ERP5Type.UnrestrictedMethod import unrestricted_apply

class DocumentExtensibleTraversableMixin(BaseExtensibleTraversableMixin):
  """
  This class provides a implementation of IExtensibleTraversable for Document classed based documents.
  """

  def getExtensibleContent(self, request, name):
    old_manager, user = self._forceIdentification(request)
    # Next get the document per name
    portal = self.getPortalObject()
    document = self.getDocumentValue(name=name, portal=portal)
    # restore original security context if there's a logged in user
    if user is not None:
      setSecurityManager(old_manager)
    if document is not None:
      document = aq_base(document.asContext(id=name, # Hide some properties to permit locating the original
                                            original_container=document.getParentValue(),
                                            original_id=document.getId(),
                                            editable_absolute_url=document.absolute_url()))
      return document.__of__(self)

    # no document found for current user, still such document may exists
    # in some cases user (like Anonymous) can not view document according to portal catalog
    # but we may ask him to login if such a document exists
    isAuthorizationForced = getattr(self, 'isAuthorizationForced', None)
    if isAuthorizationForced is not None and isAuthorizationForced():
      if unrestricted_apply(self.getDocumentValue, (name, portal)) is not None:
        # force user to login as specified in Web Section
        raise Unauthorized
