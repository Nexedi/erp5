##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.Cache import CachingMethod
from App.config import getConfiguration
from AccessControl import Unauthorized

import os
# XXX This file is destinated to include methods or scripts that are not prevent
# into one old version. The methods here should be removed once the version
# installed into the instance is not supported anymore.

# XXX DO NOT KEEP LOCAL CHANGES HERE, ALL CHANGES SHOULD BE DONE ONLY IN
# INTROSPECTION TOOL OR TRUNK, AND BACKPORTED TO HERE LATER.


#########################################################################################
# Methods introduced into portal_introspection into 5.4.3
#

# XXX This method is a copy and paste of IntrospectionTool._loadExternalConfig
# This should be kept until versions lower than 5.4.3 still supported. 
# NOT USED BY EXTERNAL METHOD
def _loadExternalConfig():
  """
    Load configuration from one external file, this configuration 
    should be set for security reasons to prevent people access 
    forbidden areas in the system.
  """
  def cached_loadExternalConfig():
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.readfp(open('/etc/erp5.cfg'))
    return config     

  cached_loadExternalConfig = CachingMethod(cached_loadExternalConfig,
                              id='IntrospectionTool__loadExternalConfig',
                              cache_factory='erp5_content_long')
  return  cached_loadExternalConfig()

# XXX This method is a copy and paste of IntrospectionTool._getZopeConfigurationFile
# This should be kept until versions lower than 5.4.3 still supported. 
# NOT USED BY EXTERNAL METHOD
def _getZopeConfigurationFile(relative_path="", mode="r"):
  """
   Get a configuration file from the instance using relative path
  """
  if ".." in relative_path or relative_path.startswith("/"):
    raise Unauthorized("In Relative Path, you cannot use .. or startwith / for security reason.")

  instance_home = getConfiguration().instancehome
  file_path = os.path.join(instance_home, relative_path)
  if not os.path.exists(file_path):
    raise IOError('The file: %s does not exist.' % file_path)

  return open(file_path, mode)
