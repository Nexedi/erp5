# -*- coding: utf-8 -*-
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

import xmlrpclib
#import zc.buildout
import zc.buildout.easy_install
import zc.buildout.download
import zc.recipe.egg
import subprocess

class Recipe(object):

  MAX_BT_PER_TRANSACTION = 2

  def __init__(self, buildout, name, options):
    self.buildout, self.options, self.name = buildout, options, name
    self.logger = logging.getLogger(self.name)
    self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)


    options.setdefault('location', os.path.join(
        buildout['buildout']['parts-directory'],
        self.name,
        ))

    # Business Template installation
    options.setdefault('repository_path', '')
    options.setdefault('bt5_list', '')
    options.setdefault('update_catalog', 'auto')

    # XML-RPC connection
    options.setdefault('protocol', 'http')
    options.setdefault('user', 'zope:zope')
    options.setdefault('hostname', 'localhost')
    options.setdefault('port', '8080')
    options.setdefault('portal_id', 'erp5')

  def _getConnectionString(self):
    """Return connection string to connect
    to instance
    """
    options = self.options
    connection_string = '%(protocol)s://%(user)s@%(hostname)'\
                        's:%(port)s/%(portal_id)s/' % options
    return connection_string

  def _getConnection(self, connection_string):
    """Return XML-RPC connected object
    """
    connection =  xmlrpclib.ServerProxy(connection_string, allow_none=True)
    return connection

  def install(self):
    options = self.options
    location = options['location']
    if not os.path.exists(location):
      os.mkdir(location)

    connection = self._getConnection(self._getConnectionString())
    # install templates
    repository_path = options['repository_path']
    connection.portal_templates.updateRepositoryBusinessTemplateList(
                                                       [repository_path], None)
    bt5_list = [bt5 for bt5 in options['bt5_list'].splitlines() if bt5]
    update_catalog_option = options['update_catalog'].lower()
    if update_catalog_option == 'false':
      update_catalog = False
    elif update_catalog_option == 'true':
      update_catalog = True
    else:
      # update_catalog_option == 'auto'
      update_catalog = None 
    while bt5_list:
      partial_bt5_list = bt5_list[:self.MAX_BT_PER_TRANSACTION]
      print 'Installing following business template:',\
                                                    ', '.join(partial_bt5_list)
      if update_catalog is not None:
        result = connection.portal_templates\
                .installBusinessTemplatesFromRepositories(partial_bt5_list,
                                                          True, update_catalog)
      else:
        # Avoid overriding default value and let business template
        # clearing catalog only if needed.
        result = connection.portal_templates\
                    .installBusinessTemplatesFromRepositories(partial_bt5_list,
                                                              True)

      bt5_list = bt5_list[self.MAX_BT_PER_TRANSACTION:]

    return [] # instance related recipe, it can be disaster to allow buildout
              # to remove instances


  update = install
