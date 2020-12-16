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

class ICrawlable(Interface):
  """
  Crawlable interface specification

  Documents which implement the ICrawlable can be crawled by
  extracting the URLs which they refer to and can be processed
  by an ERP5 crawler such as the ContributionTool.
  """

  def crawlContent():
    """
    Initialises the crawling process from the current document.
    The crawling process is delegated to an ERP5 crawler such
    as the ContributionTool.
    """

  def getContentURLList():
    """
    Returns a list of URLs which the current document refers to.
    URLs are returned as is (ie. relative, absolute, with or
    without server header).
    """

  def getContentBaseURL():
    """
    Returns the content base URL based on the actual content or
    based on any other information (ex. URL property, system
    preferences, etc.). This information can be used to generate
    a normalised URL.
    """

  def getContentNormalisedURLList():
    """
    Returns a list of URLs which the current document refers to.
    URLs are returned in a normalised way, including server, port
    and absolute path.
    """

  def isIndexContent(container=None, content=None):
    """
    Returns True if the content document acts as an index
    to other documents. Returns False if the content document
    contains relevant content for the end-user.

    This method is used by ERP5 crawlers to make a difference between
    URLs which return an index (ex. the list of emails of a mailing
    list archive) and true content (ex. email content of a mailing list
    archive).

    Either container or content must be set equal None.

    container -- a container document to which the calculation of
                 isIndexContent is delegated to, by default the
                 parent document

    content -- the content document to assess, by default self

    NOTE: Crawlable Documents and External Sources current
    use the same isIndexContent method which is unified here,
    but with a different signature. This is probably inconsistent
    and the interface must be revised. XXX
    """

  def isUpdatable(self):
    """
    This method is used to decide if document can be updated
    in the crawling process.
    """

  def getFrequencyIndex():
    """
    Returns the document update frequency as an integer
    which is used by alamrs to decide which documents
    must be updates at which time. The index represents
    a time slot (ex. all days in a month, all hours in a week).
    Note (ivan): not sure about this if needs to be part interface or not
    """

  def getCreationDateIndex(at_date):
    """
    Returns the document Creation Date Index which is the creation
    date converted into hours modulo the Frequency Index.
    Note (ivan): not sure about this if needs to be part interface or not
    """
