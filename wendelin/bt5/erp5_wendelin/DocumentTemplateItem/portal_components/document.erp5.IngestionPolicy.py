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
from zExceptions import BadRequest

class IngestionPolicy(Folder):
  """
  A policy for ingesting raw (usually) data inside ERP5.
  Every Sensor, Data Acquisition Unit or Data Aggregation Unit will be 
  configured to access a different policy.
  Each policy will have a python script which based on input data will find 
  respective Data Supply which itself contains all required information for 
  later ingestion and analytics.
  """
  
  meta_type = 'ERP5 Ingestion Policy'
  portal_type = 'Ingestion Policy'
  
  # Declarative security
  security = ClassSecurityInfo()
  
  def unpack(self, data):
    """
      Unpack data coming from fluentd. Handly alias.
    """
    return self.portal_ingestion_policies.unpack(data)
  
  security.declarePublic('ingest')
  def ingest(self, **kw):
    """
    Ingest chunk of raw data either from a Sensor or any of DAUs.
    """
    if self.REQUEST.method != 'POST':
      raise BadRequest('Only POST request is allowed.')
      
    script_id = self.getScriptId()
    if script_id is not None:
      script = getattr(self, script_id, None)
      if script is not None:
        # leave it all to responsible script who should do real ingestion
        script(**kw)