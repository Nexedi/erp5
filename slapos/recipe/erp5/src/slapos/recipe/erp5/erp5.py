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

def updateERP5(args):
  base_url = args[2]
  mysql_string = args[1]
  site_id = args[0]
  sleep = 30
  while True:
    try:
      test_url = '%s/%s/getId' % (base_url, site_id)
      result = urllib.urlopen(test_url).read()
      # XXX This result should be more assertive
      if result != site_id:
        url = '%s/manage_addProduct/ERP5/manage_addERP5Site' % base_url
        result = urllib.urlopen(url, urllib.urlencode({
          "id": site_id,
          "erp5_sql_connection_string": mysql_string,
          "cmf_activity_sql_connection_string": mysql_string, }))
        print result.read()

        result = urllib.urlopen(test_url).read()

      if result == site_id:
        print "Ready for install one business."
        # XXX Suggestion for future
        # POST '%s/erp5/portal_templates/updateRepositoryBusinessTemplateList <
        #                                                        repository_list

        # POST '%s/erp5/portal_templates/installBusinessTemplatesFromRepositories <
        #                                                        template_list

    except IOError:
      print "Unable to connect!"
    time.sleep(sleep)
