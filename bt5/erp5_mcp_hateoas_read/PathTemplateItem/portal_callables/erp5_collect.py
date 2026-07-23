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
from base64 import urlsafe_b64decode, urlsafe_b64encode

def is_text(value):
  # duck-typed: MCP hands strings over as unicode on Python 2, so an
  # isinstance(..., str) check silently misses every one of them
  return hasattr(value, "strip")

def truthy(value):
  # A client holding a cached copy of the old input schema forwards an unknown
  # parameter as a plain string, so "true"/"1" have to read as true.
  if isinstance(value, bool):
    return value
  if value in (None, ""):
    return False
  if isinstance(value, (int, float)):
    return bool(value)
  return str(value).strip().lower() in ("1", "true", "yes", "on")

view = str(view or "view")
listbox_id = str(listbox_id or "listbox")
sl = [select_list] if is_text(select_list) else (select_list or None)
maxr = min(int(max_records) if max_records not in (None, "") else 500, 500)
relative_url = str(relative_url or "")
CROSS_MODULE_ADVICE = ("This tool always works inside one listbox, so it has to"
  " be told which module. When you do not know the module -- or the portal type,"
  " which is what decides the module -- that is erp5_search's case: call it with"
  " no relative_url and it searches the whole catalog across modules, the way"
  " the UI's global search field does.")
if not relative_url:
  return mcp_ret({"error": "erp5_collect needs a document or module whose listbox to read.",
    "hint": CROSS_MODULE_ADVICE}, ensure_ascii=False)
try:
  raw = context.ERP5Document_getHateoas(mode="traverse", relative_url=relative_url, view=view, restricted=1)
except Exception as error:
  # Without this the caller gets the raw failure of the view lookup, e.g.
  # "KeyError: 'eb_site_module'" for the portal itself, which says nothing
  # about what to do instead.
  return mcp_ret({"error": "cannot read view '%s' of '%s': %s" % (view, relative_url, error),
    "hint": "Check the path with erp5_discover. " + CROSS_MODULE_ADVICE,
    "relative_url": relative_url}, ensure_ascii=False)
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
  # An empty body comes back with a 404 on the shared RESPONSE rather than as an
  # exception, so the try above never sees it and json.loads("") was left to fail
  # with "No JSON object could be decoded".
  probed = path_probe(relative_url)
  if probed is None:
    return mcp_ret({"error": "nothing readable at '%s': ERP5 rendered no view"
      " for it and the path does not resolve, so it either does not exist or the"
      " current user may not see it." % relative_url,
      "hint": "Check the id with erp5_discover, which lists every module. A"
        " portal type does not imply a module of the same name: invoices, for"
        " one, are documents of accounting_module. " + CROSS_MODULE_ADVICE,
      "relative_url": relative_url}, ensure_ascii=False)
  return mcp_ret({"error": "'%s' exists and is a %s, but ERP5 rendered no view"
    " for it, so it has no listbox to read." % (relative_url, probed),
    "hint": "The path is right, the document simply cannot be displayed on its"
      " own. Read its parent, whose listbox usually holds it. " + CROSS_MODULE_ADVICE,
    "relative_url": relative_url, "portal_type": probed}, ensure_ascii=False)
data = json.loads(raw) if isinstance(raw, str) else raw
ev = data.get("_embedded", {}).get("_view", {})
listbox = ev.get(listbox_id)

def view_name_list(payload):
  # the object_view actions the current user is left with -- on a view they
  # cannot open, this is the practical answer to "what can I look at instead"
  action_list = payload.get("_links", {}).get("action_object_view") or []
  if isinstance(action_list, dict):
    action_list = [action_list]
  return [str(a.get("name")) for a in action_list
          if isinstance(a, dict) and a.get("name")]

report_resolution = None
if not listbox:
  if not ev:
    # An empty _view is how getHateoas answers a view the current user may not
    # open: no exception, no 401, just nothing rendered. Calling that "no
    # listbox" sent the caller hunting for another listbox_id or view, when the
    # same call on a wider connection returns the form in full -- seen on
    # accounting_module, where a restricted user is left with the 'consistency'
    # action alone while zope gets the module's list view and its listbox.
    try:
      user_name = context.getPortalObject().portal_membership \
        .getAuthenticatedMember().getUserName()
    except Exception:
      user_name = None
    return mcp_ret({"error": "cannot open view '%s' of '%s': it came back empty,"
      " which is how ERP5 answers a view the current user is not allowed to see."
      " This is not a missing or misnamed listbox." % (view, relative_url),
      "hint": "Retry on a connection whose user has access to this module before"
        " trying another listbox_id or view. The same restriction also makes a"
        " module answer with zero rows rather than with a permission error.",
      "relative_url": relative_url, "user_name": user_name,
      "views_available_here": view_name_list(data)}, ensure_ascii=False)
  listbox_id_list = sorted([key for key, field in ev.items()
    if isinstance(field, dict) and field.get("type") == "ListBox"])
  if not listbox_id_list:
    # A report action is a parameter dialog, and a dialog holds no rows of its
    # own: they are in the form it renders, whose id getHateoas publishes as
    # the dialog's put action. Nothing else on the read-only path ever names
    # that form -- erp5_read shows the dialog and answers all_listboxes: null,
    # so a caller who took an entry from its 'reports' array landed here with
    # nowhere left to go. Follow the dialog once and collect what it renders.
    put_action = ev.get("_actions", {}).get("put", {})
    if not isinstance(put_action, dict):
      put_action = {}
    rendered_form = str(put_action.get("action") or "")
    if rendered_form and rendered_form != view and \
       "Base_callDialogMethod" in str(put_action.get("href") or ""):
      try:
        report_raw = context.ERP5Document_getHateoas(mode="traverse",
          relative_url=relative_url, view=rendered_form, restricted=1)
        report_data = json.loads(report_raw) \
          if (isinstance(report_raw, str) and report_raw) else {}
      except Exception:
        report_data = {}
      report_ev = report_data.get("_embedded", {}).get("_view", {})
      candidate = report_ev.get(listbox_id)
      if not candidate:
        # the rendered form names its table whatever it likes; one is unambiguous
        rendered_id_list = sorted([key for key, field in report_ev.items()
          if isinstance(field, dict) and field.get("type") == "ListBox"])
        if len(rendered_id_list) == 1:
          listbox_id = rendered_id_list[0]
          candidate = report_ev.get(listbox_id)
      if candidate:
        report_resolution = {"action": view, "rendered_form": rendered_form,
          "listbox_id": listbox_id,
          "resolved_from": "dialog _actions.put.action",
          "note": "'%s' is a parameter dialog and holds no rows itself."
            " erp5_collect followed it to '%s', the form it renders, and"
            " collected that form's table. view=\"%s\" reaches the same rows"
            " in one step." % (view, rendered_form, rendered_form)}
        data = report_data
        ev = report_ev
        listbox = candidate

def no_rows_hint(listbox_id_list, report_name_list):
  if listbox_id_list:
    return "Pass one of listbox_id_list as listbox_id."
  if view in report_name_list:
    # Saying "try a report name" here would name the very thing that just
    # failed. A report whose form renders several tables keeps them in
    # report_section_list, which getHateoas puts outside the view this tool
    # reads, so there is no single table to collect and no argument that helps.
    return ("'%s' is a report action, but the form it renders holds no single"
      " table this tool can read: a report built from several sections keeps"
      " them outside the view, and most accounting reports are built that way."
      " erp5_download(relative_url=\"%s\", action_name=\"%s\","
      " action_type=\"report\") renders it as a file instead."
      % (view, relative_url, view))
  if report_name_list:
    return ("This view holds no rows. A name from reports_available_here,"
      " passed as 'view', does return rows through this tool -- that is how a"
      " report is read.")
  return ("This view holds no rows at all. An export or print dialog produces a"
    " file rather than rows, which is erp5_download's case.")

if not listbox:
  report_link_list = data.get("_links", {}).get("action_object_jio_report") or []
  if isinstance(report_link_list, dict):
    report_link_list = [report_link_list]
  report_name_list = [str(a.get("name")) for a in report_link_list
                      if isinstance(a, dict) and a.get("name")]
  listbox_id_list = sorted([key for key, field in ev.items()
    if isinstance(field, dict) and field.get("type") == "ListBox"])
  return mcp_ret({"error": "No listbox '%s' in view '%s' of '%s'."
    % (listbox_id, view, relative_url), "listbox_id_list": listbox_id_list,
    "views_available_here": view_name_list(data),
    "reports_available_here": report_name_list,
    "hint": no_rows_hint(listbox_id_list, report_name_list)}, ensure_ascii=False)
template = listbox.get("list_method_template", "")
if not template:
  return mcp_ret({"error": "Listbox has no list_method_template."}, ensure_ascii=False)
def unq(v):
  for a, b in (("%3A", ":"), ("%2F", "/"), ("%2C", ","), ("%20", " "), ("+", " "), ("%25", "%")):
    v = v.replace(a, b)
  return str(v)
base = template.split("{")[0]
qs = base.split("?", 1)[1] if "?" in base else ""
params = {}
for pair in qs.split("&"):
  if "=" in pair:
    k, v = pair.split("=", 1)
    params[str(k)] = unq(v)

# What a report accepts is decided by its own list method, not by the catalog.
# Read that method's signature so its parameters can be named to the caller and
# -- below -- kept out of the "unknown column" warning: a criterion on 'count'
# was reported as a suspect column of a similar name when it had in fact been
# delivered to the script exactly as asked. getHateoas skips introspection for
# the generic methods for the same reason we do: they take catalog keywords,
# not parameters of their own.
GENERIC_LIST_METHOD = ("", "portal_catalog", "searchFolder", "searchResults",
                       "objectValues", "contentValues")
list_method_name = str(params.get("list_method") or "")
list_method_parameter_list = []
list_method_accepts_kw = False
if list_method_name not in GENERIC_LIST_METHOD:
  signature = None
  try:
    # erp5_collect has no top-level `portal` binding -- reaching for one raised
    # NameError straight into the except below, which silently produced no
    # parameters at all and left the misleading column warning in place.
    list_method_context = context.getPortalObject().restrictedTraverse(
      str(unq(params.get("relative_url") or "")), None)
    list_method = getattr(list_method_context, list_method_name, None)
    if list_method is not None:
      # the idiom getHateoas itself uses; ZScriptHTML_tryParams is the fallback
      # for anything that is not an ERP5 Python Script
      try:
        signature = list_method.Script_getParams()
      except Exception:
        signature = list_method.ZScriptHTML_tryParams()
  except Exception:
    signature = None
  for entry in str(signature or "").split(","):
    entry = entry.strip()
    if not entry:
      continue
    if entry.startswith("**"):
      list_method_accepts_kw = True
      continue
    if entry.startswith("*"):
      continue
    name, _, default = entry.partition("=")
    list_method_parameter_list.append(
      {"name": name.strip(), "default": default.strip() or None})
list_method_parameter_name_list = [p["name"] for p in list_method_parameter_list]

# ERP5Document_getHateoas drops its `query` argument straight into
# catalog_kw["full_text"], so a 'column:"value"' string reaches MySQL as one
# literal fulltext term and silently matches nothing. Column criteria have to
# travel in default_param_json instead: getHateoas merges that dict into
# catalog_kw and hands it to the listbox's own list_method, which is exactly
# what the UI does -- module defaults (section_category, portal_type) are kept
# and related keys resolve because the list method pulls their tables in.
def split_terms(text):
  out, buf, quoted = [], "", False
  for ch in text:
    if ch == '"':
      quoted = not quoted
      buf += ch
    elif ch in " \t\n" and not quoted:
      if buf:
        out.append(buf)
        buf = ""
    else:
      buf += ch
  if buf:
    out.append(buf)
  return out

# SQLCatalog range keywords, as the accounting list_method itself uses them:
# min = >=, nmin = >, ngt = <=, max = <.
RANGE_BY_OPERATOR = (("<=", "ngt"), (">=", "min"), ("<", "max"), (">", "nmin"))
RANGE_FOR_PAIR = {("min", "max"): "minmax", ("min", "ngt"): "minngt",
                  ("nmin", "max"): "nminmax", ("nmin", "ngt"): "nminngt"}
LOWER_BOUND_RANGE = ("min", "nmin")
UPPER_BOUND_RANGE = ("max", "ngt")

def split_bound(value):
  # '>=2024-06-01' -> ('min', '2024-06-01'); a plain value -> (None, value)
  for operator, range_keyword in RANGE_BY_OPERATOR:
    if value.startswith(operator):
      return range_keyword, value[len(operator):].strip()
  return None, value

def outside_quotes(text):
  # Grouping and OR/NOT only mean anything outside a value. A title like
  # 'ADD.SOUND ... (Demand 2024)' is data, and letting its brackets trip the
  # guard below threw the whole query away and answered with everything.
  out, quoted = "", False
  for ch in text:
    if ch == '"':
      quoted = not quoted
    elif not quoted:
      out += ch
  return out

def parse_query(text):
  # -> (column_dict, fulltext_remainder, understood, unsupported_list)
  #
  # A comparison term becomes a real SQLCatalog range criterion. Handing the
  # raw '>=2024-06-01' over as a value instead silently matches the wrong rows
  # -- a June query answered with a November invoice -- which is worse than
  # refusing, because filters_applied then claims the filter was honoured.
  if not text:
    return {}, "", 1, []
  bare = outside_quotes(text)
  upper = " %s " % bare.upper()
  if "(" in bare or ")" in bare or " OR " in upper or " NOT " in upper:
    return {}, text, 0, []
  equal, bound, rest, unsupported = {}, {}, [], []
  for term in split_terms(text):
    if term.upper() == "AND":
      continue
    head, sep, tail = term.partition(":")
    if not (sep and head) or head.startswith('"'):
      rest.append(term)
      continue
    value = tail.strip()
    if value[:1] == '"' and value[-1:] == '"':
      # quoting says "this is one value", not "this is a literal string": a
      # quoted '>=2024-06-01' is still a comparison, and reading it as an
      # equality is how a two-sided range slips through as an OR
      value = value[1:-1]
    range_keyword, value = split_bound(value)
    if range_keyword is None:
      equal.setdefault(head, []).append(value)
    else:
      bound.setdefault(head, []).append((range_keyword, value))
  found = {}
  for column, value_list in equal.items():
    if column in bound:
      unsupported.append(column)   # mixing equality and a range on one column
      continue
    found[column] = value_list[0] if len(value_list) == 1 else value_list
  for column, bound_list in bound.items():
    if column in equal:
      continue
    if len(bound_list) == 1:
      range_keyword, value = bound_list[0]
      found[column] = {"query": [value], "range": range_keyword}
      continue
    if len(bound_list) == 2:
      # explicitly lower-then-upper: sorting alphabetically puts "max" before
      # "min" and silently inverts the pair
      lower = [x for x in bound_list if x[0] in LOWER_BOUND_RANGE]
      upper = [x for x in bound_list if x[0] in UPPER_BOUND_RANGE]
      if len(lower) == 1 and len(upper) == 1:
        range_keyword = RANGE_FOR_PAIR.get((lower[0][0], upper[0][0]))
        if range_keyword is not None:
          found[column] = {"query": [lower[0][1], upper[0][1]],
                           "range": range_keyword}
          continue
    unsupported.append(column)
  return found, " ".join(rest), 1, unsupported

# MCP clients cache tool specs, so a caller on an older connection sends this
# dict as a JSON string; accept either rather than failing on connection age.
if is_text(filters):
  try:
    filters = json.loads(filters)
  except Exception:
    filters = {}

filter_dict = {}
parsed, full_text, understood, unsupported = parse_query(str(query or ""))
for k, v in parsed.items():
  filter_dict[str(k)] = v
# an explicit `filters` entry always wins over the same column parsed out of `query`
for k, v in (filters or {}).items():
  filter_dict[str(k)] = v
query_arg = str(query or "") if not understood else full_text

# The listbox carries default parameters of its own -- an accounting module
# scopes every row to a section category, for instance -- and they decide what
# the module can show at all, before any filter of ours narrows it further.
# Merging them away invisibly leaves a caller whose rows are missing with nothing
# to look at, so decode them once here and report them.
module_defaults = {}
dpj = params.get("default_param_json")
if dpj:
  try:
    module_defaults = json.loads(urlsafe_b64decode(str(dpj)))
  except Exception:
    module_defaults = {}
if filter_dict:
  merged = {}
  merged.update(module_defaults)
  merged.update(filter_dict)
  dpj = urlsafe_b64encode(str(json.dumps(merged)))

# A module listbox passes ignore_unknown_columns among its default parameters,
# so a criterion on a column SQLCatalog cannot map is dropped there and the only
# trace is a "Unknown columns [...]" line in the event log. The caller is handed
# a plausible row set in which their criterion never ran -- the worst kind of
# failure, because nothing about the answer looks wrong. Collect the filter
# columns the listbox does not search on, so they can be checked once the row
# count is known.
ALWAYS_SEARCHABLE = ("portal_type", "uid", "id", "parent_uid", "path",
                     "relative_url", "simulation_state", "validation_state",
                     "causality_state", "title", "reference")
search_column_list = []
for entry in (listbox.get("search_column_list") or []):
  search_column_list.append(
    str(entry[0]) if isinstance(entry, (list, tuple)) else str(entry))
# a key the module itself passes is a parameter of its list_method, not a
# column of ours to second-guess: overriding one is a legitimate move
# a parameter of the report's own list method is not a column either, and it
# reaches the script exactly as passed -- warning about it sent callers looking
# for a catalog problem that was never there
unlisted_column_list = [k for k in filter_dict
                        if k not in search_column_list
                        and k not in ALWAYS_SEARCHABLE
                        and k not in module_defaults
                        and k not in list_method_parameter_name_list]
report_parameter_applied = dict([(k, v) for k, v in filter_dict.items()
                                 if k in list_method_parameter_name_list])

def encode_sort_on(value):
  # getHateoas json.loads() each sort_on entry, so every one has to be a
  # serialised ["column", "direction"] pair. A bare column name went straight
  # into json.loads() and came back as "No JSON object could be decoded",
  # an error that points nowhere near the real cause.
  if not value:
    return None
  if is_text(value):
    text = value.strip()
    # a client holding a string-typed copy of this tool's spec serialises an
    # array argument into a JSON string; decode it rather than sorting on a
    # column literally named '["operation_date", "descending"]'
    if text[:1] == "[":
      try:
        return encode_sort_on(json.loads(text))
      except Exception:
        return None
    return [json.dumps([str(value), "ascending"])]
  if isinstance(value, (list, tuple)):
    if len(value) == 2 and is_text(value[0]) and is_text(value[1]) and \
       str(value[1]).lower() in ("ascending", "descending", "asc", "desc",
                                 "reverse"):
      return [json.dumps([str(value[0]), str(value[1])])]
    encoded = []
    for entry in value:
      if is_text(entry):
        encoded.append(json.dumps([str(entry), "ascending"]))
      elif isinstance(entry, (list, tuple)) and len(entry) == 2:
        encoded.append(json.dumps([str(entry[0]), str(entry[1])]))
    return encoded or None
  return None

sort_on_arg = encode_sort_on(sort_on)

def count_for(param_dict):
  # the same search, one row deep, only to read the total off it
  encoded = urlsafe_b64encode(str(json.dumps(param_dict))) if param_dict else None
  probe = context.ERP5Document_getHateoas(mode="search", relative_url=params.get("relative_url"),
    form_relative_url=params.get("form_relative_url"), list_method=params.get("list_method"),
    default_param_json=encoded, extra_param_json=params.get("extra_param_json"),
    select_list=["uid"], limit=[0, 1], query=query_arg, sort_on=None, restricted=1)
  parsed = json.loads(probe) if (isinstance(probe, str) and probe) else {}
  return parsed.get("_embedded", {}).get("count", 0)

def is_single_date(value):
  # 'YYYY-MM-DD...' as a plain value, i.e. an equality rather than a period
  if not is_text(value):
    return False
  text = value.strip()
  return len(text) >= 8 and text[:4].isdigit() and text[4:5] == "-"

if truthy(count_only):
  # The same search this tool would run, one row deep, only to read the total
  # off it. It still pays for the traverse above: the count has to describe
  # the listbox's own list_method, not the plain catalog.
  effective = {}
  effective.update(module_defaults)
  effective.update(filter_dict)
  counted = {"total_count": count_for(effective), "count_only": True,
             "relative_url": relative_url}
  if filter_dict:
    counted["filters_applied"] = filter_dict
  if module_defaults:
    counted["module_defaults"] = module_defaults
  if report_resolution:
    counted["report"] = report_resolution
  if list_method_parameter_list:
    counted["list_method"] = list_method_name
    counted["list_method_parameters"] = list_method_parameter_list
  return mcp_ret(counted, ensure_ascii=False)

columns = listbox.get("column_list", [])
select_fields = [str(x) for x in sl] if sl else ([str(c[0]) for c in columns] if columns else ["title"])
if "uid" not in select_fields:
  select_fields.append("uid")
def extract_row(item):
  row = {}
  h = item.get("_links", {}).get("self", {}).get("href", "")
  row["relative_url"] = h[len("urn:jio:get:"):] if h.startswith("urn:jio:get:") else h
  for key, val in item.items():
    if key.startswith("_") or key == "listbox_uid:list":
      continue
    if isinstance(val, dict) and "field_gadget_param" in val:
      row[key] = val["field_gadget_param"].get("default", "")
    elif isinstance(val, dict) and "default" in val:
      # A listbox column that carries a link renders each cell as
      # {"default": <the value>, "url_value": {...}} -- the url_value is a
      # renderjs command, useless to an MCP client, and leaving the wrapper in
      # place meant node_title came back as a dict instead of "TL01B", so every
      # caller had to know to dig for ["default"].
      row[key] = val["default"]
    else:
      row[key] = val
  return row
all_items = []
offset = 0
total = 0
page = min(50, maxr)
while len(all_items) < maxr:
  r2 = context.ERP5Document_getHateoas(mode="search", relative_url=params.get("relative_url"),
    form_relative_url=params.get("form_relative_url"), list_method=params.get("list_method"),
    default_param_json=dpj, extra_param_json=params.get("extra_param_json"),
    select_list=select_fields, limit=[offset, page], query=query_arg,
    sort_on=sort_on_arg, restricted=1)
  d2 = json.loads(r2) if (isinstance(r2, str) and r2) else {}
  emb = d2.get("_embedded", {})
  contents = emb.get("contents", [])
  if total == 0:
    total = emb.get("count", 0)
  if not contents:
    break
  for item in contents:
    all_items.append(extract_row(item))
  offset += len(contents)
  if offset >= total or len(contents) < page:
    break
items = all_items[:maxr]
out = {"total_count": total, "collected_count": len(items),
  "truncated": len(items) < (total or 0), "columns": columns, "items": items}
if filter_dict:
  out["filters_applied"] = filter_dict
if module_defaults:
  out["module_defaults"] = module_defaults
if report_resolution:
  out["report"] = report_resolution
if report_parameter_applied and "offset" in list_method_parameter_name_list \
   and "count" in list_method_parameter_name_list:
  # The host that windowed this report stopped after one call because it got
  # fewer rows back than the count it had asked for -- a reasonable rule for a
  # row pager and the wrong one here, where count bounds what the report
  # computes rather than the rows it yields. So do not leave the caller to
  # infer anything from the row count: hand it the next call.
  try:
    applied_count = int(report_parameter_applied.get("count") or 0)
  except Exception:
    applied_count = 0
  try:
    applied_offset = int(report_parameter_applied.get("offset") or 0)
  except Exception:
    applied_offset = 0
  if applied_count:
    out["window"] = {
      "count": applied_count, "offset": applied_offset,
      "next_offset": applied_offset + applied_count,
      "note": "This was a window over what %s computes, not over rows. How many"
        " rows came back tells you NOTHING about whether more remain: a window"
        " can be short, or empty, while later ones still have rows. Do not stop"
        " here. Call again with offset=%s, and keep going until the source"
        " itself is exhausted -- for a report windowed over the documents of a"
        " module, erp5_search(relative_url=\"%s\", count_only=true) gives the"
        " ceiling to count up to."
        % (list_method_name, applied_offset + applied_count, relative_url)}
if list_method_parameter_list:
  out["list_method"] = list_method_name
  out["list_method_parameters"] = list_method_parameter_list
  out["list_method_accepts_kw"] = list_method_accepts_kw
  if report_parameter_applied:
    out["report_parameters_applied"] = report_parameter_applied
  out["parameters_hint"] = ("These are the parameters of %s, the script that"
    " computes these rows. Pass them in 'filters' under exactly these names --"
    " a dialog shows the same things as your_<name> widgets, but the script"
    " knows them without the prefix. They are handed to the script as keyword"
    " arguments, not as catalog criteria, so what each one does is defined by"
    " that script alone: a parameter called 'count' need not be a page size."
    % list_method_name)
if query_arg:
  out["full_text"] = query_arg
warning_list = []
if out["truncated"]:
  # truncated has always been in the payload, but as a bare boolean next to two
  # numbers the caller had to compare. A host windowing a report by products
  # then loses rows twice over: max_records cuts this window short, and its
  # next call raises the report's own offset, which moves PRODUCTS -- so the
  # rows left behind here are never fetched by anything.
  if report_parameter_applied:
    warning_list.append(
      "%s of %s rows returned: max_records stopped the collection. Raising the "
      "report's own offset will NOT bring the rest back -- %s window over what "
      "the report computes, not over rows, so whatever is cut here is skipped "
      "for good. Either raise max_records (500 is the ceiling), or make the "
      "window smaller so that its rows fit under it."
      % (len(items), total, " and ".join(sorted(report_parameter_applied))))
  else:
    warning_list.append(
      "%s of %s rows returned: max_records stopped the collection, the rest "
      "were not fetched. Raise max_records (500 is the ceiling) or narrow the "
      "query." % (len(items), total))
if not understood:
  warning_list.append(
    "query uses OR/NOT/parentheses, which cannot be mapped to column criteria; "
    "it was passed as a fulltext term and probably matched nothing. Use the "
    "'filters' parameter for column criteria.")
if unsupported:
  warning_list.append(
    "no criterion was applied for %s: a column takes either one comparison, "
    "two that form a range, or an equality -- not a mix. Pass an explicit "
    "range via filters, e.g. {\"operation_date\": {\"query\": [\"2024-06-01\", "
    "\"2024-07-01\"], \"range\": \"minngt\"}}." % ", ".join(sorted(unsupported)))
if unlisted_column_list:
  # verified, not guessed: run the same search once more without these criteria
  # and see whether the result set moves at all
  effective = {}
  effective.update(module_defaults)
  for key, value in filter_dict.items():
    if key not in unlisted_column_list:
      effective[key] = value
  try:
    total_without = count_for(effective)
  except Exception:
    total_without = None
  names = ", ".join(sorted(unlisted_column_list))
  if total_without == total:
    warning_list.append(
      "no effect from the criterion on %s -- the same %s rows come back "
      "without it. A column the catalog cannot map is dropped silently, and a "
      "column that is not among this module's search columns can also mean "
      "something other than the listbox column of that name. erp5_inspect "
      "lists the usable ones under search_columns." % (names, total))
  else:
    warning_list.append(
      "not among this module's search columns: %s -- applied as a raw catalog "
      "criterion, so check that it selects what you expect: a column of a "
      "similar name can hold the other side of a relation. erp5_inspect lists "
      "the columns the listbox itself searches on under search_columns."
      % names)
# A custom list method builds its own result: a criterion on one of the columns
# it displays is handed to the script as a keyword argument and, unless that
# script does something with it, quietly does nothing. The check above only
# looks at columns the listbox does not search on, so a criterion like
# {"quantity": "<0"} on a report -- quantity IS a displayed column -- came back
# with every row and filters_applied claiming it had been honoured. That is a
# silent wrong answer, so verify these the same way: run the count again
# without them and see whether the result moves.
ignored_column_list = []
if list_method_parameter_list:
  # a key the module passes itself reaches the script as a parameter of its
  # own -- overriding one is the legitimate move test_75 pins -- so the count
  # staying equal under it proves nothing; and a key that is merely a missing
  # search column has been dealt with above. Only what is left here can be a
  # displayed column of a self-computing list method.
  candidate_list = [k for k in filter_dict
                    if k not in list_method_parameter_name_list
                    and k not in unlisted_column_list
                    and k not in module_defaults]
  if candidate_list:
    effective = {}
    effective.update(module_defaults)
    for key, value in filter_dict.items():
      if key not in candidate_list:
        effective[key] = value
    try:
      if count_for(effective) == total:
        ignored_column_list = candidate_list
    except Exception:
      ignored_column_list = []
if ignored_column_list:
  warning_list.append(
    "no effect from the criterion on %s -- the same %s rows come back without "
    "it. These rows are computed by %s, which builds its own result, so a "
    "criterion on a column it merely displays is passed to it as a keyword "
    "argument and ignored. Only the names under list_method_parameters change "
    "what it returns; anything else has to be filtered on the rows themselves."
    % (", ".join(sorted(ignored_column_list)), total, list_method_name))
date_equality_list = [k for k, v in filter_dict.items()
                      if "date" in k.lower() and is_single_date(v)]
if date_equality_list:
  warning_list.append(
    "given a single date, which tests for that exact timestamp (00:00:00 of "
    "that day) rather than for a period: %s. For a period pass a range, e.g. "
    "{\"query\": [\"2024-06-01\", \"2024-07-01\"], \"range\": \"minmax\"}."
    % ", ".join(sorted(date_equality_list)))
if warning_list:
  out["warning"] = " ".join(warning_list)
return mcp_ret(out, ensure_ascii=False)
