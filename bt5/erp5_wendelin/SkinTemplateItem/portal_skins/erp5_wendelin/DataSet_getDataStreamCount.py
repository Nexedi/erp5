"""
Get count of Data Streams for context Data set.
"""
return context.ERP5Site_getDataStreamCount(data_set_reference=context.getReference())['result']
