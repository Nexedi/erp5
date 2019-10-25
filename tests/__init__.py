from glob import glob
import os, subprocess, re
# test_suite is provided by 'run_test_suite'
from test_suite import SavedTestSuite
import sys

HERE = os.path.dirname(__file__)

class _ERP5(SavedTestSuite):
  _saved_test_id = "erp5_web_renderjs_ui_test:testFunctionalRJSInterfaceValidator"
  realtime_output = False
  enabled_product_list = ('CMFActivity', 'CMFCategory', 'ERP5', 'ERP5Catalog',
                          'ERP5eGovSecurity', 'ERP5Form',
                          'ERP5OOo', 'ERP5Security', 'ERP5SyncML', 'ERP5Type',
                          'ERP5VCS', 'ERP5Wizard', 'Formulator', 'ERP5Workflow',
                          'ERP5Configurator','HBTreeFolder2', 'MailTemplates', 
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
        # glob('%s/product/Formulator/tests/test*.py' % path) +
        # glob('%s/product/ERP5Form/tests/test*.py' % path) +
        # ['%s/product/ERP5OOo/tests/testDeferredStyle.py' % path] +
        # ['%s/product/ERP5/tests/testXHTML.py' % path] +
        ['%s/product/ERP5/tests/testBankReconciliation.py' % path] +
        # ['%s/product/ERP5Type/tests/testFunctionalCore.py' % path] +
        # ['%s/product/ERP5Type/tests/testFunctionalAnonymousSelection.py' % path] +
        # glob('%s/bt5/erp5_web/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_web_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_hal_json_style/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_web_renderjs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_web_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_token_login/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_trade_renderjs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_pdm_renderjs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_crm_renderjs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_item_renderjs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_deferred_renderjs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_accounting_renderjs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_accounting_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_bank_reconciliation_renderjs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_gadget_interface_validator_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_web_monitoring_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_travel_expense_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_officejs_support_request_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        glob('%s/bt5/erp5_officejs_afs_directory_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        # glob('%s/bt5/erp5_officejs_ui_test/TestTemplateItem/portal_components/test.*.test*.py' % path) +
        []
      ):
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
      # ERP5TioSafe is disabled for now because it requires external programs
      # such as php and it has not been updated for Zope >= 2.12
      if product == 'ERP5TioSafe':
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
      if test_case.startswith('testLive') or test_case.startswith('testVifib') \
         or test_case.find('Performance') > 0 \
         or test_case in ('testERP5LdapCatalog', # XXX (Ivan), until LDAP server is available this test will alway fail
                          # tests reading selenium tables from erp5.com
                          # not maintained
                          'testERP5eGov',
                          'testAccounting_l10n_fr_m9',
                          # Not a test
                          'testERP5SyncMLMixin'
         ):
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
    if test.startswith('testFunctional'):
      return self._updateFunctionalTestResponse(self.runUnitTest(full_test))
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
