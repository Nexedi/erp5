DELETE FROM
  shadir
WHERE
<dtml-sqltest uid type="int" multiple>

<dtml-var sql_delimiter>

<dtml-let
    a2b_hex="__import__('binascii').a2b_hex"
    loads="__import__('json').loads"
    row_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "getFollowUp[loop_item]">
      <dtml-let data="loads(loads(getData[loop_item])[0])">
        <dtml-call expr="row_list.append((uid[loop_item], a2b_hex(data['sha512']), data.get('url')))">
      </dtml-let>
    </dtml-if>
  </dtml-in>
  <dtml-if row_list>
INSERT INTO
  shadir
VALUES
    <dtml-in row_list prefix="row">
(
  <dtml-sqlvar expr="row_item[0]" type="int">,
  <dtml-sqlvar expr="row_item[1]" type="string">,
  <dtml-sqlvar expr="row_item[2]" type="string">
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>
