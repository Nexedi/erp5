SELECT original_message, portal_type
FROM translation
<dtml-sqlgroup where>
  <dtml-sqltest language type="string" op="eq"> <dtml-and>
  <dtml-sqltest message_context type="string" op="eq"> <dtml-and>
  <dtml-sqlgroup>
    <dtml-if expr="'=' in translated_message_dict">
      <dtml-sqltest column="translated_message" type="string" op="eq" expr="translated_message_dict['=']" multiple> <dtml-var logical_operator>
    </dtml-if>
    <dtml-if expr="'!=' in translated_message_dict">
      <dtml-sqltest column="translated_message" type="string" op="ne" expr="translated_message_dict['!=']" multiple> <dtml-var logical_operator>
    </dtml-if>
    <dtml-if expr="'<' in translated_message_dict"><dtml-in expr="translated_message_dict['<']" prefix="value">
      <dtml-sqltest column="translated_message" type="string" op="lt" expr="value_item"> <dtml-var logical_operator>
    </dtml-in></dtml-if>
    <dtml-if expr="'<=' in translated_message_dict"><dtml-in expr="translated_message_dict['<=']" prefix="value">
      <dtml-sqltest column="translated_message" type="string" op="le" expr="value_item"> <dtml-var logical_operator>
    </dtml-in></dtml-if>
    <dtml-if expr="'>' in translated_message_dict"><dtml-in expr="translated_message_dict['>']" prefix="value">
      <dtml-sqltest column="translated_message" type="string" op="gt" expr="value_item"> <dtml-var logical_operator>
    </dtml-in></dtml-if>
    <dtml-if expr="'>=' in translated_message_dict"><dtml-in expr="translated_message_dict['>=']" prefix="value">
      <dtml-sqltest column="translated_message" type="string" op="ge" expr="value_item"> <dtml-var logical_operator>
    </dtml-in></dtml-if>
    <dtml-if expr="'like' in translated_message_dict"><dtml-in expr="translated_message_dict['like']" prefix="value">
      <dtml-sqltest column="translated_message" type="string" op="like" expr="value_item"> <dtml-var logical_operator>
    </dtml-in></dtml-if>
    <dtml-if expr="logical_operator == 'and'">1<dtml-else>0</dtml-if>
  </dtml-sqlgroup>
</dtml-sqlgroup>