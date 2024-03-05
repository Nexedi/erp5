DELETE FROM
  shadir
WHERE
<dtml-sqltest uid type="int" multiple>

<dtml-var sql_delimiter>

<dtml-let
    loads="__import__('json').loads"
    tostr="lambda x: x.encode('utf-8') if type(x) is unicode else x"
    row_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "getFollowUp[loop_item] and getContentType[loop_item] == 'application/json'">
      <dtml-let data="loads(loads(getData[loop_item])[0])">
        <dtml-call expr="row_list.append((uid[loop_item], data['sha512'], getFilename[loop_item] or None, ';'.join(['%s=%r' % (x, tostr(data[x])) for x in ('file', 'requirement', 'revision', 'software_url', 'os', 'url') if data.get(x)]) or None))">
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
  x'<dtml-var expr="row_item[1]">',
  <dtml-sqlvar expr="row_item[2]" type="string" optional>,
  <dtml-sqlvar expr="row_item[3]" type="string" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>
