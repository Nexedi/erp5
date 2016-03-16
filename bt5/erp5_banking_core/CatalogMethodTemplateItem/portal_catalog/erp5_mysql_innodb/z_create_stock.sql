# Host:
# Database: test
# Table: 'stock'
#
CREATE TABLE `stock` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `order_id` TINYINT UNSIGNED NOT NULL,
  `node_uid` BIGINT UNSIGNED,
  `section_uid` BIGINT UNSIGNED,
  `payment_uid` BIGINT UNSIGNED,
  `explanation_uid` BIGINT UNSIGNED,
  `mirror_section_uid` BIGINT UNSIGNED,
  `mirror_node_uid` BIGINT UNSIGNED,
  `resource_uid` BIGINT UNSIGNED,
  `quantity` real ,
  `is_cancellation` BOOLEAN, 
  `date` datetime,
  `total_price` real ,
  `portal_type` VARCHAR(255),
  `simulation_state` varchar(255) default '',
  `variation_text` VARCHAR(255),
  `sub_variation_text` VARCHAR(255),
  PRIMARY KEY (`uid`, `order_id`),
  KEY `quantity` (`quantity`),
  KEY `section_uid` (`section_uid`),
  KEY `node_uid` (`node_uid`),
  KEY `payment_uid` (`payment_uid`),
  KEY `explanation_uid` (`explanation_uid`),
  KEY `resource_uid` (`resource_uid`),
  KEY `simulation_state` (`simulation_state`),
  KEY `resource_node_uid` (`resource_uid`, `node_uid`),
  KEY `resource_section_node_uid_state` (`resource_uid`, `section_uid`, `node_uid`, `simulation_state`),
  KEY `resource_payment_state` (`resource_uid`, `payment_uid`, `simulation_state`),
  KEY `resource_payment_uid` (`resource_uid`, `payment_uid`),
  KEY `resource_payment_state_date` (`resource_uid`, `payment_uid`, `simulation_state`, `date`),
  KEY `node_resource_variation_state_date` (`node_uid`, `resource_uid`, `variation_text`, `simulation_state`, `date`)
) ENGINE=InnoDB;
