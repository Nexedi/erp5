# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import imp
class ImportLock(object):
  """
  This class provides the interpreter's import lock.
  It is intended to use in ERP5Type.dynamic to avoid possible dead lock.

  It can be used in two ways :

  1) 'with' statement

  lock = ImportLock()
  with lock:
    ...

  2) traditional 'try' and 'finally'

  lock = ImportLock()
  lock.acquire()
  try:
    ...
  finally:
    lock.release()

  """
  def __enter__(self):
    imp.acquire_lock()

  def __exit__(self, type, value, tb):
    imp.release_lock()

  def acquire(self):
    imp.acquire_lock()

  def release(self):
    imp.release_lock()
