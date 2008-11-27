##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho Teixeira  <lucas@nexedi.com>
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
import re

def compressCSS(css):
    """
      CSS file compressor
      This compressor remove the comments, eol
      and all the possible tabs.
    """
    white_space_regex = re.compile("[\n|\t|\r]")
    commment_regex =  re.compile("/\*.*?\*/")
    class_regex = re.compile(r"([^{]*?){(.*?)}")
    style = re.compile(r"([\w\s-]*):([^;]*);?")
    css = commment_regex.sub('', white_space_regex.sub("", css)) 
    return '\n'.join(["%s{%s}" % (x[0].strip(), \
           ''.join(["%s:%s;" % (y[0].strip(), y[1].strip()) \
           for y in style.findall(x[1])])) for x in class_regex.findall(css)])

