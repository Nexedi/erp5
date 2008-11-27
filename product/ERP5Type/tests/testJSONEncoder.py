##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                     Lucas Carvalho <lucas@nexedi.com>
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

import unittest
from Products.ERP5Type.JSONEncoder import encodeInJson

class TestJSONEncoder(unittest.TestCase):

  def test_encodeAListType(self):
    my_list = [1, 2, 3, 'foo', 'bar']
    result = encodeInJson(my_list)
    self.assertEquals(result, '[1, 2, 3, "foo", "bar"]')

  def test_encodeATupleType(self):
    my_tuple = (1, 2, 3, 'foo', None,)
    result = encodeInJson(my_tuple)
    self.assertEquals(result, '[1, 2, 3, "foo", null]')

  def test_encodeADictionaryType(self):
    my_dict = { 'foo': 'bar',
                1: 2,
                'bar': [1, 2, 'bar'],
                2: None,
                3: float(3),
                4: True,
                5: False,
              }
    expected_result = '{"1": 2, "2": null, "3": 3.0, "bar": [1, 2, "bar"], '\
                      '"5": false, "4": true, "foo": "bar"}'
    result = encodeInJson(my_dict)
    self.assertEquals(result, expected_result)
                    
  def test_encodeAStringType(self):
    result = encodeInJson('This is my string.')
    self.assertEquals(result, '"This is my string."')

  def test_encodeAIntType(self):
    result = encodeInJson(int(3))
    self.assertEquals(result, '3')

  def test_encodeANoneType(self):
    result = encodeInJson(None)
    self.assertEquals(result, 'null')

  def test_encodeAFloatType(self):
    result = encodeInJson(float(3))
    self.assertEquals(result, '3.0')

  def test_encodeALongType(self):
    result = encodeInJson(long(3))
    self.assertEquals(result, '3')

  def test_encodeABooleanType(self):
    result_true = encodeInJson(True)
    result_false = encodeInJson(False)

    self.assertEquals(result_true, 'true')
    self.assertEquals(result_false, 'false')

if __name__ == '__main__':
  unittest.main()
