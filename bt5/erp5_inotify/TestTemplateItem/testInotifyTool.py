##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                    Julien Muchembled <jm@nexedi.com>
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

import os, shutil, tempfile, unittest
import transaction
from Acquisition import aq_base
from Products.ERP5Type.Base import Base
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5.ERP5Site import addERP5Tool

class TestInotifyTool(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return "erp5_core_proxy_field_legacy", "erp5_inotify"

  def test_inotify(self):
    from Products.ERP5.Tool.InotifyTool import IN_CREATE, IN_MODIFY, IN_DELETE
    addERP5Tool(self.portal, 'portal_inotify', 'Inotify Tool')
    inotify_tool = self.portal.portal_inotify
    for inotify in inotify_tool.objectValues():
      inotify._setEnabled(False)
    inotify_tool._p_changed = 1
    transaction.commit()
    def checkCache(notify_list):
      self.assertEqual(notify_list,
        getattr(aq_base(inotify_tool), '_v_notify_list', None))
    checkCache(None)
    tmp_dir = tempfile.mkdtemp()
    try:
      inotify_tool.process_timer(None, None)
      transaction.commit()
      checkCache([])
      inotify = inotify_tool.newContent(inode_path='string:'+tmp_dir,
                                        sense_method_id='Inotify_test',
                                        node=inotify_tool.getCurrentNode())
      inotify_id = inotify.getId()
      checkCache(None)
      inotify_tool.process_timer(None, None)
      transaction.commit()
      checkCache([])
      event_list = []
      inotify.__class__.Inotify_test = lambda self, events: \
        event_list.extend(events)
      try:
        inotify.setEnabled(True)
        transaction.commit()
        checkCache(None)
        inotify_tool.process_timer(None, None)
        transaction.commit()
        checkCache([inotify_id])
        self.assertEqual(event_list, [])
        p = os.path.join(tmp_dir, '1')
        with open(p, 'w') as f:
          inotify_tool.process_timer(None, None)
          transaction.commit()
          self.assertEqual(event_list, [{'path': p, 'mask': IN_CREATE}])
          del event_list[:]
          f.write('foo')
        inotify_tool.process_timer(None, None)
        transaction.commit()
        self.assertEqual(event_list, [{'path': p, 'mask': IN_MODIFY}])
        del event_list[:]
        p2 = os.path.join(tmp_dir, '2')
        os.rename(p, p2)
        inotify_tool.process_timer(None, None)
        transaction.commit()
        expected = [{'path': p, 'mask': IN_DELETE},
                    {'path': p2, 'mask': IN_CREATE}]
        expected.remove(event_list.pop())
        self.assertEqual(event_list, expected)
      finally:
        del inotify.__class__.Inotify_test
    finally:
      shutil.rmtree(tmp_dir)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInotifyTool))
  return suite
