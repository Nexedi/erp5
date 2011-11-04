# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
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
"""
"""

from zope.interface import Interface

class IMovementCollectionDiff(Interface):
  """Movement Collection Diff interface specification
  
  Documents which implement IMovementCollectionDiff 
  are used to represent the movements which should be
  added, updated or deleted in an IMovementCollection.
  They are usually generated and used by 
  IMovementCollectionUpdater.
  """
  def getDeletableMovementList():
    """
    Returns the list of movements which need 
    to be deleted.
    """

  def addDeletableMovement(movement):
    """
    Add a deletable movement to the diff definition
    """

  def getNewMovementList():
    """
    Returns a list temp movements which represent new
    movements to add to an existing IMovementCollection.
    """

  def addNewMovement(movement):
    """
    Add a new movement to the diff definition
    """

  def getUpdatableMovementList():
    """
    Returns movements which need to be updated, with properties to update
    """

  def addUpdatableMovement(movement, property_dict):
    """
    Add an updatable movement to the diff definition

    property_dict -- properties to update     
    """
