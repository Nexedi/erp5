##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Interface import Interface

class IEntity(Interface):
  """
    Common Interface for Entity objects
  """

  def getDefaultAddress():
    """
      Returns the default address as a text string
    """
    pass

  def getDefaultAddressStreetAddress():
    """
      Returns the default address street as a text string
    """
    pass

  def getDefaultAddressCity():
    """
      Returns the default address city as a text string
    """
    pass

  def getDefaultAddressRegion():
    """
      Returns the default address region as a text string
    """
    pass

  def getDefaultAddressZipCode():
    """
      Returns the default address zip code as a text string
    """
    pass

  def getDefaultTelephone():
    """
      Returns the default telephone as a text string
    """
    pass

  def getDefaultFax():
    """
      Returns the default fax as a text string
    """
    pass

  def getDefaultEmail():
    """
      Returns the default email as a text string
    """
    pass

  def setDefaultAddress(coordinate):
    """
      Updates the default address from a standard text string
    """
    pass

  def setDefaultTelephone(coordinate):
    """
      Updates the default telephone from a standard text string
    """
    pass

  def setDefaultFax(coordinate):
    """
      Updates the default fax from a standard text string
    """
    pass

  def setDefaultEmail(coordinate):
    """
      Updates the default email from a standard text string
    """
    pass

