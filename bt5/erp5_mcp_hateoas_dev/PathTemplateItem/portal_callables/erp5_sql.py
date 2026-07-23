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
import re as _re
from erp5.component.module.MCPDevHelpers import runSQL
portal = context.getPortalObject()

query = str(query or "").strip()
if not query:
  return mcp_ret({"error": "query is required"})
# Writes must be opted into, so a stray destructive call cannot happen by
# accident; SELECT/SHOW/DESCRIBE/EXPLAIN run freely.
statement = query.split(None, 1)[0].lower().lstrip("(")
readonly = statement in ("select", "show", "describe", "desc", "explain",
                         "analyze", "checksum", "table")
allow_write = allow_write if isinstance(allow_write, bool) else (
  str(allow_write).lower() in ("1", "true", "yes"))
if not readonly and not allow_write:
  return mcp_ret({"error": "statement is not read-only; pass allow_write=true",
                  "statement": statement})

try:
  max_rows = int(max_rows)
except Exception:
  max_rows = 50
max_rows = max(1, min(max_rows, 500))

# ZMySQLDA appends " LIMIT <max_rows>" to every SELECT statement that is
# handed a max_rows. A user LIMIT at the end of the query therefore produced
# the confusing "1064 ... near 'LIMIT 51'" (session issue B8). Detect a
# trailing LIMIT -- plain, OFFSET or "offset, count" form -- and let it
# govern: no extra LIMIT is appended and the Python-side cap applies instead.
if _re.search(r"\blimit\s+\d+(\s*,\s*\d+|\s+offset\s+\d+)?\s*;?\s*$", query,
              _re.IGNORECASE):
  query_max_rows = 0
  user_limit = True
else:
  query_max_rows = max_rows + 1
  user_limit = False

try:
  columns, rows, affected = runSQL(portal, connection_id, query, query_max_rows)
except Exception, e:
  return mcp_ret({"error": "query failed: %s" % e, "connection_id": str(connection_id)})

truncated = (len(rows) > max_rows) if not user_limit else False
rows = rows[:max_rows]

import datetime as _datetime
try:
  from decimal import Decimal as _Decimal
except Exception:
  _Decimal = None

def _cell(value):
  if value is None:
    return None
  if isinstance(value, bool):  # before int: bool is an int subclass
    return value
  if isinstance(value, (int, long, float)):
    return value
  if isinstance(value, (str, unicode)):
    text = value.decode("utf-8", "replace") if isinstance(value, str) else value
    return text[:200]
  if isinstance(value, (_datetime.datetime, _datetime.date, _datetime.time)):
    # DateTime columns are not JSON-serializable; hand back ISO strings
    # instead of raising (session issue B8).
    return value.isoformat()
  iso = getattr(value, "ISO", None)
  if iso is not None:
    # Zope DateTime cell (e.g. catalog modification_date)
    return str(iso())
  if _Decimal is not None and isinstance(value, _Decimal):
    return str(value)
  # last resort: never let one cell kill the whole json payload
  return str(value)[:200]

data = [[_cell(v) for v in row] for row in rows]

res = {"connection_id": str(connection_id),
       "columns": columns,
       "row_count": len(data),
       "truncated": truncated}
if not readonly and affected is not None:
  res["affected"] = affected
fmt = str(format or "rows")
if fmt == "count":
  res["count"] = len(data)
  if columns and data:
    res["first_row"] = data[0]
elif fmt == "summary":
  res["sample_rows"] = data[:3]
  res["hint"] = ("row_count is capped at max_rows when truncated; pass "
                 "format='rows' for the data or 'csv' for a dump")
elif fmt == "csv":
  out = [",".join(str(c) for c in columns)] if columns else []
  for row in data:
    out.append(",".join("" if v is None else str(v) for v in row))
  res["csv"] = "\n".join(out)
elif fmt == "rows":
  res["rows"] = data
else:
  return mcp_ret({"error": "format must be one of rows, count, summary, csv"})
return mcp_ret(res, ensure_ascii=False)
