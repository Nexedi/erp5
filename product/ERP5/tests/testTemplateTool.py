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
import transaction
from App.config import getConfiguration
from Products.ERP5VCS.WorkingCopy import getVcsTool

from Products.ERP5.Document.BusinessTemplate import \
    BusinessTemplateMissingDependency

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestTemplateTool(ERP5TypeTestCase):
  """
  Test the template tool
  """
  run_all_test = 1
  quiet = 1

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_csv_style')

  def getTitle(self):
    return "Template Tool"

  def afterSetUp(self):
    self.templates_tool = self.portal.portal_templates
    self.templates_tool.updateRepositoryBusinessTemplateList(\
                    ["http://www.erp5.org/dists/snapshot/bt5/",])

  def beforeTearDown(self):
    uninstall_bt_list = ["erp5_odt_style", "erp5_pdm", 'erp5_accounting']
    for bt_name in uninstall_bt_list:
      bt = self.templates_tool.getInstalledBusinessTemplate(bt_name)
      if (bt is not None) and bt.getInstallationState() == 'installed':
        bt.uninstall()
    self.stepTic()

  def testUpdateBT5FromRepository(self, quiet=quiet, run=run_all_test):
    """ Test the list of bt5 returned for upgrade """
    # edit bt5 revision so that it will be marked as updatable
    bt_list = self.templates_tool.searchFolder(title='erp5_base')
    self.assertEquals(len(bt_list), 1)
    erp5_base = bt_list[0].getObject()
    erp5_base.edit(revision=int(erp5_base.getRevision()) - 10)

    updatable_bt_list = self.templates_tool.getRepositoryBusinessTemplateList(update_only=True)
    self.assertEqual(
           [i.title for i in updatable_bt_list if i.title == "erp5_base"], 
           ["erp5_base"])
    erp5_base.replace()
    updatable_bt_list = self.templates_tool.getRepositoryBusinessTemplateList(update_only=True)
    self.assertEqual(
           [i.title for i in updatable_bt_list if i.title == "erp5_base"],
           [])

  def test_download_http(self):
    test_web = self.portal.portal_templates.download(
        'http://www.erp5.org/dists/snapshot/test_bt5/test_web.bt5')
    self.assertEquals(test_web.getPortalType(), 'Business Template')
    self.assertEquals(test_web.getTitle(), 'test_web')
    self.assertTrue(test_web.getRevision())

  def _svn_setup_ssl(self):
    """
      Function used to trust in svn.erp5.org.
    """
    trust_dict = dict(realm="https://svn.erp5.org:443",
      hostname="roundcube.nexedi.com",
      issuer_dname="Nexedi SA, Marcq en Baroeul, Nord Pas de Calais, FR",
      valid_from="Thu, 22 May 2008 13:43:01 GMT",
      valid_until="Sun, 20 May 2018 13:43:01 GMT",
      finger_print=\
        "a1:f7:c6:bb:51:69:84:28:ac:58:af:9d:05:73:de:24:45:4d:a1:bb",
      failures=8)
    getVcsTool("svn").__of__(self.portal).acceptSSLServer(trust_dict)

  def test_download_svn(self):
    # if the page looks like a svn repository, template tool will use pysvn to
    # get the bt5.
    self._svn_setup_ssl()
    bt5_url = 'https://svn.erp5.org/repos/public/erp5/trunk/bt5/test_web'
    test_web = self.portal.portal_templates.download(bt5_url)
    self.assertEquals(test_web.getPortalType(), 'Business Template')
    self.assertEquals(test_web.getTitle(), 'test_web')
    self.assertTrue(test_web.getRevision())

  def test_updateBusinessTemplateFromUrl_simple(self):
    """
     Test updateBusinessTemplateFromUrl method

     By default if a new business template has revision >= previous one
     the new bt5 is not installed, only imported.
    """
    self._svn_setup_ssl()
    template_tool = self.portal.portal_templates
    old_bt = template_tool.getInstalledBusinessTemplate('erp5_csv_style')
    # change revision to an old revision
    old_bt.setRevision(0.0001)
    url = 'https://svn.erp5.org/repos/public/erp5/trunk/bt5/erp5_csv_style'
    template_tool.updateBusinessTemplateFromUrl(url)
    new_bt = template_tool.getInstalledBusinessTemplate('erp5_csv_style')
    self.assertNotEquals(old_bt, new_bt)
    self.assertEquals('erp5_csv_style', new_bt.getTitle())

    # Test Another time with definning an ID
    old_bt = new_bt
    old_bt.setRevision(0.0002)
    template_tool.updateBusinessTemplateFromUrl(url, id="new_erp5_csv_style")
    new_bt = template_tool.getInstalledBusinessTemplate('erp5_csv_style')
    self.assertNotEquals(old_bt, new_bt)
    self.assertEquals('erp5_csv_style', new_bt.getTitle())
    self.assertEquals('new_erp5_csv_style', new_bt.getId())

    # Test if the new instance with same revision is not installed.
    old_bt = new_bt
    template_tool.updateBusinessTemplateFromUrl(url, id="not_installed_bt5")
    new_bt = template_tool.getInstalledBusinessTemplate('erp5_csv_style')
    self.assertEquals(old_bt, new_bt)
    self.assertEquals('erp5_csv_style', new_bt.getTitle())
    self.assertEquals('new_erp5_csv_style', new_bt.getId())
    not_installed_bt5 = getattr(template_tool, "not_installed_bt5", None)
    self.assertNotEquals(not_installed_bt5, None)
    self.assertEquals('erp5_csv_style', not_installed_bt5.getTitle())
    self.assertEquals(not_installed_bt5.getInstallationState(),
                      "not_installed")
    self.assertEquals(not_installed_bt5.getRevision(), new_bt.getRevision())

  def test_updateBusinessTemplateFromUrl_keep_list(self):
    """
     Test updateBusinessTemplateFromUrl method
    """
    self._svn_setup_ssl()
    template_tool = self.portal.portal_templates
    url = 'https://svn.erp5.org/repos/public/erp5/trunk/bt5/test_core'
    # don't install test_file
    keep_original_list = ( 'portal_skins/erp5_test/test_file', )
    template_tool.updateBusinessTemplateFromUrl(url,
                                   keep_original_list=keep_original_list)
    bt = template_tool.getInstalledBusinessTemplate('test_core')
    self.assertNotEquals(None, bt)
    erp5_test = getattr(self.portal.portal_skins, 'erp5_test', None)
    self.assertNotEquals(None, erp5_test)
    test_file = getattr(erp5_test, 'test_file', None)
    self.assertEquals(None, test_file)

  def test_updateBusinessTemplateFromUrl_after_before_script(self):
    """
     Test updateBusinessTemplateFromUrl method
    """
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
    self.assertEquals(bt.getDescription(), 'MODIFIED')
    self.assertEquals(bt.getChangeLog(), 'MODIFIED')
    self.assertEquals(portal.getTitle(), 'MODIFIED')

  def test_updateBusinessTemplateFromUrl_stringCastingBug(self):
    pt = self.getTemplateTool()
    template = pt.newContent(portal_type='Business Template')
    self.failUnless(template.getBuildingState() == 'draft')
    self.failUnless(template.getInstallationState() == 'not_installed')
    title = 'install_casting_to_int_bug_check'
    template.edit(title=title,
                  version='1.0',
                  description='bt for unit_test')
    transaction.commit()

    template.build()
    transaction.commit()

    cfg = getConfiguration()
    template_path = os.path.join(cfg.instancehome, 'tests', '%s' % (title,))
    # remove previous version of bt it exists
    if os.path.exists(template_path):
      shutil.rmtree(template_path)
    template.export(path=template_path, local=1)
    self.failUnless(os.path.exists(template_path))

    # setup version '9'
    first_revision = '9'
    open(os.path.join(template_path, 'bt', 'revision'), 'w').write(first_revision)
    pt.updateBusinessTemplateFromUrl(template_path)
    new_bt = pt.getInstalledBusinessTemplate(title)

    self.assertEqual(new_bt.getRevision(), first_revision)

    # setup revision '11', becasue: '11' < '9' (string comp), but 11 > 9 (int comp)
    second_revision = '11'
    self.assertTrue(second_revision < first_revision)
    self.assertTrue(int(second_revision) > int(first_revision))

    open(os.path.join(template_path, 'bt', 'revision'), 'w').write(second_revision)
    pt.updateBusinessTemplateFromUrl(template_path)
    newer_bt = pt.getInstalledBusinessTemplate(title)

    self.assertNotEqual(new_bt, newer_bt)
    self.assertEqual(newer_bt.getRevision(), second_revision)

  def test_CompareVersions(self):
    """Tests compare version on template tool. """
    compareVersions = self.getPortal().portal_templates.compareVersions
    self.assertEquals(0, compareVersions('1', '1'))
    self.assertEquals(0, compareVersions('1.2', '1.2'))
    self.assertEquals(0, compareVersions('1.2rc3', '1.2rc3'))
    self.assertEquals(0, compareVersions('1.0.0', '1.0'))

    self.assertEquals(-1, compareVersions('1.0', '1.0.1'))
    self.assertEquals(-1, compareVersions('1.0rc1', '1.0'))
    self.assertEquals(-1, compareVersions('1.0a', '1.0.1'))
    self.assertEquals(-1, compareVersions('1.1', '2.0'))

  def test_CompareVersionStrings(self):
    """Test compareVersionStrings on template tool"""
    compareVersionStrings = \
        self.getPortal().portal_templates.compareVersionStrings
    self.assertTrue(compareVersionStrings('1.1', '> 1.0'))
    self.assertFalse(compareVersionStrings('1.1rc1', '= 1.0'))
    self.assertFalse(compareVersionStrings('1.0rc1', '> 1.0'))
    self.assertFalse(compareVersionStrings('1.0rc1', '>= 1.0'))
    self.assertTrue(compareVersionStrings('1.0rc1', '>= 1.0rc1'))

  def test_getInstalledBusinessTemplate(self):
    self.assertNotEquals(None, self.getPortal()\
        .portal_templates.getInstalledBusinessTemplate('erp5_core'))

    self.assertEquals(None, self.getPortal()\
        .portal_templates.getInstalledBusinessTemplate('erp5_toto'))

  def test_getInstalledBusinessTemplateRevision(self):
    self.assertTrue(300 < self.getPortal()\
        .portal_templates.getInstalledBusinessTemplateRevision('erp5_core'))

    self.assertEquals(None, self.getPortal()\
        .portal_templates.getInstalledBusinessTemplateRevision('erp5_toto'))

  def test_getInstalledBusinessTemplateList(self):
    templates_tool = self.getPortal().portal_templates
    bt5_list = templates_tool.getInstalledBusinessTemplateList()
    another_bt_list = [ i for i in templates_tool.contentValues() \
                       if i.getInstallationState() == 'installed']
    self.assertEquals(len(bt5_list), len(another_bt_list))
    for bt in bt5_list:
      self.failUnless(bt in another_bt_list)

    self.assertEquals(bt5_list,
                      templates_tool._getInstalledBusinessTemplateList())

  def test_getInstalledBusinessTemplateTitleList(self):
    templates_tool = self.getPortal().portal_templates
    bt5_list =  templates_tool.getInstalledBusinessTemplateTitleList()
    another_bt_list = [ i.getTitle() for i in templates_tool.contentValues() \
                       if i.getInstallationState() == 'installed']
    bt5_list.sort()
    another_bt_list.sort()
    self.assertEquals(bt5_list, another_bt_list)
    for bt in bt5_list:
      self.failUnless(bt in another_bt_list)

    new_list = templates_tool._getInstalledBusinessTemplateList(only_title=1)
    new_list.sort()
    self.assertEquals(bt5_list, new_list)

  def test_getBusinessTemplateUrl(self):
    """ Test if this method can find which repository is the business
        template
    """
    # How to define an existing and use INSTANCE_HOME_REPOSITORY?
    url_list = [ 'https://svn.erp5.org/repos/public/erp5/trunk/bt5',
                 'http://www.erp5.org/dists/snapshot/bt5',
                 'http://www.erp5.org/dists/release/5.4.5/bt5',
                 "INSTANCE_HOME_REPOSITORY",
                 'file:///opt/does/not/exist']

    exist_bt5 = 'erp5_base'
    not_exist_bt5 = "erp5_not_exist"
    template_tool = self.portal.portal_templates
    getBusinessTemplateUrl = template_tool.getBusinessTemplateUrl

    # Test Exists
    self.assertEquals(getBusinessTemplateUrl(url_list, exist_bt5),
                  'https://svn.erp5.org/repos/public/erp5/trunk/bt5/erp5_base')
    self.assertEquals(getBusinessTemplateUrl(url_list[1:], exist_bt5),
                      'http://www.erp5.org/dists/snapshot/bt5/erp5_base.bt5')
    self.assertEquals(getBusinessTemplateUrl(url_list[2:], exist_bt5),
                      'http://www.erp5.org/dists/release/5.4.5/bt5/erp5_base.bt5')
    INSTANCE_HOME = getConfiguration().instancehome
    local_bt = None
    if os.path.exists(INSTANCE_HOME + "/bt5/erp5_base"):
      local_bt = 'file://' + INSTANCE_HOME + "/bt5/erp5_base"
    self.assertEquals(getBusinessTemplateUrl(url_list[3:], exist_bt5), local_bt)
    self.assertEquals(getBusinessTemplateUrl(url_list[4:], exist_bt5), None)

    # Test Not exists
    self.assertEquals(getBusinessTemplateUrl(url_list, not_exist_bt5), None)
    self.assertEquals(getBusinessTemplateUrl(url_list[1:], not_exist_bt5), None)
    self.assertEquals(getBusinessTemplateUrl(url_list[2:], not_exist_bt5), None)
    self.assertEquals(getBusinessTemplateUrl(url_list[3:], not_exist_bt5), None)
    self.assertEquals(getBusinessTemplateUrl(url_list[4:], not_exist_bt5), None)
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTemplateTool))
  return suite
