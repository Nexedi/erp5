# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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

class IUrl(Interface):
  """
  """

  def asURL():
    """
    Returns a text representation of the Url if defined
    or None else.
    """


  def fromURL(url):
    """
    Analyses a URL and splits it into two parts. URLs
    normally follow RFC 1738. However, we accept URLs
    without the protocol a.k.a. scheme part (http, mailto, etc.). In this
    case only the url_string a.k.a. scheme-specific-part is taken
    into account. asURL will then generate the full URL.
    """

  def getURLServer():
    """
    Returns the server part of a URL
    """

  def getURLPort():
    """
    Returns the port part of a URL
    """

  def getURLPath():
    """
    Returns the path part of a URL
    """

  def asNormalisedURL(base_url=None):
    """
    Returns a normalised version of the url so
    that we do not download twice the same content.
    This normalisation must refer to the same resource !
    Refer to http://en.wikipedia.org/wiki/URL_normalization .

    base_url - Specify a default URL and a default target
               for all links on a page.
               if url is a relative link, we try to compute an absolute url
               with help of base_url
    """
