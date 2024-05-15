# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

import hashlib
from BTrees.OOBTree import OOBTree
from BTrees.LOBTree import LOBTree
from AccessControl import ClassSecurityInfo
from erp5.component.document.Document import Document
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.module.BTreeData import PersistentString
from erp5.component.module.Log import log
from AccessControl.ZopeGuards import ContainerAssertions


class IndexSequence(object):
  """
  A Sequence base class for data bucket stream following the
  BTree.IReadSequence Interface
  """
  def __init__(self, data_bucket_stream, index_sequence):
    self.data_bucket_stream = data_bucket_stream
    self.index_sequence = index_sequence

  def __getitem__(self, index):
    """Return the value at the given index.
    An IndexError is raised if the index cannot be found.
    """
    raise NotImplementedError

  def __getslice__(self, index1, index2):
    """Return a subsequence from the original sequence.
    The subsequence includes the items from index1 up to, but not
    including, index2.
    """
    sub_index_sequence = self.index_sequence[index1:index2]
    return self.__class__(self.data_bucket_stream, sub_index_sequence)


class IndexKeySequence(IndexSequence):
  """
  A Sequence class to get a value sequence for data bucket stream
  """
  def __getitem__(self, index):
    """Return the value at the given index.
    An IndexError is raised if the index cannot be found.
    """
    bucket_index, bucket_key = self.index_sequence[index]
    return (bucket_index, bucket_key)


class IndexValueSequence(IndexSequence):
  """
  A Sequence class to get a value sequence for data bucket stream
  """
  def __getitem__(self, index):
    """Return the value at the given index.
    An IndexError is raised if the index cannot be found.
    """
    bucket_key = self.index_sequence[index]
    return self.data_bucket_stream.getBucketByKey(bucket_key)


class IndexItemSequence(IndexSequence):
  """
  A Sequence class to get a index item sequence for data bucket stream
  """
  def __getitem__(self, index):
    """Return the value at the given index.
    An IndexError is raised if the index cannot be found.
    """
    bucket_index, bucket_key = self.index_sequence[index]
    return (bucket_index, self.data_bucket_stream.getBucketByKey(bucket_key))


class IndexKeyItemSequence(IndexSequence):
  """
  A Sequence class to get a index key item sequence for data bucket stream
  """
  def __getitem__(self, index):
    """Return the value at the given index.
    An IndexError is raised if the index cannot be found.
    """
    bucket_index, bucket_key = self.index_sequence[index]
    return (bucket_index, bucket_key,
            self.data_bucket_stream.getBucketByKey(bucket_key))


class DataBucketStream(Document):
  """
  Represents data stored in many small files inside a "stream".
  Each file is "addressed" by its key similar to dict.
  """

  meta_type = 'ERP5 Data Bucket Stream'
  portal_type = 'Data Bucket Stream'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.CategoryCore,
    PropertySheet.SortIndex
  )

  def __init__(self, identifier, **kw):
    self.initBucketTree()
    self.initIndexTree()
    Document.__init__(self, identifier, **kw)

  def __len__(self):
    return len(self._tree)

  # XXX: Workaround to fix errors during consistency checks.
  # We should rename the "_tree" attribute add a migration
  # script for existing instances. Then we can remove
  # the following two methods.
  def objectValues(self, *args, **kw):
    return []

  def objectIds(self, *args, **kw):
    return []

  def initBucketTree(self):
    """
      Initialize the Bucket Tree
    """
    self._tree = OOBTree()

  def initIndexTree(self):
    """
      Initialize the Index Tree
    """
    self._long_index_tree = LOBTree()
    
  def getMaxKey(self, key=None):
    """
    Return the maximum key
    """
    try:
      return self._tree.maxKey(key)
    except ValueError:
      return None

  def getMaxIndex(self, index=None):
    """
    Return the maximum index
    """
    try:
      return self._long_index_tree.maxKey(index)
    except ValueError:
      return None

  def getMinKey(self, key=None):
    """
    Return the minimum key
    """
    try:
      return self._tree.minKey(key)
    except ValueError:
      return None

  def getMinIndex(self, index=None):
    """
    Return the minimum key
    """
    try:
      return self._long_index_tree.minKey(index)
    except ValueError:
      return None

  def _getOb(self, identifier, *args, **kw):
    return None

  def getBucketByKey(self, key=None):
    """
      Get one bucket
    """
    persistent_string = self._tree[key]
    v = persistent_string.value
    persistent_string._p_deactivate()  # free memory
    return v

  def getBucketByIndex(self, index=None):
    """
      Get one bucket
    """
    key = self._long_index_tree[index]
    return self.getBucketByKey(key)

  def getKeyByIndex(self, index):
    """
      Get the bucket key by a given index
    """
    return self._long_index_tree[index]
    
  def hasBucketKey(self, key):
    """
      Wether bucket with such key exists
    """
    return key in self._tree

  def hasBucketIndex(self, index):
    """
      Wether bucket with such index exists
    """
    return self._long_index_tree.has_key(index)
    
  def insertBucket(self, key, value):
    """
      Insert one bucket
    """
    try:
      count = self._long_index_tree.maxKey() + 1
    except ValueError:
      count = 0
    except AttributeError:
      pass
    try:
      self._long_index_tree.insert(count, key)
    except AttributeError:
      pass
    value = PersistentString(value)
    is_new_key = self._tree.insert(key, value)
    if not is_new_key:
      self.log("Reingestion of same key")
      self._tree[key] = value
    
  def getBucketKeySequenceByKey(self, start_key=None, stop_key=None,
                   count=None, exclude_start_key=False, exclude_stop_key=False):
    """
      Get a lazy sequence of bucket keys
    """
    sequence = self._tree.keys(min=start_key, max=stop_key,
                               excludemin=exclude_start_key,
                               excludemax=exclude_stop_key)
    if count is None:
      return sequence
    return sequence[:count]
    
  def getBucketKeySequenceByIndex(self, start_index=None, stop_index=None,
              count=None, exclude_start_index=False, exclude_stop_index=False):
    """
      Get a lazy sequence of bucket keys
    """
    sequence = self._long_index_tree.values(min=start_index, max=stop_index,
                                            excludemin=exclude_start_index,
                                            excludemax=exclude_stop_index)
    if count is None:
      return sequence
    return sequence[:count]

  def getBucketIndexKeySequenceByIndex(self, start_index=None, stop_index=None,
              count=None, exclude_start_index=False, exclude_stop_index=False):
    """
      Get a lazy sequence of bucket keys
    """
    sequence = self._long_index_tree.items(min=start_index, max=stop_index,
                                           excludemin=exclude_start_index,
                                           excludemax=exclude_stop_index)
    if count is not None:
      sequence = sequence[:count]
    return IndexKeySequence(self, sequence)

  def getBucketIndexSequenceByIndex(self, start_index=None, stop_index=None,
              count=None, exclude_start_index=False, exclude_stop_index=False):
    """
      Get a lazy sequence of bucket keys
    """
    sequence = self._long_index_tree.keys(min=start_index, max=stop_index,
                                          excludemin=exclude_start_index,
                                          excludemax=exclude_stop_index)
    if count is None:
      return sequence
    return sequence[:count]

  def getBucketValueSequenceByKey(self, start_key=None, stop_key=None,
                  count=None, exclude_start_key=False, exclude_stop_key=False):
    """
      Get a lazy sequence of bucket values
    """
    sequence = self._tree.values(min=start_key, max=stop_key,
                                 excludemin=exclude_start_key,
                                 excludemax=exclude_stop_key)
    if count is None:
      return sequence
    return sequence[:count]

  def getBucketValueSequenceByIndex(self, start_index=None, stop_index=None,
              count=None, exclude_start_index=False, exclude_stop_index=False):
    """
      Get a lazy sequence of bucket values
    """
    sequence = self._long_index_tree.values(min=start_index, max=stop_index,
                                            excludemin=exclude_start_index,
                                            excludemax=exclude_stop_index)
    if count is not None:
      sequence = sequence[:count]
    return IndexValueSequence(self, sequence)
    
  def getBucketKeyItemSequenceByKey(self, start_key=None, stop_key=None,
                   count=None, exclude_start_key=False, exclude_stop_key=False):
    """
      Get a lazy sequence of bucket items
    """
    sequence = self._tree.items(min=start_key, max=stop_key,
                               excludemin=exclude_start_key,
                               excludemax=exclude_stop_key)
    if count is None:
      return sequence
    return sequence[:count]

  def getBucketItemSequence(self, start_key=None, count=None,
                            exclude_start_key=False):
    log('DeprecationWarning: Please use getBucketKeyItemSequenceByKey')
    return self.getBucketKeyItemSequenceByKey(start_key=start_key, count=count,
                                           exclude_start_key=exclude_start_key)
    
  def getBucketIndexItemSequenceByIndex(self, start_index=None, stop_index=None,
              count=None, exclude_start_index=False, exclude_stop_index=False):
    """
      Get a lazy sequence of bucket items
    """
    sequence = self._long_index_tree.items(min=start_index, max=stop_index,
                                           excludemin=exclude_start_index,
                                           excludemax=exclude_stop_index)
    if count is not None:
      sequence = sequence[:count]
    return IndexItemSequence(self, sequence)

  def getBucketIndexKeyItemSequenceByIndex(self, start_index=None,
                                           stop_index=None, count=None,
                                           exclude_start_index=False,
                                           exclude_stop_index=False):
    """
      Get a lazy sequence of bucket items
    """
    sequence = self._long_index_tree.items(min=start_index, max=stop_index,
                                      excludemin=exclude_start_index,
                                      excludemax=exclude_stop_index)
    if count is not None:
      sequence = sequence[:count]
    return IndexKeyItemSequence(self, sequence)
    
  def getItemList(self):
    """
      Return a list of all key, value pairs
    """
    return [item for item in self._tree.items()]
    
  def getKeyList(self):
    """
      Return a list of all keys
    """
    return [key for key in self._tree.keys()]
    
  def getIndexList(self):
    """
      Return a list of all indexes
    """
    return [key for key in self._long_index_tree.keys()]
    
  def getIndexKeyTupleList(self):
    """
      Return a list of all indexes
    """
    return [key for key in self._long_index_tree.items()]
    
  def getMd5sum(self, key):
    """
      Get hexdigest of bucket.
    """
    h = hashlib.md5()
    h.update(self.getBucketByKey(key))
    return h.hexdigest()
    
  def delBucketByKey(self, key):
    """
      Remove the bucket.
    """
    del self._tree[key]
    for index, my_key in list(self.getBucketIndexKeySequenceByIndex()):
      if my_key == key:
        del self._long_index_tree[index]

  def delBucketByIndex(self, index):
    """
      Remove the bucket.
    """
    key = self._long_index_tree[index]
    del self._tree[key]
    del self._long_index_tree[index]

  def rebuildIndexTreeByKeyOrder(self):
    """
        Clear and rebuild the index tree by order of keys
    """
    self.initIndexTree()
    for count, key in enumerate(self.getBucketKeySequenceByKey()):
      self._long_index_tree.insert(count, key)


# Allow iteration over IndexSequence based classes
# in restricted python.
for index_class in (
  IndexSequence,
  IndexKeySequence,
  IndexValueSequence,
  IndexItemSequence,
  IndexKeyItemSequence,
):
  ContainerAssertions[index_class] = 1

# Cleanup
del index_class
