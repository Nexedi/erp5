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
portal = context.getPortalObject()
pc = portal.portal_components
try:
  try:
    output = pc.runLiveTest(test_list=test_list, run_only=run_only)
  except TypeError:
    output = pc.runLiveTest(test_list)
except Exception, e:
  return mcp_ret({"status": "error", "message": "runLiveTest failed: %s" % e})
output = output if isinstance(output, str) else str(output)
res = {"status": "completed", "test_list": test_list}
if run_only:
  res["run_only"] = run_only
summary = None
verdict = None
for line in output.split("\n"):
  ls = line.strip()
  if line.startswith("Ran "):
    summary = ls
  if ls in ("OK", "FAILED") or line.startswith("FAILED ("):
    verdict = ls
res["summary"] = summary
res["verdict"] = verdict
# A green run needs no transcript: only failures and full_output ask for one.
# This matters because every tool result is replayed in context for the rest
# of the session - an OK run must cost one line, not six kilobytes.
full = full_output if isinstance(full_output, bool) else (
  str(full_output).lower() not in ("0", "false", "no", ""))
if full:
  res["output"] = output[-12000:]
elif verdict != "OK":
  out_lines = output.split("\n")
  first = None
  for i, line in enumerate(out_lines):
    if line.startswith("FAIL:") or line.startswith("ERROR:"):
      first = i
      break
  res["failures"] = "\n".join(out_lines[first:])[-6000:] if first is not None else output[-2000:]
try:
  res["pending_activities"] = portal.portal_activities.countMessage()
except Exception:
  pass
return mcp_ret(res, ensure_ascii=False)
