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

class DocumentCoordinatesConstraint(Constraint):
  """
  We check if the document has all required coordinates (reference,
  version and language) and that it there is no other doc with
  the same coordinates
  we do not fix (although we could, e.g. change version number)
  """

  def checkConsistency(self, o, fixit=0, throw=False):
    """Implement here the consistency checker
    """
    # XXX we probably could check reference syntax here, based on regexp in preferences?
    errors = []

    for req in ('reference', 'language', 'version'):
      if o.getProperty(req) is None or o.getProperty(req)=='':
        s='%s is None  ' % req
        errors.append(self._generateError(o, N_(s)))
    if errors:
      if throw:
        raise Exception(str(errors))
      return errors
    res=o.portal_catalog(reference=o.getReference(),language=o.getLanguage(),version=o.getVersion(),portal_type=o.getPortalDocumentTypeList())
    res=list(res)
    if len(res)==2: # this and the other one
      s='E: another object %s - %s - %s exists' % (o.getReference(),o.getLanguage(),o.getVersion())
      errors.append(self._generateError(o, N_(s)))
    if len(res)>2: # this is very serious
      raise Exception('Fatal error: multiple objects %s - %s - %s exist' % (o.getReference(),o.getLanguage(),o.getVersion()))
      #errors.append(self._generateError(o, N_(s)))
    if hasattr(o,'Document_additionalConsistencyCheck'):
      e=o.Document_additionalConsistencyCheck()
      if e is not None and e!='':
        errors.append(self._generateError(o, N_(e)))
    if errors and throw:
      raise Exception(str(errors))
    return errors


# vim: filetype=python syntax=python shiftwidth=2 
