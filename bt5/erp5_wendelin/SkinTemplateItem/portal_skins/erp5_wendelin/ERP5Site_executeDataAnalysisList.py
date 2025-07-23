portal = context.getPortalObject()

consuming_analysis_list_dict = {}

def add_consuming_analysis(producing_analysis_relative_url, consuming_analysis_relative_url):
  consuming_analysis_list = consuming_analysis_list_dict.setdefault(producing_analysis_relative_url, [])
  consuming_analysis_list.append(consuming_analysis_relative_url)

# First we split all started Data Analysis documents into documents with transient
# inputs and without transient inputs. Documents without transient inputs
# are added to 'data_analysis_list'.
data_analysis_list = []
for data_analysis in portal.portal_catalog(portal_type = "Data Analysis",
                                           simulation_state = "started"):
  has_transient_input = False
  for line in data_analysis.objectValues(portal_type="Data Analysis Line"):
    if line.getUse() == "big_data/analysis/transient" and line.getQuantity() < 0:
      has_transient_input = True
      add_consuming_analysis(line.getParentValue().getCausality(), line.getParentRelativeUrl())
  if not has_transient_input:
    data_analysis_list.append(data_analysis)

# Now we will activate `executeDataOperation` on given Data Analysis documents
for data_analysis in data_analysis_list:
  if not data_analysis.hasActivity():
    if data_analysis.getRefreshState() in ("current", "refresh_started"):
      consuming_analysis_list = consuming_analysis_list_dict.get(data_analysis.getRelativeUrl(), [])
      data_analysis.activate(serialization_tag=str(data_analysis.getUid()))\
        .DataAnalysis_executeDataOperation(consuming_analysis_list)

# Finally we refresh specified Data Analysis documents
for data_analysis in portal.portal_catalog(portal_type = "Data Analysis",
                                           refresh_state = "refresh_planned"):
  if data_analysis.getRefreshState() == "refresh_planned":
    if not data_analysis.hasActivity():
      data_analysis.activate(serialization_tag=str(data_analysis.getUid()))\
        .DataAnalysis_clearAndReprocessFromScratch()
