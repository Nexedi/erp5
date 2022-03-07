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

import hashlib
import json
import random
from base64 import b64encode
from DateTime import DateTime


class ShaDirMixin(object):
  """
    ShaDir - Mixin Class
  """
  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.portal = self.getPortal()

    self.key = 'mykey' + str(random.random())
    file_content = 'This is the content.'
    creation_date = DateTime()
    self.expiration_date = creation_date + 30

    self.data = json.dumps([
      json.dumps({
        'sha512': hashlib.sha512(file_content).hexdigest(),
        'url': 'https://example.com/some/file.ext',
        'creation_date': str(creation_date),
        'expiration_date': str(self.expiration_date),
      }),
      b64encode("User SIGNATURE goes here."),
    ])

    self.sha512sum = hashlib.sha512(self.data).hexdigest()

    self.header_dict = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ' + b64encode('ERP5TypeTestCase:'),
    }

    module = self.portal.web_site_module
    self.shadir = module.newContent(portal_type='Web Site',
      title='SHA Dir Server', skin_selection_name='SHADIR')
    self.shadir.publish()
    self.shadir_url = self.shadir.absolute_url()
    self.tic()
