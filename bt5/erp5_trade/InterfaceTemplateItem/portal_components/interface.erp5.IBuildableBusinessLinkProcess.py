# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
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

class IBuildableBusinessLinkProcess(Interface):
  """Buildable Business Link Process interface specification

  IBuildableBusinessLinkProcess defines an API to build
  simulation movements related to business link in the context
  of a given explanation.
  """

  def getBuildableBusinessLinkValueList(explanation):
    """Returns the list of Business Link which are buildable
    by taking into account trade state dependencies between
    Business Link.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def getPartiallyBuildableBusinessLinkValueList(explanation):
    """Returns the list of Business Link which are partially buildable
    by taking into account trade state dependencies between
    Business Link.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree
    """

  def isBusinessLinkBuildable(explanation, business_link):
    """Returns True if any of the related Simulation Movement
    is buildable and if the predecessor trade state is completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """

  def isBusinessPatPartiallyBuildable(explanation, business_link):
    """Returns True if any of the related Simulation Movement
    is buildable and if the predecessor trade state is partially completed.

    explanation -- an Order, Order Line, Delivery or Delivery Line or
                   Applied Rule which implicitely defines a simulation subtree

    business_link -- a Business Link document
    """

  def isBuildable(explanation):
    """Returns True is this business process has at least one
    Business Link which is buildable
    """

  def isPartiallyBuildable(explanation):
    """Returns True is this business process has at least one
    Business Link which is partially buildable
    """
