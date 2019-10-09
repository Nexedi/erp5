# -*- coding: utf-8 -*-
#
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from __future__ import absolute_import
from inspect import getargspec
import sys

try:
    # TODO: Add support for newer versions pylint. Meanwhile, make sure that
    #       trying to use it does not import isort, because the latter hacks
    #       Python in order to execute:
    #           sys.setdefaultencoding('utf-8')
    #       This changes the behaviour of some ERP5 code.
    sys.modules.setdefault('isort', None)

    from pylint.checkers.imports import ImportsChecker
    import astroid
    ImportsChecker.get_imported_module
except (AttributeError, ImportError):
    pass
else:
    def _get_imported_module(self, importnode, modname):
        try:
            return importnode.do_import_module(modname)
        except astroid.InferenceError, ex:
            # BEGIN

            # XXX-arnau: Ignore ERP5 dynamic modules, hackish but required
            # until proper introspection is implemented because otherwise it
            # is impossible to validate Components importing other Components
            # and as it is static analysis, the module should not be loaded
            # anyway
            if modname.startswith('erp5'):
                return

            # Handle ImportError try/except checking for missing module before
            # falling back to code handling such case (#9386)
            pnode = importnode.parent
            if pnode and isinstance(pnode, astroid.TryExcept):
                for handler in pnode.handlers:
                    # Handling except:
                    if not handler.type:
                        return

                    # Handling ImportError and its Exception base classes
                    for klass in ImportError.mro():
                        if klass is object:
                            break
                        elif klass.__name__ == handler.type.name:
                            return
            # END

            if str(ex) != modname:
                args = '%r (%s)' % (modname, ex)
            else:
                args = repr(modname)
            self.add_message("F0401", args=args, node=importnode)

    if 'modnode' in getargspec(ImportsChecker.get_imported_module).args:
        # BBB for pylint < 1.4.0
        def get_imported_module(self, modnode, importnode, modname):
            return _get_imported_module(self, importnode, modname)
    else:
        get_imported_module = _get_imported_module

    ImportsChecker.get_imported_module = get_imported_module

    # All arguments are passed as arguments and this needlessly outputs a 'No
    # config file found, using default configuration' message on stderr.
    from logilab.common.configuration import OptionsManagerMixIn
    OptionsManagerMixIn.read_config_file = lambda *args, **kw: None

finally:
    if sys.modules['isort'] is None:
        del sys.modules['isort']
