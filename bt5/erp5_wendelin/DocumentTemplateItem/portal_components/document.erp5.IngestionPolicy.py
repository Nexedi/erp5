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
from zExceptions import BadRequest, NotFound
import six
from Products.ERP5Type.Utils import parse_http_header

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
      Unpack data coming from fluentd. Handy alias.
    """
    return self.portal_ingestion_policies.unpack(data)

  security.declarePublic('ingest')
  def ingest(self, **kw):
    """
    Ingest chunk of raw data either from a Sensor or any of DAUs.
    """
    environ = self.REQUEST.environ
    method = environ.pop('REQUEST_METHOD')
    try:
      if method != 'POST':
        raise BadRequest('Only POST request is allowed.')
      #keep old behavior
      if six.PY2:
        if self.REQUEST._file is not None:
          assert not self.REQUEST.form, self.REQUEST.form # Are cgi and HTTPRequest fixed ?
          # Query string was ignored so parse again, faking a GET request.
          # Such POST is legit: https://stackoverflow.com/a/14710450
          self.REQUEST.processInputs()
          self.REQUEST.form['data_chunk'] = self.REQUEST._file.read()
      else:
        if ('data_chunk' in self.REQUEST.form) and self.REQUEST.form['data_chunk']:
          # old fluentd, data is urlencoded and zope have decoded the bytes
          # https://github.com/zopefoundation/Zope/blob/031706db694b310d5b71829b22389c470f9b7a62/src/ZPublisher/HTTPRequest.py#L569-L571
          # re-encode to get the inital bytes
          content_type = self.REQUEST.environ.get('CONTENT_TYPE')
          _, params = parse_http_header(content_type)
          used_charset = params.get('charset', self.REQUEST.charset)
          self.REQUEST.form['data_chunk'] = self.REQUEST.form['data_chunk'].encode(used_charset, errors='surrogateescape')
        else:
          self.REQUEST.form['data_chunk'] = self.REQUEST.get('BODY')

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
    data_operation_script_id =  self.getDataOperationScriptId()
    if data_operation_script_id is None:
      raise NotFound('No data operation script found.')

    data_operation_script = getattr(self, data_operation_script_id, None)
    if data_operation_script is None:
      raise NotFound('No data operation script found.')

    ingestion_operation, parameter_dict = data_operation_script(movement_dict,\
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
