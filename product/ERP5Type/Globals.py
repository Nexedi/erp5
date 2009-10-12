##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
"""
    ERP5Type.Globals is a class to smoothen transition from Zope 2.8 to 2.12,
    where the Globals module has been removed. All ERP5 Code should import
    from ERP5Type.Globals instead of Globals
"""

# Globals.InitializeClass a.k.a. default__class_init__. This import location
# has not changed since 2.8 and still works on 2.12
from App.class_init import default__class_init__, ApplicationDefaultPermissions

# Nicer alias for class initializer.
InitializeClass = default__class_init__

##########################################
# Localizer is not always loaded prior to ERP5 products,
# thus, as Localizer is supposed to patch Global to add get_request to it,
# we prefer to redefine get_request inside ERP5Type/Utils,
# to avoid the case when Global wasn't patched and get_request is not available.
# This is specially important on Zope 2.12 where Globals doesn't even exist.
##########################################
try:
    import Products.iHotfix
    get_request = Products.iHotfix.get_request
except (ImportError, AttributeError):
    import Products.Localizer
    get_request = Products.Localizer.get_request

# Persistency stuff also hasn't moved much from Zope 2.8, although the old
# "Persistence" module remains there for ancient backward compatibility.
# let's try using the new 'persistence' implementation only and see how far we
# can get. This might not be enough for content in old ZODBs, though...
from Persistence import Persistent, PersistentMapping 
from App.special_dtml import HTML, HTMLFile, DTMLFile
from App.Common import package_home
from App.Dialogs import MessageDialog

from App.config import getConfiguration as _getConfiguration
_cfg = _getConfiguration()

DevelopmentMode = _cfg.debug_mode
# backward compatibility
INSTANCE_HOME = _cfg.instancehome
SOFTWARE_HOME = _cfg.softwarehome
ZOPE_HOME = _cfg.zopehome

# don't tempt potential users by leaving these lying around
del _cfg, _getConfiguration
