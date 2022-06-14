# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Core.Folder import Folder
from cStringIO import StringIO
import msgpack


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
    """
      Lazy unpack data, usable in restructed environment
      Setting use_list=False uses tuples instead of lists which is faster
    """
    data_file = StringIO(data)
    return (x for x in msgpack.Unpacker(data_file, use_list=use_list))