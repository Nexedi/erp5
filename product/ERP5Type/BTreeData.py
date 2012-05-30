import transaction
from cStringIO import StringIO
from BTrees.LOBTree import LOBTree
from persistent import Persistent

class PersistentString(Persistent):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class BTreeData(Persistent):
    def __init__(self):
        self.tree = LOBTree()

    def write(self, buf, offset):
        # TODO: auto-aggregation of continuous keys when overwriting
#         offset = long(offset)
#         assert not isinstance(offset, long), 'Offset is too big for int ' \
#             'type: %s' % (offset, )
        tree = self.tree
        buf_len = len(buf)
        try:
            lower_key = tree.maxKey(offset)
        except ValueError:
            # No early-enough entry
            key = offset
        else:
            if lower_key < offset:
                value = str(tree[lower_key])
                value_len = len(value)
                if lower_key + value_len > offset:
                    key = lower_key
                    #print 'Overwriting', key + value_len - offset, 'bytes, copying', offset - key, 'bytes'
                    buf = value[:offset - key] + buf
                else:
                    key = offset
            else:
                assert lower_key == offset, (lower_key, offset)
                key = lower_key
        buf_offset = 0
        actual_buf_len = len(buf)
        to_apply = {}
        for next_key in tree.iterkeys(key):
            if buf_offset >= actual_buf_len:
                break
            next_buf_offset = buf_offset + (next_key - key)
            #print 'Offset', offset + buf_offset, 'in key', key, 'with len', next_key - key
            to_apply[key] = PersistentString(buf[buf_offset:next_buf_offset])
            buf_offset = next_buf_offset
            key = next_key
        else:
            to_add = buf[buf_offset:]
            if to_add:
                #print 'Offset', offset + buf_offset, 'in own key with len', len(to_add)
                tree[offset + buf_offset] = PersistentString(to_add)
        for key, value in to_apply.iteritems():
            tree[key] = value
        return buf_len

    def read(self, offset, size):
        #print 'read', hex(offset), hex(size)
        start_offset = offset
#         start_offset = offset = int(offset)
#         assert not isinstance(offset, long), 'Offset is too big for int ' \
#             'type: %s' % (offset, )
        tree = self.tree
        result = StringIO()
        write = result.write
        try:
            key = tree.maxKey(offset)
        except ValueError:
            return ''
        else:
            last_key = key
            iterator = tree.iterkeys(key)
            offset -= key
        written = 0
        for key in iterator:
            #print 'key', hex(key)
            padding = min(size, key - start_offset - written)
            if padding:
                write('\x00' * padding)
                written += padding
                size -= padding
            if size == 0:
                break
            chunk = tree[key]
            to_write = str(chunk)[offset:offset+size]
            chunk._p_deactivate()
            to_write_len = len(to_write)
            write(to_write)
            size -= to_write_len
            written += to_write_len
            offset = 0
            last_key = key
        return result.getvalue()

    def truncate(self, offset):
#         offset = int(offset)
#         assert not isinstance(offset, long), 'Offset is too big for int ' \
#             'type: %s' % (offset, )
        tree = self.tree
        try:
            key = tree.maxKey(offset)
        except ValueError:
            # No key below offset, flush everything.
            tree.clear()
        else:
            value = str(tree[key])
            value_len = offset - key
            if len(value) > value_len:
                tree[key] = PersistentString(value[:value_len])
            minKey = tree.minKey
            while True:
                next_key = minKey(offset)
                if next_key is None:
                    break
                del tree[key]


