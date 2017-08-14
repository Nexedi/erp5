context.ERP5Site_assertClusterDataNotebookEnabled()
cluster_data_notebook_line = context.newContent(
  portal_type='Cluster Data Notebook Line',
  default_code_body=code)
cluster_data_notebook_line.ClusterDataNotebookLine_postExecution()
# XXX: how to return HALish 201 with X-Location?!
return cluster_data_notebook_line.getRelativeUrl()
