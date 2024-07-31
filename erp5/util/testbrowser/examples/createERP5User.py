#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Script to automatically create a given number of Zope users, which can be
# useful for performance/scalability testing. This script is really basic as,
# for example, it does not check if the user already exists (Zope will just
# state that the user already exists but do not raise an HTTP error).
#
# TODO: There must be a better way than the code below to do that though...

from __future__ import print_function
import sys

from erp5.util.testbrowser.browser import Browser

try:
  url, username, password, user_nbr, new_username_prefix, \
      new_password = sys.argv[1:]

  user_nbr = int(user_nbr)

except ValueError:
  sys.exit("ERROR: Missing arguments: %s URL USERNAME PASSWORD NUMBER_OF_USERS "
           "NEW_USERNAME_PREFIX NEW_USERS_PASSWORD" % sys.argv[0])

# Create a browser instance
browser = Browser(url, username, password)

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

# TODO: Because of post() not wrapped properly
zope_url = url.rsplit('/', 2)[0]

import base64
browser.mech_browser.addheaders.append(
    ('Authorization',
     'Basic %s' % base64.encodebytes(('%s:%s' % (username, password)).encode())).decode())

for index in range(user_nbr):
  new_username = "%s%d" % (new_username_prefix, index)

  browser.open('/acl_users/manage_users')

  browser.post('%s/acl_users/manage_users' % zope_url,
               post_data_format % {'username': new_username,
                                   'password': new_password})

  browser.open('manage_listLocalRoles')
  form = browser.getForm(action='manage_setLocalRoles')
  form.getControl(name='userid').value = new_username
  form.getControl(name='roles:list').value = erp5_role_tuple
  form.submit()
