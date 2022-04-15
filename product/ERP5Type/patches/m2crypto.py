##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

# Disable broken M2Crypto enhancement to urllib for handling 'https' url
#
# M2Crypto is a dependency of portal_web_services via SOAPpy
# but it has 2 bugs breaking testBusinessTemplate.test_download_svn:
# - https://bugzilla.osafoundation.org/show_bug.cgi?id=8626
#   (see also http://www.mail-archive.com/python-list@python.org/msg127308.html
#    where you can find a one-line hack to bypass the error)
# - M2Crypto doesn't automatically redirect from .../test_web to .../test_web/

from urllib.request import URLopener

python_open_https = URLopener.open_https
try:
  import M2Crypto
  URLopener.open_https = python_open_https
except ImportError:
  pass
