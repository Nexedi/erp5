# -*- coding: UTF-8 -*-
# Copyright (C) 2000-2002  Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Localizer

Adds a new DTML tag:

<dtml-gettext [lang=<language>|lang_expr=<expression>] [verbatim] [catalog=<id>] [data=<expression>]>
    ...
</dtml-gettext>
"""

# Import from Zope
from DocumentTemplate.DT_Util import Eval, ParseError, parse_params, \
     InstanceDict, namespace, render_blocks



# Auxiliar functions
def name_or_expr(mapping, name_attr, expr_attr, default):
    name = mapping.get(name_attr, None)
    expr = mapping.get(expr_attr, None)

    if name is None:
        if expr is None:
            return default
        return Eval(expr)
    if expr is None:
        return name
    raise ParseError('%s and %s given' % (name_attr, expr_attr), 'calendar')



class GettextTag:
    """ """

    name = 'gettext'
    blockContinuations = ()

    def __init__(self, blocks):
        tname, args, section = blocks[0]
        self.section = section.blocks

        args = parse_params(args, lang=None, lang_expr=None, verbatim=1,
                            catalog=None, data=None)

        self.lang = name_or_expr(args, 'lang', 'lang_expr', None)

        self.verbatim = args.get('', None) == 'verbatim' \
                        or args.get('verbatim', None)

        self.catalog = args.get('catalog', None)

        self.data = args.get('data', None)
        if self.data is not None:
            self.data = Eval(self.data)


    def __call__(self, md):
        # In which language, if any?
        lang = self.lang
        if lang is not None and type(lang) is not str:
            lang = lang.eval(md)

        # Get the message!!
        ns = namespace(md)[0]
        md._push(InstanceDict(ns, md))
        message = render_blocks(self.section, md)
        md._pop(1)

        # Interpret the message as verbatim or not
        if not self.verbatim:
            message = ' '.join([ x.strip() for x in message.split() ])

        # Search in a specific catalog
        if self.catalog is None:
            gettext = md.getitem('gettext', 0)
        else:
            gettext = md.getitem(self.catalog, 0).gettext

        translation = gettext(message, lang)

        # Variable substitution
        if self.data is not None:
            data = self.data.eval(md)
            translation = translation % data

        return translation
