##############################################################################
# Copyright (c) 2019 Nexedi SA and Contributors. All Rights Reserved.
#                     Kazuhiko <kazuhiko@nexedi.com>
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
import contextlib
from Products.ERP5Type import Timeout
from Products.ERP5Type.Timeout import Deadline
from timerserver.TimerServer import TimerRequest
from ZPublisher import Publish

@contextlib.contextmanager
def Dummy():
  yield

call_object_orig = Publish.call_object
def call_object(object, args, request):
  # Refer Timeout.publisher_timeout instead of
  #   from Products.ERP5Type.Timeout import publisher_timeout
  # so that we can override the value in Timeout namescope in unit tests.
  with (
    Dummy()
    if isinstance(request, TimerRequest) else
    Deadline(Timeout.publisher_timeout)
  ):
    return call_object_orig(object, args, request)
Publish.call_object = call_object

publish = Publish.__dict__['publish']
if publish.__name__ == 'new_publish': # already patched by Localizer/patches.py
  publish = publish.__defaults__[1]
publish.__defaults__ = tuple(call_object if x is call_object_orig else x for x in publish.__defaults__)
