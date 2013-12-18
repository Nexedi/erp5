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

try:
    from pylint.checkers import imports
    import astroid
except ImportError:
    pass
else:
    def get_imported_module(self, modnode, importnode, modname):
        try:
            return importnode.do_import_module(modname)
        except astroid.InferenceError, ex:
            # BEGIN
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

    imports.ImportsChecker.get_imported_module = get_imported_module
