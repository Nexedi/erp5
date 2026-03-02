DELETE FROM deleted_catalog
WHERE deletion_timestamp < DATE_ADD(NOW(), INTERVAL -1 WEEK)