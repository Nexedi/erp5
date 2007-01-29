##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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

from Products.ERP5Type.Constraint import Constraint
from Products.ERP5Type.Message import Message
N_ = lambda msg, **kw: Message('erp5_ui', msg, **kw)
_MARKER = []

class DocumentReferenceConstraint(Constraint):
  """
  This constraint checks if the document has all required coordinates
  (reference, version and language) and if there is no other document with
  the same coordinates.

  Fixing is not implemented on purpose
  (although we could, e.g. by changing version number)
  """

  def checkConsistency(self, object, fixit=0): # XXX-JPS throw is not part of API - Please remove
    """
      Implement here the consistency checker
    """
    # XXX we probably could check reference syntax here, based on regexp in preferences?
    error_list = []

    for req in ('reference', 'language', 'version'):
      if object.getProperty(req) in (None, ''):
        message = '%s is not defined' % req # XXX-JPS Is translation required here with a Message class ?
        error_list.append(self._generateError(object, N_(message)))
    if error_list:
      return error_list
    res = object.portal_catalog(reference=object.getReference(), language=object.getLanguage(),
                                version=object.getVersion(), portal_type=object.getPortalDocumentTypeList())
    res = list(res)
    if len(res) == 2: # this object and another object
      message = 'E: another object %s - %s - %s exists' % (object.getReference(),
                                     object.getLanguage(), object.getVersion())
      error_list.append(self._generateError(object, N_(message)))
    if len(res) > 2: # this is very serious since there are many objects with the same reference
      raise Exception('Fatal error: multiple objects %s - %s - %s exist' % (object.getReference(),
                                                      object.getLanguage(), object.getVersion()))
      #error_list.append(self._generateError(object, N_(s)))
    if error_list:
      return error_list

# vim: filetype=python syntax=python shiftwidth=2 
