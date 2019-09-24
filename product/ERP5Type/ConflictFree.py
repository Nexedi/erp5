import operator
from itertools import imap as map, islice
from persistent import Persistent


class DoublyLinkList(Persistent):

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
    if not self._p_changed:
      if self._p_estimated_size < self._bucket_size:
        self._p_changed = 1
      else:
        self._rotate()

  def _rotate(self):
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
    self._maybe_rotate()
    self._log.append(item)

  def extend(self, items):
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

  def __reversed__(self):
    bucket = self
    while 1:
      for item in bucket._log[::-1]:
        yield item
      bucket = bucket._prev
      if bucket is None or bucket is self:
        break

  def __add__(self, iterable):
    new = self.__class__(self)
    new.extend(iterable)
    return new

  def __eq__(self, other):
    return (type(self) is type(other)
        and len(self) == len(other)
        and all(map(operator.eq, self, other)))

  def __getitem__(self, index):
    if index == -1: # sortcut for common case
      return self._log[-1]
    # TODO: optimize by caching location of previously accessed item
    if isinstance(index, slice):
      count = len(self)
      start, stop, step = index.indices(count)
      if step < 0:
        count -= 1
        return list(islice(reversed(self), count - start, count - stop, -step))
      return list(islice(self, start, stop, step))
    if index < 0:
      start = index + len(self)
      if start < 0:
        raise IndexError(index)
    else:
      start = index
    try:
      return next(islice(self, start, None))
    except StopIteration:
      raise IndexError(index)

class ConflictFreeLog(DoublyLinkList):
  """Scalable conflict-free append-only doubly-linked list

  Wasted ZODB space due to conflicts is roughly proportional to the number of
  clients that continuously add items at the same time.
  """

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
