"""
  Check replication of Data Stream's or Data Bucket Stream's content amongst NEO clones.
"""
import random

portal_type = context.getPortalType()
if portal_type == 'Data Stream':
  # sometimes we have HUGE streams so we need to check some randomly generated
  # portion of a Data Stream
  max_stop_offset = context.getSize()
  start_offset = int(random.random() * max_stop_offset)
  stop_offset = start_offset + threshold
  if stop_offset > max_stop_offset:
    stop_offset = max_stop_offset
  checksum_list = context.DataStream_getChecksumListFromNEONodeListForStartStopOffset(
                            neo_node_list,
                            neo_cert_list[0],
                            neo_cert_list[1],
                            neo_cert_list[2],
                            start_offset,
                            stop_offset)
elif portal_type == 'Data Bucket Stream':
  # choose a random bucket key as raw data source
  key_list = context.getKeyList()
  # choose random key
  key = random.choice(key_list)
  checksum_list = context.DataBucketStream_getChecksumListFromNEONodeListForKey(
                            neo_node_list,
                            neo_cert_list[0],
                            neo_cert_list[1],
                            neo_cert_list[2],
                            key,
                            threshold)

if len(set(checksum_list)) > 1:
  # one of checksums didn't match
  print "PROBLEM:", context.getRelativeUrl(), checksum_list
else:
  print "OK:", context.getRelativeUrl(), checksum_list

return printed
