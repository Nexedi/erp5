assert button == 'forbarcontent', button

return context.Base_renderForm('Foo_viewFieldSubmitDialog', message='Field Action Submitted', keep_items={'your_integer_1': integer_1 + 1})
