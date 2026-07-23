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
import re
portal = context.getPortalObject()

best = None
for bt in portal.portal_templates.objectValues():
  if bt.getTitle() == bt_title:
    try:
      n = int(bt.getId())
    except Exception:
      continue
    if best is None or n > best[0]:
      best = (n, bt)
if best is None:
  return mcp_ret({"status": "error",
                  "error": "No installed business template titled %s" % bt_title})
bt = best[1]
vcs = bt.getVcsTool()


def as_flag(value):
  """A client with a stale schema sends a flag as text; read it as one."""
  try:
    text = value.strip().lower()
  except AttributeError:
    return bool(value)
  return text not in ("", "0", "false", "no", "none")


rebase = as_flag(rebase)
summary_only = as_flag(summary_only)
try:
  max_list = int(max_list)
except Exception:
  max_list = 25


def redact(text):
  """A remote URL may carry a token in its userinfo; never hand that back.

  Applied to git's own output as well as to the configured URL, because a
  push error quotes the URL it tried.
  """
  out = []
  for piece in str(text).split("://"):
    if out and "@" in piece.split("/")[0]:
      head, tail = piece.split("@", 1)
      if "/" not in head:
        piece = "***@" + tail
    out.append(piece)
  return "://".join(out)


def ahead_count():
  """Commits on HEAD the upstream does not have, asked of git directly.

  getAheadCount() is memoised on the tool for the duration of the request, so
  reading it after a push reports what was true before it -- which makes a
  push that landed look like one that did not.
  """
  try:
    return int(vcs.git("rev-list", "--count", "@{u}..HEAD").strip())
  except Exception:
    return None


def identity_argument_list():
  """Who the rebase commits as.

  ERP5's commit() supplies an identity of its own; a bare git rebase does
  not, and this instance has none configured, so it stops with 'Committer
  identity unknown' halfway through. Taking the identity off the tip commit
  keeps the replayed commit attributed to whoever made it.
  """
  argument_list = []
  for option, fmt in (("user.name", "%an"), ("user.email", "%ae")):
    try:
      value = vcs.git("log", "-1", "--format=" + fmt).strip()
    except Exception:
      value = ""
    if value:
      argument_list += ["-c", option + "=" + value]
  return argument_list


def describe_remote():
  """Where a push would land, so it is checked before it is done."""
  info = {}
  try:
    name_list = vcs.git("remote").split()
  except Exception:
    name_list = []
  if name_list:
    info["name"] = name_list[0]
    try:
      info["url"] = redact(vcs.git("remote", "get-url", name_list[0]).strip())
    except Exception:
      pass
  try:
    info["upstream"] = vcs.git(
      "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
    ).strip()
  except Exception:
    info["upstream"] = None
  return info


def do_rebase(result):
  """Fetch the upstream and replay HEAD onto it, or leave nothing behind.

  A push is rejected when the remote has moved on, and the fix is a rebase --
  but this working copy is shared and normally dirty with other people's
  uncommitted work, which a rebase refuses to run over. So it autostashes.

  Autostashing needs one thing done first: extractBT marks new files
  intent-to-add (git add -N), and git stash cannot save a worktree holding
  those -- it fails with "Cannot save the current worktree state" before the
  rebase even starts. Unstaging clears the marks without touching a single
  file: the changes stay in the worktree, new files go back to being
  untracked, which a rebase does not mind, and the next extractBT re-adds the
  marks. Contents are never at risk; only what happened to be staged is, and
  extractBT is what staged it.

  On any failure the rebase is aborted, which is how git restores the
  autostash, so the tree ends up as it was found rather than half rebased.
  """
  upstream = (result.get("remote") or {}).get("upstream")
  if not upstream or "/" not in upstream:
    result["rebase"] = "skipped: no upstream branch configured"
    return False
  try:
    vcs.git("fetch", upstream.split("/", 1)[0])
  except Exception, error:
    result["rebase"] = "fetch failed: %s" % redact(error)
    return False
  identity = identity_argument_list()
  try:
    vcs.git("reset", "-q")
  except Exception, error:
    result["rebase"] = "could not unstage before rebasing: %s" % redact(error)
    return False
  try:
    result["rebase"] = redact(vcs.git(*(
      identity + ["-c", "rebase.autoStash=true", "rebase", upstream]))) or "ok"
  except Exception, error:
    try:
      vcs.git("rebase", "--abort")
      note = " (rebase aborted, working copy restored)"
    except Exception, abort_error:
      if "no rebase in progress" in str(abort_error).lower():
        note = " (no rebase had started; working copy untouched)"
      else:
        note = (" (WARNING: could not abort the rebase; the working copy "
                "needs looking at by hand)")
    result["rebase"] = "failed: %s%s" % (redact(error), note)
    return False
  return True


def do_push(result):
  """Push HEAD to its upstream and say what git actually reported.

  git push writes its progress to stderr and exits 0 on 'Everything
  up-to-date', so neither silence nor an exception decides this: the commit
  count against the upstream does, and the raw output is handed back either
  way so a rejection can be read rather than guessed.
  """
  if rebase and not do_rebase(result):
    result["status"] = "error"
    result["pushed"] = False
    result["error"] = "Rebase did not succeed; nothing was pushed."
    return
  before = ahead_count()
  result["ahead"] = before
  if before == 0:
    result["pushed"] = True
    result["warning"] = "Nothing to push: already up to date with the remote."
    return
  upstream = (result.get("remote") or {}).get("upstream")
  argument_list = ["push", "--porcelain"]
  if upstream and "/" in upstream:
    remote_name, remote_branch = upstream.split("/", 1)
    argument_list += [remote_name, "HEAD:refs/heads/" + remote_branch]
  try:
    result["push_output"] = redact(vcs.git(*argument_list))
  except Exception, error:
    result["status"] = "error"
    result["pushed"] = False
    result["error"] = "Push failed: %s" % redact(error)
    if not rebase:
      result["hint"] = ("If the remote has moved on, call again with "
                        "rebase=True to replay onto it first.")
    return
  after = ahead_count()
  result["ahead_after"] = after
  result["pushed"] = after == 0
  if after != 0:
    result["status"] = "error"
    result["error"] = ("Push did not land: %s commit(s) still ahead of the "
                       "remote. See push_output." % after)


def as_selection_list(value):
  """A client forwards a parameter it has never heard of as a plain string;
  accept a JSON array or newline/comma separated entries."""
  if value is None:
    return None
  if isinstance(value, (list, tuple)):
    return [str(v) for v in value if str(v).strip()]
  text = str(value).strip()
  if text.startswith("["):
    try:
      return [str(v) for v in json.loads(text)]
    except Exception:
      pass
  return [p.strip() for p in text.replace(",", "\n").split("\n") if p.strip()]


path_list = as_selection_list(path_list)
path_pattern = as_selection_list(path_pattern)

_regex_cache = {}


def _glob_regex(pattern):
  """fnmatch semantics ('*' spans '/', '?' one char), compiled once per call."""
  rx = _regex_cache.get(pattern)
  if rx is None:
    rx = re.compile("^" + "".join(
      "." if c == "?" else ".*" if c == "*" else re.escape(c)
      for c in pattern) + "$")
    _regex_cache[pattern] = rx
  return rx


def is_selected(path):
  """A pattern is a whole path, or a prefix when it ends in '/' or '*'."""
  for pattern in path_list:
    if pattern.endswith("*"):
      if path.startswith(pattern[:-1]):
        return True
    elif pattern.endswith("/"):
      if path.startswith(pattern):
        return True
    elif path == pattern or path.startswith(pattern + "/"):
      return True
  return False


def is_globbed(path):
  """Shell-style glob matched against the path relative to the template."""
  for pattern in path_pattern:
    if pattern.endswith("/"):
      if path.startswith(pattern):
        return True
    elif _glob_regex(pattern).match(path):
      return True
  return False


def is_asked_for(path):
  """Every filter that was passed must accept the path."""
  if path_pattern and not is_globbed(path):
    return False
  if path_list and not is_selected(path):
    return False
  return True


scoped = bool(path_list or path_pattern)

# Writes the ZODB state of the template into the working copy: builds it and
# git-add -N marks whatever is new. Without this a commit records whatever was
# exported last, not what is on the instance.
#
# A full extractBT rewrites every file of the template and deletes everything
# it no longer exports - sweeping away other people's uncommitted files in a
# shared working copy. When the call narrows to a selection, export into a
# temp dir instead and copy only the selected paths over; tracked paths the
# template no longer has are deleted (what a full export would have done),
# untracked files are never touched.
created_list = []
addremove_error = None
tmp_dir = None
if not scoped:
  vcs.extractBT(bt)
else:
  # Scoped export: build, export into a temp dir, copy only the selected paths
  # over, delete selected tracked paths the template no longer has. Life of the
  # temp dir, the byte diffing and all file IO live in the trusted helper - the
  # sandbox forbids open() here - while the selection stays in this body.
  from erp5.component.module.MCPDevHelpers import scopedExport
  tracked = set(p for p in vcs.git("ls-files", "--", ".").splitlines() if p.strip())
  added, modified, removed, created_list = scopedExport(
    bt, vcs.working_copy, tracked, is_asked_for, apply=not dry_run)
if created_list and not dry_run:
  try:
    vcs.addremove(set(created_list), set())
  except Exception, error:
    addremove_error = str(error)
if addremove_error:
  result["warning"] = "git add -N failed for new files %s: %s" % (
    created_list, addremove_error)

# Read the same view of the changes that commit() filters against
# (git diff --raw --relative HEAD .), so what is reported is what gets recorded.
# Paths come out relative to the directory of this template, which is also what
# keeps the commit inside it -- every template here shares one working copy.
# Parsing is by tab, never by column: the git() wrapper strips the whole output
# and would eat the leading status column of the first line.
#
# A scoped dry run wrote nothing, so git has no diff to show: keep the
# content-level diff the scoped export computed instead.
conflicted = []
unparsed = []
if scoped and dry_run:
  # keep the content-level diff the scoped export computed above
  pass
else:
  added = []
  modified = []
  removed = []
  for line in vcs.git("diff", "--raw", "--no-renames", "--relative", "HEAD", ".").splitlines():
    parts = line.split("\t")
    if len(parts) < 2:
      if line.strip():
        unparsed.append(line)
      continue
    meta = parts[0].split()
    if not meta:
      unparsed.append(line)
      continue
    code = meta[-1][:1]
    path = parts[1]
    if code == "A":
      added.append(path)
    elif code == "D":
      removed.append(path)
    elif code == "M":
      modified.append(path)
    elif code == "U":
      conflicted.append(path)
    else:
      unparsed.append(line)

# Belonging to the template is not the same as being yours. A working copy
# that several people and several sessions share carries changes nobody asked
# to record here, and a template-wide commit would sweep them in under
# somebody else's changelog. path_list / path_pattern narrow the commit to
# what was asked for; everything else stays in the working copy and comes
# back in "skipped", so what is left behind is visible rather than assumed.

skipped = []
kept_list = []
for path_group in (added, modified, removed):
  kept = []
  for path in path_group:
    if is_asked_for(path):
      kept.append(path)
    else:
      skipped.append(path)
  kept_list.append(kept)
added, modified, removed = kept_list

result = {
  "business_template": bt_title,
  "bt_id": bt.getId(),
  "branch": vcs.git("rev-parse", "--abbrev-ref", "HEAD").strip(),
  "remote": describe_remote(),
}


def cap(name, full_list):
  """Every list is capped at max_list entries (the bill for a tool result is
  its size times the remaining conversation); counts say what is hidden."""
  result[name + "_count"] = len(full_list)
  if summary_only:
    result[name] = []
  elif max_list is not None and len(full_list) > max_list:
    result[name] = full_list[:max_list]
    result[name + "_more"] = len(full_list) - max_list
  else:
    result[name] = full_list


cap("added", added)
cap("modified", modified)
cap("removed", removed)
if path_list or path_pattern:
  result["skipped_count"] = len(skipped)
  cap("skipped", skipped)
if path_pattern:
  result["path_pattern"] = list(path_pattern)
if path_list:
  result["path_list"] = list(path_list)
cap("unparsed", unparsed)
if conflicted:
  result["conflicted"] = conflicted
  result["status"] = "error"
  result["error"] = "Working copy has conflicts; resolve them first."
  return mcp_ret(result)

if not (added or modified or removed):
  result["status"] = "clean"
  # Nothing new to record is not a reason to leave earlier commits sitting
  # unpushed: a commit and its push are separate asks, and this is how the
  # second one is made on its own -- including right after a commit whose
  # push was rejected, where the same path_list now selects nothing.
  if push and not dry_run:
    do_push(result)
    if result["status"] == "clean" and result.get("pushed"):
      result["status"] = "pushed"
  elif skipped:
    # Changed paths existed but the filter asked for none of them: that is a
    # mistyped filter, and reporting it as clean would read as done. (A
    # push-only call opts out by passing no filter, so skipped stays empty.)
    result["status"] = "error"
    result["error"] = ("path_list/path_pattern matched none of the %s changed "
                       "path(s); nothing was committed." % len(skipped))
  return mcp_ret(result)

if dry_run:
  result["status"] = "dry_run"
  return mcp_ret(result)

# Asked for only once something is actually going to be recorded, so that a
# push-only call does not have to invent a message.
if not changelog.strip():
  result["status"] = "error"
  result["error"] = "A changelog message is required."
  return mcp_ret(result)

revision_before = vcs.getRevision()
request = context.REQUEST
saved_status = request.RESPONSE.getStatus()
try:
  # commit() ends in Base_redirect, which leaves a 302 on the shared RESPONSE.
  # Pushing is done by do_push() rather than by commit(), which reports nothing.
  vcs.commit(changelog, 0, added=added, modified=modified, removed=removed)
finally:
  try:
    request.RESPONSE.setStatus(saved_status)
  except Exception:
    pass

# commit() reports git failures by returning a redirect carrying a status
# message, not by raising, so success is decided on the revision moving.
if vcs.getRevision() == revision_before:
  result["status"] = "error"
  result["error"] = "No commit was created; the working copy is unchanged."
  return mcp_ret(result)
result["status"] = "committed"
result["revision"] = vcs.git("rev-parse", "--short", "HEAD").strip()
if push:
  do_push(result)
return mcp_ret(result)
