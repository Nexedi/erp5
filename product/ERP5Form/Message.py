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
from base64 import b64encode, b64decode

try:
  from string import Template
except ImportError:
  from Products.ERP5Type.patches.string import Template

  
class Message(Persistent):
  """
  This class encapsulates message, mapping and domain for a given message
  """

  security = ClassSecurityInfo()
  security.declareObjectPublic()

  def __init__(self, domain = None, message = '', mapping = None,):
    self.message = message
    self.mapping = mapping
    self.domain = domain

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

  def __str__(self):
    """
    Return the translated message
    """
    context = get_request()['PARENTS'][0]
    translation_service = getGlobalTranslationService()
    if self.domain is None or translation_service is None :
      # Map the translated string with given parameters
      if type(self.mapping) is type({}):
        if isinstance(translated_str, unicode) :
          translated_str = self.message.encode('utf8')
        self.message = Template(self.message).substitute(mapping)
        if not isinstance(self.message, unicode):
          self.message = self.message.decode('utf8')
      return self.message
    else:
      return translation_service.translate(self.domain, self.message, mapping=self.mapping, context=context).encode('utf8')


InitializeClass(Message)
allow_class(Message)
