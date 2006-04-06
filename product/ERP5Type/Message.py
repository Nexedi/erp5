##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurélien Calonne <aurel@nexedi.com>
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

from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from Products.PythonScripts.Utility import allow_class
from Products.PageTemplates.GlobalTranslationService import getGlobalTranslationService
from Globals import get_request
from cPickle import dumps, loads

try:
  from string import Template
except ImportError:
  from Products.ERP5Type.patches.string import Template

# API of base64 has changed between python v2.3 and v2.4
import base64
try:
  # python v2.4 API
  b64encode = base64.b64encode
  b64decode = base64.b64decode
except AttributeError:
  # python v2.3 API
  b64encode = base64.encodestring
  b64decode = base64.decodestring



class Message(Persistent):
  """
  This class encapsulates message, mapping and domain for a given message
  """

  security = ClassSecurityInfo()
  security.declareObjectPublic()

  def __init__(self, domain=None, message='',
               mapping=None, default=None):
    self.message = message
    self.mapping = mapping
    self.domain = domain
    if default is None:
      default = message
    self.default = default

  security.declarePublic('dump')
  def dump(self):
    """
    Return a pickle version of the object
    """
    return b64encode(dumps(self, 2))

  security.declarePublic('load')
  def load(self, string):
    """
    Get properties from pickle version
    """
    o = loads(b64decode(string))
    self.message = o.message
    self.domain = o.domain
    self.mapping = o.mapping
    self.default = o.default

  def __str__(self):
    """
    Return the translated message
    """
    request = get_request()
    if request is not None:
      context = request['PARENTS'][0]
      translation_service = getGlobalTranslationService()
    if self.domain is None or request is None or translation_service is None :
      # Map the translated string with given parameters
      if type(self.mapping) is type({}):
        if isinstance(self.message, unicode) :
          self.message = self.message.encode('utf8')
        self.message = Template(self.message).substitute(mapping)
        if not isinstance(self.message, unicode):
          self.message = self.message.decode('utf8')
      return self.message
    else:
      translated_message = translation_service.translate(
                                             self.domain,
                                             self.message,
                                             mapping=self.mapping,
                                             context=context,
                                             default=self.default)
      if translated_message is not None:
        return translated_message.encode('utf8')
      else:
        return self.message

InitializeClass(Message)
allow_class(Message)
