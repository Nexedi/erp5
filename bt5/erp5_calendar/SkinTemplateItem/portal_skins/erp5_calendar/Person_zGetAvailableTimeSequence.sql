<dtml-in period_list prefix="loop">
  (
    <dtml-var expr="Person_zGetAvailableTime(from_date=loop_key, to_date=loop_item, 
                                             node=node, portal_type=portal_type,
                                             resource=resource,
                                             src__=1)">
  )
  <dtml-unless sequence-end> UNION ALL </dtml-unless> 
</dtml-in>
