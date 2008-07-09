##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

from OriginalClockServer import ClockServer as OriginalClockServer
from OriginalClockServer import DummyChannel
from ZServer.medusa.http_server import http_request
from ZServer.HTTPResponse import make_response
from ZPublisher.HTTPRequest import HTTPRequest
import StringIO
import thread

wait_for_close_lock = thread.allocate_lock()

class ClockServer(OriginalClockServer):
  running = True

  def __init__(self, *args, **kw):
    self.shutdown_method = kw.pop('shutdown_method')
    OriginalClockServer.__init__(self, *args, **kw)
    if self.shutdown_method is None:
      self.log_info('ClockServer shutdown_method is not set in configuration'\
                    'file. Unclean shutdown can happen.', type='warning')

  def readable(self):
    """
      Avoid starting a new tic if shutdown started.
    """
    if self.running:
      OriginalClockServer.readable(self)
    return False

  def clean_shutdown_control(self, _shutdown_phase, time_in_this_phase):
    """
      Inform invoked method that a shutdown is in progress.

      Here we:
       - Prevent regular tics from being sent. This does not prevent
         already-issued tics from running.
       - Issue a special tic, ran asynchronously from regular tics and
         asynchronously from this thread.
       - Wait for that special tic to return, so that we know all clean
         shutdown handlers have completely run.
       - Return control to caller.

      To wait for shutdown handler to return, it has been chosen to use a
      semaphore scheme. It has the following drawbacks:
       - It is intrusive: we need to hook foreign classes, since it's not
         the way things happen with regular zope data exchange.
       - We can't get what the shutdown handler returned (http return code,
         page content, ...) so we will never take Lifetime's veto. So shutdown
         handler must block until shutdown is complete, which is not how
         clean_shutdown_control is supposed to work. Note though that it is a
         design weakness in clean_shutdown_control, since some shutdown
         handlers might not have finshed their job at the time process gets
         closed.
    """
    self.running = False
    if self.shutdown_method is not None:
      # XXX: should use a float for time representation
      method = '%s?phase:int=%i&time_in_phase:float=%f' % \
        (self.shutdown_method, _shutdown_phase, time_in_this_phase)

      stdin = StringIO.StringIO()
      request_string = 'GET %s HTTP/1.0' % (method, )
      request = http_request(DummyChannel(self), request_string, 'GET', method,
                             '1.0', self.headers)
      environment = self.get_env(request)
      response = make_response(request, environment)
      # Hook response._finish to get a notification when request is over.
      def _finish():
        response.__class__._finish(response)
        wait_for_close_lock.release()
      response._finish = _finish
      # (end of hook)
      zope_request = HTTPRequest(stdin, environment, response)
      wait_for_close_lock.acquire()
      self.zhandler('Zope2', zope_request, response)
      self.log_info('ClockServer: Waiting for shutdown handler.')
      wait_for_close_lock.acquire()
      self.log_info('ClockServer: Going on.')
      wait_for_close_lock.release()
    return 0 # TODO: detect an error to allow taking the veto.

