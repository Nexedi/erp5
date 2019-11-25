##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#                                Gabriel Monnerat <gabriel@nexedi.com>
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin

class ScriptConstraint(ConstraintMixin):
  """
    This constraint call one script that should has all logic to check and
    fix consistency
  """
  meta_type = 'ERP5 Script Constraint'
  portal_type = 'Script Constraint'

  def _createConsistencyMessage(self, object_relative_url, message, mapping):
    # XXX If I put in the right place I have TypeError: 'NoneType' object is not callable
    from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
    return ConsistencyMessage(self,
      object_relative_url=object_relative_url,
      message=message,
      mapping=mapping)

  def _checkConsistency(self, obj, fixit=0, **kw):
    """
      Call script to [check|fix]Consistency
    """
    script_id = self.getScriptId()
    if script_id is None:
      raise RuntimeError("Script id not defined")
    method = getattr(obj, script_id, None)
    if method is None:
      raise RuntimeError('Script (%s) not found %s' % (script_id, self))
    object_relative_url = obj.getRelativeUrl()
    createConsistencyMessage = self._createConsistencyMessage
    message_list = []
    for item in method(fixit=fixit, **kw):
      if isinstance(item, (tuple, list)) and len(item) == 2:
        message, mapping = item
      else:
        message = item
        mapping = {}
      message_list.append(createConsistencyMessage(object_relative_url, message, mapping))
    return message_list