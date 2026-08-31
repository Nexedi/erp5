def mcp_ret(o, *a, **k):
  return json.dumps(_mcp_unicode(o), ensure_ascii=False), o
def _mcp_unicode(value):
  if isinstance(value, str):
    decode = getattr(value, "decode", None)
    if decode is None:
      return value  # Python 3
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


def is_text(value):
  return hasattr(value, "strip")


def as_flag(value):
  if isinstance(value, bool):
    return value
  if value in (None, "", 0):
    return False
  try:
    return str(value).strip().lower() not in ("", "0", "false", "no", "none")
  except Exception:
    return bool(value)


def _portal():
  return context.getPortalObject()


def _installed_bt(title):
  portal = _portal()
  best = None
  for bt in portal.portal_templates.objectValues():
    if bt.getTitle() == title:
      try:
        n = int(bt.getId())
      except Exception:
        n = None
      if best is None or (n is not None and (best[0] is None or n > best[0])):
        best = (n, bt)
  return best[1] if best else None


def _repository_root_list():
  portal = _portal()
  paths = []
  try:
    pref = portal.portal_preferences.default_configurator_preference
    paths = list(pref.getPreferredWorkingCopyList() or [])
  except Exception:
    paths = []
  if not paths:
    try:
      paths = list(portal.portal_preferences.getPreferredWorkingCopyList() or [])
    except Exception:
      paths = []
  roots = []
  for p in paths:
    p = str(p).rstrip("/")
    if p and p not in roots:
      roots.append(p)
  return roots


_VC = {}


def _any_vcs():
  if "vcs" in _VC:
    return _VC["vcs"], _VC["repo_root"]
  portal = _portal()
  tried = []
  for bt in portal.portal_templates.objectValues():
    if bt.getBuildingState() != 'built':
      continue
    try:
      vcs = bt.getVcsTool()
      repo_root = vcs.git("rev-parse", "--show-toplevel")
      _VC["vcs"], _VC["repo_root"] = vcs, repo_root
      return vcs, repo_root
    except Exception:
      tried.append(bt.getTitle())
      continue
  raise RuntimeError(
    "No installed business template resolves a git working copy.")


def _resolve_repo_dir(bt_name):
  """Absolute path of `<repository_root>/<bt_name>`, or None."""
  if "../" in bt_name or bt_name.startswith("/") or "/" in bt_name:
    raise RuntimeError(
      "business_template must be a bare directory name, got %r" % bt_name)
  vcs, repo_root = _any_vcs()
  for root in _repository_root_list():
    candidate = str(root) + "/" + str(bt_name)
    try:
      vcs.git("hash-object", candidate + "/bt/title")
      return candidate
    except Exception:
      continue
  return None


def _abort():
  # A failed install/update must not leave a half-applied ZODB transaction.
  # The surrounding request commits only when this tool returns normally.
  try:
    import transaction
    transaction.abort()
  except Exception:
    pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

bt_name = str(business_template or "").strip()
if not bt_name:
  return mcp_ret({"success": False, "operation": "install",
                  "error": "business_template is required",
                  "business_template": None})

installed = _installed_bt(bt_name)
if installed is not None:
  return mcp_ret({
    "success": False, "operation": "install",
    "error": "already_installed",
    "business_template": bt_name,
    "installed_revision": installed.getRevision() or installed.getShortRevision(),
    "hint": ("%s is already installed in ERP5. Use "
             "erp5_bt_update_from_repository to update it from the repository "
             "files, or erp5_bt_export_to_repository to push the ERP5 "
             "representation back into the repository." % bt_name)})

try:
  repo_dir_abs = _resolve_repo_dir(bt_name)
except Exception as error:
  return mcp_ret({"success": False, "operation": "install",
                  "error": "invalid_business_template",
                  "business_template": bt_name,
                  "detail": str(error)})
if repo_dir_abs is None:
  return mcp_ret({
    "success": False, "operation": "install",
    "error": "invalid_business_template",
    "business_template": bt_name,
    "repository_roots": _repository_root_list(),
    "detail": ("No directory '%s' was found beneath the configured working-copy "
               "roots." % bt_name)})

portal = _portal()
try:
  # updateBusinessTemplateFromUrl downloads the directory into a fresh ZODB
  # Business Template (one coherent snapshot: ERP5 reads every file at
  # download time), builds it, and installs it in a single transaction.
  # With no previous installed version this is an install, not an update.
  installed_bt = portal.portal_templates.updateBusinessTemplateFromUrl(
    download_url=repo_dir_abs, update_catalog=False, only_different=True)
except Exception as error:
  _abort()
  import traceback
  tb = traceback.format_exc()
  detail = str(error)
  code = "install_failed"
  for marker in ("SyntaxError", "XML", "Expat", "parse", "Traceback"):
    if marker in detail or marker in tb:
      code = "component_validation_failed"
      break
  return mcp_ret({
    "success": False, "operation": "install", "error": code,
    "business_template": bt_name, "detail": detail})

result = {
  "success": True, "operation": "install",
  "business_template": bt_name,
  "repository_to_zodb": True,
  "created": [bt_name],
  "modified": [], "deleted": [],
  "zodb_transaction_committed": None,  # governed by the surrounding request
  "warning": ("All synchronous ZODB changes from this install commit or abort "
              "together with the surrounding request transaction.")
}
try:
  result["bt_id"] = installed_bt.getId()
  result["revision"] = installed_bt.getRevision() or installed_bt.getShortRevision()
  result["short_revision"] = installed_bt.getShortRevision()
except Exception:
  pass
return mcp_ret(result)
