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

from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
import transaction
import unittest

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

  def testEmptySurchargedFieldLibrary(self):
    """
    This test checks that it is not required to duplicate all fields in a custom
    field library
    """
    portal_skins = self.getSkinsTool()
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
    field.manage_edit_xmlrpc(dict(
      form_id='Base_viewGeekFieldLibrary', field_id='my_title'))

    self.assertEquals('Generic Title', field.get_value('title'))

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

    self.assertEquals('Generic Title', field.get_value('title'))

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

    self.assertEquals(None, field.get_value('title'))
    self.changeSkin('GenericView')
    self.assertEquals('Generic Title', field.get_value('title'))
    self.changeSkin('CustomizedView')
    self.assertEquals('Customized Title', field.get_value('title'))
