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

from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
from Products.CMFCore.utils import getToolByName

def editDocument(self, object=None, **kw):
  """
  This is the default editDocument method. This method
  can easily be overwritten.
  """
  object._edit(**kw)
  portal_trees = getToolByName(object,'portal_trees')
  for o in portal_trees.objectValues():
    o.rebuild()



ERP5Conduit.editDocument = editDocument
