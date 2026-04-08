<dtml-let row_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(subject_set_uid))">
    <dtml-if expr="optimised_subject_list[loop_item]">
      <dtml-in prefix="role" expr="optimised_subject_list[loop_item]">
        <dtml-call expr="row_list.append([subject_set_uid[loop_item], role_item])">
      </dtml-in>
    </dtml-if>
  </dtml-in>
  <dtml-if expr="row_list">
INSERT INTO
  subject
  (`subject_set_uid`,  `subject`)
VALUES
    <dtml-in prefix="row" expr="row_list">
(<dtml-sqlvar expr="row_item[0]" type="string">, <dtml-sqlvar expr="row_item[1]" type="string">)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>
