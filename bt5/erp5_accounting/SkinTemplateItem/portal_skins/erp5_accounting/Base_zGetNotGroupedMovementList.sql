<dtml-comment>Returns all movements <= at_date which does not have a grouping
reference or having a grouping reference with movements where date is after the
at_date. 

Here, a group of movement means:
 section_uid is from section_uid:list, or is the same if section_uid is not passed.
 mirror_section_uid is the same
 node_uid is the same
 grouping_reference is the same

XXX now that grouping_date exists, this script will become useless.
Please consider using grouping date query with getMovementHistoryList instead of
using this obsolete script.

</dtml-comment>

( SELECT catalog.path as path,
         catalog.uid as uid,
         mirror_section.relative_url as mirror_section_relative_url,
         mirror_section.title as mirror_section_title,
         stock.mirror_section_uid,
         stock.date as date_utc,
         stock.node_uid as node_uid,
         IFNULL(stock.total_price, 0) as total_price,
         IFNULL(stock.quantity, 0) as total_quantity

  FROM catalog, stock LEFT JOIN catalog AS mirror_section on 
        ( stock.mirror_section_uid = mirror_section.uid )

  WHERE stock.node_uid in (<dtml-in node_uid><dtml-var sequence-item>
         <dtml-unless sequence-end>, </dtml-unless></dtml-in>) and
       <dtml-if simulation_state>
        stock.simulation_state in (<dtml-in simulation_state>
            <dtml-sqlvar sequence-item type="string">
         <dtml-unless sequence-end>, </dtml-unless> </dtml-in simulation_state> ) and
       </dtml-if>
        stock.portal_type in (<dtml-in portal_type>
            <dtml-sqlvar sequence-item type="string">
         <dtml-unless sequence-end>, </dtml-unless> </dtml-in portal_type> ) and
       <dtml-if section_uid>
        stock.section_uid in (<dtml-in section_uid><dtml-var sequence-item>
         <dtml-unless sequence-end>, </dtml-unless> </dtml-in section_uid> ) and
       </dtml-if>
        catalog.uid=stock.uid and
        stock.date <= <dtml-sqlvar "at_date" type="datetime"> and
        catalog.grouping_reference is NULL
) UNION (
  SELECT
      catalog.path as path,
      catalog.uid as uid,
      mirror_section.relative_url as mirror_section_relative_url,
      mirror_section.title as mirror_section_title,
      stock.mirror_section_uid,
      stock.date as date_utc,
      stock.node_uid as node_uid,
      IFNULL(stock.total_price, 0) as total_price,
      IFNULL(stock.quantity, 0) as total_quantity

  FROM  catalog AS catalog_2, stock AS stock_2, 
        catalog AS catalog, stock AS stock LEFT JOIN catalog AS mirror_section
        ON ( stock.mirror_section_uid = mirror_section.uid )

  WHERE stock.node_uid in (<dtml-in node_uid><dtml-var sequence-item>
         <dtml-unless sequence-end>, </dtml-unless></dtml-in>) and
       <dtml-if simulation_state>
        stock.simulation_state in (<dtml-in simulation_state>
            <dtml-sqlvar sequence-item type="string">
         <dtml-unless sequence-end>, </dtml-unless> </dtml-in simulation_state> ) and
       </dtml-if>
        stock.portal_type in (<dtml-in portal_type>
            <dtml-sqlvar sequence-item type="string">
         <dtml-unless sequence-end>, </dtml-unless> </dtml-in portal_type> ) and
       <dtml-if section_uid>
        stock.section_uid in (<dtml-in section_uid><dtml-var sequence-item>
         <dtml-unless sequence-end>, </dtml-unless> </dtml-in section_uid> ) and
       </dtml-if>
        stock.date <= <dtml-sqlvar "at_date" type="datetime"> and
        catalog.uid = stock.uid and
        catalog_2.uid = stock_2.uid and
        catalog.grouping_reference = catalog_2.grouping_reference and
        catalog.grouping_reference is not NULL and
       <dtml-if section_uid>
        stock_2.section_uid in (<dtml-in section_uid><dtml-var sequence-item>
         <dtml-unless sequence-end>, </dtml-unless> </dtml-in section_uid> ) and
       <dtml-else>
        stock_2.section_uid = stock.section_uid and
       </dtml-if>
        stock.mirror_section_uid = stock_2.mirror_section_uid and
        stock_2.simulation_state != 'cancelled' and
        stock.node_uid = stock_2.node_uid
  GROUP BY catalog.uid, stock.uid
  HAVING max(stock_2.date) > <dtml-sqlvar "at_date" type="datetime">
)

ORDER BY mirror_section_title, date_utc