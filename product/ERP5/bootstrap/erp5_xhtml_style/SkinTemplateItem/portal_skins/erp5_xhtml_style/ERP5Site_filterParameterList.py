kept_names = ('editable_mode', 'ignore_layout',            # erp5_web
              'selection_name', 'selection_index',         # list mode
              'selection_key',                             # list mode
              'bt_list',                                   # business template installation system
              'ignore_hide_rows',
             )
# Dialog mode is absent from the kept_name list on purpose :
# none of its variable should ever get transmited because
# it's the deepest level of navigation.
# Cancel url is always overwritten, except when rendering
# a dialog. So this is safe to propagate it.

return dict((item for item in list(parameter_list.items()) if item[0] in kept_names))
