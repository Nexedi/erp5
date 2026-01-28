# -*- coding: utf-8 -*-
from glob import glob
import os, subprocess, re
# test_suite is provided by 'run_test_suite'
from test_suite import ERP5TypeTestSuite
import sys
import six
from itertools import chain

HERE = os.path.dirname(__file__)

class _Base(ERP5TypeTestSuite):
  realtime_output = False
  enabled_product_list = ('CMFActivity', 'CMFCategory', 'ERP5', 'ERP5Catalog',
                          'ERP5Form',
                          'ERP5OOo', 'ERP5Security', 'ERP5Type',
                          'Formulator', 'ERP5Workflow',
                          'HBTreeFolder2', 'MailTemplates',
                          'PortalTransforms', 'TimerService',
                          'ZMySQLDA', 'ZSQLCatalog', 'Zelenium')

  def enableProducts(self):
    product_set = set(self.enabled_product_list)
    try:
      dir_set = set(os.walk('Products').next()[1])
      for product in dir_set - product_set:
        os.unlink(os.path.join('Products', product))
      product_set -= dir_set
    except StopIteration:
      os.mkdir('Products')
    for product in product_set:
      os.symlink(os.path.join('..', 'products', product),
                 os.path.join('Products', product))

  def _getAllTestList(self):
    test_list = []
    path = "%s/../" % HERE
    component_re = re.compile(".*/([^/]+)/TestTemplateItem/portal_components"
                              "/test\.[^.]+\.([^.]+).py$")
    for test_path in chain(
        #glob(path + '/product/*/tests/test*.py'),
        glob(path + '/bt5/erp5_core_test/TestTemplateItem/test*.py'),
        glob(path + '/bt5/erp5_core_test/TestTemplateItem/portal_components/test.*.test*.py')):
      component_re_match = component_re.match(test_path)
      if component_re_match is not None:
        test_case = "%s:%s" % (component_re_match.group(1),
                               component_re_match.group(2))
      else:
        test_case = test_path.split(os.sep)[-1][:-3] # remove .py
      if six.PY3:
        # disable tests that are not compatible with Python 3.
        if test_case in (
          # using legacy workflow
          'erp5_workflow_test:testWorkflowAndDCWorkflow',
          'testUpgradeInstanceWithOldDataFsLegacyWorkflow'
        ):
          continue
      product = test_path.split(os.sep)[-3]
      # don't test 3rd party products
      if product in ('PortalTransforms', 'MailTemplates', 'Zelenium'):
        continue
      test_list.append(test_case)
    return test_list

  def update(self):
    self.checkout('products', 'bt5')
    self.enableProducts()

  def _updateFunctionalTestResponse(self, status_dict):
    """ Convert the Unit Test output into more accurate information
        related to functional test run.
    """
    # Parse relevant information to update response information
    try:
      summary, html_test_result = status_dict['stderr'].split(b"-"*79)[1:3]
    except ValueError:
      # In case of error when parse the file, preserve the original
      # information. This prevents we have unfinished tests.
      return status_dict
    status_dict['html_test_result'] = html_test_result
    search = self.FTEST_PASS_FAIL_RE.search(summary.decode())
    if search:
      group_dict = search.groupdict()
      status_dict['failure_count'] = int(group_dict['failures']) \
          or int(status_dict.get('failure_count', 0))
      status_dict['test_count'] = int(group_dict['total'])
      status_dict['skip_count'] = int(group_dict['expected_failure'])
    return status_dict


class _ERP5(_Base):
  def _getAllTestList(self):
    all_test_list = super(_ERP5, self)._getAllTestList()
    return [x for x in all_test_list if ('wendelin' not in x.lower()) and ('mqtt' not in x.lower())]

class PERF(_ERP5):

  def getTestList(self):
    return [x for x in self._getAllTestList() if x.find('Performance')>0]

class CloudPERF(_ERP5):

  def getTestList(self):
    return ['_testPystone', '_testSQLBench']

class ERP5(_ERP5):
  mysql_db_count = 3

  def getTestList(self):
    test_list = []
    for full_test_case in self._getAllTestList():
      test_case = (':' in full_test_case and full_test_case.split(':')[1]
                   or full_test_case)

      # skip some tests
      if test_case.find('Performance') > 0:
        continue
      test_list.append(full_test_case)
    return test_list

  def run(self, full_test):
    test = ':' in full_test and full_test.split(':')[1] or full_test
    if test in ('testConflictResolution', 'testInvalidationBug'):
      status_dict = self.runUnitTest('--save', full_test)
      if not status_dict['status_code']:
        status_dict = self.runUnitTest('--load', '--activity_node=2', full_test)
      return status_dict
    elif test.startswith('testFunctional'):
      return self._updateFunctionalTestResponse(self.runUnitTest(full_test))
    elif test.startswith('testUpgradeInstanceWithOldDataFs'):
      old_data_path = None
      for path in sys.path:
        if path.endswith('/erp5-bin'):
          old_data_path = os.path.join(path, 'test_data', test)
          if not os.path.isdir(old_data_path):
            return dict(
              status_code=-1,
              test_count=1,
              failure_count=1,
              stderr='%s does not exist or is not a directory' % old_data_path)

          break
      else:
        return dict(
          status_code=-1,
          test_count=1,
          failure_count=1,
          stderr='erp5-bin repository not found in %s' % '\n'.join(sys.path))

      instance_home = (self.instance and 'unit_test.%u' % self.instance
                       or 'unit_test')

      import shutil
      shutil.rmtree(instance_home, ignore_errors=True)

      os.makedirs(os.path.join(instance_home, 'var'))
      shutil.copyfile(os.path.join(old_data_path, 'Data.fs'),
                      os.path.join(instance_home, 'var', 'Data.fs'))
      shutil.copyfile(os.path.join(old_data_path, 'dump.sql'),
                      os.path.join(instance_home, 'dump.sql'))

      return self.runUnitTest(
          '--load',
          '--portal_id=erp5',
          '--enable_full_indexing=portal_types,portal_property_sheets',
          full_test)

    return super(ERP5, self).run(full_test)

class WORKFLOW(ERP5):
  # new test suite running a few test related to Workflow
  # (to be used instead of ERP5 class, which run all tests)
  def getTestList(self):
    return ['testERP5Workflow', 'testERP5Type', 'testInteractionWorkflow',
      'erp5_core_test:testSQLCachedWorklist', 'erp5_core_test:testWorklist',
      'erp5_workflow_test:testWorkflowAndDCWorkflow', 'testERP5Simulation',
      'testDmsWithPreConversion', 'testERP5BankingCashInventory',
      'testInventoryModule', 'testPackingList', 'testBase',
      'testERP5BankingUsualCashTransfer']


class ERP5_simulation(_ERP5):

  def getTestList(self):
    p = subprocess.Popen(('grep', '-lr', '--include=test*.py',
                          '-e', '@newSimulationExpectedFailure',
                          '-e', 'erp5_report_new_simulation_failures',
                          'Products/ERP5/tests'),
                         stdout=subprocess.PIPE)
    return sorted(os.path.basename(x)[:-3]
                  for x in p.communicate()[0].splitlines())

  def runUnitTest(self, *args, **kw):
    return super(ERP5_simulation, self).runUnitTest(
      erp5_report_new_simulation_failures='1', *args, **kw)

class ERP5_scalability(_ERP5):

  def getTestList(self):
    return ['createPerson', 'createSaleOrder', 'createWebPage']

  def getTestPath(self):
    return 'erp5/util/benchmark/examples/'

  def getUsersFilePath(self):
    return 'erp5/util/benchmark/examples/scalabilityUsers'

  def getUserNumber(self, test_number):
    return [45, 135, 170, 220, 250][test_number]

  # Test duration in seconds
  def getTestDuration(self, test_number):
    return 60*10

  def getTestRepetition(self, test_number):
    return 3

class ERP5_XHTML_Only(_ERP5):

  def _getAllTestList(self):
    path = sys.path[0]
    return ['%s/product/ERP5/tests/testXHTML.py' % path]

class FunctionalTests(ERP5):

  def _getAllTestList(self):
    return [x for x in super(FunctionalTests, self)._getAllTestList()
      if x.startswith('testFunctional') or ':testFunctional' in x]


class _BusinessTemplateCodingStyleTestSuite(_Base):
  """Run coding style test on all business templates.
  """
  def getTestList(self):
    def skip_business_template(path):
      # we skip coding style check for business templates having this marker
      # property. Since the property is not exported (on purpose), modified business templates
      # will be candidate for coding style test again.
      if os.path.exists(path + '/bt/skip_coding_style_test'):
        return True
      if six.PY3 and os.path.basename(path) in (
          'erp5_workflow_test',  # uses legacy DCWorkflow
        ):
          return True
      return False

    test_list = [
      os.path.basename(path)
      for path in chain(
        glob(HERE + '/../bt5/*'),
        glob(HERE + '/../product/ERP5/bootstrap/*'))
      if os.path.isdir(path) and not skip_business_template(path)
    ]
    for path in chain(glob(HERE + '/../product/*'),
                      glob(HERE + '/../bt5')):
      if not os.path.exists(path + '/skip_coding_style_test') and os.path.isdir(path):
        test_list.append("Python3Style." + os.path.basename(path))
    return test_list

  def run(self, full_test):
    if full_test.startswith("Python3Style."):
      return self.runUnitTest('Python3StyleTest', TESTED_PRODUCT=full_test[13:])
    return self.runUnitTest('CodingStyleTest', TESTED_BUSINESS_TEMPLATE=full_test)

  def getLogDirectoryPath(self, *args, **kw):
    log_directory = os.path.join(
        self.log_directory,
        args[-1] + '-' + (kw.get('TESTED_BUSINESS_TEMPLATE') or kw['TESTED_PRODUCT']))
    os.mkdir(log_directory)
    return log_directory

class ERP5BusinessTemplateCodingStyleTestSuite(_BusinessTemplateCodingStyleTestSuite):
  def getTestList(self):
    all_test_list = super(ERP5BusinessTemplateCodingStyleTestSuite, self).getTestList()
    return [x for x in all_test_list if ('wendelin' not in x.lower()) and ('mqtt' not in x.lower())]



class ReExportERP5BusinessTemplateTestSuite(ERP5TypeTestSuite):

  def getTestList(self):
    return sorted([
        os.path.basename(path)
        for path in chain(
            glob(HERE + '/../bt5/*'),
            glob(HERE + '/../product/ERP5/bootstrap/*'))
        if not os.path.exists(path + '/bt/skip_coding_style_test') and os.path.isdir(path)
    ])

  def run(self, full_test):
    return self.runUnitTest(
        '--portal_id=erp5',
        'ReExportBusinessTemplate',
        RE_EXPORT_BUSINESS_TEMPLATE=full_test)


class RJS_Only(_ERP5):
  def getTestList(self):
    rjs_officejs_bt_list = ["erp5_officejs_",
                            "renderjs_ui_test",
                            "erp5_monaco_editor_ui_test",
                            "erp5_travel_expense_ui_test",
                            "erp5_gadget_interface_validator_ui_test",
                            "erp5_hal_json_style"]
    return [test for test in self._getAllTestList() if any(test.find(bt)>-1 for bt in rjs_officejs_bt_list)]


class WendelinERP5(_Base):

  def getTestList(self):
    all_test_list = self._getAllTestList()
    print(all_test_list)
    all_test_list =  [x for x in all_test_list if ('wendelin' in x.lower()) or ('mqtt' in x.lower())]
    return [x for x in all_test_list if  "WendelinTelecom" not in x]

  def run(self, full_test):
    test = ':' in full_test and full_test.split(':')[1] or full_test
    # from https://lab.nexedi.com/nexedi/erp5/commit/530e8b4e:
    # ---- 8< ----
    #   Combining Zope and WCFS working together requires data to be on a real
    #   storage, not on in-RAM MappingStorage inside Zope's Python process.
    #   Force this via --load --save for now.
    #
    #   Also manually indicate via --with_wendelin_core, that this test needs
    #   WCFS server - corresponding to ZODB test storage - to be launched.
    #
    #   In the future we might want to rework custom_zodb.py to always use
    #   FileStorage on tmpfs instead of δ=MappingStorage in DemoStorage(..., δ),
    #   and to always spawn WCFS for all tests, so that this hack becomes
    #   unnecessary.
    # ---- 8< ----
    # Always run configurator test from scratch
    # The load&save mechanism will load previous test data if it's present
    # If test node run configurator A test, then run configurator B test
    # It will then load the data created by A to run B
    if 'Configurator' not in test:
      status_dict = self.runUnitTest('--load', '--save', '--with_wendelin_core', full_test)
    else:
      status_dict = self.runUnitTest(full_test)
    if test.startswith('testFunctional'):
      status_dict = self._updateFunctionalTestResponse(status_dict)
    return status_dict

class WendelinTelecomERP5(WendelinERP5):
  def getTestList(self):
    all_test_list = self._getAllTestList()
    print(all_test_list)
    all_test_list =  [x for x in all_test_list if ('wendelin' in x.lower()) or ('mqtt' in x.lower())]
    return [x for x in all_test_list if  "WendelinTelecom" in x]

class WendelinBusinessTemplateCodingStyleTestSuite(_BusinessTemplateCodingStyleTestSuite):
  def getTestList(self):
    all_test_list = super(WendelinBusinessTemplateCodingStyleTestSuite, self).getTestList()
    all_test_list =  [x for x in all_test_list if ('wendelin' in x.lower()) or ('mqtt' in x.lower())]
    return [x for x in all_test_list if 'wendelin_telecom' not in x]


class WendelinTelecomBusinessTemplateCodingStyleTestSuite(_BusinessTemplateCodingStyleTestSuite):
  def getTestList(self):
    all_test_list = super(WendelinTelecomBusinessTemplateCodingStyleTestSuite, self).getTestList()
    all_test_list =  [x for x in all_test_list if ('wendelin' in x.lower()) or ('mqtt' in x.lower())]
    return [x for x in all_test_list if 'wendelin_telecom' in x]
