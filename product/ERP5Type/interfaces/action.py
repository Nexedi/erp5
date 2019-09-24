##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
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

from zope.interface import Interface

class IAction(Interface):
  """
  """
  def __getitem__(attr):
    """Return any information independant of the context

    The following keys must have a value:
    - id (string)
    - category (string)
    - priority (numeric)
    """
  def test(ec):
    """Test if the action should be displayed or not for the given context
    """
  def cook(ec):
    """Return a dict with information required to display the action

    The dict must contain the following keys:
    - id (string)
    - name (string)
    - description (string)
    - url (string)
    - icon (string)
    - category (string)
    - priority (numeric)
    """
