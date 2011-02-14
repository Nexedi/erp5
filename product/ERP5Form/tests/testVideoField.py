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
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.Globals import get_request
from StringIO import StringIO
from DateTime import DateTime


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

    self.assertEquals('<video preload="preload" src="Video content" controls="controls" height="85" width="160" loop="none" autoplay="" >\nYour browser does not support video tag.</video>', \
            self.field.render_view(value='Video content'))

    self.field.values['video_preload'] = 'none'
    self.field.values['video_loop'] = 'True'
    self.field.values['video_controls'] = 'none'
    self.field.values['video_autoplay'] = 'autoplay'
    self.field.values['video_error_message'] = 'Another error message'
    self.field.values['video_height'] = 800
    self.field.values['video_width'] = 1280

    self.assertEquals('<video preload="none" src="Another Video content" ' +
        'controls="none" height="800" width="1280" loop="True" autoplay="autoplay" ' +
        '>\nAnother error message</video>', \
            self.field.render_view(value='Another Video content'))

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestVideoField))
  return suite

