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

from Products.ERP5Type.Base import Base
from Products.ERP5Type.Utils import getPath
from zLOG import LOG
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.PythonScripts.Utility import allow_class

class Error:

  # Standard severities
  TRACE   = -300
  DEBUG   = -200
  BLATHER = -100
  INFO    =    0
  PROBLEM =  100
  WARNING =  100
  ERROR   =  200
  PANIC   =  300
  # Marker for getProperty
  _MARKER = None

  def __init__(self,summary='',severity=INFO,detail='',**kw):
    """
    set all parameters
    """
    if kw.has_key('object_path'):
      self.object_path = getPath(kw['object_path'],tuple=1)
      del kw['object_path']
    self.summary = summary
    self.severity = severity
    self.detail = detail
    self.__dict__.update(kw)

  def edit(self,**kw):
    """
    set all parameters
    """
    if kw.has_key('object_path'):
      self.object_path = getPath(kw['object_path'],tuple=1)
      del kw['object_path']
    self.__dict__.update(kw)

  def getProperty(self, key, d=_MARKER, **kw):
    """
    A simple getter
    """
    return getattr(self, key, d)

allow_class(Error)
