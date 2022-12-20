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
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Core.Folder import Folder
from cStringIO import StringIO
import msgpack
from warnings import warn


class IngestionPolicyTool(Folder):
  """
  A tool to manage so called policies for ingest data into ERP5.
  There can be a multiple policies inside it.
  Every Sensor, Data Acquisition Unit or Data Aggregation Unit will be 
  configured to access a different policy.
  Each policy will have a python script which based on input data will find 
  respective 'Data Supply' which itself contains all required information for 
  later ingestion and analytics.

  For example:
    http://erp5_site/portal_ingestion_policies/<INGESTION_POLICY_ID>/ingest
  """
  
  meta_type = 'ERP5 Ingestion Policy Tool'
  portal_type = 'Ingestion Policy Tool'
  
  # Declarative security
  security = ClassSecurityInfo()
  
  def unpack(self, data):
    """
      Unpack data coming from fluentd.
      Usually data is a msgpack instance but it can be plain one as well.
      XXX: use a simple deterministic approach to detect type of data using
      https://github.com/fluent/fluentd/blob/master/lib/fluent/plugin/in_forward.rb#L205
    """
    data_file = StringIO(data)
    msgpack_list = msgpack.Unpacker(data_file)
    # we need pure primitive list so we avoid zope security in restricted 
    # script environment, but we loose lazyness
    return [x for x in msgpack_list]

  def unpack_lazy(self, data, use_list=True):
    warn(
      "Method 'unpack_lazy' is deprecated. Please use 'unpackLazy' instead.",
      DeprecationWarning
    )
    return self.unpackLazy(data, use_list=use_list)

  def unpackLazy(self, data, use_list=True):
    """
      Lazy unpack data, usable in restructed environment
      Setting use_list=False uses tuples instead of lists which is faster
    """
    data_file = StringIO(data)
    return (x for x in msgpack.Unpacker(data_file, use_list=use_list))