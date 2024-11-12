# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
#                    Cédric Le Ninivin <cedric.leninivin@nexedi.com>
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
from Acquisition import aq_inner
from erp5.component.document.WebSection import WebSection
from Products.ERP5Type import Permissions

MARKER = []
class jIOWebSection(WebSection):
  """
  This Web Section is a wrapper to jIO to pass content in the body
  """

  portal_type = 'jIO Web Section'
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  @security.protected(Permissions.AccessContentsInformation)
  def getLayoutProperty(self, key, default=None):
    """
        A simple method to get a property of the current by
        acquiring it from the current section or its parents.
    """
    section = aq_inner(self)
    while section.getPortalType() in ('Web Section', 'Web Site', 'Static Web Section', 'Static Web Site',
                                      'jIO Web Section'):
      result = section.getProperty(key, MARKER)
      if result not in (MARKER, None):
        return result
      section = section.aq_parent
    return default

  @security.protected(Permissions.View)
  def get(self): #pylint:disable=arguments-differ
    """
      Taken from WebSection Bobo Traverse, the difference is that
      __bobo_traverse__ from DocumentExtensibleTraversableMixin is not called
    """
    # Register current web site physical path for later URL generation
    return self.ERP5Site_asjIOStyle(mode="get", text_content=self.REQUEST.get('BODY'))

  @security.protected(Permissions.View)
  def post(self):
    """
      Taken from WebSection Bobo Traverse, the difference is that
      __bobo_traverse__ from DocumentExtensibleTraversableMixin is not called
    """
    # Register current web site physical path for later URL generation
    return self.ERP5Site_asjIOStyle(mode="post", text_content=self.REQUEST.get('BODY'))

  @security.protected(Permissions.View)
  def put(self):
    """
      Taken from WebSection Bobo Traverse, the difference is that
      __bobo_traverse__ from DocumentExtensibleTraversableMixin is not called
    """
    # Register current web site physical path for later URL generation
    return self.ERP5Site_asjIOStyle(mode="put", text_content=self.REQUEST.get('BODY'))

  @security.protected(Permissions.View)
  def allDocs(self):
    """
      Taken from WebSection Bobo Traverse, the difference is that
      __bobo_traverse__ from DocumentExtensibleTraversableMixin is not called
    """
    # Register current web site physical path for later URL generation
    return self.ERP5Site_asjIOStyle(mode="allDocs", text_content=self.REQUEST.get('BODY'))
