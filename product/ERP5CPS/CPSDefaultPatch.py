# (C) Copyright 2004 Nexedi SARL <http://nexedi.com>
# Authors: Sebastien Robin <seb@nexedi.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

from Products.CPSDefault.Folder import Folder
from Products.ERP5Type.Document.Folder import Folder as ERP5Folder
from Products.ERP5Type.Base import Base

#def _propertyMap(self):
#  """Return a tuple of mappings, giving meta-data for properties """
#  return tuple(list(self._properties) + list(getattr(self, '_local_properties', ())))


Folder._setProperty = Base._setProperty
Folder.setProperty = Base.setProperty
#Folder._propertyMap = _propertyMap
Folder.getProperty = Base.getProperty
Folder._edit = Base._edit
Folder.asXML = ERP5Folder.asXML
