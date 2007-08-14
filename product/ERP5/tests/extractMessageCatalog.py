##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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
"""
This is not a unittest, but use its framework for extracting
translation messages.

how to use
-----------

$ /var/lib/erp5/Products/ERP5Type/tests/runUnitTest.py extractMessageCatalog

then erp5_content.pot and erp5_ui.pot will be made in the current directory.

"""


import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

try:
  from transaction import get as get_transaction
except ImportError:
  pass

# we reuse TestXHTML test.
from Products.ERP5.tests.testXHTML import TestXHTML

result = {}
target_catalog = ('erp5_ui', 'erp5_content')
for i in target_catalog:
  result[i] = {}

class ExtractMessageCatalog(TestXHTML):

  def afterSetUp(self):
    TestXHTML.afterSetUp(self)
    localizer = self.portal.Localizer

    for i in target_catalog:
      localizer.manage_delObjects(i)
      localizer.manage_addProduct['Localizer'].manage_addMessageCatalog(
        id=i, title='', languages=('en',))

  def beforeTearDown(self):
    for i in target_catalog:
      messages = dict(getattr(self.portal.Localizer, i)._messages)
      result[i].update(messages)

      f = file('%s.pot' % i, 'w')
      for msgid in result[i].keys():
        f.write('msgid "%s"\nmsgstr ""\n\n' % msgid)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ExtractMessageCatalog))
        return suite
