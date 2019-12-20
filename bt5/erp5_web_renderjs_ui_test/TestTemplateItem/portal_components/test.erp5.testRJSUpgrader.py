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
    self.assertIn(
        'Last modified by WebSite_checkCacheModificationDateConsistency on',
        self.manifest.getTextContent())
    self.assertIn(manifest_content, self.manifest.getTextContent())

  def test_upgrade_fix_web_site_modification_date(self):
    # The web site root (/) must be more recent that the default page, because
    # rendering / renders a page containing the default page, but uses date
    # of the web site as modification date for HTTP cache headers.
    self.web_site.edit(aggregate_value=self.html_page)
    self.tic()
    time.sleep(1)
    self.html_page.edit(text_content="<p>Hello again</p>")
    self.tic()

    self.assertLess(
        self.web_site.getModificationDate(),
        self.html_page.getModificationDate()
        )
    self.assertEqual(
        ['Web Site is older than default page'],
        [str(m.getMessage()) for m in self.web_site.checkConsistency()])
    self.web_site.fixConsistency()
    self.tic()

    self.assertEqual(
        [], [str(m.getMessage()) for m in self.web_site.checkConsistency()])
    self.assertGreater(
        self.web_site.getModificationDate(),
        self.html_page.getModificationDate())
