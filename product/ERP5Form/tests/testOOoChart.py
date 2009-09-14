##############################################################################
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Deheunynck Thibaut <thibaut@nexedi.com>
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
import transaction
from Products.ERP5Form.Form import ERP5Form
from DocumentTemplate import String

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Form.Selection import Selection
from Testing import ZopeTestCase
from Products.ERP5OOo.tests.utils import Validator
from Acquisition import aq_base
from Globals import get_request
from Products.ERP5OOo.Document.OOoDocument import STANDARD_IMAGE_FORMAT_LIST
from Products.ERP5Type.Core.Folder import Folder

HTTP_OK = 200
debug = 0

class TestOOoChart(ERP5TypeTestCase, ZopeTestCase.Functional):
    """Tests OOoChart a and this render for ERP5."""
    form_id = 'TestOOochart_viewForm'
    ooo_chart_id = 'my_ooochart'
    nb_persons = 10
    content_type = 'application/vnd.oasis.opendocument.graphics'

    def getTitle(self):
      return 'Test OOoChart'

    def getBusinessTemplateList(self):
      return ('erp5_base', 'erp5_ui_test', 'erp5_odt_style', 'erp5_ods_style',)

    def afterSetUp(self):
      self.auth = 'ERP5TypeTestCase:'
      portal = self.getPortal()
      container = portal.portal_skins.custom
      if self.form_id not in container.objectIds():
        container._setObject(self.form_id, ERP5Form(self.form_id, 'View'))
        form = getattr(container, self.form_id)

        # create some persons in person_module
        self.createPersons()
        # add a ListBox field
        form.manage_addField('listbox', 'listbox', 'ListBox')
        form.listbox.ListBox_setPropertyList(field_list_method='zCountDocumentPerOwner',
                                field_count_method='',
                                field_columns=['owner | Owner',
                                              'owner_count | Owner Count',
                                              'number_count | Reference Count'],
                                )

        # create a Field OOoChart
        form.manage_addField(self.ooo_chart_id, self.ooo_chart_id, 'OOoChart')
        
        # create a Field OOoChart
        form.manage_addField('your_ooochart', 'your_ooochart', 'OOoChart')



        # create a ZSQL Method
        sql = """SELECT owner, count(uid) AS owner_count,
                count(reference) AS number_count
                FROM catalog
                WHERE portal_type = 'Person'
                GROUP BY owner ORDER BY owner_count DESC"""

        template = String(source_string=sql)
        container.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod('zCountDocumentPerOwner', 'zCountDocumentPerOwner', 'erp5_sql_connection', '', template)
        # enable preference
        preference = self.getPortal().portal_preferences.default_site_preference
        preference.setPriority(1)
        if preference.getPreferenceState() == 'disabled':
          self.getWorkflowTool().doActionFor(ob=preference,
                                            action='enable_action',
                                            wf_id='preference_workflow')

      self.validator = Validator()
      transaction.commit()
      self.tic()

    def createPersons(self):
      """ Create 10 persons in person_module """
      module = self.getPersonModule()
      if len(module.objectIds()) == 0:
        for i in range(self.nb_persons):
          module.newContent(portal_type='Person', id='person%s' % i)

    def _validate(self, odf_file_data):
      error_list = self.validator.validate(odf_file_data)
      if error_list:
        self.fail(''.join(error_list))

    def test_ooo_chart(self):
      portal = self.getPortal()
      # Does the form exist ?
      self.assertTrue(self.form_id in portal.portal_skins.custom.objectIds())
      getattr(aq_base(portal.portal_skins.custom), self.form_id)
      form = getattr(portal.portal_skins.custom, self.form_id)
      #listbox = form.listbox
      listbox = getattr(form, 'listbox')
      self.assertEquals(listbox.meta_type, 'ListBox')
      request = get_request()
      request['here'] = portal.portal_skins.custom
      line_list = [l for l in listbox.get_value('default',
                              render_format='list',
                              REQUEST=request) ]

      # listbox is empty?
      self.assertEquals(2, len(line_list))

      # Does the field OOoChart exist ?
      ooochart = getattr(form, self.ooo_chart_id)
      self.assertEquals(ooochart.meta_type, 'OOoChart')

      response = self.publish(
                    '/%s/%s/%s?render_format=&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      # test render raw
      self.assertEquals(HTTP_OK, response.getStatus())
      content_type = response.getHeader('content-type')

      # test content type : application/vnd.oasis.opendocument.graphics
      self.assertTrue(content_type.startswith(self.content_type), content_type)
      content_disposition = response.getHeader('content-disposition')
      self.assertEquals('inline', content_disposition.split(';')[0])
      # Test ODG (zip)
      body = response.getBody()
      # Test Validation Relax NG
      self._validate(body)

      from Products.ERP5OOo.OOoUtils import OOoParser
      parser = OOoParser()
      parser.openFromString(body)
      content_xml_view = parser.oo_files['content.xml']
      import libxml2
      doc_view = libxml2.parseDoc(content_xml_view)
      xpath = '//@*[name() = "xlink:href"]'
      num_object = doc_view.xpathEval(xpath)[0].content[2:]

      content_xml_build = parser.oo_files['%s/content.xml' % num_object]
      doc_build = libxml2.parseDoc(content_xml_build)
      xpath = '//@*[name() = "office:value"]'
      values = doc_build.xpathEval(xpath)
      # Test the data presence in the file XML
      self.assertNotEquals(0, len(values))
      # 2 values because there are - 10 document created by a owner 
      #                            - 0 Reference count
      self.assertEquals(2, len(values))

      # Test the differents render
      # render image
      for image_format in STANDARD_IMAGE_FORMAT_LIST:
        response = self.publish(
                      '/%s/%s/%s?render_format=%s&display=medium'
                      % (self.portal.getId(), self.form_id, self.ooo_chart_id, image_format), self.auth )
        self.assertEquals(HTTP_OK, response.getStatus(), '%s rendering failed: %s' % (image_format, response.getStatus()))

      # render pdf
      response = self.publish(
                    '/%s/%s/%s?render_format=pdf&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      self.assertEquals(HTTP_OK, response.getStatus())


      # Change some params  and restart (circle, bar, ...)
      # chart type : circle
      form.my_ooochart.manage_edit_xmlrpc(dict(chart_type='chart:circle'))
      response = self.publish(
                    '/%s/%s/%s?render_format=&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      # Test ODG (zip) with other params
      body = response.getBody()
      # Test Validation Relax NG
      self._validate(body)

      # chart type : line
      form.my_ooochart.manage_edit_xmlrpc(dict(chart_type='chart:line'))
      response = self.publish(
                    '/%s/%s/%s?render_format=&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      # Test ODG (zip) with other params
      body = response.getBody()
      # Test Validation Relax NG
      self._validate(body)

      #chart type : scatter
      form.my_ooochart.manage_edit_xmlrpc(dict(chart_type='chart:scatter'))
      response = self.publish(
                    '/%s/%s/%s?render_format=&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      # Test ODG (zip) with other params
      body = response.getBody()
      # Test Validation Relax NG
      self._validate(body)

    def test_proxy_ooo_chart(self):
      portal = self.getPortal()
      # Does the form exist ?
      self.assertTrue(self.form_id in portal.portal_skins.custom.objectIds())
      getattr(aq_base(portal.portal_skins.custom), self.form_id)
      form = getattr(portal.portal_skins.custom, self.form_id)

      #Proxify the Field my_ooochart
      form.proxifyField({self.ooo_chart_id:'TestOOochart_viewForm.your_ooochart'})
      # Does the field OOoChart exist ?
      ooochart = getattr(form, self.ooo_chart_id)
      self.assertEquals(ooochart.meta_type, 'ProxyField')
      response = self.publish(
                    '/%s/%s/%s?render_format=&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      # test render raw
      self.assertEquals(HTTP_OK, response.getStatus())
      content_type = response.getHeader('content-type')

      # test content type : application/vnd.oasis.opendocument.graphics
      self.assertTrue(content_type.startswith(self.content_type), content_type)
      content_disposition = response.getHeader('content-disposition')
      self.assertEquals('inline', content_disposition.split(';')[0])
      # Test ODG (zip)
      body = response.getBody()
      # Test Validation Relax NG
      self._validate(body)

      from Products.ERP5OOo.OOoUtils import OOoParser
      parser = OOoParser()
      parser.openFromString(body)
      content_xml_view = parser.oo_files['content.xml']
      import libxml2
      doc_view = libxml2.parseDoc(content_xml_view)
      xpath = '//@*[name() = "xlink:href"]'
      num_object = doc_view.xpathEval(xpath)[0].content[2:]

      content_xml_build = parser.oo_files['%s/content.xml' % num_object]
      doc_build = libxml2.parseDoc(content_xml_build)
      xpath = '//@*[name() = "office:value"]'
      values = doc_build.xpathEval(xpath)
      # Test the data presence in the file XML
      self.assertNotEquals(0, len(values))
      # 2 values because there are - 10 document created by a owner 
      #                            - 0 Reference count
      self.assertEquals(2, len(values))

      # Test the differents render
      # render image
      for image_format in STANDARD_IMAGE_FORMAT_LIST:
        response = self.publish(
                      '/%s/%s/%s?render_format=%s&display=medium'
                      % (self.portal.getId(), self.form_id, self.ooo_chart_id, image_format), self.auth )
        self.assertEquals(HTTP_OK, response.getStatus(), '%s rendering failed: %s' % (image_format, response.getStatus()))

      # render pdf
      response = self.publish(
                    '/%s/%s/%s?render_format=pdf&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      self.assertEquals(HTTP_OK, response.getStatus())


      # Change some params  and restart (circle, bar, ...)
      # chart type : circle
      form.my_ooochart.manage_edit_xmlrpc(dict(chart_type='chart:circle'))
      response = self.publish(
                    '/%s/%s/%s?render_format=&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      # Test ODG (zip) with other params
      body = response.getBody()
      # Test Validation Relax NG
      self._validate(body)

      # chart type : line
      form.my_ooochart.manage_edit_xmlrpc(dict(chart_type='chart:line'))
      response = self.publish(
                    '/%s/%s/%s?render_format=&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      # Test ODG (zip) with other params
      body = response.getBody()
      # Test Validation Relax NG
      self._validate(body)

      #chart type : scatter
      form.my_ooochart.manage_edit_xmlrpc(dict(chart_type='chart:scatter'))
      response = self.publish(
                    '/%s/%s/%s?render_format=&display=medium'
                    % (self.portal.getId(), self.form_id, self.ooo_chart_id), self.auth )
      # Test ODG (zip) with other params
      body = response.getBody()
      # Test Validation Relax NG
      self._validate(body)

    def test_ods_style(self):
      # simple rendering of a chart in ods style
      self.portal.changeSkin('ODS')
      response = self.publish(
          '/%s/%s' % (self.portal.getId(), self.form_id),
          self.auth,
          handle_errors=False )
      self.assertEquals(HTTP_OK, response.getStatus())
      body = response.getBody()
      self._validate(body)

    def test_odt_style(self):
      # simple rendering of a chart in odt style
      self.portal.changeSkin('ODT')
      response = self.publish(
          '/%s/%s' % (self.portal.getId(), self.form_id),
          self.auth,
          handle_errors=False )
      self.assertEquals(HTTP_OK, response.getStatus())
      body = response.getBody()
      self._validate(body)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOOoChart))
  return suite


