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
md = min(int(max_depth) if max_depth not in (None, "") else 4, 10)
def call(mode, **kw):
  raw = context.ERP5Document_getHateoas(mode=mode, restricted=1, **kw)
  return json.loads(raw) if (isinstance(raw, str) and raw) else (raw or {})
def is_empty(v):
  return v is None or v == "" or v == [] or v == {}
def cval(fd):
  if not isinstance(fd, dict):
    return fd
  ftype = fd.get("type", "")
  default = fd.get("default", "")
  if "field_gadget_param" in fd:
    return fd["field_gadget_param"].get("default", "")
  if ftype in ("RelationStringField", "MultiRelationStringField"):
    val = default
    if isinstance(val, list):
      val = [v for v in val if v]
      return val[0] if len(val) == 1 else (val if val else "")
    return val
  return default
def cdoc(ev):
  res = {}
  skip = ("_links", "_embedded", "_actions", "form_id", "listbox", "dialog_id", "selection_name", "extra_param_json")
  for key, fd in ev.items():
    if key.startswith("_") or key in skip:
      continue
    if isinstance(fd, dict) and "list_method_template" in fd:
      continue
    if not isinstance(fd, dict) or fd.get("hidden"):
      continue
    v = cval(fd)
    if not is_empty(v):
      res[key] = v
  return res
def unq(v):
  for a, b in (("%3A", ":"), ("%2F", "/"), ("%2C", ","), ("%20", " "), ("+", " "), ("%25", "%")):
    v = v.replace(a, b)
  return str(v)
def parse_tpl(tpl):
  base = tpl.split("{")[0]
  qs = base.split("?", 1)[1] if "?" in base else ""
  p = {}
  for pair in qs.split("&"):
    if "=" in pair:
      k, v = pair.split("=", 1)
      p[str(k)] = unq(v)
  return p
def parse_doc(data, ru):
  links = data.get("_links", {})
  ev = data.get("_embedded", {}).get("_view", {})
  resolved = links.get("traversed_document", {}).get("name", ru)
  return {"relative_url": resolved, "title": data.get("title", ""),
    "portal_type": links.get("type", {}).get("name", ""),
    "fields": cdoc(ev), "children": [], "_listbox": ev.get("listbox")}
def child_urls(listbox):
  tpl = listbox.get("list_method_template", "")
  if not tpl:
    return []
  p = parse_tpl(tpl)
  cols = listbox.get("column_list", [])
  sf = [str(c[0]) for c in cols] if cols else ["title"]
  if "uid" not in sf:
    sf.append("uid")
  urls = []
  offset = 0
  total = 0
  while len(urls) < 500:
    d = call("search", relative_url=p.get("relative_url"), form_relative_url=p.get("form_relative_url"),
      list_method=p.get("list_method"), default_param_json=p.get("default_param_json"),
      extra_param_json=p.get("extra_param_json"), select_list=sf, limit=[offset, 50], query="")
    contents = d.get("_embedded", {}).get("contents", [])
    if total == 0:
      total = d.get("_embedded", {}).get("count", 0)
    if not contents:
      break
    for item in contents:
      h = item.get("_links", {}).get("self", {}).get("href", "")
      u = h[len("urn:jio:get:"):] if h.startswith("urn:jio:get:") else h
      if u:
        urls.append(str(u))
    offset += len(contents)
    if offset >= total or len(contents) < 50:
      break
  return urls
def expand(nodes, depth):
  if depth >= md:
    for n in nodes:
      n.pop("_listbox", None)
    return
  nxt = []
  for node in nodes:
    listbox = node.pop("_listbox", None)
    if not listbox:
      continue
    children = []
    for u in child_urls(listbox):
      try:
        cd = call("traverse", relative_url=str(u), view="view")
        children.append(parse_doc(cd, u))
      except Exception:
        continue
    node["children"] = children
    nxt.extend(children)
  expand(nxt, depth + 1)
data = call("traverse", relative_url=relative_url, view="view")
if not data:
  # call() turns the empty body ERP5 returns when no view was rendered into {},
  # which parse_doc then rendered as a document with no title, no type and no
  # children -- a tree that reads as "it exists and is empty" whatever the real
  # reason was. restrictedTraverse answers None for both "absent" and "not
  # allowed", so the first message claims no more than that.
  try:
    probed_target = context.getPortalObject().restrictedTraverse(str(relative_url), None)
  except Exception:
    probed_target = None
  if probed_target is None:
    return mcp_ret({"error": "nothing readable at '%s': ERP5 rendered no view"
      " for it and the path does not resolve, so it either does not exist or the"
      " current user may not see it." % relative_url,
      "hint": "Check the id with erp5_discover, which lists every module, or find"
        " the document itself with erp5_search. A portal type does not imply a"
        " module of the same name: invoices, for one, are documents of"
        " accounting_module.",
      "relative_url": relative_url}, ensure_ascii=False)
  try:
    probed = str(probed_target.getPortalType())
  except Exception:
    probed = "?"
  return mcp_ret({"error": "'%s' exists and is a %s, but ERP5 rendered no view"
    " for it, so there is no tree to walk from here." % (relative_url, probed),
    "hint": "The path is right, the document simply cannot be displayed on its"
      " own. Start from its parent instead, which usually lists it as a child.",
    "relative_url": relative_url, "portal_type": probed}, ensure_ascii=False)
node = parse_doc(data, relative_url)
expand([node], 1)
return mcp_ret(node, ensure_ascii=False)
