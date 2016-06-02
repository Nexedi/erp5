<dtml-let content_translation_dict_list="CatalogTool_getContentTranslationDictList(Base_getContentTranslationTargetObject)">
<dtml-let document_list="[]" delete_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(content_translation_dict_list))">
    <dtml-if "content_translation_dict_list[loop_item]['translated_text']">
      <dtml-call expr="document_list.append(loop_item)">
    <dtml-else>
      <dtml-call expr="delete_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(document_list) > 0">
REPLACE INTO content_translation
VALUES
    <dtml-in prefix="loop" expr="document_list">
(<dtml-sqlvar "content_translation_dict_list[loop_item]['uid']" type=int>,
 <dtml-sqlvar "content_translation_dict_list[loop_item]['property_name']" type=string>,
 <dtml-sqlvar "content_translation_dict_list[loop_item]['content_language']" type=string>,
 <dtml-sqlvar "content_translation_dict_list[loop_item]['translated_text']" type=string>
)
<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>
  </dtml-if>
  <dtml-if expr="_.len(delete_list) > 0">
<dtml-var sql_delimiter>
DELETE FROM content_translation
WHERE
  (uid, property_name, content_language) IN (<dtml-in prefix="loop" expr="delete_list">
(<dtml-sqlvar "content_translation_dict_list[loop_item]['uid']" type=int>,
 <dtml-sqlvar "content_translation_dict_list[loop_item]['property_name']" type=string>,
 <dtml-sqlvar "content_translation_dict_list[loop_item]['content_language']" type=string>
)
<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>)
</dtml-if>
</dtml-let>
</dtml-let>
