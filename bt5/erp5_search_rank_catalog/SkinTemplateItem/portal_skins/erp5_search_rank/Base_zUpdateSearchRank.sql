UPDATE `search_rank`
SET `search_rank` = <dtml-sqlvar search_rank type="int">
WHERE `uid` = <dtml-sqlvar uid type="int">