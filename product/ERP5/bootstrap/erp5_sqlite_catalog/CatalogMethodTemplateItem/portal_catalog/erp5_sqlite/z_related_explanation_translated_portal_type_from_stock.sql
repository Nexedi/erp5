<dtml-var table_1>.message_context = "portal_type"
 AND <dtml-var table_1>.language = <dtml-sqlvar "Localizer.get_selected_language()" type="string">
 
<dtml-var RELATED_QUERY_SEPARATOR>

<dtml-var table_1>.original_message = <dtml-var table_0>.portal_type
 AND <dtml-var table_0>.uid = stock.explanation_uid