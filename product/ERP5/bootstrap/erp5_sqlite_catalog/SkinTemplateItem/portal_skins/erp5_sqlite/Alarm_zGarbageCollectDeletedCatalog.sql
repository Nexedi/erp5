DELETE FROM deleted_catalog
WHERE deletion_timestamp < datetime('now', '-7 days');