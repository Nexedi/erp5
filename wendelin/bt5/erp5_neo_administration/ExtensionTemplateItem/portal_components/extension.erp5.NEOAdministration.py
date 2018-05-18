# -*- coding: utf-8 -*-
"""
 NEO consistency checks code.
"""
from ZODB import DB
from neo.client.Storage import Storage
import hashlib

def DataBucketStream_getChecksumListFromNEONodeListForKey(self, \
                            node_list, \
                            ca_file, \
                            cert_file, \
                            key_file, \
                            key, \
                            threshold):
  """
  Directly connect to NEO backends and check checksums of this Data Bucket Stream for this key.
  """
  checksum_list = []

  # get directly checksum as we have access to data stream over self
  data = self.getBucketByKey(key)
  data = data[:threshold]
  checksum = hashlib.sha256(data).hexdigest()
  checksum_list.append(checksum)

  for node in node_list:
    kw = {'master_nodes': node[0],
          'name':         node[1],
          'ca':           ca_file,
          'cert':         cert_file,
          'key':          key_file}

    # make a direct connection
    stor = Storage(**kw)
    db = DB(stor)
    conn = db.open()
    root = conn.root()
    data_stream_id = self.getId()
    data_stream = root['Application'].erp5.data_stream_module[data_stream_id]
    data = data_stream.getBucketByKey(key)
    data = data[:threshold]
    conn.close()
    db.close()

    checksum = hashlib.sha256(data).hexdigest()
    checksum_list.append(checksum)

  return checksum_list

def DataStream_getChecksumListFromNEONodeListForStartStopOffset(self, \
                            node_list, \
                            ca_file, \
                            cert_file, \
                            key_file, \
                            start_offset, \
                            end_offset):
  """
  Directly connect to NEO backends and check checksums of this Data Stream.
  """
  checksum_list = []

  # get directly checksum as we have access to data stream over self
  chunk_list = self.readChunkList(start_offset, end_offset)
  data = '\n'.join(chunk_list)
  checksum = hashlib.sha256(data).hexdigest()
  checksum_list.append(checksum)

  for node in node_list:
    kw = {'master_nodes': node[0],
          'name':         node[1],
          'ca':           ca_file,
          'cert':         cert_file,
          'key':          key_file}

    # make a direct connection
    stor = Storage(**kw)
    db = DB(stor)
    conn = db.open()
    root = conn.root()
    data_stream_id = self.getId()
    data_stream = root['Application'].erp5.data_stream_module[data_stream_id]
    chunk_list = data_stream.readChunkList(start_offset, end_offset)
    data = '\n'.join(chunk_list)
    conn.close()
    db.close()

    checksum = hashlib.sha256(data).hexdigest()
    checksum_list.append(checksum)

  return checksum_list
