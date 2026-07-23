def mcp_ret(o, *a, **k):
  return json.dumps(_mcp_unicode(o), ensure_ascii=False), o
def _mcp_unicode(value):
  # json.dumps(ensure_ascii=False) joins its output chunks on Python 2, so a
  # payload mixing unicode with utf-8 str makes that join decode the bytes as
  # ascii and die on the first umlaut: "'ascii' codec can't decode byte 0xc3".
  # Anything read from ZODB or through Localizer is such a native str, while
  # everything from getHateoas is unicode, so the mix is the norm on a
  # localised instance and never shows up on an all-ascii one.
  if isinstance(value, str):
    decode = getattr(value, "decode", None)
    if decode is None:
      return value  # Python 3: str is already text
    try:
      return decode("utf-8")
    except Exception:
      return decode("utf-8", "replace")
  if isinstance(value, dict):
    return dict([(_mcp_unicode(k), _mcp_unicode(v)) for k, v in value.items()])
  if isinstance(value, (list, tuple)):
    return [_mcp_unicode(x) for x in value]
  return value
def _script_error(script, e):
  detail = str(e)
  # A Script(Python) that failed to compile stores the real syntax-error
  # traceback in .errors (and various versions use _v_error/_error/err_tb).
  for attr in ("errors", "_v_error", "_error", "err_tb"):
    try:
      tb = getattr(script, attr, None)
      if tb:
        if isinstance(tb, (list, tuple)):
          tb = "\n".join(str(x) for x in tb)
        detail = "%s\n--- zope traceback ---\n%s" % (detail, tb)
        break
    except Exception:
      pass
  return detail

def _parse_params(params):
  required = []
  optional = {}
  sig = str(params or "")
  for part in sig.split(","):
    part = part.strip()
    if not part:
      continue
    if "=" in part:
      optional[part.split("=")[0].strip()] = part
    else:
      required.append(part)
  return required, optional

def _nested_def(body):
  for line in (body or "").split("\n"):
    stripped = line.strip()
    if not stripped.startswith("def "):
      continue
    if len(line) - len(line.lstrip(" ")) > 0:
      return True
  return False

import json
import re as _re
from erp5.component.module.MCPDevHelpers import sha256Hex
CORE = ("Base_edit", "Base_view", "Base_doAction", "Base_redirect", "Base_callDialogMethod",
        "Base_callAction", "Base_makeWorkflowMethod", "ERP5Site_view", "Localizer_translate",
        "Workflow_statusModify")
is_core = script_id in CORE or (script_id.startswith("Base_") and "Workflow" in script_id)
aoc = allow_overwrite_core if isinstance(allow_overwrite_core, bool) else (str(allow_overwrite_core).lower() in ("1", "true", "yes"))
if is_core and not aoc:
  return mcp_ret({"error": "refusing to write core framework script '%s' (set allow_overwrite_core=true)" % script_id})
try:
  folder = context.getPortalObject().portal_skins[skin_folder]
except Exception, e:
  return mcp_ret({"error": "skin folder '%s' not found: %s" % (skin_folder, e)})
# Default params to "" and echo what was used + guidance once.
params = params if params is not None else ""
status = "updated"
existing = script_id in folder.objectIds()
if existing:
  # B6 from ERP5-MCP-SESSION-ISSUES-2026-09-25: a tool call with only
  # script_id + skin_folder emptied an existing script silently (sha256 of the
  # empty string in the audit trail). Never treat a missing/unset body as "".
  if body is None and not body_file:
    return mcp_ret({"error": "body required to update an existing script "
                    "(use erp5_skin_call to execute)",
                    "script_id": script_id, "skin_folder": skin_folder,
                    "hint": "pass body/body_file with the intended new source; "
                            "erp5_skin_call runs the script without rewriting it"})
  if body == "" and not body_file and not allow_empty:
    return mcp_ret({"error": "refusing to write an empty body over existing "
                    "script '%s' (pass allow_empty=true for an explicit wipe)"
                    % script_id,
                    "script_id": script_id, "skin_folder": skin_folder})
if not existing:
  folder.manage_addProduct["PythonScripts"].manage_addPythonScript(id=script_id)
  status = "created"
script = folder[script_id]
# body_file: authoring stays out of the tool argument; the response sha256 and
# length let the caller verify byte-exact deployment against the local file.
if body_file:
  from erp5.component.module.MCPDevHelpers import readFile
  try:
    data = readFile(str(body_file))
  except Exception, e:
    return mcp_ret({"error": "body_file unreadable: %s" % e, "body_file": str(body_file)})
  try:
    body = data.decode("utf-8")
  except UnicodeDecodeError:
    body = data.decode("utf-8", "replace")
elif body is None:
  body = ""
script.ZPythonScript_edit(str(params or ""), str(body or ""))

# surface the real state so the caller isn't surprised later
error_detail = None
for attr in ("errors", "_v_error", "_error"):
  try:
    tb = getattr(script, attr, None)
    if tb:
      if isinstance(tb, (list, tuple)):
        tb = "\n".join(str(x) for x in tb)
      error_detail = "%s" % tb
      break
  except Exception:
    pass

required, _optional = _parse_params(params)
resp = {
  "status": status,
  "script_id": script_id,
  "skin_folder": skin_folder,
  "params": params,
  "length": len(body or ""),
  "sha256": sha256Hex(body or ""),
}
if error_detail:
  resp["error"] = "script body did not compile:\n%s" % error_detail
else:
  resp["callable_standalone"] = not required
  if required:
    resp["hint"] = ("This script requires params %s. It can only be called via "
                    "erp5_skin_call by passing params={'...': ...}; a standalone "
                    "call (no params) will fail. To make it callable standalone, "
                    "give the required params defaults or pass params=''." % required)
  if _nested_def(body):
    resp["warning"] = ("Body contains a nested 'def' — Zope Script (Python) does "
                       "not support nested function definitions; use an iterative "
                       "form instead or the script will not compile.")
if live_test:
  # Optional add-on: write-then-verify. A failure here must not abort the write.
  try:
    try:
      lt_script = context.getPortalObject().portal_skins[skin_folder][script_id]
      lt_out = lt_script()
    except TypeError:
      lt_out = ("<live test: call requires params / can't run standalone; "
                "invoke via erp5_skin_call with params instead>")
    resp["live_test_runs"] = True
    resp["live_test_output"] = lt_out if isinstance(lt_out, str) else repr(lt_out)
  except Exception, e:
    resp["live_test_runs"] = False
    resp["live_test_error"] = "live test failed: %s" % _script_error(script, e)
return mcp_ret(resp, ensure_ascii=False)
