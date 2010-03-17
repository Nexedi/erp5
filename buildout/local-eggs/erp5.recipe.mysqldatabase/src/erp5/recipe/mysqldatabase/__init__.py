# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
import logging

import zc.buildout

class Recipe(object):
    
  def __init__(self, buildout, name, options):
    self.buildout, self.options, self.name = buildout, options, name
    self.logger=logging.getLogger(self.name)

    options['location'] = os.path.join(
        buildout['buildout']['parts-directory'],
        self.name,
        )

    options.setdefault('mysql_host', 'localhost')

    options.setdefault('mysql_port', '3306')

  def install(self):
    options = self.options
    location = options['location']

    try:
      import MySQLdb
    except ImportError:
      raise ImportError('To be able to create database MySQLdb is required'
          ' Install system wide or use software generated python')
    database_name, user, password, port, host\
          = \
        options.get('mysql_database_name'), \
        options.get('mysql_user'), \
        options.get('mysql_password'), \
        options.get('mysql_port'), \
        options.get('mysql_host')

    if not (database_name and user):
      raise zc.buildout.UserError('database_name and user are '
        'required to create database and grant privileges')

    connection = MySQLdb.connect(
      host = self.options.get('mysql_host'),
      port = int(self.options.get('mysql_port')),
      user = self.options.get('mysql_superuser'),
      passwd = self.options.get('mysql_superpassword'),
    )
    connection.autocommit(0)
    cursor = connection.cursor()
    cursor.execute(
      'CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET utf8 COLLATE '
      'utf8_unicode_ci' % database_name)
    privileges = ['GRANT ALL PRIVILEGES ON %s.* TO %s' % (
        database_name, user)]

    if host:
      privileges.append('@%s' % host)
    if password:
      privileges.append(' IDENTIFIED BY "%s"' % password)
    cursor.execute(''.join(privileges))
    connection.commit()
    connection.close()
      
    return location

  update = install


