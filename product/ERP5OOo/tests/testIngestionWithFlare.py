# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from __future__ import absolute_import
import unittest
from Products.ERP5OOo.tests.testIngestion import TestIngestion
from Products.ERP5Type.tests.ERP5TypeTestCase import _getPersistentMemcachedServerDict

class TestIngestionWithFlare(TestIngestion):
  """
    ERP5 Document Management System - test file ingestion mechanism with Flare
  """

  ##################################
  ##  ZopeTestCase Skeleton
  ##################################

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "ERP5 DMS - Ingestion with Flare"

  def setSystemPreference(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    memcached = _getPersistentMemcachedServerDict()
    # create a Cache Factory for tests
    cache_factory = self.portal.portal_caches.newContent(portal_type = 'Cache Factory')
    cache_factory.cache_duration = 15768000
    cache_plugin = cache_factory.newContent(portal_type='Distributed Ram Cache')
    default_pref.setPreferredConversionCacheFactory(cache_factory.getId())
    persistent_memcached_plugin = self.portal.portal_memcached.persistent_memcached_plugin
    persistent_memcached_plugin.setUrlString('%s:%s' %(memcached['hostname'], memcached['port']))
    cache_plugin.setSpecialiseValue(persistent_memcached_plugin)
    TestIngestion.setSystemPreference(self)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestIngestionWithFlare))
  return suite
