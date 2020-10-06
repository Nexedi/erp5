##############################################################################
#
# Copyright (c) 2002-2020 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class testComputerMetadata(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base', 'erp5_ingestion', 'erp5_dms',)

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    pass

  def test_upload(self):
    upload_content = 'xxxx'
    document = self.portal.portal_contributions.newContent(
      data=upload_content
    )
    self.assertTrue(document.getPortalType(), 'Computer Metadata Snapshot')
    self.assertTrue(document.getData(), upload_content)

