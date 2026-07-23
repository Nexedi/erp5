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
mods = modules
if isinstance(mods, str):
  mods = [m.strip() for m in mods.split(",") if m.strip()]

def form_rel_from_template(tmpl):
  if not tmpl:
    return ""
  base = tmpl.split("{")[0]
  q = base.split("?", 1)[1] if "?" in base else ""
  for pair in q.split("&"):
    if pair.startswith("form_relative_url="):
      return pair.split("=", 1)[1]
  return ""

def named_action_list(payload, link_key):
  action_list = payload.get("_links", {}).get(link_key) or []
  if isinstance(action_list, dict):
    # getHateoas emits a bare object, not a list, when there is exactly one
    action_list = [action_list]
  return [{"name": str(a.get("name", "")), "title": a.get("title", "")}
          for a in action_list if isinstance(a, dict) and a.get("name")]

result = {}
for module_id in (mods or []):
  try:
    raw = context.ERP5Document_getHateoas(mode="traverse", relative_url=module_id, view="view", restricted=1)
    if isinstance(raw, str) and not raw.strip():
      # An id with no view rendered is answered with an empty body rather than
      # an error, so json.loads("") failed with "No JSON object could be
      # decoded" -- reported per module, where it read as a fault of this tool.
      # restrictedTraverse answers None for both "absent" and "not allowed", so
      # the first message claims no more than that.
      try:
        probed_target = context.getPortalObject().restrictedTraverse(str(module_id), None)
      except Exception:
        probed_target = None
      if probed_target is None:
        result[module_id] = {"error": "nothing readable at '%s': ERP5 rendered no"
          " view for it and the path does not resolve, so it either does not"
          " exist or the current user may not see it." % module_id,
          "hint": "erp5_discover lists every module id. A portal type does not"
            " imply a module of the same name: invoices, for one, are documents"
            " of accounting_module."}
        continue
      try:
        probed = str(probed_target.getPortalType())
      except Exception:
        probed = "?"
      result[module_id] = {"error": "'%s' exists and is a %s, but ERP5 rendered"
        " no view for it, so it declares no columns here." % (module_id, probed),
        "portal_type": probed,
        "hint": "This tool inspects modules; a document or a type without a view"
          " of its own has nothing to inspect. Read its parent instead."}
      continue
    data = json.loads(raw) if isinstance(raw, str) else raw
    ev = data.get("_embedded", {}).get("_view", {})
    listbox = ev.get("listbox")
    if listbox:
      result[module_id] = {"title": listbox.get("title", ""),
        "columns": listbox.get("column_list", []),
        # column_list is only what the listbox displays; what may be filtered or
        # ordered on is declared separately and does not have to overlap. These
        # are the column names erp5_collect accepts in `filters` / `sort_on`.
        "search_columns": listbox.get("search_column_list", []),
        "sort_columns": listbox.get("sort_column_list", []),
        "portal_type": listbox.get("portal_type", []),
        "default_sort": listbox.get("sort", []),
        "form_relative_url": form_rel_from_template(listbox.get("list_method_template", ""))}
    else:
      result[module_id] = {"note": "This module's default view renders no listbox."}
    # Two other tools send callers here to find out which views a document has,
    # and this reported neither views nor reports -- so erp5_collect's own hint
    # pointed at an answer that was not here, and a report action, which is what
    # holds a module's computed tables, stayed invisible at the very step meant
    # to describe the module.
    entry = result[module_id]
    for link_key, out_key in (("action_object_view", "views"),
                              ("action_object_jio_report", "reports"),
                              ("action_object_jio_print", "prints"),
                              ("action_object_jio_exchange", "exchanges")):
      entry[out_key] = named_action_list(data, link_key)
    if entry["reports"]:
      entry["reports_hint"] = ("A report holds a computed table, not stored"
        " documents. erp5_collect(relative_url=\"%s\", view=\"%s\") returns"
        " its rows -- it follows the report's parameter dialog to the form"
        " holding them, and names the report's own parameters in the response"
        " under list_method_parameters. erp5_download with the same name"
        " renders it as a file instead."
        % (module_id, entry["reports"][0].get("name", "")))
  except Exception, e:
    result[module_id] = {"error": str(e)}
return mcp_ret(result, ensure_ascii=False)
