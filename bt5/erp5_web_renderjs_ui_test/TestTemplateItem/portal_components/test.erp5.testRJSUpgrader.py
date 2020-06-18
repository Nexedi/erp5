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
import textwrap
import time

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestRenderJSUpgrade(ERP5TypeTestCase):
  """Test Upgrader scripts for renderjs UI.
  """
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
