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

def _browser_url(rel):
  if not rel:
    return ""
  portal = context.getPortalObject()
  req = portal.REQUEST
  u = (req.get("URL") or req.get("ACTUAL_URL") or "").split("?")[0]
  marker = "/portal_web_services/"
  base = u.split(marker)[0] if marker in u else portal.absolute_url()
  return base + "/#/" + rel

raw = context.ERP5Document_getHateoas(
  mode="traverse", relative_url=relative_url, view=(view or "view"), restricted=1)
def path_probe(rel):
  # An empty body means no view was rendered, and that covers three different
  # things: the path is not there, the user may not see it, or the type has no
  # view to build. Resolving the path tells the last apart from the first two;
  # restrictedTraverse answers None for both "absent" and "not allowed", so the
  # message below claims no more than that.
  try:
    target = context.getPortalObject().restrictedTraverse(str(rel), None)
  except Exception:
    target = None
  if target is None:
    return None
  try:
    return str(target.getPortalType())
  except Exception:
    return "?"

if isinstance(raw, str) and not raw.strip():
  # getHateoas answers with an empty body and a 404 on the shared RESPONSE
  # rather than raising, so json.loads("") was left to fail with "No JSON object
  # could be decoded" -- a message naming neither the path nor a way forward.
  probed = path_probe(relative_url)
  if probed is None:
    return mcp_ret({"error": "nothing readable at '%s': ERP5 rendered no view"
      " for it and the path does not resolve, so it either does not exist or the"
      " current user may not see it." % relative_url,
      "hint": "Check the id with erp5_discover, which lists every module, or find"
        " the document itself with erp5_search. A portal type does not imply a"
        " module of the same name: invoices, for one, are documents of"
        " accounting_module.",
      "relative_url": relative_url}, ensure_ascii=False)
  return mcp_ret({"error": "'%s' exists and is a %s, but ERP5 rendered no view"
    " for it: getHateoas returned an empty body, which is what it does for a type"
    " that has no view action of its own or whose form cannot be built."
    % (relative_url, probed),
    "hint": "The path is right, the document simply cannot be displayed on its"
      " own. Read its parent, which usually lists it, or take its catalogued"
      " fields from erp5_search. What the type does offer is under"
      " portal_types/%s." % probed,
    "relative_url": relative_url, "portal_type": probed}, ensure_ascii=False)
data = json.loads(raw) if isinstance(raw, str) else raw
links = data.get("_links", {})
ev = data.get("_embedded", {}).get("_view", {})

def is_listbox_key(key, fd):
  if key == "listbox":
    return True
  return isinstance(fd, dict) and "list_method_template" in fd

def extract_value(fd, include_choices=False):
  if not isinstance(fd, dict):
    return fd
  ftype = fd.get("type", "")
  default = fd.get("default", "")
  if "field_gadget_param" in fd:
    return fd["field_gadget_param"].get("default", "")
  if ftype in ("RelationStringField", "MultiRelationStringField"):
    return {"value": default, "portal_types": fd.get("portal_types", []),
            "urls": fd.get("relation_item_relative_url", [])}
  if ftype == "MatrixBox":
    return {"matrix_data": fd.get("data", []),
            "template_field_dict": fd.get("template_field_dict", {})}
  if ftype == "FormBox":
    sub_view = fd.get("_embedded", {}).get("_view", {})
    if not sub_view:
      return {}
    sub_fields = {}
    for sk, sv in sub_view.items():
      if sk.startswith("_") or sk == "form_id" or not isinstance(sv, dict):
        continue
      if sv.get("hidden"):
        continue
      sub_fields[sk] = {"title": sv.get("title", sk), "value": sv.get("default", ""),
        "editable": bool(sv.get("editable", 0)), "type": sv.get("type", "unknown"),
        "key": sv.get("key", "")}
    return sub_fields
  if include_choices and ftype in ("ListField", "RadioField", "ParallelListField", "MultiListField"):
    items = []
    for it in fd.get("items", []):
      if isinstance(it, (list, tuple)) and len(it) >= 2 and it[1]:
        items.append({"label": it[0], "value": it[1]})
    return {"value": default, "valid_choices": items}
  return default

def is_empty(v):
  if v is None or v == "" or v == [] or v == {}:
    return True
  if not isinstance(v, dict):
    return False
  if "portal_types" in v and "urls" in v:
    val = v.get("value"); urls = v.get("urls", [])
    if isinstance(val, list):
      v_empty = True
      for x in val:
        if x:
          v_empty = False
          break
    else:
      v_empty = not val
    return v_empty and not urls
  if "matrix_data" in v:
    return not v.get("matrix_data")
  if "valid_choices" in v and "value" in v:
    return is_empty(v.get("value"))
  allsub = bool(v)
  for sv in v.values():
    if not (isinstance(sv, dict) and "value" in sv):
      allsub = False
      break
  if allsub:
    for sv in v.values():
      if not is_empty(sv.get("value")):
        return False
    return True
  return False

def named(link_key):
  rawl = links.get(link_key, [])
  if isinstance(rawl, dict):
    rawl = [rawl]
  return [{"name": a.get("name", ""), "title": a.get("title", "")} for a in rawl]

def simplify(ev_, include_choices=False):
  out = {}
  for key, fd in ev_.items():
    if key.startswith("_") or key in ("form_id",) or is_listbox_key(key, fd):
      continue
    out[key] = {"title": fd.get("title", key) if isinstance(fd, dict) else key,
      "value": extract_value(fd, include_choices),
      "editable": bool(fd.get("editable", 0)) if isinstance(fd, dict) else False,
      "type": fd.get("type", "unknown") if isinstance(fd, dict) else "unknown"}
  return out

views = named("action_object_view")
resolved = links.get("traversed_document", {}).get("name", relative_url)
ae = all_editable if isinstance(all_editable, bool) else (str(all_editable).lower() in ("1", "true", "yes"))

if ae:
  def editable_only(fdict):
    r = {}
    for k, v in fdict.items():
      if v.get("editable") and v.get("type") != "LabelField":
        r[k] = v
    return r
  fields_by_view = {}
  default_view = view or "view"
  ed = editable_only(simplify(ev, True))
  if ed:
    fields_by_view[default_view] = ed
  for vinfo in views:
    vname = vinfo.get("name", "")
    if not vname or vname == default_view:
      continue
    try:
      vraw = context.ERP5Document_getHateoas(mode="traverse", relative_url=str(relative_url), view=str(vname), restricted=1)
      vdata = json.loads(vraw) if isinstance(vraw, str) else vraw
      ved = editable_only(simplify(vdata.get("_embedded", {}).get("_view", {}), True))
      if ved:
        fields_by_view[vname] = ved
    except Exception:
      pass
  return mcp_ret({"title": data.get("title", ""), "portal_type": links.get("type", {}).get("name", ""),
    "relative_url": resolved, "url": _browser_url(resolved), "all_editable": True,
    "fields_by_view": fields_by_view, "views": views}, ensure_ascii=False)

fields = {}
for key, fd in ev.items():
  if key.startswith("_") or key in ("form_id",) or is_listbox_key(key, fd):
    continue
  value = extract_value(fd)
  editable = bool(fd.get("editable", 0)) if isinstance(fd, dict) else False
  # An empty read-only field carries no information, but an empty editable one
  # is precisely what the caller is expected to fill in -- and on a dialog form
  # every input starts empty, so skipping them hid the fields that had to be
  # passed: a report dialog came back listing only the inputs that happened to
  # carry a default, while its date, count and offset fields were missing
  # entirely. Empty is now a reason to hide a field only when it cannot be
  # written either.
  if is_empty(value) and not editable:
    continue
  fields[key] = {"title": fd.get("title", key) if isinstance(fd, dict) else key, "value": value,
    "editable": editable,
    "type": fd.get("type", "unknown") if isinstance(fd, dict) else "unknown"}

def form_rel_from_template(tmpl):
  if not tmpl:
    return ""
  base = tmpl.split("{")[0]
  q = base.split("?", 1)[1] if "?" in base else ""
  for pair in q.split("&"):
    if pair.startswith("form_relative_url="):
      return pair.split("=", 1)[1]
  return ""

all_listboxes = {}
for key, fd in ev.items():
  if key.startswith("_"):
    continue
  if is_listbox_key(key, fd) and isinstance(fd, dict):
    all_listboxes[key] = {"title": fd.get("title", ""), "columns": fd.get("column_list", []),
      "portal_type": fd.get("portal_type", []), "default_sort": fd.get("sort", []),
      "form_relative_url": form_rel_from_template(fd.get("list_method_template", ""))}

report_list = named("action_object_jio_report")
payload = {"title": data.get("title", ""), "portal_type": links.get("type", {}).get("name", ""),
  "relative_url": resolved, "url": _browser_url(resolved), "parent": links.get("parent", {}).get("name", ""),
  "fields": fields, "workflows": named("action_workflow"), "actions": named("action_object_jio_action"),
  "views": views, "jumps": named("action_object_jio_jump"), "exchanges": named("action_object_jio_exchange"),
  "prints": named("action_object_jio_print"), "reports": report_list, "all_listboxes": all_listboxes or None,
  "has_create_action": links.get("action_object_new_content_action") is not None}

# A report action was listed here with nothing saying what runs it: erp5_download
# documents only 'exchanges' and 'prints', so by the documentation a 'reports'
# entry belonged to no tool at all, and the name of the form actually holding
# the rows appears nowhere on the read-only path.
if report_list:
  payload["reports_hint"] = ("A report returns a TABLE. Pass its name to"
    " erp5_collect as 'view' -- erp5_collect(relative_url=\"%s\", view=\"%s\")"
    " -- and you get its rows; erp5_collect follows the report's parameter"
    " dialog to the form that holds them. Read the action itself"
    " (erp5_read(relative_url=\"%s\", view=\"%s\")) to see its parameters."
    " Use erp5_download with the same action_name only when you want the"
    " rendered PDF/ODS/XLSX file instead of rows."
    % (relative_url, report_list[0].get("name", ""),
       relative_url, report_list[0].get("name", "")))

# Reading a report action lands on its dialog, and a dialog holds no rows -- so
# this answered all_listboxes: null, which under the documented
# erp5_read -> erp5_collect flow reads as "nothing to collect here, stop". Say
# where the rows are instead, and name the form that has them.
put_action = ev.get("_actions", {}).get("put", {})
if not isinstance(put_action, dict):
  put_action = {}
if "Base_callDialogMethod" in str(put_action.get("href") or ""):
  dialog_parameter_dict = {}
  for field_id, field_data in ev.items():
    if field_id.startswith("_") or not isinstance(field_data, dict):
      continue
    if not field_data.get("editable") or field_data.get("hidden"):
      continue
    dialog_parameter_dict[field_id] = {
      "title": field_data.get("title", field_id),
      "type": field_data.get("type", "unknown"),
      "value": field_data.get("default", "")}
  payload["dialog"] = {
    "renders": str(put_action.get("action") or ""),
    "parameters": dialog_parameter_dict,
    "rows": ("all_listboxes is null because this is a parameter dialog, not a"
      " table -- that is expected and does not mean there is nothing to read."
      " The rows are in the form named under 'renders'."
      " erp5_collect(relative_url=\"%s\", view=\"%s\") returns them and"
      " follows this dialog for you. The parameters above are passed to"
      " erp5_collect in 'filters' without their your_ prefix; the response"
      " lists the names the report's own script accepts under"
      " list_method_parameters. erp5_download with the same action_name returns"
      " the same report as a file." % (relative_url, view))}
  if all_listboxes:
    # Some dialogs hold their table themselves rather than rendering a second
    # form -- a resource stock view is one -- and telling that caller
    # "all_listboxes is null" was simply false: it is right there above.
    payload["dialog"]["rows"] = ("This dialog carries its own table: it is the"
      " one listed under all_listboxes above, and"
      " erp5_collect(relative_url=\"%s\", view=\"%s\") returns its rows. The"
      " parameters above narrow them -- pass them in filters without the your_"
      " prefix, under the names the response then lists as"
      " list_method_parameters." % (relative_url, view))

return mcp_ret(payload, ensure_ascii=False)
