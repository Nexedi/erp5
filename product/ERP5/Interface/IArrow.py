##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from zope.interface import Interface

class IArrow(Interface):
  """
    The Arrow lists the methods which are available to 
    access all source and destination categories of
    a movement or of a delivery.
  """
  def getSourceArrowBaseCategoryList():
    """
      Returns all categories which are used to define the source
      of this Arrow
    """

  def getDestinationArrowBaseCategoryList():
    """
      Returns all categories which are used to define the destination
      of this Arrow
    """

  def _getSourceArrowList(spec=(), filter=None, portal_type=(), base=0, 
                          keep_default=1, checked_permission=None):
    """
      Returns all categories which define the source of the 
      document (ex. source, source_section, etc.)
    """

  def _getDestinationArrowList(spec=(), filter=None, portal_type=(), base=0, 
                               keep_default=1, checked_permission=None):
    """
      Returns all categories which define the destination of the 
      document (ex. destination, destination_section, etc.)
    """
