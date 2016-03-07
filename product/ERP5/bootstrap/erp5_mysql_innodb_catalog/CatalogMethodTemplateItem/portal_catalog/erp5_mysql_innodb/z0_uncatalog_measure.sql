<dtml-comment>
  JM: Since unindexing a measure triggers the reindexing of the related
  resource (what will clean the measure table - cf z0_catalog_measure_list),
  is it required to delete according to uid column?
  The test against metric_type_uid is there in case we delete a metric_type_uid
  category that is used as an implicit measure.
</dtml-comment>
DELETE FROM measure
WHERE <dtml-sqltest uid op=eq type=int>
   OR <dtml-sqltest uid op=eq type=int column="metric_type_uid">
