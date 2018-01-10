# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush Tiwari<ayush.tiwari@nexedi.com>
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
"""
Products.ERP5.interfaces.amount
"""

from zope.interface import Interface

class ICommit(Interface):
  """Commit interface specification
  """

  def getLatestDraftBusinessCommit():
    """
    Returns the lastest draft commit available where the current object
    can be added
    """

class ICommitObject(ICommit):
  """Commit interface specification for ERP5 objects

  ICommitObject defines the set of function which helps in commiting any ERP5
  object to Business Commit. As it concerns with commiting an object, it'll
  always be creating a Business Item in the Business Commit.
  """

  def createBusinessItem(layer=1, sign=1):
    """
    Creates a Business Item object with the path of the current object inside
    the latest Business Commit.

    layer -- Priority of the Business Item
    sign -- Sign of the Business Item

    NOTE: It will still be needed to add the follow_up Business Template to
    properly add the Business Item in Business Commit
    """

class ICommitObjectProperty(ICommit):
  """Commit interface specification for properties of ERP5 objects

  ICommitPropertyObject defines the set of function which helps in commiting any
  ERP5 object property to latest Business Commit. It will always create a
  Business Property Item in the Business Commit.
  """

  def createBusinessPropertyItem(layer=1, sign=1):
    """
    Creates a Business Property Item object with the path of the property for
    the ERP5 object specified.
    """
