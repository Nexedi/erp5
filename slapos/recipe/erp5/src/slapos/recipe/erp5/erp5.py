##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
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
# as published by the Free Software Foundation; either version 3
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
import time
import urllib
import xmlrpclib
import socket

def updateERP5(args):
  site_id = args[0]
  mysql_string = args[1]
  base_url = args[2]
  memcached_provider = args[3]
  conversion_server_address = args[4]
  conversion_server_port = args[5]
  bt5_list = args[6]
  bt5_repository_list = []
  if len(args) > 7:
    bt5_repository_list = args[7]
  erp5_catalog_storage = "erp5_mysql_innodb_catalog"
  sleep = 60
  while True:
    try:
      proxy = xmlrpclib.ServerProxy(base_url)
      if proxy.isERP5SitePresent() == False:
        url = '%s/manage_addProduct/ERP5/manage_addERP5Site' % base_url
        result = urllib.urlopen(url, urllib.urlencode({
          "id": site_id,
         # This parameter should be an argument in future.
          "erp5_catalog_storage": erp5_catalog_storage,
          "erp5_sql_connection_string": mysql_string,
          "cmf_activity_sql_connection_string": mysql_string, }))
        print result.read()

        print "ERP5 Site creation output: %s" % result.read()

        if proxy.isERP5SitePresent() == True:
          print "Site was created successfuly!"

          # Update URL to ERP5 Site
          erp5 = xmlrpclib.ServerProxy("%s/%s" % (base_url, site_id),
                                       allow_none=1)

          # Update Cache Coordinates
          erp5.portal_memcached.default_memcached_plugin.\
                setUrlString(memcached_provider)

          # Update and enable System preferrence with ERP5 Site Coordinates.
          # XXX NO SYSTEM PREFERENCE AS DEFAULT so it is used Default
          # Preference instead as object creation is not possible by
          # xmlrpc or post.
          preference = erp5.portal_preferences.default_site_preference
          preference.setPreferredOoodocServerAddress(conversion_server_address)
          preference.setPreferredOoodocServerPortNumber(conversion_server_port)
          preference.enable()

          if len(bt5_repository_list) > 0:
            erp5.portal_templates.\
                updateRepositoryBusinessTemplateList(bt5_repository_list, None)

          if len(bt5_list) > 0:
            # XXX If no repository is provided, use just trunk.
            if len(erp5.portal_templates.getRepositoryList()) == 0:
              bt5_repository_list = ["http://www.erp5.org/dists/snapshot/bt5"]
              erp5.portal_templates.\
                updateRepositoryBusinessTemplateList(bt5_repository_list, None)

            erp5.portal_templates.\
              installBusinessTemplatesFromRepositories(bt5_list)

          # The persistent cache is only configurable after install \
          # erp5_dms.
          #erp5.portal_memcached.persistent_memcached_plugin.\
          #       setUrlString(kumo_address)
      else:
        print "ERP5 site is already present, ignore."

    except IOError:
      print "Unable to create the ERP5 Site!"
    except socket.error, e:
      print "Unable to connect to ZOPE!"
    time.sleep(sleep)
