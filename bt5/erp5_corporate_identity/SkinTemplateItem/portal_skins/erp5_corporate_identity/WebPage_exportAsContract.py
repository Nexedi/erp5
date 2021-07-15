# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

return context.WebPage_viewAsContract(
  document_save=document_save,
  display_svg=display_svg,
  batch_mode=batch_mode,
  include_content_table=include_content_table,
  include_history_table=include_history_table,
  include_reference_table=include_reference_table,
  include_linked_content=include_linked_content,
  include_report_content=include_report_content,
  format=format,
  **kw
)
