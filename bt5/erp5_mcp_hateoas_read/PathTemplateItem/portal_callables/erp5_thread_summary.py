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
mp = min(int(max_posts) if max_posts not in (None, "") else 500, 500)
def call(mode, **kw):
  raw = context.ERP5Document_getHateoas(mode=mode, restricted=1, **kw)
  return json.loads(raw) if (isinstance(raw, str) and raw) else {}
def exrow(item):
  r = {}
  h = item.get("_links", {}).get("self", {}).get("href", "")
  r["relative_url"] = h[len("urn:jio:get:"):] if h.startswith("urn:jio:get:") else h
  for k, v in item.items():
    if k.startswith("_") or k == "listbox_uid:list":
      continue
    if isinstance(v, dict) and "field_gadget_param" in v:
      r[k] = v["field_gadget_param"].get("default", "")
    else:
      r[k] = v
  return r
d = call("search", query=str('reference:"%s" AND portal_type:"Discussion Thread"' % reference),
  select_list=["title", "reference", "uid"], limit=[0, 2])
matches = [i for i in d.get("_embedded", {}).get("contents", []) if i.get("reference") == reference]
if not matches:
  return mcp_ret({"error": "No Discussion Thread with reference '%s'" % reference})
h = matches[0].get("_links", {}).get("self", {}).get("href", "")
rel = h[len("urn:jio:get:"):] if h.startswith("urn:jio:get:") else h
doc = call("traverse", relative_url=str(rel), view="view")
ev = doc.get("_embedded", {}).get("_view", {})
listbox = ev.get("listbox")
meta = {"relative_url": rel, "reference": reference, "title": doc.get("_links", {}).get("traversed_document", {}).get("title", "")}
if not listbox:
  return mcp_ret({"error": "No listbox in '%s'" % rel, "thread": meta})
def unq(v):
  for a, b in (("%3A", ":"), ("%2F", "/"), ("%2C", ","), ("%20", " "), ("+", " "), ("%25", "%")):
    v = v.replace(a, b)
  return str(v)
tpl = listbox.get("list_method_template", "")
base = tpl.split("{")[0]
qs = base.split("?", 1)[1] if "?" in base else ""
p = {}
for pair in qs.split("&"):
  if "=" in pair:
    k, v = pair.split("=", 1)
    p[str(k)] = unq(v)
posts = []
offset = 0
total = 0
while len(posts) < mp:
  sd = call("search", relative_url=p.get("relative_url"), form_relative_url=p.get("form_relative_url"),
    list_method=p.get("list_method"), default_param_json=p.get("default_param_json"), extra_param_json=p.get("extra_param_json"),
    select_list=["source_title", "creation_date", "text_content", "uid"], limit=[offset, 50], query="",
    sort_on='["creation_date","ascending"]')
  c = sd.get("_embedded", {}).get("contents", [])
  if total == 0:
    total = sd.get("_embedded", {}).get("count", 0)
  if not c:
    break
  for item in c:
    r = exrow(item)
    posts.append({"index": len(posts) + 1, "author": r.get("source_title", "Unknown"),
      "date": r.get("creation_date", ""), "content": r.get("text_content", ""), "relative_url": r.get("relative_url", "")})
  offset += len(c)
  if offset >= total or len(c) < 50:
    break
meta["total_posts"] = total or len(posts)
return mcp_ret({"thread": meta, "posts": posts[:mp]}, ensure_ascii=False)
