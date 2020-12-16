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

class IReferenceable(Interface):
  """
  Referenceable interface specification

  Documents which implement IReferenceable can be implicitely related
  to other documents through the reference properties present in their
  content.
  """

  def getSearchableReferenceList():
    """
    Returns a list of dictionaries which represent the
    reference expressions found in the current document.

    Example of result:
      [('P-ERP5-Trade.Design-001-en',
            {'version': '001',
             'reference': 'P-ERP5-Trade.Design',
             'language': 'en'})
      ]
    """

  def getImplicitSuccessorValueList():
    """
    Returns all documents which the current document is referencing
    by analysing the document content and finding all references,
    for instance by calling getSearchableReferenceList.
    """

  def getImplicitPredecessorValueList():
    """
    Returns all documents which content contains a reference
    to the current document.
    """
