def mcp_ret(o, *a, **k):
  return _json.dumps(_mcp_unicode(o), ensure_ascii=False), o
def _mcp_unicode(value):
  # json.dumps(ensure_ascii=False) joins its output chunks on Python 2, so a
  # payload mixing unicode with utf-8 str makes that join decode the bytes as
  # ascii and die on the first umlaut: "'ascii' codec can't decode byte 0xc3".
  # A translated status message is exactly such a native str, while the
  # relative_url the caller sent is unicode -- so on a localised instance the
  # outcome of the action would crash the tool reporting it. Decode
  # everything once, up front.
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
def _mcp_text(value):
  if value is None:
    return ""
  if isinstance(value, (list, tuple)):
    return ". ".join([_mcp_text(x) for x in value if x not in (None, "")])
  try:
    return str(value)
  except Exception:
    pass
  try:
    return repr(value)
  except Exception:
    return ""
def _mcp_exception_message(error):
  # ValidationFailed carries the translatable Message -- or a list of them --
  # that the UI prints in its status bar; other exceptions only have str().
  msg = getattr(error, "msg", None)
  if msg is not None and msg != "":
    text = _mcp_text(msg)
    if text:
      return text
  text = _mcp_text(error)
  if text:
    return text
  try:
    return repr(error)
  except Exception:
    return "action refused without a message"
def _mcp_unquote(text):
  # There is no urllib in restricted python and the status message travels
  # url-quoted utf-8 inside the redirect location.
  text = text.replace("+", " ")
  chunks = text.split("%")
  byte_list = [ord(c) for c in chunks[0]]
  for chunk in chunks[1:]:
    rest = chunk
    try:
      byte_list.append(int(chunk[:2], 16))
      rest = chunk[2:]
    except Exception:
      byte_list.append(ord("%"))
    for c in rest:
      byte_list.append(ord(c))
  try:
    return bytes(bytearray(byte_list)).decode("utf-8")
  except Exception:
    return "".join([chr(x) for x in byte_list])
def _mcp_location_message(location):
  # Classic skins report the outcome with a 302 to a portal_status_message URL.
  if not location or "portal_status_message=" not in location:
    return ""
  return _mcp_unquote(location.split("portal_status_message=", 1)[1].split("&", 1)[0])
def _mcp_result_message(result):
  # The renderjs skin does not redirect: it answers with a body of
  # {"portal_status_message": "<the reason>"} -- on a refusal that body is the
  # only place the reason appears, so it has to be read back out of the
  # returned string.
  if not result or "portal_status_message" not in result:
    return ""
  try:
    payload = _json.loads(result)
  except Exception:
    return ""
  if isinstance(payload, dict):
    return _mcp_text(payload.get("portal_status_message"))
  return ""
_MCP_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
  "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
def parse_date(val):
  # Same parser as erp5_write: a DateTimeField's HATEOAS default is rendered
  # RFC-822 style, e.g. "Fri, 28 Aug 2026 00:00:00 +0000", so a leading
  # weekday token is dropped and a month name accepted -- otherwise a
  # replayed default comes back None and clears the field.
  if not val or not hasattr(val, "split"):
    return None
  s = val.strip().replace("T", " ")
  parts = [p for p in s.split(" ") if p]
  if not parts:
    return None
  if parts[0].endswith(",") and not parts[0][:-1].isdigit():
    parts = parts[1:]
  if not parts:
    return None
  datepart = parts[0]
  timepart = parts[1] if len(parts) > 1 else ""
  sep = "-" if "-" in datepart else ("/" if "/" in datepart else None)
  if sep is None:
    # "28 Aug 2026 00:00:00 +0000": day, month name and year are separate tokens.
    if len(parts) >= 3 and datepart.isdigit():
      mon = _MCP_MONTHS.get(parts[1][:3].lower())
      if mon is not None and parts[2].isdigit():
        try:
          y, m, d = int(parts[2]), mon, int(datepart)
        except Exception:
          return None
        h = mi = 0
        tp_src = parts[3] if len(parts) > 3 else ""
        if tp_src and ":" in tp_src:
          tp = tp_src.split(":")
          try:
            h = int(tp[0])
            mi = int(tp[1]) if len(tp) > 1 else 0
          except Exception:
            h = mi = 0
        return (y, m, d, h, mi)
    return None
  dp = datepart.split(sep)
  if len(dp) != 3:
    return None
  try:
    if len(dp[0]) == 4:
      y, m, d = int(dp[0]), int(dp[1]), int(dp[2])
    else:
      d, m, y = int(dp[0]), int(dp[1]), int(dp[2])
    h = mi = 0
    if timepart and ":" in timepart:
      tp = timepart.split(":")
      h = int(tp[0])
      mi = int(tp[1]) if len(tp) > 1 else 0
    return (y, m, d, h, mi)
  except Exception:
    return None
def _submit(relative_url, action_name, param_dict=None, comment=None):
  import json
  portal = context.getPortalObject()
  document = portal.restrictedTraverse(relative_url, None)
  if document is None:
    return {"error": "not found: %s" % relative_url}
  raw = context.ERP5Document_getHateoas(mode="traverse", relative_url=str(relative_url), view=str(action_name), restricted=1)
  data = json.loads(raw) if (isinstance(raw, str) and raw) else {}
  ev = data.get("_embedded", {}).get("_view", {})
  dialog_method = ev.get("_actions", {}).get("put", {}).get("action", "")
  if not dialog_method:
    return {"error": "no dialog action for '%s' (not a dialog action)" % action_name}
  def hidden(n):
    fd = ev.get(n, {})
    return fd.get("default", "") if isinstance(fd, dict) else ""
  form_id = hidden("form_id")
  dialog_id = hidden("dialog_id") or form_id
  dialog_category = hidden("dialog_category")
  extra_param_json = hidden("extra_param_json") or "{}"
  update_method = hidden("update_method") or None
  def render_float(fd, value):
    # Mirror Formulator's FloatWidget.format_value. The HATEOAS default of a
    # FloatField is the raw python float, but FloatValidator only understands
    # what the widget rendered, so the number has to be formatted back into the
    # field's input_style before it is submitted. Handing the validator a float
    # instead crashes normalizeFullWidthNumber ('float' object has no attribute
    # 'decode'), and handing it an unformatted "1234.5" makes a '-1.234,5'
    # styled field read the '.' as a thousands separator and store 12345.0 --
    # the value grows by a factor of ten on every submit.
    if value is None or value == "":
      return ""
    try:
      number = float(value)
    except (TypeError, ValueError):
      return value
    input_style = fd.get("input_style") or "-1234.5"
    precision = fd.get("precision")
    if isinstance(precision, str) and precision.strip("-").isdigit():
      precision = int(precision)
    percent = "%" in input_style
    if percent:
      number = number * 100
    if precision not in (None, "") and abs(number) * 10 ** precision < 2 ** 53:
      text = ("%%0.%sf" % precision) % number
    else:
      text = str(number)
    if "e" in text or "E" in text:
      # scientific notation, the widget returns it as is
      return text
    fpart = ""
    if precision != 0:
      if "." not in text:  # inf / nan
        return text
      text, fpart = text.split(".")
    decimal_separator = ""
    decimal_point = "."
    if input_style == "-1 234.5":
      decimal_separator = " "
    elif input_style == "-1 234,5":
      decimal_separator = " "
      decimal_point = ","
    elif input_style == "-1.234,5":
      decimal_separator = "."
      decimal_point = ","
    elif input_style == "-1,234.5":
      decimal_separator = ","
    if decimal_separator:
      if text.startswith("-"):
        sign = "-"
        text = text[1:]
      else:
        sign = ""
      i = len(text) % 3 or 3
      integer = text[:i]
      while i < len(text):
        integer += decimal_separator + text[i:i + 3]
        i += 3
      text = sign + integer
    if precision != 0:
      text += decimal_point
      if precision:
        text += fpart[:precision].ljust(precision, "0")
      else:
        text += fpart
    if percent:
      text += "%"
    return text
  # Formulator validates a DateTimeField from its subfield_<key>_year /
  # _month / _day entries and never looks at the field key itself
  # (DateTimeValidator.validate -> Field.validate_sub_field). Replaying only
  # "field_your_start_date" left those absent, and validate_all catches the
  # KeyError it raises, logs it and moves on (ERP5Form/Form.py) -- so the
  # field was dropped from the validated result without a word and the date
  # the caller passed never reached the dialog method.
  # The caller's params are resolved into overrides up front, so a date passed
  # in is expanded through the same path as a replayed default; applying them
  # after the loop would put the plain key back and be ignored again.
  if isinstance(param_dict, str):
    param_dict = json.loads(param_dict)
  override = {}
  if param_dict:
    for k, v in param_dict.items():
      override[k if k.startswith("field_") else ("field_your_%s" % k)] = v
  if comment is not None:
    override["field_your_comment"] = comment
  fdata = {}
  date_field_key = {}
  for key, fd in ev.items():
    if key.startswith("_") or not isinstance(fd, dict):
      continue
    fkey = fd.get("key", key)
    ftype = fd.get("type", "")
    d = override.get(fkey, fd.get("default", ""))
    if ftype == "DateTimeField":
      date_field_key[fkey] = 1
      parsed = parse_date(d)
      sub_key_list = [fd.get("subfield_year_key", ""),
        fd.get("subfield_month_key", ""), fd.get("subfield_day_key", ""),
        fd.get("subfield_hour_key", ""), fd.get("subfield_minute_key", "")]
      for i in range(len(sub_key_list)):
        sub_key = sub_key_list[i]
        if not sub_key:
          continue
        if parsed is None:
          # What an empty date input submits: the validator reads all-empty
          # subfields as "no date given" and returns None.
          fdata[sub_key] = ""
        elif i == 0:
          fdata[sub_key] = str(parsed[i])
        else:
          fdata[sub_key] = str(parsed[i]).zfill(2)
      continue
    if ftype == "FloatField":
      d = render_float(fd, d)
    elif ftype == "IntegerField":
      d = "" if d is None or d == "" else str(d)
    fdata[fkey] = d if d is not None else ""
    if fkey.startswith("field_") and ftype in ("CheckBoxField", "ListField", "ParallelListField", "MultiListField", "RadioField"):
      fdata["default_%s:int" % fkey] = "0"
  for k, v in override.items():
    # A param naming no field of the form is still submitted, since some
    # dialog methods read the REQUEST directly -- but a date has already been
    # expanded into its subfields above and must not get its own key back.
    if k not in date_field_key:
      fdata[k] = v
  mm = {}
  for k, v in fdata.items():
    if k.endswith(":int"):
      try:
        mm[k[:-4]] = int(v)
      except Exception:
        mm[k[:-4]] = 0
    elif k.endswith(":list"):
      mm[k[:-5]] = v if isinstance(v, list) else ([v] if v not in (None, "") else [])
    else:
      mm[k] = v
  def _mcp_native(v):
    # REQUEST.form values of a real HTTP submit are native strings: utf-8
    # encoded bytes on Python 2, text on Python 3. JSON decoding always yields
    # text, so on Python 2 it must be encoded -- else the unicode leaks into
    # the stored property and unrestrictedTraverse iterates over the
    # characters of such a path. On Python 3 text is already native and must
    # be left untouched.
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
  req = portal.REQUEST
  saved = dict(req.form)
  saved_status = req.RESPONSE.getStatus()
  info = {"status_code": None, "saved_status": saved_status, "field_errors": None,
    "x_location": None, "location": None, "portal_status_message": None,
    "dialog_method": dialog_method, "result": None, "exception": None, "exception_detail": None}
  try:
    for k, v in mm.items():
      req.form[_mcp_native(k)] = _mcp_native(v)
    try:
      info["result"] = str(document.Base_callDialogMethod(dialog_method=dialog_method, dialog_id=dialog_id,
        form_id=form_id, dialog_category=dialog_category, update_method=update_method, extra_param_json=extra_param_json))
    except Exception as error:
      # An action refused by a guard or a constraint reaches us as an exception
      # (ValidationFailed, WorkflowException, Unauthorized...). Letting it
      # escape turns the whole call into a bare JSON-RPC internal error and
      # loses the one thing the caller needs: the reason.
      info["exception"] = _mcp_exception_message(error)
      try:
        info["exception_detail"] = repr(error)[:500]
      except Exception:
        pass
    info["status_code"] = req.RESPONSE.getStatus()
    info["field_errors"] = req.get("field_errors")
    # Base_redirect hands the outcome to keep_items, which lands in REQUEST.form.
    for getter in (req.form.get, req.get):
      try:
        candidate = getter("portal_status_message")
      except Exception:
        candidate = None
      if candidate:
        info["portal_status_message"] = _mcp_text(candidate)
        break
    try:
      info["x_location"] = req.RESPONSE.getHeader("X-Location")
    except Exception:
      pass
    try:
      info["location"] = req.RESPONSE.getHeader("Location")
    except Exception:
      pass
  finally:
    req.form.clear()
    req.form.update(saved)
    try:
      req.other.pop("field_errors", None)
    except Exception:
      pass
    try:
      # The dialog leaves its own verdict on the shared RESPONSE: a 403 for a
      # refused action, or a 302 to a portal_status_message URL. Left there,
      # that becomes the MCP reply itself -- the client cannot read it, the
      # call surfaces as a bare internal error and the message is lost. Put
      # the response back the way we found it.
      req.RESPONSE.setStatus(saved_status)
      try:
        req.RESPONSE.headers.pop("location", None)
      except Exception:
        req.RESPONSE.setHeader("Location", "")
    except Exception:
      pass
  return info

import json as _json
info = _submit(relative_url, action_name, param_dict=params)
if "error" in info:
  return mcp_ret(info)
status = info.get("status_code")
saved_status = info.get("saved_status")
message = (info.get("portal_status_message")
  or _mcp_result_message(info.get("result"))
  or _mcp_location_message(info.get("location") or info.get("x_location") or ""))
exception_message = info.get("exception")
fe = {}
if info.get("field_errors"):
  try:
    for k, v in info["field_errors"].items():
      fe[k] = str(getattr(v, "error_text", None) or v)
  except Exception:
    fe = {"raw": str(info["field_errors"])}
failed = bool(exception_message) or bool(fe)
method_refused = False
try:
  # The RESPONSE is shared mutable state and can already carry a 4xx from
  # something else, so only a status this submit changed is a signal.
  if status and int(status) >= 400 and status != saved_status:
    # 405 is never a verdict on the action. ERP5Document_getHateoas sets it
    # when REQUEST.other["method"] is not GET for a traverse render, and an
    # MCP call arrives as a POST -- so any form rendered inside this submit
    # leaves one behind, and reporting failure on it labelled submits that had
    # really run as failures. What the action itself says is field_errors, the
    # caught exception or the status message. Every other 4xx still counts: a
    # refusal by a guard arrives as a 403 and carries its reason.
    if int(status) == 405:
      method_refused = True
    else:
      failed = True
except Exception:
  pass
if failed:
  # The numeric HTTP status goes in "status_code": the output schema types
  # "status" as a plain string, so a code there fails output validation and
  # the whole call comes back as an internal error instead of this payload.
  res = {"error": exception_message or message or "Dialog action failed",
    "action": action_name, "status_code": status, "relative_url": relative_url,
    "dialog_method": info.get("dialog_method")}
  if fe:
    res["field_errors"] = fe
  if message and message != res["error"]:
    res["message"] = message
  if info.get("exception_detail"):
    res["exception"] = info["exception_detail"]
  return mcp_ret(res)
res = {"status": "success", "relative_url": relative_url, "action": action_name, "dialog_method": info.get("dialog_method")}
loc = info.get("x_location") or info.get("location") or ""
if "urn:jio:get:" in loc:
  res["new_document"] = loc.split("urn:jio:get:")[-1]
if method_refused:
  # Not swallowed: a render inside this call was refused even though the action
  # reported nothing, and the caller should still see that it happened. It goes
  # into the existing message rather than a new key, which the output schema
  # would reject.
  note = ("a form rendered inside this call refused the request method (405);"
    " the action itself reported no error")
  message = (message + " -- " + note) if message else note
if message:
  # A dialog reports its outcome in the status message even when it succeeds
  # ("Payment created."), so this is information, not a verdict.
  res["message"] = message
return mcp_ret(res, ensure_ascii=False)
