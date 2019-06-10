#!//usr/bin/python
# -*- coding: utf-8 -*-
"""
Sample Python script to ingest into a Wendelin instance.
"""

import msgpack
import requests

# configure for your instance
reference = "test-1"
username = "zope"
password = "insecure"
ingestion_policy_url = "http://%s:%s@localhost:20000/erp5/portal_ingestion_policies/test-1/ingest" %(username, password)

data = {"msg": 'Hello World! Zdravej Sviat!'}
payload = msgpack.packb([0, data], use_bin_type=True)

params = {'reference': reference,
          'data_chunk': payload}
headers = {'CONTENT_TYPE': 'application/octet-stream'}

r = requests.post(ingestion_policy_url, 
                  params = params, 
                  headers=headers)

if r.status_code >= 200 and r.status_code<=204:
  print "Successfully uploaded %s bytes to Wendelin." %len(payload)
