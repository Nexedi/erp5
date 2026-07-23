# -*- coding: utf-8 -*-
##############################################################################
# Integration tests for the in-ERP5 HATEOAS MCP tools (portal_callables/erp5_*).
# Everything is exercised end-to-end: the tests really create, write, search,
# read, clone and delete ERP5 documents *through the tool layer* and assert on
# what the tools return -- mirroring the functional coverage of the external
# erp5-mcp-hateoas test suite, but as real ERP5 integration tests.
##############################################################################
import json

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestMcpHateoasTools(ERP5TypeTestCase):

  def getTitle(self):
    return "MCP HATEOAS Tools"

  def afterSetUp(self):
    self.pc = self.portal.portal_callables
    self._cleanup = []
    self.login()

  def beforeTearDown(self):
    self.abort()
    for rel in reversed(self._cleanup):
      try:
        obj = self.portal.unrestrictedTraverse(str(rel), None)
        if obj is not None:
          obj.getParentValue().manage_delObjects([obj.getId()])
      except Exception:
        pass
    self.commit()
    self.tic()

  def call(self, tool_id, **kw):
    from AccessControl.SecurityManagement import getSecurityManager
    self.portal.REQUEST.AUTHENTICATED_USER = getSecurityManager().getUser()
    skins = self.portal.portal_skins
    saved = skins.getCurrentSkinName()
    skins.changeSkin('Hal')
    try:
      raw = getattr(self.pc, tool_id)(**kw)
    finally:
      if saved:
        skins.changeSkin(saved)
    if isinstance(raw, (str, unicode)):
      return json.loads(raw)
    return raw

  def create(self, module, portal_type, field_values=None):
    res = self.call("erp5_create", relative_url=module, portal_type=portal_type)
    self.assertTrue(isinstance(res, dict), res)
    self.assertNotIn("error", res, res)
    rel = str(res["relative_url"])
    self._cleanup.append(rel)
    self.tic()
    if field_values:
      w = self.call("erp5_write", relative_url=rel, field_values=field_values)
      self.assertEqual(w.get("status"), "success", w)
      self.tic()
    return rel

  def create_sub(self, parent_rel, portal_type):
    res = self.call("erp5_create", relative_url=parent_rel, portal_type=portal_type)
    self.assertNotIn("error", res, res)
    self.tic()
    return str(res["relative_url"])

  def test_01_discover(self):
    d = self.call("erp5_discover")
    self.assertIn("modules_by_application", d)
    self.assertIn("worklist", d)
    self.assertIn("tip", d)
    self.assertIn("erp5_guide", d["tip"])
    self.assertTrue(isinstance(d.get("total_pending"), int))

  def test_02_inspect(self):
    d = self.call("erp5_inspect", modules="person_module")
    self.assertIn("person_module", d)
    m = d["person_module"]
    self.assertTrue(len(m["columns"]) > 0)
    self.assertIn("form_relative_url", m)
    self.assertTrue(m["form_relative_url"].startswith("portal_skins/"))

  def test_03_create_and_read(self):
    rel = self.create("person_module", "Person")
    r = self.call("erp5_read", relative_url=rel)
    self.assertEqual(r["portal_type"], "Person")
    self.assertEqual(r["relative_url"], rel)
    for key in ("fields", "views", "actions", "workflows", "url", "exchanges", "prints", "jumps", "has_create_action"):
      self.assertIn(key, r)
    self.assertTrue(any(v["name"] == "view" for v in r["views"]))

  def test_04_write_and_read_back(self):
    rel = self.create("person_module", "Person")
    w = self.call("erp5_write", relative_url=rel, field_values={"field_my_first_name": "McpTest", "field_my_last_name": "Alpha", "field_my_gender": "male"})
    self.assertEqual(w.get("status"), "success", w)
    r = self.call("erp5_read", relative_url=rel)
    self.assertEqual(r["fields"]["my_first_name"]["value"], "McpTest")
    self.assertEqual(r["fields"]["my_last_name"]["value"], "Alpha")
    self.assertEqual(r["fields"]["my_gender"]["type"], "ListField")
    self.assertIn("McpTest", r["title"])

  def test_05_write_list_field(self):
    rel = self.create("person_module", "Person")
    w = self.call("erp5_write", relative_url=rel, field_values={"field_my_career_role_list": "intern"})
    self.assertEqual(w.get("status"), "success", w)
    r = self.call("erp5_read", relative_url=rel)
    self.assertEqual(r["fields"]["my_career_role_list"]["type"], "ParallelListField")
    self.assertEqual(r["fields"]["my_career_role_list"]["value"], ["intern"])

  def test_06_write_unknown_field_rejected(self):
    rel = self.create("person_module", "Person")
    w = self.call("erp5_write", relative_url=rel, field_values={"field_my_does_not_exist": "x"})
    self.assertIn("error", w)
    self.assertIn("my_does_not_exist", json.dumps(w))
    w2 = self.call("erp5_write", relative_url=rel, field_values={"field_my_first_name": "Ok"}, skip_validation=True)
    self.assertEqual(w2.get("status"), "success", w2)

  def test_07_create_then_search(self):
    tag = "zzsearchperson"
    ids = []
    for i in range(3):
      rel = self.create("person_module", "Person", field_values={"field_my_last_name": tag})
      ids.append(rel)
    self.tic()
    cat_n = len(self.portal.portal_catalog(portal_type="Person", title=tag))
    res = self.call("erp5_search", relative_url="person_module", query='title:"%s"' % tag, select_list=["title"], limit=10)
    self.assertTrue(res["count"] >= 3, {"tool": res, "catalog": cat_n})
    rels = [row["relative_url"] for row in res["results"]]
    for rel in ids:
      self.assertIn(rel, rels)
    self.assertIn("url", res["results"][0])

  def test_08_search_pagination(self):
    tag = "zzpageperson"
    for i in range(4):
      self.create("person_module", "Person", field_values={"field_my_last_name": tag})
    self.tic()
    page1 = self.call("erp5_search", relative_url="person_module", query='title:"%s"' % tag, limit=2, offset=0)
    self.assertEqual(page1["count"], 2)
    self.assertTrue(page1["has_more"])
    self.assertEqual(page1["next_offset"], 2)
    page2 = self.call("erp5_search", relative_url="person_module", query='title:"%s"' % tag, limit=2, offset=2)
    self.assertTrue(page2["count"] >= 2)
    self.assertNotEqual(page1["results"][0]["relative_url"], page2["results"][0]["relative_url"])

  def test_09_read_deep(self):
    rel = self.create("sale_order_module", "Sale Order")
    self.create_sub(rel, "Sale Order Line")
    tree = self.call("erp5_read_deep", relative_url=rel)
    self.assertEqual(tree["relative_url"], rel)
    self.assertTrue(len(tree.get("children", [])) >= 1, tree)
    self.assertEqual(tree["children"][0]["portal_type"], "Sale Order Line")

  def test_10_collect(self):
    rel = self.create("sale_order_module", "Sale Order")
    self.create_sub(rel, "Sale Order Line")
    self.create_sub(rel, "Sale Order Line")
    r = self.call("erp5_read", relative_url=rel)
    self.assertTrue(r.get("all_listboxes"))
    listbox_id = sorted(r["all_listboxes"].keys())[0]
    rows = self.call("erp5_collect", relative_url=rel, listbox_id=listbox_id)
    self.assertNotIn("error", rows, rows)
    self.assertTrue(rows.get("collected_count", 0) >= 2, rows)

  def test_11_all_editable(self):
    rel = self.create("person_module", "Person")
    r = self.call("erp5_read", relative_url=rel, all_editable=True)
    self.assertTrue(r.get("all_editable"))
    self.assertIn("fields_by_view", r)
    self.assertIn("view", r["fields_by_view"])
    gender = r["fields_by_view"]["view"].get("my_gender")
    self.assertTrue(gender is not None)
    self.assertIn("valid_choices", gender["value"])

  def test_12_reports_discovery(self):
    r = self.call("erp5_read", relative_url="accounting_module")
    names = [x["name"] for x in r.get("reports", [])]
    self.assertIn("trial_balance_report", names)
    self.assertIn("general_ledger_report", names)

  def test_13_write_relation_field(self):
    org = self.create("organisation_module", "Organisation", field_values={"field_my_title": "zzmcporgtest"})
    self.tic()
    person = self.create("person_module", "Person")
    w = self.call("erp5_write", relative_url=person, field_values={"field_my_career_subordination_title": "zzmcporgtest"})
    self.assertEqual(w.get("status"), "success", w)
    r = self.call("erp5_read", relative_url=person)
    sub = r["fields"]["my_career_subordination_title"]["value"]
    self.assertEqual(sub["portal_types"], ["Organisation"])
    self.assertTrue(sub["urls"] and sub["urls"][0].startswith("organisation_module/"))

  def test_14_action_workflow(self):
    rel = self.create("organisation_module", "Organisation", field_values={"field_my_title": "ZZMcpValidate"})
    before = self.call("erp5_read", relative_url=rel)
    wf = [w["name"] for w in before.get("workflows", [])]
    self.assertIn("submit_action", wf)
    res = self.call("erp5_action", relative_url=rel, action_name="submit_action")
    self.assertNotIn("error", res, res)
    self.tic()
    obj = self.portal.unrestrictedTraverse(str(rel))
    self.assertEqual(obj.getValidationState(), "submitted")

  def test_15_clone(self):
    rel = self.create("person_module", "Person", field_values={"field_my_first_name": "ZZCloneSrc"})
    res = self.call("erp5_clone", relative_url=rel)
    self.assertNotIn("error", res, res)
    new_rel = str(res["relative_url"])
    self._cleanup.append(new_rel)
    self.tic()
    self.assertNotEqual(new_rel, rel)
    r = self.call("erp5_read", relative_url=new_rel)
    self.assertEqual(r["fields"]["my_first_name"]["value"], "ZZCloneSrc")

  def test_16_delete_sub_object(self):
    rel = self.create("sale_order_module", "Sale Order")
    line = self.create_sub(rel, "Sale Order Line")
    self.assertTrue(self.portal.unrestrictedTraverse(str(line), None) is not None)
    res = self.call("erp5_delete", relative_url=line)
    self.assertNotIn("error", res, res)
    self.assertEqual(res.get("status"), "success", res)

  def test_17_skin_write_read_call_list(self):
    body = "return 'mcp-selftest-%s' % (1 + 1)"
    w = self.call("erp5_skin_write", script_id="ZZ_mcp_selftest", body=body)
    self.assertIn(w.get("status"), ("created", "updated"), w)
    rd = self.call("erp5_skin_read", script_id="ZZ_mcp_selftest")
    self.assertIn("mcp-selftest", rd["body"])
    out = self.call("erp5_skin_call", script_id="ZZ_mcp_selftest")
    self.assertEqual(out["output"], "mcp-selftest-2")
    lst = self.call("erp5_skin_list", skin_folder="custom")
    self.assertTrue(any(o["id"] == "ZZ_mcp_selftest" for o in lst["objects"]))
    self.portal.portal_skins.custom.manage_delObjects(["ZZ_mcp_selftest"])

  def test_18_skin_write_core_guard(self):
    w = self.call("erp5_skin_write", script_id="Base_edit", body="return 1")
    self.assertIn("error", json.dumps(w).lower() + str(w.get("status", "")).lower())

  def test_19_log_tail(self):
    marker = "ZZMcpLogProbe12345"
    self.call("erp5_skin_write", script_id="ZZ_mcp_logprobe", body="from Products.ERP5Type.Log import log\nlog('%s', 'hello')\nreturn 'ok'" % marker)
    self.call("erp5_skin_call", script_id="ZZ_mcp_logprobe")
    tail = self.call("erp5_log_tail", grep=marker)
    self.assertIn("content", tail)
    self.portal.portal_skins.custom.manage_delObjects(["ZZ_mcp_logprobe"])

  def test_20_guide_list_and_tutorial(self):
    # Guides now live as GUIDE-* Web Pages (compatible with erp5-mcp-hateoas remote guides).
    listing = getattr(self.pc, "erp5_guide")(tutorial="list")
    self.assertIn("GUIDE-create_person", listing)
    self.assertIn("Create and validate a Person", listing)
    # short id resolves to GUIDE-<id>; code placeholders (<new_url>) survive the html round-trip
    content = getattr(self.pc, "erp5_guide")(tutorial="create_person")
    self.assertIn("Create and validate a Person", content)
    self.assertIn("erp5_create", content)
    self.assertIn("<new_url>", content)
    # full reference also works
    full = getattr(self.pc, "erp5_guide")(tutorial="GUIDE-create_person")
    self.assertIn("Create and validate a Person", full)

  def test_21_guide_unknown(self):
    res = json.loads(getattr(self.pc, "erp5_guide")(tutorial="no_such_guide_xyz"))
    self.assertIn("error", res)
    self.assertIn("available_tutorials", res)

  def test_22_download_original_file(self):
    rel = self.create("document_module", "File")
    obj = self.portal.unrestrictedTraverse(str(rel))
    obj.setData("hello mcp bytes")
    obj.setContentType("text/plain")
    obj.setFilename("mcp.txt")
    self.commit()
    self.tic()
    res = self.call("erp5_download", relative_url=rel, action_name="download", action_type="exchange")
    self.assertTrue(isinstance(res, list), res)
    link = res[0]
    self.assertEqual(link["type"], "resource_link")
    self.assertTrue(link["uri"].endswith("/Base_download"))
    self.assertEqual(link["mimeType"], "text/plain")
    self.assertEqual(link["size"], len("hello mcp bytes"))

  def test_23_download_inline_base64(self):
    rel = self.create("document_module", "File")
    obj = self.portal.unrestrictedTraverse(str(rel))
    obj.setData("inline-bytes")
    obj.setContentType("text/plain")
    self.commit()
    self.tic()
    res = self.call("erp5_download", relative_url=rel, action_name="download", action_type="exchange", inline=True)
    self.assertEqual(res.get("status"), "success", res)
    self.assertIn("content_base64", res)
    import base64
    self.assertEqual(base64.b64decode(res["content_base64"]), "inline-bytes")

  def test_24_download_report_url(self):
    res = self.call("erp5_download", relative_url="accounting_module", action_name="trial_balance_report", action_type="report", params={"at_date": "2025/12/31"})
    self.assertTrue(isinstance(res, list), res)
    uri = res[0]["uri"]
    self.assertIn("/accounting_module/Base_callDialogMethod?", uri)
    self.assertIn("dialog_method=AccountModule_viewTrialBalanceReport", uri)
    self.assertIn("field_your_simulation_state:list=", uri)
    self.assertIn("subfield_field_your_at_date_year=2025", uri)

  # A tool gets the text a JSON payload decodes to, while REQUEST.form of a
  # real HTTP submit holds native strings -- utf-8 encoded bytes on Python 2.
  # Without that conversion the unicode reaches the stored property: a
  # LinesField then keeps a list of unicode, which breaks every consumer
  # treating such an entry as a path. A Business Template is the document
  # under test because its build() is where this first showed up.

  def test_25_write_lines_field_stores_native_strings(self):
    rel = self.create("portal_templates", "Business Template")
    w = self.call("erp5_write", relative_url=rel, field_values={
      "field_my_template_path_list":
        u"portal_types/Business Template\nportal_categories/role/**"})
    self.assertEqual(w.get("status"), "success", w)
    path_list = self.portal.unrestrictedTraverse(rel).getTemplatePathList()
    # a Business Template keeps its lists sorted
    self.assertEqual(sorted(path_list),
                     ["portal_categories/role/**", "portal_types/Business Template"])
    for path in path_list:
      self.assertIsInstance(path, str)

  def test_26_written_path_stays_traversable(self):
    # unrestrictedTraverse() splits a native string on "/" but iterates over
    # the characters of a unicode one, so Business Template build failed with
    # KeyError: u'p' -- the first letter of "portal_types/...".
    rel = self.create("portal_templates", "Business Template")
    w = self.call("erp5_write", relative_url=rel, field_values={
      "field_my_template_path_list": u"portal_types/Business Template"})
    self.assertEqual(w.get("status"), "success", w)
    path = self.portal.unrestrictedTraverse(rel).getTemplatePathList()[0]
    self.assertEqual(self.portal.unrestrictedTraverse(path),
                     self.portal.portal_types["Business Template"])

  def test_27_write_non_ascii_lines_field(self):
    rel = self.create("portal_templates", "Business Template")
    value = u"portal_categories/r\xf4le/**"
    w = self.call("erp5_write", relative_url=rel,
                  field_values={"field_my_template_path_list": value})
    self.assertEqual(w.get("status"), "success", w)
    stored = self.portal.unrestrictedTraverse(rel).getTemplatePathList()[0]
    self.assertIsInstance(stored, str)
    self.assertEqual(stored, value.encode("utf-8") if str is bytes else value)

  def test_28_action_comment_stored_as_native_string(self):
    # erp5_action fills REQUEST.form the same way erp5_write does, and the
    # workflow comment is a form value that ends up stored.
    rel = self.create("organisation_module", "Organisation",
                      field_values={"field_my_title": "ZZMcpComment"})
    comment = u"soumis par le test caf\xe9"
    res = self.call("erp5_action", relative_url=rel,
                    action_name="submit_action", comment=comment)
    self.assertNotIn("error", res, res)
    self.tic()
    obj = self.portal.unrestrictedTraverse(str(rel))
    comment_list = [entry.get("comment")
                    for history in obj.workflow_history.values()
                    for entry in history if entry.get("comment")]
    self.assertEqual(len(comment_list), 1, comment_list)
    stored = comment_list[0]
    self.assertIsInstance(stored, str)
    self.assertEqual(stored, comment.encode("utf-8") if str is bytes else comment)

  # Numbers need the same treatment as text, plus formatting. A FloatField is
  # published with its raw python value but submitted by the browser as what
  # the widget rendered, so a tool that replays the value has to render it the
  # same way -- see render_float in erp5_write.

  def set_input_style(self, path, input_style):
    """Surcharge a FloatField's input_style, returning a restore callable."""
    from Products.ERP5Form.Form import field_value_cache
    field = self.portal.unrestrictedTraverse(path)
    if field.meta_type == "ProxyField":
      # input_style may be delegated to the template field, in which case
      # setting it on the proxy would be ignored
      field = field.getRecursiveTemplateField()
    saved = field.values.get("input_style")

    def apply(value):
      field.values["input_style"] = value
      field._p_changed = 1
      # get_value serves memoised field values; without this the form keeps
      # handing out the old input_style and the surcharge is a no-op
      field_value_cache.clear()

    apply(input_style)
    return lambda: apply(saved)

  def test_29_write_float_field_accepts_a_number(self):
    # A JSON payload carries 1.5, not "1.5". Passing the float straight into
    # REQUEST.form made FloatValidator call value.decode and blow up with
    # "'float' object has no attribute 'decode'".
    rel = self.create("foo_module", "Foo")
    w = self.call("erp5_write", relative_url=rel, field_values={
      "field_my_quantity": 1.5, "field_my_price": 2})
    self.assertEqual(w.get("status"), "success", w)
    obj = self.portal.unrestrictedTraverse(rel)
    self.assertEqual(obj.getQuantity(), 1.5)
    self.assertEqual(obj.getPrice(), 2)

  def test_30_write_unrelated_field_with_float_on_the_form(self):
    # Every editable field of the form is resubmitted, so an untouched
    # FloatField crashed the write of a plain string field too.
    rel = self.create("bar_module", "Bar", field_values={"field_my_quantity": 3.5})
    w = self.call("erp5_write", relative_url=rel,
                  field_values={"field_my_title": "ZZMcpFloat"})
    self.assertEqual(w.get("status"), "success", w)
    # Bar carries no quantity accessor, so read the untouched float back
    # through the tool rather than through a generated getter
    r = self.call("erp5_read", relative_url=rel)
    self.assertEqual(r["fields"]["my_quantity"]["value"], 3.5)

  def test_31_untouched_float_does_not_drift(self):
    # The value has to survive the render/validate round trip unchanged. With
    # a thousands-separator input_style an unformatted "1234.5" comes back as
    # 12345.0, so a float grew by a factor of ten on every single write.
    rel = self.create("foo_module", "Foo")
    restore = self.set_input_style(
      "portal_skins/erp5_ui_test/Foo_view/my_quantity", "-1.234,5")
    try:
      # Prove the surcharge really reached the form the tool reads: only a
      # '-1.234,5' styled field reads "1.234,5" as one thousand two hundred
      # thirty four and a half -- the default style rejects it outright.
      w = self.call("erp5_write", relative_url=rel,
                    field_values={"field_my_quantity": "1.234,5"})
      self.assertEqual(w.get("status"), "success", w)
      obj = self.portal.unrestrictedTraverse(rel)
      self.assertEqual(obj.getQuantity(), 1234.5)
      w = self.call("erp5_write", relative_url=rel,
                    field_values={"field_my_quantity": 1234.5})
      self.assertEqual(w.get("status"), "success", w)
      self.assertEqual(obj.getQuantity(), 1234.5)
      for _ in range(3):
        w = self.call("erp5_write", relative_url=rel,
                      field_values={"field_my_title": "ZZMcpNoDrift"})
        self.assertEqual(w.get("status"), "success", w)
        self.assertEqual(obj.getQuantity(), 1234.5)
    finally:
      restore()

  def test_32_write_integer_field_accepts_a_number(self):
    # IntegerValidator goes through the same normalizeFullWidthNumber call,
    # so an int crashed exactly like a float did.
    rel = self.create("foo_module", "Foo")
    w = self.call("erp5_write", relative_url=rel, form_id="view_integer_field",
                  field_values={"field_my_quantity": 7})
    self.assertEqual(w.get("status"), "success", w)
    self.assertEqual(self.portal.unrestrictedTraverse(rel).getQuantity(), 7)

  # A RelationStringField's business rules live in its parameter_list -- extra
  # catalog filters the relation lookup applies (validation_state, use, ...).
  # erp5_write resolves the title to a uid itself and submits it in the field's
  # hidden relation key, and a supplied uid is taken as already picked, so the
  # field never runs its own constrained lookup. Unless resolve_uid applies
  # parameter_list too, every such constraint is silently bypassed.

  def make_org(self, tag):
    """Organisation whose title is unique to this run -> (relative_url, title).

    A fixed title is not enough: a run whose tearDown does not complete leaves
    its organisations behind, and the next run then has two documents with the
    same title. The relation lookup answers that with "Select appropriate
    document in the list." and the test fails for a reason of its own making.
    """
    rel = self.create("organisation_module", "Organisation")
    title = "ZZMcp%s%s" % (tag, rel.rsplit("/", 1)[-1])
    w = self.call("erp5_write", relative_url=rel,
                  field_values={"field_my_title": title})
    self.assertEqual(w.get("status"), "success", w)
    self.tic()
    return rel, title

  def link_org(self, person, title):
    w = self.call("erp5_write", relative_url=person,
                  field_values={"field_my_career_subordination_title": title})
    self.tic()
    return w

  def linked_org(self, person):
    """relative_url the person's subordination points at, or None."""
    r = self.call("erp5_read", relative_url=person)
    field = r["fields"].get("my_career_subordination_title")
    if field is None:  # an empty relation is dropped from the view
      return None
    urls = field["value"].get("urls") or []
    return str(urls[0]) if urls else None

  # Foo_viewRelationField/my_constrained_successor_title is a relation field
  # carrying parameter_list [('validation_state', 'validated')] -- a fixture
  # for exactly this, so the constraint under test is a real field setting and
  # nothing shared has to be mutated for the duration of a test.
  CONSTRAINED_VIEW = "view_relation_field"
  CONSTRAINED_FIELD = "field_my_constrained_successor_title"

  def make_foo(self, tag, validated=False):
    """Foo with a title unique to this run -> (relative_url, title)."""
    rel = self.create("foo_module", "Foo")
    title = "ZZMcp%s%s" % (tag, rel.rsplit("/", 1)[-1])
    # edit(), not erp5_write: Foo_view exposes my_id, and replaying it turns a
    # title edit into a rename, which collides with a sibling created in the
    # same test. Fixture setup has no business going through the tool anyway.
    # edit() rather than setTitle() because only edit() marks the document for
    # reindexing, and the relation lookup under test resolves via the catalog.
    self.portal.unrestrictedTraverse(rel).edit(title=title)
    self.tic()
    if validated:
      # Jump the state rather than firing the transition: Foo has four
      # workflows, the "validate_action" listed on the document belongs to
      # another one and leaves validation_state at draft silently, and
      # foo_validation_workflow's own "validate" transition is guarded against
      # the test user. Forcing the state is what a fixture wants anyway.
      obj = self.portal.unrestrictedTraverse(rel)
      self.portal.portal_workflow._jumpToStateFor(
        obj, "validated", wf_id="foo_validation_workflow")
      obj.reindexObject()
    self.tic()
    return rel, title

  def linked_successor(self, foo):
    """relative_url the constrained successor points at, or None."""
    r = self.call("erp5_read", relative_url=foo, view=self.CONSTRAINED_VIEW)
    field = r["fields"].get("my_constrained_successor_title")
    if field is None:  # an empty relation is dropped from the view
      return None
    urls = field["value"].get("urls") or []
    return str(urls[0]) if urls else None

  def ensure_foo_category(self):
    """my_foo_category_title is required on that form -> give it a value.

    Without it every write through the form fails validation on that field,
    which would let a "must be refused" assertion pass for the wrong reason.
    """
    base = self.portal.portal_categories.foo_category
    if "zzmcpcat" not in base.objectIds():
      base.newContent(portal_type="Category", id="zzmcpcat",
                      title="ZZMcpFooCategory")
    self.tic()
    return "ZZMcpFooCategory"

  def write_successor(self, foo, title):
    w = self.call("erp5_write", relative_url=foo,
                  form_id=self.CONSTRAINED_VIEW,
                  field_values={
                    self.CONSTRAINED_FIELD: title,
                    "field_my_foo_category_title": self.foo_category_title})
    self.tic()
    return w

  def test_33_relation_respects_field_parameter_list(self):
    self.foo_category_title = self.ensure_foo_category()
    _, draft_title = self.make_foo("Draft")
    valid, valid_title = self.make_foo("Valid", validated=True)
    foo = self.create("foo_module", "Foo")
    self.tic()
    # the draft Foo is excluded by the field's parameter_list, however exactly
    # its title matches
    w = self.write_successor(foo, draft_title)
    self.assertNotEqual(w.get("status"), "success", w)
    self.assertIn("error", w)
    self.assertIsNone(self.linked_successor(foo))
    # a validated Foo passes the same constraint
    w = self.write_successor(foo, valid_title)
    self.assertEqual(w.get("status"), "success", w)
    self.assertEqual(self.linked_successor(foo), str(valid))

  def test_34_relation_requires_an_exact_catalog_index_match(self):
    # resolve_uid used to fall back to the first catalog row when nothing
    # matched exactly, silently linking an unrelated document. This only
    # discriminates when the catalog matches the index loosely; when it
    # matches exactly the assertion simply holds for both.
    _, title_a = self.make_org("Prefix")
    self.make_org("Prefix")
    person = self.create("person_module", "Person")
    self.tic()
    # a strict prefix of a real title must resolve to nothing
    self.link_org(person, title_a[:-1])
    self.assertIsNone(self.linked_org(person))

  def test_35_constraint_holds_when_a_link_already_exists(self):
    # The bypass was worst on a field that already had a link: erp5_write
    # injected the uid of the excluded document and reported success, quietly
    # repointing the relation at something the field does not accept.
    #
    self.foo_category_title = self.ensure_foo_category()
    valid, _ = self.make_foo("KeepValid", validated=True)
    _, draft_title = self.make_foo("KeepDraft")
    foo = self.create("foo_module", "Foo")
    # The starting link is established through the API rather than the tool:
    # resolving it by title made the setup fail whenever the catalog answered
    # with two brains for that one title, which has nothing to do with the
    # behaviour under test. Why a duplicate appeared is unexplained -- it is
    # transient (nothing survives the run) and was not reproduced outside a
    # test; going through the API sidesteps it either way.
    self.portal.unrestrictedTraverse(foo).setSuccessorValue(
      self.portal.unrestrictedTraverse(valid))
    self.tic()
    self.assertEqual(self.linked_successor(foo), str(valid))
    # the draft Foo is excluded by the field's parameter_list, so the existing
    # link has to survive an attempt to repoint at it
    w = self.write_successor(foo, draft_title)
    self.assertNotEqual(w.get("status"), "success", w)
    self.assertEqual(self.linked_successor(foo), str(valid))
    # and it must be refused for the constraint, not because the title was
    # ambiguous -- that would pass this test for the wrong reason
    self.assertNotIn("Select appropriate",
                     w.get("field_errors", {}).get(
                       "my_constrained_successor_title", ""), w)

  def test_36_replayed_relation_survives_an_unrelated_write(self):
    # erp5_write resubmits every editable field, so the current link has to be
    # replayed when the caller did not touch the relation -- only a value the
    # caller actually supplied may drop it.
    # (Whether supplying "" clears a relation is up to the field's own title
    # setter: strict, uid-driven fields clear, lenient ones keep the link. It
    # is not a property of the tool, so it is not asserted here.)
    org, title = self.make_org("ReplayLink")
    person = self.create("person_module", "Person")
    self.tic()
    self.link_org(person, title)
    self.assertEqual(self.linked_org(person), str(org))
    w = self.call("erp5_write", relative_url=person,
                  field_values={"field_my_first_name": "ZZMcpReplay"})
    self.tic()
    self.assertEqual(w.get("status"), "success", w)
    self.assertEqual(self.linked_org(person), str(org))

  def test_37_validation_error_payload_matches_the_output_schema(self):
    # The numeric HTTP status used to be returned as "status", which the tool's
    # JSON Form output schema types as a string (it carries "success"). Output
    # validation then rejected the whole payload and the caller got a JSON-RPC
    # internal error instead of the field errors. Calling the tool directly
    # skips that validation, so assert the payload shape the schema requires.
    rel = self.create("foo_module", "Foo")
    w = self.call("erp5_write", relative_url=rel, form_id="view_integer_field",
                  field_values={"field_my_quantity": "not-a-number"})
    self.assertIn("error", w)
    self.assertTrue(w.get("field_errors"), w)
    self.assertIn("my_quantity", w["field_errors"])
    self.assertNotIsInstance(w.get("status", u""), int)
    self.assertTrue(int(w["status_code"]) >= 400, w)

  # Every editable field of the form is replayed, so a date the caller never
  # mentioned still makes the round trip through serialize(). A DateTimeField
  # is published RFC-822 style ("Fri, 28 Aug 2026 00:00:00 +0000"); parse_date
  # only read "-" and "/" separated dates, answered None for that, and the
  # else branch submitted empty year/month/day subfields -- so writing any one
  # field silently cleared every date on the form and still reported success.

  def test_38_untouched_date_survives_an_unrelated_write(self):
    rel = self.create("sale_order_module", "Sale Order")
    w = self.call("erp5_write", relative_url=rel, field_values={
      "field_my_start_date": "2026-08-28", "field_my_stop_date": "2026-09-15"})
    self.assertEqual(w.get("status"), "success", w)
    self.tic()
    obj = self.portal.unrestrictedTraverse(rel)
    self.assertEqual(obj.getStartDate().ISO()[:10], "2026-08-28")
    self.assertEqual(obj.getStopDate().ISO()[:10], "2026-09-15")
    w = self.call("erp5_write", relative_url=rel,
                  field_values={"field_my_title": "ZZMcpDateReplay"})
    self.assertEqual(w.get("status"), "success", w)
    self.tic()
    self.assertIsNotNone(obj.getStartDate(), "start_date was blanked by the replay")
    self.assertIsNotNone(obj.getStopDate(), "stop_date was blanked by the replay")
    self.assertEqual(obj.getStartDate().ISO()[:10], "2026-08-28")
    self.assertEqual(obj.getStopDate().ISO()[:10], "2026-09-15")

  def test_39_replayed_date_round_trips_the_published_format(self):
    # What the replay has to parse is whatever erp5_read publishes for the
    # field, so assert against that string rather than a format assumed here:
    # a change in how DateTimeField renders would otherwise quietly bring the
    # blanking back.
    rel = self.create("sale_order_module", "Sale Order")
    self.call("erp5_write", relative_url=rel,
              field_values={"field_my_start_date": "2026-08-28"})
    self.tic()
    published = self.call("erp5_read", relative_url=rel)["fields"]["my_start_date"]["value"]
    self.assertTrue(published, "start_date not published by erp5_read")
    for _ in range(3):
      w = self.call("erp5_write", relative_url=rel,
                    field_values={"field_my_title": "ZZMcpDateStable"})
      self.assertEqual(w.get("status"), "success", w)
      self.tic()
      again = self.call("erp5_read", relative_url=rel)["fields"]["my_start_date"]["value"]
      self.assertEqual(again, published)

  def test_40_empty_date_does_not_trip_the_blanking_guard(self):
    # The guard fires only for a stored value that could not be parsed. A date
    # that is legitimately empty still has to write normally, otherwise every
    # document with an unset date becomes unwritable.
    rel = self.create("sale_order_module", "Sale Order")
    w = self.call("erp5_write", relative_url=rel,
                  field_values={"field_my_start_date": ""})
    self.assertEqual(w.get("status"), "success", w)
    self.tic()
    # an empty date is dropped from the view altogether, like an empty relation
    field = self.call("erp5_read", relative_url=rel)["fields"].get("my_start_date")
    self.assertFalse(field and field.get("value"), field)
    w = self.call("erp5_write", relative_url=rel,
                  field_values={"field_my_title": "ZZMcpEmptyDate"})
    self.assertEqual(w.get("status"), "success", w)
    self.assertNotIn("unparseable_date_fields", w)

  # Base_edit accepts a bare title for a RelationStringField and stores it as
  # plain text without creating the link, so an empty field_errors was being
  # reported as success over a relation that pointed at nothing. A relation
  # the caller actually supplied is now re-read and confirmed bound before the
  # tool answers success.

  def test_41_unresolvable_relation_is_not_reported_as_success(self):
    self.foo_category_title = self.ensure_foo_category()
    foo = self.create("foo_module", "Foo")
    self.tic()
    w = self.write_successor(foo, "ZZMcpNoSuchFooAnywhere")
    self.assertNotEqual(w.get("status"), "success", w)
    self.assertIn("error", w)
    self.assertIsNone(self.linked_successor(foo))

  def test_42_unbound_relation_is_named_in_the_error(self):
    # Whether the refusal comes from ERP5's own field validation or from the
    # tool's post-edit binding check, the caller has to be told which relation
    # failed -- "success" with a silently unlinked field is the bug.
    self.foo_category_title = self.ensure_foo_category()
    foo = self.create("foo_module", "Foo")
    self.tic()
    w = self.write_successor(foo, "ZZMcpNoSuchFooAnywhere")
    reported = list(w.get("unbound_relations") or []) + list(w.get("field_errors", {}).keys())
    self.assertIn("my_constrained_successor_title", reported, w)

  def test_43_resolved_relation_still_reports_success(self):
    # The binding check must not turn a perfectly good relation write into a
    # failure, and must not fire for a relation the caller never supplied.
    self.foo_category_title = self.ensure_foo_category()
    valid, valid_title = self.make_foo("BindOk", validated=True)
    foo = self.create("foo_module", "Foo")
    self.tic()
    w = self.write_successor(foo, valid_title)
    self.assertEqual(w.get("status"), "success", w)
    self.assertNotIn("unbound_relations", w)
    self.assertEqual(self.linked_successor(foo), str(valid))
    w = self.call("erp5_write", relative_url=foo, form_id=self.CONSTRAINED_VIEW,
                  field_values={"field_my_foo_category_title": self.foo_category_title})
    self.tic()
    self.assertEqual(w.get("status"), "success", w)
    self.assertEqual(self.linked_successor(foo), str(valid))

  # A transition refused by a constraint never reaches the caller as an
  # exception. Workflow_statusModify catches the ValidationFailed and, under
  # the renderjs skin, answers a body of {"portal_status_message": "<reason>"}
  # with a 403 left on the shared REQUEST.RESPONSE. Both used to be dropped:
  # the 403 became the MCP reply itself, which no client can read, and the
  # numeric status was returned as "status", typed a string by the output
  # schema, so output validation replaced the payload. Either way a refusal
  # arrived as a bare JSON-RPC internal error carrying no reason at all.

  REFUSAL = "ZZMcp refusal: a required property is missing"

  def refuse_transitions(self, msg):
    """Make every workflow transition raise ValidationFailed(msg).

    The seam is portal_workflow.doActionFor, which is what
    Workflow_statusModify calls, so everything downstream of the refusal --
    the catch, the status message, the 403 on the shared response -- still
    happens for real. Patching that rather than a particular constraint keeps
    the test independent of any one module's business rules. Returns a
    callable that puts the class back.
    """
    from Products.ERP5Type.Core.Workflow import ValidationFailed
    klass = self.portal.portal_workflow.__class__
    owned = "doActionFor" in klass.__dict__
    original = klass.__dict__.get("doActionFor")

    def refusing(*args, **kw):
      raise ValidationFailed(msg)

    def restore():
      if owned:
        setattr(klass, "doActionFor", original)
      else:
        try:
          delattr(klass, "doActionFor")
        except AttributeError:
          pass

    setattr(klass, "doActionFor", refusing)
    return restore

  def refused_submit(self, title):
    """Submit an Organisation through erp5_action, with the transition refused."""
    rel = self.create("organisation_module", "Organisation",
                      field_values={"field_my_title": title})
    restore = self.refuse_transitions(self.REFUSAL)
    try:
      res = self.call("erp5_action", relative_url=rel,
                      action_name="submit_action")
    finally:
      restore()
    return rel, res

  def test_44_refused_transition_reports_the_reason(self):
    rel, res = self.refused_submit("ZZMcpRefusedReason")
    self.assertIn("error", res, res)
    self.assertIn(self.REFUSAL, res["error"], res)
    # The reason really travelled: "debug" is only emitted when the tool could
    # not find out why, and that branch is what has to stay unreachable here.
    self.assertNotIn("debug", res, res)

  def test_45_refused_transition_is_not_reported_as_success(self):
    # Nothing was raised and nothing came back in field_errors, so the tool
    # used to answer "success" over a document that never moved.
    rel, res = self.refused_submit("ZZMcpRefusedState")
    self.assertNotEqual(res.get("status"), "success", res)
    self.assertEqual(
      self.portal.unrestrictedTraverse(str(rel)).getValidationState(), "draft")

  def test_46_refused_transition_payload_matches_the_output_schema(self):
    # Same trap as test_37: the HTTP status belongs in "status_code", because
    # the output schema types "status" as the string that carries "success".
    rel, res = self.refused_submit("ZZMcpRefusedSchema")
    self.assertIn("error", res, res)
    self.assertIsInstance(res["error"], (str, unicode))
    self.assertNotIsInstance(res.get("status", u""), int)
    self.assertTrue(int(res["status_code"]) >= 400, res)

  def test_47_refused_transition_leaves_the_response_clean(self):
    # The dialog leaves its verdict on the shared REQUEST.RESPONSE: a 403, or
    # a 302 to a portal_status_message URL. Left there it is that verdict, not
    # the tool's payload, that the MCP client receives.
    rel = self.create("organisation_module", "Organisation",
                      field_values={"field_my_title": "ZZMcpRefusedResponse"})
    response = self.portal.REQUEST.RESPONSE
    response.setStatus(200)
    restore = self.refuse_transitions(self.REFUSAL)
    try:
      res = self.call("erp5_action", relative_url=rel,
                      action_name="submit_action")
    finally:
      restore()
    self.assertIn("error", res, res)
    self.assertTrue(response.getStatus() < 400, response.getStatus())
    self.assertFalse(response.getHeader("Location"), response.getHeader("Location"))

  def test_49_discover_survives_a_non_ascii_module_title(self):
    # json.dumps(ensure_ascii=False) joins its output chunks on Python 2, so a
    # payload mixing unicode with utf-8 str makes that join decode the bytes
    # as ascii: "'ascii' codec can't decode byte 0xc3 in position 15". In
    # erp5_discover the mix is structural -- the worklist arrives from
    # ERP5Document_getHateoas as unicode while a module title comes back from
    # Localizer as a native str -- so the tool raised on any localised
    # instance and an all-ascii one never noticed.
    module = self.portal.organisation_module
    saved = module.getTitle()
    title = u"Gesch\xe4ftspartner"
    # as ZODB and Localizer hand it over: utf-8 encoded native bytes
    module.setTitle(title.encode("utf-8"))
    try:
      res = self.call("erp5_discover")
    finally:
      module.setTitle(saved)
    published = [m["title"]
                 for group in res["modules_by_application"].values()
                 for m in group]
    self.assertIn(title, published, published)

  def test_50_strip_personal_data_survives_a_non_ascii_payload(self):
    # Where a localised instance actually died: the personal-data hook
    # re-serialises the tool's data channel with the same ensure_ascii=False,
    # so fixing the tools alone was not enough -- erp5_discover still came
    # back as a JSON-RPC internal error, with the traceback pointing here
    # rather than at the tool.
    services = [x for x in self.portal.portal_web_services.objectValues()
                if x.getPortalType() == "MCP Service"]
    self.assertTrue(services, "no MCP Service on this instance")
    service = services[0]
    tool = self.portal.portal_callables.erp5_discover
    title = u"Verkaufs-Auftr\xe4ge"
    # the mix that breaks the join: unicode from getHateoas next to a native
    # str title read through Localizer
    data = {u"worklist": [{u"name": u"plain unicode"}],
            u"modules": [{u"title": title.encode("utf-8")}]}
    text, out = service._stripPersonalData(("", data), tool)
    self.assertTrue(text, out)
    if not isinstance(text, unicode):
      text = text.decode("utf-8")
    self.assertIn(title, text)

  def test_51_get_on_the_endpoint_is_405_rather_than_an_error(self):
    # Streamable HTTP lets a client open an SSE stream with GET. This server
    # never initiates messages, and the transport's answer for that is 405.
    # Raising instead reached the client as a JSON-RPC internal error and put
    # a traceback in the event log every time a client tried the stream --
    # which clients do routinely, so it was pure noise.
    services = [x for x in self.portal.portal_web_services.objectValues()
                if x.getPortalType() == "MCP Service"]
    self.assertTrue(services, "no MCP Service on this instance")
    service = services[0]
    request = self.portal.REQUEST
    response = request.RESPONSE
    saved_status = response.getStatus()
    try:
      body = service._handleGet(request)
      status = response.getStatus()
      allow = response.getHeader("Allow")
    finally:
      response.setStatus(saved_status)
    self.assertEqual(status, 405)
    self.assertFalse(body)
    self.assertIn("POST", allow or "")

  def test_52_rich_payloads_are_not_withheld_by_the_personal_data_hook(self):
    # A download answers with content blocks -- a list, or a dict carrying
    # "content" -- and the hook used to withhold any such payload outright
    # while stripping was on, so no document could be downloaded at all. File
    # bytes still are not redacted: the policy covers the fields of a record,
    # not what is inside an attachment.
    services = [x for x in self.portal.portal_web_services.objectValues()
                if x.getPortalType() == "MCP Service"]
    self.assertTrue(services, "no MCP Service on this instance")
    service = services[0]
    tool = self.portal.portal_callables.erp5_download
    link_list = [{"type": "resource_link", "uri": "http://example.invalid/x",
                  "mimeType": "application/pdf", "size": 17}]
    # 'personal_data_blocked_tool_list' defaults to ('erp5_download',), so on a
    # service nobody has configured otherwise the hook refuses this tool before
    # it ever looks at the payload. The payload shape is what is under test
    # here, so state the setting this test depends on rather than inherit
    # whichever one an instance happens to carry.
    service.setPersonalDataBlockedToolList([])
    self.assertEqual(service._stripPersonalData(link_list, tool), link_list)
    envelope = {"content": [{"type": "text", "text": "inline"}]}
    self.assertEqual(service._stripPersonalData(envelope, tool), envelope)
    # the record rule is untouched: a tuple is still walked by the policy
    text, data = service._stripPersonalData(
      ("", {"relative_url": "person_module/1", "portal_type": "Person",
            "title": "Doe, John", "default_telephone_text": "+49 123"}), tool)
    self.assertEqual(data["title"], "Doe, John")
    self.assertNotIn("123", data["default_telephone_text"])

  def paged_total(self, **kw):
    """Count by paging the search and summing 'count', the slow way."""
    total = 0
    offset = 0
    while True:
      page = self.call("erp5_search", limit=200, offset=offset, **kw)
      self.assertNotIn("error", page, page)
      total += page["count"]
      if not page["has_more"]:
        return total
      offset = page["next_offset"]

  def test_53_count_only_agrees_with_paging(self):
    # count_only answers the total in one catalog COUNT instead of a request
    # per page. It lives in erp5_search rather than in a tool of its own so
    # that it is fed the very filters the search parses: a separate counter
    # would have to re-implement parse_query and could drift from it. The test
    # is that agreement, unfiltered and filtered -- not a hardcoded number.
    fast = self.call("erp5_search", relative_url="organisation_module",
                     count_only=True)
    self.assertNotIn("error", fast, fast)
    self.assertIsInstance(fast["total_count"], int)
    self.assertNotIn("results", fast)          # no rows are fetched
    self.assertEqual(fast["total_count"],
                     self.paged_total(relative_url="organisation_module"))
    # and the filters really reach the count
    query = 'title:"WBI"'
    filtered = self.call("erp5_search", relative_url="organisation_module",
                         count_only=True, query=query)
    self.assertNotIn("error", filtered, filtered)
    self.assertEqual(filtered["total_count"],
                     self.paged_total(relative_url="organisation_module", query=query))
    self.assertTrue(filtered["total_count"] < fast["total_count"], (filtered, fast))

  def test_54_count_only_accepts_a_string_and_leaves_search_alone(self):
    # A client holding the pre-count_only schema forwards the flag as a plain
    # string, so "true" has to read as true -- otherwise the caller silently
    # gets a page of rows back instead of the count they asked for.
    as_string = self.call("erp5_search", relative_url="organisation_module",
                          count_only="true")
    self.assertIn("total_count", as_string)
    # every falsy spelling must leave the ordinary search untouched
    for value in (False, 0, "", "false", None):
      rows = self.call("erp5_search", relative_url="organisation_module",
                       count_only=value, limit=3)
      self.assertNotIn("total_count", rows)
      self.assertEqual(rows["count"], 3)
      self.assertEqual(len(rows["results"]), 3)

  def test_55_count_only_reports_what_it_cannot_count(self):
    missing = self.call("erp5_search", relative_url="no_such_module",
                        count_only=True)
    self.assertIn("error", missing)
    self.assertNotIn("total_count", missing)

  def test_48_accepted_transition_still_reports_success(self):
    # A refusal is now told from an acceptance by comparing the workflow
    # states before and after, so an accepted transition has to keep answering
    # success -- and its own status message must not be read as a complaint.
    rel = self.create("organisation_module", "Organisation",
                      field_values={"field_my_title": "ZZMcpAccepted"})
    res = self.call("erp5_action", relative_url=rel, action_name="submit_action")
    self.assertNotIn("error", res, res)
    self.assertEqual(res.get("status"), "success", res)
    self.tic()
    self.assertEqual(
      self.portal.unrestrictedTraverse(str(rel)).getValidationState(), "submitted")

  ############################################################################
  # Listbox-backed search: erp5_collect(filters=...) and erp5_inspect.
  #
  # ERP5Document_getHateoas parses its `query` argument only to validate column
  # names and then does catalog_kw["full_text"] = query, so a 'column:"value"'
  # string reached MySQL as a single literal fulltext term and matched nothing
  # -- on every module, without an error. Column criteria now travel in
  # default_param_json instead, which getHateoas merges into catalog_kw and
  # hands to the listbox's own list_method: the route the UI takes, so module
  # defaults survive and related keys resolve.
  ############################################################################

  def collect(self, relative_url, **kw):
    rows = self.call("erp5_collect", relative_url=relative_url, **kw)
    self.assertNotIn("error", rows, rows)
    return rows

  def collected_titles(self, rows):
    return sorted([str(x.get("title") or "") for x in rows["items"]])

  def test_83_two_writes_in_one_request_do_not_leak_into_each_other(self):
    # Every call of a live test shares one REQUEST, and so does every call of a
    # JSON-RPC batch. erp5_write replays the whole form, so a field left behind
    # by the previous call is indistinguishable from one of ours and gets
    # edited into this document: a batch of writes once carried the first
    # tool's body and id into every tool that followed, and erp5_collect
    # answered with erp5_discover's payload.
    self.call("erp5_write", relative_url="portal_callables/erp5_skin_list",
              field_values={"field_my_read_only": 1})
    self.call("erp5_write", relative_url="portal_callables/erp5_log_tail",
              field_values={"field_my_read_only": 1})
    self.assertEqual(
      self.portal.portal_callables.erp5_log_tail.getId(), "erp5_log_tail")
    # each still answers with its own payload, so each still has its own body
    self.assertIn("objects", self.call("erp5_skin_list", skin_folder="custom"))
    self.assertIn("content", self.call("erp5_log_tail", max_entries=1))

  def test_82_a_blocked_tool_is_refused_while_stripping_is_active(self):
    # The blocked list is how a service keeps a tool out of reach entirely
    # while personal-data stripping is on, whatever the tool would return. It
    # defaults to ('erp5_download',), so this is the behaviour a service has
    # unless someone empties the list.
    services = [x for x in self.portal.portal_web_services.objectValues()
                if x.getPortalType() == "MCP Service"]
    if not services:
      self.skipTest("no MCP Service on this instance")
    service = services[0]
    tool = self.portal.portal_callables.erp5_download
    service.setPersonalDataBlockedToolList(["erp5_download"])
    text, data = service._stripPersonalData([{"type": "text"}], tool)
    self.assertIn("disabled", text)
    self.assertIsNone(data)

  def test_78_search_finds_a_document_without_knowing_its_portal_type(self):
    # The case erp5_collect cannot serve at all: a name, but no idea which
    # module holds it, so there is no listbox to point the tool at.
    sample = self.call("erp5_search", limit=1, select_list=["title"])["results"]
    title = sample[0].get("title") if sample else None
    if not title or '"' in title:
      self.skipTest("no plainly titled document to look for")
    res = self.call("erp5_search", query='title:"%s"' % title,
                    select_list=["title", "portal_type"], limit=20)
    self.assertTrue(res["results"])
    self.assertEqual(set(r["title"] for r in res["results"]), set([title]))

  def test_79_collect_says_which_tool_searches_across_modules(self):
    # It used to fail with the raw view lookup error, "KeyError:
    # 'eb_site_module'", which says nothing about what to do instead.
    res = self.call("erp5_collect", relative_url="", select_list=["title"])
    self.assertIn("error", res)
    hint = res.get("hint", "")
    self.assertIn("erp5_search", hint)
    self.assertIn("portal type", hint)

  def test_80_collect_counts_without_collecting(self):
    rows = self.call("erp5_collect", relative_url="sale_order_module",
                     filters={"portal_type": "Sale Order"},
                     select_list=["title"], max_records=1)
    counted = self.call("erp5_collect", relative_url="sale_order_module",
                        filters={"portal_type": "Sale Order"}, count_only=True)
    self.assertEqual(counted["total_count"], rows["total_count"])
    self.assertNotIn("items", counted)

  def test_81_a_bracket_inside_a_value_is_data_not_grouping(self):
    # Brackets group only outside a value. A title like "... (Demand 2024)"
    # tripped the OR/NOT guard, which threw the whole query away and answered
    # with an unfiltered result set.
    title = "zzz no such title (Demand 2024)"
    query = 'title:"%s"' % title
    search = self.call("erp5_search", query=query, select_list=["title"], limit=1)
    self.assertNotIn("warning", search)
    self.assertEqual(search.get("filters_applied", {}).get("title"), title)
    collect = self.call("erp5_collect", relative_url="sale_order_module",
                        query=query, select_list=["title"], max_records=1)
    self.assertNotIn("warning", collect)
    self.assertEqual(collect.get("filters_applied", {}).get("title"), title)

  def test_76_search_without_a_module_covers_the_whole_portal(self):
    # Left without a module, erp5_search takes the path the UI's own global
    # search field takes: no list_method, so getHateoas queries portal_catalog
    # itself. It used to pass searchFolder regardless, which scoped the search
    # to the site root -- every criterion then answered zero while an
    # unfiltered call still returned rows, so it read like "nothing matches".
    scoped = self.call("erp5_search", relative_url="sale_order_module",
                       query='portal_type:"Sale Order"', count_only=True)
    if not scoped["total_count"]:
      self.skipTest("no sale order to judge the portal-wide search on")
    whole = self.call("erp5_search", query='portal_type:"Sale Order"',
                      count_only=True)
    # scoping narrows, so the module can never hold more than the portal
    self.assertGreaterEqual(whole["total_count"], scoped["total_count"])
    # and the criterion has to bite portal-wide, not return the whole catalog
    everything = self.call("erp5_search", count_only=True)
    self.assertGreater(everything["total_count"], whole["total_count"])

  def test_77_search_reaches_several_modules_in_one_call(self):
    # Sale Orders and Organisations live in different modules, so a single
    # count that adds up to both is proof the search spanned them -- and it
    # needs no assumption about what this instance happens to hold.
    order = self.call("erp5_search", query='portal_type:"Sale Order"',
                      count_only=True)["total_count"]
    organisation = self.call("erp5_search", query='portal_type:"Organisation"',
                             count_only=True)["total_count"]
    if not (order and organisation):
      self.skipTest("this instance has no two kinds of document to span")
    both = self.call(
      "erp5_search",
      query='portal_type:"Sale Order" portal_type:"Organisation"',
      count_only=True)["total_count"]
    self.assertEqual(both, order + organisation)

  def test_72_search_points_at_collect_when_a_column_stays_blank(self):
    # A column only the module's own list_method can resolve comes back empty
    # instead of failing, so a criterion on it silently did nothing. The row
    # set looks fine, which is exactly why the tool has to say something.
    res = self.call("erp5_search", relative_url="accounting_module",
                    query='operation_date:">=2024-06-01"',
                    select_list=["title", "operation_date"], limit=3)
    if not res.get("results"):
      self.skipTest("accounting_module holds no row to judge the hint on")
    hint = res.get("hint", "")
    self.assertIn("operation_date", hint)
    self.assertIn("NOT applied", hint)
    self.assertIn("erp5_collect", hint)

  def test_73_search_says_so_when_it_drops_a_query_it_cannot_map(self):
    # OR/NOT/parentheses were dropped whole and the caller got an unfiltered
    # result that read like an answer.
    res = self.call("erp5_search", relative_url="sale_order_module",
                    query='( title:"%zzz_no_such_title%" OR title:"%zzz_none%" )',
                    select_list=["title"], limit=1)
    self.assertIn("OR/NOT/parentheses", res.get("warning", ""))
    self.assertNotIn("filters_applied", res)

  def test_74_collect_reports_the_defaults_the_listbox_applies(self):
    # The listbox narrows the rows before any filter of the caller's, and used
    # to do it invisibly.
    res = self.call("erp5_collect", relative_url="sale_order_module",
                    select_list=["title"], max_records=1)
    self.assertIn("portal_type", res.get("module_defaults", {}))

  def test_75_collect_does_not_flag_an_overridden_module_default(self):
    # A key the module passes itself is a parameter of its list_method:
    # overriding it is legitimate and must not read as a suspect column -- the
    # "no effect" warning it once got blames a column the script merely
    # displays, when AccountingTransactionModule_getAccountingTransactionList
    # in fact pops and uses section_category. The count probe behind that
    # warning cannot see the difference on an instance that holds no
    # accounting row at all: 0 rows come back with or without the criterion.
    # And a blanket assertNotIn("warning", res) would demand more than the fix
    # gives: with max_records=1 on any stocked module the answer legitimately
    # carries the truncation warning, so what is pinned here is that the
    # overridden key stays unnamed.
    res = self.call("erp5_collect", relative_url="accounting_module",
                    filters={"section_category": ""}, select_list=["title"],
                    max_records=1)
    if "section_category" not in res.get("module_defaults", {}):
      self.skipTest("this accounting listbox declares no section_category default")
    self.assertNotIn("section_category", res.get("warning", ""))

  def test_70_search_turns_two_bounds_into_one_range(self):
    # 'date:>=A AND date:<B' used to keep only the last term per column, so the
    # lower bound vanished and the answer covered everything before B.
    res = self.call("erp5_search", relative_url="sale_order_module",
                    query='modification_date:">=2026-07-01" AND modification_date:"<2100-01-01"',
                    select_list=["modification_date"], limit=5)
    self.assertEqual(res.get("filters_applied", {}).get("modification_date"),
                     {"query": ["2026-07-01", "2100-01-01"], "range": "minmax"})

  def test_71_collect_reads_a_quoted_comparison_as_a_comparison(self):
    # Quoting says "this is one value", not "match the literal string '>=...'".
    # Read as an equality, two bounds became a list, which SQLCatalog takes as
    # "either of these" -- a range query answered with rows from outside it.
    res = self.call("erp5_collect", relative_url="sale_order_module",
                    query='modification_date:">=2026-07-01" AND modification_date:"<2100-01-01"',
                    select_list=["title"], max_records=1)
    self.assertEqual(res.get("filters_applied", {}).get("modification_date"),
                     {"query": ["2026-07-01", "2100-01-01"], "range": "minmax"})

  def test_68_collect_flags_a_filter_column_the_catalog_drops(self):
    # getHateoas calls SQLCatalog with ignore_unknown_columns, so a criterion on
    # a column it cannot map is dropped and the rows come back looking filtered.
    # Nothing in the answer says so, which is why the tool has to.
    plain = self.call("erp5_collect", relative_url="sale_order_module",
                      select_list=["title"], max_records=1)
    bogus = self.call("erp5_collect", relative_url="sale_order_module",
                      filters={"zzz_no_such_column": "%nothing%"},
                      select_list=["title"], max_records=1)
    self.assertEqual(bogus["total_count"], plain["total_count"])
    warning = bogus.get("warning", "")
    self.assertIn("zzz_no_such_column", warning)
    self.assertIn("no effect", warning)

  def test_69_collect_flags_a_single_date_as_an_equality(self):
    # A bare date on a date column tests one exact timestamp (00:00:00 of that
    # day), not the period the caller almost always means.
    res = self.call("erp5_collect", relative_url="sale_order_module",
                    filters={"start_date": "2024-06-01"},
                    select_list=["title"], max_records=1)
    warning = res.get("warning", "")
    self.assertIn("start_date", warning)
    self.assertIn("single date", warning)

  def order(self, tag):
    # The title is made unique per document: sale_order_module is shared and a
    # killed run leaves fixtures behind, which would break an exact-count
    # assertion for a reason unrelated to filtering.
    #
    # The title is set through the ZODB API rather than erp5_write on purpose.
    # erp5_write replays the whole form, and consecutive tool calls inside one
    # test share self.portal.REQUEST, so a second write inherits the first
    # one's field_my_title -- which silently gave two orders the same title.
    #
    # Indexing goes through self.tic(). It drains the WHOLE activity queue, so
    # make sure that queue is empty before starting a run: anything heavy left
    # pending (builder alarms, _updateSimulation) gets written inside the test
    # transaction, and teardown rolling that back is what wedges MariaDB.
    res = self.call("erp5_create", relative_url="sale_order_module",
                    portal_type="Sale Order")
    self.assertNotIn("error", res, res)
    rel = str(res["relative_url"])
    self._cleanup.append(rel)
    title = "%s-%s" % (tag, rel.rstrip("/").split("/")[-1])
    document = self.portal.unrestrictedTraverse(rel)
    document.setTitle(title)
    self.tic()
    return title

  def test_56_inspect_reports_what_may_be_searched_and_sorted(self):
    # The displayed columns are not the searchable ones, so a caller shown only
    # column_list guesses filter keys the listbox never accepts.
    module = self.call("erp5_inspect", modules="sale_order_module")["sale_order_module"]
    for key in ("columns", "search_columns", "sort_columns"):
      self.assertIn(key, module, module)
      self.assertTrue(module[key], (key, module))
      for pair in module[key]:
        self.assertEqual(len(pair), 2, pair)
    searchable = sorted([str(c[0]) for c in module["search_columns"]])
    displayed = sorted([str(c[0]) for c in module["columns"]])
    self.assertIn("title", searchable)
    # the two really are read from different listbox properties
    self.assertNotEqual(searchable, displayed)

  def test_57_filters_narrow_the_listbox_to_the_matching_row(self):
    keep = self.order("ZZMcpFilterKeep")
    self.order("ZZMcpFilterDrop")
    rows = self.collect("sale_order_module", filters={"title": keep},
                        select_list=["title"])
    self.assertEqual(rows["total_count"], 1, rows)
    self.assertEqual(self.collected_titles(rows), [keep])
    self.assertEqual(rows["filters_applied"], {"title": keep})

  def test_58_a_column_query_is_routed_to_a_filter_not_to_fulltext(self):
    # The regression itself: this used to answer 0 rows and no error.
    title = self.order("ZZMcpQueryRouted")
    rows = self.collect("sale_order_module", query='title:"%s"' % title,
                        select_list=["title"])
    self.assertEqual(rows["total_count"], 1, rows)
    self.assertEqual(rows["filters_applied"], {"title": title})
    self.assertNotIn("full_text", rows)   # nothing was left for the fulltext leg

  def test_59_an_explicit_filter_wins_over_the_same_column_in_the_query(self):
    wanted = self.order("ZZMcpPrecedenceWanted")
    other = self.order("ZZMcpPrecedenceOther")
    rows = self.collect("sale_order_module",
                        query='title:"%s"' % other,
                        filters={"title": wanted}, select_list=["title"])
    self.assertEqual(rows["filters_applied"], {"title": wanted})
    self.assertEqual(self.collected_titles(rows), [wanted])

  def test_60_filters_are_accepted_as_a_json_string(self):
    # MCP clients cache tool specs, so a caller on an older connection sends
    # the dict as a JSON string; it must not be dropped on the floor.
    title = self.order("ZZMcpFiltersAsString")
    rows = self.collect("sale_order_module", filters=json.dumps({"title": title}),
                        select_list=["title"])
    self.assertEqual(rows["filters_applied"], {"title": title})
    self.assertEqual(self.collected_titles(rows), [title])
    # and a value that is not JSON at all must not raise
    junk = self.collect("sale_order_module", filters="not json", max_records=1)
    self.assertNotIn("filters_applied", junk)

  def test_61_an_unmappable_query_warns_instead_of_a_silent_zero(self):
    # OR/NOT/parentheses cannot be turned into column criteria. Answering an
    # empty page for them is what kept the original bug invisible.
    rows = self.collect("sale_order_module", max_records=1,
                        query='title:"ZZMcpA" OR title:"ZZMcpB"')
    self.assertIn("warning", rows)
    self.assertIn("filters", rows["warning"])
    self.assertNotIn("filters_applied", rows)
    self.assertEqual(rows["items"], [])

  def test_62_module_defaults_are_merged_with_the_filters_not_replaced(self):
    # accounting_module's listbox scopes itself through default_param_json. If
    # the filters replaced that dict instead of merging into it, the filtered
    # search could report rows the plain listbox never shows.
    base = self.collect("accounting_module", max_records=1)
    narrowed = self.collect("accounting_module", max_records=1,
                            filters={"portal_type": ["Sale Invoice Transaction"]})
    self.skip_without_accounting_row(base)
    self.assertTrue(0 < narrowed["total_count"] <= base["total_count"],
                    (narrowed["total_count"], base["total_count"]))

  ############################################################################
  # Range criteria in `query`.
  #
  # 'operation_date:>=2024-06-01 AND operation_date:<2024-07-01' used to be
  # turned into two literal equality values, so a June query came back with a
  # November invoice while filters_applied claimed the filter had been applied.
  # Silently wrong beats not filtering at all only in the sense of being worse.
  #
  # These tests create nothing and never call tic(): they read the dates they
  # need out of the module at runtime, so they neither depend on fixtures nor
  # drain the activity queue.
  ############################################################################

  def skip_without_accounting_row(self, rows):
    """Skip where an instance holds no accounting transaction to judge on.

    These tests read the dates they need out of the module instead of creating
    documents, which keeps them free of fixtures and of tic(). The price is
    that an empty accounting_module leaves them nothing to assert about, and a
    test that cannot run should say so rather than report a defect.
    """
    if not rows["total_count"]:
      self.skipTest("this instance has no accounting transaction to judge on")

  def as_date(self, value):
    from DateTime import DateTime
    return DateTime(value)

  def date_list(self, rows):
    return [self.as_date(x["operation_date"]) for x in rows["items"]
            if x.get("operation_date")]

  def test_63_a_comparison_in_query_becomes_a_range_criterion(self):
    # the shape matters, not just the row count: two literal values here is
    # exactly the regression, and it reports itself as a successful filter
    rows = self.collect("accounting_module", max_records=1,
                        select_list=["operation_date"],
                        query="operation_date:>=2024-06-01"
                              " AND operation_date:<2024-07-01")
    applied = rows["filters_applied"]["operation_date"]
    self.assertEqual(applied["range"], "minmax")
    self.assertEqual([str(x) for x in applied["query"]],
                     ["2024-06-01", "2024-07-01"])

  def test_64_a_narrow_range_returns_a_subset_of_a_wider_one(self):
    wide = self.collect("accounting_module", max_records=200,
                        select_list=["operation_date"],
                        query="operation_date:>=2024-01-01"
                              " AND operation_date:<2025-01-01")
    narrow = self.collect("accounting_module", max_records=200,
                          select_list=["operation_date"],
                          query="operation_date:>=2024-09-01"
                                " AND operation_date:<2024-10-01")
    self.skip_without_accounting_row(wide)
    self.assertTrue(narrow["total_count"] <= wide["total_count"],
                    (narrow["total_count"], wide["total_count"]))
    wide_uid_set = set([x["uid"] for x in wide["items"]])
    for row in narrow["items"]:
      self.assertIn(row["uid"], wide_uid_set)
    for date in self.date_list(narrow):
      self.assertTrue(self.as_date("2024/09/01") <= date, date)
      self.assertTrue(date < self.as_date("2024/10/01"), date)

  def test_65_the_lower_bound_includes_and_the_upper_bound_excludes(self):
    # the boundary date is read from the data, so this does not depend on any
    # particular document existing. Sorted descending on purpose: transactions
    # with no operation_date sort to the front when ascending, and the sample
    # would then be an empty string rather than a date.
    sample = self.collect("accounting_module", max_records=20,
                          select_list=["operation_date"],
                          sort_on=["operation_date", "descending"])
    self.skip_without_accounting_row(sample)
    date_list = self.date_list(sample)
    self.assertTrue(date_list, sample)
    day = date_list[0].strftime("%Y-%m-%d")
    empty = self.collect("accounting_module", max_records=1,
                         query="operation_date:>=%s AND operation_date:<%s"
                               % (day, day))
    self.assertEqual(empty["total_count"], 0, empty)
    inclusive = self.collect("accounting_module", max_records=50,
                             select_list=["operation_date"],
                             query="operation_date:>=%s AND operation_date:<=%s"
                                   % (day, day))
    self.assertEqual(inclusive["filters_applied"]["operation_date"]["range"],
                     "minngt")
    self.assertTrue(inclusive["total_count"] > 0, inclusive)
    for date in self.date_list(inclusive):
      self.assertEqual(date.strftime("%Y-%m-%d"), day)

  def test_66_an_unmappable_comparison_pair_warns_and_filters_nothing(self):
    # two lower bounds cannot be expressed as one criterion. Guessing at one
    # would be the same class of bug as the original, so nothing is applied.
    base = self.collect("accounting_module", max_records=1)
    clash = self.collect("accounting_module", max_records=1,
                         query="operation_date:>=2024-06-01"
                               " AND operation_date:>=2024-07-01")
    self.assertIn("warning", clash)
    self.assertIn("operation_date", clash["warning"])
    self.assertNotIn("filters_applied", clash)
    self.assertEqual(clash["total_count"], base["total_count"])

  def test_67_sort_on_accepts_a_bare_column_name_and_a_pair(self):
    # getHateoas json.loads() every sort_on entry, so a bare column name used
    # to fail with "No JSON object could be decoded" -- a message that says
    # nothing about the real cause
    ascending = self.collect("accounting_module", max_records=20,
                             select_list=["operation_date"],
                             sort_on="operation_date")
    descending = self.collect("accounting_module", max_records=20,
                              select_list=["operation_date"],
                              sort_on=["operation_date", "descending"])
    self.skip_without_accounting_row(ascending)
    up = self.date_list(ascending)
    down = self.date_list(descending)
    self.assertTrue(up, ascending)
    self.assertTrue(down, descending)
    self.assertEqual(up, sorted(up))
    self.assertEqual(down, sorted(down, reverse=True))
    self.assertTrue(down[0] >= up[0], (down[0], up[0]))

  def test_68_stock_point_change_is_not_reverted(self):
    # Regression: erp5_write used to resubmit every editable field of the
    # form. On a Sale Packing List line that replay re-bound the resource
    # relation, and ERP5 then recomputed the line's Source Stock Point from
    # that resource -- so an explicit stock point change was silently
    # reverted to the resource's default. Base_edit preserves fields the form
    # does not submit, so the tool now submits only the fields the caller
    # supplied, and an untouched resource (or stock point) is left alone.
    spl = self.create("sale_packing_list_module", "Sale Packing List")
    line = self.create_sub(spl, "Sale Packing List Line")
    self.tic()
    r = self.call("erp5_read", relative_url=line, all_editable=True)
    my_source = r["fields_by_view"]["view"]["my_source"]
    choices = [c["value"] for c in my_source["value"]["valid_choices"]
               if c.get("value")]
    self.assertTrue(choices, r)
    self.call("erp5_write", relative_url=line,
              field_values={"field_my_resource_title": "Screw Ring"})
    self.tic()
    obj = self.portal.unrestrictedTraverse(line)
    current = obj.getSource()
    target = next((c for c in choices if c != current), choices[0])
    w = self.call("erp5_write", relative_url=line,
                  field_values={"field_my_source": target})
    self.assertEqual(w.get("status"), "success", w)
    self.tic()
    self.assertEqual(obj.getSource(), target,
                     "writing the source stock point did not persist")
    w2 = self.call("erp5_write", relative_url=line,
                   field_values={"field_my_title": "ZZMcpStockPointFixed"})
    self.assertEqual(w2.get("status"), "success", w2)
    self.tic()
    self.assertEqual(obj.getSource(), target,
                     "an unrelated write reverted the source stock point")
