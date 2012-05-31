from BTrees.LOBTree import LOBTree
from persistent import Persistent

class PersistentString(Persistent):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

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
    def __init__(self):
        self._tree = LOBTree()

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
                value_len = len(chunk.value)
                if lower_key + value_len > offset:
                    key = lower_key
                    buf = chunk.value[:offset - key] + buf
        while buf:
            try:
                next_key = tree.minKey(key + 1)
            except ValueError:
                to_write_len = len(buf)
                next_key = None
            else:
                to_write_len = next_key - key
            try:
                chunk = tree[key]
            except KeyError:
                tree[key] = chunk = PersistentString('')
            entry_size = len(chunk.value)
            to_write = buf[:to_write_len]
            buf = buf[to_write_len:]
            if to_write_len < entry_size:
                assert not buf, (key, to_write_len, entry_size)
                to_write += chunk.value[to_write_len:]
            chunk.value = to_write
            key = next_key

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
                write('\x00' * padding)
                next_byte += padding
                size -= padding
                chunk_offset = 0
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
                next_key = minKey(offset)
                if next_key is None:
                    break
                del tree[key]

if __name__ == '__main__':

    def check(tree, length, read_offset, read_length, data, keys=None):
        tree_length = len(tree)
        tree_data = tree.read(read_offset, read_length)
        tree_iterator_data = ''.join(tree.iterate(read_offset, read_length))
        assert tree_length == length, tree_length
        assert tree_data == data, repr(tree_data)
        assert tree_iterator_data == data, repr(tree_iterator_data)
        if keys is not None:
            tree_keys = list(tree._tree.keys())
            assert tree_keys == keys, tree_keys

    data = BTreeData()

    data.write('', 10)
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

    data.write('XY', 4)
    check(data, 7, 0, 10, '0123XY6', [0, 5])

    data.write('a', 10)
    data.write('8', 8)
    check(data, 11, 0, 10, '0123XY6\x008\x00', [0, 5, 8, 10])
    check(data, 11, 7, 10, '\x008\x00a')

    data.write('ABCDE', 6)
    check(data, 11, 0, 11, '0123XYABCDE', [0, 5, 8, 10])

