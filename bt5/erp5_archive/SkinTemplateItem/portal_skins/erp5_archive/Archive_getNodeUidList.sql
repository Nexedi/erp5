select distinct(stock.node_uid) 
from stock 
where 
  (1)
  <dtml-if account_uid_list>
    or 
    (stock.payment_uid not in ( 
     <dtml-in account_uid_list>
      <dtml-unless sequence-start>, </dtml-unless>
       <dtml-sqlvar sequence-item type="int">
     </dtml-in>
     ) 
    or stock.payment_uid is NULL
    or stock.payment_uid = "")
  </dtml-if>
  <dtml-if account_node_uid>
    and stock.node_uid != <dtml-sqlvar account_node_uid type="int" >
  </dtml-if>