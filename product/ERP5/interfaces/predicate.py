# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
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
"""
Products.ERP5.interfaces.predicate
"""

from zope.interface import Interface

class IPredicate(Interface):
  """Predicate document interface specification

  A Predicate allows to make a statement about a document.
  A statement can be related to:

  - the attributes of the document (ex. price >= 3.0)

  - the categories of the document (ex. )

  The Predicate class is an abstract class, which is
  implemented by subclasses.
  """

  def test(context, tested_base_category_list=None):
    """
    A Predicate can be tested on a given context. Parameters can
    passed in order to ignore some conditions:

    tested_base_category_list -- a list of category that we do
        want to test. For example, we might want to test only the
        destination or the source of a predicate.
        (XXX-JPS - is this really needed ? is this appropriate
         naming - probably not)
    """

  def asSQLExpression():
    """
    A Predicate can be rendered as an sql expression. This
    can be useful to create reporting trees based on the
    ZSQLCatalog. This SQL expression is however partial since
    python scripts which are used by the test method of the predicate
    can be converted to SQL. If a python script is defined to
    implement test, results obtained through asSQLExpression
    must be additionnaly tested by invoking test().
    """

  def asQuery():
    """
    A Predicate can be rendered as a set of catalog conditions. This
    can be useful to create reporting trees based on the
    ZSQLCatalog. This condition set is however partial since
    python scripts which are used by the test method of the predicate
    cannot be converted to catalog conditions. If a python script is defined to
    implement test, results obtained through asQuery must be additionnaly
    tested by invoking test().
    """
