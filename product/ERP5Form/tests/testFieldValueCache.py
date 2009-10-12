# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
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

from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
import transaction
import unittest

class TestFieldValueCache(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "TestDiscussionThread"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return (
      'erp5_base',
    )

  def setUpOnce(self):
    """
       Do nothing
    """

  def afterSetUp(self):
    """
    This is ran before each and every test, used to set up the environment
    """
    self.person_module = self.portal.getDefaultModule(portal_type='Person')

  def testEditZMIFieldPurgesValueCache(self):
    """
    This test makes sure that if manage_edit is called on a ZMI
    field then its ValueCache is purged.
    """
    person = self.person_module.newContent()
    form = person.Person_view
    # Render
    form()
    # Get form value
    field = form.my_first_name
    id = 'title'
    from Products.ERP5Form.ProxyField import _field_value_cache
    cache_id = ('ProxyField.get_value',
                field._p_oid,
                field._p_oid,
                id)
    # Make sure cache has field
    self.assertTrue(_field_value_cache.has_key(cache_id))
    # Make sure cache and field are equal
    self.assertEquals(field.get_value(id), _field_value_cache[cache_id])
    # Call manage_renameObject
    form.manage_renameObject('my_first_name', 'my_first_name2')
    form.manage_renameObject('my_first_name2', 'my_first_name')
    # Make sure cache has no field
    self.assertFalse(_field_value_cache.has_key(cache_id))
    # Render
    form()
    # Make sure cache has field
    self.assertTrue(_field_value_cache.has_key(cache_id))
    # Make sure cache and field are equal
    self.assertEquals(field.get_value(id), _field_value_cache[cache_id])
