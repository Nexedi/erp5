REPLACE INTO
  catalog
  (`uid`, `security_uid`, `owner`, `viewable_owner`, `path`, `relative_url`, `parent_uid`, `id`, `description`, `title`, `meta_type`,
   `portal_type`, `opportunity_state`, `corporate_registration_code`, `ean13_code`, `validation_state`, `simulation_state`,
   `causality_state`, `invoice_state`, `payment_state`, `event_state`, `immobilisation_state`, `reference`, `grouping_reference`, `grouping_date`,
   `source_reference`, `destination_reference`, `string_index`, `int_index`, `float_index`, `has_cell_content`, `creation_date`,
   `modification_date`)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
