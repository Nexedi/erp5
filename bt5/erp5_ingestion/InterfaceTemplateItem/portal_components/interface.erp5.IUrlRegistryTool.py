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

class IUrlRegistryTool(Interface):
  """Tool to register URLs
  This tool aim to maintain consistency in URL management
  of crawlable sources in order to maintain consistency
  between an external resource identifier and generated
  document inside ERP5.

  Multiple URL can be associated to the same reference

  A System Preference can used to configure the global namespace.
  This enable isolation of url mappings for different Groups.

  This is a configurable tool to support different scope for mappings.
  So it is possible to restrict the crawling of an URL
  only once in the context of portal;
  Or restrict the crawling of an url for the scope of an external_source
  or a module only (Crawling multiple times the same URL for a portal)
  """

  def clearUrlRegistryTool(context=None):
    """Unregister all urls in all namespaces.
    Only available for Manager

    context - a context to access container of mappings.
    """

  def registerURL(url, reference, context=None):
    """Register the mapping url:reference
    this method is aimed to be called from interaction_workflow
    which trig on _setReference in order to keep the association
    between url:reference up to date.

    url - external resource identifier
    reference - reference of downloaded resource (ERP5 Object instance)
    context - a context to access container of mappings.
              If not passed, mappings are stored on tool itself
    """

  def getReferenceList(context=None):
    """return all references registered by portal_url_registry
    according given context

    context - a context to access container of mappings.
    """

  def getReferenceFromURL(url, context=None):
    """return reference of document according provided url

    url - external resource identifier
    context - a context to access container of mappings.
              If not passed, mapping are stored on tool itself
    """

  def getURLListFromReference(reference, context=None):
    """return list of urls associated to given reference
    and context.

    reference - reference of downloaded resource (ERP5 Object instance)
    context - a context to access container of mappings.
    """

  def updateUrlRegistryTool():
    """Rebuild all url mappings for active preference
    """
