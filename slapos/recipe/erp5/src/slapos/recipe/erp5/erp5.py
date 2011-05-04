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
  # FIXME Use a dict
  site_id = args[0]
  mysql_string = args[1]
  base_url = args[2]
  memcached_provider = args[3]
  conversion_server = args[4]
  kumo_provider = args[5]
  bt5_list = args[6]
  bt5_repository_list = []
  if len(args) > 7:
    bt5_repository_list = args[7]

  if len(bt5_list) > 0 and len(bt5_repository_list) == 0:
    bt5_repository_list = ["http://www.erp5.org/dists/snapshot/bt5"]
  erp5_catalog_storage = "erp5_mysql_innodb_catalog"
  business_template_setup_finished = 0
  external_service_assertion = 1
  update_script_id = "ERP5Site_assertExternalServiceList"
  sleep = 120
  while True:
    try:
      proxy = xmlrpclib.ServerProxy(base_url)
      print "Adding site at %r" % base_url
      if proxy.isERP5SitePresent() == False:
        url = '%s/manage_addProduct/ERP5/manage_addERP5Site' % base_url
        result = urllib.urlopen(url, urllib.urlencode({
          "id": site_id,
          "erp5_catalog_storage": erp5_catalog_storage,
          "erp5_sql_connection_string": mysql_string,
          "cmf_activity_sql_connection_string": mysql_string, }))
        print "ERP5 Site creation output: %s" % result.read()

      if not business_template_setup_finished:
        if proxy.isERP5SitePresent() == True:
          print "Start to set initial business template setup."
          # Update URL to ERP5 Site
          erp5 = xmlrpclib.ServerProxy("%s/%s" % (base_url, site_id),
                                       allow_none=1)

          repository_list = erp5.portal_templates.getRepositoryList()
          if len(bt5_repository_list) > 0 and \
             set(bt5_repository_list) != set(repository_list):
            erp5.portal_templates.\
                updateRepositoryBusinessTemplateList(bt5_repository_list, None)

          installed_bt5_list =\
            erp5.portal_templates.getInstalledBusinessTemplateTitleList()
          for bt5 in bt5_list:
            if bt5 not in installed_bt5_list:
              erp5.portal_templates.\
                installBusinessTemplatesFromRepositories([bt5])

          repository_set = set(erp5.portal_templates.getRepositoryList())
          installed_bt5_list = erp5.portal_templates.\
               getInstalledBusinessTemplateTitleList()
          if (set(repository_set) == set(bt5_repository_list)) and \
              len([i for i in bt5_list if i not in installed_bt5_list]) == 0:
            print "Repositories updated and business templates installed."
            business_template_setup_finished = 1

      if external_service_assertion:
        url = "%s/%s/%s" % (base_url, site_id, update_script_id)
        result = urllib.urlopen(url, urllib.urlencode({
          "memcached" : memcached_provider,
          "kumo" : kumo_provider,
          "conversion_server" : conversion_server,})).read()
        external_service_assertion = not (result == "True")

    except IOError:
      print "Unable to create the ERP5 Site!"
    except socket.error, e:
      print "Unable to connect to ZOPE! %s" % e
    except xmlrpclib.Fault, e:
      print "XMLRPC Fault: %s" % e
    time.sleep(sleep)
