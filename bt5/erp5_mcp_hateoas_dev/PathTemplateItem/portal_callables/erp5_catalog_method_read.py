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
from erp5.component.module.MCPDevHelpers import catalogMethodInfo

portal = context.getPortalObject()
if not str(method_id or "").strip():
  return mcp_ret({"error": "method_id is required, e.g. "
                  "'z_catalog_product_sale_supply_line_list'."})
try:
  info = catalogMethodInfo(portal, method_id,
                           sql_catalog_id=str(sql_catalog_id) if sql_catalog_id else None)
except LookupError, e:
  return mcp_ret({"error": "%s" % e,
                  "hint": "method ids can be listed with a one-line skin script "
                          "(erp5_skin_write + erp5_skin_call): "
                          "return portal.portal_catalog.getSQLCatalog().objectIds(); "
                          "the BT export lists the same files under "
                          "<bt>/CatalogMethodTemplateItem/portal_catalog/erp5_mysql_innodb/."})
except Exception, e:
  return mcp_ret({"error": "catalog method read failed: %s" % e})
info["hint"] = ("editing: erp5_catalog_method_write takes src and/or "
                "arguments_src (plus optional exact-match replacements); both "
                "texts are applied together through one manage_edit so the "
                "parsed _arg stays in sync (session issue B9).")
return mcp_ret(info, ensure_ascii=False)
