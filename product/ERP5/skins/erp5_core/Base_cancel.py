## Script (Python) "Base_cancel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,cancel_url
##title=
##
# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST

request[ 'RESPONSE' ].redirect( cancel_url )
