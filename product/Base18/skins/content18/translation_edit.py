## Script (Python) "translation_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=target_content, target_language, text, file='', SafetyBelt='', choice=' Change '
##title=Edit a document
##
##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
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
#try:
if 1:
    target_content = context.restrictedTraverse(target_content, None)
    context.edit( ''
                , text
                , file
                , safety_belt=SafetyBelt
                , target_language=target_language
                , target_content=target_content
                )
    qst='portal_status_message=Document+changed.'

    if choice == ' Change and View ':
        target_action = context.getTypeInfo().getActionById( 'view' )
    else:
        target_action = context.getTypeInfo().getActionById( 'edit' )

    context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
#except Exception, msg:
#    target_action = context.getTypeInfo().getActionById( 'edit' )
#    context.REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (
#                                                                       context.absolute_url()
#                                                                     , target_action
#                                                                     , msg
#                                                                     ))
