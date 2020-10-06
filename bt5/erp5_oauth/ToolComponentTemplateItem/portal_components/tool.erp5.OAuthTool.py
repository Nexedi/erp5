##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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

from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool

class OAuthTool(BaseTool):
  """
    OAuthTool is used to allow API authentification
  """
  title = 'OAuths'
  id = 'portal_oauth'
  meta_type = 'ERP5 OAuth Tool'
  portal_type = 'OAuth Tool'
  allowed_types = ()

  def __setstate__(self, value):
    """
    Delete object() attributes which has never been used and whose classes
    code has been deleted and dummy classes kept only to allow unpickle of
    portal_oauth which happens before __setstate__() is called...
    """
    BaseTool.__setstate__(self, value)
    is_already_migrated = True
    for attribute_name in ('consumer', 'my_access_token', 'my_request_token', 'signature_methods'):
      try:
        delattr(self, attribute_name)
        is_already_migrated = False
      except AttributeError:
        pass
    if not is_already_migrated:
      # str attributes
      for attribute_name in ('verifier', 'nonce'):
        try:
          delattr(self, attribute_name)
        except AttributeError:
          pass

InitializeClass(OAuthTool)

import sys
sys.modules['Products.ERP5TioSafe.Tool.OAuthTool'] = sys.modules[__name__]
class DummyClassForUnpickle(object):
  def __init__(self, *_, **__):
    pass
OAuthToken = DummyClassForUnpickle
OAuthConsumer = DummyClassForUnpickle
OAuthSignatureMethod = DummyClassForUnpickle
OAuthSignatureMethod_HMAC_SHA1 = DummyClassForUnpickle
OAuthSignatureMethod_PLAINTEXT = DummyClassForUnpickle