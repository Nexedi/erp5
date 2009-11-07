# -*- coding: utf-8 -*-
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

class IDeliverySolverFactory(Interface):
  """Delivery Solver Factory interface specification

  IDeliverySolverFactory provides methods to create delivery
  solver instances and retrieve metadata related to delivery
  solvers.

  NOTE:
    - wouldn't it be better to use ERP5 document
      classes for delivery solvers.
      (only meaningful reason: use activities to 
      setTotalQuantity on 10,000+ movements)
  """

  def newDeliverySolver(class_name, movement_list):
    """
    Return a new instance of delivery solver of the given
    class_name and with appropriate parameters.

    class_name -- the class name of the delivery solver.
    
    movement_list -- movements to initialise the instance with
    """

  def getDeliverySolverClassNameList():
    """
    Return the list of class names of available delivery solvers.
    """

  def getDeliverySolverTranslatedItemList(class_name_list=None):
    """
    Return the list of class names and translated titles of available
    delivery solvers. Use this method to fill listfields in user interface
    forms.

    class_name_list -- optionnal parameter to filter results only
                       with provided class names
    """

  def getDeliverySolverTranslatedTitle(class_name):
    """
    Return the title to be used in the user interface for the
    delivery solver with given class_name

    class_name -- the class name of a delivery solver
    """

  def getDeliverySolverTranslatedDescription(class_name):
    """
    Return the description to be used in the user interface for the
    delivery solver with given class_name

    class_name -- the class name of a delivery solver
    """