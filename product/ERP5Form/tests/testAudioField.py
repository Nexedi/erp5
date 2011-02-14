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
from Products.ERP5Form.AudioField import AudioField
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.Globals import get_request
from StringIO import StringIO
from DateTime import DateTime


class TestAudioField(ERP5TypeTestCase):
  """Tests Audio field
  """

  def getTitle(self):
    return "Audio Field"

  def afterSetUp(self):
    self.field = AudioField('test_field')
    self.widget = self.field.widget

  def test_render_view(self):
    self.field.values['default'] = 'Audio content'

    self.assertEquals('<audio preload="preload" src="Audio content" ' +
        'loop="none" controls="controls" autoplay="" >\nYour browser does not ' +
        'support audio tag.</audio>', self.field.render_view(value='Audio content'))

    self.field.values['audio_preload'] = 'none'
    self.field.values['audio_loop'] = 'True'
    self.field.values['audio_controls'] = 'none'
    self.field.values['audio_autoplay'] = 'autoplay'
    self.field.values['audio_error_message'] = 'Another error message'

    self.assertEquals('<audio preload="none" src="Another Audio content" ' +
        'loop="True" controls="none" autoplay="autoplay" >\nAnother error ' +
        'message</audio>', self.field.render_view(value='Another Audio content'))

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAudioField))
  return suite

