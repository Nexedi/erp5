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
"""
  The followed transforms classes moved to PortalTransforms product.

  To keep the backward compatibility with the persistent objects which
  were not updated yet, it was added the followed imports.

  Without this patch the persistent objects becomes broken and not
  accessible or updatable by Subversion.

  XXX Please remove this path once portal_transforms is not used or
  once all objects are already moved to latest versions of ERP5.
  (at least revision 30051)


"""

import sys
try:
  from Products.PortalTransforms.transforms import png_to_text
  from Products.PortalTransforms.transforms import w3m_dump
  from Products.PortalTransforms.transforms import html_to_text


  sys.modules['Products.ERP5Type.patches.transforms.png_to_text'] = png_to_text
  sys.modules['Products.ERP5Type.patches.transforms.w3m_dump'] = w3m_dump
  sys.modules['Products.ERP5Type.patches.transforms.html_to_text'] = html_to_text

except ImportError:
  from zLOG import LOG, WARNING
  LOG('ERP5Type.patches.transforms', WARNING,
      'Count not import transforms introduced for backward compatibility')
