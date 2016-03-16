select distinct(stock.payment_uid) 
from stock 
where 
  (1)
  <dtml-if account_uid_list>
    and
    stock.payment_uid in (
     <dtml-in account_uid_list>
       <dtml-unless sequence-start>, </dtml-unless>
       <dtml-sqlvar sequence-item type="int">
     </dtml-in>
     ) 
  </dtml-if>
  and stock.payment_uid is not NULL  
  and stock.payment_uid != ""