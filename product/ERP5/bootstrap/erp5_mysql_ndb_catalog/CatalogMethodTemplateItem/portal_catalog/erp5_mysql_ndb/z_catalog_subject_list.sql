REPLACE INTO subject VALUES 
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
  <dtml-if sequence-start><dtml-else>,</dtml-if>
  <dtml-let subject="Subject[loop_item]">
    <dtml-if subject>
      <dtml-in prefix="word" expr="subject.split()">
<dtml-if sequence-start><dtml-else>,</dtml-if>
(<dtml-sqlvar "uid[loop_item]" type="int">, <dtml-sqlvar word_item type="string">)
      </dtml-in>
    <dtml-else>
(<dtml-sqlvar "uid[loop_item]" type="int">, NULL)
    </dtml-if>
  </dtml-let>
</dtml-in>
