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
import json
import re as _re
from erp5.component.module.MCPDevHelpers import sha256Hex, abortTransaction

portal = context.getPortalObject()

source = str(source or "")
function_name = str(function or "run")
keep_flag = keep if isinstance(keep, bool) else (str(keep).lower() in ("1", "true", "yes"))
if not source.strip():
  return mcp_ret({"error": "source is required: a full Extension Component "
                  "module source (docstring, imports, functions)"})
if not _re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", function_name):
  return mcp_ret({"error": "function must be a plain module-level function "
                  "name, got %r" % function_name})
try:
  args = json.loads(args_json) if isinstance(args_json, (str, unicode)) else (args_json or [])
  kwargs = json.loads(kwargs_json) if isinstance(kwargs_json, (str, unicode)) else (kwargs_json or {})
except Exception, e:
  return mcp_ret({"error": "args_json/kwargs_json is not valid JSON: %s" % e})
if not isinstance(args, (list, tuple)) or not isinstance(kwargs, dict):
  return mcp_ret({"error": "args_json must be a JSON array and kwargs_json a "
                  "JSON object"})

# The source digest names the component, so re-running the same payload finds
# and reuses it (idempotent re-runs against any halfway state, including one
# left by an aborted request).
digest = sha256Hex(source)[:8]
reference = str(component_reference) if component_reference else "MCPTrustedExec_" + digest
if not _re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", reference):
  return mcp_ret({"error": "component_reference must be a plain identifier, "
                  "got %r" % reference})
comps = portal.portal_components
comp_id = "extension.erp5." + reference
ext_id = "ZZ_trusted_exec_" + digest
created = comp_id not in comps.objectIds()
try:
  if created:
    comp = comps.newContent(id=comp_id, portal_type="Extension Component",
                            reference=reference, version="erp5")
  else:
    comp = comps[comp_id]
  comp.setTextContent(source)
  try:
    comp.clearRecordedProperty("text_content")
  except Exception:
    pass
  if comp.getValidationState() != "validated":
    comp.validate()
  # plug the component into the dynamic package before wiring the method
  portal.portal_components.reset()

  custom = portal.portal_skins.custom
  if ext_id in custom.objectIds():
    custom.manage_delObjects([ext_id])
  custom.manage_addProduct["ExternalMethod"].manage_addExternalMethod(
    id=ext_id, title="MCP trusted exec one-shot", module=reference,
    function=function_name)
  # Bind through the FOLDER and hand the portal explicitly as the FIRST
  # positional argument. Two things were tried instead and both fail:
  # - getattr(portal, ext_id) resolves through the skin machinery, whose
  #   per-process location cache does not know the just-added method -- and
  #   priming that cache (initializeCache) inside a request that holds an
  #   uncommitted component reset wedged a Zope thread for hours.
  # - custom[ext_id].__of__(portal) is refused by the restricted sandbox for
  #   ExternalMethod instances ("not allowed to access '__of__' in this
  #   context").
  # With the portal passed explicitly, Zope's ExternalMethod self-injection
  # never kicks in -- that fallback only applies when the first parameter is
  # NAMED 'self' -- so the function's first parameter (any name but 'self')
  # receives the ERP5 site and the payload's own arguments follow from the
  # second parameter on.
  ext = getattr(custom, ext_id)
  output = ext(portal, *tuple(args), **dict(kwargs))
except Exception, e:
  # The component, the external method AND everything the function already
  # mutated live in the same request transaction; the error is caught here,
  # so without this abort the request would commit and leave a half-applied
  # mutation plus the temp artifacts. Aborting rolls all of it back:
  # error => nothing persisted (temp artifacts included).
  abortTransaction()
  resp = {"error": "trusted exec failed: %s" % e,
          "transaction_aborted": True,
          "component_reference": reference}
  return mcp_ret(resp)

resp = {"status": "ok",
        "component_reference": reference,
        "component_created": created,
        "function": function_name}
if not keep_flag:
  cleanup_error = None
  try:
    custom.manage_delObjects([ext_id])
    comps.manage_delObjects([comp_id])
    portal.portal_components.reset()
  except Exception, e:
    cleanup_error = str(e)
  resp["cleaned_up"] = [ext_id, comp_id]
  if cleanup_error:
    resp["warning"] = "cleanup failed: %s" % cleanup_error
else:
  resp["kept"] = {"component_id": comp_id, "external_method_id": ext_id}
try:
  resp["output"] = _mcp_unicode(output)
except Exception:
  resp["output"] = repr(output)
return mcp_ret(resp)
