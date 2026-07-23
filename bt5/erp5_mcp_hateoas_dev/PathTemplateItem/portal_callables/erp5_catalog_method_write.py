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
from erp5.component.module.MCPDevHelpers import sha256Hex, catalogMethodInfo, catalogMethodEdit

portal = context.getPortalObject()
if not str(method_id or "").strip():
  return mcp_ret({"error": "method_id is required, e.g. "
                  "'z_catalog_product_sale_supply_line_list'."})
if not (src not in (None, "") or arguments_src not in (None, "")
        or title not in (None, "") or connection_id not in (None, "")
        or replacements):
  return mcp_ret({"error": "nothing to write: pass src and/or arguments_src "
                  "(full texts) and/or replacements (exact-match patterns), "
                  "or title.",
                  "hint": "read the current state first with "
                          "erp5_catalog_method_read; after a failed sequence "
                          "always re-read before retrying pattern edits."})

try:
  current = catalogMethodInfo(portal, method_id,
                              sql_catalog_id=str(sql_catalog_id) if sql_catalog_id else None)
except LookupError, e:
  return mcp_ret({"error": "%s" % e,
                  "hint": "read a known method first with erp5_catalog_method_read; "
                          "method ids are listed by "
                          "portal.portal_catalog.getSQLCatalog().objectIds()."})
except Exception, e:
  return mcp_ret({"error": "catalog method read failed: %s" % e})

new_src = current["src"]
new_arguments = current["arguments_src"]
if src not in (None, ""):
  new_src = str(src)
elif src_file:
  from erp5.component.module.MCPDevHelpers import readFile
  try:
    data = readFile(str(src_file))
  except Exception, e:
    return mcp_ret({"error": "src_file unreadable: %s" % e, "src_file": str(src_file)})
  try:
    new_src = data.decode("utf-8")
  except UnicodeDecodeError:
    new_src = data.decode("utf-8", "replace")
if arguments_src not in (None, ""):
  new_arguments = str(arguments_src)

applied = 0
replacements_target = str(replacements_target or "src")
if replacements_target not in ("src", "arguments_src"):
  return mcp_ret({"error": "replacements_target must be 'src' or "
                  "'arguments_src', got %r" % replacements_target})
if replacements:
  reps = json.loads(replacements) if isinstance(replacements, (str, unicode)) else replacements
  target = {"src": new_src, "arguments_src": new_arguments}[replacements_target]
  target = target.encode("utf-8") if isinstance(target, unicode) else target
  for rep in reps:
    old = rep.get("old_string", "")
    new = rep.get("new_string", "")
    old_s = old.encode("utf-8") if isinstance(old, unicode) else old
    new_s = new.encode("utf-8") if isinstance(new, unicode) else new
    count = target.count(old_s)
    if rep.get("replace_all"):
      if count == 0:
        return mcp_ret({"error": "replacement not found: %r" % old_s[:100]})
    elif count != 1:
      # must-match-once, like erp5_callable_write: a mangled multi-line
      # pattern (JSON escaping through the transport, B4) must fail loudly
      # instead of silently matching nothing
      return mcp_ret({"error": "replacement must match exactly once in %s "
                      "(matched %d): %r" % (replacements_target, count, old_s[:100]),
                      "hint": "multi-line changes are safer as a full src "
                              "rewrite (text_content transport preserves "
                              "newlines; patterns through replacements= are "
                              "for short single-line quote-free edits)"})
    target = target.replace(old_s, new_s)
    applied += 1
  target = target.decode("utf-8") if isinstance(target, str) else target
  if replacements_target == "src":
    new_src = target
  else:
    new_arguments = target

new_connection_id = (str(connection_id) if connection_id not in (None, "")
                     else current["connection_id"])
changed = (new_src != current["src"]) or (new_arguments != current["arguments_src"]) \
  or (str(title) if title not in (None, "") else current["title"]) != current["title"] \
  or new_connection_id != current["connection_id"]

if not changed:
  return mcp_ret({"status": "noop", "method_id": current["method_id"],
                  "sql_catalog_id": current["sql_catalog_id"],
                  "replacements_applied": applied,
                  "note": "content identical to what is deployed; nothing "
                          "written (byte-exact no-op)"})

try:
  info = catalogMethodEdit(portal, method_id,
                           sql_catalog_id=str(sql_catalog_id) if sql_catalog_id else None,
                           title=str(title) if title not in (None, "") else None,
                           connection_id=connection_id,
                           arguments_src=new_arguments,
                           src=new_src,
                           force_connection=(force_connection if isinstance(force_connection, bool)
                                             else str(force_connection).lower() in ("1", "true", "yes")))
except ValueError, e:
  return mcp_ret({"error": "%s" % e,
                  "hint": "changing the connection_id of a catalog method is "
                          "almost always an accident; pass force_connection=true "
                          "only when you mean it."})
except Exception, e:
  return mcp_ret({"error": "catalog method write failed: %s" % e,
                  "hint": "a failed manage_edit leaves the method untouched "
                          "(no half-applied state); re-read with "
                          "erp5_catalog_method_read before retrying."})

info["status"] = "written"
info["replacements_applied"] = applied
info["src_sha256"] = sha256Hex(info.get("src") or "")
info["arguments_sha256"] = sha256Hex(info.get("arguments_src") or "")
info["changed"] = {
  "src": new_src != current["src"],
  "arguments_src": new_arguments != current["arguments_src"],
}
return mcp_ret(info, ensure_ascii=False)
