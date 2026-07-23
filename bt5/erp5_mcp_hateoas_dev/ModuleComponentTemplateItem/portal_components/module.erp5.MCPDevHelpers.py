# Copyright (C) 2026 Klaus Woelfel <klaus@nexedi.com>
# Trusted helpers for the erp5-inerp5 MCP dev tools.
#
# portal_callables MCP tools run inside the restricted sandbox, which forbids
# os / open / subprocess and most product imports. The functions below live in
# a validated Module Component, i.e. they run unrestricted, and expose the
# small trusted surface the tools need:
# - local file access for `body_file` (plus sha256 verification of writes)
# - a temp dir and byte-accurate file copy for path-scoped BT export
# - raw SQL against a site Z SQL connection
# - activity queue status and a synchronous drain (the ERP5TypeTestCase.tic()
#   algorithm), for instances that have no activity worker
# Everything else - argument validation, shaping, truncation, output - stays
# in the tool bodies where it is readable and auditable.

import hashlib
import os
import shutil
import tempfile
import time

from AccessControl.SecurityInfo import ModuleSecurityInfo
from DateTime import DateTime

# The tools calling into this module run inside the restricted sandbox: without
# a ModuleSecurityInfo the import itself is refused with an opaque
# "import of 'erp5.component.module.erp5_version.MCPDevHelpers' is unauthorized"
# (the module loads fine - AccessControl just does not know it may be imported).
security = ModuleSecurityInfo(__name__)
for name in ('MAX_FILE_BYTES', 'sha256Hex', 'readFile', 'pathExists', 'joinPath',
             'ensureDir', 'writeFile', 'removeFile', 'mkdtemp', 'rmtree',
             'scopedExport', 'exportFileContent',
             'runSQL', 'activityStatus', 'drainActivities', 'abortTransaction',
             'catalogMethodInfo', 'catalogMethodEdit'):
  security.declarePublic(name)

MAX_FILE_BYTES = 4 * 1024 * 1024


def sha256Hex(data):
  if isinstance(data, unicode):
    data = data.encode('utf-8')
  return hashlib.sha256(data).hexdigest()


def readFile(path, max_bytes=MAX_FILE_BYTES):
  """Read a local file as bytes, refusing oversized files."""
  with open(path, 'rb') as f:
    data = f.read(max_bytes + 1)
  if len(data) > max_bytes:
    raise ValueError('file exceeds %d bytes: %s' % (max_bytes, path))
  return data


def pathExists(path):
  return os.path.exists(path)


def joinPath(base, *rest):
  return os.path.join(base, *rest)


def ensureDir(path):
  if path and not os.path.isdir(path):
    os.makedirs(path)


def writeFile(path, data):
  if isinstance(data, unicode):
    data = data.encode('utf-8')
  parent = os.path.dirname(path)
  if parent and not os.path.isdir(parent):
    os.makedirs(parent)
  with open(path, 'wb') as f:
    f.write(data)


def removeFile(path):
  try:
    os.remove(path)
    return True
  except OSError:
    return False


def mkdtemp(prefix='mcp_'):
  return tempfile.mkdtemp(prefix=prefix)


def rmtree(path):
  shutil.rmtree(path, ignore_errors=True)


def scopedExport(bt, workcopy, tracked, is_selected, apply=True):
  """Export a built business template into the working copy, path-scoped.

  Builds the template (like extractBT), exports it into a temp dir, and copies
  only the paths for which is_selected(path) is true into workcopy. Tracked
  paths the template no longer has are deleted (what a full export would have
  done); untracked worktree files are never touched. With apply=False nothing
  is written - the caller gets the content-level diff only, for dry runs.

  Returns (added, modified, removed, created): content-level diffs of the
  selected paths, plus the subset of added that is new in the worktree (only
  meaningful with apply=True; those need git add -N).
  """
  from erp5.component.module.WorkingCopy import BusinessTemplateWorkingCopy
  if bt.getBuildingState() == 'draft':
    bt.edit()
  bt.build(update_revision=False)
  tmp_dir = tempfile.mkdtemp(prefix='erp5_mcp_export_')
  added = []
  modified = []
  removed = []
  created = []
  try:
    bta = BusinessTemplateWorkingCopy(creation=1, path=tmp_dir)
    file_set, _unused = bta.export(bt)
    file_set = set(str(p) for p in file_set)
    tracked = set(str(p) for p in tracked)
    for path in sorted(tracked | file_set):
      if not is_selected(path):
        continue
      tmp_path = os.path.join(tmp_dir, path)
      wc_path = os.path.join(workcopy, path)
      if path in file_set:
        with open(tmp_path, 'rb') as f:
          data = f.read()
        if not os.path.exists(wc_path):
          added.append(path)
          if apply:
            parent = os.path.dirname(wc_path)
            if parent and not os.path.isdir(parent):
              os.makedirs(parent)
            with open(wc_path, 'wb') as f:
              f.write(data)
            created.append(path)
        else:
          with open(wc_path, 'rb') as f:
            old = f.read()
          if old != data:
            modified.append(path)
            if apply:
              with open(wc_path, 'wb') as f:
                f.write(data)
      elif os.path.exists(wc_path) and path in tracked:
        removed.append(path)
        if apply:
          try:
            os.remove(wc_path)
          except OSError:
            pass
  finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
  return added, modified, removed, created


def abortTransaction():
  """Abort the surrounding request transaction.

  Restricted skin scripts and portal_callables tools may not touch the
  transaction module themselves (only transaction.doom is public there), so
  the tools call this helper. Its job: when a tool catches a raised error
  instead of letting it escape to the publisher, the request would otherwise
  commit normally -- persisting everything the failed code already did
  (ERP5-MCP-SESSION-ISSUES-2026-09-25 B3: an errored erp5_skin_call left work
  done before the exception committed). Aborting instead means:
  error => nothing the failing call did is persisted, temp artifacts included.
  """
  import transaction
  transaction.abort()


def runSQL(portal, connection_id, query, max_rows=100):
  """Execute raw SQL on a site connection; returns (columns, rows, affected).

  Uses the underlying ZMySQLDA DB wrapper directly, so SELECTs come back as
  (column names, row tuples) and the write path still registers with the Zope
  transaction (db.query() calls _register() when the connection is TM-aware).
  """
  conn = portal.unrestrictedTraverse(str(connection_id))
  db = conn._v_database_connection
  items, rows = db.query(query, max_rows)
  affected = None
  try:
    affected = db.db.affected_rows()
  except Exception:
    pass
  return [i['name'] for i in items], rows, affected


def activityStatus(portal, include_messages=False, message_limit=20):
  """Summarise the pending activity queue without dumping it."""
  pa = portal.portal_activities
  message_list = pa.getMessageList()
  by_node = {}
  by_method = {}
  oldest = None
  now = DateTime()
  for m in message_list:
    node = getattr(m, 'processing_node', None)
    by_node[node] = by_node.get(node, 0) + 1
    mid = getattr(m, 'method_id', '?')
    by_method[mid] = by_method.get(mid, 0) + 1
    cd = getattr(m, 'creation_date', None)
    if cd is not None and (oldest is None or cd < oldest):
      oldest = cd
  out = {
    'pending': len(message_list),
    'by_processing_node': by_node,
    'by_method_id': by_method,
    'oldest_age_seconds': (
      int((now - oldest) * 86400) if oldest is not None else None),
  }
  if include_messages:
    messages = []
    for m in message_list[:message_limit]:
      messages.append({
        'uid': getattr(m, 'uid', None),
        'method_id': getattr(m, 'method_id', None),
        'path': str(getattr(m, 'object_path', '') or ''),
        'processing_node': getattr(m, 'processing_node', None),
        'retry': getattr(m, 'retry', 0),
        'creation_date': str(getattr(m, 'creation_date', '') or ''),
      })
    out['messages'] = messages
    if len(message_list) > message_limit:
      out['messages_truncated'] = True
  return out


def drainActivities(portal, max_seconds=240, retry_stuck=False,
                    cancel_stuck=False):
  """Process the pending activity queue synchronously, in this process.

  Replicates ERP5TypeTestCase.tic(): commit, then loop process_timer() until
  the queue is empty. Messages stuck in the invoked state (processing_node
  == -2) never recover on their own; with retry_stuck they are re-invoked
  through ActivityTool.manageInvoke, with cancel_stuck they are cancelled
  through ActivityTool.manageCancel - the right answer for messages that can
  never succeed, e.g. immediateReindexObject queued for a portal_callables
  PythonScript. Without either flag they are reported and the drain stops.
  Aborts the surrounding request transaction at the end, like tic() does -
  the processed activities committed their own transactions.
  """
  import transaction
  from Products.CMFActivity.Activity.Queue import VALIDATION_ERROR_DELAY

  pa = portal.portal_activities
  transaction.commit()
  start = time.time()
  result = {'loops': 0, 'retried': [], 'timeout': False, 'stuck': []}
  message_list = pa.getMessageList()
  result['initial_pending'] = len(message_list)
  retry_done = set()
  call_count = 0
  while message_list:
    if time.time() - start > max_seconds:
      result['timeout'] = True
      break
    stuck = [m for m in message_list if getattr(m, 'processing_node', None) == -2]
    if stuck:
      if not (retry_stuck or cancel_stuck):
        result['stuck'] = [{
          'path': str(getattr(m, 'object_path', '') or ''),
          'method_id': getattr(m, 'method_id', ''),
          'uid': getattr(m, 'uid', None),
        } for m in stuck[:20]]
        result['error'] = (
          '%d message(s) are stuck in invoked state (processing_node == -2); '
          'pass retry_stuck=1 to re-invoke them or cancel_stuck=1 to cancel '
          'them' % len(stuck))
        break
      pairs = []
      for m in stuck:
        # manageInvoke/manageCancel split str paths on '/', so hand them the
        # original object_path object (usually already a path tuple).
        raw_path = getattr(m, 'object_path', None)
        key = (str(raw_path or ''), getattr(m, 'method_id', ''))
        if key not in retry_done:
          retry_done.add(key)
          pairs.append((raw_path, key[1], key[0]))
      for raw_path, method_id, display_path in pairs:
        try:
          if cancel_stuck:
            pa.manageCancel(raw_path, method_id)
          else:
            pa.manageInvoke(raw_path, method_id)
          result['retried'].append({
            'path': display_path, 'method_id': method_id,
            'action': 'cancelled' if cancel_stuck else 'invoked'})
        except Exception, e:
          result.setdefault('retry_errors', []).append({
            'path': display_path, 'method_id': method_id, 'error': str(e)})
      if pairs:
        transaction.commit()
        message_list = pa.getMessageList()
        continue
    pa.process_timer(None, None)
    call_count += 1
    result['loops'] = call_count
    if call_count % 10 == 0:
      try:
        pa.timeShift(3 * VALIDATION_ERROR_DELAY)
      except Exception:
        pass
    message_list = pa.getMessageList()
  result['pending'] = len(pa.getMessageList())
  transaction.abort()
  return result


def _catalogEncoding(value):
  """str for Zope APIs: MCP arguments arrive as unicode and str(unicode) with
  non-ascii blows up ('ascii' codec)."""
  if isinstance(value, unicode):
    return value.encode('utf-8')
  return str(value)


def _resolveCatalogMethod(portal, method_id, sql_catalog_id=None):
  """(sql_catalog, method) for a Z SQL Method under portal_catalog.

  The methods live inside portal_catalog/<sql_catalog_id>/<method_id>, NOT on
  the tool: portal_catalog._getOb(method_id) returns nothing, which made
  read-only inspections report every method as MISSING. _getOb is also
  forbidden to restricted scripts, so this helper runs from the trusted
  module (ERP5-MCP-SESSION-ISSUES-2026-09-25 A2/B1).
  """
  ct = portal.portal_catalog
  if sql_catalog_id:
    catalog = ct._getOb(_catalogEncoding(sql_catalog_id))
  else:
    catalog = ct.getSQLCatalog()
  method = catalog._getOb(_catalogEncoding(method_id), None)
  if method is None:
    raise LookupError('SQL method %r not found inside catalog %r (they live at '
                      'portal_catalog/<sql_catalog_id>/<method_id>, not on '
                      'portal_catalog itself)'
                      % (method_id, catalog.getId()))
  return catalog, method


def catalogMethodInfo(portal, method_id, sql_catalog_id=None):
  """JSON-friendly description of one Z SQL Method, for erp5_catalog_method_read."""
  catalog, method = _resolveCatalogMethod(portal, method_id, sql_catalog_id)
  method_id = _catalogEncoding(method_id)
  filter_information = dict(catalog.filter_dict.get(method_id) or {})
  registrations = []
  for property_id in catalog.propertyIds():
    if not property_id.startswith('sql_'):
      continue
    value = catalog.getProperty(property_id)
    if isinstance(value, (list, tuple)) and method_id in [_catalogEncoding(v) for v in value]:
      registrations.append(property_id)
  return {
    'method_id': str(method_id),
    'sql_catalog_id': str(catalog.getId()),
    'title': str(method.title or ''),
    'connection_id': str(method.connection_id),
    'arguments_src': method.arguments_src or '',
    'src': method.src or '',
    'filtered': bool(filter_information.get('filtered')),
    'expression': filter_information.get('expression') or None,
    'expression_cache_key': list(filter_information.get('expression_cache_key') or ()),
    'filter_portal_types': list(filter_information.get('type') or ()),
    'registrations': registrations,
  }


def catalogMethodEdit(portal, method_id, sql_catalog_id=None, title=None,
                      connection_id=None, arguments_src=None, src=None,
                      force_connection=False):
  """Apply one manage_edit to a Z SQL Method and return its post-edit info.

  manage_edit re-parses the arguments into _arg and re-compiles the DTML
  template, so src and arguments_src must be handed over together -- editing
  only one of them through the ZMI-style API would silently desynchronise the
  parsed state from the source the BT exports.
  """
  catalog, method = _resolveCatalogMethod(portal, method_id, sql_catalog_id)
  if connection_id is not None and \
      _catalogEncoding(connection_id) != _catalogEncoding(method.connection_id) and \
      not force_connection:
    raise ValueError('refusing to change connection_id from %r to %r '
                     'without force_connection=true'
                     % (method.connection_id, connection_id))
  new_title = method.title if title is None else _catalogEncoding(title)
  new_connection_id = (method.connection_id if connection_id is None
                       else _catalogEncoding(connection_id))
  new_arguments = (method.arguments_src if arguments_src is None
                   else _catalogEncoding(arguments_src))
  new_src = method.src if src is None else _catalogEncoding(src)
  method.manage_edit(new_title, new_connection_id, new_arguments, new_src)
  return catalogMethodInfo(portal, method_id, sql_catalog_id or catalog.getId())


def exportFileContent(bt, rel_path):
  """Build the template and return the freshly exported content of one file,
  or None when the template no longer exports it. Used to inspect exactly what
  an export would write without touching the working copy."""
  from erp5.component.module.WorkingCopy import BusinessTemplateWorkingCopy
  if bt.getBuildingState() == 'draft':
    bt.edit()
  bt.build(update_revision=False)
  tmp_dir = tempfile.mkdtemp(prefix='erp5_mcp_export_')
  try:
    bta = BusinessTemplateWorkingCopy(creation=1, path=tmp_dir)
    file_set, _unused = bta.export(bt)
    if rel_path in file_set:
      with open(os.path.join(tmp_dir, rel_path), 'rb') as f:
        return f.read().decode('utf-8', 'replace')
    return None
  finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
