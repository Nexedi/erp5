##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.commandtransform import popentransform

# Conversor using w3m to replace lynx at PortalTransforms...

class w3m_dump(popentransform):
  __implements__ = itransform

  __name__ = "w3m_dump"
  inputs   = ('text/html',)
  output  = 'text/plain'
  
  __version__ = '2008.07.11-1'

  binaryName = "w3m"
  binaryArgs = "-dump -T text/html -o display_charset=utf-8 -o ignore_null_img_alt=0 "
  useStdin = True
  
  def getData(self, couterr):
    lines = [ line for line in couterr.readlines()]
    if len(lines) > 0:
      # This prevent this message be showed
      # -> "Can't open config directory (/root/.w3m)!"
      if ".w3m" in lines[0]:
        lines[0] = "".join(lines[0].split("!")[1:])
    return "".join(lines)

def register():
  return w3m_dump()
