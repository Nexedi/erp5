#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script to automatically create a given number of Zope users, which can be
# useful for performance/scalability testing. This script is really basic as,
# for example, it does not check if the user already exists (Zope will just
# state that the user already exists but do not raise an HTTP error).
#
# TODO: There must be a better way than the code below to do that though...

import sys

from erp5.util.testbrowser.browser import Browser

try:
  url, site_id, username, password, user_nbr, new_username_prefix, \
      new_password = sys.argv[1:]

  user_nbr = int(user_nbr)

except ValueError:
  print >>sys.stderr, "ERROR: Missing arguments: %s URL SITE_ID USERNAME " \
      "PASSWORD NUMBER_OF_USERS NEW_USERNAME_PREFIX NEW_USERS_PASSWORD" % \
      sys.argv[0]

  sys.exit(1)

# Create a browser instance
browser = Browser(url, site_id, username=username, password=password)

erp5_role_tuple = ('Assignee',
                   'Assignor',
                   'Associate',
                   'Auditor',
                   'Author',
                   'Manager',
                   'Member',
                   'Owner',
                   'Reviewer')

post_data_format = "submit=Add&roles:list=Manager&roles:list=Owner&name=" \
    "%(username)s&password=%(password)s&confirm=%(password)s"

for index in range(user_nbr):
  new_username = "%s%d" % (new_username_prefix, index)

  browser.open('/acl_users/manage_users')

  browser.post('%s/acl_users/manage_users' % url,
               post_data_format % {'username': new_username,
                                   'password': new_password})

  browser.open('manage_listLocalRoles')
  form = browser.getForm(action='manage_setLocalRoles')
  form.getControl(name='userid').value = new_username
  form.getControl(name='roles:list').value = erp5_role_tuple
  form.submit()
