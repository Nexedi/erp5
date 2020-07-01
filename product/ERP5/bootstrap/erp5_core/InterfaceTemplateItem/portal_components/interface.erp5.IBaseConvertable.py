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

class IBaseConvertable(Interface):
  """
  Base Convertable interface specification

  Documents which implement IBaseConvertable first
  convert the original data to a base format which is later
  used to generate the target converted format.
  """

  def hasBaseData():
    """
    Returns True is base data was defined on the document, False
    else. This method is normally provided by a property sheet
    and does not need to be implemented.

    XXX - unclear whether this method should be part of the interface
    """

  def convertFile(**kw):
    """
    A workflow method to invoke whenever the base format
    conversion occurs.

    kw -- optional parameters which must be passed to the workflow
          method and which will eventually end up in the
          workflow history as a way to inform the user of
          the results of the conversion process.

    TODO::
      - XXX-JPS usefulness is really uncertain
    """

  def convertToBaseFormat():
    """
    Converts the original document to a base format
    which is later used by the conversion engine to
    generate the target format requested by the user.
    """

  def updateBaseMetadata(**kw):
    """
    Updates metadata information of the base data.
    This method is the reverse of
    IMetadataDiscoverable.getContentInformation.

    kw -- metadata parameters
    """
