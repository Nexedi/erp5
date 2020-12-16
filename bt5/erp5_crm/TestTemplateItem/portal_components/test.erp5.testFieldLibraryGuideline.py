# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#               Romain Courteaud <romain@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList

class TestFieldLibraryGuideline(ERP5TypeTestCase):
  business_template_title = 'erp5_geek'
  skin_folder_name = 'erp5_geek'
  field_library_id = 'Base_viewGeekFieldLibrary'
  wrong_field_library_id = 'Geek_viewFieldLibrary'
  form_id = 'Base_viewGeek'

  def getTitle(self):
    return "Field Library Guideline Test"

  def getBusinessTemplateList(self):
    """  """
    return (
      'erp5_base',
      'erp5_crm',
      'erp5_administration',
      )

  def beforeTearDown(self):
    """
    Remove objects created in tests.
    """
    # Remove skin folder
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
    self.commit()

  def stepCreateSkinFolder(self, sequence=None, sequence_list=None, **kw):
    """
    Create a skin folder
    """
    ps = self.getSkinsTool()
    ps.manage_addProduct['OFSP'].manage_addFolder(self.skin_folder_name)
    skin_folder = ps._getOb(self.skin_folder_name, None)
    self.assertTrue(skin_folder is not None)
    sequence.edit(skin_folder_id=skin_folder.getId())
    # add skin in layers
    for skin_name, selection in ps.getSkinPaths():
      selection = selection.split(',')
      selection.append(self.skin_folder_name)
      ps.manage_skinLayers(skinpath=tuple(selection), skinname=skin_name,
                           add_skin=1)

  def stepCreateNewBusinessTemplate(self, sequence=None,
                                    sequence_list=None, **kw):
    """
    Create a new Business Template
    """
    template_tool = self.getTemplateTool()
    template = template_tool.newContent(
        portal_type='Business Template',
        title=self.business_template_title,
        template_skin_id_list=[self.skin_folder_name])
    sequence.edit(custom_business_template=template)

  def stepCheckMissingFieldLibrary(self, sequence=None,
                                   sequence_list=None, **kw):
    """
    Check that the dialog propose to create the field library
    """
    business_template = sequence.get('custom_business_template')
    modifiable_field_list = \
        business_template.BusinessTemplate_getModifiableFieldList()
    self.assertEqual(1, len(modifiable_field_list))
    modifiable_field = modifiable_field_list[0]
    self.assertEqual('1_create_form', modifiable_field.choice[0])
    self.assertEqual('%s/%s' % (self.skin_folder_name, self.field_library_id),
                      modifiable_field.object_id)

  def test_01_missingFieldLibrary(self):
    """
    Create an business template with an empty skin folder.
    Check that the 'Manage Field Library' action propose to create the field
    library.
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateNewBusinessTemplate \
                       CheckMissingFieldLibrary \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def createForm(self, form_id):
    skin_tool = self.getSkinsTool()
    skin_folder = skin_tool._getOb(self.skin_folder_name)
    addERP5Form = skin_folder.manage_addProduct['ERP5Form'].addERP5Form
    addERP5Form(form_id, 'View')
    return skin_folder._getOb(form_id)

  def stepCreateFieldLibrary(self, sequence=None,
                             sequence_list=None, **kw):
    """
    Create a Field Library
    """
    form = self.createForm(self.field_library_id)
    sequence.edit(field_library=form)

  def stepCreateForm(self, sequence=None,
                     sequence_list=None, **kw):
    """
    Create a Form
    """
    form = self.createForm(self.form_id)
    sequence.edit(form=form)

  def stepCreateNotProxifiedField(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Create a not proxified field
    """
    form = sequence.get('form')
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_title', 'Title', 'StringField')

  def stepCheckToProxifyField(self, sequence=None,
                         sequence_list=None, **kw):
    """
    Check that the dialog propose to proxify the field
    """
    business_template = sequence.get('custom_business_template')
    modifiable_field_list = \
        business_template.BusinessTemplate_getModifiableFieldList()
    self.assertEqual(1, len(modifiable_field_list))
    modifiable_field = modifiable_field_list[0]
    self.assertEqual('0_keep_non_proxy_field',
                      modifiable_field.choice_item_list[0][1])
    self.assertEqual('%s/%s/my_title' % (self.skin_folder_name,
                                          self.form_id),
                      modifiable_field.object_id)

  def test_02_notProxifiedField(self):
    """
    Create an business template with a skin folder containing a Field Library.
    Add a form to the skin folder.
    Add a not proxified field inside this form.
    Check that the 'Manage Field Library' action propose to proxify the field.
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateFieldLibrary \
                       CreateForm \
                       CreateNotProxifiedField \
                       CreateNewBusinessTemplate \
                       CheckToProxifyField \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateDeadProxyField(self, sequence=None,
                               sequence_list=None, **kw):
    """
    Create a dead proxy field
    """
    form = sequence.get('form')
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_title', 'Title', 'ProxyField')

  def stepCheckDeadFieldDetection(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check that the dialog detects the dead proxy field
    """
    business_template = sequence.get('custom_business_template')
    modifiable_field_list = \
        business_template.BusinessTemplate_getModifiableFieldList()
    self.assertEqual(1, len(modifiable_field_list))
    modifiable_field = modifiable_field_list[0]
    self.assertEqual('0_keep_dead_proxy_field',
                      modifiable_field.choice_item_list[0][1])
    self.assertEqual('%s/%s/my_title' % (self.skin_folder_name,
                                          self.form_id),
                      modifiable_field.object_id)

  def test_03_deadProxyField(self):
    """
    Create an business template with a skin folder containing a Field Library.
    Add a form to the skin folder.
    Add a dead proxy field inside this form.
    Check that the 'Manage Field Library' detects this dead proxy field.
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateFieldLibrary \
                       CreateForm \
                       CreateDeadProxyField \
                       CreateNewBusinessTemplate \
                       CheckDeadFieldDetection \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateTemplateField(self, sequence=None,
                               sequence_list=None, **kw):
    """
    Create a template field
    """
    form = sequence.get('field_library')
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_title', 'Title', 'ProxyField')

  def stepCheckUnusedTemplateFieldDetection(self, sequence=None,
                                            sequence_list=None, **kw):
    """
    Check that the dialog detects this unused proxy field.
    """
    business_template = sequence.get('custom_business_template')
    modifiable_field_list = \
        business_template.BusinessTemplate_getModifiableFieldList()
    self.assertEqual(1, len(modifiable_field_list))
    modifiable_field = modifiable_field_list[0]
    self.assertEqual('0_unused_proxy_field',
                      modifiable_field.choice_item_list[0][1])
    self.assertEqual('%s/%s/my_title' % (self.skin_folder_name,
                                          self.field_library_id),
                      modifiable_field.object_id)

  def test_04_unusedProxyField(self):
    """
    Create an business template with a skin folder containing a Field Library.
    Add a template field inside the field library.
    Check that the 'Manage Field Library' detects this unused proxy field.
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateFieldLibrary \
                       CreateTemplateField \
                       CreateNewBusinessTemplate \
                       CheckUnusedTemplateFieldDetection \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateWronglyProxifiedField(self, sequence=None,
                                      sequence_list=None, **kw):
    """
    Create a wrong proxy field
    """
    form = sequence.get('form')
    addField = form.manage_addProduct['Formulator'].manage_addField
    addField('my_title', 'Title', 'ProxyField')
    field = getattr(form, 'my_title')
    field.manage_edit_xmlrpc(dict(
            form_id='Organisation_view',
            field_id='my_title'))

  def stepCheckWrongProxificationDetection(self, sequence=None,
                                           sequence_list=None, **kw):
    """
    Check that the dialog detects the wrong proxification.
    """
    business_template = sequence.get('custom_business_template')
    modifiable_field_list = \
        business_template.BusinessTemplate_getModifiableFieldList()
    self.assertEqual(1, len(modifiable_field_list))
    modifiable_field = modifiable_field_list[0]
    self.assertEqual('2_unproxify_field',
                      modifiable_field.choice_item_list[0][1])
    self.assertEqual('%s/%s/my_title' % (self.skin_folder_name,
                                          self.form_id),
                      modifiable_field.object_id)

  def test_05_wrongProxification(self):
    """
    Create an business template with a skin folder containing a Field Library.
    Add a form to the skin folder.
    Add a proxy field (inside this form) linking to another Field Library.

    Check that the 'Manage Field Library' detects this wrong proxification.
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateFieldLibrary \
                       CreateForm \
                       CreateWronglyProxifiedField \
                       CreateNewBusinessTemplate \
                       CheckWrongProxificationDetection \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCreateWrongFieldLibrary(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Create a Field Library with a wrong name.
    """
    form = self.createForm(self.wrong_field_library_id)
    sequence.edit(wrong_field_library=form)

  def stepCheckWrongFieldLibraryDetection(self, sequence=None,
                                          sequence_list=None, **kw):
    """
    Check that the dialog detects the wrong field library.
    """
    business_template = sequence.get('custom_business_template')
    modifiable_field_list = \
        business_template.BusinessTemplate_getModifiableFieldList()
    self.assertEqual(1, len(modifiable_field_list))
    modifiable_field = modifiable_field_list[0]
    self.assertEqual('4_delete_form', modifiable_field.choice[0])
    self.assertEqual('%s/%s' % (self.skin_folder_name,
                                 self.wrong_field_library_id),
                      modifiable_field.object_id)

  def test_06_wrongFieldLibrary(self):
    """
    Create an business template with a skin folder containing a Field Library.
    Add aother field library in this skin folder.
    Check that the 'Manage Field Library' detects this wrong field library.
    """
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateSkinFolder \
                       CreateFieldLibrary \
                       CreateWrongFieldLibrary \
                       CreateNewBusinessTemplate \
                       CheckWrongFieldLibraryDetection \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFieldLibraryGuideline))
  return suite
