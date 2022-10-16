from __future__ import print_function
from BTrees.LOBTree import LOBTree
from persistent import Persistent
import itertools
from six.moves import range

# Maximum memory to allocate for sparse-induced padding.
MAX_PADDING_CHUNK = 2 ** 20

class PersistentString(Persistent):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return self.value

  # Save place when storing this data in zodb
  __getstate__ = __str__
  __setstate__ = __init__

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

    buf (string)
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
              len(chunk.value) < self._chunk_size and
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
        tree[key] = chunk = PersistentString('')
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

    Returns string of read data.
    """
    return ''.join(self.iterate(offset, size))

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
          yield '\x00' * padding_chunk
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
    self.write('', offset)

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

if __name__ == '__main__':

  def check(tree, length, read_offset, read_length, data_, keys=None):
    print(list(tree._tree.items()))
    tree_length = len(tree)
    tree_data = tree.read(read_offset, read_length)
    tree_iterator_data = ''.join(tree.iterate(read_offset, read_length))
    assert tree_length == length, tree_length
    assert tree_data == data_, repr(tree_data)
    assert tree_iterator_data == data_, repr(tree_iterator_data)
    if keys is not None:
      tree_keys = list(tree._tree.keys())
      assert tree_keys == keys, tree_keys

  PersistentString.__repr__ = lambda self: repr(self.value)

  data = BTreeData()

  data.write('', 10)
  check(data, 10, 0, 20, '\x00' * 10, [10])

  data.truncate(0)
  check(data, 0, 0, 20, '', [])

  data.write('a', 5)
  check(data, 6, 4, 3, '\x00a', [5])

  data.write('b', 5)
  check(data, 6, 4, 3, '\x00b', [5])

  data.write('0123456', 0)
  check(data, 7, 0, 10, '0123456', [0, 5])
  check(data, 7, 0, 1, '0')
  check(data, 7, 1, 1, '1')
  check(data, 7, 2, 1, '2')
  check(data, 7, 5, 1, '5')
  check(data, 7, 6, 1, '6')

  # Unaligned write, spilling in next existing chunk
  data.write('XY', 4)
  check(data, 7, 0, 10, '0123XY6', [0, 5])
  # Unaligned write, inside existing chunk
  data.write('VW', 1)
  check(data, 7, 0, 10, '0VW3XY6', [0, 5])
  # Empty write inside existing chunk
  data.write('', 4)
  check(data, 7, 0, 10, '0VW3XY6', [0, 5])
  # Aligned write
  data.write('Z', 5)
  check(data, 7, 0, 10, '0VW3XZ6', [0, 5])

  data.write('a', 10)
  data.write('8', 8)
  check(data, 11, 0, 10, '0VW3XZ6\x008\x00', [0, 5, 8, 10])
  check(data, 11, 7, 10, '\x008\x00a')

  data.write('ABCDE', 6)
  check(data, 11, 0, 11, '0VW3XZABCDE', [0, 5, 8, 10])

  data.truncate(7)
  check(data, 7, 0, 7, '0VW3XZA', [0, 5])
  data.truncate(5)
  check(data, 5, 0, 5, '0VW3X', [0])
  data.truncate(3)
  check(data, 3, 0, 3, '0VW', [0])
  data.truncate(0)
  check(data, 0, 0, 0, '', [])

  data.truncate(10)
  check(data, 10, 0, 10, '\x00' * 10, [10])
  data.write('a', 15)
  check(data, 16, 0, 16, '\x00' * 15 + 'a', [15])
  data.write('bc', 9)
  check(data, 16, 0, 16, '\x00' * 9 + 'bc' + '\x00' * 4 + 'a', [9, 15])

  data = BTreeData(chunk_size=4, max_chunk_size=10)
  data.write('01', 0)
  check(data, 2, 0, 10, '01', [0])
  data.write('23', 2)
  check(data, 4, 0, 10, '0123', [0])
  data.write('AB4', 2)
  check(data, 5, 0, 10, '01AB4', [0])
  data.write('C56', 4)
  check(data, 7, 0, 10, '01ABC56', [0])
  data.write('7', 7)
  check(data, 8, 0, 10, '01ABC567', [0, 7])
  data.write('8', 8)
  check(data, 9, 0, 10, '01ABC5678', [0, 7])
  data.write('C', 12)
  check(data, 13, 0, 13, '01ABC5678\x00\x00\x00C', [0, 7, 12])
  data.write('9ABcDEFG', 9)
  check(data, 17, 0, 17, '01ABC56789ABcDEFG', [0, 7, 12])
  for _ in data.defragment():
    pass
  check(data, 17, 0, 17, '01ABC56789ABcDEFG', [0, 10])
  data.write('HIJKL', len(data))
  check(data, 22, 0, 22, '01ABC56789ABcDEFGHIJKL', [0, 10, 17])
  for _ in data.defragment():
    pass
  check(data, 22, 0, 22, '01ABC56789ABcDEFGHIJKL', [0, 10, 20])
  data.write('NOPQRSTUVWXYZ', 23)
  check(data, 36, 0, 36, '01ABC56789ABcDEFGHIJKL\x00NOPQRSTUVWXYZ', [0, 10, 20, 23, 33])
  for _ in data.defragment():
    pass
  check(data, 36, 0, 36, '01ABC56789ABcDEFGHIJKL\x00NOPQRSTUVWXYZ', [0, 10, 20, 23, 33])

  data = BTreeData(max_chunk_size=10)
  for x in range(255):
    data.write('%02x' % x, x * 2)
  check(data, 510, 0, 10, '0001020304', [x * 2 for x in range(255)])
  defragment_generator = data.defragment(batch_size=2)
  defragment_generator.next()
  check(data, 510, 0, 10, '0001020304', [0] + [x * 2 for x in range(2, 255)])
  opaque = defragment_generator.next()
  defragment_generator.close()
  check(data, 510, 0, 10, '0001020304', [0] + [x * 2 for x in range(4, 255)])
  defragment_generator = data.defragment(batch_size=2, resume_at=opaque)
  defragment_generator.next()
  check(data, 510, 0, 10, '0001020304', [0] + [x * 2 for x in range(5, 255)])
  defragment_generator.send(10)
  check(data, 510, 0, 10, '0001020304', [0, 10, 20] + [x * 2 for x in range(13, 255)])
  defragment_generator.next()
  check(data, 510, 0, 10, '0001020304', [0, 10, 20, 30, 40] + [x * 2 for x in range(23, 255)])
  for _ in defragment_generator:
    pass
  check(data, 510, 0, 10, '0001020304', [x * 10 for x in range(51)])
