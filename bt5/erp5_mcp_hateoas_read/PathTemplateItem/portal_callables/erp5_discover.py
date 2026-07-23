def mcp_ret(o, *a, **k):
  return json.dumps(_mcp_unicode(o), ensure_ascii=False), o
def _mcp_unicode(value):
  # json.dumps(ensure_ascii=False) joins its output chunks on Python 2, so a
  # payload mixing unicode with utf-8 str makes that join decode the bytes as
  # ascii and die on the first umlaut: "'ascii' codec can't decode byte 0xc3".
  # Here the mix is structural -- the worklist comes back from
  # ERP5Document_getHateoas as unicode, while a module title read through
  # Localizer is a native str -- so it breaks on any localised instance while
  # an all-ascii one never notices. Decode everything once, up front.
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
result = {}
try:
  wraw = context.ERP5Document_getHateoas(mode="worklist", restricted=1)
  wdata = json.loads(wraw) if isinstance(wraw, str) else wraw
  worklist = []
  for item in wdata.get("worklist", []):
    entry = {"name": item.get("name", ""), "count": item.get("count")}
    m = item.get("module", "")
    if m.startswith("urn:jio:get:"):
      entry["module"] = m[len("urn:jio:get:"):]
    worklist.append(entry)
  result["portal_title"] = wdata.get("_links", {}).get("portal", {}).get("name", "ERP5")
  result["worklist"] = worklist
  result["total_pending"] = sum(w["count"] for w in worklist if w["count"] is not None)
except Exception, e:
  result["worklist"] = []; result["worklist_error"] = str(e); result["total_pending"] = 0
try:
  portal = context.getPortalObject()
  check = portal.portal_membership.checkPermission
  by_app = {}
  count = 0
  for module_id in portal.objectIds():
    if not module_id.endswith("_module"):
      continue
    try:
      module = getattr(portal, module_id)
    except Exception:
      continue
    if not check("View", module):
      continue
    try:
      app = module.getBusinessApplicationTranslatedTitle() or ""
    except Exception:
      app = ""
    try:
      title = module.getTranslatedTitle() or module_id
    except Exception:
      title = module_id
    by_app.setdefault(app, []).append({"id": module_id, "title": title})
    count += 1
  for app in by_app:
    by_app[app].sort(key=lambda m: m["title"])
  result["modules_by_application"] = by_app
  result["module_count"] = count
except Exception, e:
  result["modules_by_application"] = None; result["module_count"] = 0; result["modules_error"] = str(e)
result["tip"] = 'Use erp5_guide(tutorial="list") to see step-by-step tutorials for common operations (creating documents, workflows, accounting, etc.).'
return mcp_ret(result, ensure_ascii=False)
