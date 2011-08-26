from persistent import Persistent

class ConflictFreeLog(Persistent):
  """Scalable conflict-free append-only double-linked list
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

  if not hasattr(Persistent, '_p_estimated_size'): # BBB: Zope 2.8
    _p_estimated_size = property(lambda self: len(self._log) * 64)

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
    if old_state.get('_tail_count', 0) == new_state.get('_tail_count', 0):
      i = len(old_state['_log'])
    else:
      i = 0
    saved_state['_log'].extend(new_state['_log'][i:])
    return saved_state
