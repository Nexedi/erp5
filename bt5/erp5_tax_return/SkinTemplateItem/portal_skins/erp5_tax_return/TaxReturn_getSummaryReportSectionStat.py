from Products.PythonScripts.standard import Object

return [Object(uid='new_',
               resource_title='Total',
               **container.REQUEST[script.getId()])]
