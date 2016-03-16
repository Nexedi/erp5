<dtml-let content_translation_dict_list="CatalogTool_getContentTranslationDictList(Base_getContentTranslationTargetObject)">
<dtml-if "content_translation_dict_list">
REPLACE INTO content_translation
VALUES
<dtml-in "content_translation_dict_list">
(<dtml-sqlvar "_['sequence-item']['uid']" type=int>,
 <dtml-sqlvar "_['sequence-item']['property_name']" type=string>,
 <dtml-sqlvar "_['sequence-item']['content_language']" type=string>,
 <dtml-sqlvar "_['sequence-item']['translated_text']" type=string>
)
<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>
</dtml-if>
</dtml-let>
