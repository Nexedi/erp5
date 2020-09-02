# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.Formulator.XMLToForm import XMLToForm
from Products.Formulator.FormToXML import formToXML
from Products.Formulator.TALESField import TALESMethod
from lxml import etree
from unittest import expectedFailure

class TestProxyField(ERP5TypeTestCase):
  """
  Check proxy field
  """

  def getTitle(self):
    return "TestProxyField"

  def changeSkin(self, skin_name):
    """
      Change current Skin
    """
    request = self.app.REQUEST
    self.getPortal().portal_skins.changeSkin(skin_name)
    request.set('portal_skin', skin_name)

  def beforeTearDown(self):
    """Remove objects created in tests."""
    # Remove forms
    custom_folder = self.getSkinsTool().custom
    custom_folder.manage_delObjects(custom_folder.objectIds())

    # Remove skin folders
    if 'erp5_geek' in self.getSkinsTool().objectIds():
      self.getSkinsTool().manage_delObjects(['erp5_geek'])
      ps = self.getSkinsTool()
      for skin_name, selection in ps.getSkinPaths():
        new_selection = []
        selection = selection.split(',')
        for skin_id in selection:
          if skin_id != 'erp5_geek':
            new_selection.append(skin_id)
        ps.manage_skinLayers(skinpath=tuple(new_selection),
                             skinname=skin_name, add_skin=1)

    if 'customized_geek' in self.getSkinsTool().objectIds():
      self.getSkinsTool().manage_delObjects(['customized_geek'])
      ps = self.getSkinsTool()
      for skin_name, selection in ps.getSkinPaths():
        new_selection = []
        selection = selection.split(',')
        for skin_id in selection:
          if skin_id != 'customized_geek':
            new_selection.append(skin_id)
        ps.manage_skinLayers(skinpath=tuple(new_selection),
                             skinname=skin_name, add_skin=1)
    self.commit()

  def testEmptySurchargedFieldLibrary(self):
    """
    This test checks that it is not required to duplicate all fields in a custom
    field library
    """
    portal_skins = self.getSkinsTool()
    my_title_value = 'Generic Title'
    # Create an empty field library
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('customized_geek')
    skin_folder = portal_skins._getOb('customized_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)

    # Create the default field library with a template field
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = portal_skins._getOb('erp5_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)
    form.manage_addField('my_title', my_title_value, 'StringField')

    # Custom field library has to have an higher priority
    selection = portal_skins.getSkinPath('View')
    selection = selection.split(',')
    selection.append('customized_geek')
    selection.append('erp5_geek')
    portal_skins.manage_skinLayers(skinpath=tuple(selection),
                                skinname='View', add_skin=1)
    portal_skins.getPortalObject().changeSkin(None)

    skin_folder = portal_skins._getOb('custom')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form('Base_viewGeek',
                                                          'View')
    form = skin_folder._getOb('Base_viewGeek', None)
    form.manage_addField('my_title', 'Title', 'ProxyField')
    field = form._getOb('my_title')
    field.manage_edit_xmlrpc(dict(
      form_id='Base_viewGeekFieldLibrary', field_id='my_title'))

    self.assertEqual(my_title_value, field.get_value('title'))

    # Reveal a bug, causes infinite loop when ProxyField.getTemplateField
    # returns the proxyfield itself.
    # This is caused by the acquisition context
    self.assertRaises(KeyError, self.portal.portal_skins.custom.Base_viewGeek.\
        my_title.Base_viewGeekFieldLibrary.my_title.get_value, 'ANYTHING_WHICH_RAISES_KEY_ERROR')

  def testPathOfTemplateField(self):
    """
    This test checks if it is possible to specify the skin folder of a form
    """
    portal_skins = self.getSkinsTool()
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('customized_geek')
    skin_folder = portal_skins._getOb('customized_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)
    form.manage_addField('my_title', 'Customized Title', 'StringField')

    portal_skins.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = portal_skins._getOb('erp5_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)
    form.manage_addField('my_title', 'Generic Title', 'StringField')

    # Custom field library has to have an higher priority
    selection = portal_skins.getSkinPath('View')
    selection = selection.split(',')
    selection.append('customized_geek')
    selection.append('erp5_geek')
    portal_skins.manage_skinLayers(skinpath=tuple(selection),
                                skinname='View', add_skin=1)
    portal_skins.getPortalObject().changeSkin(None)

    skin_folder = portal_skins._getOb('custom')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form('Base_viewGeek',
                                                          'View')
    form = skin_folder._getOb('Base_viewGeek', None)
    form.manage_addField('my_title', 'Title', 'ProxyField')
    field = getattr(form, 'my_title')
    # Explicitely enter skin folder of the template field's form
    field.manage_edit_xmlrpc(dict(
      form_id='erp5_geek/Base_viewGeekFieldLibrary', field_id='my_title'))

    self.assertEqual('Generic Title', field.get_value('title'))

  @expectedFailure
  def testSkinSelectionTemplateField(self):
    """
    Check that proxy field values are generated from the current skin selection
    """
    portal_skins = self.getSkinsTool()
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('customized_geek')
    skin_folder = portal_skins._getOb('customized_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)
    form.manage_addField('my_title', 'Customized Title', 'StringField')

    portal_skins.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = portal_skins._getOb('erp5_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)
    form.manage_addField('my_title', 'Generic Title', 'StringField')

    selection = portal_skins.getSkinPath('View')
    selection = selection.split(',')
    selection.append('customized_geek')
    selection.append('erp5_geek')
    portal_skins.addSkinSelection('CustomizedView', ','.join(selection))

    selection = portal_skins.getSkinPath('View')
    selection = selection.split(',')
    selection.append('erp5_geek')
    selection.append('customized_geek')
    portal_skins.addSkinSelection('GenericView', ','.join(selection))

    # XXX KeyError is raised if skin selection View is not modified.
    # This part has to be removed has soon as this bug is fixed
    selection = portal_skins.getSkinPath('View')
    portal_skins.manage_skinLayers(skinpath=tuple(selection),
                                skinname='View')

    portal_skins.getPortalObject().changeSkin(None)

    skin_folder = portal_skins._getOb('custom')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form('Base_viewGeek',
                                                          'View')
    form = skin_folder._getOb('Base_viewGeek', None)
    form.manage_addField('my_title', 'Title', 'ProxyField')
    field = getattr(form, 'my_title')
    field.manage_edit_xmlrpc(dict(
      form_id='Base_viewGeekFieldLibrary', field_id='my_title'))
    self.commit()

    self.assertEqual(None, field.get_value('title'))
    self.changeSkin('GenericView')
    self.assertEqual('Generic Title', field.get_value('title'))
    self.changeSkin('CustomizedView')
    self.assertEqual('Customized Title', field.get_value('title'))

  def testEmptySurchargedFieldLibrary_acquisition(self):
    """
    This test checks that it is not required to duplicate all fields in a custom
    field library, and field is well return in portal acquisition context
    """
    portal_skins = self.getSkinsTool()
    my_title_value = 'Generic Title'
    # Create an empty field library
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('customized_geek')
    skin_folder = portal_skins._getOb('customized_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)

    # Create the default field library with a template field
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = portal_skins._getOb('erp5_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)
    form.manage_addField('my_title', my_title_value, 'StringField')

    # Custom field library has to have an higher priority
    selection = portal_skins.getSkinPath('View')
    selection = selection.split(',')
    selection.append('customized_geek')
    selection.append('erp5_geek')
    portal_skins.manage_skinLayers(skinpath=tuple(selection),
                                skinname='View', add_skin=1)
    portal_skins.getPortalObject().changeSkin(None)

    skin_folder = portal_skins._getOb('custom')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form('Base_viewGeek',
                                                          'View')
    form = skin_folder._getOb('Base_viewGeek', None)
    form.manage_addField('my_title', 'Title', 'ProxyField')
    field = form._getOb('my_title')
    field.manage_edit_xmlrpc(dict(
      form_id='Base_viewGeekFieldLibrary', field_id='my_title'))

    # Check that acquisition wrapper fits
    # restricted environment requirements.
    # If object returned is not wrapped in portal context,
    # current user is not Found in current context
    # then Unauthorized Exception is raised.
    python_script_id = "ERP5Site_testAccessProxyFieldProperty"
    python_script_parameter = "proxy_field"
    python_script_body = """
print proxy_field.getRecursiveTemplateField().meta_type
return printed
"""
    skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(
                                                id=python_script_id)
    python_script_object = skin_folder._getOb(python_script_id)
    python_script_object.ZPythonScript_edit(python_script_parameter,
                                            python_script_body)
    python_script_object(field)

  def test_serializeProxyField(self):
    """Test formToXML and XMLToForm with proxyfields.
    """
    portal_skins = self.getSkinsTool()
    # Create the default field library with a template field
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = portal_skins._getOb('erp5_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeekFieldLibrary',
        'View')
    form = skin_folder._getOb('Base_viewGeekFieldLibrary', None)
    form.manage_addField('my_title', 'My Geek Title', 'StringField')

    # Custom field library has to have an higher priority
    selection = portal_skins.getSkinPath('View')
    selection = selection.split(',')
    selection.append('erp5_geek')
    portal_skins.manage_skinLayers(skinpath=tuple(selection),
                                skinname='View', add_skin=1)
    portal_skins.getPortalObject().changeSkin(None)

    skin_folder = portal_skins._getOb('custom')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form('Base_viewGeek',
                                                          'View')
    form = skin_folder._getOb('Base_viewGeek', None)
    form.manage_addField('my_title', 'Title', 'ProxyField')
    field = form._getOb('my_title')
    field.manage_edit_xmlrpc(dict(
      form_id='Base_viewGeekFieldLibrary', field_id='my_title'))
    my_title = 'My Custom Proxy Title'
    field.manage_edit_surcharged_xmlrpc({'title': my_title})

    # Test xml serialisation of form.
    xml_string = formToXML(form)
    xml_tree = etree.fromstring(xml_string)
    field_node = xml_tree.find('groups/group/fields/field')
    self.assertEqual(field_node.find('type').text, 'ProxyField')
    self.assertTrue(field_node.find('delegated_list/title') is not None)

    skin_folder.manage_addProduct['ERP5Form'].addERP5Form('Base_viewSuperGeek',
                                                          'View')
    form = skin_folder._getOb('Base_viewSuperGeek')
    # Test objectification of XML
    XMLToForm(xml_string, form)
    self.assertTrue(form.my_title.get_value('title'), my_title)

  def test_proxifyParallelListField(self):
    """ParallelListField has its own get_value method and the method does
    different from the original one. This test checks if ProxyField can
    behave the same as ParallelListField.
    """
    # Setup
    if getattr(self.portal.portal_categories, 'colour', None) is None:
      self.portal.portal_categories.newContent('colour')
    if getattr(self.portal.portal_categories, 'size', None) is None:
      self.portal.portal_categories.newContent('size')

    portal_skins = self.getSkinsTool()
    # Create skin folder
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = portal_skins._getOb('erp5_geek')

    skin_folder.manage_addProduct['ERP5Form'].addERP5Form('Base_viewGeek1',
                                                          'View')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form('Base_viewGeek2',
                                                          'View')

    form_1 = skin_folder.Base_viewGeek1
    # Add a parallel list field
    form_1.manage_addField('my_field', '', 'ParallelListField')
    form_1.my_field.manage_tales_xmlrpc(
      dict(default="python:['colour/blue']",
           items="python: [['Blue', 'colour/blue'], ['Red', 'colour/red'], ['Large', 'size/large'], ['Small', 'size/small']]"))
    form_1.my_field.manage_edit_xmlrpc(
      dict(hash_script_id="Base_getMultiListFieldPropertyDictList"))

    form_2 = skin_folder.Base_viewGeek2
    # Add a proxy field which has the same configuration as above field.
    form_2.manage_addField('my_field', '', 'ProxyField')
    form_2.my_field.manage_edit_xmlrpc(dict(form_id='Base_viewFieldLibrary',
                                            field_id='my_parallel_list_field'))
    form_2.my_field._surcharged_edit(
      dict(hash_script_id="Base_getMultiListFieldPropertyDictList"),
      ['hash_script_id'])
    form_2.my_field._surcharged_tales(
      dict(default=TALESMethod("python:['colour/blue']"),
           items=TALESMethod("python: [['Blue', 'colour/blue'], ['Red', 'colour/red'], ['Large', 'size/large'], ['Small', 'size/small']]")),
      ['default', 'items', 'hash_script_id'])

    # Compare
    # XXX Remove new lines. An extra new line is inserted by unknown reason.
    form_1_html = form_1.my_field.render(REQUEST=self.app.REQUEST).replace('\n', '')
    form_2_html = form_2.my_field.render(REQUEST=self.app.REQUEST).replace('\n', '')
    self.assertEqual(form_1_html, form_2_html)

  def test_broken_proxy_field(self):
    portal_skins = self.getSkinsTool()
    portal_skins.manage_addProduct['OFSP'].manage_addFolder('erp5_geek')
    skin_folder = portal_skins._getOb('erp5_geek')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewGeek',
        'View')
    form = skin_folder._getOb('Base_viewGeek', None)
    form.manage_addField('my_title', 'Title', 'ProxyField')

    field = getattr(form, 'my_title')

    self.assertIsNone(field.getTemplateField())
    self.assertEqual('', field.render())
    self.assertEqual('', field.get_tales('default'))
    self.assertIsNone(field.get_value('default'))

    with self.assertRaisesRegexp(
        AttributeError,
        'The proxy field <ProxyField at /%s/portal_skins/erp5_geek/Base_viewGeek/my_title> cannot find a template field'
        % self.portal.getId()):
      field.get_recursive_tales('default')
