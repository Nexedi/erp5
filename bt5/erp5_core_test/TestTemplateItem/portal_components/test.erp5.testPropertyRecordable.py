##############################################################################
#
# Copyright (c) 2022 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestPropertyRecordable(ERP5TypeTestCase):

  def _makeOne(self, **kw):
    from Products.ERP5.mixin.property_recordable import PropertyRecordableMixin
    import erp5.portal_type

    class PropertyRecordablePerson(erp5.portal_type.Person, PropertyRecordableMixin):
      pass

    p = PropertyRecordablePerson('test').__of__(self.portal)
    p.edit(**kw)
    return p

  def test_record_property(self):
    p = self._makeOne(first_name='Foo', last_name='Baz')
    p.recordProperty('first_name')
    p.setFirstName('Bar')
    self.assertEqual(p.getFirstName(), 'Bar')
    self.assertTrue(p.isPropertyRecorded('first_name'))
    self.assertEqual(p.getRecordedProperty('first_name'), 'Foo')
    self.assertEqual(p.getRecordedPropertyIdList(), ['first_name'])

  def test_record_property_category(self):
    p = self._makeOne(region='source')
    p.recordProperty('region')
    p.setRegion('destination')
    self.assertEqual(p.getRegionList(), ['destination'])
    self.assertTrue(p.isPropertyRecorded('region'))
    self.assertEqual(p.getRecordedProperty('region'), ['source'])
    self.assertEqual(p.getRecordedPropertyIdList(), ['region'])

  def test_record_property_local_property(self):
    p = self._makeOne(**{self.id(): 'Foo'})
    p.recordProperty(self.id())
    p.edit(**{self.id(): 'Bar'})
    self.assertEqual(p.getProperty(self.id()), 'Bar')
    self.assertTrue(p.isPropertyRecorded(self.id()))
    self.assertEqual(p.getRecordedProperty(self.id()), 'Foo')
    self.assertEqual(p.getRecordedPropertyIdList(), [self.id()])

  def test_as_recorded_context(self):
    p = self._makeOne(first_name='Foo', last_name='Baz')
    p.recordProperty('first_name')
    p.setFirstName('bar')
    self.assertEqual(p.asRecordedContext().getFirstName(), 'Foo')

  def test_clear_recorded_property_(self):
    p = self._makeOne(first_name='Foo', last_name='Baz')
    p.recordProperty('first_name')
    p.recordProperty('last_name')

    p.clearRecordedProperty('first_name')
    self.assertFalse(p.isPropertyRecorded('first_name'))
    self.assertTrue(p.isPropertyRecorded('last_name'))

    p.clearRecordedProperty('last_name')
    self.assertFalse(p.isPropertyRecorded('first_name'))
    self.assertFalse(p.isPropertyRecorded('last_name'))
