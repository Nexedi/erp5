# -*- coding:utf-8 -*-
##############################################################################
#
# Copyright (C) 2021 Nexedi SA and Contributors.
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

import json

from oic import rndstr
from oic.oauth2.grant import Token
from oic.oic import Client
from oic.oic.message import AuthorizationResponse
from oic.oic.message import RegistrationResponse

from zExceptions import Unauthorized

openid_connect_cache_factory = "openid_connect_server_auth_token_cache_factory"

def _getOpenOpenIdConnector(portal, reference="default"):
  """Returns google client id and secret key.

  Internal function.
  """
  result_list = portal.portal_catalog.unrestrictedSearchResults(
    portal_type="OpenId Connect Connector",
    reference=reference,
    validation_state="validated",
    limit=2,
  )
  assert result_list, "OpenId Connector not found"
  if len(result_list) == 2:
    raise ValueError("Impossible to select one OpenId Connector Please contact support")

  openid_connector = result_list[0].getObject()
  return openid_connector

def unrestrictedSearchOpenIdConnectLogin(self, login, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  return self.getPortalObject().portal_catalog.unrestrictedSearchResults(
    portal_type="OpenId Connect Login",
    reference=login,
    validation_state="validated", limit=1)

def _getOpenOpenIdClientIdAndSecretKey(portal, reference="default"):
  """Returns client id and secret key.

  Internal function.
  """
  openid_connector = _getOpenOpenIdConnector(portal, reference)
  return openid_connector.getUserId(), openid_connector.getPassword()


def _prepareAndReturnClient(portal, openid_connector, reference="default"):
  from oic.utils.authn.client import CLIENT_AUTHN_METHOD

  client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
  issuer = openid_connector.getUrlString()
  client.provider_config(issuer)

  client_metadata = json.loads(openid_connector.getDescription())
  client_metadata["client_id"] = openid_connector.getUserId()
  client_metadata["client_secret"] = openid_connector.getPassword()
  client_reg = RegistrationResponse(**client_metadata)

  client.store_registration_info(client_reg)
  return client


def redirectToOpenIdConnectLoginPage(self, reference="default"):
  portal = self.getPortalObject()
  openid_connector = _getOpenOpenIdConnector(portal, reference)
  client = _prepareAndReturnClient(portal, openid_connector, reference)

  session = {}
  session["state"] = rndstr()
  session["nonce"] = rndstr()
  portal.Base_setBearerToken(session["state"], session, openid_connect_cache_factory)
  args = {
      "client_id": client.client_id,
      "response_type": "code",
      "scope": openid_connector.getScopeList(),
      "nonce": session["nonce"],
      "redirect_uri": client.registration_response["redirect_uris"][0],
      "state": session["state"]
  }

  auth_req = client.construct_AuthorizationRequest(request_args=args)
  login_url = auth_req.request(client.authorization_endpoint)

  return self.REQUEST.RESPONSE.redirect(login_url)

def getAccessTokenFromCode(self, query_string, redirect_uri, reference="default"):
  portal = self.getPortalObject()
  openid_connector = _getOpenOpenIdConnector(portal, reference)
  client = _prepareAndReturnClient(portal, openid_connector, reference)
  aresp = client.parse_response(
    AuthorizationResponse,
    info=query_string,
    sformat="urlencoded"
  )
  args = {
    "redirect_uri": client.registration_response["redirect_uris"][0],
    "grant_type": "authorization_code",
  }
  response = client.do_access_token_request(
    state=aresp["state"],
    request_args=args,
    authn_method="client_secret_basic",
  )
  response = dict(response)
  if 'id_token' in response:
    assert response['id_token'].verify()
    response.pop('id_token')
  return response

def getAccessTokenFromRefreshToken(self, response_dict, reference="default"):
  portal = self.getPortalObject()
  openid_connector = _getOpenOpenIdConnector(portal, reference)
  client = _prepareAndReturnClient(portal, openid_connector, reference)
  args = {
    "redirect_uri": client.registration_response["redirect_uris"][0],
  }
  token = Token(response_dict)
  response = client.do_access_token_refresh(
    token=token,
    request_args=args,
    authn_method="client_secret_basic",
  )
  if 'id_token' in response:
    assert response['id_token'].verify()
  return dict(response)

def getUserEntry(self, token="", reference="default"):
  portal = self.getPortalObject()
  openid_connector = _getOpenOpenIdConnector(portal, reference)
  client = _prepareAndReturnClient(portal, openid_connector, reference)
  result = client.do_user_info_request(token=token, method="GET")
  return dict(result)

