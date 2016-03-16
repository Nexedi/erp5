# Host:
# Database: test
# Table: 'stock'
#
CREATE TABLE `stock` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `node_uid` BIGINT UNSIGNED,
  `section_uid` BIGINT UNSIGNED,
  `payment_uid` BIGINT UNSIGNED,
  `function_uid` BIGINT UNSIGNED,
  `project_uid` BIGINT UNSIGNED,
  `mirror_section_uid` BIGINT UNSIGNED,
  `mirror_node_uid` BIGINT UNSIGNED,
  `resource_uid` BIGINT UNSIGNED,
  `quantity` real ,
  `date` datetime,
  `total_price` real ,
  `portal_type` VARCHAR(255),
  `simulation_state` varchar(255) default '',
  `variation_text` VARCHAR(255),
  `sub_variation_text` VARCHAR(255),
  KEY `uid` (`uid`),
  KEY `quantity` (`quantity`),
  KEY `section_uid` (`section_uid`),
  KEY `mirror_section_uid` (`mirror_section_uid`),
  KEY `mirror_node_uid` (`mirror_node_uid`),
  KEY `node_uid` (`node_uid`),
  KEY `payment_uid` (`payment_uid`),
  KEY `function_uid` (`function_uid`),
  KEY `project_uid` (`project_uid`),
  KEY `resource_uid` (`resource_uid`),
  KEY `simulation_state` (`simulation_state`),
  KEY `resource_node_uid` (`resource_uid`, `node_uid`),
  KEY `resource_section_node_uid` (`resource_uid`, `section_uid`, `node_uid`, `simulation_state`)
) TYPE = ndb;
