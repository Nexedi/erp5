data_analysis = context.getPortalObject().restrictedTraverse(
  data_analysis_relative_url)
data_analysis\
  .activate(serialization_tag=str(data_analysis.getUid()))\
  .DataAnalysis_executeDataOperation()
