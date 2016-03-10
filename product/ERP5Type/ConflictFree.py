from persistent import Persistent

class ConflictFreeLog(Persistent):
  """Scalable conflict-free append-only double-linked list

  Wasted ZODB space due to conflicts is roughly proportional to the number of
  clients that continuously add items at the same time.
  """
  _prev = _next = None
  _tail_count = 0
  _bucket_size = 1000

  def __init__(self, items=(), bucket_size=None):
    self._log = list(items)
    if bucket_size:
      assert bucket_size > 0
      self._bucket_size = bucket_size

  def __len__(self):
    return self._tail_count + len(self._log)

  def _maybe_rotate(self):
    if self._p_estimated_size < self._bucket_size:
      self._p_changed = 1
    else:
      tail = self.__class__()
      tail._log = self._log
      prev = self._prev
      if prev is None:
        prev = self
      else:
        assert not self._next._tail_count
        tail._tail_count = self._tail_count
      tail._prev = prev
      prev._next = tail
      self._prev = tail
      tail._next = self
      self._tail_count += len(self._log)
      self._log = []

  def append(self, item):
    if not self._p_changed:
      self._maybe_rotate()
    self._log.append(item)

  def extend(self, items):
    if not self._p_changed:
      self._maybe_rotate()
    self._log.extend(items)

  def __iadd__(self, other):
    self.extend(other)
    return self

  def __iter__(self):
    bucket = self._next
    if bucket is None:
      bucket = self
    while 1:
      for item in bucket._log:
        yield item
      if bucket is self:
        break
      bucket = bucket._next

  def reversed(self):
    bucket = self
    while 1:
      for item in bucket._log[::-1]:
        yield item
      bucket = bucket._prev
      if bucket in (None, self):
        break

  def _p_resolveConflict(self, old_state, saved_state, new_state):
    # May be called for the head and its predecessor.
    old_tail_count = old_state.get('_tail_count', 0)
    d = new_state.get('_tail_count', 0) - old_tail_count
    # Added elements by us:
    added = new_state['_log'][
      # The following computed value is also non-zero
      # if we rotated during a previous conflict resolution.
      len(old_state['_log']) - d
      :]
    if d:
      if old_tail_count == saved_state.get('_tail_count', 0):
        # We are the first one to rotate. Really rotate.
        # Only the head conflicts in this case.
        return dict(new_state, _log=saved_state['_log'][d:] + added)
      # Another node rotated before us. Revert our rotation.
      # Both the head and its predecessor conflict.
    #else:
      # We didn't rotate. Just add our items to saved head.
      # Only the head conflicts.
    saved_state['_log'] += added
    return saved_state
