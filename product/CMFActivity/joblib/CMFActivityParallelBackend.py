##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
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

import logging
from ZODB.POSException import ConflictError
from Products.CMFActivity.ActivityRuntimeEnvironment import \
  getActivityRuntimeEnvironment
import six

logger = logging.getLogger(__name__)
try:
  if six.PY2:
    from sklearn.externals.joblib import register_parallel_backend
    from sklearn.externals.joblib.parallel import ParallelBackendBase, parallel_backend
    from sklearn.externals.joblib.parallel import FallbackToBackend, SequentialBackend
    from sklearn.externals.joblib.hashing import hash as joblib_hash
  else:
    from joblib import register_parallel_backend
    from joblib.parallel import ParallelBackendBase, parallel_backend
    from joblib.parallel import FallbackToBackend, SequentialBackend
    from joblib.hashing import hash as joblib_hash

except ImportError:
  logger.warn("Joblib cannot be imported, support disabled")
else:
  class JoblibResult(object):

    def __init__(self, result, callback):
      self.result = result
      self.callback = callback

    def get(self, timeout=None):
      result = self.result.result
      callback = self.callback
      if callback is not None:
        callback(result)
      return result

  class JoblibDispatch(object):

    def __init__(self, backend):
      self.backend = backend

    def get(self, timeout=None):
      backend = self.backend
      def onError(exc_type, exc_value, traceback):
        active_process = backend.active_process
        activate = active_process.getParentValue().activate
        kw = {
          'active_process': active_process,
          'activity': 'SQLJoblib',
          'tag': "joblib_" + active_process.getId(),
        }
        for sig, batch in backend.job_list:
          activate(signature=sig, **kw)._callSafeFunction(batch)
      getActivityRuntimeEnvironment().edit(on_error_callback=onError)
      raise ConflictError

  class CMFActivityBackend(ParallelBackendBase):
    def __init__(self, *args, **kw):
      self.active_process = active_process = kw['active_process']
      self.job_list = []
      self.result_dict = active_process.getResultDict()

    def effective_n_jobs(self, n_jobs):
      """Dummy implementation to prevent n_jobs <=0

      and allow (sequential) n_jobs=1 and n_jobs != 1 (parallel) behaviour
      """
      if n_jobs == 0:
        raise ValueError('n_jobs == 0 in Parallel has no meaning')
      return abs(n_jobs)

    def apply_async(self, batch, callback=None):
      """Schedule a func to be run"""
      sig = joblib_hash(batch)
      result = self.result_dict.get(sig)
      if result is None:
        self.job_list.append((sig, batch))
        return JoblibDispatch(self)
      return JoblibResult(result, callback)

    def configure(self, n_jobs=1, parallel=None, **backend_args):
      """Reconfigure the backend and return the number of workers. This
      makes it possible to reuse an existing backend instance for successive
      independent calls to Parallel with different parameters."""

      if n_jobs == 1:
        raise FallbackToBackend(SequentialBackend())

      self.parallel = parallel
      return self.effective_n_jobs(n_jobs)

    def abort_everything(self, ensure_ready=True):
      # All jobs will be aborted here while they are still processing our backend
      if ensure_ready:
        self.configure(n_jobs=self.parallel.n_jobs, parallel=self.parallel,
                        **self.parallel._backend_args)
      return

  register_parallel_backend('CMFActivity', CMFActivityBackend)
