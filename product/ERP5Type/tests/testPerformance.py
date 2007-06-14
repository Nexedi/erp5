##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.CMFCore.tests.base.testcase import LogInterceptor
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.Cache import clearCache
from DateTime import DateTime
from time import time

# Define variable to chek if performance are good or not
# XXX These variable are specific to the testing environment
MIN_OBJECT_VIEW=0.110
MAX_OBJECT_VIEW=0.120
MIN_MODULE_VIEW=0.125
MAX_MODULE_VIEW=0.175
MIN_OBJECT_CREATION=0.0070
MAX_OBJECT_CREATION=0.0090
MIN_TIC=0.0330
MAX_TIC=0.0348
LISTBOX_COEF=0.02472
DO_TEST = 1

class TestPerformance(ERP5TypeTestCase, LogInterceptor):

    # Some helper methods
    quiet = 0
    run_all_test = 1

    def getTitle(self):
      return "Performance"

    def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return ('erp5_base',
              'erp5_ui_test',)

    def getBarModule(self):
      """
      Return the bar module
      """
      return self.getPortal()['bar_module']

    def afterSetUp(self):
      """
        Executed before each test_*.
      """
      self.login()
      self.bar_module = self.getBarModule()
      # Make the collection frequency higher,
      # because if it is waiting too much time, then the collection
      # take too much time and the test fails
      import gc
      gc.set_threshold(5000, 10, 10)


    def test_00_viewBarObject(self, quiet=quiet, run=run_all_test):
      """
      Estimate average time to render object view
      """
      if not run : return
      if not quiet:
        message = 'Test form to view Bar object'
        LOG('Testing... ', 0, message)
      # Some init to display form with some value
      gender = self.getPortal().portal_categories['gender']
      gender.newContent(id='male', title='Male', portal_type='Category')
      gender.newContent(id='female', title='Female', portal_type='Category')

      bar = self.bar_module.newContent(id='bar',
                                       portal_type='Bar',
                                       title='Bar Test',
                                       quantity=10000,)
      bar.setReference(bar.getRelativeUrl())
      get_transaction().commit()
      self.tic()
      # Check performance
      before_view = time()
      for x in xrange(100):
          bar.Bar_viewPerformance()
      after_view = time()
      req_time = (after_view - before_view)/100.
      if not quiet:
          print "time to view object form %.4f < %.4f < %.4f\n" %(MIN_OBJECT_VIEW, req_time, MAX_OBJECT_VIEW)
      if DO_TEST:
          self.failUnless(MIN_OBJECT_VIEW < req_time < MAX_OBJECT_VIEW)

    def test_01_viewBarModule(self, quiet=quiet, run=run_all_test):
      """
      Estimate average time to render module view
      """
      if not run : return
      if not quiet:
        message = 'Test form to view Bar module'
        LOG('Testing... ', 0, message)
      # remove previous object
      self.bar_module.manage_delObjects(['bar'])
      get_transaction().commit()
      self.tic()
      view_result = {}
      tic_result = {}
      add_result = {}
      # add object in bar module
      for i in xrange(10):
          before_add = time()
          for x in xrange(100):
            p = self.bar_module.newContent(portal_type='Bar',
                                           title='Bar Test',
                                           quantity="%4d" %(x,))
          after_add = time()
          get_transaction().commit()
          before_tic = time()
          self.tic()
          after_tic = time()
          before_form = time()
          for x in xrange(100):
            self.bar_module.BarModule_viewBarList()
          after_form = time()
          # store result
          key = "%06d" %(100*i+100,)
          view_result[key] = (after_form - before_form)/100.
          tic_result[key] = (after_tic - before_tic)/100.
          add_result[key] = (after_add - before_add)/100.

      # check result
      keys = view_result.keys()
      keys.sort()
      i = 0
      for key in keys:
        module_value = view_result[key]
        tic_value = tic_result[key]
        add_value = add_result[key]
        min_view = MIN_MODULE_VIEW + LISTBOX_COEF * i
        max_view = MAX_MODULE_VIEW + LISTBOX_COEF * i
        if not quiet:
            print "nb objects = %s\n\tadd = %.4f < %.4f < %.4f" %(key, MIN_OBJECT_CREATION, add_value, MAX_OBJECT_CREATION)
            print "\ttic = %.4f < %.4f < %.4f" %(MIN_TIC, tic_value, MAX_TIC)
            print "\tview = %.4f < %.4f < %.4f" %(min_view, module_value, max_view)
            print
        if DO_TEST:
            self.failUnless(min_view < module_value < max_view)
            self.failUnless(MIN_OBJECT_CREATION < add_value < MAX_OBJECT_CREATION)
            self.failUnless(MIN_TIC < tic_value < MAX_TIC)
        i += 1

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPerformance))
        return suite
