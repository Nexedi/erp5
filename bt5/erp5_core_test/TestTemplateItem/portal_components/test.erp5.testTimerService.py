##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Yoshinori Okuji <yo@nexedi.com>
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

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from AccessControl.ZopeGuards import guarded_apply, guarded_getattr
from zExceptions import Unauthorized

class TestTimerService(ERP5TypeTestCase):
  """
  Test TimerService-related features. Maybe this should be put in TimerService
  itself, but TimerService is not a part of ERP5, and I am not sure if it is a good
  idea to put an ERP5-type test in it.
  """

  def getTitle(self):
    return "TimerService"

  def getBusinessTemplateList(self):
    """
    """
    return ()

  def afterSetUp(self):
    uf = self.portal.acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def test_01_checkAnonymousProcessing(self):
    """
      Test whether a timer can be invoked by anonymous.
    """
    noSecurityManager()
    timer_service = self.app.Control_Panel.timer_service
    process_timer = guarded_getattr(timer_service, 'process_timer')
    try:
        guarded_apply(process_timer, (0,))
    except Unauthorized:
        self.fail('calling process_timer is unauthorized')
    except:
        # Do not care about any exception but unauthorized.
        pass

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTimerService))
  return suite
