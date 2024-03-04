select
  date

from
  message_queue

where uid = <dtml-sqlvar uid type="int">