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


def _text(value):
  if isinstance(value, str):
    decode = getattr(value, "decode", None)
    if decode is None:
      return value
    try:
      return decode("utf-8")
    except Exception:
      return decode("utf-8", "replace")
  return value


def _as_bytes(value):
  """Native bytes, from py2 str, py2 unicode or py3 str."""
  if isinstance(value, str):
    if getattr(value, "decode", None) is not None:
      return value  # Python 2 str is already bytes
    return value.encode("utf-8")  # Python 3 text
  encode = getattr(value, "encode", None)
  if encode is not None:
    return value.encode("utf-8")  # Python 2 unicode
  return value


def _probe_compile():
  try:
    compile("x=1", "<probe>", "exec")
    return True
  except Exception:
    return False


_COMPILE_OK = _probe_compile()
_DEFERRED = "__deferred_validation__"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

bt_name = str(business_template or "").strip()
if not bt_name:
  return mcp_ret({"success": False, "operation": "export",
                  "error": "business_template is required",
                  "business_template": None})

installed_bt = _installed_bt(bt_name)
if installed_bt is None:
  return mcp_ret({
    "success": False, "operation": "export",
    "error": "not_installed",
    "business_template": bt_name,
    "hint": ("%s is not installed in ERP5, so there is no ERP5 representation "
             "to export." % bt_name)})

repo_dir_abs = _resolve_repo_dir(bt_name)
if repo_dir_abs is None:
  return mcp_ret({"success": False, "operation": "export",
                  "error": "invalid_business_template",
                  "business_template": bt_name,
                  "repository_roots": _repository_root_list()})

dry_run = as_flag(dry_run)
force = as_flag(force)

# Stage the ERP5 representation into a temp directory and index it with git so
# this sandboxed script can enumerate and hash the exported files.
vcs, repo_root = _any_vcs()
stage = "/tmp/mcp_bt_stage_" + bt_name + "_" + \
        str(int(__import__("time").time() * 1000))
export_error = None
stage_blob_map = {}
stage_file_list = []
conflict_list = []
untracked_list = []
try:
  installed_bt.export(path=stage, local=True)
  vcs.git("-C", stage, "init", "-q")
  vcs.git("-C", stage, "add", "-A")
  stage_file_list = _git_list(vcs, stage, "ls-files")
  for rel in stage_file_list:
    stage_blob_map[rel] = _blob(vcs, "-C", stage, "hash-object",
                                stage + "/" + rel)
except Exception as error:
  export_error = str(error)

# What the export would change in the repository, relative to the current
# working tree of the BT directory.
bt_rel = repo_relative(repo_root, repo_dir_abs)
working_tracked = _git_list(vcs, repo_root, "ls-files", repo_dir_abs)
working_untracked = _git_list(vcs, repo_root, "ls-files", "--others",
                              "--exclude-standard", repo_dir_abs)

zodb_modified = []
zodb_added = []
zodb_deleted = []
if export_error is None:
  stage_rel_set = set(stage_file_list)
  for rel in stage_file_list:
    repo_rel = bt_rel + "/" + rel
    working = _blob(vcs, "hash-object", repo_root + "/" + repo_rel)
    if working is None or working != stage_blob_map[rel]:
      # ERp5 would (re)write this file over the repository copy.
      zodb_modified.append(rel)
  for rel in working_tracked:
    # A tracked repo file with no counterpart in a built BT would be removed
    # by an export (dangling file clean-up), unless it is a keep path.
    base = rel[len(bt_rel) + 1:]
    if base not in stage_rel_set:
      zodb_deleted.append(base)

# Local edits that an export would clobber or drop.
working_edit_map = {}
for rel in working_tracked:
  head = _blob(vcs, "rev-parse", "HEAD:" + rel)
  if head is None:
    continue
  working = _blob(vcs, "hash-object", repo_root + "/" + rel)
  if working is not None and working != head:
    working_edit_map[rel] = True

for rel in working_untracked:
  untracked_list.append(rel[len(bt_rel) + 1:] if rel.startswith(bt_rel) else rel)

# exported_modifies = files whose repo working copy would change.
exported_modified_set = set(zodb_modified)
for base in zodb_deleted:
  exported_modified_set.add(bt_rel + "/" + base)
for rel in stage_file_list:
  exported_modified_set.add(bt_rel + "/" + rel)

for rel in working_edit_map:
  if rel in exported_modified_set:
    conflict_list.append(rel)

result = {
  "success": False, "operation": "export",
  "business_template": bt_name,
  "dry_run": dry_run,
}

if export_error is not None:
  return mcp_ret({"success": False, "operation": "export",
                  "error": "export_failed", "business_template": bt_name,
                  "detail": export_error})

def _repo_rel(base):
  return (bt_rel + "/" + base) if bt_rel else base

result["zodb_to_repository"] = {
  "modified": sorted(set(_repo_rel(x) for x in zodb_modified))[:500],
  "added": sorted(set(_repo_rel(x) for x in zodb_added))[:500],
  "deleted": sorted(set(_repo_rel(x) for x in zodb_deleted))[:500],
}

predict = {
  "modified": sorted(set(_repo_rel(x) for x in zodb_modified))[:500],
  "added": sorted(set(_repo_rel(x) for x in zodb_added))[:500],
  "deleted": sorted(set(_repo_rel(x) for x in zodb_deleted))[:500],
}
if untracked_list:
  predict["untracked_in_repository_bt_dir"] = sorted(set(untracked_list))[:200]
result["would_change"] = predict

for rel in working_edit_map:
  if rel in exported_modified_set:
    conflict_list.append(rel)

# Untracked files inside the Business Template directory would be removed by
# an export (dangling-file clean-up), so treat them as conflicts too.
for rel in working_untracked:
  conflict_list.append(rel)

conflict_list = list(set(conflict_list))
conflict_list.sort()
result["conflicts"] = conflict_list
result["export_to_repository_safe"] = not conflict_list

if conflict_list and not as_flag(force):
  result["error"] = "repository_write_conflict"
  result["hint"] = ("These repository files were modified locally since the "
                    "baseline AND would be overwritten by an export, or are "
                    "untracked files an export would remove. Resolve them, or "
                    "call again with force=true to clobber them with the ERP5 "
                    "state (not recommended).")
  if dry_run:
    return mcp_ret(result)
  return mcp_ret(result)

# Validate the staged export before touching the working repository.
validation_failed = []
for rel in stage_file_list:
  if not rel.endswith((".py", ".xml")):
    continue
  raw = _blob(vcs, "-C", stage, "show", ":" + rel)
  if raw is None:
    continue
  extension = rel[rel.rfind("."):]
  if extension == ".py":
    if not _COMPILE_OK:
      continue  # no compiler importable; deferred to the build/install step
    try:
      compile(_as_bytes(raw), "<business template export>", "exec")
    except Exception as error:
      validation_failed.append("%s: python_syntax_error: %s" % (rel, error))
  elif extension == ".xml":
    try:
      import xml.dom.minidom
    except Exception:
      continue  # no XML parser importable in this restricted tool; deferred to extract/install
    try:
      xml.dom.minidom.parseString(_as_bytes(raw))
    except Exception as error:
      validation_failed.append("%s: xml_parse_error: %s" % (rel, error))
if validation_failed:
  result["error"] = "component_validation_failed"
  result["validation_errors"] = validation_failed
  result["export_to_repository_safe"] = False
  return mcp_ret(result)

if dry_run:
  result["success"] = True
  result["warning"] = ("Dry run: nothing was written. The ERP5 side is "
                       "exported and validated, but no repository file was "
                       "changed and no commit was made.")
  return mcp_ret(result)

# Apply: materialise the ERP5 state into the working copy (privileged),
# then commit. In-flight, unrelated working-copy changes outside this BT's
# directory are never touched; the whole BT is committed under one changelog.
if not changelog or not str(changelog).strip():
  result["success"] = False
  result["error"] = "changelog_required"
  result["hint"] = "A changelog message is required to record the export commit."
  return mcp_ret(result)

try:
  used_bt = None
  for bt in _portal().portal_templates.objectValues():
    if bt.getBuildingState() == 'built':
      used_bt = bt
      break
  export_vcs = used_bt.getVcsTool(vcs="git", path=repo_dir_abs)
  revision_before = export_vcs.getRevision()
  export_vcs.extractBT(installed_bt)
except Exception as error:
  result["success"] = False
  result["error"] = "export_failed"
  result["detail"] = str(error)
  return mcp_ret(result)

try:
  added, modified, removed, unparsed = [], [], [], 0
  for line in export_vcs.git("diff", "--raw", "--no-renames", "--relative",
                             "HEAD", ".").splitlines():
    parts = line.split("\t")
    if len(parts) < 2:
      continue
    meta = parts[0].split()
    if not meta:
      continue
    code = meta[-1][:1]
    path = parts[1]
    if code == "A":
      added.append(path)
    elif code == "D":
      removed.append(path)
    elif code == "M":
      modified.append(path)
    else:
      unparsed += 1
  export_vcs.commit(changelog, 0, added=added, modified=modified,
                    removed=removed)
except Exception as error:
  result["success"] = False
  result["error"] = "export_failed"
  result["detail"] = str(error)
  return mcp_ret(result)

try:
  revision_after = export_vcs.git("rev-parse", "--short", "HEAD").strip()
except Exception:
  revision_after = None
result["committed"] = revision_after != revision_before
result["revision"] = revision_after
result["committed_paths"] = {"added": added, "modified": modified,
                              "removed": removed}
if unparsed:
  result["unparsed_diff_lines"] = unparsed
result["success"] = True
result["zodb_transaction_committed"] = None
result["warning"] = ("All synchronous ZODB changes from this export commit or "
                     "abort together with the surrounding request transaction. "
                     "The repository change is a separate, non-transactional "
                     "filesystem step recorded as a git commit.")
return mcp_ret(result)
