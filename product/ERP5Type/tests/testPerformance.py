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

import unittest
from time import time
import gc
import subprocess

from zExceptions import Unauthorized
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.ERP5Type.tests.utils import LogInterceptor
import os

# Define variable to chek if performance are good or not
# XXX These variable are specific to the testing environment
#     (pystone results: min: < 131578.9 - mean: ~ 139768.5 - max: > 147058.8)
# Historical values are here to remember what was original values on this
# specific testing environment. We must always try to stay below max
# historical values.
                                    # Historical values
MIN_OBJECT_VIEW=0.043               # 0.160 0.020, 0.112
MAX_OBJECT_VIEW=0.057               # 0.174 0.050, 0.120
MIN_OBJECT_MANY_LINES_VIEW=0.165    # 0.040, 0.274
MAX_OBJECT_MANY_LINES_VIEW=0.215    # 0.090, 0.294
MIN_OBJECT_PROXYFIELD_VIEW=0.176    # 0.242 0.020, 0.199
MAX_OBJECT_PROXYFIELD_VIEW=0.191    # 0.257 0.090, 0.220
#CURRENT_MIN_OBJECT_VIEW=0.1220
#CURRENT_MAX_OBJECT_VIEW=0.1280
MIN_MODULE_VIEW=0.050               # 0.160 0.020, 0.125
MAX_MODULE_VIEW=0.065               # 0.174 0.070, 0.175
MIN_TIC=0.0073                      # 0.0333 0.0020, 0.260
MAX_TIC=0.0011                      # 0.0354 0.0090, 0.343
MIN_OBJECT_CREATION=0.0053          # 0.0130  0.0010, 0.0070
MAX_OBJECT_CREATION=0.0068          # 0.0145  0.0040, 0.0082
LISTBOX_COEF=0.00173                # 0.02472
# Change history
# 2016-08-11
#   Adapt values with new hardware from online.net.
# 2013-03-01
#   Adapt values with new hardware and last improvements
# 2010-02-09
#  the bot is slightly slower since 2009-11-29
#   MIN_OBJECT_VIEW : 0.142 -> 0.144
#   MAX_OBJECT_VIEW : 0.144 -> 0.147
#   MIN_MODULE_VIEW : 0.147 -> 0.148
#   MAX_MODULE_VIEW : 0.150 -> 0.153
#   LISTBOX_COEF: 0.00169 -> 0.00173
#  too fast by the result of optimisation
#   MIN_TIC : 0.0329 -> 0.0323
#   MAX_TIC : 0.0350 -> 0.0344
#   MIN_OBJECT_MANY_LINES_VIEW : 0.288 -> 0.280
#   MAX_OBJECT_MANY_LINES_VIEW : 0.292 -> 0.286
#   MIN_OBJECT_PROXYFIELD_VIEW : 0.225 -> 0.213
#   MAX_OBJECT_PROXYFIELD_VIEW : 0.228 -> 0.217
#  XXX test_02_viewFooObjectWithManyLines became slower with [31650]
#      due to a new field in Foo_view.
# 2009-11-16
#   MIN_OBJECT_CREATION : 0.0071 -> 0.0068
#   MAX_OBJECT_CREATION : 0.0077 -> 0.0073
#   MIN_TIC : 0.0333 -> 0.0329
#   MAX_TIC : 0.0355 -> 0.0350
#   MAX_MODULE_VIEW : 0.151 -> 0.150
#   MIN_OBJECT_MANY_LINES_VIEW : 0.289 -> 0.288
#   MIN_OBJECT_MANY_LINES_VIEW : 0.293 -> 0.292
# 2009-11-12
#  temporary increase threshold for view to notice future regressions
#   MIN_OBJECT_VIEW : 0.132 -> 0.142
#   MAX_OBJECT_VIEW : 0.138 -> 0.144
#  too fast by the result of optimisation
#   MIN_OBJECT_CREATION : 0.0090 -> 0.0071
#   MAX_OBJECT_CREATION : 0.0110 -> 0.0077
#   MIN_TIC : 0.0345 -> 0.0333
#   MAX_TIC : 0.0395 -> 0.0355
#   MIN_MODULE_VIEW : 0.149 -> 0.147
#   MAX_MODULE_VIEW : 0.189 -> 0.151
#   LISTBOX_COEF : 0.001725 -> 0.00169
# 2009-10-23
#  too fast by the result of optimisation
#   MIN_OBJECT_MANY_LINES_VIEW : 0.300 -> 0.289
#   MAX_OBJECT_MANY_LINES_VIEW : 0.320 -> 0.293
#  too fast by modifying the pagination renderer
#   MIN_MODULE_VIEW : 0.155 -> 0.149
#   MAX_MODULE_VIEW : 0.195 -> 0.189
#   LISTBOX_COEF : 0.02472 -> 0.001725
DO_TEST = 1

# Profiler support.
# set 1 to get profiler's result (unit_test/tests/<func_name>)
PROFILE = 0
# set this to 'pprofile' to profile with pprofile ( https://github.com/vpelletier/pprofile )
# instad of python's standard library profiler ( https://docs.python.org/2/library/profile.html )
PROFILER = 'pprofile'


class TestPerformanceMixin(ERP5TypeTestCase, LogInterceptor):

    def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return ('erp5_base',
              'erp5_ui_test',)

    def afterSetUp(self):
      """
        Executed before each test_*.
      """
      # We don't want cpu time to be spent by random external sources:
      # - Bot should have its SQL database in a tmpfs storage.
      # - As bot delete all '*.pyc' files before updating the working copy,
      #   all '*.pyc' files have just been recreated. They should be synced:
      subprocess.call('sync')
      # - Prevent GC from happening.
      # It would increase the "crosstalk" between using more ram and using more cpu.
      # Another problem is that it makes result even less reproductible on another
      # machine where memory use does not evolve identicaly (ie. x86_64 arch,
      # because of 64bits pointers).
      gc.disable()
      self.login()
      self.bar_module = self.getBarModule()
      self.foo_module = self.portal.foo_module

    def getBarModule(self):
      """
      Return the bar module
      """
      return self.portal['bar_module']

    def profile(self, func, suffix='', args=(), kw=None):
      """Profile `func(*args, **kw)` with selected profiler,
      and dump output in a file called `func.__name__ + suffix`
      """
      if not kw:
        kw = {}

      if PROFILER == 'pprofile':
        import pprofile
        prof = pprofile.Profile()
      else:
        from cProfile import Profile
        prof = Profile()

      prof_file = '%s%s' % (func.__name__, suffix)
      try:
        os.unlink(prof_file)
      except OSError:
        pass
      prof.runcall(func, *args, **kw)
      prof.dump_stats(prof_file)

    def beforeTearDown(self):
      # Re-enable gc at teardown.
      gc.enable()
      self.abort()


class TestPerformance(TestPerformanceMixin):

    def getTitle(self):
      return "Performance"

    def beforeTearDown(self):
      super(TestPerformance, self).beforeTearDown()
      self.bar_module.manage_delObjects(list(self.bar_module.objectIds()))
      self.foo_module.manage_delObjects(list(self.foo_module.objectIds()))
      gender = self.portal.portal_categories['gender']
      gender.manage_delObjects(list(gender.objectIds()))
      gender = self.portal.portal_caches.clearAllCache()
      self.tic()

    def checkViewBarObject(self, min, max, prefix=None):
      # Some init to display form with some value
      if prefix is None:
        prefix = ''
      gender = self.portal.portal_categories['gender']
      if 'male' not in gender.objectIds():
        gender.newContent(id='male', title='Male', portal_type='Category')
      if 'female' not in gender.objectIds():
        gender.newContent(id='female', title='Female', portal_type='Category')

      bar = self.bar_module.newContent(id='bar',
                                       portal_type='Bar',
                                       title='Bar Test',
                                       quantity=10000,)
      bar.setReference(bar.getRelativeUrl())
      self.tic()
      # Check performance
      before_view = time()
      for x in xrange(100):
        # XXX: Note that we don't clean TransactionVariable cache and REQUEST
        #      before each call to 'view' requests. In reality, they would be
        #      always empty at the beginning of such requests.
        #      If you work to improve performance of 'view' requests using this
        #      kind of cache, make sure it is actually useful outside
        #      testPerformance.
        bar.Bar_viewPerformance()
      after_view = time()
      req_time = (after_view - before_view)/100.
      print "%s time to view object form %.4f < %.4f < %.4f\n" % \
              (prefix, min, req_time, max)
      if PROFILE:
          self.profile(bar.Bar_viewPerformance)
      if DO_TEST:
          self.assertTrue(min < req_time < max,
                          '%.4f < %.4f < %.4f' % (min, req_time, max))

    def test_00_viewBarObject(self, min=None, max=None):
      """
      Estimate average time to render object view
      """
      message = 'Test form to view Bar object'
      LOG('Testing... ', 0, message)
      self.checkViewBarObject(MIN_OBJECT_VIEW, MAX_OBJECT_VIEW,
                              prefix='objective')

    def test_01_viewBarModule(self):
      """
      Estimate average time to render module view
      """
      message = 'Test form to view Bar module'
      LOG('Testing... ', 0, message)
      self.tic()
      view_result = {}
      tic_result = {}
      add_result = {}
      # call view once to fill caches
      self.bar_module.BarModule_viewBarList()
      # add object in bar module
      for i in xrange(10):
          def add():
            for x in xrange(100):
              p = self.bar_module.newContent(portal_type='Bar',
                                             title='Bar Test',
                                             quantity="%4d" %(x,))
          before_add = time()
          if PROFILE:
            self.profile(add, i)
          else:
            add()
          after_add = time()
          self.commit()
          before_tic = time()
          if PROFILE:
              self.profile(self.tic, i)
          else:
              self.tic()
          after_tic = time()
          gc.collect()
          before_form = time()
          for x in xrange(100):
            self.bar_module.BarModule_viewBarList()
          after_form = time()
          # store result
          key = "%06d" %(100*i+100,)
          view_result[key] = (after_form - before_form)/100.
          tic_result[key] = (after_tic - before_tic)/100.
          add_result[key] = (after_add - before_add)/100.

          if PROFILE:
              self.profile(self.bar_module.BarModule_viewBarList, i)
      keys = view_result.keys()
      keys.sort()
      # first display results
      i = 0
      for key in keys:
        module_value = view_result[key]
        tic_value = tic_result[key]
        add_value = add_result[key]
        min_view = MIN_MODULE_VIEW + LISTBOX_COEF * i
        max_view = MAX_MODULE_VIEW + LISTBOX_COEF * i
        print "nb objects = %s\n\tadd = %.4f < %.4f < %.4f" %(key, MIN_OBJECT_CREATION, add_value, MAX_OBJECT_CREATION)
        print "\ttic = %.4f < %.4f < %.4f" %(MIN_TIC, tic_value, MAX_TIC)
        print "\tview = %.4f < %.4f < %.4f" %(min_view, module_value, max_view)
        print
        i += 1
      # then check results
      if DO_TEST:
          i = 0
          for key in keys:
            module_value = view_result[key]
            tic_value = tic_result[key]
            add_value = add_result[key]
            min_view = MIN_MODULE_VIEW + LISTBOX_COEF * i
            max_view = MAX_MODULE_VIEW + LISTBOX_COEF * i
            self.assertTrue(min_view < module_value < max_view,
                            'View: %.4f < %.4f < %.4f' % (
                min_view, module_value, max_view))
            self.assertTrue(
                MIN_OBJECT_CREATION < add_value < MAX_OBJECT_CREATION,
                'Create: %.4f < %.4f < %.4f' % (
                MIN_OBJECT_CREATION, add_value, MAX_OBJECT_CREATION))
            self.assertTrue(MIN_TIC < tic_value < MAX_TIC,
                            'Tic: %.4f < %.4f < %.4f' % (
                MIN_TIC, tic_value, MAX_TIC))
            i += 1


    def test_viewProxyField(self):
      # render a form with proxy fields: Foo_viewProxyField
      foo = self.foo_module.newContent(
                           portal_type='Foo',
                           title='Bar Test',
                           quantity=10000,
                           price=32,
                           start_date=DateTime(2008,1,1))
      foo.newContent(portal_type='Foo Line',
                     title='Line 1')
      foo.newContent(portal_type='Foo Line',
                     title='Line 2')
      self.tic()
      # Check performance
      before_view = time()
      for x in xrange(100):
        foo.Foo_viewProxyField()
      after_view = time()
      req_time = (after_view - before_view)/100.

      print "time to view proxyfield form %.4f < %.4f < %.4f\n" % \
              ( MIN_OBJECT_PROXYFIELD_VIEW,
                req_time,
                MAX_OBJECT_PROXYFIELD_VIEW )
      if PROFILE:
        self.profile(foo.Foo_viewProxyField)
      if DO_TEST:
        self.assertTrue( MIN_OBJECT_PROXYFIELD_VIEW < req_time
                                    < MAX_OBJECT_PROXYFIELD_VIEW,
          '%.4f < %.4f < %.4f' % (
              MIN_OBJECT_PROXYFIELD_VIEW,
              req_time,
              MAX_OBJECT_PROXYFIELD_VIEW))

    def test_02_viewFooObjectWithManyLines(self):
      """
      Estimate average time to render object view with many lines
      """
      foo = self.foo_module.newContent(portal_type='Foo',
                                       title='Foo Test')
      for i in xrange(100):
          foo.newContent(portal_type='Foo Line',
                         title='Line %s' % i)
      self.tic()
      # Check performance
      before_view = time()
      for x in xrange(100):
        foo.Foo_viewPerformance()
      after_view = time()
      req_time = (after_view - before_view)/100.

      print "time to view object form with many lines %.4f < %.4f < %.4f\n" % \
              ( MIN_OBJECT_MANY_LINES_VIEW,
                req_time,
                MAX_OBJECT_MANY_LINES_VIEW )
      if PROFILE:
          self.profile(foo.Foo_viewPerformance)
      if DO_TEST:
        self.assertTrue( MIN_OBJECT_MANY_LINES_VIEW < req_time
                                    < MAX_OBJECT_MANY_LINES_VIEW,
          '%.4f < %.4f < %.4f' % (
              MIN_OBJECT_MANY_LINES_VIEW,
              req_time,
              MAX_OBJECT_MANY_LINES_VIEW))


class TestPropertyPerformance(TestPerformanceMixin):
  def afterSetUp(self):
    super(TestPerformanceMixin, self).afterSetUp()
    self.foo = self.portal.foo_module.newContent(
        portal_type='Foo',
        title='Foo Test',
        protected_property='Restricted Property',
    )

    # we will run the test as anonymous user. Setup permissions so that anymous can
    # get and set all properties, except `protected_property` (unless test change to another user)
    for permission in ('View', 'Access contents information', 'Modify portal content'):
      self.foo.manage_permission(permission, ['Anonymous'], 1)

    self.tic()
    self.logout()

  def _benchmark(self, nb_iterations, min_time, max_time):
    def decorated(f):
      before = time()
      for i in xrange(nb_iterations):
        f(i)
      after = time()
      total_time = (after - before) / 100.

      print ("time %s.%s %.4f < %.4f < %.4f\n" % \
              ( self.id(),
                f.__doc__ or f.__name__,
                min_time,
                total_time,
                max_time ))
      if PROFILE:
        self.profile(f, args=(i, ))
      if DO_TEST:
        self.assertTrue(
            min_time < total_time < max_time,
            '%.4f < %.4f < %.4f' %
            (min_time, total_time, max_time))
    return decorated

  def test_getProperty_protected_property_refused(self):
    getProperty = self.foo.getProperty
    self.assertRaises(Unauthorized, getProperty, 'protected_property')

    @self._benchmark(100000, 0.0001, 1)
    def getPropertyWithRestrictedPropertyRefused(_):
      getProperty('protected_property', checked_permission='Access contents information')

  def test_getProperty_protected_property_allowed(self):
    getProperty = self.foo.getProperty
    self.login()
    @self._benchmark(100000, 0.0001, 1)
    def getPropertyWithRestrictedPropertyAllowed(_):
      getProperty('protected_property', checked_permission='Access contents information')

  def test_getProperty_simple_property(self):
    getProperty = self.foo.getProperty
    @self._benchmark(100000, 0.0001, 1)
    def getPropertyWithSimpleProperty(_):
      getProperty('title', checked_permission='Access contents information')

  def test_edit_restricted_properties(self):
    _edit = self.foo.edit
    self.login()
    @self._benchmark(10000, 0.0001, 1)
    def edit(i):
      _edit(
          title=str(i),
          protected_property=str(i)
      )
