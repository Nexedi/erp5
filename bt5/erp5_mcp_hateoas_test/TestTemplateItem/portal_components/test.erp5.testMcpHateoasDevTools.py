# -*- coding: utf-8 -*-
##############################################################################
# Tests for the erp5_skin_write / erp5_skin_call dev-tool improvements.
#
# Covers the traps fixed in ERP5-SKIN-TOOL-IMPROVEMENTS.md:
#   * erp5_skin_call no longer answers an opaque "Script (Python) X has
#     errors." -- it surfaces the real exception message and, when a call or
#     compile fails, the stored Zope syntax traceback (script.errors), plus a
#     'hint' naming required params that were not passed.
#   * erp5_skin_write defaults params to "", echoes the params actually
#     written, reports callable_standalone, returns a real compile traceback
#     on a body that will not compile, warns on a nested 'def', and supports
#     live_test (write-then-verify, whose failure does not abort the write).
#
# Everything runs end-to-end *through the tools* in portal_callables, exactly
# like the rest of the erp5_mcp_hateoas_test suite.
##############################################################################
import json

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestMcpHateoasDevTools(ERP5TypeTestCase):

  def getTitle(self):
    return "MCP HATEOAS Dev Tools (skin write/call)"

  def afterSetUp(self):
    self.pc = self.portal.portal_callables
    self._script_to_remove = []
    self.login()

  def beforeTearDown(self):
    self.abort()
    custom = self.portal.portal_skins.custom
    for script_id in self._script_to_remove:
      try:
        if script_id in custom.objectIds():
          custom.manage_delObjects([script_id])
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

  def _write(self, script_id, body, params="", live_test=None):
    self._script_to_remove.append(script_id)
    kw = dict(script_id=script_id, body=body, params=params)
    if live_test is not None:
      kw["live_test"] = live_test
    return self.call("erp5_skin_write", **kw)

  # --- erp5_skin_write ---

  def test_01_write_echoes_params_and_reports_callable_standalone(self):
    w = self._write("ZZ_mcp_dev_plain", "return 'ok'", params="")
    self.assertEqual(w.get("status"), "created")
    self.assertEqual(w.get("params"), "")
    self.assertTrue(w.get("callable_standalone"), w)
    self.assertNotIn("hint", w)

  def test_02_write_required_param_not_callable_standalone(self):
    w = self._write("ZZ_mcp_dev_req", "return x", params="x")
    self.assertFalse(w.get("callable_standalone"), w)
    self.assertIn("x", w["hint"])
    self.assertIn("required", w["hint"])

  def test_03_write_syntax_error_reports_real_traceback(self):
    w = self._write("ZZ_mcp_dev_syn", "return [1, 2\nreturn 3", params="")
    self.assertIn("error", w, w)
    self.assertTrue(w["error"].startswith("script body did not compile"), w["error"])
    self.assertIn("Script (Python)", w["error"])  # real Zope traceback, not opaque message

  def test_04_write_nested_def_warns(self):
    body = ("def outer():\n"
            "  def inner():\n"
            "    return 1\n"
            "  return inner()\n"
            "return outer()")
    w = self._write("ZZ_mcp_dev_nest", body, params="")
    self.assertIn("warning", w, w)
    self.assertIn("nested 'def'", w["warning"])

  def test_05_write_defaults_params_and_returns_param(self):
    w = self._write("ZZ_mcp_dev_noparam", "return 1")  # params omitted -> ""
    self.assertEqual(w.get("params"), "")
    self.assertTrue(w.get("callable_standalone"), w)

  # --- erp5_skin_call ---

  def test_06_call_raising_script_reports_real_exception(self):
    script_id = "ZZ_mcp_dev_raise"
    self._write(script_id, "raise ValueError('zzboom')", params="")
    out = self.call("erp5_skin_call", script_id=script_id)
    self.assertIn("error", out)
    self.assertIn("zzboom", out["error"])
    self.assertNotIn("has errors", out["error"])

  def test_07_call_compile_broken_script_reports_zope_traceback(self):
    script_id = "ZZ_mcp_dev_broken"
    self._write(script_id, "return [1, 2\nreturn 3", params="")
    out = self.call("erp5_skin_call", script_id=script_id)
    self.assertIn("error", out)
    self.assertIn("--- zope traceback ---", out["error"])
    self.assertIn("Script (Python)", out["error"])
    self.assertIn("invalid syntax", out["error"])

  def test_08_call_non_string_return_is_reprd(self):
    script_id = "ZZ_mcp_dev_dict"
    self._write(script_id, "return {'a': 1, 'b': [1, 2]}", params="")
    out = self.call("erp5_skin_call", script_id=script_id)
    self.assertNotIn("error", out, out)
    self.assertEqual(out["output"], "{'a': 1, 'b': [1, 2]}")

  def test_09_call_required_param_hint(self):
    script_id = "ZZ_mcp_dev_needx"
    self._write(script_id, "return 'got:%s' % x", params="x")
    out = self.call("erp5_skin_call", script_id=script_id)
    self.assertIn("error", out)
    self.assertIn("hint", out, out)
    self.assertIn("x", out["hint"])
    self.assertIn("params", out["hint"])

  def test_10_call_with_required_param_succeeds(self):
    script_id = "ZZ_mcp_dev_needx2"
    self._write(script_id, "return 'got:%s' % x", params="x")
    out = self.call("erp5_skin_call", script_id=script_id, params={"x": 42})
    self.assertNotIn("error", out, out)
    self.assertEqual(out["output"], "got:42")

  # --- live_test (write-then-verify) ---

  def test_11_write_live_test_success(self):
    w = self._write("ZZ_mcp_dev_ltok", "return 'ltrun'", params="", live_test=True)
    self.assertEqual(w.get("status"), "created")
    self.assertEqual(w.get("live_test_runs"), True)
    self.assertEqual(w.get("live_test_output"), "ltrun")

  def test_12_write_live_test_failure_does_not_abort_write(self):
    w = self._write("ZZ_mcp_dev_ltfail", "raise ValueError('liveboom')",
                    params="", live_test=True)
    self.assertEqual(w.get("status"), "created")
    self.assertEqual(w.get("live_test_runs"), False)
    self.assertIn("liveboom", w.get("live_test_error", ""))

  # --- safety guards kept ---

  def test_13_write_refuses_core_script(self):
    w = self.call("erp5_skin_write", script_id="Base_edit", body="return 1")
    self.assertIn("error", w, w)
    self.assertIn("Base_edit", w["error"])


class TestMcpCallableWrite(ERP5TypeTestCase):
  """Tests for erp5_callable_write (portal_callables write tool).

  Covers create/update of Python Script and MCP Tool callables, the
  replacements machinery, the JSON-form specification handling that keeps a
  tool's Python signature in sync with its input schema, and the core-id
  guard.
  """

  def getTitle(self):
    return "MCP HATEOAS Dev Tools (callable write)"

  def afterSetUp(self):
    self.pc = self.portal.portal_callables
    self.login()

  def beforeTearDown(self):
    self.abort()

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

  INPUT_SCHEMA = {
    "required": ["foo"],
    "type": "object",
    "properties": {
      "foo": {"type": "string"},
      "bar": {"type": "integer", "default": 1},
    },
  }
  OUTPUT_SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}}}

  # --- plain Python Script ---

  def test_01_create_and_roundtrip_body_and_params(self):
    w = self.call("erp5_callable_write", script_id="ZZ_cw_plain",
                  portal_type="Python Script", title="ZZ_cw_plain",
                  body="return {'a': 1}\n", params="")
    self.assertEqual(w.get("status"), "created", w)
    self.assertEqual(w.get("portal_type"), "Python Script")
    self.assertEqual(w.get("params"), "")
    self.assertNotIn("error", w, w)
    doc = self.pc["ZZ_cw_plain"]
    self.assertEqual(doc.getBody(), "return {'a': 1}\n")
    self.assertEqual(doc.getPortalType(), "Python Script")

  def test_02_update_existing_callable_body(self):
    self.call("erp5_callable_write", script_id="ZZ_cw_upd",
              portal_type="Python Script", body="return 1\n", params="")
    w = self.call("erp5_callable_write", script_id="ZZ_cw_upd",
                  body="return 2\n", params="")
    self.assertEqual(w.get("status"), "updated", w)
    self.assertEqual(self.pc["ZZ_cw_upd"].getBody(), "return 2\n")

  def test_03_text_content_alias(self):
    w = self.call("erp5_callable_write", script_id="ZZ_cw_alias",
                  portal_type="Python Script", text_content="return 3\n",
                  params="")
    self.assertEqual(w.get("status"), "created", w)
    self.assertEqual(self.pc["ZZ_cw_alias"].getBody(), "return 3\n")

  def test_04_replacements_apply_exactly_once(self):
    self.call("erp5_callable_write", script_id="ZZ_cw_rep",
              portal_type="Python Script", body="return 'x' + 'x'\n",
              params="")
    w = self.call("erp5_callable_write", script_id="ZZ_cw_rep",
                  replacements=[{"old_string": "'x' + 'x'",
                                 "new_string": "'y'", "replace_all": False}])
    self.assertEqual(w.get("replacements_applied"), 1, w)
    self.assertEqual(w.get("status"), "updated")
    self.assertEqual(self.pc["ZZ_cw_rep"].getBody(), "return 'y'\n")

  def test_05_replacements_ambiguous_match_refused(self):
    self.call("erp5_callable_write", script_id="ZZ_cw_amb",
              portal_type="Python Script", body="return 'x' + 'x'\n",
              params="")
    w = self.call("erp5_callable_write", script_id="ZZ_cw_amb",
                  replacements=[{"old_string": "'x'", "new_string": "'y'",
                                 "replace_all": False}])
    self.assertIn("error", w, w)
    self.assertIn("exactly once", w["error"])
    # body must be untouched
    self.assertEqual(self.pc["ZZ_cw_amb"].getBody(), "return 'x' + 'x'\n")

  def test_06_replacement_not_found(self):
    self.call("erp5_callable_write", script_id="ZZ_cw_nf",
              portal_type="Python Script", body="return 1\n", params="")
    w = self.call("erp5_callable_write", script_id="ZZ_cw_nf",
                  replacements=[{"old_string": "nope", "new_string": "y",
                                 "replace_all": False}])
    self.assertIn("error", w, w)
    self.assertIn("matched 0", w["error"])

  def test_07_replace_all(self):
    self.call("erp5_callable_write", script_id="ZZ_cw_all",
              portal_type="Python Script", body="a = 'x' + 'x'\nreturn a\n",
              params="")
    w = self.call("erp5_callable_write", script_id="ZZ_cw_all",
                  replacements=[{"old_string": "'x'", "new_string": "'y'",
                                 "replace_all": True}])
    self.assertEqual(w.get("replacements_applied"), 1, w)
    self.assertEqual(self.pc["ZZ_cw_all"].getBody(),
                     "a = 'y' + 'y'\nreturn a\n")

  def test_08_params_set_directly(self):
    w = self.call("erp5_callable_write", script_id="ZZ_cw_params",
                  portal_type="Python Script", body="return x\n",
                  params="x, y=2")
    self.assertEqual(w.get("params"), "x, y=2", w)
    self.assertEqual(self.pc["ZZ_cw_params"].getParameterSignature(),
                     "x, y=2")

  def test_09_compile_error_reported(self):
    w = self.call("erp5_callable_write", script_id="ZZ_cw_syn",
                  portal_type="Python Script", body="return [1, 2\nreturn 3\n",
                  params="")
    self.assertIn("error", w, w)
    self.assertTrue(w["error"].startswith("script body did not compile"),
                    w["error"])
    self.assertIn("invalid syntax", w["error"])

  # --- MCP Tool + JSON-form specification ---

  def test_10_mcp_tool_creates_spec_and_derives_signature(self):
    w = self.call("erp5_callable_write", script_id="ZZ_cw_mt",
                  portal_type="MCP Tool", body="return {'ok': True}\n",
                  params="", input_schema=self.INPUT_SCHEMA,
                  output_schema=self.OUTPUT_SCHEMA)
    self.assertEqual(w.get("status"), "created", w)
    self.assertEqual(w.get("spec_updated"), True, w)
    self.assertEqual(w.get("params"), "foo, bar=1", w)
    spec_id = "ZZ_cw_mt_spec"
    self.assertIn(spec_id, self.pc.objectIds())
    spec = self.pc[spec_id]
    self.assertEqual(spec.getPortalType(), "JSON Form")
    self.assertEqual(json.loads(spec.getTextContent()), self.INPUT_SCHEMA)
    self.assertEqual(json.loads(spec.getResponseSchema()), self.OUTPUT_SCHEMA)
    tool = self.pc["ZZ_cw_mt"]
    self.assertEqual(tool.getSpecificationValue().getId(), spec_id)
    self.assertEqual(tool.getParameterSignature(), "foo, bar=1")
    self.assertEqual(tool.getInputSchema(), self.INPUT_SCHEMA)
    self.assertEqual(tool.getOutputSchema(), self.OUTPUT_SCHEMA)

  def test_11_mcp_tool_signature_follows_spec_change(self):
    self.call("erp5_callable_write", script_id="ZZ_cw_mt2",
              portal_type="MCP Tool", body="return 1\n", params="",
              input_schema=self.INPUT_SCHEMA)
    self.assertEqual(self.pc["ZZ_cw_mt2"].getParameterSignature(),
                     "foo, bar=1")
    other = {"required": ["baz"], "type": "object",
             "properties": {"baz": {"type": "string"}}}
    w = self.call("erp5_callable_write", script_id="ZZ_cw_mt2",
                  input_schema=other)
    self.assertEqual(w.get("spec_updated"), True, w)
    self.assertEqual(self.pc["ZZ_cw_mt2"].getParameterSignature(), "baz")

  def test_12_update_signature_from_spec_false_keeps_params(self):
    w = self.call("erp5_callable_write", script_id="ZZ_cw_mt3",
                  portal_type="MCP Tool", body="return 1\n",
                  params="x, y=1",
                  update_signature_from_spec=False)
    self.assertEqual(w.get("params"), "x, y=1", w)
    self.assertEqual(self.pc["ZZ_cw_mt3"].getParameterSignature(), "x, y=1")

  def test_13_input_schema_on_plain_script_is_ignored_with_warning(self):
    w = self.call("erp5_callable_write", script_id="ZZ_cw_notmcp",
                  portal_type="Python Script", body="return 1\n", params="",
                  input_schema=self.INPUT_SCHEMA)
    self.assertEqual(w.get("status"), "created", w)
    self.assertIn("warning", w, w)
    self.assertIn("MCP Tool", w["warning"])
    self.assertEqual(w.get("spec_updated"), False)

  # --- safety guards ---

  def test_14_refuses_core_callable(self):
    w = self.call("erp5_callable_write", script_id="Base_edit",
                  portal_type="Python Script", body="return 1\n", params="")
    self.assertIn("error", w, w)
    self.assertIn("Base_edit", w["error"])
    self.assertIn("allow_overwrite_core", w["error"])

  def test_15_allow_overwrite_core_bypasses_guard(self):
    w = self.call("erp5_callable_write", script_id="ZZ_cw_base",
                  portal_type="Python Script", body="return 1\n", params="",
                  allow_overwrite_core=True)
    self.assertEqual(w.get("status"), "created", w)

  def test_16_refuses_non_json_form_spec_collision(self):
    # a same-named non-JSON-Form object must not be hijacked as the spec
    self.pc.newContent(id="ZZ_cw_clash_spec", portal_type="Python Script",
                       reference="ZZ_cw_clash_spec")
    w = self.call("erp5_callable_write", script_id="ZZ_cw_clash",
                  portal_type="MCP Tool", body="return 1\n", params="",
                  input_schema=self.INPUT_SCHEMA)
    self.assertIn("error", w, w)
    self.assertIn("JSON Form", w["error"])