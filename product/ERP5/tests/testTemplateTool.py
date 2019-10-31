# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
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

import os
import shutil
import unittest
import random
import tempfile
from xml.dom.minidom import getDOMImplementation
from App.config import getConfiguration
from Products.CMFCore.ActionsTool import ActionsTool
from Products.ERP5VCS.WorkingCopy import getVcsTool
from Products.ERP5.Document.BusinessTemplate import \
    BusinessTemplateMissingDependency

from Products.ERP5.Tool.TemplateTool import BusinessTemplateUnknownError

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestTemplateTool(ERP5TypeTestCase):
  """Test the template tool
  """
  test_tool_id = 'test_portal_templates'

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_stock_cache',
           )

  def getTitle(self):
    return "Template Tool"

  def afterSetUp(self):
    self.templates_tool = self.portal.portal_templates
    self.setupAutomaticBusinessTemplateRepository(
         searchable_business_template_list=["erp5_core", "erp5_base"])
    if getattr(self.portal, self.test_tool_id, None) is not None:
      self.portal.manage_delObjects(ids=[self.test_tool_id])
    self.portal.newContent(portal_type='Template Tool',
                           id=self.test_tool_id)
    self.dummy_template_tool = getattr(self.portal, self.test_tool_id)

  def beforeTearDown(self):
    self.tic()
    mark_replaced_bt_list = ["erp5_odt_style", "erp5_pdm", 'erp5_accounting',
           'erp5_workflow', 'erp5_configurator',
           'erp5_ingestion_mysql_innodb_catalog', "erp5_configurator_standard"]
    for bt_name in mark_replaced_bt_list:
      bt = self.templates_tool.getInstalledBusinessTemplate(bt_name)
      if (bt is not None) and bt.getInstallationState() in ['installed',
                                                            'replaced']:
        self.templates_tool.manage_delObjects([bt.getId()])
    self.tic()
    bt = self.templates_tool.getInstalledBusinessTemplate("erp5_base")
    if bt.getInstallationState() == "replaced":
      bt.install(force=1)
    self.tic()

  def testUpdateBT5FromRepository(self):
    """ Test the list of bt5 returned for upgrade """
    # edit bt5 revision so that it will be marked as updatable
    erp5_base = self.templates_tool.getInstalledBusinessTemplate('erp5_base',
                                                                 strict=True)
    erp5_base._setRevision('')

    self.assertTrue("erp5_base" in (bt.getTitle() for bt in
      self.templates_tool.getRepositoryBusinessTemplateList(update_only=True)))
    erp5_base.replace()
    self.assertFalse("erp5_base" in (bt.getTitle() for bt in
      self.templates_tool.getRepositoryBusinessTemplateList(update_only=True)))
    self.abort()

  def test_download_http(self):
    test_web = self.portal.portal_templates.download(
        'http://www.erp5.org/dists/snapshot/test_bt5/test_web.bt5')
    self.assertEqual(test_web.getPortalType(), 'Business Template')
    self.assertEqual(test_web.getTitle(), 'test_web')
    self.assertEqual(len(test_web.getRevision()), 28)

  def _svn_setup_ssl(self):
    """
      Function used to trust in svn.erp5.org.
    """
    for trust_dict in [
      # for subversion 1.6
      {'failures': 8,
        'finger_print': 'a1:f7:c6:bb:51:69:84:28:ac:58:af:9d:05:73:de:24:45:4d:a1:bb',
        'hostname': 'roundcube.nexedi.com',
        'issuer_dname': 'Nexedi SA, Marcq en Baroeul, Nord Pas de Calais, FR',
        'realm': 'https://svn.erp5.org:443',
        'valid_from': 'Thu, 22 May 2008 13:43:01 GMT',
        'valid_until': 'Sun, 20 May 2018 13:43:01 GMT'},
      # for subversion 1.8
      {'failures': 8,
        'finger_print': 'A1:F7:C6:BB:51:69:84:28:AC:58:AF:9D:05:73:DE:24:45:4D:A1:BB',
        'hostname': 'mail.nexedi.com',
        'issuer_dname': 'Nexedi SA, Marcq en Baroeul, Nord Pas de Calais, FR(webmaster@nexedi.com)',
        'realm': 'https://svn.erp5.org:443',
        'valid_from': 'May 22 13:43:01 2008 GMT',
        'valid_until': 'May 20 13:43:01 2018 GMT'}
      ]:
      getVcsTool("svn").__of__(self.portal).acceptSSLServer(trust_dict)

  def test_download_svn(self):
    # if the page looks like a svn repository, template tool will use pysvn to
    # get the bt5.
    self._svn_setup_ssl()
    bt5_url = 'https://svn.erp5.org/repos/public/erp5/trunk/bt5/test_web'
    test_web = self.portal.portal_templates.download(bt5_url)
    self.assertEqual(test_web.getPortalType(), 'Business Template')
    self.assertEqual(test_web.getTitle(), 'test_web')
    self.assertEqual(len(test_web.getRevision()), 28)

  def test_updateBusinessTemplateFromUrl_simple(self):
    """
     Test updateBusinessTemplateFromUrl method

     By default if a new business template has revision != previous one
     the new bt5 is not installed, only imported.
    """
    self._svn_setup_ssl()

    global PropertiesTool
    class PropertiesTool(ActionsTool):
      id = 'portal_properties'
    cls = PropertiesTool

    # Assign a fake properties tool to the portal
    tool = PropertiesTool()
    self.portal._setObject(tool.id, tool, set_owner=False, suppress_events=True)
    del tool
    self.commit()

    template_tool = self.portal.portal_templates

    url = 'https://svn.erp5.org/repos/public/erp5/trunk/bt5/erp5_csv_style'
    template_tool.updateBusinessTemplateFromUrl(url)
    old_bt = template_tool.getInstalledBusinessTemplate('erp5_csv_style')
    # fake different revision
    old_bt.setRevision('')

    # Break the properties tool
    self.assertIs(self.portal.portal_properties.__class__, cls)
    self.commit()
    self.portal._p_jar.cacheMinimize()
    del PropertiesTool
    self.assertIsNot(self.portal.portal_properties.__class__, cls)

    # Remove portal.portal_properties
    from Products.ERP5Type.dynamic.portal_type_class import \
      _bootstrapped, synchronizeDynamicModules
    _bootstrapped.remove(self.portal.id)
    synchronizeDynamicModules(self.portal, force=True)

    # The bt from this repo
    url = self._getBTPathAndIdList(('erp5_csv_style',))[0][0]

    new_bt = template_tool.updateBusinessTemplateFromUrl(url)
    self.assertNotEquals(old_bt, new_bt)
    self.assertEqual('erp5_csv_style', new_bt.getTitle())

    # Test Another time with definning an ID
    old_bt = new_bt
    old_bt.setRevision('')
    template_tool.updateBusinessTemplateFromUrl(url, id="new_erp5_csv_style")
    new_bt = template_tool.getInstalledBusinessTemplate('erp5_csv_style')
    self.assertNotEquals(old_bt, new_bt)
    self.assertEqual('erp5_csv_style', new_bt.getTitle())
    self.assertEqual('new_erp5_csv_style', new_bt.getId())

    # Test if the new instance with same revision is not installed.
    old_bt = new_bt
    template_tool.updateBusinessTemplateFromUrl(url, id="not_installed_bt5")
    new_bt = template_tool.getInstalledBusinessTemplate('erp5_csv_style')
    self.assertEqual(old_bt, new_bt)
    self.assertEqual('erp5_csv_style', new_bt.getTitle())
    self.assertEqual('new_erp5_csv_style', new_bt.getId())
    not_installed_bt5 = template_tool['not_installed_bt5']
    self.assertEqual('erp5_csv_style', not_installed_bt5.getTitle())
    self.assertEqual(not_installed_bt5.getInstallationState(),
                      "not_installed")
    self.assertEqual(not_installed_bt5.getRevision(), new_bt.getRevision())

  def test_updateBusinessTemplateFromUrl_keep_list(self):
    self._svn_setup_ssl()
    template_tool = self.portal.portal_templates
    url = 'https://svn.erp5.org/repos/public/erp5/trunk/bt5/test_core'
    # make sure this `test_core` bt is not installed
    template_tool.updateBusinessTemplateFromUrl(url)
    bt = template_tool.getInstalledBusinessTemplate('test_core')
    bt.uninstall()
    self.tic()

    # don't install test_file
    keep_original_list = ('portal_skins/erp5_test/test_file', )
    template_tool.updateBusinessTemplateFromUrl(url,
                                   keep_original_list=keep_original_list)

    bt = template_tool.getInstalledBusinessTemplate('test_core')
    self.assertNotEqual(None, bt)
    erp5_test = self.portal.portal_skins['erp5_test']
    self.assertFalse(erp5_test.hasObject('test_file'))

  def test_updateBusinessTemplateFromUrl_after_before_script(self):
    from Products.ERP5Type.tests.utils import createZODBPythonScript
    portal = self.getPortal()
    self._svn_setup_ssl()
    createZODBPythonScript(portal.portal_skins.custom,
                                   'BT_dummyA',
                                   'scripts_params=None',
                                   '# Script body\n'
                                   'return context.setDescription("MODIFIED")')

    createZODBPythonScript(portal.portal_skins.custom,
                                   'BT_dummyB',
                                   'scripts_params=None',
                                   '# Script body\n'
                                   'return context.setChangeLog("MODIFIED")')

    createZODBPythonScript(portal.portal_skins.custom,
                                   'BT_dummyC',
                                   'scripts_params=None',
                                   '# Script body\n'
                                   'return context.getPortalObject().setTitle("MODIFIED")')

    template_tool = self.portal.portal_templates
    url = 'https://svn.erp5.org/repos/public/erp5/trunk/bt5/test_html_style'
    # don't install test_file
    before_triggered_bt5_id_list = ['BT_dummyA', 'BT_dummyB']
    after_triggered_bt5_id_list = ['BT_dummyC']
    template_tool.updateBusinessTemplateFromUrl(url,
                                   before_triggered_bt5_id_list=before_triggered_bt5_id_list,
                                   after_triggered_bt5_id_list=after_triggered_bt5_id_list)
    bt = template_tool.getInstalledBusinessTemplate('test_html_style')
    self.assertNotEquals(None, bt)
    self.assertEqual(bt.getDescription(), 'MODIFIED')
    self.assertEqual(bt.getChangeLog(), 'MODIFIED')
    self.assertEqual(portal.getTitle(), 'MODIFIED')

  def test_CompareVersions(self):
    """Tests compare version on template tool. """
    compareVersions = self.getPortal().portal_templates.compareVersions
    self.assertEqual(0, compareVersions('1', '1'))
    self.assertEqual(0, compareVersions('1.2', '1.2'))
    self.assertEqual(0, compareVersions('1.2rc3', '1.2rc3'))
    self.assertEqual(0, compareVersions('1.0.0', '1.0'))

    self.assertEqual(-1, compareVersions('1.0', '1.0.1'))
    self.assertEqual(-1, compareVersions('1.0rc1', '1.0'))
    self.assertEqual(-1, compareVersions('1.0a', '1.0.1'))
    self.assertEqual(-1, compareVersions('1.1', '2.0'))

  def test_CompareVersionStrings(self):
    """Test compareVersionStrings on template tool"""
    compareVersionStrings = \
        self.getPortal().portal_templates.compareVersionStrings
    self.assertTrue(compareVersionStrings('1.1', '> 1.0'))
    self.assertFalse(compareVersionStrings('1.1rc1', '= 1.0'))
    self.assertFalse(compareVersionStrings('1.0rc1', '> 1.0'))
    self.assertFalse(compareVersionStrings('1.0rc1', '>= 1.0'))
    self.assertTrue(compareVersionStrings('1.0rc1', '>= 1.0rc1'))


  def test_getInstalledBusinessTemplate_installed(self):
    test_bt = self.portal.portal_templates.newContent(
      portal_type='Business Template',
      title='erp5_test_bt_%s' % self.id())
    test_bt.install()
    self.tic()
    self.assertEqual(test_bt,
      self.portal.portal_templates.getInstalledBusinessTemplate('erp5_test_bt_%s' % self.id()))

  def test_getInstalledBusinessTemplate_erp5_core_installed(self):
    erp5_core = self.portal.portal_templates.getInstalledBusinessTemplate('erp5_core')
    self.assertNotEqual(None, erp5_core)
    self.assertEqual('Business Template', erp5_core.getPortalType())

  def test_getInstalledBusinessTemplate_not_installed(self):
    self.assertEqual(None,
     self.portal.portal_templates.getInstalledBusinessTemplate('not_installed'))

  def test_getInstalledBusinessTemplate_provision(self):
    test_bt = self.portal.portal_templates.newContent(
      portal_type='Business Template',
      title='test_bt_%s' % self.id(),
      provision_list=['erp5_test_bt_%s' % self.id()])
    test_bt.install()
    self.tic()
    self.assertEqual(test_bt,
      self.portal.portal_templates.getInstalledBusinessTemplate('erp5_test_bt_%s' % self.id()))

  def test_getInstalledBusinessTemplate_replaced(self):
    test_bt_v1 = self.portal.portal_templates.newContent(
      portal_type='Business Template',
      title='test_bt_%s' % self.id(),
      version='1')
    test_bt_v1.install()
    self.tic()
    test_bt_v2 = self.portal.portal_templates.newContent(
      portal_type='Business Template',
      title='test_bt_%s' % self.id(),
      version='2')
    test_bt_v2.install()
    self.assertEqual('replaced', test_bt_v1.getInstallationState())
    self.tic()
    self.assertEqual(test_bt_v2,
      self.portal.portal_templates.getInstalledBusinessTemplate('test_bt_%s' % self.id()))

  def test_getInstalledBusinessTemplate_uninstalled(self):
    test_bt = self.portal.portal_templates.newContent(
      portal_type='Business Template',
      title='test_bt_%s' % self.id())
    test_bt.install()
    test_bt.uninstall()
    self.tic()
    self.assertEqual(None,
      self.portal.portal_templates.getInstalledBusinessTemplate('test_bt_%s' % self.id()))

  def test_getInstalledBusinessTemplate_replaced_then_uninstalled(self):
    test_bt_v1 = self.portal.portal_templates.newContent(
      portal_type='Business Template',
      title='test_bt_%s' % self.id(),
      version='1')
    test_bt_v1.install()
    self.tic()
    test_bt_v2 = self.portal.portal_templates.newContent(
      portal_type='Business Template',
      title='test_bt_%s' % self.id(),
      version='2')
    test_bt_v2.install()
    self.assertEqual('replaced', test_bt_v1.getInstallationState())
    self.tic()
    test_bt_v2.uninstall()
    self.assertEqual(None,
      self.portal.portal_templates.getInstalledBusinessTemplate('test_bt_%s' % self.id()))

  def test_revision(self):
    template_tool = self.portal.portal_templates
    getInstalledRevision = template_tool.getInstalledBusinessTemplateRevision
    self.assertEqual(None, getInstalledRevision('erp5_toto'))
    available_bt, = template_tool.getRepositoryBusinessTemplateList(
      template_list=('test_core',))
    revision = available_bt.getRevision()
    self.assertEqual('+Kds1k1J41hzO4yIO+GcKQukNps=', revision)
    installed_bt = template_tool.download("%s/%s" % (available_bt.repository,
                                                     available_bt.filename))
    self.assertEqual(revision, installed_bt.getRevision())
    installed_bt.install()
    self.assertEqual(revision, getInstalledRevision('test_core'))
    bt = installed_bt.Base_createCloneDocument(batch_mode=1)
    bt.build(update_revision=False)
    root = tempfile.mkdtemp()
    try:
      bt.export(root, local=1)
      with open(os.path.join(root, 'bt', 'title')) as f:
        self.assertTrue('test_core', f.read())
      # We don't export revision anymore.
      self.assertFalse(os.path.exists(os.path.join(root, 'bt', 'revision')))
      # Computed at download ...
      self.assertEqual(revision, template_tool.download(root).getRevision())
    finally:
      shutil.rmtree(root)
    bt._setVersion("2.0")
    # ... at building by default ...
    bt.build()
    revision = bt.getRevision()
    self.assertEqual('xR/n0PtLoc+1CR0AyJ+xGjbxsjE=', revision)
    self.portal.portal_skins.erp5_test.manage_renameObject('test_file',
                                                           'test_file2')
    bt.build(update_revision=False)
    self.assertEqual(revision, bt.getRevision())
    # ... and at export.
    bt.export(str(random.random()))
    self.assertEqual('fnLZVdsjkNDoC0JWstMY2XL1x+s=', bt.getRevision())
    self.abort()

  def test_getInstalledBusinessTemplateList(self):
    templates_tool = self.getPortal().portal_templates
    bt5_list = templates_tool.getInstalledBusinessTemplateList()
    another_bt_list = [i for i in templates_tool.contentValues() \
                       if i.getInstallationState() == 'installed']
    self.assertEqual(len(bt5_list), len(another_bt_list))
    for bt in bt5_list:
      self.assertTrue(bt in another_bt_list)

    self.assertEqual(bt5_list,
                      templates_tool._getInstalledBusinessTemplateList())

  def test_getInstalledBusinessTemplateTitleList(self):
    templates_tool = self.getPortal().portal_templates
    bt5_list = templates_tool.getInstalledBusinessTemplateTitleList()
    another_bt_list = [i.getTitle() for i in templates_tool.contentValues() \
                       if i.getInstallationState() == 'installed']
    bt5_list.sort()
    another_bt_list.sort()
    self.assertEqual(bt5_list, another_bt_list)
    for bt in bt5_list:
      self.assertTrue(bt in another_bt_list)

    new_list = templates_tool._getInstalledBusinessTemplateList(only_title=1)
    new_list.sort()
    self.assertEqual(bt5_list, new_list)

  def test_getBusinessTemplateUrl(self):
    """ Test if this method can find which repository is the business
        template
    """
    # How to define an existing and use INSTANCE_HOME_REPOSITORY?
    url_list = ['https://svn.erp5.org/repos/public/erp5/trunk/bt5',
                'http://www.erp5.org/dists/snapshot/bt5',
                'http://www.erp5.org/dists/release/5.4.5/bt5',
                "INSTANCE_HOME_REPOSITORY",
                'file:///opt/does/not/exist']

    exist_bt5 = 'erp5_base'
    not_exist_bt5 = "erp5_not_exist"
    template_tool = self.portal.portal_templates
    getBusinessTemplateUrl = template_tool.getBusinessTemplateUrl

    # Test Exists
    self.assertEqual(getBusinessTemplateUrl(url_list, exist_bt5),
                  'https://svn.erp5.org/repos/public/erp5/trunk/bt5/erp5_base')
    self.assertEqual(getBusinessTemplateUrl(url_list[1:], exist_bt5),
                      'http://www.erp5.org/dists/snapshot/bt5/erp5_base.bt5')
    self.assertEqual(getBusinessTemplateUrl(url_list[2:], exist_bt5),
                      'http://www.erp5.org/dists/release/5.4.5/bt5/erp5_base.bt5')
    INSTANCE_HOME = getConfiguration().instancehome
    local_bt = None
    if os.path.exists(INSTANCE_HOME + "/bt5/erp5_base"):
      local_bt = 'file://' + INSTANCE_HOME + "/bt5/erp5_base"
    self.assertEqual(getBusinessTemplateUrl(url_list[3:], exist_bt5), local_bt)
    self.assertEqual(getBusinessTemplateUrl(url_list[4:], exist_bt5), None)

    # Test Not exists
    self.assertEqual(getBusinessTemplateUrl(url_list, not_exist_bt5), None)
    self.assertEqual(getBusinessTemplateUrl(url_list[1:], not_exist_bt5), None)
    self.assertEqual(getBusinessTemplateUrl(url_list[2:], not_exist_bt5), None)
    self.assertEqual(getBusinessTemplateUrl(url_list[3:], not_exist_bt5), None)
    self.assertEqual(getBusinessTemplateUrl(url_list[4:], not_exist_bt5), None)

  def test_resolveBusinessTemplateListDependency(self):
    """ Test API able to return a complete list of bt5s to setup a sub set of
    business templates.
    """
    repository = "dummy_repository"
    template_tool = self.dummy_template_tool
    # setup dummy internal repository data to make unit test independant
    # from any real repository
    def addRepositoryEntry(**kw):
      kw['id'] = '%s.bt5' % kw['title']
      kw.setdefault('version', '1')
      kw.setdefault('provision_list', ())
      kw.setdefault('dependency_list', ())
      kw.setdefault('revision', '1')
      return kw
    template_tool.repository_dict[repository] = (
      addRepositoryEntry(title='foo', dependency_list=()),
      addRepositoryEntry(title='bar', dependency_list=('foo',)),
      addRepositoryEntry(title='baz', dependency_list=('bar',)),
      addRepositoryEntry(title='biz', dependency_list=()),
      addRepositoryEntry(title='ca1', provision_list=('sql',)),
      addRepositoryEntry(title='ca2', provision_list=('sql',)),
      addRepositoryEntry(title='a', dependency_list=()),
      addRepositoryEntry(title='b', dependency_list=('a'), revision='5'),
      addRepositoryEntry(title='end', dependency_list=('baz','sql', 'b')),
      )

    # Simulate that we have some installed bt.
    for bt_id in ('foo', 'ca1', 'b'):
      bt = template_tool.newContent(portal_type='Business Template',
                             title=bt_id, revision='4', id=bt_id)
      bt.install()

    bt5_id_list = ['baz']
    bt5_list = template_tool.resolveBusinessTemplateListDependency(bt5_id_list)
    self.assertEqual([(repository, 'foo.bt5'),
                       (repository, 'bar.bt5'),
                       (repository, 'baz.bt5')], bt5_list)

    bt5_id_list = ['foo']
    bt5_list = template_tool.resolveBusinessTemplateListDependency(
                      bt5_id_list)
    self.assertEqual([(repository, 'foo.bt5')], bt5_list)

    bt5_id_list = ['biz', 'end']

    bt5_list = template_tool.resolveBusinessTemplateListDependency(bt5_id_list)
    self.assertEqual([(repository, 'foo.bt5'),
                       (repository, 'a.bt5'),
                       (repository, 'bar.bt5'),
                       (repository, 'b.bt5'),
                       (repository, 'ca1.bt5'),
                       (repository, 'baz.bt5'),
                       (repository, 'end.bt5'),
                       (repository, 'biz.bt5')], bt5_list)

    # By removing ca1, we remove the choice for the "sql" provider.
    # Therefore template tool does not know any more what to take for "sql".
    template_tool.manage_delObjects(['ca1'])
    self.commit()
    self.assertRaises(BusinessTemplateMissingDependency,
                template_tool.resolveBusinessTemplateListDependency,
                bt5_id_list)

    bt5_id_list = ['erp5_do_not_exist']
    self.assertRaises(BusinessTemplateUnknownError,
                   template_tool.resolveBusinessTemplateListDependency,
                   bt5_id_list)

  def test_installBusinessTemplatesFromRepository_simple(self):
    """ Simple test for portal_templates.installBusinessTemplatesFromRepository
    """
    bt5_name = 'erp5_odt_style'
    self.tic()
    bt = self.templates_tool.getInstalledBusinessTemplate(bt5_name, strict=True)
    self.assertEqual(bt, None)
    operation_log = \
      self.templates_tool.installBusinessTemplateListFromRepository([bt5_name])
    self.assertTrue("Installed %s with" % bt5_name in operation_log[-1])
    bt = self.templates_tool.getInstalledBusinessTemplate(bt5_name, strict=True)
    self.assertNotEquals(bt, None)
    self.assertEqual(bt.getTitle(), bt5_name)

    # Repeat operation, the bt5 should be ignored
    self.templates_tool.installBusinessTemplateListFromRepository([bt5_name])
    bt_old = self.templates_tool.getInstalledBusinessTemplate(bt5_name, strict=True)
    self.assertEqual(bt.getId(), bt_old.getId())

    # Repeat operation, new bt5 should be inslalled due only_different = False
    operation_log = self.templates_tool.installBusinessTemplateListFromRepository(
          [bt5_name], only_different=False)

    self.assertTrue("Installed %s with" % bt5_name in operation_log[-1])
    bt_new = self.templates_tool.getInstalledBusinessTemplate(bt5_name,
                                                              strict=True)
    self.assertNotEquals(bt.getId(), bt_new.getId())

  def test_installBusinessTemplatesFromRepository_update_catalog(self):
    """ Test if update catalog is trigger when needed.
    """
    has_cleared_catalog = []
    from Products.ERP5Catalog.Document.ERP5Catalog import ERP5Catalog
    orig_manage_catalogClear = ERP5Catalog.manage_catalogClear
    def manage_catalogClear(*args, **kw):
      has_cleared_catalog.append(None)
      return orig_manage_catalogClear(*args, **kw)
    ERP5Catalog.manage_catalogClear = manage_catalogClear
    try:
      bt5_name = 'erp5_ingestion_mysql_innodb_catalog'
      template_tool = self.portal.portal_templates
      self.tic()
      bt = template_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertEqual(bt, None)
      operation_log = template_tool.installBusinessTemplateListFromRepository([bt5_name],
                            only_different=False, update_catalog=0)

      self.assertTrue("Installed %s with" % bt5_name in operation_log[0])
      bt = template_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertNotEquals(bt.getId(), None)
      self.commit()
      self.assertFalse(has_cleared_catalog)
      # Before launch activities make sure email table is created even
      # catalog is not created.
      catalog_tool = self.portal.portal_catalog
      catalog_tool.erp5_mysql_innodb.z0_drop_email()
      catalog_tool.erp5_mysql_innodb.z_create_email()
      self.tic()

      bt5_name = 'erp5_odt_style'
      operation_log = template_tool.installBusinessTemplateListFromRepository([bt5_name],
                            only_different=False, update_catalog=1)
      self.assertTrue("Installed %s with" % bt5_name in operation_log[-1])
      bt = template_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertEqual(bt.getTitle(), bt5_name)
      self.commit()
      self.assertTrue(has_cleared_catalog)
      del has_cleared_catalog[:]
      self.tic()

      # Install again should not force catalog to be updated
      operation_log = template_tool.installBusinessTemplateListFromRepository(
                [bt5_name], only_different=False)
      self.assertTrue("Installed %s with" % bt5_name in operation_log[-1])
      bt = template_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertNotEquals(bt, None)
      self.assertEqual(bt.getTitle(), bt5_name)
      self.commit()
      self.assertFalse(has_cleared_catalog)
      self.tic()
    finally:
      ERP5Catalog.manage_catalogClear = orig_manage_catalogClear
      # Make sure no broken catalog it will be left behind and propaguated to
      # the next tests.
      if len(self.portal.portal_activities.getMessageList())>0:
        self.portal.portal_activities.manageClearActivities()
        self.commit()
        self.portal.ERP5Site_reindexAll(clear_catalog=1)
      self.tic()

  def test_installBusinessTemplatesFromRepository_activate(self):
    """ Test if update catalog is trigger when needed.
    """
    bt5_name_list = ['erp5_odt_style', 'erp5_pdm']
    self.tic()
    for bt5_name in bt5_name_list:
      bt = self.templates_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertEqual(bt, None)

    self.templates_tool.installBusinessTemplateListFromRepository(
                            bt5_name_list, activate=True)

    for bt5_name in bt5_name_list:
      bt = self.templates_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertEqual(bt, None)

    self.tic()
    for bt5_name in bt5_name_list:
      bt = self.templates_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertNotEquals(bt, None)
      self.assertEqual(bt.getTitle(), bt5_name)

  def test_installBusinessTemplatesFromRepository_install_dependency(self):
    """Test if dependencies are automatically installed properly
    """
    # erp5_configurator_{ung,standard} depends on erp5_configurator which in
    # turn depends on erp5_workflow
    bt5_name_list = ['erp5_configurator_standard']
    template_tool = self.portal.portal_templates
    for repos in template_tool.getRepositoryList():
      if "bootstrap" not in repos:
        repository = repos
    self.tic()
    for bt5_name in bt5_name_list:
      bt = template_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertEqual(bt, None)

    bt = template_tool.getInstalledBusinessTemplate("erp5_configurator")
    self.assertEqual(bt, None)
    bt = template_tool.getInstalledBusinessTemplate("erp5_workflow")
    self.assertEqual(bt, None)

    self.assertRaises(BusinessTemplateMissingDependency,
              template_tool.installBusinessTemplateListFromRepository,
                            bt5_name_list)

    # Try fail in activities.
    self.assertRaises(BusinessTemplateMissingDependency,
              template_tool.installBusinessTemplateListFromRepository,
                      bt5_name_list, True, True, True)

    for bt5_name in bt5_name_list:
      bt = template_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertEqual(bt, None)
      dependency_list = template_tool.getDependencyList(
                   (repository, bt5_name))
      self.assertNotEquals(dependency_list, [])

    template_tool.installBusinessTemplateListFromRepository(
                            bt5_name_list, install_dependency=True)
    for bt5_name in bt5_name_list:
      bt = template_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertNotEquals(bt, None)

    bt = template_tool.getInstalledBusinessTemplate("erp5_configurator")
    self.assertNotEquals(bt, None)
    bt = template_tool.getInstalledBusinessTemplate("erp5_workflow")
    self.assertNotEquals(bt, None)
    self.abort()

    # Same as above but also check that dependencies are properly resolved if
    # one of the dependency is explicitly added to the list of bt5 to be
    # installed
    template_tool.installBusinessTemplateListFromRepository(
      bt5_name_list + ['erp5_workflow'],
      install_dependency=True)
    for bt5_name in bt5_name_list:
      bt = template_tool.getInstalledBusinessTemplate(bt5_name)
      self.assertNotEquals(bt, None)

    bt = template_tool.getInstalledBusinessTemplate("erp5_configurator")
    self.assertNotEquals(bt, None)
    bt = template_tool.getInstalledBusinessTemplate("erp5_workflow")
    self.assertNotEquals(bt, None)
    self.abort()

  def test_installBusinessTemplateListFromRepository_ignore_when_installed(self):
    """Check that install one business template, this method does not download
    many business templates that are already installed
    """
    template_tool = self.portal.portal_templates
    before = {bt.getTitle(): bt.getId()
      for bt in template_tool.getInstalledBusinessTemplateList()}

    bt_title = 'test_core'
    # This test will install `bt_title` from repository and check that nothing
    # else was installed.
    # Test assume that `bt_title` is not installed at this point and that it
    # does not depend on anything that's not already installed.
    self.assertNotIn(bt_title, before)

    template_tool.installBusinessTemplateListFromRepository([bt_title],
        install_dependency=True)
    self.tic()
    after = {bt.getTitle(): bt.getId()
      for bt in template_tool.getInstalledBusinessTemplateList()}
    del after[bt_title]
    self.assertEqual(before, after)

  def test_sortBusinessTemplateList(self):
    """Check sorting of a list of business template by their dependencies
    """
    template_tool = self.portal.portal_templates

    bt5list = template_tool.resolveBusinessTemplateListDependency(('erp5_credential',))
    # add some entropy by disorder bt5list returned by
    # resolveBusinessTemplateListDependency
    position_list = range(len(bt5list))
    new_bt5_list = []
    while position_list:
      position = random.choice(position_list)
      position_list.remove(position)
      new_bt5_list.append(bt5list[position])

    ordered_list = template_tool.sortBusinessTemplateList(new_bt5_list)
    # group orders
    first_group = range(0, 5)
    second_group =  range(5, 11)
    third_group = range(11, 12)
    fourth_group = range(12, 14)
    fifth_group = range(14, 15)

    expected_position_dict = {
      'erp5_property_sheets': first_group,
      'erp5_core_proxy_field_legacy': first_group,
      'erp5_mysql_innodb_catalog': first_group,
      'erp5_core': first_group,
      'erp5_xhtml_style': first_group,
      'erp5_jquery': second_group,
      'erp5_jquery_ui': second_group,
      'erp5_full_text_mroonga_catalog': second_group,
      'erp5_ingestion_mysql_innodb_catalog': second_group,
      'erp5_base': second_group,
      'erp5_knowledge_pad': second_group,
      'erp5_ingestion': third_group,
      'erp5_web': fourth_group,
      'erp5_crm': fourth_group,
      'erp5_credential': fifth_group}

    for bt in ordered_list:
      self.assertTrue(ordered_list.index(bt) in expected_position_dict[bt[1]],
            'Expected positions for %r: %r, got %r' % (bt[1],
                                                  expected_position_dict[bt[1]],
                                                  ordered_list.index(bt)))

  def test_upgradeSite(self):
    templates_tool = self.dummy_template_tool
    repository = "dummy_repository"

    # setup dummy repository to make unit test independant from any real
    # repository. This function creates the bt5list XML of the repository and
    # the minimum BT files.
    def createBtAndAddToRepository(repository, xml, **kw):
      bt_dir = "%s/%s/bt" % (repository, kw['title'])
      if not os.path.exists(bt_dir):
        os.makedirs(bt_dir)
      with open("%s/title" % bt_dir, "wb") as f:
        f.write(kw['title'])
      template = xml.createElement('template')
      template.setAttribute('id', kw['title'])
      defaults = {
        'copyright': "Copyright Test Template Tool",
        'license': "GPL",
        'title': kw['title'], # title is mandatory
        'version': "1.0",
        'revision': "1"
      }
      for el in ['copyright', 'version', 'revision', 'license', 'title']:
        node = xml.createElement(el)
        node.appendChild(xml.createTextNode(kw.get(el, defaults[el])))
        template.appendChild(node)
      for dep in kw.get('dependency_list', []):
        node = xml.createElement('dependency')
        node.appendChild(xml.createTextNode(dep))
        template.appendChild(node)
      xml.documentElement.appendChild(template)

    def copyTestCoreBt(bt_name):
      bt_path = "%s/%s" % (repository, bt_name)
      available_bt, = self.portal.portal_templates.getRepositoryBusinessTemplateList(
                        template_list=('test_core',)
                      )
      test_core_path = available_bt.repository + "/test_core"
      if os.path.exists(bt_path):
        shutil.rmtree(bt_path)
      shutil.copytree(test_core_path, bt_path)

    # bt4 and bt5 are copies of test_core
    copyTestCoreBt("bt4")
    copyTestCoreBt("bt5")
    # create bt1..5 BT inside dummy_repository
    repo_xml = getDOMImplementation().createDocument(None, "repository", None)
    createBtAndAddToRepository(repository, repo_xml, title='bt1', dependency_list=('bt4',)),
    createBtAndAddToRepository(repository, repo_xml, title='bt2'),
    createBtAndAddToRepository(repository, repo_xml, title='bt3'),
    createBtAndAddToRepository(repository, repo_xml, title='bt4'),
    createBtAndAddToRepository(repository, repo_xml, title='bt5'),
    with open("%s/bt5list" % repository,"wb") as repo_xml_fd:
      repo_xml.writexml(repo_xml_fd)
      repo_xml_fd.close()

    # Install dummy_repository
    templates_tool.repository_dict[repository] = None
    templates_tool.updateRepositoryBusinessTemplateList([repository])

    def getInstalledBtList():
      return sorted([bt.getTitle() for bt in templates_tool.getInstalledBusinessTemplateList()])

    # Install manually 2 BT
    templates_tool.updateBusinessTemplateFromUrl("%s/bt2" % repository)
    self.assertEqual(getInstalledBtList(), ['bt2'])
    templates_tool.updateBusinessTemplateFromUrl("%s/bt3" % repository)
    self.assertEqual(getInstalledBtList(), ['bt2', 'bt3'])

    # First upgrade
    templates_tool.upgradeSite(bt5_list=['bt1'], keep_bt5_id_set=['bt2'], delete_orphaned=True)
    self.assertEqual(getInstalledBtList(), ['bt1', 'bt2', 'bt4'])
    # test_file has been installed with bt4
    erp5_test = self.portal.portal_skins['erp5_test']
    self.assertTrue(erp5_test.hasObject('test_file'))

    # Second upgrade
    templates_tool.upgradeSite(bt5_list=['bt5'], keep_bt5_id_set=['bt2'], delete_orphaned=True)
    self.assertEqual(getInstalledBtList(), ['bt2', 'bt5'])
    # test_file is now installed with bt5
    erp5_test = self.portal.portal_skins['erp5_test']
    self.assertTrue(erp5_test.hasObject('test_file'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTemplateTool))
  return suite
