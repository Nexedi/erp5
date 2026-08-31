def mcp_ret(o, *a, **k):
  return json.dumps(_mcp_unicode(o), ensure_ascii=False), o
def _mcp_unicode(value):
  # json.dumps(ensure_ascii=False) joins its output chunks on Python 2, so a
  # payload mixing unicode with utf-8 str makes that join decode the bytes as
  # ascii and die on the first umlaut. Everything read from ZODB or through
  # the VCS/git helpers comes back as a native str, while MCP arguments arrive
  # as unicode, so the mix is the rule rather than the exception.
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


def is_text(value):
  # duck-typed: MCP hands strings over as unicode on Python 2, so an
  # isinstance(..., str) test silently misses every one of them
  return hasattr(value, "strip")


def as_flag(value):
  # a client holding a stale copy of the input schema forwards a flag as text
  if isinstance(value, bool):
    return value
  if value in (None, "", 0):
    return False
  try:
    return str(value).strip().lower() not in ("", "0", "false", "no", "none")
  except Exception:
    return bool(value)


# ---------------------------------------------------------------------------
# ERP5-side resolution.
#
# The tools never touch the filesystem directly: the Python Script sandbox
# this runs in forbids os/os.path and open(), so every byte that has to be
# read or written goes through a privileged API -- the VCS (git) tool, which
# reads and writes files via a subprocess owned by the Zope process, and the
# standard Business Template APIs (portal_templates / bt.export), which have
# their own filesystem access. All paths are plain strings; none of os.path
# is used.
# ---------------------------------------------------------------------------

def _portal():
  return context.getPortalObject()


def _installed_bt(title):
  """The installed Business Template document whose title matches, newest id."""
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
  """The working-copy roots shared with the coding agent.

  They are configured on the active configuration preference
  (default_configurator_preference, field my_preferred_working_copy_list) and
  point at the same checkout the agent edits. Falling back to the generic
  portal_preferences resolver keeps the tools usable when that specific
  preference is renamed or absent.
  """
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


# cached so the expensive installed-BT scan happens once per request
_VC = {}

def _any_vcs():
  """A git VCS tool rooted on the agent-shared working copy.

  The roots that are shared with the coding agent live on
  default_configurator_preference (my_preferred_working_copy_list); the generic
  active preference (which bt.getVcsTool()/getExportPath() use) points at the
  software-release copy, not the one the agent edits. So this tool binds the
  git VCS explicitly onto the agent-shared root, and every git read/write runs
  with -C <repo_root> so paths come back relative to the repository top level.

  The tool itself does no filesystem I/O: all bytes travel through the git
  subprocess and the privileged Business Template APIs, which the script
  sandbox allows. Requires erp5_forge and Developer/Manager privileges.
  """
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
    "(tried %s). These tools need the erp5_forge BT and the shared working "
    "copy to be reachable with the caller's Developer/Manager privileges."
    % ", ".join(tried))


def _resolve_repo_dir(bt_name):
  """Absolute path of `<repository_root>/<bt_name>`, or None.

  Binds the git VCS tool on the SAME root that contains the Business Template
  and remembers that (vcs, repo_root, repo_dir) in the request cache, so every
  later step compares against the repository the template actually lives in.
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
      # existence probe without os: git hash-object reads the file
      vcs.git("hash-object", candidate + "/bt/title")
      repo_root = vcs.git("-C", root, "rev-parse", "--show-toplevel")
    except Exception:
      continue
    _VC["vcs"], _VC["repo_root"], _VC["repo_dir"] = vcs, repo_root, candidate
    return candidate
  return None


def repo_relative(repo_root, absolute_path):
  """Strip <repo_root>/ from an absolute path to make a repo-relative one."""
  prefix = str(repo_root).rstrip("/") + "/"
  if str(absolute_path).startswith(prefix):
    return str(absolute_path)[len(prefix):]
  return str(absolute_path)


def _blob(vcs, *expr):
  """A git object id for any expression, or None when it does not resolve."""
  try:
    return vcs.git(*expr)
  except Exception:
    return None


def _git_list(vcs, repo_dir_cwd, *expr):
  """git output split into non-empty lines, [] on failure."""
  try:
    out = vcs.git(*expr) if not repo_dir_cwd else vcs.git("-C", repo_dir_cwd, *expr)
  except Exception:
    return []
  if not out:
    return []
  return [line for line in out.split("\n") if line]


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


def _validate_source(extension, content):
  """Return None if valid, else a real problem report.

  The restricted sandbox forbids every content validator -- compile, ast and
  the whole xml.* tree are "unauthorized". So real syntax/XML validation
  cannot run here; it happens in the ERP5 build/install/update step (under
  privileges). This function returns the _DEFERRED sentinel when the validator
  it needs is unavailable, so the caller reports it as deferred rather than
  as a false failure. When a validator IS available it parses for real.
  """
  if extension in (".py",):
    if not _COMPILE_OK:
      return _DEFERRED
    try:
      compile(_as_bytes(content), "<business template>", "exec")
      return None
    except Exception as error:
      return "python_syntax_error: %s" % (error,)
  if extension in (".xml",):
    if not _XML_OK:
      return _DEFERRED
    try:
      # minidom refuses a unicode (text) string that carries an XML encoding
      # declaration, so hand it the raw bytes.
      xml.dom.minidom.parseString(_as_bytes(content))
      return None
    except Exception as error:
      return "xml_parse_error: %s" % (error,)
  return None


def _probe_compile():
  try:
    compile("x=1", "<probe>", "exec")
    return True
  except Exception:
    return False


def _probe_xml():
  try:
    import xml.dom.minidom
    return True
  except Exception:
    return False


_COMPILE_OK = _probe_compile()
_XML_OK = _probe_xml()
_DEFERRED = "__deferred_validation__"


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


def _stage_export(bt, stage_dir):
  """Export the installed (built) BT into `stage_dir` and index it with git.

  `git add -A` + `git ls-files` lets this script enumerate the exported files
  and hash their contents without any os/listdir/open access.

  export() does not build: without the build below the comparison sees the
  LAST BUILT state, not the current ZODB one, and edits made after the last
  build are silently reported as "no drift". Same refresh as the scoped export
  helper (MCPDevHelpers.scopedExport) before every commit.
  """
  vcs, repo_root = _any_vcs()
  if bt.getBuildingState() == "draft":
    bt.edit()
  bt.build(update_revision=False)
  bt.export(path=stage_dir, local=True)
  # Exporting through BusinessTemplateFolder(creation=1) builds the directory.
  vcs.git("-C", stage_dir, "init", "-q")
  vcs.git("-C", stage_dir, "add", "-A")
  return vcs, repo_root


def _zodb_state(bt, select=None):
  """A temp-dir snapshot of the installed BT's ZODB representation.

  Returns (vcs, repo_root, stage_dir, {rel_path -> blob}) where rel_path is the
  path the file would have inside the repository's Business Template folder.
  `select(rel)` optionally narrows hashing (and therefore every comparison)
  to the matching BT-relative paths -- a scoped status answers the "is my
  file in drift?" question without a git call per file of a 1000+-file BT,
  which is what used to time the whole tool out (session issue B7).
  """
  vcs, repo_root = _any_vcs()
  name = str(bt.getTitle())
  stage = "/tmp/mcp_bt_stage_" + name + "_" + str(int(__import__("time").time() * 1000))
  vcs, repo_root = _stage_export(bt, stage)
  files = _git_list(vcs, stage, "ls-files")
  blob_map = {}
  for rel in files:
    if select is not None and not select(rel):
      continue
    blob_map[rel] = _blob(vcs, "-C", stage, "hash-object", stage + "/" + rel)
  return vcs, repo_root, stage, blob_map


# ---------------------------------------------------------------------------
# Scoping and list capping.
#
# path_pattern (glob, '*' spans '/') narrows every comparison -- repository
# side, ERP5 side, conflicts, validation -- to matching paths. Patterns are
# matched against repository-root-relative paths (e.g.
# bt5/erp5_core/CatalogMethodTemplateItem/...), the form the report uses.
# summary_only / max_list cap the returned lists the way erp5_bt_commit does;
# with no explicit summary_only, templates with more than 500 files are
# summarized automatically (B7: a git-call-per-file full status on them is
# what timed the tool out).
# ---------------------------------------------------------------------------

_glob_cache = {}


def _glob_regex(pattern):
  # fnmatch semantics: '*' spans '/', '?' is one char
  rx = _glob_cache.get(pattern)
  if rx is None:
    rx = _re.compile("^" + "".join(
      "." if c == "?" else ".*" if c == "*" else _re.escape(c)
      for c in pattern) + "$")
    _glob_cache[pattern] = rx
  return rx


def _as_pattern_list(value):
  """A client forwards a parameter it has never heard of as a plain string;
  accept a JSON array or newline/comma separated entries."""
  if value is None:
    return []
  if isinstance(value, (list, tuple)):
    return [str(v) for v in value if str(v).strip()]
  text = str(value).strip()
  if text.startswith("["):
    try:
      parsed = json.loads(text)
      if isinstance(parsed, list):
        return [str(v) for v in parsed if str(v).strip()]
    except Exception:
      pass
  return [p.strip() for p in text.replace(",", "\n").split("\n") if p.strip()]


pattern_list = _as_pattern_list(path_pattern)
scanned = bool(pattern_list)


def is_asked_for(repo_relative_path):
  if not pattern_list:
    return True
  for pattern in pattern_list:
    if pattern.endswith("/"):
      if repo_relative_path.startswith(pattern):
        return True
    elif _glob_regex(pattern).match(repo_relative_path):
      return True
  return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

bt_name = str(business_template or "").strip()

if not bt_name:
  return mcp_ret({
    "error": "business_template is required: the bare directory name of the "
             "Business Template, e.g. 'erp5_project'.",
    "business_template": None,
  })

installed_bt = _installed_bt(bt_name)
repo_dir_abs = None
try:
  repo_dir_abs = _resolve_repo_dir(bt_name)
except Exception as error:
  repo_dir_abs = None
  resolution_error = str(error)
else:
  resolution_error = None

if repo_dir_abs is None:
  return mcp_ret({
    "error": "no repository directory found for business_template '%s' under "
             "the configured working-copy roots. Not present in the shared "
             "checkout, or not readable by this connection." % bt_name,
    "business_template": bt_name,
    "repository_roots": _repository_root_list(),
    "installed_in_erp5": installed_bt is not None,
  })

vcs, repo_root = None, None
vcs_error = None
try:
  vcs, repo_root = _any_vcs()
except Exception as error:
  vcs_error = str(error)
  return mcp_ret({
    "error": "repository access unavailable",
    "business_template": bt_name,
    "detail": vcs_error,
    "hint": "These tools act on the shared git working copy and need the "
            "caller to hold development permissions (Manager or Developer) "
            "and the erp5_forge BT to be installed, so that getVcsTool and "
            "the git subprocess can read and write the checkout.",
  })
bt_rel_prefix = repo_relative(repo_root, repo_dir_abs)
baseline_revision = vcs.git("rev-parse", "HEAD")
branch = vcs.git("rev-parse", "--abbrev-ref", "HEAD")

tracked = _git_list(vcs, repo_root, "ls-files", repo_dir_abs)
untracked = _git_list(vcs, repo_root, "ls-files", "--others", "--exclude-standard",
                      repo_dir_abs)
total_file_count = len(tracked) + len(untracked)

# summary_only=None means "caller did not say": big templates get the summary
# treatment automatically, since a full per-file sweep is what timed out (B7).
summary_automatic = False
if summary_only is None:
  summary_only = total_file_count > 500
  summary_automatic = summary_only
else:
  if isinstance(summary_only, bool):
    summary_only = summary_only
  else:
    summary_only = str(summary_only).strip().lower() not in (
      "", "0", "false", "no", "none")
try:
  max_list = int(max_list)
except Exception:
  max_list = 25

# Every side compares only the selected paths, so a scoped status on a
# 1000+-file BT costs a handful of git calls instead of thousands.
selected_tracked = [p for p in tracked if is_asked_for(p)]
selected_untracked = [p for p in untracked if is_asked_for(p)] if scanned else untracked

# Verify the expected repository revision, when the caller supplied one.
# It is a git object id (full or shortened), or the special marker 'git-head'
# meaning "whatever origin/HEAD currently is". No sha256 content hash is
# stored here because the baseline is the git HEAD commit itself.
if expected_repository_revision:
  expected_repository_revision = str(expected_repository_revision).strip()
  if expected_repository_revision and \
     expected_repository_revision != "git-head" and \
     not baseline_revision.startswith(expected_repository_revision):
    return mcp_ret({
      "error": "repository_changed",
      "business_template": bt_name,
      "expected_repository_revision": expected_repository_revision,
      "repository_revision": baseline_revision,
      "hint": "The working copy has moved on since the caller captured its "
              "revision. Re-enter the expected revision or omit it to see "
              "the current status."
    })

# ---------------------------------------------------------------------------
# Repository side: compare the working tree against the baseline (HEAD).
# ---------------------------------------------------------------------------
repo_modified = []
repo_added = []
repo_deleted = []
for rel in selected_tracked:
  head = _blob(vcs, "rev-parse", "HEAD:" + rel)
  if head is None:
    repo_added.append(rel)
    continue
  working = _blob(vcs, "hash-object", repo_root + "/" + rel)
  if working is None:
    repo_deleted.append(rel)
  elif working != head:
    repo_modified.append(rel)
for rel in selected_untracked:
  if rel not in repo_added:
    repo_added.append(rel)
repo_modified.sort()
repo_added.sort()
repo_deleted.sort()

# ---------------------------------------------------------------------------
# ERP5 side: export the installed ZODB representation and compare to baseline.
# ---------------------------------------------------------------------------
zodb_vcs = None
stage_dir = None
zodb_modified = []
zodb_added = []
zodb_deleted = []
if installed_bt is not None:
  try:
    def _select_zodb(rel):
      # zodb paths are reported with the bt5/ prefix; selection sees the same
      # paths the report uses
      return is_asked_for(bt_rel_prefix + "/" + rel)
    zv, zroot, stage_dir, zodb_blob_map = _zodb_state(installed_bt, select=_select_zodb)
    zodb_vcs = zv
    for rel in sorted(zodb_blob_map):
      head = _blob(zv, "rev-parse", "HEAD:" + bt_rel_prefix + "/" + rel)
      if head is None:
        zodb_added.append(bt_rel_prefix + "/" + rel)
      elif zodb_blob_map[rel] != head:
        zodb_modified.append(bt_rel_prefix + "/" + rel)
    # Deleted on the ERP5 side: present at HEAD, absent from the export.
    zodb_rel_set = set([bt_rel_prefix + "/" + r for r in zodb_blob_map])
    for rel in selected_tracked:
      if rel not in zodb_rel_set:
        zodb_deleted.append(rel)
    zodb_modified.sort()
    zodb_added.sort()
    zodb_deleted.sort()
  except Exception as error:
    zodb_error = str(error)
  else:
    zodb_error = None
else:
  zodb_error = (
    "not installed: no ERP5/ZODB representation to compare against. The "
    "repository side is complete; install from the repository to populate "
    "the ERP5 side.")

# ---------------------------------------------------------------------------
# Conflicts: independently modified / added / deleted on both sides.
# ---------------------------------------------------------------------------
repo_set = set(repo_modified) | set(repo_added) | set(repo_deleted)
zodb_set = set(zodb_modified) | set(zodb_added) | set(zodb_deleted)
conflicts = sorted(repo_set & zodb_set)

# ---------------------------------------------------------------------------
# Validation (Python syntax / XML) of the head-of-line sources.
# ---------------------------------------------------------------------------
validation_error_list = []
validation_failed_list = []
checked = 0
deferred_count = 0
for rel in selected_tracked:
  if not rel.endswith((".py", ".xml")):
    continue
  head = _blob(vcs, "rev-parse", "HEAD:" + rel)
  if head is None:
    continue  # not present at baseline; validated at install/update time
  content = _blob(vcs, "show", "HEAD:" + rel)
  if content is None:
    continue
  checked += 1
  extension = rel[rel.rfind("."):] if "." in rel else ""
  problem = _validate_source(extension, content)
  if problem == _DEFERRED:
    deferred_count += 1
  elif problem:
    validation_failed_list.append(rel)
    validation_error_list.append("%s: %s" % (rel, problem))

# Capped reporting: nothing is hidden silently -- every list carries its
# count, and a "_more" marker says how many entries were left out.
def cap_into(container, name, full_list):
  container[name + "_count"] = len(full_list)
  if summary_only:
    container[name] = []
  elif max_list and len(full_list) > max_list:
    container[name] = full_list[:max_list]
    container[name + "_more"] = len(full_list) - max_list
  else:
    container[name] = full_list

result = {
  "business_template": bt_name,
  "repository_root": repo_root,
  "repository_path": repo_dir_abs,
  "baseline_revision": baseline_revision,
  "branch": branch,
  "installed_in_erp5": installed_bt is not None,
  "file_count": total_file_count,
  "summary_only": bool(summary_only),
  "path_pattern": pattern_list or None,
  "repository_to_zodb": {},
}
if scanned:
  result["selected_file_count"] = len(selected_tracked) + len(selected_untracked)
  if not selected_tracked and not selected_untracked:
    result["hint"] = ("path_pattern %s matched no file of this business "
                      "template; patterns are matched against "
                      "repository-root-relative paths like "
                      "bt5/erp5_core/CatalogMethodTemplateItem/..." % pattern_list)
if summary_automatic:
  result["summary_note"] = ("summary_only set automatically for this %d-file "
    "template (full sweeps time out); pass summary_only=false for full "
    "lists, or scope with path_pattern" % total_file_count)
cap_into(result["repository_to_zodb"], "modified", repo_modified)
cap_into(result["repository_to_zodb"], "added", repo_added)
cap_into(result["repository_to_zodb"], "deleted", repo_deleted)
if installed_bt is not None:
  result["zodb_to_repository"] = {}
  cap_into(result["zodb_to_repository"], "modified", zodb_modified)
  cap_into(result["zodb_to_repository"], "added", zodb_added)
  cap_into(result["zodb_to_repository"], "deleted", zodb_deleted)
  result["erp5_revision"] = None
  try:
    result["erp5_revision"] = installed_bt.getRevision()
  except Exception:
    pass
else:
  result["zodb_to_repository"] = None
if conflicts:
  cap_into(result, "conflicts", conflicts)
else:
  result["conflicts"] = []
  result["conflicts_count"] = 0
conflict_count = len(conflicts)
validation = {
  "checked_files": checked,
  "failed": validation_failed_list,
  "content_validation_deferred": deferred_count,
}
result["validation"] = validation
if validation_failed_list:
  result["validation"]["errors"] = validation_error_list
result["update_from_repository_safe"] = (not conflicts) and \
  not validation_failed_list and (installed_bt is not None) and \
  (zodb_error is None)
result["export_to_repository_safe"] = (not conflicts) and installed_bt is not None

if conflicts:
  shown = result.get("conflicts") or []
  suffix = (": " + ", ".join(str(p) for p in shown)) \
    if len(shown) == conflict_count else ""
  result["warning"] = ("Conflicting changes exist on both the repository and "
    "the ERP5 side for %d path(s)%s. Resolve them before updating ERP5 from "
    "the repository or exporting ERP5 to the repository."
    % (conflict_count, suffix))
elif validation_failed_list:
  result["warning"] = ("The repository fails validation (%s); updating ERP5 "
    "from it is not safe until these are fixed." %
    ", ".join(validation_failed_list))
elif not installed_bt:
  result["warning"] = ("%s is not installed in ERP5. "
    "'update_from_repository' is not applicable until it is installed with "
    "erp5_bt_install_from_repository." % bt_name)
if zodb_error:
  if installed_bt is not None:
    result["warning"] = (result.get("warning", "") + " ERP5 comparison "
      "incomplete: %s." % zodb_error).strip()
  else:
    result["warning"] = (result.get("warning", "") + " " +
                         zodb_error).strip()
if deferred_count:
  note = ("%d file(s) could not be content-validated here "
          "restricted tool (no syntax/XML validator is importable); update/install "
          "validates them properly via the ERP5 build step." %
          deferred_count)
  result["warning"] = (result.get("warning", "") + " " + note).strip()

# The temporary export snapshot stays under /tmp; it is never written into the
# working repository, so an interrupted run cannot leave the repository half
# exported.
return mcp_ret(result)
