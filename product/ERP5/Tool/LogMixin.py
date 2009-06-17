##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Rafael M. Monnerat <rafael@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

# XXX This Mixin is not finished yet. Added as a reference for the
# future implementation which will come.

class LogMixin:
  """
    The idea of this mixin is to try to share all the code related
    to log file access, caching, log filtering and filtering 
    optimisation. 

    The model chosen here is simplistic:
    - one tool per service
    - account parameter is used to select the customer account
    - log_name parameter is used to select the log

    I prefer this way for now so that the code for log access in
    Tools is reduced to the minimum and we do not need to 
    add so many portal types.
  """
  security = ClassSecurityInfo()

  security.declareProtected('getLogFile', Permissions.ManagePortal)
  def getLogFile(self, file_name, account=None):
    """
      Returns the raw log file (as they are)
      Must be overriden
    """
    raise NotImplementedError

  security.declareProtected('getLogFileNameList', Permissions.ManagePortal)
  def getLogFileNameList(self, log_name, account=None,
                        domain=None, user_name=None, 
                        from_line=None, to_line=None,
                        from_date=None, to_date=None ):
    """
      Returns the list of file names for all log files. This 
      is iseful if we use logrotate for example. It is also
      useful to provide some filtering parameters here 
      (ex. to reduce the number of files to parse)
    """
    raise NotImplementedError

  security.declareProtected('getLogNameList', Permissions.ManagePortal)
  def getLogNameList(self, account=None):
    """
      Returns the list of log names.
    """
    raise NotImplementedError

  security.declareProtected('parseLogLine', Permissions.ManagePortal)
  def parseLogLine(self, log_name, log_line ):
    """
      Parses the line and returns a dict
    """
    method = self.getTypeBasedMethod('parseLogLine')
    return method(log_name, log_line)
