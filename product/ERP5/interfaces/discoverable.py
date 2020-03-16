# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

class IDiscoverable(Interface):
  """
  Discoverable interface specification

  Documents which implement IDiscoverable provides
  methods to discover and update metadata properties
  from content, user input, file name, etc.
  """

  def getContentInformation():
    """
    Returns a dictionary of possible metadata which can be extracted from the
    document content (ex. title from an HTML file, creation date from a PDF
    document, etc.)
    """

  def getPropertyDictFromUserLogin(user_login=None):
    """
    Based on the user_login, find out all properties which
    can be discovered to later update document metadata.

    user_login -- optional user login ID
    """

  def getPropertyDictFromContent():
    """
    Based on the result of getContentInformation, find out all
    properties which can be discovered to later update document metadata.
    """

  def getPropertyDictFromFilename(filename):
    """
    Based on the file name, find out all properties which
    can be discovered to later update document metadata.

    filename -- file name to use in discovery process
    """

  def getPropertyDictFromInput():
    """
    Based on the user input, find out all properties which
    can be discovered to later update document metadata.
    """

  def discoverMetadata(filename=None, user_login=None):
    """
    Updates the document metadata by discovering metadata from
    the user login, the document content, the file name and the
    user input. The order of discovery should be set in system
    preferences.

    filename - optional file name (ex. AA-BBB-CCC-223-en.doc)

    user_login -- optional user login ID

    XXX - it is unclear if this method should also trigger finishIngestion
          and whether this should be documented here or not
    """

  def finishIngestion():
    """
    Finish the ingestion process (ex. allocate a reference number automatically if
    no reference was defined.)

    XXX - it is unclear if this method should be part of the interface
    """

  def getExtensionFromFilename():
    """Return calculated value of extension read from filename
    """

  def getContentTypeFromContent():
    """Return calculated value of content type read from content
    """
