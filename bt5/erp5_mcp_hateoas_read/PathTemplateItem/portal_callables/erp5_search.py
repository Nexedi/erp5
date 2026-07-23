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
from base64 import urlsafe_b64encode

def norm_sort_on(s):
  # sort_on is a structured [column, direction] pair, or a list of such pairs for
  # multi-key sort, e.g. ["modification_date", "descending"] or
  # [["modification_date", "descending"], ["title", "ascending"]]. direction is
  # "ascending" or "descending" (default "ascending" if omitted). Encoded here into
  # the JSON-serialized ["col", "order"] string(s) that ERP5Document_getHateoas wants.
  if not s:
    return None
  pairs = s if isinstance(s[0], (list, tuple)) else [s]
  out = []
  for p in pairs:
    col = p[0]
    order = p[1] if len(p) > 1 else "ascending"
    out.append(json.dumps([col, order]))
  return out

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

lim = int(limit) if limit not in (None, "") else 50
off = int(offset) if offset not in (None, "") else 0
sl = [select_list] if isinstance(select_list, str) else (select_list or None)
relative_url = str(relative_url or "")
# With no list_method, getHateoas searches portal.portal_catalog itself -- the
# path the renderjs UI's own global search field takes. Naming a module means
# searchFolder, which is that same catalog scoped to the module by parent_uid.
# Passing searchFolder with no module scoped the search to the site root, which
# answered every criterion with zero rows while an unfiltered call still
# returned documents: an empty result that read like "nothing matches".
list_method = "searchFolder" if (relative_url and "/" not in relative_url) else None

# SQLCatalog range keywords: min = >=, nmin = >, ngt = <=, max = <.
RANGE_BY_OPERATOR = (("<=", "ngt"), (">=", "min"), ("<", "max"), (">", "nmin"))
RANGE_FOR_PAIR = {("min", "max"): "minmax", ("min", "ngt"): "minngt",
                  ("nmin", "max"): "nminmax", ("nmin", "ngt"): "nminngt"}
LOWER_BOUND_RANGE = ("min", "nmin")
UPPER_BOUND_RANGE = ("max", "ngt")

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
  # -> (column_dict, understood, unsupported_list)
  #
  # Two bounds on one column have to become a single range criterion. The old
  # parser kept the last term per column, so 'date:>=A AND date:<B' quietly
  # dropped the lower bound and answered with everything before B; a list of
  # two values would have been just as wrong, since SQLCatalog reads that as
  # "either of these". A single bound is left to SQLCatalog, which parses the
  # operator out of the value itself.
  if not text:
    return {}, 1, []
  bare = outside_quotes(text)
  upper = " %s " % bare.upper()
  if "(" in bare or ")" in bare or " OR " in upper or " NOT " in upper:
    return {}, 0, []
  equal, bound, rest, unsupported = {}, {}, [], []
  for term in split_terms(text):
    if term.upper() == "AND":
      continue
    head, sep, tail = term.partition(":")
    if not (sep and head) or head.startswith('"'):
      rest.append(term.strip('"'))
      continue
    value = tail.strip()
    if value[:1] == '"' and value[-1:] == '"':
      # quoting says "this is one value", not "this is a literal string": a
      # quoted '>=2024-06-01' is still a comparison, and treating it as an
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
      lower = [x for x in bound_list if x[0] in LOWER_BOUND_RANGE]
      upper_bound = [x for x in bound_list if x[0] in UPPER_BOUND_RANGE]
      if len(lower) == 1 and len(upper_bound) == 1:
        range_keyword = RANGE_FOR_PAIR.get((lower[0][0], upper_bound[0][0]))
        if range_keyword is not None:
          found[column] = {"query": [lower[0][1], upper_bound[0][1]],
                           "range": range_keyword}
          continue
    unsupported.append(column)
  if rest and not found:
    found["title"] = "%" + " ".join(rest) + "%"
  return found, 1, unsupported

filters, understood, unsupported = parse_query(str(query or ""))
default_param_json = urlsafe_b64encode(json.dumps(filters)) if filters else None

warning_list = []
if not understood:
  warning_list.append(
    "query uses OR/NOT/parentheses, which cannot be mapped to column criteria; "
    "it was ignored and the result is unfiltered.")
if unsupported:
  warning_list.append(
    "no criterion was applied for %s: a column takes either one comparison, "
    "two that form a range, or an equality -- not a mix." % ", ".join(sorted(unsupported)))

if truthy(count_only):
  # One catalog COUNT(*) instead of paging through every row to add the pages
  # up. countFolder is searchFolder's counting twin -- same parent scoping,
  # same filters -- and both are fed the filters parsed above, so the number
  # describes exactly the search this tool would otherwise have run. Keeping
  # it here rather than in a tool of its own is what guarantees that: a
  # separate counter would have to re-implement parse_query and could drift
  # from it silently.
  portal = context.getPortalObject()
  folder = portal.restrictedTraverse(relative_url, None) if relative_url else None
  if relative_url and folder is None:
    return mcp_ret({"error": "not found: %s" % relative_url})
  count_kw = {}
  for key, value in filters.items():
    # Python 2 keyword names must be native str, while JSON decoding yields text.
    try:
      count_kw[str(key)] = value
    except Exception:
      return mcp_ret({"error": "filter name is not a usable catalog column: %s" % key,
        "relative_url": relative_url})
  # countResults is to portal_catalog what countFolder is to a folder: the
  # counting twin of the search this tool would otherwise have run.
  counter = (portal.portal_catalog.countResults if folder is None
             else getattr(folder, "countFolder", None))
  if counter is None:
    return mcp_ret({"error": "'%s' cannot be counted: it is not a folder" % relative_url,
      "hint": "count_only works on a module or another folder. For the rows of one document's listbox use erp5_collect.",
      "relative_url": relative_url})
  try:
    total = int(counter(**count_kw)[0][0])
  except Exception as error:
    return mcp_ret({"error": "count failed: %s" % error,
      "hint": "Fall back to paging with limit/offset and summing 'count'.",
      "relative_url": relative_url})
  counted = {"total_count": total, "count_only": True,
             "relative_url": relative_url, "query": query or ""}
  if warning_list:
    counted["warning"] = " ".join(warning_list)
  return mcp_ret(counted)

COLLECT_ADVICE = ("Use erp5_collect(relative_url=..., filters={...}) instead: it"
  " runs the module's own list_method, so related keys resolve and the module's"
  " default parameters still apply, which is what the module shows in the UI."
  " erp5_inspect lists the columns it accepts under search_columns.")

try:
  raw = context.ERP5Document_getHateoas(
    mode="search", relative_url=relative_url, list_method=list_method,
    default_param_json=default_param_json, select_list=sl, sort_on=norm_sort_on(sort_on),
    limit=[off, lim], restricted=1)
except Exception as error:
  # A related key whose join needs a table this query never brought in fails as
  # "Unknown column '<table>.<column>' in 'on clause'". That names the SQL, not
  # the way out, so say what to do about it.
  message = str(error)
  failure = {"error": "search failed: %s" % message, "relative_url": relative_url}
  if "on clause" in message or "Unknown column" in message:
    failure["hint"] = ("this is a column the plain catalog cannot join on its"
      " own -- erp5_search runs the generic searchFolder. " + COLLECT_ADVICE)
  return mcp_ret(failure, ensure_ascii=False)
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
      "hint": "Check the id with erp5_discover, which lists every module, or drop"
        " relative_url to search the whole catalog. A portal type does not imply"
        " a module of the same name: invoices, for one, are documents of"
        " accounting_module.",
      "relative_url": relative_url}, ensure_ascii=False)
  return mcp_ret({"error": "'%s' exists and is a %s, but ERP5 rendered no view"
    " for it, so there is nothing to search inside." % (relative_url, probed),
    "hint": "Searching is scoped through a document's own view; a type without"
      " one cannot scope it. Drop relative_url and search the whole catalog with"
      " a portal_type criterion instead.",
    "relative_url": relative_url, "portal_type": probed}, ensure_ascii=False)
data = json.loads(raw) if isinstance(raw, str) else raw
contents = data.get("_embedded", {}).get("contents", [])

def browser_url(rel):
  if not rel:
    return ""
  portal = context.getPortalObject()
  req = portal.REQUEST
  u = (req.get("URL") or req.get("ACTUAL_URL") or "").split("?")[0]
  marker = "/portal_web_services/"
  base = u.split(marker)[0] if marker in u else portal.absolute_url()
  return base + "/#/" + rel

def extract_row(item):
  row = {}
  self_link = item.get("_links", {}).get("self", {}).get("href", "")
  rel = self_link[len("urn:jio:get:"):] if self_link.startswith("urn:jio:get:") else self_link
  row["relative_url"] = rel
  row["url"] = browser_url(rel)
  for key, val in item.items():
    if key.startswith("_") or key == "listbox_uid:list":
      continue
    if isinstance(val, dict) and "field_gadget_param" in val:
      row[key] = val["field_gadget_param"].get("default", "")
    else:
      row[key] = val
  return row

results = [extract_row(it) for it in contents]

# Scoping to a document ERP5 cannot render a view for is not refused: the
# search runs unscoped and answers with the whole portal, which reads as "these
# are the rows under that path". Seen on a Comment, whose type has no view of
# its own -- 50 rows came back, every one of them from somewhere else.
if relative_url and results:
  inside = relative_url + "/"
  escaped = True
  for row in results:
    rel = row.get("relative_url") or ""
    if rel == relative_url or rel.startswith(inside):
      escaped = False
      break
  if escaped:
    warning_list.append(
      "the scope to '%s' was not applied -- none of these rows is under it, so"
      " this is a portal-wide search. ERP5 scopes a search through the"
      " document's own view, and a document whose type has no view falls back"
      " to searching everything. Narrow it with a portal_type criterion"
      " instead." % relative_url)

has_more = len(results) >= lim
resp = {"count": len(results), "offset": off, "has_more": has_more,
        "next_offset": off + len(results) if has_more else None, "results": results}
if filters:
  resp["filters_applied"] = filters
if warning_list:
  resp["warning"] = " ".join(warning_list)

# A listbox column that this tool cannot resolve comes back empty rather than
# failing -- the caller then reads a plausible row set in which the very column
# they searched on is blank, and a criterion on it was silently not applied.
# Detect that and name the tool that can do it, so a caller does not have to
# recognise the symptom themselves.
def is_blank(value):
  return value is None or value == "" or value == [] or value == {}

def listbox_list_method(rel):
  # only consulted once something already looks wrong, so the extra traverse
  # never costs anything on the normal path
  try:
    raw2 = context.ERP5Document_getHateoas(mode="traverse", relative_url=rel,
                                           view="view", restricted=1)
    parsed = json.loads(raw2) if isinstance(raw2, str) else raw2
    listbox = parsed.get("_embedded", {}).get("_view", {}).get("listbox") or {}
    return listbox.get("list_method") or ""
  except Exception:
    return ""

if results and sl:
  requested = [str(c) for c in sl if str(c) not in ("relative_url", "url")]
  blank_column_list = [c for c in requested
                       if len([r for r in results if not is_blank(r.get(c))]) == 0]
  if blank_column_list:
    detail = ""
    method = listbox_list_method(relative_url) if relative_url else ""
    if method and method != "searchFolder":
      detail = (" '%s' declares list_method '%s', which this tool does not use."
                % (relative_url, method))
    filtered = [c for c in blank_column_list if c in filters]
    lead = ("the criterion on %s was probably NOT applied, and"
            % ", ".join(sorted(filtered))) if filtered else "note that"
    resp["hint"] = ("%s these requested columns came back empty for every row:"
      " %s.%s %s" % (lead, ", ".join(blank_column_list), detail, COLLECT_ADVICE))

# A single portal type lives in a single module, and there the module's own
# listbox knows more than the plain catalog does. Name that module, so the
# caller does not have to know which one holds the type.
portal_type_criterion = filters.get("portal_type")
if portal_type_criterion and not isinstance(portal_type_criterion, (list, tuple, dict)):
  try:
    module = context.getPortalObject().getDefaultModule(str(portal_type_criterion))
  except Exception:
    module = None
  if module is not None:
    advice = ("searching one portal type means searching one module:"
      " erp5_collect(relative_url=\"%s\", filters={...}) answers it the way the"
      " module itself does -- related keys resolved, its default parameters"
      " applied, columns as the UI shows them. Prefer it unless you need the"
      " plain catalog." % module.getRelativeUrl())
    resp["hint"] = ("%s %s" % (resp["hint"], advice)) if resp.get("hint") else advice
return mcp_ret(resp, ensure_ascii=False)
