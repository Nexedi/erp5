##parameters=form_id,cancel_url

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST

request[ 'RESPONSE' ].redirect( cancel_url )
