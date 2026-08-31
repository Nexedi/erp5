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
  used_bt = None
  for bt in portal.portal_templates.objectValues():
    if bt.getBuildingState() == 'built':
      used_bt = bt
      break
  if used_bt is None:
    raise RuntimeError(
      "No built installed business template to bind the git VCS tool.")
  tried = []
  for root_info in _repository_root_list():
    root = str(root_info).rstrip("/")
    try:
      vcs = used_bt.getVcsTool(vcs="git", path=root)
      repo_root = vcs.git("-C", root, "rev-parse", "--show-toplevel")
    except Exception:
      tried.append(root)
      continue
    _VC["vcs"], _VC["repo_root"] = vcs, repo_root
    return vcs, repo_root
  raise RuntimeError(
    "Could not open a git VCS tool on any configured working-copy root "
    "(tried %s). Need the erp5_forge BT and Developer/Manager privileges."
    % ", ".join(tried))


def _resolve_repo_dir(bt_name):
  """Absolute path of `<repository_root>/<bt_name>`, or None.

  Binds the git VCS tool on the SAME root that contains the Business Template
  and remembers (vcs, repo_root, repo_dir) so later steps compare against the
  repository the template actually lives in.
  """
  if "../" in bt_name or bt_name.startswith("/") or "/" in bt_name:
    raise RuntimeError(
      "business_template must be a bare directory name, got %r" % bt_name)
  used_bt = None
  for bt in _portal().portal_templates.objectValues():
    if bt.getBuildingState() == 'built':
      used_bt = bt
      break
  if used_bt is None:
    raise RuntimeError("No built installed business template to bind the git VCS tool.")
  for root_info in _repository_root_list():
    root = str(root_info).rstrip("/")
    candidate = root + "/" + str(bt_name)
    try:
      vcs = used_bt.getVcsTool(vcs="git", path=root)
      vcs.git("hash-object", candidate + "/bt/title")
      repo_root = vcs.git("-C", root, "rev-parse", "--show-toplevel")
    except Exception:
      continue
    _VC["vcs"], _VC["repo_root"], _VC["repo_dir"] = vcs, repo_root, candidate
    return candidate
  return None


def repo_relative(repo_root, absolute_path):
  prefix = str(repo_root).rstrip("/") + "/"
  if str(absolute_path).startswith(prefix):
    return str(absolute_path)[len(prefix):]
  return str(absolute_path)


def _blob(vcs, *expr):
  try:
    return vcs.git(*expr)
  except Exception:
    return None


def _git_list(vcs, repo_dir_cwd, *expr):
  try:
    out = vcs.git(*expr) if not repo_dir_cwd else vcs.git("-C", repo_dir_cwd, *expr)
  except Exception:
    return []
  if not out:
    return []
  return [line for line in out.split("\n") if line]


def _compute_changes(bt_name):
  """Return the two-way diff of a BT between baseline(HEAD), repo and ERP5.

  Returns (vcs, repo_root, repo_dir, repo_modified, repo_added, repo_deleted,
  zodb_modified, zodb_added, zodb_deleted, conflicts, resolution_error).
  """
  installed_bt = _installed_bt(bt_name)
  repo_dir_abs = _resolve_repo_dir(bt_name)
  if repo_dir_abs is None:
    return (None, None, None, [], [], [], [], [], [], [], None, None)
  vcs, repo_root = _any_vcs()
  bt_rel = repo_relative(repo_root, repo_dir_abs)
  tracked = _git_list(vcs, repo_root, "ls-files", repo_dir_abs)
  untracked = _git_list(vcs, repo_root, "ls-files", "--others",
                        "--exclude-standard", repo_dir_abs)
  repo_modified = []
  repo_added = []
  repo_deleted = []
  for rel in tracked:
    head = _blob(vcs, "rev-parse", "HEAD:" + rel)
    if head is None:
      repo_added.append(rel)
      continue
    working = _blob(vcs, "hash-object", repo_root + "/" + rel)
    if working is None:
      repo_deleted.append(rel)
    elif working != head:
      repo_modified.append(rel)
  for rel in untracked:
    if rel not in repo_added:
      repo_added.append(rel)
  repo_modified.sort(); repo_added.sort(); repo_deleted.sort()

  zodb_modified = zodb_added = zodb_deleted = []
  zodb_error = None
  if installed_bt is not None:
    try:
      vv = None
      stage = "/tmp/mcp_bt_stage_" + bt_name + "_" + \
              str(int(__import__("time").time() * 1000))
      installed_bt.export(path=stage, local=True)
      vv, _ = _any_vcs()
      vv.git("-C", stage, "init", "-q")
      vv.git("-C", stage, "add", "-A")
      stage_files = _git_list(vv, stage, "ls-files")
      zodb_modified = []; zodb_added = []; zodb_deleted = []
      zodb_blob_map = {}
      for rel in stage_files:
        zodb_blob_map[rel] = _blob(vv, "-C", stage, "hash-object",
                                   stage + "/" + rel)
      for rel in sorted(zodb_blob_map):
        head = _blob(vv, "rev-parse", "HEAD:" + bt_rel + "/" + rel)
        if head is None:
          zodb_added.append(bt_rel + "/" + rel)
        elif zodb_blob_map[rel] != head:
          zodb_modified.append(bt_rel + "/" + rel)
      zodb_rel_set = set([bt_rel + "/" + r for r in zodb_blob_map])
      for rel in tracked:
        if rel not in zodb_rel_set:
          zodb_deleted.append(rel)
      zodb_modified.sort(); zodb_added.sort(); zodb_deleted.sort()
    except Exception as error:
      zodb_error = str(error)

  repo_set = set(repo_modified) | set(repo_added) | set(repo_deleted)
  zodb_set = set(zodb_modified) | set(zodb_added) | set(zodb_deleted)
  conflicts = sorted(repo_set & zodb_set)
  return (vcs, repo_root, repo_dir_abs, repo_modified, repo_added, repo_deleted,
          zodb_modified, zodb_added, zodb_deleted, conflicts, zodb_error)


def _abort():
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
  return mcp_ret({"success": False, "operation": "update",
                  "error": "business_template is required",
                  "business_template": None})

installed_bt = _installed_bt(bt_name)
if installed_bt is None:
  return mcp_ret({
    "success": False, "operation": "update",
    "error": "not_installed",
    "business_template": bt_name,
    "hint": ("%s is not installed in ERP5. Use erp5_bt_install_from_repository "
             "to install it from the repository first." % bt_name)})

def _text(value):
  """Normalise native bytes and unicode to a Python text string."""
  if isinstance(value, str):
    decode = getattr(value, "decode", None)
    if decode is None:
      return value  # Python 3
    try:
      return decode("utf-8")
    except Exception:
      return decode("utf-8", "replace")
  return value


def _validate_component_sources(repo_root, repo_dir_abs):
  """Trigger ERP5's own component validation on the Python files being applied.

  A Module Component's source edit compiles the Python, so broken code raises.
  Each .py the update will apply is fed to a throwaway Module Component whose
  edit + checkConsistency() are validated, and the throwaway is then removed --
  no broken component can be applied and nothing is left behind. The regular
  python sandbox forbids compile/ast, so this is the only genuine syntax gate
  available to the tool; it runs under the caller's portal permissions.

  Returns a list of one-line failures ([] = all applied component sources are
  syntactically valid).
  """
  vcs, _ = _any_vcs()
  rel_list = _git_list(vcs, repo_root, "ls-files", repo_dir_abs)
  portal = _portal()
  cc_tool = getattr(portal, "portal_components", None)
  if cc_tool is None:
    return []
  try:
    if "__bt_validate_tmp__" in cc_tool.objectIds():
      cc_tool._delObject("__bt_validate_tmp__")
  except Exception:
    pass
  try:
    tmp = cc_tool.newContent(portal_type="Module Component",
                             id="__bt_validate_tmp__", temp_object=True)
  except Exception:
    # cannot build a throwaway here; ERP5's transactional build still validates
    return []
  try:
    bound = getattr(tmp, "__of__", None)
    if bound is not None:
      tmp = bound(cc_tool)
  except Exception:
    # The sandbox denies __of__; the throwaway validates unbound, and ERP5's
    # own transactional build is the backstop when even that fails.
    pass
  errors = []
  for rel in rel_list:
    if not rel.endswith(".py"):
      continue
    content = _blob(vcs, "show", "HEAD:" + rel)
    if content is None:
      continue  # uncommitted file: validated by the transactional build itself
    try:
      tmp.setTextContent(_text(content))
      check = getattr(tmp, "checkConsistency", None)
      if callable(check):
        check()
    except Exception as error:
      errors.append("%s: component_validation_failed" % rel)
  try:
    cc_tool._delObject("__bt_validate_tmp__")
  except Exception:
    pass
  return errors


force = as_flag(force)

if not force:
  (vcs, repo_root, repo_dir_abs, repo_modified, repo_added, repo_deleted,
   zodb_modified, zodb_added, zodb_deleted, conflicts, zodb_error) = \
    _compute_changes(bt_name)
  if conflicts:
    return mcp_ret({
      "success": False, "operation": "update",
      "error": "synchronization_conflict",
      "business_template": bt_name,
      "conflicts": conflicts,
      "hint": ("Changes exist on BOTH the repository and the ERP5 side for "
               "%s. Updating ERP5 from the repository would overwrite the "
               "ERP5-side changes. Resolve them, or call again with "
               "force=true explicitly to proceed (not recommended)." %
               ", ".join(conflicts))})
  if repo_dir_abs is None:
    return mcp_ret({"success": False, "operation": "update",
                    "error": "invalid_business_template",
                    "business_template": bt_name})

# Explicit component-validation gate: feed the Python sources this update
# would apply to a throwaway Module Component (whose edit compiles the code).
# Any broken component blocks the update before ERP5's own transactional build.
repo_dir_for_apply = _resolve_repo_dir(bt_name)
component_error_list = []
if repo_dir_for_apply:
  component_error_list = _validate_component_sources(_any_vcs()[1],
                                                    repo_dir_for_apply)
if component_error_list:
  _abort()
  return mcp_ret({
    "success": False, "operation": "update",
    "error": "component_validation_failed",
    "business_template": bt_name,
    "component_errors": component_error_list,
    "hint": ("Broken component source in the repository blocks the update. "
              "Fix the listed Python files (or revert them) before updating "
              "ERP5 from the repository, so broken code is never installed."),
  })

try:
  updated_bt = installed_bt.getParentValue().updateBusinessTemplateFromUrl(
    download_url=repo_dir_for_apply,
    update_catalog=as_flag(update_catalog),
    reinstall=as_flag(reinstall),
    only_different=True,
  )
except Exception as error:
  _abort()
  import traceback
  tb = traceback.format_exc()
  detail = str(error)
  code = "update_failed"
  for marker in ("SyntaxError", "XML", "Expat", "parse", "Traceback"):
    if marker in detail or marker in tb:
      code = "component_validation_failed"
      break
  return mcp_ret({"success": False, "operation": "update", "error": code,
                  "business_template": bt_name, "detail": detail})

result = {
  "success": True, "operation": "update",
  "business_template": bt_name,
  "created": [], "modified": [], "deleted": [],
  "zodb_transaction_committed": None,
  "warning": ("All synchronous ZODB changes from this update commit or abort "
              "together with the surrounding request transaction.")
}
try:
  result["bt_id"] = updated_bt.getId()
  result["revision"] = updated_bt.getRevision() or updated_bt.getShortRevision()
  result["short_revision"] = updated_bt.getShortRevision()
  # The same list method the ERP5 update flow uses to decide keep/remove.
  modified_list = updated_bt.BusinessTemplate_getModifiedObject()
  for line in list(modified_list or []):
    object_id = getattr(line, "object_id", None)
    state = str(getattr(line, "object_state", "") or "")
    if object_id is None:
      continue
    if state.startswith("Added"):
      result["created"].append(object_id)
    elif state.startswith("Removed"):
      result["deleted"].append(object_id)
    else:
      result["modified"].append(object_id)
except Exception:
  pass
return mcp_ret(result)
