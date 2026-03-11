SELECT uid, path FROM deleted_catalog WHERE <dtml-sqltest column="deletion_timestamp" expr="timestamp" op="ge" type="datetime">
