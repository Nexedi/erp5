"""
  Check if a NEO backup works by checking a list of Data Streams against a NEO backup server.
  Check consists of reading same portions of Data Stream from production and clone systems,
  calculate hash and compare it.
  Result of checks is gradually appended to an intermediat Active Process which is later examined for inconsistencies.
"""

threshold = context.ERP5Site_getPreferredThresholdSize()
neo_node_list, neo_cert_list = context.ERP5Site_getNEONodeListAndSSLCertificateLocation()

active_process = context.newActiveProcess()
# so we can distinguish from other Active Processes when needed!
active_process.setTitle("NEO_Clone_check")

# which Data Streams to check ...
data_stream_list = context.ERP5Site_getDataStreamListToCheck()

for data_stream in data_stream_list:
  portal_type = data_stream.getPortalType()
  if ((portal_type == "Data Stream" and data_stream.getSize() > 0) or
     (portal_type == "Data Bucket Stream" and len(data_stream.getKeyList()) > 0)):
    # Data Stream or Data Bucket Stream needs to have data ...
    tag = '%s_consistency_check' %data_stream.getPath()
    data_stream.activate(tag = tag,
                         active_process = active_process.getPath()).DataStream_checkIfNEOCloneBackupIsConsistent(
                                                                    neo_node_list,
                                                                    neo_cert_list,
                                                                    threshold)
