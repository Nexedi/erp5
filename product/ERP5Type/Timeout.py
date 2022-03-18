##############################################################################
# Copyright (c) 2019-2020 Nexedi SA and Contributors. All Rights Reserved.
#                     Kazuhiko <kazuhiko@nexedi.com>
#                     Vincent Pelletier <vincent@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
from contextlib import contextmanager
import threading
import time, six
from AccessControl.SecurityInfo import ModuleSecurityInfo
from ZPublisher.HTTPResponse import status_codes
from Products.TimerService.timerserver.TimerServer import TimerRequest

__all__ = (
  'TimeoutReachedError', 'Deadline', 'getDeadline', 'getTimeLeft',
  'getPublisherDeadlineValue',
)

class TimeoutReachedError(Exception):
  """
  A deadline was reached.
  """
  pass

# There is no appropriate status code for timeout.
status_codes['timeoutreachederror'] = 500 # Internal Server Error
del status_codes

# Placeholder timeouts until product's "initialize" is called.
publisher_timeout = None
activity_timeout = None

_site_local = threading.local()

@contextmanager
def Deadline(offset):
  """
  Context manager for defining the code-wise scope of a deadline.
  offset (float)
    Number of seconds the context-managed piece of code should be allowed to
    run for. Positive values are based on current time, while negative values
    are based on pre-existing deadline, and no deadline will be set if none
    was pre-existing.
    There is no automated enforcement of this delay, it is up to the code to
    check whether it exceeded the allotted preiod, and to raise
    TimeoutReachedError.
    If None, it has no effect on a possible current deadline, for caller code
    simplicity.
  """
  if offset is None:
    yield
  else:
    old_deadline = getattr(_site_local, 'deadline', None)
    if old_deadline is None:
      if offset >= 0:
        _site_local.deadline = time.time() + offset
    elif offset < 0:
      _site_local.deadline = old_deadline + offset
    else:
      # Ignore attempts to extend an existing deadline.
      _site_local.deadline = min(old_deadline, time.time() + offset)
    try:
      yield
    finally:
      _site_local.deadline = old_deadline

ModuleSecurityInfo('Products.ERP5Type.Timeout').declarePublic('Deadline')

def getDeadline():
  """
  Return currently-applicable deadline as a timestamp, or None if there is
  no currently applicable deadline.
  """
  return getattr(_site_local, 'deadline', None)

def getTimeLeft():
  """
  Return the number of seconds left until current deadline, or None if there is
  no currently applicable deadline.
  """
  deadline = getattr(_site_local, 'deadline', None)
  return None if deadline is None else max(deadline - time.time(), 0.000001)

def getPublisherDeadlineValue(request):
  """
  Return an instance of Deadline class suitable for publication.
  """
  return Deadline(
    None if isinstance(request, TimerRequest) else publisher_timeout,
  )
