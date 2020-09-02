##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#          Gabriel Lima <ciberglo@gmail.com>
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
from Products.ERP5Form.VideoField import VideoField

class TestVideoField(ERP5TypeTestCase):
  """Tests Video field
  """

  def getTitle(self):
    return "Video Field"

  def afterSetUp(self):
    self.field = VideoField('test_field')
    self.widget = self.field.widget

  def test_render_view(self):
    self.field.values['default'] = 'Video content'

    self.assertEqual('<video preload="auto" src="Video content" controls="controls" height="85" width="160" >Your browser does not support video tag.</video>', \
                      self.field.render_view(value='Video content'))

    self.field.values['video_preload'] = False
    self.field.values['video_loop'] = True
    self.field.values['video_controls'] = False
    self.field.values['video_autoplay'] = True
    self.field.values['video_error_message'] = 'Another error message'
    self.field.values['video_height'] = 800
    self.field.values['video_width'] = 1280

    self.assertEqual('<video src="Another Video content" ' +
        'height="800" width="1280" loop="loop" autoplay="autoplay" ' +
        '>Another error message</video>', \
            self.field.render_view(value='Another Video content'))

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestVideoField))
  return suite

