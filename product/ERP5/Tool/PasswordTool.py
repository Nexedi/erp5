##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
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

import socket

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, get_request
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from zLOG import LOG, INFO
import time, random, md5
from DateTime import DateTime
from Products.ERP5Type.Message import translateString
from Acquisition import aq_base
from Globals import PersistentMapping

class PasswordTool(BaseTool):
  """
    PasswoordTool is used to allow a user to change its password
  """
  title = 'Password Tool'
  id = 'portal_password'
  meta_type = 'ERP5 Password Tool'
  portal_type = 'Password Tool'
  allowed_types = ()

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainPasswordTool', _dtmldir )


  _expiration_day = 1
  password_request_dict = {}
  
  def __init__(self):
    self.password_request_dict = PersistentMapping()

  def mailPasswordResetRequest(self, user_login=None, REQUEST=None):
    """
    Create a ramdom string and expiration date for request
    """
    if user_login is None:
      user_login = REQUEST["user_login"]

    # check user exists
    user_list = self.portal_catalog.unrestrictedSearchResults(portal_type="Person", reference=user_login)
    if len(user_list) == 0:
      msg = translateString("User ${user} does not exist.",
                            mapping={'user':user_login})
      if REQUEST is not None:
        ret_url = '%s/login_form?portal_status_message=%s' % \
                  (self.getPortalObject().absolute_url(),msg)
        return REQUEST.RESPONSE.redirect( ret_url )
      else:
        return msg

    user = user_list[0].getObject()
    # generate a ramdom string
    random_url = self._generateUUID()
    url = "%s/portal_password/resetPassword?reset_key=%s" %(self.getPortalObject().absolute_url() , random_url)
    # generate expiration date
    expiration_date = DateTime() + self._expiration_day
    
    # XXX before r26093, password_request_dict was initialized by an OOBTree and
    # replaced by a dict on each request, so if it's data structure is not up
    # to date, we update it if needed
    if not isinstance(self.password_request_dict, PersistentMapping):
      LOG('ERP5.PasswordTool', INFO, 'Updating password_request_dict to'
                                     ' PersistentMapping')
      self.password_request_dict = PersistentMapping()
    
    # register request
    self.password_request_dict[random_url] = (user_login, expiration_date)

    # send mail
    subject = "[%s] Reset of your password" %(self.getPortalObject().getTitle())
    message = "\nYou requested to reset your %s account password.\n\n" \
              "Please copy and paste the following link into your browser: \n%s\n\n" \
              "Please note that this link will be valid only one time, until %s.\n" \
              "After this date, or after having used this link, you will have to make " \
              "a new request\n\n" \
              "Thank you" %(self.getPortalObject().getTitle(), url, expiration_date)    
    self.portal_notifications.sendMessage(sender=None, recipient=[user,], subject=subject, message=message)
    if REQUEST is not None:
      msg = translateString("An email has been sent to you.")
      ret_url = '%s/login_form?portal_status_message=%s' % \
                (self.getPortalObject().absolute_url(),msg)
      return REQUEST.RESPONSE.redirect( ret_url )
  

  def _generateUUID(self, args=""):
    """
    Generate a unique id that will be used as url for password
    """
    # this code is based on
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/213761
    # by Carl Free Jr
    # as uuid module is only available in pyhton 2.5
    t = long( time.time() * 1000 )
    r = long( random.random()*100000000000000000L )
    try:
      a = socket.gethostbyname( socket.gethostname() )
    except:
      # if we can't get a network address, just imagine one
      a = random.random()*100000000000000000L
    data = str(t)+' '+str(r)+' '+str(a)+' '+str(args)
    data = md5.md5(data).hexdigest()
    return data


  def resetPassword(self, reset_key=None, REQUEST=None):
    """
    """
    if REQUEST is None:
      REQUEST = get_request()
    user_login, expiration_date = self.password_request_dict.get(reset_key, (None, None))
    if reset_key is None or user_login is None:
      ret_url = '%s/login_form' % self.getPortalObject().absolute_url()
      return REQUEST.RESPONSE.redirect( ret_url )

    # check date
    current_date = DateTime()
    if current_date > expiration_date:
      msg = translateString("Date has expire.")
      ret_url = '%s/login_form?portal_status_message=%s' % \
                (self.getPortalObject().absolute_url(), msg)
      return REQUEST.RESPONSE.redirect( ret_url )
      
    # redirect to form as all is ok
    REQUEST.set("password_key", reset_key)
    return self.reset_password_form(REQUEST=REQUEST)


  def removeExpiredRequests(self, **kw):
    """
    Browse dict and remove expired request
    """
    current_date = DateTime()
    for key, (login, date) in self.password_request_dict.items():
      if date < current_date:
        self.password_request_dict.pop(key)
        
         
  def changeUserPassword(self, user_login, password, password_confirmation, password_key, REQUEST=None):
    """
    Reset the password for a given login    
    """
    # check the key
    register_user_login, expiration_date = self.password_request_dict.get(password_key, (None, None))

    current_date = DateTime()
    msg = None
    if register_user_login is None:
      msg = ""
    elif register_user_login != user_login:
      msg = translateString("Bad login provided.")
    elif current_date > expiration_date:
      msg = translateString("Date has expire.")
    elif not password:
      msg = translateSTring("Password must be entered.")
    elif password != password_confirmation:
      msg = translateString("Passwords do not match.")
    if msg is not None:
      if REQUEST is not None:
        ret_url = '%s/login_form?portal_status_message=%s' % \
                  (self.getPortalObject().absolute_url(), msg)
        return REQUEST.RESPONSE.redirect( ret_url )
      else:
        return msg

    # all is OK, change password and remove it from request dict
    self.password_request_dict.pop(password_key)
    persons = self.acl_users.erp5_users.getUserByLogin(user_login)              
    person = persons[0]
    person._setPasswordByForce(password)
    person.reindexObject()
    if REQUEST is not None:
      msg = translateString("Password changed.")
      ret_url = '%s/login_form?portal_status_message=%s' % \
                (self.getPortalObject().absolute_url(), msg)
      return REQUEST.RESPONSE.redirect( ret_url )
    
InitializeClass(PasswordTool)
