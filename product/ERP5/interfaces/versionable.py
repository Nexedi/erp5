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

class IVersionable(Interface):
  """
  Versionable interface specification

  Documents which implement IVersionable are available in different
  versions and languages and include a revision number.
  """

  def getLatestVersionValue(language=None):
    """
    Returns the the latest version with the latest revision
    of the current document which the current user is
    allows to view. If the current document implements
    ITranslatable, the latest version in the original
    language is returned, unless the document also exists
    with the same version in the user preferred language.

    language -- optional parameter to return the latest document
                in the specified language for documents which also
                implement ITranslatable
    """

  def getVersionValueList(version=None, language=None):
    """
    Returns the list of documents with same reference, same portal_type
    but different version or language.

    language -- optional parameter to specify a language
                for documents which also implement ITranslatable

    version -- optional parameter to specify a version for
               documents which also implement ITranslatable
    """

  def isVersionUnique():
    """
    Returns True if no other document exists with the same
    reference, version and language (for documents which implement
    ITranslatable), or if the current document has no reference.
    Else return False.
    """

  def getRevision():
    """
    Returns the current revision of the current document.
    The return value is a string in order to be consistent
    with the property sheet definition.
    """

  def getRevisionList():
    """
    Returns the list of revisions of the current document.
    """

  def mergeRevision():
    """
    Merge the current document with any previous revision
    by using the content of the current document to replace
    the content of previous revisions, and by deleting the
    current document afterwards. Returns the resulting
    document of the merge process.
    """
