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
import base64
from urllib import quote
portal = context.getPortalObject()
req = portal.REQUEST
document = portal.restrictedTraverse(relative_url, None)
if document is None:
  return mcp_ret({"error": "not found: %s" % relative_url})

inline_flag = inline if isinstance(inline, bool) else (str(inline).lower() in ("1", "true", "yes"))
deferred_forced = False
def _mcp_native(v):
  # REQUEST.form values of a real HTTP submit are native strings: utf-8 encoded
  # bytes on Python 2, text on Python 3. What arrives here comes from JSON, so
  # a number stays a number and text stays unicode -- and a Formulator
  # validator handed an int calls string methods on it, which is where
  # "'int' object has no attribute 'decode'" comes from (normalizeFullWidthNumber
  # in IntegerValidator). params={"count": 20} died on that while
  # params={"count": "20"} worked, which is not a distinction a caller should
  # have to know. Unicode is encoded for the same reason as in erp5_write: it
  # otherwise leaks into stored properties. bool is tested before int because it
  # is a subclass of it -- str(False) would be "False", which a checkbox
  # validator reads as true.
  if isinstance(v, (list, tuple)):
    return [_mcp_native(x) for x in v]
  if isinstance(v, dict):
    return dict([(_mcp_native(k2), _mcp_native(v2)) for k2, v2 in v.items()])
  if isinstance(v, str):
    return v
  if hasattr(v, "encode"):  # Python 2 unicode
    return v.encode("utf-8")
  if v is None:
    return ""
  if isinstance(v, bool):
    return "1" if v else "0"
  if isinstance(v, (int, float)):
    return str(v)
  return v

def assert_output_action():
  # A read-only connector reaches reports through this tool, so it must not
  # double as a way to drive an arbitrary dialog action: _actions.put.action
  # exists for create_related_payment exactly as it does for a report, and
  # nothing here told them apart -- action_type only decorated the description.
  # ERP5 publishes the classification already: an action offered as output is
  # listed under the document's own _links. Answers None when the requested
  # action is one of those, otherwise the payload explaining the refusal.
  #
  # Rendering the plain view costs a second getHateoas, and that one is not
  # free of consequences: run before the action's own view, it changes what the
  # dialog's hidden selection_name field resolves to (the report then points at
  # the wrong selection). Hence both precautions -- call this only once the
  # action view has been rendered, and hand the REQUEST back as found.
  if str(action_name) == "download":
    return None
  saved_form = dict(req.form)
  saved_other = dict(req.other)
  try:
    try:
      view_links = json.loads(context.ERP5Document_getHateoas(
        mode="traverse", relative_url=str(relative_url), view="view",
        restricted=1)).get("_links", {})
    except Exception:
      view_links = {}
  finally:
    req.form.clear()
    req.form.update(saved_form)
    for added_key in [k for k in req.other.keys() if k not in saved_other]:
      try:
        del req.other[added_key]
      except Exception:
        pass
    for key, value in saved_other.items():
      if req.other.get(key) is not value:
        req.other[key] = value
  allowed_action_list = []
  for link_key in ("action_object_jio_report", "action_object_jio_print",
                   "action_object_jio_exchange"):
    entry = view_links.get(link_key, [])
    if isinstance(entry, dict):
      entry = [entry]
    for candidate in entry:
      name = candidate.get("name", "") if isinstance(candidate, dict) else ""
      if name:
        allowed_action_list.append(name)
  if str(action_name) in allowed_action_list:
    return None
  allowed_action_list.sort()
  return {
    "error": "'%s' is not a report, a print or an exchange of %s"
      % (action_name, relative_url),
    "hint": "This tool only renders what the document itself offers as"
      " output, so that a connector exposing only read-only tools cannot"
      " drive a writing dialog through it. Anything else goes through"
      " erp5_dialog, which is not a read-only tool.",
    "available": allowed_action_list,
    "relative_url": relative_url}

def wbase():
  u = (req.get("URL") or req.get("ACTUAL_URL") or "").split("?")[0]
  m = "/portal_web_services/"
  return u.split(m)[0] if m in u else portal.absolute_url()

stored = None
try:
  stored = document.getData()
except Exception:
  stored = None

# 1) Original stored file -> resource_link to Base_download.
if stored and str(action_name) == "download" and not inline_flag:
  try: ctype = document.getContentType() or "application/octet-stream"
  except Exception: ctype = "application/octet-stream"
  try: fname = document.getFilename() or relative_url.replace("/", "_")
  except Exception: fname = relative_url.replace("/", "_")
  return [{"type": "resource_link", "uri": wbase() + "/" + relative_url + "/Base_download",
    "name": fname, "title": fname, "mimeType": ctype, "size": len(stored),
    "description": "Original file. HTTP GET (same Basic auth as the MCP endpoint) - no base64. Pass inline=true for base64."}]

# 2) Generated print/export/report -> resource_link to a Base_callDialogMethod GET URL.
if not inline_flag and str(action_name) != "download":
  ev = json.loads(context.ERP5Document_getHateoas(mode="traverse", relative_url=str(relative_url), view=str(action_name), restricted=1)).get("_embedded", {}).get("_view", {})
  dm = ev.get("_actions", {}).get("put", {}).get("action", "")
  if not dm:
    return mcp_ret({"error": "no download endpoint for '%s' (check exchanges/prints/reports)" % action_name})
  refusal = assert_output_action()
  if refusal is not None:
    return mcp_ret(refusal)
  def hid(n):
    fd = ev.get(n, {})
    return fd.get("default", "") if isinstance(fd, dict) else ""
  form_id = hid("form_id")
  if not form_id:
    try:
      vfd = json.loads(context.ERP5Document_getHateoas(mode="traverse", relative_url=str(relative_url), view="view", restricted=1)).get("_embedded", {}).get("_view", {}).get("form_id")
      form_id = vfd.get("default", "") if isinstance(vfd, dict) else ""
    except Exception:
      form_id = ""
  sel = hid("selection_name") or (form_id + "_selection" if form_id else "")
  CORE = ("dialog_method","dialog_id","form_id","dialog_category","extra_param_json","update_method","selection_name")
  qd = [("dialog_method", dm), ("dialog_id", hid("dialog_id")), ("form_id", form_id),
        ("dialog_category", hid("dialog_category")), ("extra_param_json", hid("extra_param_json") or "{}"),
        ("selection_name", sel)]
  um = hid("update_method")
  if um: qd.append(("update_method", um))
  # resolve caller overrides: accept "format", "your_format", "field_your_format", "at_date" ...
  overrides = {}
  if params:
    pp = json.loads(params) if isinstance(params, str) else params
    alias = {}
    for key, fd in ev.items():
      if key.startswith("_") or not isinstance(fd, dict): continue
      alias[key] = key
      fk = fd.get("key", key)
      alias[fk] = key
      if key.startswith("your_"): alias[key[5:]] = key
    for k, v in pp.items():
      fid = alias.get(k) or alias.get("your_" + str(k)) or alias.get("field_your_" + str(k)) or alias.get("field_" + str(k))
      if fid: overrides[fid] = v
  MULTI = ("MultiListField","MultiCheckBoxField","ParallelListField","LinesField")
  def emit(fd, fkey, value):
    t = fd.get("type", "")
    if t == "DateTimeField":
      y = m = d = ""
      if value and hasattr(value, "replace"):
        s = value.replace("-", "/").split(" ")[0].split("T")[0]
        pz = s.split("/")
        if len(pz) == 3:
          if len(pz[0]) == 4: y, m, d = pz[0], pz[1], pz[2]
          else: d, m, y = pz[0], pz[1], pz[2]
      for kk, vv in ((fd.get("subfield_year_key"), y), (fd.get("subfield_month_key"), m), (fd.get("subfield_day_key"), d)):
        if kk: qd.append((kk, vv))
      return
    if t in MULTI:
      qd.append(("default_%s" % fkey, ""))
      vals = value if isinstance(value, (list, tuple)) else ([value] if value not in (None, "") else [])
      for it in vals: qd.append(("%s:list" % fkey, it))
      return
    if t == "CheckBoxField":
      qd.append(("default_%s:int" % fkey, "0"))
      qd.append((fkey, 1 if value in (1, "1", True, "true") else 0))
      return
    if t in ("ListField", "RadioField"):
      qd.append(("default_%s" % fkey, ""))
      qd.append((fkey, value if not isinstance(value, (list, tuple)) else (value[0] if value else "")))
      return
    qd.append((fkey, value if value is not None else ""))
  for key, fd in ev.items():
    if key.startswith("_") or not isinstance(fd, dict): continue
    fkey = fd.get("key", key)
    if fkey in CORE or not fkey.startswith("field_"): continue
    value = overrides.get(key, fd.get("default", ""))
    # 'ods' as an explicit format double-converts when portal_skin already renders ODS -> treat as native
    if key == "your_format" and str(value).lower() in ("ods", "sxc"):
      value = ""
    if key == "your_deferred_style" and value not in (0, "0", False):
      # Deferred means the report is not rendered at all: it is queued as an
      # activity and mailed, and with the stored-as-document preference on it
      # also creates and shares a Document. That is a write, and this is the
      # read-only route to a report -- so it runs synchronously and comes back
      # as the file that was asked for. The caller is told, below.
      value = 0
      deferred_forced = True
    emit(fd, fkey, value)
  qs = "&".join("%s=%s" % (quote(str(k), safe=":"), quote(str(x), safe="")) for k, x in qd)
  deferred_note = (" Deferred style was forced off: a deferred report is not"
    " rendered but queued and mailed, which a read-only tool must not do."
    ) if deferred_forced else ""
  fname = "%s_%s" % (relative_url.replace("/", "_"), action_name)
  return [{"type": "resource_link", "uri": wbase() + "/" + relative_url + "/Base_callDialogMethod?" + qs,
    "name": fname, "title": fname,
    "description": "Generated %s '%s' (dialog method %s). HTTP GET (same Basic auth, follow redirects) streams the file - no base64. For a specific file format pass params={\"format\":\"pdf\"} (or ods/xlsx/csv). Pass inline=true for base64." % (action_type or "output", action_name, dm) + deferred_note}]

# 3) inline=true -> render via the dialog method and return base64.
raw = context.ERP5Document_getHateoas(mode="traverse", relative_url=str(relative_url), view=str(action_name), restricted=1)
ev = (json.loads(raw) if (isinstance(raw, str) and raw) else {}).get("_embedded", {}).get("_view", {})
dm = ev.get("_actions", {}).get("put", {}).get("action", "")
if not dm:
  return mcp_ret({"error": "no download endpoint for '%s'" % action_name})
refusal = assert_output_action()
if refusal is not None:
  return mcp_ret(refusal)
def hidden(n):
  fd = ev.get(n, {})
  return fd.get("default", "") if isinstance(fd, dict) else ""
form_id = hidden("form_id"); dialog_id = hidden("dialog_id") or form_id
dialog_category = hidden("dialog_category"); extra = hidden("extra_param_json") or "{}"
update_method = hidden("update_method") or None
fdata = {}
for key, fd in ev.items():
  if key.startswith("_") or not isinstance(fd, dict): continue
  fkey = fd.get("key", key)
  dv = fd.get("default", "")
  fdata[fkey] = dv if dv is not None else ""
  if fkey.startswith("field_"): fdata["default_%s:int" % fkey] = "0"
if params:
  pp = json.loads(params) if isinstance(params, str) else params
  for k, v in pp.items():
    fdata[k if k.startswith("field_") else ("field_your_%s" % k)] = v
if "your_deferred_style" in ev and fdata.get("field_your_deferred_style") not in (0, "0", False):
  # Same reason as in the link branch above, and it matters more here: this
  # one really does run the report, so a deferred submit would return nothing
  # to the caller and mail the result instead.
  fdata["field_your_deferred_style"] = 0
  deferred_forced = True
mm = {}
# _mcp_native runs first so that the marshalling below still sees the ':int'
# and ':list' suffixed keys as the strings ZPublisher would have parsed.
for k, v in _mcp_native(fdata).items():
  if k.endswith(":int"):
    try: mm[k[:-4]] = int(v)
    except Exception: mm[k[:-4]] = 0
  elif k.endswith(":list"):
    mm[k[:-5]] = v if isinstance(v, list) else ([v] if v not in (None, "") else [])
  else: mm[k] = v
saved = dict(req.form); body = None; ctype = None; cdisp = None
try:
  for k, v in mm.items(): req.form[k] = v
  body = document.Base_callDialogMethod(dialog_method=dm, dialog_id=dialog_id, form_id=form_id,
    dialog_category=dialog_category, update_method=update_method, extra_param_json=extra)
  try:
    ctype = req.RESPONSE.getHeader("Content-Type"); cdisp = req.RESPONSE.getHeader("Content-Disposition")
  except Exception: pass
finally:
  req.form.clear(); req.form.update(saved)
if not body:
  return mcp_ret({"error": "download produced no content", "dialog_method": dm})
if isinstance(body, unicode): body = body.encode("utf-8")
elif not isinstance(body, str): body = str(body)
filename = None
if cdisp and "filename=" in cdisp: filename = cdisp.split("filename=")[-1].strip().strip('"')
if not filename: filename = relative_url.replace("/", "_")
res = {"status": "success", "relative_url": relative_url, "action": action_name, "filename": filename,
  "content_type": (ctype or "application/octet-stream").split(";")[0].strip(), "size": len(body)}
note_list = []
if deferred_forced:
  note_list.append("deferred style was forced off: a deferred report is not"
    " rendered but queued and mailed, which a read-only tool must not do")
if len(body) > 4000000:
  note_list.append("file too large to return inline (%d bytes)" % len(body))
else:
  res["content_base64"] = base64.b64encode(body)
if note_list:
  res["note"] = ". ".join(note_list)
return mcp_ret(res, ensure_ascii=False)
