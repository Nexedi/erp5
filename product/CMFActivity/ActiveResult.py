##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from builtins import object
from Products.ERP5Type.Utils import getPath
from zLOG import LOG, INFO
from Products.PythonScripts.Utility import allow_class

class ActiveResult(object):
  """
    Encapsulates the result of deferred activity.
    This class is used by processes to store results
    (and eventually, errors)
  """

  def __init__(self, summary='', severity=INFO, detail='', **kw):
    """
    set all parameters
    """
    self.summary = summary
    self.severity = severity
    self.detail = detail
    self.edit(**kw)

  def edit(self,**kw):
    """
    set all parameters
    """
    if 'object_path' in kw:
      self.object_path = getPath(kw.pop('object_path'), tuple=1)
    self.__dict__.update(kw)

  def getProperty(self, value, d=None):
    """
    A simple getter
    """
    return getattr(self,value,d)

  def getResult(self):
    """
    Returns the result
    """
    return self.result

  def isResult(self):
    """
    Tells if the result is a result or an error
    """
    return self.severity <= INFO

  def isError(self):
    """
    Tells if the result is a result or an error
    """
    return self.severity > INFO

  def __str__(self):
    """
    String representation of this active result
    """
    return "<%s at %s\n%s - %s\n%s>" % (
        self.__class__, id(self), self.severity, self.summary, self.detail)

allow_class(ActiveResult)
