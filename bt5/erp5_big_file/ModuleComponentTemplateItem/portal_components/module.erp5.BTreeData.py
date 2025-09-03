from __future__ import print_function
from BTrees.LOBTree import LOBTree
from persistent import Persistent
import itertools
import six

# Maximum memory to allocate for sparse-induced padding.
MAX_PADDING_CHUNK = 2 ** 20

class PersistentBytes(Persistent):
  def __init__(self, value):
    assert isinstance(value, bytes)
    self.value = value

  def __bytes__(self):
    return self.value
  if six.PY2:
    __str__ = __bytes__

  # Save place when storing this data in zodb
  __getstate__ = __bytes__
  __setstate__ = __init__

PersistentString = PersistentBytes  # BBB compatibility with old name instances that might be saved in ZODB


negative_offset_error = ValueError('Negative offset')

class BTreeData(Persistent):
  """
  In-ZODB (non-BLOB) storage of arbitrary binary data.

  File is managed as chunks, each with a starting offset. Chunks are
  individually persistent (so they are loaded individually when accessed),
  and organised in a BTree (so access to any part of the file is in
  O=log(N)).

  Each call to write() creates a new chunk, so the number and size of chunks
  is (and must be) controled outside this class.

  It supports sparse files, ie writing one byte at 10M offset will not use
  10MB on disk. Sparse bytes read as 0x00 (NULL-bytes).
  """
  _chunk_size = None
  _max_chunk_size = None

  @property
  def chunk_size(self):
    """Aggregate consecutive writes up to this size."""
    return self._chunk_size

  @chunk_size.setter
  def chunk_size(self, value):
    if value is not None and (value <= 0 or int(value) != value):
      raise ValueError('Invalid chunk_size')
    self._chunk_size = value

  @property
  def max_chunk_size(self):
    """Prevent chunks from exceeding this size."""
    return self._max_chunk_size

  @max_chunk_size.setter
  def max_chunk_size(self, value):
    if value is not None and (value <= 0 or int(value) != value):
      raise ValueError('Invalid max chunk_size')
    self._max_chunk_size = value

  def __init__(self, chunk_size=None, max_chunk_size=None):
    """
    chunk_size (int, None)
      If non-None, aggregate consecutive writes up to this size.
      Overlaping or larger writes may exceed this size, though.
    max_chunk_size (int, None)
      If non-None, prevent chunks from exceeding this size.
    """
    self._tree = LOBTree()
    self.chunk_size = chunk_size
    self.max_chunk_size = max_chunk_size

  def __len__(self):
    """
    Return the position of last data chunk in file.
    Does not tell how many bytes are actually used.
    """
    tree = self._tree
    try:
      result = tree.maxKey()
    except ValueError:
      return 0
    return result + len(tree[result].value)

  def write(self, buf, offset):
    """
    Create a new chunk at given offset, with given data.

    buf (bytes)
     Data to write
    offset (int)
     Offset of first data byte.
    """
    # TODO: auto-aggregation of continuous keys when overwriting
    if offset < 0:
      raise negative_offset_error
    tree = self._tree
    key = offset
    try:
      lower_key = tree.maxKey(offset)
    except ValueError:
      pass
    else:
      # Reuse data from an existing and overlapping entry, if any.
      # Avoids fragmenting the file when overwriting with unaligned
      # writes.
      if lower_key < offset:
        chunk = tree[lower_key]
        chunk_end = lower_key + len(chunk.value)
        if chunk_end > offset or (
              len(chunk.value) < (self._chunk_size or 0) and
              chunk_end == offset
            ):
          key = lower_key
          buf = chunk.value[:offset - key] + buf
    try:
      tree.minKey(len(buf) + offset)
    except ValueError:
      try:
        eof = tree.maxKey()
      except ValueError:
        pass
      else:
        if not tree[eof].value:
          del tree[eof]
    max_to_write_len = self._max_chunk_size or float('inf')
    while buf or offset > len(self):
      try:
        next_key = tree.minKey(key + 1)
      except ValueError:
        to_write_len = len(buf)
        next_key = None
      else:
        to_write_len = min(len(buf), next_key - key)
      try:
        chunk = tree[key]
      except KeyError:
        tree[key] = chunk = PersistentBytes(b'')
      entry_size = len(chunk.value)
      if entry_size < to_write_len:
        to_write_len = min(to_write_len, max_to_write_len)
      to_write = buf[:to_write_len]
      buf = buf[to_write_len:]
      if to_write_len < entry_size:
        assert not buf, (key, to_write_len, entry_size, repr(buf))
        to_write += chunk.value[to_write_len:]
      chunk.value = to_write
      key = next_key or key + to_write_len

  def read(self, offset, size):
    """
    Read data back from object.

    offset (int)
     Offset of first byte to read.
    size (int)
     Number of bytes to read.

    Returns bytes of read data.
    """
    return b''.join(self.iterate(offset, size))

  def iterate(self, offset=0, size=None):
    """
    Return file data in storage-efficient chunks.

    offset (int)
     Offset of first byte to read.
    size (int, None)
     Number of bytes to read.
     If None, the whole file is read.

    Yields data chunks as they are read from storage (or locally generated,
    when padding over sparse area).
    """
    if offset < 0:
      raise negative_offset_error
    tree = self._tree
    try:
      key = tree.maxKey(offset)
    except ValueError:
      key = offset
    # (supposedly) marginal optimisations possible:
    # - use key found by maxKey
    # - avoid loading last key if its past the end of read request
    # Would simlify the loop, but might duplicate code... And CPU is not
    # expected to be the bottleneck here.
    if size is None:
      size = len(self) - offset
    next_byte = offset
    for key in tree.iterkeys(key):
      padding = min(size, key - next_byte)
      if padding > 0:
        next_byte += padding
        size -= padding
        chunk_offset = 0
        while padding:
          padding_chunk = min(padding, MAX_PADDING_CHUNK)
          padding -= padding_chunk
          yield b'\x00' * padding_chunk
      else:
        chunk_offset = next_byte - key
      if size == 0:
        break
      chunk = tree[key]
      to_write = chunk.value[chunk_offset:chunk_offset + size]
      # Free memory used by chunk. Helps avoiding thrashing connection
      # cache by discarding chunks earlier.
      chunk._p_deactivate()
      to_write_len = len(to_write)
      size -= to_write_len
      next_byte += to_write_len
      yield to_write

  def truncate(self, offset):
    """
    Truncate data at given offset.

    offset (int)
     Offet of the first byte to discard.
    """
    if offset < 0:
      raise negative_offset_error
    tree = self._tree
    try:
      key = tree.maxKey(offset)
    except ValueError:
      tree.clear()
    else:
      chunk = tree[key]
      chunk_len = len(chunk.value)
      value_len = offset - key
      if chunk_len > value_len:
        chunk.value = chunk.value[:value_len]
      minKey = tree.minKey
      # It is not possible to drop keys as we iterate when using
      # iterkeys, so call minKey repeatedly.
      while True:
        try:
          key = minKey(offset)
        except ValueError:
          break
        del tree[key]
    self.write(b'', offset)

  # XXX: Various batch_size values need to be benchmarked, and a saner
  # default is likely to be applied.
  def defragment(self, batch_size=100, resume_at=None):
    """
    Merge contiguous chunks up to max_chunk_size.

    This method is a generator,  allowing caller to define a stop condition
    (time, number of calls, ...). Yield value is an opaque, small and
    serialisable value which only use is to be passed to resume_at
    parameter.

    batch_size (int)
      Yield every this many internal operations. Allows trading overhead
      for precision. This value may be adjusted on-the-fly by giving the
      new value as parameter of the "send" method on generator (see
      Python doc on generators).

    resume_at (opaque)
      If provided, resume interrupted processing at that point.
    """
    chunk_size = self._max_chunk_size
    key = resume_at or 0
    tree = self._tree
    for iteration in itertools.count(1):
      try:
        key = tree.minKey(key)
      except ValueError:
        return
      if iteration % batch_size == 0:
        new_batch_size = yield key
        if new_batch_size:
          batch_size = new_batch_size
      chunk = tree[key]
      chunk_len = len(chunk.value)
      remainder = chunk_size - chunk_len
      if remainder <= 0:
        # Current entry is large enough, go to next one.
        key += 1
        continue
      end_offset = key + chunk_len
      try:
        next_key = tree.minKey(key + 1)
      except ValueError:
        # No next entry, defrag is over.
        return
      if next_key != end_offset:
        # There is a hole between current entry end and next one, do
        # not concatenate and move on with next entry.
        assert next_key > end_offset, (key, chunk_len, next_key)
        key = next_key
        continue
      next_chunk = tree[next_key]
      next_chunk_len = len(next_chunk.value)
      if next_chunk_len >= chunk_size:
        # Next entry is larger than target size, do not concatenate and
        # go to the entry after that.
        key = next_key + 1
        continue
      # Concatenate current entry and next one.
      chunk.value += next_chunk.value[:remainder]
      del tree[next_key]
      if next_chunk_len > remainder:
        key = next_key + remainder
        # Concatenation result is larger than target size, split into
        # a new entry.
        next_chunk.value = next_chunk.value[remainder:]
        tree[key] = next_chunk
