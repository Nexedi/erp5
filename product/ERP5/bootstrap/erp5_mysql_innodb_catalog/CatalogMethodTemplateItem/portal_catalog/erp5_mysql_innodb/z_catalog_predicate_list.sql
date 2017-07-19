DELETE FROM
  predicate
WHERE
<dtml-sqltest uid type="int" multiple>

<dtml-var sql_delimiter>

<dtml-let predicate_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "isPredicate[loop_item]">
      <dtml-if expr="_.len(predicate_property_dict[loop_item]) > 0">
        <dtml-call expr="predicate_list.append(loop_item)">
      </dtml-if>
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(predicate_list) > 0">
INSERT INTO predicate VALUES
    <dtml-in prefix="loop" expr="predicate_list">
      <dtml-if sequence-start><dtml-else>,</dtml-if>
( 
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="predicate_property_dict[loop_item].get('quantity', None)" type="float" optional>,
  <dtml-sqlvar expr="predicate_property_dict[loop_item].get('quantity_range_min', None)" type="float" optional>,
  <dtml-sqlvar expr="predicate_property_dict[loop_item].get('quantity_range_max', None)" type="float" optional>,
  <dtml-sqlvar expr="predicate_property_dict[loop_item].get('start_date', None)" type="datetime" optional>,
  <dtml-sqlvar expr="predicate_property_dict[loop_item].get('start_date_range_min', None)" type="datetime" optional>,
  <dtml-sqlvar expr="predicate_property_dict[loop_item].get('start_date_range_max', None)" type="datetime" optional>
)
    </dtml-in>
  </dtml-if>
</dtml-let>
