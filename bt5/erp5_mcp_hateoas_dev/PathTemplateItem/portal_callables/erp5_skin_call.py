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

def _required_params(script, **kw):
  try:
    sig = script.getParams()  # e.g. 'a, b=1'
  except Exception:
    try:
      sig = str(getattr(script, "_params", "") or "")
    except Exception:
      sig = ""
  required = []
  optional = {}
  for part in sig.split(","):
    part = part.strip()
    if not part:
      continue
    if "=" in part:
      optional[part.split("=")[0].strip()] = part
    else:
      required.append(part)
  return required, optional

import json
from erp5.component.module.MCPDevHelpers import abortTransaction
portal = context.getPortalObject()
ctx_obj = portal.restrictedTraverse(relative_url, None) if relative_url else portal
if ctx_obj is None:
  return mcp_ret({"error": "context not found: %s" % relative_url})
script = getattr(ctx_obj, script_id, None)
if script is None:
  ps = portal.portal_skins
  try:
    path = ps.getSkinPath(ps.getCurrentSkinName()) or ""
  except Exception:
    path = ""
  for fid in [f.strip() for f in path.split(",") if f.strip()]:
    folder = getattr(ps, fid, None)
    try:
      if folder is not None and script_id in folder.objectIds():
        script = folder[script_id].__of__(ctx_obj)
        break
    except Exception:
      pass
if script is None:
  return mcp_ret({"error": "script '%s' not found" % script_id})
required, _optional = _required_params(script)
p = json.loads(params) if isinstance(params, str) else (params or {})
cp = dict((str(k), v) for k, v in p.items())
req = portal.REQUEST
saved = dict(req.form)
for k, v in cp.items():
  req.form[k] = v
res_hint = None
if required and not set(required) & set(cp):
  # note in the response (non-fatal) so the user sees it even on success
  res_hint = ("callable takes required params %s; pass them via 'params' "
              "or the call will fail" % required)
try:
  try:
    output = script(**cp)
  except TypeError:
    output = script()
except Exception, e:
  req.form.clear(); req.form.update(saved)
  # The error is caught here, so it never escapes to the publisher and the
  # request would otherwise commit normally -- persisting everything the
  # script already did (a half-applied mutation; patch order is arbitrary on
  # this Python 2 instance). Aborting instead means: error => nothing
  # persisted. Write mutation helpers idempotently anyway (old/new marker
  # pairs, replace-or-skip), since any halfway state may have been committed
  # by an earlier version of this tool before this abort existed.
  abortTransaction()
  resp = {"error": "script call failed: %s" % _script_error(script, e),
          "script_id": script_id,
          "transaction_aborted": True}
  if res_hint:
    resp["hint"] = res_hint
  return mcp_ret(resp)
req.form.clear(); req.form.update(saved)
resp = {"script_id": script_id,
        "output": output if isinstance(output, str) else repr(output)}
if res_hint:
  resp["hint"] = res_hint
return mcp_ret(resp, ensure_ascii=False)
