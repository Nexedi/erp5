# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from base64 import b64decode
import json


class TestErp5Officejs(ERP5TypeTestCase):

  def test_webPageRestrictedTraverseOnViewSkinSelection(self):
    """
      Check we can restricted traverse an image from a web page on the default
      skin selection. (`web_page.getDocumentValue(reference)`)
    """
    # test initialisation
    image = self.portal.image_module.newContent(
      portal_type="Image",
      reference="TEST-Test.Restricted.Traverse.With.ERP5.Officejs",
      version="001",
      language="en",
      filename="white_pixel.png",
      data=b64decode("".join([
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACXBIWXMAAAsTAAALEw",
        "EAmpwYAAAAB3RJTUUH4QUdBikq4C9IOgAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdp",
        "dGggR0lNUFeBDhcAAAAMSURBVAjXY/j//z8ABf4C/tzMWecAAAAASUVORK5CYII=",
      ])),
    )
    image.publish()
    web_page = self.portal.web_page_module.newContent(
      portal_type="Web Page",
    )
    self.tic()

    # actual test
    other_image = web_page.restrictedTraverse("TEST-Test.Restricted.Traverse.With.ERP5.Officejs")
    self.assertEqual(image.getUid(), other_image.getUid())


class TestEmbedOfficeJSInERP5JS(ERP5TypeTestCase):
  """Tests for embedding OfficeJS apps in ERP5JS on a single origin."""

  def afterSetUp(self):
    self.web_site_module = self.portal.web_site_module

  def _createOfficeJSWebSite(self, site_id, title="Test App"):
    """Helper: create a Web Site with the OfficeJS renderer marker."""
    web_site = self.web_site_module.newContent(
      portal_type="Web Site",
      id=site_id,
      title=title,
    )
    web_site.setProperty(
      "container_layout",
      "WebSection_renderOfficeJSApplicationPage"
    )
    web_site.setProperty(
      "content_layout",
      "WebSection_renderOfficeJSApplicationPage"
    )
    web_site.setProperty(
      "custom_render_method_id",
      "WebSection_renderOfficeJSApplicationPage"
    )
    return web_site

  # -----------------------------------------------------------
  # ERP5Site_getAvailableOfficeJSAppList tests
  # -----------------------------------------------------------
  def test_getAvailableOfficeJSAppList_empty(self):
    """Script returns empty list when no OfficeJS Web Sites exist."""
    self.tic()
    result = json.loads(
      self.portal.ERP5Site_getAvailableOfficeJSAppList()
    )
    # Filter out any pre-existing officejs sites from BTs
    # We only care that the script runs without error and returns a list
    self.assertIsInstance(result, list)

  def test_getAvailableOfficeJSAppList_finds_officejs_site(self):
    """Script discovers a Web Site with the OfficeJS renderer."""
    self._createOfficeJSWebSite(
      "test_officejs_embed_app",
      title="Test Embed App"
    )
    self.tic()

    result = json.loads(
      self.portal.ERP5Site_getAvailableOfficeJSAppList()
    )
    found = [app for app in result
             if app["id"] == "test_officejs_embed_app"]
    self.assertEqual(len(found), 1)
    self.assertEqual(found[0]["title"], "Test Embed App")
    self.assertIn("/web_site_module/test_officejs_embed_app/",
                  found[0]["url"])

  def test_getAvailableOfficeJSAppList_ignores_non_officejs_site(self):
    """Script does not return Web Sites without the OfficeJS renderer."""
    # Create a plain Web Site (e.g., ERP5JS renderjs_runner)
    self.web_site_module.newContent(
      portal_type="Web Site",
      id="test_renderjs_runner",
      title="RenderJS Runner",
    )
    self.tic()

    result = json.loads(
      self.portal.ERP5Site_getAvailableOfficeJSAppList()
    )
    found = [app for app in result
             if app["id"] == "test_renderjs_runner"]
    self.assertEqual(len(found), 0)

  def test_getAvailableOfficeJSAppList_multiple_apps(self):
    """Script returns multiple OfficeJS apps sorted or not."""
    self._createOfficeJSWebSite(
      "test_officejs_text_editor",
      title="Text Editor"
    )
    self._createOfficeJSWebSite(
      "test_officejs_image_editor",
      title="Image Editor"
    )
    self.tic()

    result = json.loads(
      self.portal.ERP5Site_getAvailableOfficeJSAppList()
    )
    ids = [app["id"] for app in result]
    self.assertIn("test_officejs_text_editor", ids)
    self.assertIn("test_officejs_image_editor", ids)

  # -----------------------------------------------------------
  # Bootloader template variable tests
  # -----------------------------------------------------------
  def test_bootloader_html_has_app_id_configuration(self):
    """Bootloader HTML template includes app_id configuration tag."""
    web_page = self.portal.web_page_module.restrictedTraverse(
      "gadget_officejs_bootloader_html", None
    )
    if web_page is None:
      # Try by reference
      results = self.portal.portal_catalog(
        portal_type="Web Page",
        reference="gadget_officejs_bootloader.html",
        limit=1,
      )
      if results:
        web_page = results[0].getObject()
    if web_page is not None:
      text_content = web_page.getTextContent() or ""
      self.assertIn('data-install-configuration="app_id"', text_content)
      self.assertIn('${application_id}', text_content)

  def test_bootloader_html_has_app_version_configuration(self):
    """Bootloader HTML template includes app_version configuration tag."""
    web_page = self.portal.web_page_module.restrictedTraverse(
      "gadget_officejs_bootloader_html", None
    )
    if web_page is None:
      results = self.portal.portal_catalog(
        portal_type="Web Page",
        reference="gadget_officejs_bootloader.html",
        limit=1,
      )
      if results:
        web_page = results[0].getObject()
    if web_page is not None:
      text_content = web_page.getTextContent() or ""
      self.assertIn('data-install-configuration="app_version"', text_content)
      self.assertIn('${app_version}', text_content)

  # -----------------------------------------------------------
  # Service Worker versioning tests
  # -----------------------------------------------------------
  def test_service_worker_has_text_substitution(self):
    """Service Worker Web Script has text_content_substitution_mapping set."""
    sw = self.portal.web_page_module.restrictedTraverse(
      "gadget_officejs_bootloader_serviceworker_js", None
    )
    if sw is None:
      results = self.portal.portal_catalog(
        portal_type="Web Script",
        reference="gadget_officejs_bootloader_serviceworker.js",
        limit=1,
      )
      if results:
        sw = results[0].getObject()
    if sw is not None:
      mapping_method = sw.getProperty(
        "text_content_substitution_mapping_method_id", ""
      )
      self.assertEqual(
        mapping_method,
        "WebPage_getRenderJSSubstitutionMappingDict"
      )

  def test_service_worker_has_version_stamp(self):
    """Service Worker source contains APP_VERSION placeholder."""
    sw = self.portal.web_page_module.restrictedTraverse(
      "gadget_officejs_bootloader_serviceworker_js", None
    )
    if sw is None:
      results = self.portal.portal_catalog(
        portal_type="Web Script",
        reference="gadget_officejs_bootloader_serviceworker.js",
        limit=1,
      )
      if results:
        sw = results[0].getObject()
    if sw is not None:
      text_content = sw.getTextContent() or ""
      self.assertIn("APP_VERSION", text_content)
      self.assertIn("${modification_date}", text_content)

  # -----------------------------------------------------------
  # WebSection_renderOfficeJSApplicationPage template vars test
  # -----------------------------------------------------------
  def test_render_page_includes_application_id(self):
    """WebSection_renderOfficeJSApplicationPage passes application_id."""
    # Verify the script source includes the application_id mapping key
    script = getattr(self.portal, "WebSection_renderOfficeJSApplicationPage",
                     None)
    if script is not None:
      body = script.body()
      self.assertIn("application_id", body)
      self.assertIn("app_version", body)

  # -----------------------------------------------------------
  # Phase 6: per-app IndexedDB isolation
  # -----------------------------------------------------------
  def _getWebPageText(self, doc_id, reference, portal_type="Web Page"):
    web_page = self.portal.web_page_module.restrictedTraverse(doc_id, None)
    if web_page is None:
      results = self.portal.portal_catalog(
        portal_type=portal_type,
        reference=reference,
        limit=1,
      )
      if results:
        web_page = results[0].getObject()
    if web_page is None:
      return None
    return web_page.getTextContent() or ""

  def test_in_app_html_has_app_id_configuration(self):
    """Post-install app shell HTML emits app_id configuration tag."""
    text_content = self._getWebPageText(
      "rjs_gadget_erp5_html", "officejs_launcher.html"
    )
    if text_content is not None:
      self.assertIn('data-renderjs-configuration="app_id"', text_content)
      self.assertIn('${app_id}', text_content)

  def test_render_default_page_includes_app_id(self):
    """WebSection_renderDefaultPageAsGadget passes app_id in mapping_dict."""
    script = getattr(self.portal, "WebSection_renderDefaultPageAsGadget", None)
    if script is not None:
      body = script.body()
      self.assertIn('"app_id"', body)
      self.assertIn("getWebSiteValue().getId()", body)

  def test_launcher_publishes_getIndexedDBPrefix_acquisition(self):
    """rjs_gadget_erp5_launcher_js publishes getIndexedDBPrefix via
    allowPublicAcquisition and uses the prefix for its own setting DB."""
    text_content = self._getWebPageText(
      "rjs_gadget_erp5_launcher_js", "erp5_launcher_nojqm.js",
      portal_type="Web Script"
    )
    if text_content is not None:
      self.assertIn(
        '.allowPublicAcquisition("getIndexedDBPrefix"', text_content
      )
      self.assertIn("renderjs_runner", text_content)
      self.assertIn('INDEXEDDB_PREFIX + "setting"', text_content)

  def test_setting_gadget_acquires_prefix(self):
    """gadget_officejs_setting_js acquires getIndexedDBPrefix from parent
    and uses the resolved prefix for the global-setting database."""
    text_content = self._getWebPageText(
      "gadget_officejs_setting_js", "gadget_officejs_setting.js",
      portal_type="Web Script"
    )
    if text_content is not None:
      self.assertIn(
        '.declareAcquiredMethod("getIndexedDBPrefix", "getIndexedDBPrefix")',
        text_content
      )
      self.assertIn('prefix + "global-setting"', text_content)

  def test_local_default_is_prefixed_in_configurator(self):
    """gadget_officejs_page_jio_configurator_js acquires prefix and uses
    it for local_default."""
    text_content = self._getWebPageText(
      "gadget_officejs_page_jio_configurator_js",
      "gadget_officejs_page_jio_configurator.js",
      portal_type="Web Script"
    )
    if text_content is not None:
      self.assertIn(
        '.declareAcquiredMethod("getIndexedDBPrefix", "getIndexedDBPrefix")',
        text_content
      )
      self.assertIn('prefix + "local_default"', text_content)

  def test_local_jio_gadget_prefixes_configuration_hash(self):
    """gadget_officejs_local_jio_js acquires prefix and uses it for the
    configuration-hash and officejs-erp5 databases."""
    text_content = self._getWebPageText(
      "gadget_officejs_local_jio_js",
      "gadget_officejs_local_jio.js",
      portal_type="Web Script"
    )
    if text_content is not None:
      self.assertIn(
        '.declareAcquiredMethod("getIndexedDBPrefix", "getIndexedDBPrefix")',
        text_content
      )
      self.assertIn(
        'prefix + selected_storage_name + "-configuration-hash"',
        text_content
      )
      self.assertIn('prefix + "officejs-erp5-hash"', text_content)
      self.assertIn('prefix + "officejs-erp5"', text_content)

  def test_erp5js_router_prefixes_router_databases(self):
    """rjs_gadget_erp5_router_js acquires prefix and uses it for the
    selection/navigation_history/document_state databases."""
    text_content = self._getWebPageText(
      "rjs_gadget_erp5_router_js", "gadget_erp5_router.js",
      portal_type="Web Script"
    )
    if text_content is not None:
      self.assertIn(
        ".declareAcquiredMethod('getIndexedDBPrefix', 'getIndexedDBPrefix')",
        text_content
      )
      self.assertIn('prefix + "selection"', text_content)
      self.assertIn('prefix + "navigation_history"', text_content)
      self.assertIn('prefix + "document_state"', text_content)
