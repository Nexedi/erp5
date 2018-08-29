# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho <lucas@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################


import base64
import hashlib
import random
from Products.ERP5Type.Utils import bytes2str, str2bytes


class ShaCacheMixin(object):
  """
    ShaCache - Mixin Class
  """
  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.portal = self.getPortal()
    module = self.portal.web_site_module
    self.shacache = module.newContent(portal_type='Web Site',
      title='SHA Cache Server', skin_selection_name='SHACACHE')
    self.shacache.publish()
    self.header_dict = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ' + bytes2str(base64.b64encode(str2bytes(
        '%s:%s' % self.manager_username, self.manager_password)))
    }
    self.shacache_url = self.shacache.absolute_url()
    self.tic()
    self.data = 'Random Content. %s' % str(random.random())
    self.key = hashlib.sha512(self.data).hexdigest()
