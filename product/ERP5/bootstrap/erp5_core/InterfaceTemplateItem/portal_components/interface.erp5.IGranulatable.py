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

class IGranulatable(Interface):
  """
  Granulatable interface specification

  Documents which implement IGranulatable can be analysed
  and granulated into smaller sub documents. Reversely,
  content can be updated from sub content.
  """

  def granulateContent():
    """
    Populates the current document with subcontent based on the
    document content. This can be used for example to transform the
    whole XML of an RSS feed into a collection of subcontents,
    one per news item.

    NOTE: this method used to be called populateContent
    """

  def assembleContent():
    """
    Updated the current document by assembling subcontent
    and generate a new document. It is the reverse method
    of IGranulatable.granulateContent
    """
