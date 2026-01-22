<dtml-var table_1>.uid = <dtml-var table_0>.category_uid

<dtml-var RELATED_QUERY_SEPARATOR>

<dtml-var table_2>.original_message = <dtml-var table_1>.portal_type
AND <dtml-var table_2>.message_context = "portal_type"
AND <dtml-var table_2>.language = <dtml-sqlvar "Localizer.get_selected_language()" type="string">

<dtml-var RELATED_QUERY_SEPARATOR>

<dtml-var table_0>.uid = catalog.uid
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.causality.getUid()">
