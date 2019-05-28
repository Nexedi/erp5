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
from zExceptions import BadRequest, NotFound

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
  def ingest(self, REQUEST, **kw):
    """
    Ingest chunk of raw data either from a Sensor or any of DAUs.
    """
    environ = REQUEST.environ
    method = environ.pop('REQUEST_METHOD')
    try:
      if method != 'POST':
        raise BadRequest('Only POST request is allowed.')
      if REQUEST._file is not None:
        assert not REQUEST.form, REQUEST.form # Are cgi and HTTPRequest fixed ?
        # Query string was ignored so parse again, faking a GET request.
        # Such POST is legit: https://stackoverflow.com/a/14710450
        REQUEST.processInputs()
        REQUEST.form['data_chunk'] = REQUEST._file.read()
    finally:
      environ['REQUEST_METHOD'] = method
      
    tag_parsing_script_id = self.getScriptId()
    
    if tag_parsing_script_id is None:
      raise NotFound('No tag parsing script found.')

    tag_parsing_script = getattr(self, tag_parsing_script_id, None)
    if tag_parsing_script is None:
      raise NotFound('No tag parsing script found.')
      
    # XXX Compatibility with old ingestion. Must be dropped before merging
    # with wendelin master
    if tag_parsing_script_id == "ERP5Site_handleDefaultFluentdIngestion":
      return tag_parsing_script(**kw)
    
    reference = self.REQUEST.get('reference')
    data_chunk = self.REQUEST.get('data_chunk')  

    # the script parses the fluentd tag (reference) and returns a dictionary
    # which describes the ingestion movement. Then we use this dictionary to
    # search  for an existing movement and if we do not find one, we create
    # a new one.
    movement_dict = tag_parsing_script(reference)
    if not movement_dict:
    # unsuccessfull parsing log and do not process
      self.log("Bad tag: %s" %reference)
      return

    # to simplyfy the catalog query, at the moment we assume that aggregate
    # and resource are defined on Data Ingestion Line and the rest is
    # defined on Data Ingestion. This assumption should be dropped later and
    # simulation be used instead.
    ingestion_operation, parameter_dict = \
      self.IngestionPolicy_getIngestionOperationAndParameterDict(movement_dict,
                                                                 reference)
    if ingestion_operation is None:
      raise NotFound('No ingestion operation found.')

    ingestion_script_id = ingestion_operation.getScriptId()
    if ingestion_script_id is None:
      raise NotFound('No ingestion operation script id defined.')
    
    ingestion_script = getattr(self, ingestion_script_id, None)
    if ingestion_script is None:
      raise NotFound('No such ingestion script found: %s' %ingestion_script_id)
    
    ingestion_script(data_chunk=data_chunk, **parameter_dict)