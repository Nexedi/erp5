##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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

import zope.interface

from Products.PythonScripts.Utility import allow_class
from Products.ERP5Type import interfaces

class ObjectMessage:
  """
  Object Message is used for notifications to user.
  """

  zope.interface.implements( interfaces.IObjectMessage, )

  def __init__(self, object_relative_url='', message='', mapping={}, **kw):
    
    self.object_relative_url = object_relative_url
    self.message = message
    self.mapping = mapping
    
    self.__dict__.update(kw)

  def getTranslatedMessage(self):
    """
    Return the message translated
    """
    from Products.ERP5Type.Message import Message
    return Message(domain='erp5_ui', message=self.message, 
                   mapping=self.mapping)

  getMessage = getTranslatedMessage
                    
  def edit(self, **kw):
    """
    Set all parameters
    """ 
    self.__dict__.update(kw)

  def getProperty(self, value, d=None):
    """
    A simple getter
    """
    return getattr(self, value, d)

  def __getattr__(self, name):
    """
    Wrap the message with the object
    """
    if name.startswith('__') :
      raise AttributeError, name
    else:
      obj = self.getObject()
      if obj is not None:
        return getattr(obj, name)
      else:
        raise AttributeError, name

  def getObject(self):
    """
    Get the Object.
    """
    from Products.ERP5Type.Globals import get_request
    request = get_request()['PARENTS']
    if request is not None:
      for item in request:
        if item.meta_type == 'ERP5 Site':
          return item.unrestrictedTraverse(self.object_relative_url)

    return None

  def __repr__(self):
    repr_str = '<%s object at 0x%x\n ' % (self.__class__.__name__, id(self))
    repr_str += '\n '.join([' %r: %r' % (k, v) \
                           for k, v in self.__dict__.items()])
    repr_str += '>'
    return repr_str

allow_class(ObjectMessage)
