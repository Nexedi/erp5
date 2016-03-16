"""
    This script is an experimental version of what should be a generic OpenOffice importer,
    which is a collection of scripts and UI to import lots of objects to ERP5
    from a spreadsheet. The idea is to let the user map each spreadsheet column with
    one portal type property.
"""
module = context.foo_module

import_file = context.restrictedTraverse('foo_import_data_list').data
return module.Base_importFile(import_file=import_file)
