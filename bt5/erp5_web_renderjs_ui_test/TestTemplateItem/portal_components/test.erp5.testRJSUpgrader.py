# coding: utf-8
##############################################################################
#
# Copyright (c) 2018 Nexedi SA and Contributors. All Rights Reserved.
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
from six.moves import cStringIO as StringIO
import textwrap
import time

from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class RenderJSUpgradeTestCase(ERP5TypeTestCase):
  def afterSetUp(self):
    self.login()
    self.web_site = self.portal.web_site_module.newContent(
        portal_type='Web Site',
        skin_selection_name='RJS',
    )
    self.web_site.publish()
    self.manifest = self.portal.web_page_module.newContent(
        portal_type='Web Manifest',
        text_content="# empty",
        reference='{}.appcache'.format(self.id()),
    )
    self.manifest.publish()
    self.html_page = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        text_content="<b>content</b>",
        reference='{}.html'.format(self.id()))
    self.html_page.publish()
    self.javascript = self.portal.web_page_module.newContent(
        portal_type='Web Script',
        text_content="alert('hello !')",
        reference='{}.js'.format(self.id()))
    self.javascript.publish()


class TestRenderJSUpgrade(RenderJSUpgradeTestCase):
  """Test Upgrader scripts for renderjs UI.
  """
  def test_upgrade_empty_site(self):
    self.assertEqual([], self.web_site.checkConsistency())
    self.assertEqual([], self.web_site.fixConsistency())

  def test_upgrade_fix_pages_modification_date(self):
    # ERP5JS Web Sites define the list of pages to be cached using an
    # application cache manifest. We have a post-upgrade constraint which
    # checks that the manifest is more recent that the referenced files.
    manifest_content = textwrap.dedent(
        '''\
        CACHE MANIFEST
        # v1 - 2011-08-13
        # This is a comment.
        http://www.example.com/index.html

        {}
        {}
        NETWORK:
        *
        ''').format(
            self.html_page.getReference(), self.javascript.getReference())
    self.manifest.edit(text_content=manifest_content)
    self.web_site.setProperty(
        'configuration_manifest_url', self.manifest.getReference())
    self.tic()
    time.sleep(1)
    self.javascript.edit(text_content="alert('hello again !')")
    self.tic()

    self.assertLess(
        self.manifest.getModificationDate(),
        self.javascript.getModificationDate())
    self.assertEqual(
        [
            'Document {} is newer than cache manifest'.format(
                self.javascript.getReference()),
        ], [str(m.getMessage()) for m in self.web_site.checkConsistency()])
    self.web_site.fixConsistency()
    self.tic()

    self.assertEqual(
        [], [str(m.getMessage()) for m in self.web_site.checkConsistency()])
    self.assertGreater(
        self.manifest.getModificationDate(),
        self.javascript.getModificationDate())
    # Last modified... is insert at second line
    self.assertIn(
        'Last modified by WebSite_checkCacheModificationDateConsistency on',
        self.manifest.getTextContent().split('\n')[1])
    manifest_content_list = manifest_content.split('\n')
    self.assertIn(manifest_content_list[0] , self.manifest.getTextContent())
    self.assertIn('\n'.join(manifest_content_list[2:]) , self.manifest.getTextContent())

  def test_upgrade_site_with_non_existant_appcache(self):
    non_existant_appcache = 'gw4wA4qA4T9^s*L3WD="k]'
    self.web_site.setProperty(
        'configuration_manifest_url', non_existant_appcache)
    self.tic()
    self.assertEqual(
        [
          'Error: Web Site %s references a non existant appcache %s' % (self.web_site.getRelativeUrl(), non_existant_appcache)
        ], [str(m.getMessage()) for m in self.web_site.checkConsistency()])

  def test_upgrade_site_translation(self):
    test_upgrade_site_translation_data_js = self.portal.web_page_module.newContent(
        portal_type='Web Script',
        reference='test_upgrade_site_translation_data.js',
        text_content='// will be filled',
    )
    test_upgrade_site_translation_data_js.publish()
    test_upgrade_site_translation_data_js_modification_date = test_upgrade_site_translation_data_js.getModificationDate()

    test_upgrade_site_translation_data_html = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        reference='test_upgrade_site_translation.html',
        content_type='text/html',
        text_content=textwrap.dedent('''
            <!DOCTYPE html>
              <html>
                <head>
                  <meta charset="utf-8" />
                  <meta name="viewport" content="width=device-width" />
                  <title>Translation Gadget</title>
                  <link rel="http://www.renderjs.org/rel/interface" href="interface_translation.html">

                  <!-- renderjs -->
                  <script src="rsvp.js" type="text/javascript"></script>
                  <script src="renderjs.js" type="text/javascript"></script>

                  <!-- custom script -->
                  <script src="test_upgrade_site_translation_data.js" type="text/javascript"></script>
                  <script src="gadget_translation.js" type="text/javascript"></script>

                  </head>
                <body>
                </body>
              </html>
              '''),
      )
    test_upgrade_site_translation_data_html.publish()

    self.web_site.setProperty(
        'configuration_translation_gadget_url',
        'test_upgrade_site_translation.html',
    )
    self.web_site.setAvailableLanguageList(['en', 'fa'])
    self.tic()
    self.assertEqual(
        ['Translation data script content is not up to date'],
        [str(m.getMessage()) for m in self.web_site.checkConsistency()])
    self.web_site.fixConsistency()
    self.tic()

    self.assertEqual(
        [],
        [str(m.getMessage()) for m in self.web_site.checkConsistency()])
    self.assertIn(
        "window.translation_data = ",
        test_upgrade_site_translation_data_js.getTextContent())
    self.assertGreater(
        test_upgrade_site_translation_data_js.getModificationDate(),
        test_upgrade_site_translation_data_js_modification_date)


class TestRenderUpdateTranslationData(RenderJSUpgradeTestCase):
  """Tests for "Update Translation Data" utilities on RJS web sites.
  """
  def afterSetUp(self):
    super(TestRenderUpdateTranslationData, self).afterSetUp()
    # create a translation script for this web site
    self.web_script_translation_data_js = self.portal.web_page_module.newContent(
        portal_type='Web Script',
        # the convention is that this script has suffix translation_data.js
        reference='{}_translation_data.js'.format(self.id()),
        text_content='// will be filled',
    )
    self.web_script_translation_data_js.publish()
    self.web_page_translation_gadget = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        reference='{}_translation.html'.format(self.id()),
        content_type='text/html',
        text_content=textwrap.dedent('''
            <!DOCTYPE html>
              <html>
                <head>
                  <meta charset="utf-8" />
                  <meta name="viewport" content="width=device-width" />
                  <title>Translation Gadget</title>
                  <link rel="http://www.renderjs.org/rel/interface" href="interface_translation.html">

                  <!-- renderjs -->
                  <script src="rsvp.js" type="text/javascript"></script>
                  <script src="renderjs.js" type="text/javascript"></script>

                  <!-- custom script -->
                  <script src="{translation_data_js_reference}" type="text/javascript"></script>
                  <script src="gadget_translation.js" type="text/javascript"></script>

                  </head>
                <body>
                </body>
              </html>
              ''').format(translation_data_js_reference=self.web_script_translation_data_js.getReference()),
      )
    self.web_page_translation_gadget.publish()
    self.web_site.setProperty(
        'configuration_translation_gadget_url',
        self.web_page_translation_gadget.getReference()
    )

    self.web_site.setAvailableLanguageList(['en', 'fa'])

    # add a manifest to list web pages to extract messages from
    createZODBPythonScript(
        self.portal.portal_skins.custom,
        'WebSection_getTestPrecacheManifestList',
        '',
        textwrap.dedent('''
        return [
          'test_gadget_with_translation.html',
          'test_gadget_with_translation.js',
          'test_portal_skins_gadget.html',
        ]
        '''))
    self.web_site.setProperty(
        'configuration_precache_manifest_script_list',
        'WebSection_getTestPrecacheManifestList')
    self.tic()

  def beforeTearDown(self):
    super(TestRenderUpdateTranslationData, self).beforeTearDown()
    if 'test_gadget_with_translation_html' in self.portal.web_page_module.objectIds():
      self.portal.web_page_module.manage_delObjects(ids=['test_gadget_with_translation_html'])
      self.tic()

  def test_WebSite_getTranslationDataWebScriptValue(self):
    self.assertEqual(
        self.web_site.WebSite_getTranslationDataWebScriptValue(),
        self.web_script_translation_data_js)

  def test_Base_getTranslationSourceFileList(self):
    self.assertIn(
        'test_gadget_with_translation.html',
        self.web_site.Base_getTranslationSourceFileList())
    self.assertIn(
        'test_gadget_with_translation.js',
        self.web_site.Base_getTranslationSourceFileList())
    self.assertIn(
        'test_gadget_with_translation.html',
        self.web_site.Base_getTranslationSourceFileList(only_html=True))
    self.assertNotIn(
        'test_gadget_with_translation.js',
        self.web_site.Base_getTranslationSourceFileList(only_html=True))

  def test_WebSite_getTranslationDataTextContent_extract_from_web_page(self):
    self.portal.web_page_module.newContent(
        portal_type='Web Page',
        id='test_gadget_with_translation_html',
        reference='test_gadget_with_translation.html',
        text_content=textwrap.dedent('''
        <html>
          <!--
            data-i18n=Message in comments
            data-i18n="Quoted message in comments"
            data-i18n=Message with "some parts" 'quoted' in comments
            data-i18n=
          -->
          <h1 data-i18n="Message in attributes">Message in attributes</h1>
          <input type="submit" data-i18n="[value]Message for attribute" value="Message for attribute"></input>
          <h1 data-i18n="Message with {substitution}">Message with {substitution}</h1>
          <h1 data-i18n="Message with [square brackets]">Message with [square brackets]</h1>
          <div data-i18n="[html]Message in <a href='link'>HTML</a>">
          </div>
          <div data-i18n="">Empty data-i18n</div>
          <script>
            <span data-i18n="Message in script attributes">Message in script attributes</span>
          </script>
          <div data-i18n="メッサージュ"></div>
        ''')
    ).publish()
    self.tic()

    translation_data_text_content = self.web_site.WebSite_getTranslationDataTextContent()
    self.assertIn('"Message in comments":', translation_data_text_content)
    self.assertIn('"Quoted message in comments":', translation_data_text_content)
    self.assertIn('"Message with \\"some parts\\" \'quoted\' in comments":', translation_data_text_content)
    self.assertIn('"Message in attributes":', translation_data_text_content)
    self.assertIn('"Message for attribute":', translation_data_text_content)
    self.assertIn('"Message with {substitution}":', translation_data_text_content)
    self.assertIn('"Message with [square brackets]":', translation_data_text_content)
    self.assertIn('"Message in <a href=\'link\'>HTML</a>":', translation_data_text_content)
    self.assertIn('"Message in script attributes":', translation_data_text_content)
    self.assertIn('"メッサージュ":', translation_data_text_content)

  def test_WebSite_getTranslationDataTextContent_extract_from_page_template(self):
    self.portal.portal_skins.custom.manage_addProduct['PageTemplates'].manage_addPageTemplate(
        'test_portal_skins_gadget.html',
        text=textwrap.dedent('''
          <html>
          <!--
           data-i18n=Message from page template
           -->
          </html>'''))
    self.portal.changeSkin(None) # refresh skin cache
    translation_data_text_content = self.web_site.WebSite_getTranslationDataTextContent()
    self.assertIn('"Message from page template":', translation_data_text_content)

  def test_WebSite_getTranslationDataTextContent_extract_from_file(self):
    self.portal.portal_skins.custom.manage_addProduct['OFS'].manage_addFile(
        'test_portal_skins_gadget.html',
        file=StringIO(textwrap.dedent('''
          <html>
          <!--
           data-i18n=Message from file
           -->
          </html>''')))
    self.portal.changeSkin(None) # refresh skin cache
    translation_data_text_content = self.web_site.WebSite_getTranslationDataTextContent()
    self.assertIn('"Message from file":', translation_data_text_content)

  def test_WebSite_getTranslationDataTextContent_ignore_draft_web_page(self):
    self.portal.web_page_module.newContent(
        portal_type='Web Page',
        id='test_gadget_with_translation_html',
        reference='test_gadget_with_translation.html',
        text_content=textwrap.dedent('''
          <html>
          <!--
            data-i18n=Message in draft web page
          -->
          </html>'''))
    translation_data_text_content = self.web_site.WebSite_getTranslationDataTextContent()
    self.assertNotIn('"Message in draft web page":', translation_data_text_content)

  def test_WebSite_getTranslationDataTextContent_ignore_archived_web_page(self):
    web_page = self.portal.web_page_module.newContent(
        portal_type='Web Page',
        id='test_gadget_with_translation_html',
        reference='test_gadget_with_translation.html',
        text_content=textwrap.dedent('''
          <html>
          <!--
            data-i18n=Message in archived web page
          -->
          </html>'''))
    web_page.publish()
    web_page.archive()
    self.tic()
    translation_data_text_content = self.web_site.WebSite_getTranslationDataTextContent()
    self.assertNotIn('"Message in archived web page":', translation_data_text_content)
