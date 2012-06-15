#(setq python-guess-indent nil)
# (setq python-indent 2)
# (setq py-indent-offset 2)
#(setq tab-width 2)
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

from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.ERP5Type.tests.utils import LogInterceptor
from App.config import getConfiguration
import os

# Define variable to chek if performance are good or not
# XXX These variable are specific to the testing environment
#     (pystone results: min: < 35373.2 - mean: ~ 35990.7 - max: > 36589.8)
# Historical values are here to remember what was original values on this
# specific testing environment. We must always try to stay below max
# historical values.
                                    # Historical values
MIN_OBJECT_VIEW=0.144               # 0.112
MAX_OBJECT_VIEW=0.147               # 0.120
MIN_OBJECT_MANY_LINES_VIEW=0.280    # 0.274
MAX_OBJECT_MANY_LINES_VIEW=0.286    # 0.294
MIN_OBJECT_PROXYFIELD_VIEW=0.213    # 0.199
MAX_OBJECT_PROXYFIELD_VIEW=0.217    # 0.220
#CURRENT_MIN_OBJECT_VIEW=0.1220
#CURRENT_MAX_OBJECT_VIEW=0.1280
MIN_MODULE_VIEW=0.148               # 0.125
MAX_MODULE_VIEW=0.153               # 0.175
MIN_TIC=0.0323                      # 0.260
MAX_TIC=0.0344                      # 0.343
MIN_OBJECT_CREATION=0.0068          # 0.0070
MAX_OBJECT_CREATION=0.0073          # 0.0082
LISTBOX_COEF=0.00173                # 0.02472
# Change history
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

# set 1 to get profiler's result (unit_test/tests/<func_name>)
PROFILE=1

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

    def beforeTearDown(self):
      # Re-enable gc at teardown.
      gc.enable()
      self.abort()
      self.bar_module.manage_delObjects(list(self.bar_module.objectIds()))
      self.foo_module.manage_delObjects(list(self.foo_module.objectIds()))
      gender = self.getPortal().portal_categories['gender']
      gender.manage_delObjects(list(gender.objectIds()))
      gender = self.getPortal().portal_caches.clearAllCache()
      self.tic()

    def checkViewBarObject(self, min, max, quiet=quiet, prefix=None):
      # Some init to display form with some value
      if prefix is None:
        prefix = ''
      gender = self.getPortal().portal_categories['gender']
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
      if not quiet:
          print "%s time to view object form %.4f < %.4f < %.4f\n" % \
              (prefix, min, req_time, max)
      if PROFILE:
          self.profile(bar.Bar_viewPerformance)
      if DO_TEST:
          self.failUnless(min < req_time < max,
                          '%.4f < %.4f < %.4f' % (min, req_time, max))

    def profile(self, func, name=None, suffix='.prof', func_args=(), func_kwargs={}):
        if name is None:
            name = func.__name__

        prof_file = '%s%s' % (name, suffix)
        try:
            os.unlink(prof_file)
        except OSError:
            pass

        from cProfile import Profile
        prof = Profile()
        prof.runcall(func, *func_args, **func_kwargs)
        prof.dump_stats(prof_file)

    def test_00_viewBarObject(self, quiet=quiet, run=run_all_test,
                              min=None, max=None):
      """
      Estimate average time to render object view
      """
      if not run : return
      if not quiet:
        message = 'Test form to view Bar object'
        LOG('Testing... ', 0, message)
      self.checkViewBarObject(MIN_OBJECT_VIEW, MAX_OBJECT_VIEW,
                              prefix='objective')

#    def test_00b_currentViewBarObject(self, quiet=quiet, run=run_all_test):
#      """
#      Estimate average time to render object view and check with current values
#      """
#      if not run : return
#      if not quiet:
#        message = 'Test form to view Bar object with current values'
#        LOG('Testing... ', 0, message)
#      self.checkViewBarObject(CURRENT_MIN_OBJECT_VIEW, CURRENT_MAX_OBJECT_VIEW,
#                              prefix='current')

    def test_01_viewBarModule(self, quiet=quiet, run=run_all_test):
      """
      Estimate average time to render module view
      """
      if not run : return
      if not quiet:
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
        if not quiet:
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
            self.failUnless(min_view < module_value < max_view,
                            'View: %.4f < %.4f < %.4f' % (
                min_view, module_value, max_view))
            self.failUnless(
                MIN_OBJECT_CREATION < add_value < MAX_OBJECT_CREATION,
                'Create: %.4f < %.4f < %.4f' % (
                MIN_OBJECT_CREATION, add_value, MAX_OBJECT_CREATION))
            self.failUnless(MIN_TIC < tic_value < MAX_TIC,
                            'Tic: %.4f < %.4f < %.4f' % (
                MIN_TIC, tic_value, MAX_TIC))
            i += 1


    def test_viewProxyField(self, quiet=quiet):
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

      if not quiet:
        print "time to view proxyfield form %.4f < %.4f < %.4f\n" % \
              ( MIN_OBJECT_PROXYFIELD_VIEW,
                req_time,
                MAX_OBJECT_PROXYFIELD_VIEW )
      if PROFILE:
        self.profile(foo.Foo_viewProxyField)
      if DO_TEST:
        self.failUnless( MIN_OBJECT_PROXYFIELD_VIEW < req_time
                                    < MAX_OBJECT_PROXYFIELD_VIEW,
          '%.4f < %.4f < %.4f' % (
              MIN_OBJECT_PROXYFIELD_VIEW,
              req_time,
              MAX_OBJECT_PROXYFIELD_VIEW))

    def test_02_viewFooObjectWithManyLines(self, quiet=quiet):
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

      if not quiet:
        print "time to view object form with many lines %.4f < %.4f < %.4f\n" % \
              ( MIN_OBJECT_MANY_LINES_VIEW,
                req_time,
                MAX_OBJECT_MANY_LINES_VIEW )
      if PROFILE:
          self.profile(foo.Foo_viewPerformance)
      if DO_TEST:
        self.failUnless( MIN_OBJECT_MANY_LINES_VIEW < req_time
                                    < MAX_OBJECT_MANY_LINES_VIEW,
          '%.4f < %.4f < %.4f' % (
              MIN_OBJECT_MANY_LINES_VIEW,
              req_time,
              MAX_OBJECT_MANY_LINES_VIEW))

    def test_03_installBusinessTemplate(self, quiet=quiet):
      """
      """
      template_tool = self.getTemplateTool()
      bt = template_tool.newContent(portal_type='Business Template')

      # Filesystem Property Sheet
      property_sheet_id_list = []
      cfg = getConfiguration()
      for i in xrange(20):
        ps_title = 'UnitTest%d' % i
        ps_data =  '''class UnitTest%i:
  """Fake property sheet for unit test"""
  _properties = ({"id": "ps_prop1", "type": "string"},)
  _categories = ()''' % i

        file_path = os.path.join(cfg.instancehome, 'PropertySheet',
                                 ps_title + '.py')

        if os.path.exists(file_path):
          os.remove(file_path)

        with file(file_path, 'w') as f:
          f.write(ps_data)

        property_sheet_id_list.append(ps_title)

      bt.edit(template_property_sheet_id_list=property_sheet_id_list)
      bt.build()
      transaction.commit()
      self.tic()

      def time_decorator(function):
        def patched(*args, **kwargs):
          before = time()
          function(*args, **kwargs)
          elapsed = time() - before

          LOG('PERFORMANCES', 0,
              'PATCHED %s, call time: %.4f' % (function, elapsed))

        return patched

      from Products.ERP5.Document.BusinessTemplate import \
          FilesystemDocumentTemplateItem, PropertySheetTemplateItem

      _resetDynamicModules = FilesystemDocumentTemplateItem._resetDynamicModules
      preinstall = PropertySheetTemplateItem.preinstall
      install = PropertySheetTemplateItem.install

      from Products.ERP5Type.Tool.TypesTool import TypesTool
      resetDynamicDocuments = TypesTool.resetDynamicDocuments

      iteration = 10
      def run():
        req_time = 0.
        try:
          FilesystemDocumentTemplateItem._resetDynamicModules = time_decorator(
              _resetDynamicModules)

          TypesTool.resetDynamicDocuments = time_decorator(
              resetDynamicDocuments)                  

          PropertySheetTemplateItem.preinstall = time_decorator(preinstall)
          PropertySheetTemplateItem.install = time_decorator(install)

          for i in xrange(0, iteration + 1):
            LOG('PERFORMANCES', 0,
                '>>>>>>>>>>>>> INSTALL (%d/%d)' % (i, iteration))

            before = time()
            object_to_update_dict = bt.preinstall()
            bt.install(force=False, object_to_update=object_to_update_dict)
            transaction.commit()
            self.tic()
            elapsed = float(time() - before)
            req_time += elapsed

            LOG('PERFORMANCES', 0,
                '<<<<<<<<<<<<< FINISHED INSTALLATION: %.4f (%d/%d)' % \
                    (elapsed, i, iteration))

            bt.uninstall()
            transaction.commit()
            self.tic()
        finally:
            FilesystemDocumentTemplateItem._resetDynamicModules = \
                _resetDynamicModules

            TypesTool.resetDynamicDocuments = resetDynamicDocuments

            PropertySheetTemplateItem.preinstall = preinstall
            PropertySheetTemplateItem.install = install

        req_time /= iteration

        if not quiet:
            print "Time to install Business Template with Filesystem " \
                "Property Sheets: %.4f" % req_time

        if PROFILE:
          if PropertySheetTemplateItem._perform_migration:
            prefix = 'zodb-'
          else:
            prefix = 'filesystem-'

          self.profile(bt.preinstall,
                       name=prefix + 'preinstall')

          self.profile(bt.install,
                       name=prefix + 'install',
                       func_kwargs={'force': True,
                                    'object_to_update': object_to_update_dict})

          self.profile(self.getPortal().portal_types.resetDynamicDocuments,
                       name=prefix + 'reset')

          transaction.commit()
          self.tic()
          bt.uninstall()

        return req_time

      try:
        PropertySheetTemplateItem._perform_migration = False
        run()
      finally:
        PropertySheetTemplateItem._perform_migration = True          

      # Migrate Property Sheets to ZODB
      bt.install(force=True)
      transaction.commit()
      self.tic()

      bt.uninstall()
      transaction.commit()
      self.tic()

      run()

    def _upgrade(self, export_path, sha_file_dict):
      portal = self.getPortal()
      template_tool = portal.portal_templates

      # Independent
      from Products import ERP5
      os.system('%s %s' % (os.path.join(ERP5.__path__[0], 'bin', 'genbt5list'),
                           export_path))

      template_tool.updateRepositoryBusinessTemplateList((export_path,))

      update_bt_list = template_tool.getUpdatedRepositoryBusinessTemplateList()
      # END

      sha_dict = {}

      from hashlib import sha1

      def callback(arg_tuple, directory, files):
        bt_sha_file_dict, file_list = arg_tuple
        for excluded_directory in ('CVS', '.svn'):
          try:
            files.remove(excluded_directory)
          except ValueError:
            pass
        for file in files:
          absolute_path = os.path.join(directory, file)
          if os.path.isfile(absolute_path):
            if absolute_path in bt_sha_file_dict:
              with open(absolute_path) as f:
                if sha1(f.read()).hexdigest() == bt_sha_file_dict[absolute_path]:
                  continue

            file_list.append(absolute_path)

      for update_bt in update_bt_list:
        # download
        repository, title = template_tool.decodeRepositoryBusinessTemplateUid(
          update_bt.getUid())

        installed_bt = template_tool.getInstalledBusinessTemplate(title=title)

        clone, = template_tool.manage_pasteObjects(
          template_tool.manage_copyObjects(ids=[installed_bt.getId()]))

        bt = template_tool[clone['new_id']]

        bt_title = bt.getTitle()
        path = os.path.join(export_path, bt_title)
        file_list = []
        os.path.walk(path, callback, (sha_file_dict[bt_title], file_list))
        file_list.sort()

#        import pdb; pdb.set_trace()
        bt.importFile(dir=True, file=file_list, root_path=path)
        bt.build(no_action=True)

      transaction.commit()
      self.tic()

    def test_04_upgradeBusinessTemplate(self, quiet=quiet):
      portal = self.getPortal()
      template_tool = portal.portal_templates
      property_sheet_tool = portal.portal_property_sheets

      # Create dummy property sheets
      bt_dict = {}
      for i in range(1): # XXX: 20
        bt_title = 'test_performance_%d' % i

        property_sheet_path_list = []
        for j in range(10): # XXX: 10
          clone, = property_sheet_tool.manage_pasteObjects(
            property_sheet_tool.manage_copyObjects(ids=['DublinCore']))

          property_sheet = property_sheet_tool[clone['new_id']]
          property_sheet_id = '%s_%d' % (bt_title, j)
          property_sheet.setId(property_sheet_id)
          property_sheet_path_list.append('portal_property_sheets/%s' % \
                                          property_sheet_id)

        bt = template_tool.newContent(
          title=bt_title,
          portal_type='Business Template',
          template_property_sheet_id_list=property_sheet_path_list)

        bt.build()
        bt.install(force=True)
        transaction.commit()
        self.tic()

        bt_dict[bt_title] = {'bt': bt,
                             'property_sheet_path_list': property_sheet_path_list}

      from App.config import getConfiguration
      export_path = os.path.join(getConfiguration().instancehome,
                                 'var', 'upgradeBusinessTemplate')

      if os.path.exists(export_path):
        import shutil
        shutil.rmtree(export_path)

      os.makedirs(export_path)

      sha_dict = {}
      sha_file_dict = {}
      for title, d in bt_dict.iteritems():
        bt_sha_dict = {}
        bt_sha_file_dict = {}

        d['bt'].export(path=os.path.join(export_path, title), local=True,
                       sha_dict=bt_sha_dict,
                       sha_file_dict=bt_sha_file_dict)

        sha_dict[title] = bt_sha_dict
        sha_file_dict[title] = bt_sha_file_dict

      def run():
        for d in bt_dict.itervalues():
          bt = d['bt']
          property_sheet_path_list = d['property_sheet_path_list']

          clone, = template_tool.manage_pasteObjects(
            template_tool.manage_copyObjects(ids=[bt.getId()]))

          bt = template_tool[clone['new_id']]

          for index, name in enumerate(('short_title_property',
                                        'contributor_property',
                                        'right_property')):
            property_sheet = portal.unrestrictedTraverse(
              property_sheet_path_list[index])

            getattr(property_sheet, name).setPropertyDefault("python: ('foo',)")

          property_sheet = portal.unrestrictedTraverse(
            property_sheet_path_list[index + 1])

          property_sheet.deleteContent('title_property')

          transaction.commit()
          self.tic()

          bt.build()
          bt.install(force=False, with_sha=True, object_to_update=bt.preinstall())
          transaction.commit()
          self.tic()

          with open(os.path.join(export_path, bt.getTitle(),
                                 'bt', 'revision'), 'w') as f:
            f.write(str(int(bt.getRevision()) + 1))

        self._upgrade(export_path, sha_file_dict)
#        import pdb; pdb.set_trace()

        from Products import ERP5
        os.system('%s %s' % (os.path.join(ERP5.__path__[0], 'bin', 'genbt5list'),
                             export_path))

        template_tool.updateRepositoryBusinessTemplateList((export_path,))

        update_bt_list = template_tool.getUpdatedRepositoryBusinessTemplateList()

        install_bt_list = []
        for update_bt in update_bt_list:
          repository_id_tuple = template_tool.decodeRepositoryBusinessTemplateUid(
            update_bt.getUid())

          begin = time()
          bt = template_tool.download(os.path.join(*repository_id_tuple))
          print "DOWNLOAD: %.4f" % (time() - begin)

          install_bt_list.append(bt)

        begin = time()
        transaction.commit()
        self.tic()
        print "COMMIT: %.4f" % (time() - begin)

        full_begin = time()
        end_preinstall = end_install = 0.
        for bt in install_bt_list:
          begin = time()
          object_to_update_dict = bt.preinstall(sha_dict=sha_dict[bt.getTitle()])
          end = time() - begin
          print "PREINSTALL: %.4f" % end
          end_preinstall += end

#          assert object_to_update_dict == bt.preinstall()

          begin = time()
          bt.install(force=False, object_to_update=object_to_update_dict)
          end = time() - begin
          print "INSTALL: %.4f" % end
          end_install += end

          bt_dict[bt.getTitle()]['bt'] = bt

        begin = time()
        transaction.commit()
        self.tic()
        print "COMMIT: %.4f" % (time() - begin)

        full_end = time() - full_begin

        print "===> TOTAL PREINSTALL: %.4f (AVG=%.4f)" % \
            (end_preinstall, end_preinstall / len(install_bt_list))

        print "===> TOTAL INSTALL: %.4f (AVG=%.4f)" % \
            (end_install, end_install / len(install_bt_list))

        print "===> TOTAL: %.4f (AVG=%.4f)" % (full_end,
                                               full_end / len(install_bt_list))

#        import pdb; pdb.set_trace()
        # operation_log = template_tool.installBusinessTemplateListFromRepository(
        #   update_bt_list)

      run()

    def test_05_fastUpgradeBusinessTemplate(self, quiet=quiet):
      portal = self.getPortal()
      template_tool = portal.portal_templates
      property_sheet_tool = portal.portal_property_sheets

      from Products.ERP5Type.Globals import PersistentMapping
      import OFS.XMLExportImport
      from hashlib import sha1
      from StringIO import StringIO
      def generateShaForInstalledBusinessTemplate(bt):
          """
          UGUU

          XXX: moved to install()
          XXX: object_to_update?
          """
          bt._sha_file_dict = PersistentMapping()
          for path, obj in bt._property_sheet_item._objects.iteritems():
              f = StringIO()
              OFS.XMLExportImport.exportXML(obj._p_jar, obj._p_oid, f)
              bt._sha_file_dict[os.path.join('PropertySheetTemplateItem',
                                             path)] = sha1(f.getvalue()).hexdigest()

      # Create dummy property sheets
      bt_dict = {}
      for i in range(1): # XXX: 20
        bt_title = 'test_performance_%d' % i

        property_sheet_path_list = []
        for j in range(10): # XXX: 10
          clone, = property_sheet_tool.manage_pasteObjects(
            property_sheet_tool.manage_copyObjects(ids=['DublinCore']))

          property_sheet = property_sheet_tool[clone['new_id']]
          property_sheet_id = '%s_%d' % (bt_title, j)
          property_sheet.setId(property_sheet_id)
          property_sheet_path_list.append('portal_property_sheets/%s' % \
                                          property_sheet_id)

        bt = template_tool.newContent(
          title=bt_title,
          portal_type='Business Template',
          template_property_sheet_id_list=property_sheet_path_list)

        bt.build()
        bt.install(force=True)
        # B-UGUU
        generateShaForInstalledBusinessTemplate(bt)
        # E-UGUU
        transaction.commit()
        self.tic()

        bt_dict[bt_title] = {'bt': bt,
                             'property_sheet_path_list': property_sheet_path_list}

      from App.config import getConfiguration
      export_path = os.path.join(getConfiguration().instancehome,
                                 'var', 'upgradeBusinessTemplate')

      if os.path.exists(export_path):
        import shutil
        shutil.rmtree(export_path)

      os.makedirs(export_path)

      # B-UGUU
      from hashlib import sha1
      def callback(arg_tuple, directory, files):
        export_path, sha_dict = arg_tuple
        for excluded_directory in ('CVS', '.svn'):
          try:
            files.remove(excluded_directory)
          except ValueError:
            pass
        for file in files:
          absolute_path = os.path.join(directory, file)
          if os.path.isfile(absolute_path):
            key = absolute_path[len(export_path) + 1:]
            key = key.rsplit('.', 1)[0]
            if key.startswith('bt/'):
              continue            

            with open(absolute_path) as f:
              sha_dict[key] = sha1(f.read()).hexdigest()
      # E-UGUU

      filesystem_sha_dict = {}
      filesystem_property_dict = {}
      for title, d in bt_dict.iteritems():
        bt_path = os.path.join(export_path, title)
        d['bt'].export(path=bt_path, local=True)

        # B-UGUU
        os.path.walk(bt_path, callback,
                     (bt_path, filesystem_sha_dict.setdefault(title, {})))

        filesystem_property_dict[title] = bt.propertyMap()
        # E-UGUU

      def run():
        for d in bt_dict.itervalues():
          bt = d['bt']
          property_sheet_path_list = d['property_sheet_path_list']

          clone, = template_tool.manage_pasteObjects(
            template_tool.manage_copyObjects(ids=[bt.getId()]))

          bt = template_tool[clone['new_id']]

          for index, name in enumerate(('short_title_property',
                                        'contributor_property',
                                        'right_property')):
            property_sheet = portal.unrestrictedTraverse(
              property_sheet_path_list[index])

            getattr(property_sheet, name).setPropertyDefault("python: ('foo',)")

          property_sheet = portal.unrestrictedTraverse(
            property_sheet_path_list[index + 1])

          property_sheet.deleteContent('title_property')

          transaction.commit()
          self.tic()

          bt.build()
          object_to_update_dict = bt.preinstall()
          bt.install(force=False, object_to_update=object_to_update_dict)
          # B-UGUU: could be optimized by computing the hash of modified
          # objects only
          generateShaForInstalledBusinessTemplate(bt)
          # E-UGUU
          transaction.commit()
          self.tic()

          with open(os.path.join(export_path, bt.getTitle(),
                                 'bt', 'revision'), 'w') as f:
            f.write(str(int(bt.getRevision()) + 1))

        from Products import ERP5
        os.system('%s %s' % (os.path.join(ERP5.__path__[0], 'bin', 'genbt5list'),
                             export_path))

        template_tool.updateRepositoryBusinessTemplateList((export_path,))

        update_bt_list = template_tool.getUpdatedRepositoryBusinessTemplateList()

        bt_object_to_update_dict = {}
        install_bt_list = []
        for update_bt in update_bt_list:
          repository_id_tuple = template_tool.decodeRepositoryBusinessTemplateUid(
            update_bt.getUid())

          begin = time()
          # B-UGUU
          path, title = repository_id_tuple
          bt = template_tool.download(
            os.path.join(path, title),
            filesystem_sha_dict=filesystem_sha_dict[title],
            object_to_update_dict=bt_object_to_update_dict.setdefault(title, {}))

#          import pdb; pdb.set_trace()
          # E-UGUU
          print "DOWNLOAD: %.4f" % (time() - begin)
          install_bt_list.append(bt)

        begin = time()
        transaction.commit()
        self.tic()
        print "COMMIT: %.4f" % (time() - begin)

        full_begin = time()
        end_preinstall = end_install = 0.
        for bt in install_bt_list:
          print "====> %r" % bt.preinstall()

          # # begin = time()
          # # object_to_update_dict = bt.preinstall(sha_dict=sha_dict[bt.getTitle()])
          # # end = time() - begin
          # # print "PREINSTALL: %.4f" % end
          # # end_preinstall += end

#          assert object_to_update_dict == bt.preinstall()

          begin = time()
          title = bt.getTitle()


          self.profile(bt.install,
                       name='testPerformanceInstall' + title,
                       func_kwargs={'force': True,
                                    'object_to_update': bt_object_to_update_dict[title]})

#          self.profile(bt.install(force=False, object_to_update=bt_object_to_update_dict[title])
          end = time() - begin
          print "INSTALL: %.4f" % end
          end_install += end

          bt_dict[title]['bt'] = bt

        begin = time()
        transaction.commit()
        self.tic()
        print "COMMIT: %.4f" % (time() - begin)

        full_end = time() - full_begin

        print "===> TOTAL INSTALL: %.4f (AVG=%.4f)" % \
            (end_install, end_install / len(install_bt_list))

        print "===> TOTAL: %.4f (AVG=%.4f)" % (full_end,
                                               full_end / len(install_bt_list))

        # import pdb; pdb.set_trace()
        # operation_log = template_tool.installBusinessTemplateListFromRepository(
        #   update_bt_list)

      run()
#      import pdb; pdb.set_trace()


    def test_06_WTFFastUpgradeBusinessTemplate(self, quiet=quiet):
      portal = self.getPortal()
      template_tool = portal.portal_templates
      property_sheet_tool = portal.portal_property_sheets

      from Products.ERP5Type.Globals import PersistentMapping
      import OFS.XMLExportImport
      from hashlib import sha1
      from StringIO import StringIO
      def generateShaForInstalledBusinessTemplate(bt):
          """
          UGUU

          XXX: moved to install()
          XXX: object_to_update?
          """
          bt._sha_file_dict = PersistentMapping()
          for path, obj in bt._property_sheet_item._objects.iteritems():
              f = StringIO()
              OFS.XMLExportImport.exportXML(obj._p_jar, obj._p_oid, f)
              bt._sha_file_dict[os.path.join('PropertySheetTemplateItem',
                                             path)] = sha1(f.getvalue()).hexdigest()

      # Create dummy property sheets
      bt_dict = {}
      for i in range(1): # XXX: 20
        bt_title = 'test_performance_%d' % i

        property_sheet_path_list = []
        for j in range(10): # XXX: 10
          clone, = property_sheet_tool.manage_pasteObjects(
            property_sheet_tool.manage_copyObjects(ids=['DublinCore']))

          property_sheet = property_sheet_tool[clone['new_id']]
          property_sheet_id = '%s_%d' % (bt_title, j)
          property_sheet.setId(property_sheet_id)
          property_sheet_path_list.append('portal_property_sheets/%s' % \
                                          property_sheet_id)

        bt = template_tool.newContent(
          title=bt_title,
          portal_type='Business Template',
          template_property_sheet_id_list=property_sheet_path_list)

        bt.build()
        bt.install(force=True)
        # B-UGUU
        generateShaForInstalledBusinessTemplate(bt)
        # E-UGUU
        transaction.commit()
        self.tic()

        bt_dict[bt_title] = {'bt': bt,
                             'property_sheet_path_list': property_sheet_path_list}

      from App.config import getConfiguration
      export_path = os.path.join(getConfiguration().instancehome,
                                 'var', 'upgradeBusinessTemplate')

      if os.path.exists(export_path):
        import shutil
        shutil.rmtree(export_path)

      os.makedirs(export_path)

      # B-UGUU
      from hashlib import sha1
      def callback(arg_tuple, directory, files):
        export_path, sha_dict = arg_tuple
        for excluded_directory in ('CVS', '.svn'):
          try:
            files.remove(excluded_directory)
          except ValueError:
            pass
        for file in files:
          absolute_path = os.path.join(directory, file)
          if os.path.isfile(absolute_path):
            key = absolute_path[len(export_path) + 1:]
            key = key.rsplit('.', 1)[0]
            if key.startswith('bt/'):
              continue            

            with open(absolute_path) as f:
              sha_dict[key] = sha1(f.read()).hexdigest()
      # E-UGUU

      filesystem_sha_dict = {}
      filesystem_property_dict = {}
      for title, d in bt_dict.iteritems():
        bt_path = os.path.join(export_path, title)
        d['bt'].export(path=bt_path, local=True)

        # B-UGUU
        os.path.walk(bt_path, callback,
                     (bt_path, filesystem_sha_dict.setdefault(title, {})))

        filesystem_property_dict[title] = bt.propertyMap()
        # E-UGUU

      def run():
        for d in bt_dict.itervalues():
          bt = d['bt']
          property_sheet_path_list = d['property_sheet_path_list']

          clone, = template_tool.manage_pasteObjects(
            template_tool.manage_copyObjects(ids=[bt.getId()]))

          bt = template_tool[clone['new_id']]

          for index, name in enumerate(('short_title_property',
                                        'contributor_property',
                                        'right_property')):
            property_sheet = portal.unrestrictedTraverse(
              property_sheet_path_list[index])

            getattr(property_sheet, name).setPropertyDefault("python: ('foo',)")

          property_sheet = portal.unrestrictedTraverse(
            property_sheet_path_list[index + 1])

          property_sheet.deleteContent('title_property')

          transaction.commit()
          self.tic()

          bt.build()
          object_to_update_dict = bt.preinstall()
          bt.install(force=False, object_to_update=object_to_update_dict)
          # B-UGUU: could be optimized by computing the hash of modified
          # objects only
          generateShaForInstalledBusinessTemplate(bt)
          # E-UGUU
          transaction.commit()
          self.tic()

          with open(os.path.join(export_path, bt.getTitle(),
                                 'bt', 'revision'), 'w') as f:
            f.write(str(int(bt.getRevision()) + 1))

        from Products import ERP5
        os.system('%s %s' % (os.path.join(ERP5.__path__[0], 'bin', 'genbt5list'),
                             export_path))

        template_tool.updateRepositoryBusinessTemplateList((export_path,))
        import pdb; pdb.set_trace()
        update_bt_list = template_tool.getUpdatedRepositoryBusinessTemplateList()

        bt_object_to_update_dict = {}
        install_bt_list = []
        for update_bt in update_bt_list:
          repository_id_tuple = template_tool.decodeRepositoryBusinessTemplateUid(
            update_bt.getUid())

          begin = time()
          # B-UGUU
          path, title = repository_id_tuple
          bt = template_tool.download(
            os.path.join(path, title),
            filesystem_sha_dict=filesystem_sha_dict[title],
            object_to_update_dict=bt_object_to_update_dict.setdefault(title, {}))

#          import pdb; pdb.set_trace()
          # E-UGUU
          print "DOWNLOAD: %.4f" % (time() - begin)
          install_bt_list.append(bt)

        begin = time()
        transaction.commit()
        self.tic()
        print "COMMIT: %.4f" % (time() - begin)

        full_begin = time()
        end_preinstall = end_install = 0.
        for bt in install_bt_list:
          print "====> %r" % bt.preinstall()

          # # begin = time()
          # # object_to_update_dict = bt.preinstall(sha_dict=sha_dict[bt.getTitle()])
          # # end = time() - begin
          # # print "PREINSTALL: %.4f" % end
          # # end_preinstall += end

#          assert object_to_update_dict == bt.preinstall()

          begin = time()
          title = bt.getTitle()


          self.profile(bt.install,
                       name='testPerformanceInstall' + title,
                       func_kwargs={'force': True,
                                    'object_to_update': bt_object_to_update_dict[title]})

#          self.profile(bt.install(force=False, object_to_update=bt_object_to_update_dict[title])
          end = time() - begin
          print "INSTALL: %.4f" % end
          end_install += end

          bt_dict[title]['bt'] = bt

        begin = time()
        transaction.commit()
        self.tic()
        print "COMMIT: %.4f" % (time() - begin)

        full_end = time() - full_begin

        print "===> TOTAL INSTALL: %.4f (AVG=%.4f)" % \
            (end_install, end_install / len(install_bt_list))

        print "===> TOTAL: %.4f (AVG=%.4f)" % (full_end,
                                               full_end / len(install_bt_list))

        # import pdb; pdb.set_trace()
        # operation_log = template_tool.installBusinessTemplateListFromRepository(
        #   update_bt_list)

      run()
#      import pdb; pdb.set_trace()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPerformance))
  return suite
