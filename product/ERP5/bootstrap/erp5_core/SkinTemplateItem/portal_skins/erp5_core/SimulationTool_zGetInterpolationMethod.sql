<dtml-if expr="interpolation_method == 'linear'">
  <dtml-if group_by_time_sequence_list>
    CASE
     WHEN <dtml-var stock_table_id>.mirror_date = <dtml-var stock_table_id>.date THEN 1
     ELSE (
       UNIX_TIMESTAMP(
         IFNULL(
           LEAST(
             IFNULL(slot_at_date, slot_to_date),
             GREATEST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)
           ),
           GREATEST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)
         )
       )
       - UNIX_TIMESTAMP(
         GREATEST(
           IFNULL(
             slot_from_date, TIMESTAMP(0)
           ),
           LEAST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)
         )
       )
     )
     / (
       UNIX_TIMESTAMP(GREATEST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)) -
       UNIX_TIMESTAMP(LEAST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)) ) END
  <dtml-else>
  CASE
     WHEN <dtml-var stock_table_id>.mirror_date = <dtml-var stock_table_id>.date THEN 1
     ELSE (
      UNIX_TIMESTAMP(LEAST(
        <dtml-if interpolation_method_at_date>
          <dtml-sqlvar interpolation_method_at_date type="datetime">
        <dtml-else>
          <dtml-sqlvar interpolation_method_to_date type="datetime">
        </dtml-if>,
            GREATEST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date) ))
       - UNIX_TIMESTAMP(GREATEST(<dtml-sqlvar interpolation_method_from_date type="datetime">,
                  LEAST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date))))
      / ( UNIX_TIMESTAMP(GREATEST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)) -
         UNIX_TIMESTAMP(LEAST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)) ) END
  </dtml-if>
<dtml-elif expr="interpolation_method == 'all_or_nothing'">
  CASE
    WHEN (
      -- movement contained in time frame
      LEAST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)
        >= <dtml-sqlvar interpolation_method_from_date type="datetime"> AND
      GREATEST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)
      <dtml-if interpolation_method_at_date>
        <= <dtml-sqlvar interpolation_method_at_date type="datetime">
      <dtml-else>
        < <dtml-sqlvar interpolation_method_to_date type="datetime">
      </dtml-if>
    ) THEN 1
    ELSE 0
  END
<dtml-elif expr="interpolation_method == 'one_for_all'">
  CASE
    WHEN (
      -- movement overlaps with time frame
      GREATEST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)
        <= <dtml-sqlvar interpolation_method_from_date type="datetime"> OR
      LEAST(<dtml-var stock_table_id>.date, <dtml-var stock_table_id>.mirror_date)
      <dtml-if interpolation_method_at_date>
        >= <dtml-sqlvar interpolation_method_at_date type="datetime">
      <dtml-else>
        > <dtml-sqlvar interpolation_method_to_date type="datetime">
      </dtml-if>
    ) THEN 0
    ELSE 1
  END
<dtml-else>
  1
</dtml-if>
