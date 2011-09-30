##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

import os
import argparse

class ArgumentType(object):
  @classmethod
  def directoryType(cls, path):
    if not os.path.exists(path):
      os.makedirs(path)
    elif not (os.path.isdir(path) and os.access(path, os.W_OK)):
      raise argparse.ArgumentTypeError("'%s' does not seem to be writable" % path)

    return path

  @classmethod
  def objectFromModule(cls, module_name, object_name=None,
                       callable_object=False):
    if module_name.endswith('.py'):
      module_name = module_name[:-3]

    if not object_name:
      object_name = module_name

    import sys
    sys.path.append(os.getcwd())

    try:
      module = __import__(module_name, globals(), locals(), [object_name], -1)
    except Exception, e:
      raise argparse.ArgumentTypeError("Cannot import '%s.%s': %s" % \
                                         (module_name, object_name, str(e)))

    try:
      obj = getattr(module, object_name)
    except AttributeError:
      raise argparse.ArgumentTypeError("Could not get '%s' in '%s'" % \
                                         (object_name, module_name))

    if callable_object and not callable(obj):
      raise argparse.ArgumentTypeError(
        "'%s.%s' is not callable" % (module_name, object_name))

    return obj

  @classmethod
  def checkIntValueWrapper(cls, minimum):
    def checkIntValue(value):
      try:
        converted_value = int(value)
      except ValueError:
        pass
      else:
        if converted_value >= minimum:
          return converted_value

      raise argparse.ArgumentTypeError('Expected an integer >= %d' % minimum)

    return checkIntValue

  @classmethod
  def strictlyPositiveIntOrRangeType(cls, value):
    checkIntValue = cls.checkIntValueWrapper(minimum=1)

    try:
      return checkIntValue(value)
    except argparse.ArgumentTypeError:
      try:
        min_max_list = value.split(',')
      except ValueError:
        pass
      else:
        if len(min_max_list) == 2:
          minimum, maximum = checkIntValue(min_max_list[0]), \
              checkIntValue(min_max_list[1])

          if minimum >= maximum:
            raise argparse.ArgumentTypeError('%d >= %d' % (minimum, maximum))

          return (minimum, maximum)

    raise argparse.ArgumentTypeError(
      'expects either a strictly positive integer or a range of strictly '
      'positive integer separated by a comma')
