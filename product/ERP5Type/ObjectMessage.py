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

from Products.ERP5Type.Message import Message
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.Utility import allow_class
from Globals import get_request

class ObjectMessage: 
  """
   Object Message is used for notifications to user.
  """
  def __init__(self, object_relative_url='', message='', **kw):
    
    self.object_relative_url = object_relative_url
    self.message = message
    
    self.__dict__.update(kw)

  def getTranslatedMessage(self):
    """
    Return the message translated
    """
    return Message(domain='erp5_ui', message=self.message)

  def getMessage(self):
    """
    Return the message without translation
    """
    return self.message
                    
  def edit(self, **kw):
    """
    set all parameters
    """ 
    self.__dict__.update(kw)

  def getProperty(self, value):
    """
    A simple getter
    """
    return getattr(self, value, None)

  def getObject(self):
     """
     Get the Object 
     """
     request = get_request()['PARENTS']
     if request is not None:
       for item in request:
         if item.meta_type ==  'ERP5 Site':
           return item.restrictedTraverse(self.object_relative_url)

     return None

allow_class(ObjectMessage)   
