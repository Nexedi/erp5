##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from erp5.component.mixin.LoginAccountProviderMixin import LoginAccountProviderMixin
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from webauthn import (
  generate_registration_options,
  options_to_json,
  verify_registration_response,
  generate_authentication_options,
  verify_authentication_response,
)
from webauthn.helpers import base64url_to_bytes, parse_authentication_credential_json, bytes_to_base64url
from webauthn.helpers.structs import (
  PublicKeyCredentialDescriptor,
  UserVerificationRequirement,
  AuthenticatorSelectionCriteria,
)
import json


@zope.interface.implementer(interfaces.INode)
class WebAuthnLogin(XMLObject, LoginAccountProviderMixin):
  """WebAuthnLogin
  """
  meta_type = 'ERP5 WebAuthn Login'
  portal_type = 'WebAuthn Login'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Reference
                    , PropertySheet.WebAuthnLogin
                    , PropertySheet.LoginConstraint
                    )

  security.declareProtected(Permissions.SetOwnPassword, 'generateRegistration')
  def generateRegistration(self, relying_party_id, relying_party_name):
    """
    generateRegistration
    XXX pass as parameter. Beware, a login is only valid for a single domain...
    """
    return options_to_json(generate_registration_options(
      rp_id=relying_party_id,
      rp_name=relying_party_name,
      user_name=self.getReference(),
      # Unique user identifier
      user_id=self.getParentValue().getUserId().encode(),
      # require to touch the nitrokey
      authenticator_selection=AuthenticatorSelectionCriteria(
        user_verification=UserVerificationRequirement.REQUIRED
      ),
    ))

  security.declareProtected(Permissions.SetOwnPassword, 'finishRegistration')
  def finishRegistration(self, challenge, public_key_credential, relying_party_id,
                         http_origin):
    """
    finishRegistration
    # XXX check if challenge must be trusted with hmac?
    """
    # Verify the registration response

    verified_registration = verify_registration_response(
      credential=public_key_credential,
      expected_challenge=base64url_to_bytes(challenge),
      expected_origin=http_origin,
      expected_rp_id=relying_party_id,
    )
    self.edit(**{
      "credential_id_base64url": bytes_to_base64url(verified_registration.credential_id),
      "public_key_base64url": bytes_to_base64url(verified_registration.credential_public_key),
      "sign_count": verified_registration.sign_count,
      "transports": verified_registration.fmt,
    })

  security.declareProtected(Permissions.View, 'generateAuthentication')
  def generateAuthentication(self, relying_party_id):
    """
    generateAuthentication
    """
    return options_to_json(generate_authentication_options(
      rp_id=relying_party_id,
      allow_credentials=[PublicKeyCredentialDescriptor(id=base64url_to_bytes(self.getProperty("credential_id_base64url")))],
      # require to touch the nitrokey
      user_verification=UserVerificationRequirement.REQUIRED,
    ))

  security.declareProtected(Permissions.SetOwnPassword, 'verifyAuthentication')
  def verifyAuthentication(self, challenge, public_key_credential, relying_party_id,
                           http_origin):
    """
    verifyAuthentication
    """
    verified_authentication = verify_authentication_response(
      credential=public_key_credential,
      expected_challenge=base64url_to_bytes(challenge),
      expected_origin=http_origin,
      expected_rp_id=relying_party_id,
      credential_public_key=base64url_to_bytes(self.getProperty("public_key_base64url")),
      credential_current_sign_count=self.getProperty("sign_count"),
    )
    self.edit(sign_count=verified_authentication.new_sign_count)

