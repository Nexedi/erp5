## Script (Python) "Organisation_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST

try:
  # Validate the form
  context.Organisation_view.validate_all_to_request(request)
  context.edit(id=request.my_id
             , title=request.my_title
             , corporate_name = request.my_corporate_name
      , description = request.my_description)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = context.Organisation_view.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return context.Organisation_view(request)
else:
  redirect_url = '%s/Organisation_view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=Data+Updated.'
                                  )

request[ 'RESPONSE' ].redirect( redirect_url )
