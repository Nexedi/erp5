##############################################################################
#
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
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

class TestMultiRelationField(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "TestMultiRelationField"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base',)

  def test_01_relationFieldReindexObject(self):
    """
    Check that edition of a relation field create a reindex activity.
    This is necessary when only a relation field is edited on a form,
    and when document is not indexed because of indirect things (like
    edit_workflow).
    """
    foo_object = self.portal.foo_module.newContent()
    self.tic()
    form = self.portal.Foo_view
    relation_field = form.my_foo_category_title
    category = self.portal.portal_categories.action_type.object_jump
    editor = relation_field.validator.editor('my_foo_category_title', 'foo_category',
                 ['Category'], [('Category', 'Category')], 'title', '',
                 [([category.getUid()], category.getUid(), category.getId(),
                   None, 'subfield_field_my_foo_category_title_item')], '')
    foo_path = foo_object.getPath()
    foo_uid = foo_object.getUid()
    self.assertEqual([x.path for x in self.portal.portal_catalog(uid=foo_uid)], [foo_path])
    foo_object.unindexObject()
    self.tic()
    self.assertEqual([x.path for x in self.portal.portal_catalog(uid=foo_uid)], [])
    editor.edit(foo_object)
    self.tic()
    self.assertEqual([x.path for x in self.portal.portal_catalog(uid=foo_uid)], [foo_path])
