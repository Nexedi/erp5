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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter

from Products.ERP5Type.XMLObject import XMLObject

## # Hand made temp object (rather than ERP5Type generated) because we need
## # it now
class DomainGenerator(XMLObject):
  """
  This class defines a predicate as well as all necessary
  information to generate subdomains.

  Instances are stored in RAM as temp objects

  Generator API - DRAFT
  """
  meta_type='ERP5 Domain Generator'
  portal_type='Domain Generator'
  isPortalContent = ConstantGetter('isPortalContent', value=False)
  icon = None

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected( Permissions.AccessContentsInformation, 'getDomainGeneratorList' )
  def getDomainGeneratorList(self, depth=0, klass=None, script='', parent=None):
    """
    """
    # check parameters
    if script == '':
      return []
    if parent is None:
      parent = self
    if klass is None:
      # in casre we are not a temp object
      klass = self
    # We call a script which builds for us a list DomainGenerator instances
    # We need a way to know how deep we are in the domain generation
    # to prevent infinite recursion
    method = getattr(klass, script)
    return method(depth=depth, parent=parent)