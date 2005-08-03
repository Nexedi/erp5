# -*- coding: ISO-8859-1 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

from scribus import *
import re

TITLE = "Mayoro: Modifing Styles of text fields"
BUTTON_OK = 1
ICON_INFORMATION = 1
ICON_WARNING = 2

# Modification des zones pour les montants
if HaveDoc():
        words = 0
        source = "whole document"
        for page in range(PageCount()):
                GotoPage(page)
                for obj in GetAllObjects():
                        #input_field = GetTextFrame(obj)
                        try:
                             SetTextAlignment(2, obj)  # 2 = right
                             SetFont("Courier 10 Pitch Regular", obj)
                             SetFontSize(14, obj)
                             words += 1
                        except:
                             pass
        if words == 0: words = "No"
        MessageBox(TITLE, "%s text fields modified in %s" % (words, source),ICON_INFORMATION, BUTTON_OK)
else:
        MessageBox(TITLE, "Not document open", ICON_WARNING, BUTTON_OK)




# Modfication des entêtes
# if HaveDoc():
#         words = 0
#         source = "selected textframe"
#         sel_count = SelectionCount()
#         if sel_count:
#               for i in range(sel_count):
#                     obj = GetSelectedObject(i)
#                     try:
#                           SetTextAlignment(0, obj)  # 0 = left
#                           SetFont("Courier 10 Pitch Regular", obj)
#                           SetFontSize(11, obj)
#                           words += 1
#                     except:
#                           pass
#         if words == 0: words = "No"
#         MessageBox(TITLE, "%s text fields modified in %s" % (words, source),ICON_INFORMATION, BUTTON_OK)
# else:
#         MessageBox(TITLE, "Not document open", ICON_WARNING, BUTTON_OK)
