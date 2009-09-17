##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from base64 import b64encode, b64decode

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

  def translate(self):
    """
    Return the translated message. If the original is a string object,
    the return value is a string object. If it is a unicode object,
    the return value is a unicode object.
    """
    request = get_request()
    if request is not None:
      context = request['PARENTS'][0]
      translation_service = getGlobalTranslationService()

    message = self.message
    if self.domain is None or request is None or translation_service is None :
      # Map the translated string with given parameters
      if type(self.mapping) is type({}):
        if isinstance(message, unicode) :
          message = message.encode('utf-8')
        message = Template(message).substitute(self.mapping)
    else:
      translated_message = translation_service.translate(
                                             self.domain,
                                             self.message,
                                             mapping=self.mapping,
                                             context=context,
                                             default=self.default)
      if translated_message is not None:
        message = translated_message

    if isinstance(self.message, str) and isinstance(message, unicode):
      message = message.encode('utf-8')
    elif isinstance(self.message, unicode) and isinstance(message, str):
      message = message.decode('utf-8')

    return message

  def __str__(self):
    """
    Return the translated message as a string object.
    """
    message = self.translate()
    if isinstance(message, unicode):
      message = message.encode('utf-8')
    return message

  def __unicode__(self):
    """
    Return the translated message as a unicode object.
    """
    message = self.translate()
    if isinstance(message, str):
      message = message.decode('utf-8')
    return message

  def __len__(self):
    return len(str(self))

  def __getitem__(self, index):
    return str(self)[index]

  def __getslice__(self, i, j):
    return str(self)[i:j]

InitializeClass(Message)
allow_class(Message)


def translateString(message, **kw):
  return Message(domain='erp5_ui', message=message, **kw)
