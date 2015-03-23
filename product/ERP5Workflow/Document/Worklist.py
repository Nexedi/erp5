##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#               2015 Wenjie Zheng <wenjie.zheng@tiolive.com>
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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.patches.Expression import Expression_createExprContext
from Products.DCWorkflow.Expression import Expression
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.DCWorkflow.Guard import Guard
from Products.DCWorkflow.permissions import ManagePortal
from Persistence import PersistentMapping
from Products.CMFCore.utils import getToolByName

class Worklist(XMLObject):
    """
    A ERP5 Worklist.
    """

    meta_type = 'ERP5 Worklist'
    portal_type = 'Worklist'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    description = ''
    var_matches = None  # Compared with catalog when set.
    actbox_name = ''
    actbox_url = ''
    actbox_icon = ''
    actbox_category = 'global'
    guard = None

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = (
               PropertySheet.Base,
               PropertySheet.XMLObject,
               PropertySheet.CategoryCore,
               PropertySheet.DublinCore,
               PropertySheet.Worklist,
    )

    def getGuard(self):
        if self.guard is not None:
            return self.guard
        else:
            return Guard().__of__(self)  # Create a temporary guard.

    def getGuardSummary(self):
        res = None
        if self.guard is not None:
            res = self.guard.getSummary()
        return res

    def getAvailableCatalogVars(self):
        res = []
        res.append(self.getParentValue().getStateBaseCategory())
        for vdef in self.getParentValue().contentValues(portal_type="Variable"):
            id = vdef.getId()
            if vdef.for_catalog:
                res.append(id)
        res.sort()
        return res

    def getVarMatchKeys(self):
        if self.var_matches:
            return self.var_matches.keys()
        else:
            return []

    def getVarMatch(self, id):
        if self.var_matches:
            matches = self.var_matches.get(id, ())
            if not isinstance(matches, (tuple, Expression)):
                # Old version, convert it.
                matches = (matches,)
                self.var_matches[id] = matches
            return matches
        else:
            return ()

    def getVarMatchText(self, id):
        values = self.getVarMatch(id)
        if isinstance(values, Expression):
            return values.text
        return '; '.join(values)

    def setProperties(self, description,
                      actbox_name='', actbox_url='', actbox_category='global',
                      actbox_icon='', props=None, REQUEST=None):
        '''
        '''
        if props is None:
            props = REQUEST
        self.description = str(description)
        for key in self.getAvailableCatalogVars():
            # Populate var_matches.
            # add field in real time
            fieldname = 'var_match_%s' % key
            v = props.get(fieldname, '')
            if v:
                if not self.var_matches:
                    self.var_matches = PersistentMapping()

                if tales_re.match(v).group(1):
                    # Found a TALES prefix
                    self.var_matches[key] = Expression(v)
                else:
                    # Falling back to formatted string
                    v = [ var.strip() for var in v.split(';') ]
                    self.var_matches[key] = tuple(v)

            else:
                if self.var_matches and self.var_matches.has_key(key):
                    del self.var_matches[key]
        self.actbox_name = str(actbox_name)
        self.actbox_url = str(actbox_url)
        self.actbox_category = str(actbox_category)
        self.actbox_icon = str(actbox_icon)
        g = Guard()
        if g.changeFromProperties(props or REQUEST):
            self.guard = g
        else:
            self.guard = None
        if REQUEST is not None:
            return self.manage_properties(REQUEST, 'Properties changed.')

    def search(self, info=None, **kw):
        """ Perform the search corresponding to this worklist

        Returns sequence of ZCatalog brains
        - info is a mapping for resolving formatted string variable references
        - additional keyword/value pairs may be used to restrict the query
        """
        if not self.var_matches:
            return

        if info is None:
            info = {}

        catalog = getToolByName(self, 'portal_catalog')
        criteria = {}

        for key, values in self.var_matches.items():
            if isinstance(values, Expression):
                wf = self.getParent()
                portal = wf._getPortalRoot()
                context = Expression_createExprContext(StateChangeInfo(portal, wf))
                criteria[key] = values(context)
            else:
                criteria[key] = [x % info for x in values]

        criteria.update(kw)

        return catalog.searchResults(**criteria)

