##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

"""Types Tool Interfaces.
"""

from zope.interface import Attribute
from Products.CMFCore.interfaces import ITypesTool as ICMFCoreTypesTool

class ITypesTool(ICMFCoreTypesTool):
  """ERP5Type's types tool.

  ERP5Type's types tool extends CMF types tool, by looking up requested types
  into registered types providers.
  """
  type_provider_list = Attribute('type_provider_list',
                                 'List of ids of types providers')

# For backward compatibility only
from Products.ERP5Type.interfaces.type_provider import ITypeProvider
