from glob import glob
import os, subprocess, re
# test_suite is provided by 'run_test_suite'
from test_suite import ERP5TypeTestSuite
import sys

HERE = os.path.dirname(__file__)

class _ERP5(ERP5TypeTestSuite):
  realtime_output = False
  enabled_product_list = ('CMFActivity', 'CMFCategory', 'ERP5', 'ERP5Catalog',
                          'ERP5Form',
                          'ERP5OOo', 'ERP5Security', 'ERP5Type',
                          'Formulator', 'ERP5Workflow',
                          'HBTreeFolder2', 'MailTemplates',
                          'PortalTransforms', 'TimerService', 'ZLDAPConnection', 
                          'ZLDAPMethods', 'ZMySQLDA', 'ZSQLCatalog', 'Zelenium')

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
    for test_path in (
        glob('%s/product/*/tests/test*.py' % path) +
        glob('%s/bt5/*/TestTemplateItem/test*.py' % path) +
        glob('%s/bt5/*/TestTemplateItem/portal_components/test.*.test*.py' % path)):
      component_re_match = component_re.match(test_path)
      if component_re_match is not None:
        test_case = "%s:%s" % (component_re_match.group(1),
                               component_re_match.group(2))
      else:
        test_case = test_path.split(os.sep)[-1][:-3] # remove .py
      product = test_path.split(os.sep)[-3]
      # don't test 3rd party products
      if product in ('PortalTransforms', 'MailTemplates', 'Zelenium'):
        continue
      test_list.append(test_case)
    return test_list

  def update(self):
    self.checkout('products', 'bt5')
    self.enableProducts()


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
    elif test == 'testUpgradeInstanceWithOldDataFs':
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

  def _updateFunctionalTestResponse(self, status_dict):
    """ Convert the Unit Test output into more accurate information
        related to funcional test run.
    """
    # Parse relevant information to update response information
    try:
      summary, html_test_result = status_dict['stderr'].split("-"*79)[1:3]
    except ValueError:
      # In case of error when parse the file, preserve the original
      # informations. This prevents we have unfinished tests.
      return status_dict
    status_dict['html_test_result'] = html_test_result
    search = self.FTEST_PASS_FAIL_RE.search(summary)
    if search:
      group_dict = search.groupdict()
      status_dict['failure_count'] = int(group_dict['failures'])
      status_dict['test_count'] = int(group_dict['total'])
      status_dict['skip_count'] = int(group_dict['expected_failure'])
    return status_dict

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


class ERP5BusinessTemplateCodingStyleTestSuite(_ERP5):
  """Run coding style test on all business templates.
  """
  def getTestList(self):
    test_list = []
    for business_template_path in (
            glob('%s/../bt5/*' % HERE)
            + glob('%s/../product/ERP5/bootstrap/*' % HERE)):
      # we skip coding style check for business templates having this marker
      # property. Since the property is not exported (on purpose), modified business templates
      # will be candidate for coding style test again.
      if os.path.isdir(business_template_path) and \
              not os.path.exists(os.path.join(business_template_path, 'bt/skip_coding_style_test')):
        test_list.append(os.path.basename(business_template_path))
    return test_list

  def run(self, full_test):
    return self.runUnitTest('CodingStyleTest', TESTED_BUSINESS_TEMPLATE=full_test)

  def getLogDirectoryPath(self, *args, **kw):
    log_directory = os.path.join(
        self.log_directory,
        '{}-{}'.format(args[-1] , kw['TESTED_BUSINESS_TEMPLATE']))
    os.mkdir(log_directory)
    return log_directory


class RJS_Only(_ERP5):
  def getTestList(self):
    rjs_officejs_bt_list = ["erp5_officejs_",
                            "renderjs_ui_test",
                            "erp5_monaco_editor_ui_test",
                            "erp5_travel_expense_ui_test",
                            "erp5_gadget_interface_validator_ui_test",
                            "erp5_hal_json_style"]
    return [test for test in self._getAllTestList() if any(test.find(bt)>-1 for bt in rjs_officejs_bt_list)]