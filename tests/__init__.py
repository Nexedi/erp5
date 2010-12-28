import glob, os, subprocess
# test_suite is provided by 'run_test_suite'
from test_suite import ERP5TypeTestSuite

class _ERP5(ERP5TypeTestSuite):
  realtime_output = False
  enabled_product_list = ('CMFActivity', 'CMFCategory', 'ERP5', 'ERP5Catalog',
                          'ERP5eGovSecurity', 'ERP5Form', 'ERP5Legacy',
                          'ERP5OOo', 'ERP5PropertySheetLegacy', 'ERP5Security',
                          'ERP5Subversion', 'ERP5SyncML', 'ERP5Type',
                          'ERP5Wizard', 'Formulator', 'HBTreeFolder2',
                          'MailTemplates', 'PortalTransforms', 'TimerService',
                          'ZLDAPConnection', 'ZLDAPMethods', 'ZMySQLDA',
                          'ZMySQLDDA', 'ZSQLCatalog')

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

  def update(self, working_copy_list=None):
    self.checkout('products', 'bt5')
    self.enableProducts()


class PERF(_ERP5):
  allow_restart = True

  def getTestList(self):
    return ('testPerformance',) * 3

  def update(self):
    self.checkout('products', 'bt5/erp5_base', 'bt5/erp5_ui_test')
    self.enableProducts()

class ERP5(_ERP5):
  mysql_db_count = 3

  def getTestList(self):
    test_list = []
    for test_path in glob.glob('Products/*/tests/test*.py') + \
                     glob.glob('bt5/*/TestTemplateItem/test*.py'):
      test_case = test_path.split(os.sep)[-1][:-3] # remove .py
      product = test_path.split(os.sep)[-3]
      # don't test 3rd party products
      if product in ('PortalTransforms', 'MailTemplates'):
        continue
      # skip some tests
      if test_case.startswith('testLive') or test_case.startswith('testVifib') \
         or test_case in ('testPerformance', 'testSimulationPerformance'):
        continue
      test_list.append(test_case)
    return test_list

  def run(self, test):
    if test in ('testConflictResolution', 'testInvalidationBug'):
      status_dict = self.runUnitTest('--save', test)
      if not status_dict['status_code']:
        status_dict = self.runUnitTest('--load', '--activity_node=2', test)
      return status_dict
    return super(ERP5, self).run(test)

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
