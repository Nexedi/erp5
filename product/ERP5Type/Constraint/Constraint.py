##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
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

class Constraint:
    """
      Default Constraint implementation
    """

    def __init__(self, id=None, description=None, type=None, **constraint_definition):
      """
        Remove unwanted attributes from constraint definition and keep
        them as instance attributes
      """
      self.id = id
      self.description = description
      self.type = type
      self.constraint_definition = constraint_definition

    def edit(self, id=None, description=None, type=None, **constraint_definition):
      """
        Remove unwanted attributes from constraint definition and keep
        them as instance attributes
      """
      if id is not None: self.id = id
      if description is not None: self.description = description
      if type is not None: self.type = type
      self.constraint_definition.update(constraint_definition)

    def checkConsistency(self, object, fixit = 0):
      """
        Default method is to return no error.
      """
      errors = []
      return errors

    def fixConsistency(self, object):
      """
        Default method is to call checkConsistency with
        fixit set to 1
      """
      return self.checkConsistency(object, fixit = 1)

