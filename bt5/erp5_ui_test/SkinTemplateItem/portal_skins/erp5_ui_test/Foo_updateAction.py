"""Call the Foo_viewDummyDialog"""
return context.Base_renderForm(
  'Foo_viewDummyDialog',
  message='"Update" action is done with "%s".' % string_field,
  keep_items={
    'key_posted_during_on_update': 'A value pushed by update action'
  }
)
