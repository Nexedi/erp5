##############################################################################
#
# Copyright (c) 2021 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
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
from erp5.component.mixin.RESTAPIClientConnectorMixin import RESTAPIClientConnectorMixin
from Products.ERP5Type import Permissions
from AccessControl import ModuleSecurityInfo

module_security = ModuleSecurityInfo(__name__)
module_security.declarePublic('TextSynthError')
class TextSynthError(Exception):
  __allow_access_to_unprotected_subobjects__ = {
    'header_dict': 1,
    'body': 1,
    'status': 1,
  }

  def __init__(self, header_dict, body, status):
    super(TextSynthError, self).__init__()
    self.header_dict = header_dict
    self.body = body
    self.status = status

class TextSynthClientConnector(RESTAPIClientConnectorMixin):
  meta_type = 'TextSynth Client Connector'
  security = RESTAPIClientConnectorMixin.security
  TextSynthError = TextSynthError

  def _getAccessToken(self):
    return self.getClientSecret()

  security.declareProtected(Permissions.AccessContentsInformation, 'translate')
  def translate(
    self,
    text,
    target_lang,
    source_lang='auto',
    engine=None,
    timeout=None,
    archive_kw=None,
    archive_document_relative_url=None,
  ):
    """
    Translate a text using a given engine.
    """
    engine = engine if engine else self.getTranslationEngineId()
    return self.call(
      archive_resource=(
        None
        if archive_kw is None else
        'translate'
      ),
      method='GET',
      path='/v1/engines/%s/translate' % engine,
      body={
        'text':text,
        'source_lang':source_lang,
        'target_lang':target_lang,
      },
      timeout=timeout,
      archive_kw=archive_kw,
      archive_document_relative_url=archive_document_relative_url,
    )