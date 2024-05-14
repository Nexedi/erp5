# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import warnings
from collections import Mapping
from collections import Iterable
try:
  from deepdiff import DeepDiff
  from deepdiff.helper import strings, numbers
except ImportError:
  DeepDiff = None
  strings = None
  numbers = None
  warnings.warn("Please install deepdiff, it is needed by json_representable mixin",
                DeprecationWarning)


def DeepDiff__diff_iterable(self, level, parents_ids=frozenset({})):
    """Difference of iterables"""
    level.t1 = str(level.t1)
    level.t2 = str(level.t2)
    self._DeepDiff__diff_str(level)

def DeepDiff__diff(self, level, parents_ids=frozenset({})):
    """The main diff method"""
    if level.t1 is level.t2:
        return
    if self._DeepDiff__skip_this(level):
        return

    if type(level.t1) != type(level.t2):
        self._DeepDiff__diff_types(level)

    elif isinstance(level.t1, strings):
        self._DeepDiff__diff_str(level)

    elif isinstance(level.t1, numbers):
        self._DeepDiff__diff_numbers(level)

    elif isinstance(level.t1, Mapping):
        self._DeepDiff__diff_dict(level, parents_ids)

    elif isinstance(level.t1, tuple):
        # Sort the values for t1 and t2 before diffing tuples.
        # Reason being that we except tuples and other iterables to be diffed
        # as a string so as not to use the forced feature of recursive diff
        # by deepdiff. Thus, sorting tuples before diffing will atleast give us
        # diff in the format where we would be able to see the more asthetic
        # diff for tuples.
        level.t1 = sorted(level.t1)
        level.t2 = sorted(level.t2)
        self._DeepDiff__diff_tuple(level, parents_ids)

    elif isinstance(level.t1, (set, frozenset)):
        self._DeepDiff__diff_set(level)

    elif isinstance(level.t1, Iterable):
        if self.ignore_order:
            self._DeepDiff__diff_iterable_with_contenthash(level)
        else:
            self._DeepDiff__diff_iterable(level, parents_ids)

    else:
        self._DeepDiff__diff_obj(level, parents_ids)

    return

# Monkey patch the functions for DeepDiff class.
# This patch fixes the requirement of diffing the iterables which by default
# was too complicated in DeepDiff(doing recursive diff inside the iterables).
# Rather than doing that, now we treat the iterables as string and calculate
# the diff accordingly
# Do not try to monkey-patch when there is no DeepDiff class imported. This is
# because we don't want any component(for ex DiffTool) be acting as Broken Modified
# if the DeepDiff patch is not working properly
try:
  DeepDiff._DeepDiff__diff_iterable = DeepDiff__diff_iterable
  DeepDiff._DeepDiff__diff = DeepDiff__diff
except AttributeError:
  pass
