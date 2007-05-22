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

from Products.PythonScripts.Utility import allow_class
from Products.ERP5Type.ObjectMessage import ObjectMessage

class ConsistencyMessage(ObjectMessage):
  """
  Consistency Message is used for notifications to user after checkConsistency.
  """
  def __init__(self, constraint, object_relative_url='',
              message='', mapping = {}, **kw):
    """
    init specific variable to constraint
    """
    self.object_relative_url = object_relative_url
    self.message = message
    self.mapping = mapping
    self.description = constraint.description
    self.class_name = constraint.__class__.__name__
    self.__dict__.update(kw)

  def __getitem__(self, key):
    """
    Backward compatibilty with previous tuple
    message returned by Constraint
    """
    if key == 0:
      return self.object_relative_url
    elif key == 1:
      return '%s inconsistency' % self.class_name
    elif key == 2:
      return 104
    elif key in (4, -1):
      return self.description
    else:
      return self.getTranslatedMessage()

  def fix(self):
    """
    Fix constraint
    XXX to  be implemented
    """
    pass

allow_class(ConsistencyMessage)
