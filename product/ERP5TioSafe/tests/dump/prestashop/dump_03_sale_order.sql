DROP TABLE IF EXISTS `ps_address`;
CREATE TABLE `ps_address` (
  `id_address` int(10) unsigned NOT NULL auto_increment,
  `id_country` int(10) unsigned NOT NULL,
  `id_state` int(10) unsigned default NULL,
  `id_customer` int(10) unsigned NOT NULL default '0',
  `id_manufacturer` int(10) unsigned NOT NULL default '0',
  `id_supplier` int(10) unsigned NOT NULL default '0',
  `alias` varchar(32) NOT NULL,
  `company` varchar(32) default NULL,
  `lastname` varchar(32) NOT NULL,
  `firstname` varchar(32) NOT NULL,
  `address1` varchar(128) NOT NULL,
  `address2` varchar(128) default NULL,
  `postcode` varchar(12) default NULL,
  `city` varchar(64) NOT NULL,
  `other` text,
  `phone` varchar(16) default NULL,
  `phone_mobile` varchar(16) default NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  `active` tinyint(1) unsigned NOT NULL default '1',
  `deleted` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_address`),
  KEY `address_customer` (`id_customer`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_address` WRITE;
INSERT INTO `ps_address` VALUES (1,21,5,0,1,0,'manufacturer',NULL,'JOBS','STEVE','1 Infinite Loop',NULL,'95014','Cupertino',NULL,'(800) 275-2273',NULL,'2009-09-17 09:48:51','2009-09-17 09:48:51',1,0),(2,8,0,1,0,0,'Mon adresse','My Company','DOE','John','16, Main street','2nd floor','75000','Paris ',NULL,'0102030405',NULL,'2009-09-17 09:48:51','2009-09-17 09:48:51',1,0);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_attribute`;
CREATE TABLE `ps_attribute` (
  `id_attribute` int(10) unsigned NOT NULL auto_increment,
  `id_attribute_group` int(10) unsigned NOT NULL,
  `color` varchar(32) default NULL,
  PRIMARY KEY  (`id_attribute`),
  KEY `attribute_group` (`id_attribute_group`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_attribute` WRITE;
INSERT INTO `ps_attribute` VALUES (1,1,NULL),(2,1,NULL),(3,2,'#D2D6D5'),(4,2,'#008CB7'),(5,2,'#F3349E'),(6,2,'#93D52D'),(7,2,'#FD9812'),(8,1,NULL),(9,1,NULL),(10,3,NULL),(11,3,NULL),(12,1,NULL),(13,1,NULL),(14,2,NULL),(15,1,''),(16,1,''),(17,1,''),(18,2,'#7800F0'),(19,2,'#F6EF04'),(20,2,'#F60409'),(21,4,'#000000'),(22,4,'#000000'),(23,4,'#000000'),(24,4,'#000000'),(25,4,'#000000');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_attribute_group`;
CREATE TABLE `ps_attribute_group` (
  `id_attribute_group` int(10) unsigned NOT NULL auto_increment,
  `is_color_group` tinyint(1) NOT NULL default '0',
  PRIMARY KEY  (`id_attribute_group`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_attribute_group` WRITE;
INSERT INTO `ps_attribute_group` VALUES (1,0),(2,1),(3,0),(4,0);
UNLOCK TABLES;

DROP TABLE IF EXISTS `ps_attribute_group_lang`;
CREATE TABLE `ps_attribute_group_lang` (
  `id_attribute_group` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  `public_name` varchar(64) NOT NULL,
  PRIMARY KEY  (`id_attribute_group`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_attribute_group_lang` WRITE;
INSERT INTO `ps_attribute_group_lang` VALUES (1,1,'Disk space','Disk space'),(1,2,'Capacite','Capacite'),(2,1,'Color','Color'),(2,2,'Couleur','Couleur'),(3,1,'ICU','Processor'),(3,2,'ICU','Processeur'),(4,1,'Size','Size'),(4,2,'Size','Size');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_attribute_impact`;
CREATE TABLE `ps_attribute_impact` (
  `id_attribute_impact` int(10) unsigned NOT NULL auto_increment,
  `id_product` int(11) NOT NULL,
  `id_attribute` int(11) NOT NULL,
  `weight` float NOT NULL,
  `price` decimal(10,2) NOT NULL,
  PRIMARY KEY  (`id_attribute_impact`),
  UNIQUE KEY `id_product` (`id_product`,`id_attribute`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_attribute_impact` WRITE;
INSERT INTO `ps_attribute_impact` VALUES (1,1,2,0,'60.00'),(2,1,5,0,'0.00'),(3,1,16,0,'50.00'),(4,1,15,0,'0.00'),(5,1,4,0,'0.00'),(6,1,19,0,'0.00'),(7,1,3,0,'0.00'),(8,1,14,0,'0.00'),(9,1,7,0,'0.00'),(10,1,20,0,'0.00'),(11,1,6,0,'0.00'),(12,1,18,0,'0.00');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_attribute_lang`;
CREATE TABLE `ps_attribute_lang` (
  `id_attribute` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY  (`id_attribute`,`id_lang`),
  KEY `id_lang` (`id_lang`,`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_attribute_lang` WRITE;
INSERT INTO `ps_attribute_lang` VALUES (1,1,'2GB'),(1,2,'2Go'),(2,1,'4GB'),(2,2,'4Go'),(3,1,'Metal'),(3,2,'Metal'),(4,1,'Blue'),(4,2,'Bleu'),(5,1,'Pink'),(5,2,'Rose'),(6,1,'Green'),(6,2,'Vert'),(7,1,'Orange'),(7,2,'Orange'),(8,1,'Optional 64GB solid-state drive'),(8,2,'Disque dur SSD (solid-state drive) de 64 Go '),(9,1,'80GB Parallel ATA Drive @ 4200 rpm'),(9,2,'Disque dur PATA de 80 Go a 4 200 tr/min'),(10,1,'1.60GHz Intel Core 2 Duo'),(10,2,'Intel Core 2 Duo a 1,6 GHz'),(11,1,'1.80GHz Intel Core 2 Duo'),(11,2,'Intel Core 2 Duo a 1,8 GHz'),(12,1,'80GB: 20,000 Songs'),(12,2,'80 Go : 20 000 chansons'),(13,1,'160GB: 40,000 Songs'),(13,2,'160 Go : 40 000 chansons'),(14,2,'Noir'),(14,1,'Black'),(15,1,'8Go'),(15,2,'8Go'),(16,1,'16Go'),(16,2,'16Go'),(17,1,'32Go'),(17,2,'32Go'),(18,1,'Purple'),(18,2,'Violet'),(19,1,'Yellow'),(19,2,'Jaune'),(20,1,'Red'),(20,2,'Rouge'),(21,1,'S'),(21,2,'S'),(22,1,'M'),(22,2,'M'),(23,1,'L'),(23,2,'L'),(24,1,'L'),(24,2,'XL'),(25,1,'XS'),(25,2,'XS');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_carrier`;
CREATE TABLE `ps_carrier` (
  `id_carrier` int(10) unsigned NOT NULL auto_increment,
  `id_tax` int(10) unsigned default '0',
  `name` varchar(64) NOT NULL,
  `url` varchar(255) default NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  `deleted` tinyint(1) unsigned NOT NULL default '0',
  `shipping_handling` tinyint(1) unsigned NOT NULL default '1',
  `range_behavior` tinyint(1) unsigned NOT NULL default '0',
  `is_module` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_carrier`),
  KEY `deleted` (`deleted`,`active`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_carrier` WRITE;
INSERT INTO `ps_carrier` VALUES (1,0,'0',NULL,1,0,0,0,0),(2,1,'My carrier',NULL,1,0,1,0,0);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_carrier_lang`;
CREATE TABLE `ps_carrier_lang` (
  `id_carrier` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `delay` varchar(128) default NULL,
  UNIQUE KEY `shipper_lang_index` (`id_lang`,`id_carrier`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_carrier_lang` WRITE;
INSERT INTO `ps_carrier_lang` VALUES (1,1,'Pick up in-store'),(1,2,'Retrait au magasin'),(2,1,'Delivery next day!'),(2,2,'Livraison le lendemain !');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_carrier_zone`;
CREATE TABLE `ps_carrier_zone` (
  `id_carrier` int(10) unsigned NOT NULL,
  `id_zone` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_carrier`,`id_zone`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_carrier_zone` WRITE;
INSERT INTO `ps_carrier_zone` VALUES (1,1),(2,1),(2,2);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_category`;
CREATE TABLE `ps_category` (
  `id_category` int(10) unsigned NOT NULL auto_increment,
  `id_parent` int(10) unsigned NOT NULL,
  `level_depth` tinyint(3) unsigned NOT NULL default '0',
  `active` tinyint(1) unsigned NOT NULL default '0',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_category`),
  KEY `category_parent` (`id_parent`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_category` WRITE;
INSERT INTO `ps_category` VALUES (1,0,0,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(2,1,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(3,1,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(4,1,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_category_group`;
CREATE TABLE `ps_category_group` (
  `id_category` int(10) unsigned NOT NULL,
  `id_group` int(10) unsigned NOT NULL,
  KEY `category_group_index` (`id_category`,`id_group`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_category_group` WRITE;
INSERT INTO `ps_category_group` VALUES (1,1),(2,1),(3,1),(4,1);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_category_lang`;
CREATE TABLE `ps_category_lang` (
  `id_category` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  `description` text,
  `link_rewrite` varchar(128) NOT NULL,
  `meta_title` varchar(128) default NULL,
  `meta_keywords` varchar(128) default NULL,
  `meta_description` varchar(128) default NULL,
  UNIQUE KEY `category_lang_index` (`id_category`,`id_lang`),
  KEY `category_name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_category_lang` WRITE;
INSERT INTO `ps_category_lang` VALUES (1,1,'Home','','home',NULL,NULL,NULL),(1,2,'Accueil','','home',NULL,NULL,NULL),(2,1,'iPods','Now that you can buy movies from the iTunes Store and sync them to your iPod, the whole world is your theater.','music-ipods','','',''),(2,2,'iPods','Il est temps, pour le meilleur lecteur de musique, de remonter sur scene pour un rappel. Avec le nouvel iPod, le monde est votre scene.','musique-ipods','','',''),(3,1,'Accessories','Wonderful accessories for your iPod','accessories-ipod','','',''),(3,2,'Accessoires','Tous les accessoires a la mode pour votre iPod','accessoires-ipod','','',''),(4,1,'Laptops','The latest Intel processor, a bigger hard drive, plenty of memory, and even more new features all fit inside just one liberating inch. The new Mac laptops have the performance, power, and connectivity of a desktop computer. Without the desk part.','laptops','Apple laptops','Apple laptops MacBook Air','Powerful and chic Apple laptops'),(4,2,'Portables','Le tout dernier processeur Intel, un disque dur plus spacieux, de la memoire a profusion et d\'autres nouveautes. Le tout, dans a peine 2,59 cm qui vous liberent de toute entrave. Les nouveaux portables Mac reunissent les performances, la puissance et la connectivite d\'un ordinateur de bureau. Sans la partie bureau.','portables-apple','Portables Apple','portables apple macbook air','portables apple puissants et design');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_category_product`;
CREATE TABLE `ps_category_product` (
  `id_category` int(10) unsigned NOT NULL,
  `id_product` int(10) unsigned NOT NULL,
  `position` int(10) unsigned NOT NULL default '0',
  KEY `category_product_index` (`id_category`,`id_product`),
  KEY `id_product` (`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


LOCK TABLES `ps_category_product` WRITE;
INSERT INTO `ps_category_product` VALUES (1,1,0),(1,2,1),(1,6,2),(1,7,3),(2,1,0),(2,2,1),(2,7,2),(3,8,0),(3,9,1),(4,5,0),(4,6,1),(1,10,4),(1,11,5);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_country`;
CREATE TABLE `ps_country` (
  `id_country` int(10) unsigned NOT NULL auto_increment,
  `id_zone` int(10) unsigned NOT NULL,
  `iso_code` varchar(3) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  `contains_states` tinyint(1) NOT NULL default '0',
  PRIMARY KEY  (`id_country`),
  KEY `country_iso_code` (`iso_code`),
  KEY `country_` (`id_zone`)
) ENGINE=MyISAM AUTO_INCREMENT=245 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_country` WRITE;
INSERT INTO `ps_country` VALUES (1,1,'DE',1,0),(2,1,'AT',1,0),(3,1,'BE',1,0),(4,2,'CA',1,0),(5,3,'CN',1,0),(6,1,'ES',1,0),(7,1,'FI',1,0),(8,1,'FR',1,0),(9,1,'GR',1,0),(10,1,'IT',1,0),(11,3,'JP',1,0),(12,1,'LU',1,0),(13,1,'NL',1,0),(14,1,'PL',1,0),(15,1,'PT',1,0),(16,1,'CZ',1,0),(17,1,'GB',1,0),(18,1,'SE',1,0),(19,1,'CH',1,0),(20,1,'DK',1,0),(21,2,'US',1,1),(22,3,'HK',1,0),(23,1,'NO',1,0),(24,5,'AU',1,0),(25,3,'SG',1,0),(26,1,'IE',1,0),(27,5,'NZ',1,0),(28,3,'KR',1,0),(29,3,'IL',1,0),(30,4,'ZA',1,0),(31,4,'NG',1,0),(32,4,'CI',1,0),(33,4,'TG',1,0),(34,2,'BO',1,0),(35,4,'MU',1,0),(143,1,'HU',1,0),(36,1,'RO',1,0),(37,1,'SK',1,0),(38,4,'DZ',1,0),(39,2,'AS',1,0),(40,1,'AD',1,0),(41,4,'AO',1,0),(42,2,'AI',1,0),(43,2,'AG',1,0),(44,2,'AR',1,0),(45,3,'AM',1,0),(46,2,'AW',1,0),(47,3,'AZ',1,0),(48,2,'BS',1,0),(49,3,'BH',1,0),(50,3,'BD',1,0),(51,2,'BB',1,0),(52,1,'BY',1,0),(53,2,'BZ',1,0),(54,4,'BJ',1,0),(55,2,'BM',1,0),(56,3,'BT',1,0),(57,4,'BW',1,0),(58,2,'BR',1,0),(59,3,'BN',1,0),(60,4,'BF',1,0),(61,3,'MM',1,0),(62,4,'BI',1,0),(63,3,'KH',1,0),(64,4,'CM',1,0),(65,4,'CV',1,0),(66,4,'CF',1,0),(67,4,'TD',1,0),(68,2,'CL',1,0),(69,2,'CO',1,0),(70,4,'KM',1,0),(71,4,'CD',1,0),(72,4,'CG',1,0),(73,2,'CR',1,0),(74,1,'HR',1,0),(75,2,'CU',1,0),(76,1,'CY',1,0),(77,4,'DJ',1,0),(78,2,'DM',1,0),(79,2,'DO',1,0),(80,3,'TL',1,0),(81,2,'EC',1,0),(82,4,'EG',1,0),(83,2,'SV',1,0),(84,4,'GQ',1,0),(85,4,'ER',1,0),(86,1,'EE',1,0),(87,4,'ET',1,0),(88,2,'FK',1,0),(89,1,'FO',1,0),(90,5,'FJ',1,0),(91,4,'GA',1,0),(92,4,'GM',1,0),(93,3,'GE',1,0),(94,4,'GH',1,0),(95,2,'GD',1,0),(96,1,'GL',1,0),(97,1,'GI',1,0),(98,2,'GP',1,0),(99,2,'GU',1,0),(100,2,'GT',1,0),(101,1,'GG',1,0),(102,4,'GN',1,0),(103,4,'GW',1,0),(104,2,'GY',1,0),(105,2,'HT',1,0),(106,5,'HM',1,0),(107,1,'VA',1,0),(108,2,'HN',1,0),(109,1,'IS',1,0),(110,3,'IN',1,0),(111,3,'ID',1,0),(112,3,'IR',1,0),(113,3,'IQ',1,0),(114,1,'IM',1,0),(115,2,'JM',1,0),(116,1,'JE',1,0),(117,3,'JO',1,0),(118,3,'KZ',1,0),(119,4,'KE',1,0),(120,1,'KI',1,0),(121,3,'KP',1,0),(122,3,'KW',1,0),(123,3,'KG',1,0),(124,3,'LA',1,0),(125,1,'LV',1,0),(126,3,'LB',1,0),(127,4,'LS',1,0),(128,4,'LR',1,0),(129,4,'LY',1,0),(130,1,'LI',1,0),(131,1,'LT',1,0),(132,3,'MO',1,0),(133,1,'MK',1,0),(134,4,'MG',1,0),(135,4,'MW',1,0),(136,3,'MY',1,0),(137,3,'MV',1,0),(138,4,'ML',1,0),(139,1,'MT',1,0),(140,5,'MH',1,0),(141,2,'MQ',1,0),(142,4,'MR',1,0),(144,4,'YT',1,0),(145,2,'MX',1,0),(146,5,'FM',1,0),(147,1,'MD',1,0),(148,1,'MC',1,0),(149,3,'MN',1,0),(150,1,'ME',1,0),(151,2,'MS',1,0),(152,4,'MA',1,0),(153,4,'MZ',1,0),(154,4,'NA',1,0),(155,5,'NR',1,0),(156,3,'NP',1,0),(157,2,'AN',1,0),(158,5,'NC',1,0),(159,2,'NI',1,0),(160,4,'NE',1,0),(161,5,'NU',1,0),(162,5,'NF',1,0),(163,5,'MP',1,0),(164,3,'OM',1,0),(165,3,'PK',1,0),(166,5,'PW',1,0),(167,3,'PS',1,0),(168,2,'PA',1,0),(169,5,'PG',1,0),(170,2,'PY',1,0),(171,2,'PE',1,0),(172,3,'PH',1,0),(173,5,'PN',1,0),(174,2,'PR',1,0),(175,3,'QA',1,0),(176,4,'RE',1,0),(177,1,'RU',1,0),(178,4,'RW',1,0),(179,2,'BL',1,0),(180,2,'KN',1,0),(181,2,'LC',1,0),(182,2,'MF',1,0),(183,2,'PM',1,0),(184,2,'VC',1,0),(185,5,'WS',1,0),(186,1,'SM',1,0),(187,4,'ST',1,0),(188,3,'SA',1,0),(189,4,'SN',1,0),(190,1,'RS',1,0),(191,4,'SC',1,0),(192,4,'SL',1,0),(193,1,'SI',1,0),(194,5,'SB',1,0),(195,4,'SO',1,0),(196,2,'GS',1,0),(197,3,'LK',1,0),(198,4,'SD',1,0),(199,2,'SR',1,0),(200,1,'SJ',1,0),(201,4,'SZ',1,0),(202,3,'SY',1,0),(203,3,'TW',1,0),(204,3,'TJ',1,0),(205,4,'TZ',1,0),(206,3,'TH',1,0),(207,5,'TK',1,0),(208,5,'TO',1,0),(209,2,'TT',1,0),(210,4,'TN',1,0),(211,1,'TR',1,0),(212,3,'TM',1,0),(213,2,'TC',1,0),(214,5,'TV',1,0),(215,4,'UG',1,0),(216,1,'UA',1,0),(217,3,'AE',1,0),(218,2,'UY',1,0),(219,3,'UZ',1,0),(220,5,'VU',1,0),(221,2,'VE',1,0),(222,3,'VN',1,0),(223,2,'VG',1,0),(224,2,'VI',1,0),(225,5,'WF',1,0),(226,4,'EH',1,0),(227,3,'YE',1,0),(228,4,'ZM',1,0),(229,4,'ZW',1,0),(230,1,'AL',1,0),(231,3,'AF',1,0),(232,5,'AQ',1,0),(233,1,'BA',1,0),(234,5,'BV',1,0),(235,5,'IO',1,0),(236,1,'BG',1,0),(237,2,'KY',1,0),(238,3,'CX',1,0),(239,3,'CC',1,0),(240,5,'CK',1,0),(241,2,'GF',1,0),(242,5,'PF',1,0),(243,5,'TF',1,0),(244,1,'AX',1,0);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_country_lang`;
CREATE TABLE `ps_country_lang` (
  `id_country` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  UNIQUE KEY `country_lang_index` (`id_country`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_country_lang` WRITE;
INSERT INTO `ps_country_lang` VALUES (1,1,'Germany'),(1,2,'Allemagne'),(2,1,'Austria'),(2,2,'Autriche'),(3,1,'Belgium'),(3,2,'Belgique'),(4,1,'Canada'),(4,2,'Canada'),(5,1,'China'),(5,2,'Chine'),(6,1,'Spain'),(6,2,'Espagne'),(7,1,'Finland'),(7,2,'Finlande'),(8,1,'France'),(8,2,'France'),(9,1,'Greece'),(9,2,'Grece'),(10,1,'Italy'),(10,2,'Italie'),(11,1,'Japan'),(11,2,'Japon'),(12,1,'Luxemburg'),(12,2,'Luxembourg'),(13,1,'Netherlands'),(13,2,'Pays-bas'),(14,1,'Poland'),(14,2,'Pologne'),(15,1,'Portugal'),(15,2,'Portugal'),(16,1,'Czech Republic'),(16,2,'Republique Tcheque'),(17,1,'United Kingdom'),(17,2,'Royaume-Uni'),(18,1,'Sweden'),(18,2,'Suede'),(19,1,'Switzerland'),(19,2,'Suisse'),(20,1,'Denmark'),(20,2,'Danemark'),(21,1,'USA'),(21,2,'USA'),(22,1,'HongKong'),(22,2,'Hong-Kong'),(23,1,'Norway'),(23,2,'Norvege'),(24,1,'Australia'),(24,2,'Australie'),(25,1,'Singapore'),(25,2,'Singapour'),(26,1,'Ireland'),(26,2,'Eire'),(27,1,'New Zealand'),(27,2,'Nouvelle-Zelande'),(28,1,'South Korea'),(28,2,'Coree du Sud'),(29,1,'Israel'),(29,2,'Israel'),(30,1,'South Africa'),(30,2,'Afrique du Sud'),(31,1,'Nigeria'),(31,2,'Nigeria'),(32,1,'Ivory Coast'),(32,2,'Cote d\'Ivoire'),(33,1,'Togo'),(33,2,'Togo'),(34,1,'Bolivia'),(34,2,'Bolivie'),(35,1,'Mauritius'),(35,2,'Ile Maurice'),(143,1,'Hungary'),(143,2,'Hongrie'),(36,1,'Romania'),(36,2,'Roumanie'),(37,1,'Slovakia'),(37,2,'Slovaquie'),(38,1,'Algeria'),(38,2,'Algerie'),(39,1,'American Samoa'),(39,2,'Samoa Americaines'),(40,1,'Andorra'),(40,2,'Andorre'),(41,1,'Angola'),(41,2,'Angola'),(42,1,'Anguilla'),(42,2,'Anguilla'),(43,1,'Antigua and Barbuda'),(43,2,'Antigua et Barbuda'),(44,1,'Argentina'),(44,2,'Argentine'),(45,1,'Armenia'),(45,2,'Armenie'),(46,1,'Aruba'),(46,2,'Aruba'),(47,1,'Azerbaijan'),(47,2,'Azerbaidjan'),(48,1,'Bahamas'),(48,2,'Bahamas'),(49,1,'Bahrain'),(49,2,'Bahrein'),(50,1,'Bangladesh'),(50,2,'Bangladesh'),(51,1,'Barbados'),(51,2,'Barbade'),(52,1,'Belarus'),(52,2,'Belarus'),(53,1,'Belize'),(53,2,'Belize'),(54,1,'Benin'),(54,2,'Benin'),(55,1,'Bermuda'),(55,2,'Bermudes'),(56,1,'Bhutan'),(56,2,'Bhoutan'),(57,1,'Botswana'),(57,2,'Botswana'),(58,1,'Brazil'),(58,2,'Bresil'),(59,1,'Brunei'),(59,2,'Brunei Darussalam'),(60,1,'Burkina Faso'),(60,2,'Burkina Faso'),(61,1,'Burma (Myanmar)'),(61,2,'Burma (Myanmar)'),(62,1,'Burundi'),(62,2,'Burundi'),(63,1,'Cambodia'),(63,2,'Cambodge'),(64,1,'Cameroon'),(64,2,'Cameroun'),(65,1,'Cape Verde'),(65,2,'Cap-Vert'),(66,1,'Central African Republic'),(66,2,'Centrafricaine, Republique'),(67,1,'Chad'),(67,2,'Tchad'),(68,1,'Chile'),(68,2,'Chili'),(69,1,'Colombia'),(69,2,'Colombie'),(70,1,'Comoros'),(70,2,'Comores'),(71,1,'Congo, Dem. Republic'),(71,2,'Congo, Rep. Dem.'),(72,1,'Congo, Republic'),(72,2,'Congo, Rep.'),(73,1,'Costa Rica'),(73,2,'Costa Rica'),(74,1,'Croatia'),(74,2,'Croatie'),(75,1,'Cuba'),(75,2,'Cuba'),(76,1,'Cyprus'),(76,2,'Chypre'),(77,1,'Djibouti'),(77,2,'Djibouti'),(78,1,'Dominica'),(78,2,'Dominica'),(79,1,'Dominican Republic'),(79,2,'Republique Dominicaine'),(80,1,'East Timor'),(80,2,'Timor oriental'),(81,1,'Ecuador'),(81,2,'Equateur'),(82,1,'Egypt'),(82,2,'Egypte'),(83,1,'El Salvador'),(83,2,'El Salvador'),(84,1,'Equatorial Guinea'),(84,2,'Guinee Equatoriale'),(85,1,'Eritrea'),(85,2,'Erythree'),(86,1,'Estonia'),(86,2,'Estonie'),(87,1,'Ethiopia'),(87,2,'Ethiopie'),(88,1,'Falkland Islands'),(88,2,'Falkland, Iles'),(89,1,'Faroe Islands'),(89,2,'Feroe, Iles'),(90,1,'Fiji'),(90,2,'Fidji'),(91,1,'Gabon'),(91,2,'Gabon'),(92,1,'Gambia'),(92,2,'Gambie'),(93,1,'Georgia'),(93,2,'Georgie'),(94,1,'Ghana'),(94,2,'Ghana'),(95,1,'Grenada'),(95,2,'Grenade'),(96,1,'Greenland'),(96,2,'Groenland'),(97,1,'Gibraltar'),(97,2,'Gibraltar'),(98,1,'Guadeloupe'),(98,2,'Guadeloupe'),(99,1,'Guam'),(99,2,'Guam'),(100,1,'Guatemala'),(100,2,'Guatemala'),(101,1,'Guernsey'),(101,2,'Guernesey'),(102,1,'Guinea'),(102,2,'Guinee'),(103,1,'Guinea-Bissau'),(103,2,'Guinee-Bissau'),(104,1,'Guyana'),(104,2,'Guyana'),(105,1,'Haiti'),(105,2,'Haiti'),(106,1,'Heard Island and McDonald Islands'),(106,2,'Heard, Ile et Mcdonald, Iles'),(107,1,'Vatican City State'),(107,2,'Saint-Siege (Etat de la Cite du Vatican)'),(108,1,'Honduras'),(108,2,'Honduras'),(109,1,'Iceland'),(109,2,'Islande'),(110,1,'India'),(110,2,'Indie'),(111,1,'Indonesia'),(111,2,'Indonesie'),(112,1,'Iran'),(112,2,'Iran'),(113,1,'Iraq'),(113,2,'Iraq'),(114,1,'Isle of Man'),(114,2,'Ile de Man'),(115,1,'Jamaica'),(115,2,'Jamaique'),(116,1,'Jersey'),(116,2,'Jersey'),(117,1,'Jordan'),(117,2,'Jordanie'),(118,1,'Kazakhstan'),(118,2,'Kazakhstan'),(119,1,'Kenya'),(119,2,'Kenya'),(120,1,'Kiribati'),(120,2,'Kiribati'),(121,1,'Korea, Dem. Republic of'),(121,2,'Coree, Rep. Populaire Dem. de'),(122,1,'Kuwait'),(122,2,'Koweit'),(123,1,'Kyrgyzstan'),(123,2,'Kirghizistan'),(124,1,'Laos'),(124,2,'Laos'),(125,1,'Latvia'),(125,2,'Lettonie'),(126,1,'Lebanon'),(126,2,'Liban'),(127,1,'Lesotho'),(127,2,'Lesotho'),(128,1,'Liberia'),(128,2,'Liberia'),(129,1,'Libya'),(129,2,'Libyenne, Jamahiriya Arabe'),(130,1,'Liechtenstein'),(130,2,'Liechtenstein'),(131,1,'Lithuania'),(131,2,'Lituanie'),(132,1,'Macau'),(132,2,'Macao'),(133,1,'Macedonia'),(133,2,'Macedoine'),(134,1,'Madagascar'),(134,2,'Madagascar'),(135,1,'Malawi'),(135,2,'Malawi'),(136,1,'Malaysia'),(136,2,'Malaisie'),(137,1,'Maldives'),(137,2,'Maldives'),(138,1,'Mali'),(138,2,'Mali'),(139,1,'Malta'),(139,2,'Malte'),(140,1,'Marshall Islands'),(140,2,'Marshall, Iles'),(141,1,'Martinique'),(141,2,'Martinique'),(142,1,'Mauritania'),(142,2,'Mauritanie'),(144,1,'Mayotte'),(144,2,'Mayotte'),(145,1,'Mexico'),(145,2,'Mexique'),(146,1,'Micronesia'),(146,2,'Micronesie'),(147,1,'Moldova'),(147,2,'Moldova'),(148,1,'Monaco'),(148,2,'Monaco'),(149,1,'Mongolia'),(149,2,'Mongolie'),(150,1,'Montenegro'),(150,2,'Montenegro'),(151,1,'Montserrat'),(151,2,'Montserrat'),(152,1,'Morocco'),(152,2,'Maroc'),(153,1,'Mozambique'),(153,2,'Mozambique'),(154,1,'Namibia'),(154,2,'Namibie'),(155,1,'Nauru'),(155,2,'Nauru'),(156,1,'Nepal'),(156,2,'Nepal'),(157,1,'Netherlands Antilles'),(157,2,'Antilles Neerlandaises'),(158,1,'New Caledonia'),(158,2,'Nouvelle-Caledonie'),(159,1,'Nicaragua'),(159,2,'Nicaragua'),(160,1,'Niger'),(160,2,'Niger'),(161,1,'Niue'),(161,2,'Niue'),(162,1,'Norfolk Island'),(162,2,'Norfolk, Ile'),(163,1,'Northern Mariana Islands'),(163,2,'Mariannes du Nord, Iles'),(164,1,'Oman'),(164,2,'Oman'),(165,1,'Pakistan'),(165,2,'Pakistan'),(166,1,'Palau'),(166,2,'Palaos'),(167,1,'Palestinian Territories'),(167,2,'Palestinien Occupe, Territoire'),(168,1,'Panama'),(168,2,'Panama'),(169,1,'Papua New Guinea'),(169,2,'Papouasie-Nouvelle-Guinee'),(170,1,'Paraguay'),(170,2,'Paraguay'),(171,1,'Peru'),(171,2,'Perou'),(172,1,'Philippines'),(172,2,'Philippines'),(173,1,'Pitcairn'),(173,2,'Pitcairn'),(174,1,'Puerto Rico'),(174,2,'Porto Rico'),(175,1,'Qatar'),(175,2,'Qatar'),(176,1,'Reunion'),(176,2,'Reunion'),(177,1,'Russian Federation'),(177,2,'Russie, Federation de'),(178,1,'Rwanda'),(178,2,'Rwanda'),(179,1,'Saint Barthelemy'),(179,2,'Saint-Barthelemy'),(180,1,'Saint Kitts and Nevis'),(180,2,'Saint-Kitts-et-Nevis'),(181,1,'Saint Lucia'),(181,2,'Sainte-Lucie'),(182,1,'Saint Martin'),(182,2,'Saint-Martin'),(183,1,'Saint Pierre and Miquelon'),(183,2,'Saint-Pierre-et-Miquelon'),(184,1,'Saint Vincent and the Grenadines'),(184,2,'Saint-Vincent-et-Les Grenadines'),(185,1,'Samoa'),(185,2,'Samoa'),(186,1,'San Marino'),(186,2,'Saint-Marin'),(187,1,'São Tome and Príncipe'),(187,2,'Sao Tome-et-Principe'),(188,1,'Saudi Arabia'),(188,2,'Arabie Saoudite'),(189,1,'Senegal'),(189,2,'Senegal'),(190,1,'Serbia'),(190,2,'Serbie'),(191,1,'Seychelles'),(191,2,'Seychelles'),(192,1,'Sierra Leone'),(192,2,'Sierra Leone'),(193,1,'Slovenia'),(193,2,'Slovenie'),(194,1,'Solomon Islands'),(194,2,'Salomon, Iles'),(195,1,'Somalia'),(195,2,'Somalie'),(196,1,'South Georgia and the South Sandwich Islands'),(196,2,'Georgie du Sud et les Iles Sandwich du Sud'),(197,1,'Sri Lanka'),(197,2,'Sri Lanka'),(198,1,'Sudan'),(198,2,'Soudan'),(199,1,'Suriname'),(199,2,'Suriname'),(200,1,'Svalbard and Jan Mayen'),(200,2,'Svalbard et Ile Jan Mayen'),(201,1,'Swaziland'),(201,2,'Swaziland'),(202,1,'Syria'),(202,2,'Syrienne'),(203,1,'Taiwan'),(203,2,'Taiwan'),(204,1,'Tajikistan'),(204,2,'Tadjikistan'),(205,1,'Tanzania'),(205,2,'Tanzanie'),(206,1,'Thailand'),(206,2,'Thailande'),(207,1,'Tokelau'),(207,2,'Tokelau'),(208,1,'Tonga'),(208,2,'Tonga'),(209,1,'Trinidad and Tobago'),(209,2,'Trinite-et-Tobago'),(210,1,'Tunisia'),(210,2,'Tunisie'),(211,1,'Turkey'),(211,2,'Turquie'),(212,1,'Turkmenistan'),(212,2,'Turkmenistan'),(213,1,'Turks and Caicos Islands'),(213,2,'Turks et Caiques, Iles'),(214,1,'Tuvalu'),(214,2,'Tuvalu'),(215,1,'Uganda'),(215,2,'Ouganda'),(216,1,'Ukraine'),(216,2,'Ukraine'),(217,1,'United Arab Emirates'),(217,2,'Emirats Arabes Unis'),(218,1,'Uruguay'),(218,2,'Uruguay'),(219,1,'Uzbekistan'),(219,2,'Ouzbekistan'),(220,1,'Vanuatu'),(220,2,'Vanuatu'),(221,1,'Venezuela'),(221,2,'Venezuela'),(222,1,'Vietnam'),(222,2,'Vietnam'),(223,1,'Virgin Islands (British)'),(223,2,'Iles Vierges Britanniques'),(224,1,'Virgin Islands (U.S.)'),(224,2,'Iles Vierges des Etats-Unis'),(225,1,'Wallis and Futuna'),(225,2,'Wallis et Futuna'),(226,1,'Western Sahara'),(226,2,'Sahara Occidental'),(227,1,'Yemen'),(227,2,'Yemen'),(228,1,'Zambia'),(228,2,'Zambie'),(229,1,'Zimbabwe'),(229,2,'Zimbabwe'),(230,1,'Albania'),(230,2,'Albanie'),(231,1,'Afghanistan'),(231,2,'Afghanistan'),(232,1,'Antarctica'),(232,2,'Antarctique'),(233,1,'Bosnia and Herzegovina'),(233,2,'Bosnie-Herzegovine'),(234,1,'Bouvet Island'),(234,2,'Bouvet, Ile'),(235,1,'British Indian Ocean Territory'),(235,2,'Ocean Indien, Territoire Britannique de L\''),(236,1,'Bulgaria'),(236,2,'Bulgarie'),(237,1,'Cayman Islands'),(237,2,'Caimans, Iles'),(238,1,'Christmas Island'),(238,2,'Christmas, Ile'),(239,1,'Cocos (Keeling) Islands'),(239,2,'Cocos (Keeling), Iles'),(240,1,'Cook Islands'),(240,2,'Cook, Iles'),(241,1,'French Guiana'),(241,2,'Guyane Francaise'),(242,1,'French Polynesia'),(242,2,'Polynesie Francaise'),(243,1,'French Southern Territories'),(243,2,'Terres Australes Francaises'),(244,1,'Åland Islands'),(244,2,'Åland, Iles');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_currency`;
CREATE TABLE `ps_currency` (
  `id_currency` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(32) NOT NULL,
  `iso_code` varchar(3) NOT NULL default '0',
  `sign` varchar(8) NOT NULL,
  `blank` tinyint(1) unsigned NOT NULL default '0',
  `format` tinyint(1) unsigned NOT NULL default '0',
  `decimals` tinyint(1) unsigned NOT NULL default '1',
  `conversion_rate` decimal(13,6) NOT NULL,
  `deleted` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_currency`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_currency` WRITE;
INSERT INTO `ps_currency` VALUES (1,'Euro','EUR','€',1,2,1,'1.000000',0),(2,'Dollar','USD','$',0,1,1,'1.470000',0),(3,'Pound','GBP','£',0,1,1,'0.800000',0);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_customer`;
CREATE TABLE `ps_customer` (
  `id_customer` int(10) unsigned NOT NULL auto_increment,
  `id_gender` int(10) unsigned NOT NULL,
  `secure_key` varchar(32) NOT NULL default '-1',
  `email` varchar(128) NOT NULL,
  `passwd` varchar(32) NOT NULL,
  `last_passwd_gen` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `birthday` date default NULL,
  `lastname` varchar(32) NOT NULL,
  `newsletter` tinyint(1) unsigned NOT NULL default '0',
  `ip_registration_newsletter` varchar(15) default NULL,
  `newsletter_date_add` datetime default NULL,
  `optin` tinyint(1) unsigned NOT NULL default '0',
  `firstname` varchar(32) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  `deleted` tinyint(1) NOT NULL default '0',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_customer`),
  UNIQUE KEY `customer_email` (`email`),
  KEY `customer_login` (`email`,`passwd`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_customer` WRITE;
INSERT INTO `ps_customer` VALUES (1,1,'47ce86627c1f3c792a80773c5d2deaf8','john@doe.com','4717e0bdb6970abede946f45ae0c1c6d','2009-09-17 07:48:51','1970-01-15','DOE',1,NULL,'2009-09-17 09:54:53',1,'John',1,0,'2009-09-17 09:48:51','2009-09-17 09:54:53'),(2,9,'02d849254b0dd5a0ed20082ec54d9c4a','prestashop@prestashop.com','154c31ed01c2317e6fee607bb99b68a7','2009-09-17 01:55:26',NULL,'SITE',0,NULL,NULL,0,'Prestashop',1,0,'2009-09-17 09:55:26','2009-09-17 09:55:26'),(3,2,'898d9b1eca5f2115b4f256fd5a5bf272','jane@doe.com','9c29952d9a02ece31771cad1c97b3b2a','2009-09-17 01:56:30','1975-01-01','DOE',0,NULL,NULL,0,'Jane',1,0,'2009-09-17 09:56:30','2009-09-17 09:56:42');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_customer_group`;
CREATE TABLE `ps_customer_group` (
  `id_customer` int(10) unsigned NOT NULL,
  `id_group` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_customer`,`id_group`),
  KEY `customer_login` (`id_group`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_customer_group` WRITE;
INSERT INTO `ps_customer_group` VALUES (1,1),(2,1),(3,1);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_group`;
CREATE TABLE `ps_group` (
  `id_group` int(10) unsigned NOT NULL auto_increment,
  `reduction` decimal(10,2) NOT NULL default '0.00',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_group`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_group` WRITE;
INSERT INTO `ps_group` VALUES (1,'0.00','2009-09-17 09:48:51','2009-09-17 09:48:51');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_group_lang`;
CREATE TABLE `ps_group_lang` (
  `id_group` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  UNIQUE KEY `attribute_lang_index` (`id_group`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_group_lang` WRITE;
INSERT INTO `ps_group_lang` VALUES (1,1,'Default'),(1,2,'Defaut');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_image`;
CREATE TABLE `ps_image` (
  `id_image` int(10) unsigned NOT NULL auto_increment,
  `id_product` int(10) unsigned NOT NULL,
  `position` tinyint(2) unsigned NOT NULL default '0',
  `cover` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_image`),
  KEY `image_product` (`id_product`)
) ENGINE=MyISAM AUTO_INCREMENT=52 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_image` WRITE;
INSERT INTO `ps_image` VALUES (40,1,4,0),(39,1,3,0),(38,1,2,0),(37,1,1,1),(48,2,3,0),(47,2,2,0),(49,2,4,0),(46,2,1,1),(15,5,1,1),(16,5,2,0),(17,5,3,0),(18,6,4,0),(19,6,5,0),(20,6,1,1),(24,7,1,1),(33,8,1,1),(27,7,3,0),(26,7,2,0),(29,7,4,0),(30,7,5,0),(32,7,6,0),(36,9,1,1),(41,1,5,0),(42,1,6,0),(44,1,7,0),(45,1,8,0),(50,10,1,1),(51,11,1,1);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_image_lang`;
CREATE TABLE `ps_image_lang` (
  `id_image` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `legend` varchar(128) default NULL,
  UNIQUE KEY `image_lang_index` (`id_image`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_image_lang` WRITE;
INSERT INTO `ps_image_lang` VALUES (40,2,'iPod Nano'),(40,1,'iPod Nano'),(39,2,'iPod Nano'),(39,1,'iPod Nano'),(38,2,'iPod Nano'),(38,1,'iPod Nano'),(37,2,'iPod Nano'),(37,1,'iPod Nano'),(48,2,'iPod shuffle'),(48,1,'iPod shuffle'),(47,2,'iPod shuffle'),(47,1,'iPod shuffle'),(49,2,'iPod shuffle'),(49,1,'iPod shuffle'),(46,2,'iPod shuffle'),(46,1,'iPod shuffle'),(10,1,'luxury-cover-for-ipod-video'),(10,2,'housse-luxe-pour-ipod-video'),(11,1,'cover'),(11,2,'housse'),(12,1,'myglove-ipod-nano'),(12,2,'myglove-ipod-nano'),(13,1,'myglove-ipod-nano'),(13,2,'myglove-ipod-nano'),(14,1,'myglove-ipod-nano'),(14,2,'myglove-ipod-nano'),(15,1,'MacBook Air'),(15,2,'macbook-air-1'),(16,1,'MacBook Air'),(16,2,'macbook-air-2'),(17,1,'MacBook Air'),(17,2,'macbook-air-3'),(18,1,'MacBook Air'),(18,2,'macbook-air-4'),(19,1,'MacBook Air'),(19,2,'macbook-air-5'),(20,1,' MacBook Air SuperDrive'),(20,2,'superdrive-pour-macbook-air-1'),(24,2,'iPod touch'),(24,1,'iPod touch'),(33,1,'housse-portefeuille-en-cuir'),(26,1,'iPod touch'),(26,2,'iPod touch'),(27,1,'iPod touch'),(27,2,'iPod touch'),(29,1,'iPod touch'),(29,2,'iPod touch'),(30,1,'iPod touch'),(30,2,'iPod touch'),(32,1,'iPod touch'),(32,2,'iPod touch'),(33,2,'housse-portefeuille-en-cuir-ipod-nano'),(36,2,'Ecouteurs a isolation sonore Shure SE210'),(36,1,'Shure SE210 Sound-Isolating Earphones for iPod and iPhone'),(41,1,'iPod Nano'),(41,2,'iPod Nano'),(42,1,'iPod Nano'),(42,2,'iPod Nano'),(44,1,'iPod Nano'),(44,2,'iPod Nano'),(45,1,'iPod Nano'),(45,2,'iPod Nano'),(50,1,'Maillot de Bain'),(50,2,'Maillot de Bain'),(51,1,'Short'),(51,2,'Short');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_image_type`;
CREATE TABLE `ps_image_type` (
  `id_image_type` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(16) NOT NULL,
  `width` int(10) unsigned NOT NULL,
  `height` int(10) unsigned NOT NULL,
  `products` tinyint(1) NOT NULL default '1',
  `categories` tinyint(1) NOT NULL default '1',
  `manufacturers` tinyint(1) NOT NULL default '1',
  `suppliers` tinyint(1) NOT NULL default '1',
  `scenes` tinyint(1) NOT NULL default '1',
  PRIMARY KEY  (`id_image_type`),
  KEY `image_type_name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_image_type` WRITE;
INSERT INTO `ps_image_type` VALUES (1,'small',45,45,1,1,1,1,0),(2,'medium',80,80,1,1,1,1,0),(3,'large',300,300,1,1,1,1,0),(4,'thickbox',600,600,1,0,0,0,0),(5,'category',500,150,0,1,0,0,0),(6,'home',129,129,1,0,0,0,0),(7,'large_scene',556,200,0,0,0,0,1),(8,'thumb_scene',161,58,0,0,0,0,1);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_lang`;
CREATE TABLE `ps_lang` (
  `id_lang` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(32) NOT NULL,
  `active` tinyint(3) unsigned NOT NULL default '0',
  `iso_code` char(2) NOT NULL,
  PRIMARY KEY  (`id_lang`),
  KEY `lang_iso_code` (`iso_code`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_lang` WRITE;
INSERT INTO `ps_lang` VALUES (1,'English (English)',1,'en'),(2,'Francais (French)',1,'fr');


DROP TABLE IF EXISTS `ps_manufacturer`;
CREATE TABLE `ps_manufacturer` (
  `id_manufacturer` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_manufacturer`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_manufacturer` WRITE;
INSERT INTO `ps_manufacturer` VALUES (1,'Apple Computer, Inc','2009-09-17 09:48:51','2009-09-17 09:48:51'),(2,'Shure Incorporated','2009-09-17 09:48:51','2009-09-17 09:48:51');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_manufacturer_lang`;
CREATE TABLE `ps_manufacturer_lang` (
  `id_manufacturer` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `description` text,
  `short_description` varchar(254) default NULL,
  `meta_title` varchar(254) default NULL,
  `meta_keywords` varchar(254) default NULL,
  `meta_description` varchar(254) default NULL,
  PRIMARY KEY  (`id_manufacturer`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_module`;
CREATE TABLE `ps_module` (
  `id_module` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_module`),
  KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=52 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_module` WRITE;
INSERT INTO `ps_module` VALUES (1,'homefeatured',1),(2,'gsitemap',1),(3,'cheque',1),(4,'paypal',1),(5,'editorial',1),(6,'bankwire',1),(7,'blockadvertising',1),(8,'blockbestsellers',1),(9,'blockcart',1),(10,'blockcategories',1),(11,'blockcurrencies',1),(12,'blockinfos',1),(13,'blocklanguages',1),(14,'blockmanufacturer',1),(15,'blockmyaccount',1),(16,'blocknewproducts',1),(17,'blockpaymentlogo',1),(18,'blockpermanentlinks',1),(19,'blocksearch',1),(20,'blockspecials',1),(21,'blocktags',1),(22,'blockuserinfo',1),(23,'blockvariouslinks',1),(24,'blockviewed',1),(25,'statsdata',1),(26,'statsvisits',1),(27,'statssales',1),(28,'statsregistrations',1),(30,'statspersonalinfos',1),(31,'statslive',1),(32,'statsequipment',1),(33,'statscatalog',1),(34,'graphvisifire',1),(35,'graphxmlswfcharts',1),(36,'graphgooglechart',1),(37,'graphartichow',1),(38,'statshome',1),(39,'gridextjs',1),(40,'statsbestcustomers',1),(41,'statsorigin',1),(42,'pagesnotfound',1),(43,'sekeywords',1),(44,'statsproduct',1),(45,'statsbestproducts',1),(46,'statsbestcategories',1),(47,'statsbestvouchers',1),(48,'statsbestsuppliers',1),(49,'statscarrier',1),(50,'statsnewsletter',1),(51,'statssearch',1);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_module_country`;
CREATE TABLE `ps_module_country` (
  `id_module` int(10) unsigned NOT NULL,
  `id_country` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_module`,`id_country`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_module_country` WRITE;
INSERT INTO `ps_module_country` VALUES (3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7),(3,8),(3,9),(3,10),(3,11),(3,12),(3,13),(3,14),(3,15),(3,16),(3,17),(3,18),(3,19),(3,20),(3,21),(3,22),(3,23),(3,24),(3,25),(3,26),(3,27),(3,28),(3,29),(3,30),(3,31),(3,32),(3,33),(3,34),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),(4,10),(4,11),(4,12),(4,13),(4,14),(4,15),(4,16),(4,17),(4,18),(4,19),(4,20),(4,21),(4,22),(4,23),(4,24),(4,25),(4,26),(4,27),(4,28),(4,29),(4,30),(4,31),(4,32),(4,33),(4,34),(6,1),(6,2),(6,3),(6,4),(6,5),(6,6),(6,7),(6,8),(6,9),(6,10),(6,11),(6,12),(6,13),(6,14),(6,15),(6,16),(6,17),(6,18),(6,19),(6,20),(6,21),(6,22),(6,23),(6,24),(6,25),(6,26),(6,27),(6,28),(6,29),(6,30),(6,31),(6,32),(6,33),(6,34);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_module_currency`;
CREATE TABLE `ps_module_currency` (
  `id_module` int(10) unsigned NOT NULL,
  `id_currency` int(11) NOT NULL,
  PRIMARY KEY  (`id_module`,`id_currency`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_module_currency` WRITE;
INSERT INTO `ps_module_currency` VALUES (3,1),(3,2),(3,3),(4,-2),(6,1),(6,2),(6,3);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_module_group`;
CREATE TABLE `ps_module_group` (
  `id_module` int(10) unsigned NOT NULL,
  `id_group` int(11) NOT NULL,
  PRIMARY KEY  (`id_module`,`id_group`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_module_group` WRITE;
INSERT INTO `ps_module_group` VALUES (3,1),(4,1),(6,1);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_order_detail`;
CREATE TABLE `ps_order_detail` (
  `id_order_detail` int(10) unsigned NOT NULL auto_increment,
  `id_order` int(10) unsigned NOT NULL,
  `product_id` int(10) unsigned NOT NULL,
  `product_attribute_id` int(10) unsigned default NULL,
  `product_name` varchar(255) NOT NULL,
  `product_quantity` int(10) unsigned NOT NULL default '0',
  `product_quantity_in_stock` int(10) unsigned NOT NULL default '0',
  `product_quantity_refunded` int(10) unsigned NOT NULL default '0',
  `product_quantity_return` int(10) unsigned NOT NULL default '0',
  `product_quantity_reinjected` int(10) unsigned NOT NULL default '0',
  `product_price` decimal(13,6) NOT NULL default '0.000000',
  `product_quantity_discount` decimal(13,6) NOT NULL default '0.000000',
  `product_ean13` varchar(13) default NULL,
  `product_reference` varchar(32) default NULL,
  `product_supplier_reference` varchar(32) default NULL,
  `product_weight` float NOT NULL,
  `tax_name` varchar(16) NOT NULL,
  `tax_rate` decimal(10,2) NOT NULL default '0.00',
  `ecotax` decimal(10,2) NOT NULL default '0.00',
  `download_hash` varchar(255) default NULL,
  `download_nb` int(10) unsigned default '0',
  `download_deadline` datetime default '0000-00-00 00:00:00',
  PRIMARY KEY  (`id_order_detail`),
  KEY `order_detail_order` (`id_order`),
  KEY `product_id` (`product_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_order_detail` WRITE;
INSERT INTO `ps_order_detail` VALUES (1,1,7,23,'iPod touch - Capacite: 32Go',1,0,0,0,0,'392.140500','0.000000',NULL,NULL,NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(2,1,9,0,'Ecouteurs a isolation sonore Shure SE210',1,0,0,0,0,'124.581900','0.000000',NULL,NULL,NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(3,2,11,0,'Short',5,5,0,0,0,'12.123746','0.000000','9876543210982','9876short5432',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(4,3,10,49,'Maillot de Bain - Couleur : Rouge, Size : L',1,1,0,0,0,'16.722408','0.000000','1234567890128','123mdb321',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(5,4,10,43,'Maillot de Bain - Couleur : Bleu, Size : L',1,1,0,0,0,'16.722408','0.000000','1234567890128','123mdb321',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(6,4,10,44,'Maillot de Bain - Couleur : Bleu, Size : M',2,2,0,0,0,'16.722408','0.000000','1234567890128','123mdb321',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(7,4,10,47,'Maillot de Bain - Couleur : Noir, Size : M',3,3,0,0,0,'16.722408','0.000000','1234567890128','123mdb321',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(8,4,10,48,'Maillot de Bain - Couleur : Noir, Size : S',4,4,0,0,0,'16.722408','0.000000','1234567890128','123mdb321',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(9,4,10,49,'Maillot de Bain - Couleur : Rouge, Size : L',5,5,0,0,0,'16.722408','0.000000','1234567890128','123mdb321',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(10,4,10,50,'Maillot de Bain - Couleur : Rouge, Size : M',6,6,0,0,0,'16.722408','0.000000','1234567890128','123mdb321',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(11,4,10,51,'Maillot de Bain - Couleur : Rouge, Size : S',7,7,0,0,0,'16.722408','0.000000','1234567890128','123mdb321',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00'),(12,4,11,0,'Short',8,8,0,0,0,'12.123746','0.000000','9876543210982','9876short5432',NULL,0,'TVA 19.6%','19.60','0.00','',0,'0000-00-00 00:00:00');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_order_discount`;
CREATE TABLE `ps_order_discount` (
  `id_order_discount` int(10) unsigned NOT NULL auto_increment,
  `id_order` int(10) unsigned NOT NULL,
  `id_discount` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  `value` decimal(10,2) NOT NULL default '0.00',
  PRIMARY KEY  (`id_order_discount`),
  KEY `order_discount_order` (`id_order`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_order_history`;
CREATE TABLE `ps_order_history` (
  `id_order_history` int(10) unsigned NOT NULL auto_increment,
  `id_employee` int(10) unsigned NOT NULL,
  `id_order` int(10) unsigned NOT NULL,
  `id_order_state` int(10) unsigned NOT NULL,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_order_history`),
  KEY `order_history_order` (`id_order`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_order_history` WRITE;
INSERT INTO `ps_order_history` VALUES (1,0,1,1,'2009-09-17 09:48:51'),(2,0,2,1,'2009-09-17 10:34:39'),(3,0,3,1,'2009-09-17 10:35:44'),(4,0,4,1,'2009-09-17 10:36:58'),(5,1,2,2,'2009-09-17 10:37:48'),(6,1,2,4,'2009-09-17 10:37:53'),(7,1,3,2,'2009-09-17 10:38:04'),(8,1,3,4,'2009-09-17 10:38:09'),(9,1,4,2,'2009-09-17 10:39:26'),(10,1,4,4,'2009-09-17 10:39:30');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_order_message`;
CREATE TABLE `ps_order_message` (
  `id_order_message` int(10) unsigned NOT NULL auto_increment,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_order_message`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_order_message` WRITE;
INSERT INTO `ps_order_message` VALUES (1,'2009-09-17 09:48:51');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_order_message_lang`;
CREATE TABLE `ps_order_message_lang` (
  `id_order_message` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  `message` text NOT NULL,
  PRIMARY KEY  (`id_order_message`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_order_message_lang` WRITE;
INSERT INTO `ps_order_message_lang` VALUES (1,1,'Delay','Hi,\n\nUnfortunately, an item on your order is currently out of stock. This may cause a slight delay in delivery.\nPlease accept our apologies and rest assured that we are working hard to rectify this.\n\nBest regards,\n'),(1,2,'Delai','Bonjour,\n\nUn des elements de votre commande est actuellement en reapprovisionnement, ce qui peut legerement retarder son envoi.\n\nMerci de votre comprehension.\n\nCordialement, \n');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_order_return`;
CREATE TABLE `ps_order_return` (
  `id_order_return` int(10) unsigned NOT NULL auto_increment,
  `id_customer` int(10) unsigned NOT NULL,
  `id_order` int(10) unsigned NOT NULL,
  `state` tinyint(1) unsigned NOT NULL default '1',
  `question` text NOT NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_order_return`),
  KEY `order_return_customer` (`id_customer`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_order_return_detail`;
CREATE TABLE `ps_order_return_detail` (
  `id_order_return` int(10) unsigned NOT NULL,
  `id_order_detail` int(10) unsigned NOT NULL,
  `id_customization` int(10) NOT NULL default '0',
  `product_quantity` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_order_return`,`id_order_detail`,`id_customization`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_order_return_state`;
CREATE TABLE `ps_order_return_state` (
  `id_order_return_state` int(10) unsigned NOT NULL auto_increment,
  `color` varchar(32) default NULL,
  PRIMARY KEY  (`id_order_return_state`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_order_return_state` WRITE;
INSERT INTO `ps_order_return_state` VALUES (1,'#ADD8E6'),(2,'#EEDDFF'),(3,'#DDFFAA'),(4,'#FFD3D3'),(5,'#FFFFBB');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_order_return_state_lang`;
CREATE TABLE `ps_order_return_state_lang` (
  `id_order_return_state` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  UNIQUE KEY `order_state_lang_index` (`id_order_return_state`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_order_return_state_lang` WRITE;
INSERT INTO `ps_order_return_state_lang` VALUES (1,1,'Waiting for confirmation'),(2,1,'Waiting for package'),(3,1,'Package received'),(4,1,'Return denied'),(5,1,'Return completed'),(1,2,'En attente de confirmation'),(2,2,'En attente du colis'),(3,2,'Colis recu'),(4,2,'Retour refuse'),(5,2,'Retour termine');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_order_slip`;
CREATE TABLE `ps_order_slip` (
  `id_order_slip` int(10) unsigned NOT NULL auto_increment,
  `id_customer` int(10) unsigned NOT NULL,
  `id_order` int(10) unsigned NOT NULL,
  `shipping_cost` tinyint(3) unsigned NOT NULL default '0',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_order_slip`),
  KEY `order_slip_customer` (`id_customer`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_order_slip_detail`;
CREATE TABLE `ps_order_slip_detail` (
  `id_order_slip` int(10) unsigned NOT NULL,
  `id_order_detail` int(10) unsigned NOT NULL,
  `product_quantity` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_order_slip`,`id_order_detail`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_order_state`;
CREATE TABLE `ps_order_state` (
  `id_order_state` int(10) unsigned NOT NULL auto_increment,
  `invoice` tinyint(1) unsigned default '0',
  `send_email` tinyint(1) unsigned NOT NULL default '0',
  `color` varchar(32) default NULL,
  `unremovable` tinyint(1) unsigned NOT NULL,
  `hidden` tinyint(1) unsigned NOT NULL default '0',
  `logable` tinyint(1) NOT NULL default '0',
  `delivery` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_order_state`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_order_state` WRITE;
INSERT INTO `ps_order_state` VALUES (1,0,1,'lightblue',1,0,0,0),(2,1,1,'#DDEEFF',1,0,1,0),(3,1,1,'#FFDD99',1,0,1,1),(4,1,1,'#EEDDFF',1,0,1,1),(5,1,0,'#DDFFAA',1,0,1,1),(6,1,1,'#DADADA',1,0,0,0),(7,1,1,'#FFFFBB',1,0,0,0),(8,0,1,'#FFDFDF',1,0,0,0),(9,1,1,'#FFD3D3',1,0,0,0),(10,0,1,'lightblue',1,0,0,0),(11,0,0,'lightblue',1,0,0,0);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_order_state_lang`;
CREATE TABLE `ps_order_state_lang` (
  `id_order_state` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  `template` varchar(64) NOT NULL,
  UNIQUE KEY `order_state_lang_index` (`id_order_state`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_order_state_lang` WRITE;
INSERT INTO `ps_order_state_lang` VALUES (1,1,'Awaiting cheque payment','cheque'),(2,1,'Payment accepted','payment'),(3,1,'Preparation in progress','preparation'),(4,1,'Shipped','shipped'),(5,1,'Delivered',''),(6,1,'Canceled','order_canceled'),(7,1,'Refund','refund'),(8,1,'Payment error','payment_error'),(9,1,'Out of stock','outofstock'),(10,1,'Awaiting bank wire payment','bankwire'),(11,1,'Awaiting PayPal payment',''),(1,2,'En attente du paiement par cheque','cheque'),(2,2,'Paiement accepte','payment'),(3,2,'Preparation en cours','preparation'),(4,2,'En cours de livraison','shipped'),(5,2,'Livre',''),(6,2,'Annule','order_canceled'),(7,2,'Rembourse','refund'),(8,2,'Erreur de paiement','payment_error'),(9,2,'Produit(s) indisponibles','outofstock'),(10,2,'En attente du paiement par virement bancaire','bankwire'),(11,2,'En attente du paiement par PayPal','');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_orders`;
CREATE TABLE `ps_orders` (
  `id_order` int(10) unsigned NOT NULL auto_increment,
  `id_carrier` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `id_customer` int(10) unsigned NOT NULL,
  `id_cart` int(10) unsigned NOT NULL,
  `id_currency` int(10) unsigned NOT NULL,
  `id_address_delivery` int(10) unsigned NOT NULL,
  `id_address_invoice` int(10) unsigned NOT NULL,
  `secure_key` varchar(32) NOT NULL default '-1',
  `payment` varchar(255) NOT NULL,
  `module` varchar(255) default NULL,
  `recyclable` tinyint(1) unsigned NOT NULL default '0',
  `gift` tinyint(1) unsigned NOT NULL default '0',
  `gift_message` text,
  `shipping_number` varchar(32) default NULL,
  `total_discounts` decimal(10,2) NOT NULL default '0.00',
  `total_paid` decimal(10,2) NOT NULL default '0.00',
  `total_paid_real` decimal(10,2) NOT NULL default '0.00',
  `total_products` decimal(10,2) NOT NULL default '0.00',
  `total_shipping` decimal(10,2) NOT NULL default '0.00',
  `total_wrapping` decimal(10,2) NOT NULL default '0.00',
  `invoice_number` int(10) unsigned NOT NULL default '0',
  `delivery_number` int(10) unsigned NOT NULL default '0',
  `invoice_date` datetime NOT NULL,
  `delivery_date` datetime NOT NULL,
  `valid` int(1) unsigned NOT NULL default '0',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_order`),
  KEY `id_customer` (`id_customer`),
  KEY `id_cart` (`id_cart`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_orders` WRITE;
INSERT INTO `ps_orders` VALUES (1,2,2,1,1,1,2,2,'47ce86627c1f3c792a80773c5d2deaf8','Cheque','cheque',1,0,'','','0.00','625.98','625.98','516.72','7.98','0.00',1,0,'2008-09-10 15:30:44','0000-00-00 00:00:00',0,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(2,2,2,1,2,1,2,2,'47ce86627c1f3c792a80773c5d2deaf8','Cheque','cheque',1,0,'','','0.00','80.48','80.48','60.62','7.98','0.00',2,1,'2009-09-17 10:37:48','2009-09-17 10:37:53',1,'2009-09-17 10:34:39','2009-09-17 10:37:53'),(3,2,2,1,3,1,2,2,'47ce86627c1f3c792a80773c5d2deaf8','Cheque','cheque',1,0,'','','0.00','27.98','27.98','16.72','7.98','0.00',3,2,'2009-09-17 10:38:04','2009-09-17 10:38:09',1,'2009-09-17 10:35:44','2009-09-17 10:38:09'),(4,2,2,1,4,1,2,2,'47ce86627c1f3c792a80773c5d2deaf8','Cheque','cheque',1,0,'','','0.00','676.00','676.00','565.22','0.00','0.00',4,3,'2009-09-17 10:39:26','2009-09-17 10:39:30',1,'2009-09-17 10:36:58','2009-09-17 10:39:30');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_pack`;
CREATE TABLE `ps_pack` (
  `id_product_pack` int(10) unsigned NOT NULL,
  `id_product_item` int(10) unsigned NOT NULL,
  `quantity` int(10) unsigned NOT NULL default '1',
  PRIMARY KEY  (`id_product_pack`,`id_product_item`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_product`;
CREATE TABLE `ps_product` (
  `id_product` int(10) unsigned NOT NULL auto_increment,
  `id_supplier` int(10) unsigned default NULL,
  `id_manufacturer` int(10) unsigned default NULL,
  `id_tax` int(10) unsigned NOT NULL,
  `id_category_default` int(10) unsigned default NULL,
  `id_color_default` int(10) unsigned default NULL,
  `on_sale` tinyint(1) unsigned NOT NULL default '0',
  `ean13` varchar(13) default NULL,
  `ecotax` decimal(10,2) NOT NULL default '0.00',
  `quantity` int(10) unsigned NOT NULL default '0',
  `price` decimal(13,6) NOT NULL default '0.000000',
  `wholesale_price` decimal(13,6) NOT NULL default '0.000000',
  `reduction_price` decimal(10,2) default NULL,
  `reduction_percent` float default NULL,
  `reduction_from` date default NULL,
  `reduction_to` date default NULL,
  `reference` varchar(32) default NULL,
  `supplier_reference` varchar(32) default NULL,
  `location` varchar(64) default NULL,
  `weight` float NOT NULL default '0',
  `out_of_stock` int(10) unsigned NOT NULL default '2',
  `quantity_discount` tinyint(1) default '0',
  `customizable` tinyint(2) NOT NULL default '0',
  `uploadable_files` tinyint(4) NOT NULL default '0',
  `text_fields` tinyint(4) NOT NULL default '0',
  `active` tinyint(1) unsigned NOT NULL default '0',
  `indexed` tinyint(1) NOT NULL default '0',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_product`),
  KEY `product_supplier` (`id_supplier`),
  KEY `product_manufacturer` (`id_manufacturer`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_product` WRITE;
INSERT INTO `ps_product` VALUES (1,1,1,1,2,2,0,'0','0.00',800,'124.581940','70.000000','0.00',5,'2009-09-17','2009-09-17','','',NULL,0.5,2,0,0,0,0,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(2,1,1,1,2,0,0,'0','0.00',100,'66.053500','33.000000','0.00',0,'2009-09-17','2009-09-17','','',NULL,0,2,0,0,0,0,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(5,1,1,1,4,0,0,'0','0.00',274,'1504.180602','1000.000000','0.00',0,'2009-09-17','2009-09-17','',NULL,NULL,1.36,2,0,0,0,0,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(6,1,1,1,4,0,0,'0','0.00',250,'1170.568561','0.000000','0.00',0,'2009-09-17','2009-09-17','',NULL,NULL,0.75,2,0,0,0,0,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(7,0,0,1,2,0,0,'','0.00',180,'241.638796','200.000000','0.00',0,'2009-09-17','2009-09-17','',NULL,NULL,0,2,0,0,0,0,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(8,0,0,1,3,0,0,'','0.00',1,'25.041806','0.000000','0.00',0,'2009-09-17','2009-09-17','',NULL,NULL,0,2,0,0,0,0,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(9,2,2,1,3,0,0,'','0.00',1,'124.581940','0.000000','0.00',0,'2009-09-17','2009-09-17','',NULL,NULL,0,2,0,0,0,0,1,1,'2009-09-17 09:48:51','2009-09-17 09:48:51'),(10,0,0,1,1,0,0,'1234567890128','0.00',60,'16.722408','10.000000','0.00',0,'2009-09-17','2009-09-17','123mdb321','','',0,2,0,0,0,0,1,1,'2009-09-17 10:04:08','2009-09-17 10:10:33'),(11,0,0,1,1,0,0,'9876543210982','0.00',87,'12.123746','5.000000','0.00',0,'2009-09-17','2009-09-17','9876short5432','','',0,2,0,0,0,0,1,1,'2009-09-17 10:27:15','2009-09-17 10:32:29');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_product_attachment`;
CREATE TABLE `ps_product_attachment` (
  `id_product` int(10) NOT NULL,
  `id_attachment` int(10) NOT NULL,
  PRIMARY KEY  (`id_product`,`id_attachment`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_product_attribute`;
CREATE TABLE `ps_product_attribute` (
  `id_product_attribute` int(10) unsigned NOT NULL auto_increment,
  `id_product` int(10) unsigned NOT NULL,
  `reference` varchar(32) default NULL,
  `supplier_reference` varchar(32) default NULL,
  `location` varchar(64) default NULL,
  `ean13` varchar(13) default NULL,
  `wholesale_price` decimal(13,6) NOT NULL default '0.000000',
  `price` decimal(10,2) NOT NULL default '0.00',
  `ecotax` decimal(10,2) NOT NULL default '0.00',
  `quantity` int(10) unsigned NOT NULL default '0',
  `weight` float NOT NULL default '0',
  `default_on` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_product_attribute`),
  KEY `product_attribute_product` (`id_product`),
  KEY `reference` (`reference`),
  KEY `supplier_reference` (`supplier_reference`)
) ENGINE=MyISAM AUTO_INCREMENT=52 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_product_attribute` WRITE;
INSERT INTO `ps_product_attribute` VALUES (30,1,'','',NULL,'','0.000000','0.00','0.00',50,0,0),(29,1,'','',NULL,'','0.000000','50.00','0.00',50,0,0),(28,1,'','',NULL,'','0.000000','0.00','0.00',50,0,0),(27,1,'','',NULL,'','0.000000','50.00','0.00',50,0,0),(26,1,'','',NULL,'','0.000000','0.00','0.00',50,0,0),(25,1,'','',NULL,'','0.000000','50.00','0.00',50,0,0),(7,2,'','',NULL,'','0.000000','0.00','0.00',10,0,0),(8,2,'','',NULL,'','0.000000','0.00','0.00',20,0,1),(9,2,'','',NULL,'','0.000000','0.00','0.00',30,0,0),(10,2,'','',NULL,'','0.000000','0.00','0.00',40,0,0),(12,5,'',NULL,NULL,'','0.000000','899.00','0.00',100,0,0),(13,5,'',NULL,NULL,'','0.000000','0.00','0.00',99,0,1),(14,5,'',NULL,NULL,'','0.000000','270.00','0.00',50,0,0),(15,5,'',NULL,NULL,'','0.000000','1169.00','0.00',25,0,0),(23,7,'',NULL,NULL,'','0.000000','180.00','0.00',70,0,0),(22,7,'',NULL,NULL,'','0.000000','90.00','0.00',60,0,0),(19,7,'',NULL,NULL,'','0.000000','0.00','0.00',50,0,1),(31,1,'','',NULL,'','0.000000','50.00','0.00',50,0,1),(32,1,'','',NULL,'','0.000000','0.00','0.00',50,0,0),(33,1,'','',NULL,'','0.000000','50.00','0.00',50,0,0),(34,1,'','',NULL,'','0.000000','0.00','0.00',50,0,0),(35,1,'','',NULL,'','0.000000','50.00','0.00',50,0,0),(36,1,'','',NULL,'','0.000000','0.00','0.00',50,0,0),(39,1,'','',NULL,'','0.000000','50.00','0.00',50,0,0),(40,1,'','',NULL,'','0.000000','0.00','0.00',50,0,0),(41,1,'','',NULL,'','0.000000','50.00','0.00',50,0,0),(42,1,'','',NULL,'','0.000000','0.00','0.00',50,0,0),(43,10,'','','','','0.000000','0.00','0.00',9,0,1),(44,10,'','','','','0.000000','0.00','0.00',18,0,0),(45,10,'','','','','0.000000','0.00','0.00',30,0,0),(46,10,'','','','','0.000000','0.00','0.00',40,0,0),(47,10,'','','','','0.000000','0.00','0.00',47,0,0),(48,10,'','','','','0.000000','0.00','0.00',56,0,0),(49,10,'','','','','0.000000','0.00','0.00',64,0,0),(50,10,'','','','','0.000000','0.00','0.00',74,0,0),(51,10,'','','','','0.000000','0.00','0.00',83,0,0);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_product_attribute_combination`;
CREATE TABLE `ps_product_attribute_combination` (
  `id_attribute` int(10) unsigned NOT NULL,
  `id_product_attribute` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_attribute`,`id_product_attribute`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_product_attribute_combination` WRITE;
INSERT INTO `ps_product_attribute_combination` VALUES (3,9),(3,12),(3,13),(3,14),(3,15),(3,29),(3,30),(4,7),(4,25),(4,26),(4,43),(4,44),(4,45),(5,10),(5,35),(5,36),(6,8),(6,39),(6,40),(7,33),(7,34),(8,13),(8,15),(9,12),(9,14),(10,12),(10,13),(11,14),(11,15),(14,31),(14,32),(14,46),(14,47),(14,48),(15,19),(15,26),(15,28),(15,30),(15,32),(15,34),(15,36),(15,40),(15,42),(16,22),(16,25),(16,27),(16,29),(16,31),(16,33),(16,35),(16,39),(16,41),(17,23),(18,41),(18,42),(19,27),(19,28),(20,49),(20,50),(20,51),(21,45),(21,48),(21,51),(22,44),(22,47),(22,50),(23,43),(23,46),(23,49);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_product_attribute_image`;
CREATE TABLE `ps_product_attribute_image` (
  `id_product_attribute` int(10) NOT NULL,
  `id_image` int(10) NOT NULL,
  PRIMARY KEY  (`id_product_attribute`,`id_image`),
  KEY `id_image` (`id_image`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_product_attribute_image` WRITE;
INSERT INTO `ps_product_attribute_image` VALUES (7,46),(8,47),(9,49),(10,48),(12,0),(13,0),(14,0),(15,0),(19,0),(22,0),(23,0),(25,38),(26,38),(27,45),(28,45),(29,44),(30,44),(31,37),(32,37),(33,40),(34,40),(35,41),(36,41),(39,39),(40,39),(41,42),(42,42);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_product_download`;
CREATE TABLE `ps_product_download` (
  `id_product_download` int(10) unsigned NOT NULL auto_increment,
  `id_product` int(10) unsigned NOT NULL,
  `display_filename` varchar(255) default NULL,
  `physically_filename` varchar(255) default NULL,
  `date_deposit` datetime NOT NULL,
  `date_expiration` datetime default NULL,
  `nb_days_accessible` int(10) unsigned default NULL,
  `nb_downloadable` int(10) unsigned default '1',
  `active` tinyint(1) unsigned NOT NULL default '1',
  PRIMARY KEY  (`id_product_download`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_product_lang`;
CREATE TABLE `ps_product_lang` (
  `id_product` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `description` text,
  `description_short` text,
  `link_rewrite` varchar(128) NOT NULL,
  `meta_description` varchar(255) default NULL,
  `meta_keywords` varchar(255) default NULL,
  `meta_title` varchar(128) default NULL,
  `name` varchar(128) NOT NULL,
  `available_now` varchar(255) default NULL,
  `available_later` varchar(255) default NULL,
  UNIQUE KEY `product_lang_index` (`id_product`,`id_lang`),
  KEY `id_lang` (`id_lang`),
  KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_product_lang` WRITE;
INSERT INTO `ps_product_lang` VALUES (1,1,'<p><strong><span style=\"font-size: small\">Curved ahead of the curve.</span></strong></p>\r\n<p>For those about to rock, we give you nine amazing colors. But that\'s only part of the story. Feel the curved, all-aluminum and glass design and you won\'t want to put iPod nano down.</p>\r\n<p><strong><span style=\"font-size: small\">Great looks. And brains, too.</span></strong></p>\r\n<p>The new Genius feature turns iPod nano into your own highly intelligent, personal DJ. It creates playlists by finding songs in your library that go great together.</p>\r\n<p><strong><span style=\"font-size: small\">Made to move with your moves.</span></strong></p>\r\n<p>The accelerometer comes to iPod nano. Give it a shake to shuffle your music. Turn it sideways to view Cover Flow. And play games designed with your moves in mind.</p>','<p>New design. New features. Now in 8GB and 16GB. iPod nano rocks like never before.</p>','ipod-nano','','','','iPod Nano','In stock',''),(1,2,'<p><span style=\"font-size: small\"><strong>Des courbes avantageuses.</strong></span></p>\r\n<p>Pour les amateurs de sensations, voici neuf nouveaux coloris. Et ce n\'est pas tout ! Faites l\'experience du design elliptique en aluminum et verre. Vous ne voudrez plus le lacher.</p>\r\n<p><strong><span style=\"font-size: small\">Beau et intelligent.</span></strong></p>\r\n<p>La nouvelle fonctionnalite Genius fait d\'iPod nano votre DJ personnel. Genius cree des listes de lecture en recherchant dans votre bibliotheque les chansons qui vont bien ensemble.</p>\r\n<p><strong><span style=\"font-size: small\">Fait pour bouger avec vous.</span></strong></p>\r\n<p>iPod nano est equipe de l\'accelerometre. Secouez-le pour melanger votre musique. Basculez-le pour afficher Cover Flow. Et decouvrez des jeux adaptes a vos mouvements.</p>','<p>Nouveau design. Nouvelles fonctionnalites. Desormais en 8 et 16 Go. iPod nano, plus rock que jamais.</p>','ipod-nano','','','','iPod Nano','En stock',''),(2,1,'<p><span style=\"font-size: small\"><strong>Instant attachment.</strong></span></p>\r\n<p>Wear up to 500 songs on your sleeve. Or your belt. Or your gym shorts. iPod shuffle is a badge of musical devotion. Now in new, more brilliant colors.</p>\r\n<p><span style=\"font-size: small\"><strong>Feed your iPod shuffle.</strong></span></p>\r\n<p>iTunes is your entertainment superstore. It’s your ultra-organized music collection and jukebox. And it’s how you load up your iPod shuffle in one click.</p>\r\n<p><span style=\"font-size: small\"><strong>Beauty and the beat.</strong></span></p>\r\n<p>Intensely colorful anodized aluminum complements the simple design of iPod shuffle. Now in blue, green, pink, red, and original silver.</p>','<p>iPod shuffle, the world’s most wearable music player, now clips on in more vibrant blue, green, pink, and red.</p>','ipod-shuffle','','','','iPod shuffle','In stock',''),(2,2,'<p><span style=\"font-size: small\"><strong>Un lien immediat.</strong></span></p>\r\n<p>Portez jusqu\'a 500 chansons accrochees a votre manche, a votre ceinture ou a votre short. Arborez votre iPod shuffle comme signe exterieur de votre passion pour la musique. Existe desormais en quatre nouveaux coloris encore plus eclatants.</p>\r\n<p><span style=\"font-size: small\"><strong>Emplissez votre iPod shuffle.</strong></span></p>\r\n<p>iTunes est un immense magasin dedie au divertissement, une collection musicale parfaitement organisee et un jukebox. Vous pouvez en un seul clic remplir votre iPod shuffle de chansons.</p>\r\n<p><strong><span style=\"font-size: small\">La musique en technicolor.</span></strong></p>\r\n<p>iPod shuffle s\'affiche desormais dans de nouveaux coloris intenses qui rehaussent le design epure du boitier en aluminium anodise. Choisissez parmi le bleu, le vert, le rose, le rouge et l\'argente d\'origine.</p>','<p>iPod shuffle, le baladeur le plus portable du monde, se clippe maintenant en bleu, vert, rose et rouge.</p>','ipod-shuffle','','','','iPod shuffle','En stock',''),(5,1,'<p>MacBook Air is nearly as thin as your index finger. Practically every detail that could be streamlined has been. Yet it still has a 13.3-inch widescreen LED display, full-size keyboard, and large multi-touch trackpad. It’s incomparably portable without the usual ultraportable screen and keyboard compromises.</p><p>The incredible thinness of MacBook Air is the result of numerous size- and weight-shaving innovations. From a slimmer hard drive to strategically hidden I/O ports to a lower-profile battery, everything has been considered and reconsidered with thinness in mind.</p><p>MacBook Air is designed and engineered to take full advantage of the wireless world. A world in which 802.11n Wi-Fi is now so fast and so available, people are truly living untethered — buying and renting movies online, downloading software, and sharing and storing files on the web. </p>','MacBook Air is ultrathin, ultraportable, and ultra unlike anything else. But you don’t lose inches and pounds overnight. It’s the result of rethinking conventions. Of multiple wireless innovations. And of breakthrough design. With MacBook Air, mobile computing suddenly has a new standard.','macbook-air','','','','MacBook Air','',NULL),(5,2,'<p>MacBook Air est presque aussi fin que votre index. Pratiquement tout ce qui pouvait etre simplifie l\'a ete. Il n\'en dispose pas moins d\'un ecran panoramique de 13,3 pouces, d\'un clavier complet et d\'un vaste trackpad multi-touch. Incomparablement portable il vous evite les compromis habituels en matiere d\'ecran et de clavier ultra-portables.</p><p>L\'incroyable finesse de MacBook Air est le resultat d\'un grand nombre d\'innovations en termes de reduction de la taille et du poids. D\'un disque dur plus fin a des ports d\'E/S habilement dissimules en passant par une batterie plus plate, chaque detail a ete considere et reconsidere avec la finesse a l\'esprit.</p><p>MacBook Air a ete concu et elabore pour profiter pleinement du monde sans fil. Un monde dans lequel la norme Wi-Fi 802.11n est desormais si rapide et si accessible qu\'elle permet veritablement de se liberer de toute attache pour acheter des videos en ligne, telecharger des logiceeeeiels, stocker et partager des fichiers sur le Web. </p>','MacBook Air est ultra fin, ultra portable et ultra different de tout le reste. Mais on ne perd pas des kilos et des centimetres en une nuit. C\'est le resultat d\'une reinvention des normes. D\'une multitude d\'innovations sans fil. Et d\'une revolution dans le design. Avec MacBook Air, l\'informatique mobile prend soudain une nouvelle dimension.','macbook-air','','','','MacBook Air','',NULL),(6,1,'Every MacBook has a larger hard drive, up to 250GB, to store growing media collections and valuable data.<br /><br />The 2.4GHz MacBook models now include 2GB of memory standard — perfect for running more of your favorite applications smoothly.','MacBook makes it easy to hit the road thanks to its tough polycarbonate case, built-in wireless technologies, and innovative MagSafe Power Adapter that releases automatically if someone accidentally trips on the cord.','macbook','','','','MacBook','',NULL),(6,2,'Chaque MacBook est equipe d\'un disque dur plus spacieux, d\'une capacite atteignant 250 Go, pour stocker vos collections multimedia en expansion et vos donnees precieuses.<br /><br />Le modele MacBook a 2,4 GHz integre desormais 2 Go de memoire en standard. L\'ideal pour executer en souplesse vos applications preferees.','MacBook vous offre la liberte de mouvement grace a son boitier resistant en polycarbonate, a ses technologies sans fil integrees et a son adaptateur secteur MagSafe novateur qui se deconnecte automatiquement si quelqu\'un se prend les pieds dans le fil.','macbook','','','','MacBook','',NULL),(7,1,'<h3>Five new hands-on applications</h3>\r\n<p>View rich HTML email with photos as well as PDF, Word, and Excel attachments. Get maps, directions, and real-time traffic information. Take notes and read stock and weather reports.</p>\r\n<h3>Touch your music, movies, and more</h3>\r\n<p>The revolutionary Multi-Touch technology built into the gorgeous 3.5-inch display lets you pinch, zoom, scroll, and flick with your fingers.</p>\r\n<h3>Internet in your pocket</h3>\r\n<p>With the Safari web browser, see websites the way they were designed to be seen and zoom in and out with a tap.<sup>2</sup> And add Web Clips to your Home screen for quick access to favorite sites.</p>\r\n<h3>What\'s in the box</h3>\r\n<ul>\r\n<li><span></span>iPod touch</li>\r\n<li><span></span>Earphones</li>\r\n<li><span></span>USB 2.0 cable</li>\r\n<li><span></span>Dock adapter</li>\r\n<li><span></span>Polishing cloth</li>\r\n<li><span></span>Stand</li>\r\n<li><span></span>Quick Start guide</li>\r\n</ul>','<ul>\r\n<li>Revolutionary Multi-Touch interface</li>\r\n<li>3.5-inch widescreen color display</li>\r\n<li>Wi-Fi (802.11b/g)</li>\r\n<li>8 mm thin</li>\r\n<li>Safari, YouTube, Mail, Stocks, Weather, Notes, iTunes Wi-Fi Music Store, Maps</li>\r\n</ul>','ipod-touch','','','','iPod touch','',NULL),(7,2,'<h1>Titre 1</h1>\r\n<h2>Titre 2</h2>\r\n<h3>Titre 3</h3>\r\n<h4>Titre 4</h4>\r\n<h5>Titre 5</h5>\r\n<h6>Titre 6</h6>\r\n<ul>\r\n<li>UL</li>\r\n<li>UL</li>\r\n<li>UL</li>\r\n<li>UL</li>\r\n</ul>\r\n<ol>\r\n<li>OL</li>\r\n<li>OL</li>\r\n<li>OL</li>\r\n<li>OL</li>\r\n</ol>\r\n<p>paragraphe...</p>\r\n<p>paragraphe...</p>\r\n<p>paragraphe...</p>\r\n<table border=\"0\">\r\n<thead> \r\n<tr>\r\n<th>th</th> <th>th</th> <th>th</th>\r\n</tr>\r\n</thead> \r\n<tbody>\r\n<tr>\r\n<td>td</td>\r\n<td>td</td>\r\n<td>td</td>\r\n</tr>\r\n<tr>\r\n<td>td</td>\r\n<td>td</td>\r\n<td>td</td>\r\n</tr>\r\n</tbody>\r\n</table>\r\n<h3>Cinq nouvelles applications sous la main</h3>\r\n<p>Consultez vos e-mails au format HTML enrichi, avec photos et pieces jointes au format PDF, Word et Excel. Obtenez des cartes, des itineraires et des informations sur l\'etat de la circulation en temps reel. Redigez des notes et consultez les cours de la Bourse et les bulletins meteo.</p>\r\n<h3>Touchez du doigt votre musique et vos videos. Entre autres.</h3>\r\n<p>La technologie multi-touch revolutionnaire integree au superbe ecran de 3,5 pouces vous permet d\'effectuer des zooms avant et arriere, de faire defiler et de feuilleter des pages a l\'aide de vos seuls doigts.</p>\r\n<h3>Internet dans votre poche</h3>\r\n<p>Avec le navigateur Safari, vous pouvez consulter des sites web dans leur mise en page d\'origine et effectuer un zoom avant et arriere d\'une simple pression sur l\'ecran.</p>\r\n<h3>Contenu du coffret</h3>\r\n<ul>\r\n<li><span></span>iPod touch</li>\r\n<li><span></span>Ecouteurs</li>\r\n<li><span></span>Cable USB 2.0</li>\r\n<li><span></span>Adaptateur Dock</li>\r\n<li><span></span>Chiffon de nettoyage</li>\r\n<li><span></span>Support</li>\r\n<li><span></span>Guide de demarrage rapide</li>\r\n</ul>\r\n<p> </p>','<p>Interface multi-touch revolutionnaire<br />Ecran panoramique couleur de 3,5 pouces<br />Wi-Fi (802.11b/g)<br />8 mm d\'epaisseur<br />Safari, YouTube, iTunes Wi-Fi Music Store, Courrier, Cartes, Bourse, Meteo, Notes</p>','ipod-touch','','','','iPod touch','En stock',NULL),(8,1,'<p>Lorem ipsum</p>','<p>Lorem ipsum</p>','housse-portefeuille-en-cuir-belkin-pour-ipod-nano-noir-chocolat','','','','Housse portefeuille en cuir Belkin pour iPod nano - Noir/Chocolat','',NULL),(8,2,'<p><strong>Caracteristiques</strong></p>\r\n<li>Cuir doux resistant<br /> </li>\r\n<li>Acces au bouton Hold<br /> </li>\r\n<li>Fermeture magnetique<br /> </li>\r\n<li>Acces au Dock Connector<br /> </li>\r\n<li>Protege-ecran</li>','<p>Cet etui en cuir tendance assure une protection complete contre les eraflures et les petits aleas de la vie quotidienne. Sa conception elegante et compacte vous permet de glisser votre iPod directement dans votre poche ou votre sac a main.</p>','housse-portefeuille-en-cuir-ipod-nano-noir-chocolat','','','','Housse portefeuille en cuir (iPod nano) - Noir/Chocolat','',NULL),(9,1,'<div class=\"product-overview-full\">Using Hi-Definition MicroSpeakers to deliver full-range audio, the ergonomic and lightweight design of the SE210 earphones is ideal for premium on-the-go listening on your iPod or iPhone. They offer the most accurate audio reproduction from both portable and home stereo audio sources--for the ultimate in precision highs and rich low end. In addition, the flexible design allows you to choose the most comfortable fit from a variety of wearing positions. <br /> <br /> <strong>Features </strong> <br /> \r\n<ul>\r\n<li>Sound-isolating design </li>\r\n<li> Hi-Definition MicroSpeaker with a single balanced armature driver </li>\r\n<li> Detachable, modular cable so you can make the cable longer or shorter depending on your activity </li>\r\n<li> Connector compatible with earphone ports on both iPod and iPhone </li>\r\n</ul>\r\n<strong>Specifications </strong><br /> \r\n<ul>\r\n<li>Speaker type: Hi-Definition MicroSpeaker </li>\r\n<li> Frequency range: 25Hz-18.5kHz </li>\r\n<li> Impedance (1kHz): 26 Ohms </li>\r\n<li> Sensitivity (1mW): 114 dB SPL/mW </li>\r\n<li> Cable length (with extension): 18.0 in./45.0 cm (54.0 in./137.1 cm) </li>\r\n</ul>\r\n<strong>In the box</strong><br /> \r\n<ul>\r\n<li>Shure SE210 earphones </li>\r\n<li> Extension cable (36.0 in./91.4 cm) </li>\r\n<li> Three pairs foam earpiece sleeves (small, medium, large) </li>\r\n<li> Three pairs soft flex earpiece sleeves (small, medium, large) </li>\r\n<li> One pair triple-flange earpiece sleeves </li>\r\n<li> Carrying case </li>\r\n</ul>\r\nWarranty<br /> Two-year limited <br />(For details, please visit <br />www.shure.com/PersonalAudio/CustomerSupport/ProductReturnsAndWarranty/index.htm.) <br /><br /> Mfr. Part No.: SE210-A-EFS <br /><br />Note: Products sold through this website that do not bear the Apple Brand name are serviced and supported exclusively by their manufacturers in accordance with terms and conditions packaged with the products. Apple\'s Limited Warranty does not apply to products that are not Apple-branded, even if packaged or sold with Apple products. Please contact the manufacturer directly for technical support and customer service.</div>','<p>Evolved from personal monitor technology road-tested by pro musicians and perfected by Shure engineers, the lightweight and stylish SE210 delivers full-range audio that\'s free from outside noise.</p>','ecouteurs-a-isolation-sonore-shure-se210-blanc','','','','Shure SE210 Sound-Isolating Earphones for iPod and iPhone','',NULL),(9,2,'<p>Bases sur la technologie des moniteurs personnels testee sur la route par des musiciens professionnels et perfectionnee par les ingenieurs Shure, les ecouteurs SE210, legers et elegants, fournissent une sortie audio a gamme etendue exempte de tout bruit externe.</p>\r\n<p><img src=\"http://store.apple.com/Catalog/fr/Images/TM255_screen1.jpg\" border=\"0\" /></p>\r\n<p><strong>Conception a isolation sonore <br /></strong>Les embouts a isolation sonore fournis bloquent plus de 90 % du bruit ambiant. Combines a un design ergonomique seduisant et un cable modulaire, ils minimisent les intrusions du monde exterieur, vous permettant de vous concentrer sur votre musique. Concus pour les amoureux de la musique qui souhaitent faire evoluer leur appareil audio portable, les ecouteurs SE210 vous permettent d\'emmener la performance avec vous. <br /> <br /><strong>Micro-transducteur haute definition <br /></strong>Developpes pour une ecoute de qualite superieure en deplacement, les ecouteurs SE210 utilisent un seul transducteur a armature equilibree pour beneficier d\'une gamme audio etendue. Le resultat ? Un confort d\'ecoute epoustouflant qui restitue tous les details d\'un spectacle live.</p>\r\n<p><strong>Le kit universel Deluxe comprend les elements suivants : <br /></strong>- <strong><em>Embouts a isolation sonore</em></strong> <br />Les embouts a isolation sonore inclus ont un double role : bloquer les bruits ambiants et garantir un maintien et un confort personnalises. Comme chaque oreille est differente, le kit universel Deluxe comprend trois tailles (S, M, L) d\'embouts mousse et flexibles. Choisissez la taille et le style d\'embout qui vous conviennent le mieux : une bonne etancheite est un facteur cle pour optimiser l\'isolation sonore et la reponse des basses, ainsi que pour accroitre le confort en ecoute prolongee.<br /><br />- <em><strong>Cable modulaire</strong></em> <br />En se basant sur les commentaires de nombreux utilisateurs, les ingenieurs de Shure ont developpe une solution de cable detachable pour permettre un degre de personnalisation sans precedent. Le cable de 1 metre fourni vous permet d\'adapter votre confort en fonction de l\'activite et de l\'application.<br /> <br />- <em><strong>Etui de transport</strong></em> <br />Outre les embouts a isolation sonore et le cable modulaire, un etui de transport compact et resistant est fourni avec les ecouteurs SE210 pour vous permettre de ranger vos ecouteurs de maniere pratique et sans encombres.<br /> <br />- <strong><em>Garantie limitee de deux ans <br /></em></strong>Chaque solution SE210 achetee est couverte par une garantie pieces et main-d\'œuvre de deux ans.<br /><br /><strong>Caracteristiques techniques</strong></p>\r\n<ul>\r\n<li> Type de transducteur : micro-transducteur haute definition<br /></li>\r\n<li> Sensibilite (1 mW) : pression acoustique de 114 dB/mW<br /></li>\r\n<li> Impedance (a 1 kHz) : 26 W<br /></li>\r\n<li> Gamme de frequences : 25 Hz – 18,5 kHz<br /></li>\r\n<li> Longueur de cable / avec rallonge : 45 cm / 136 cm<br /></li>\r\n</ul>\r\n<p><strong>Contenu du coffret<br /></strong></p>\r\n<ul>\r\n<li> Ecouteurs Shure SE210<br /></li>\r\n<li> Kit universel Deluxe (embouts a isolation sonore, cable modulaire, etui de transport)</li>\r\n</ul>','<p>Les ecouteurs a isolation sonore ergonomiques et legers offrent la reproduction audio la plus fidele en provenance de sources audio stereo portables ou de salon.</p>','ecouteurs-a-isolation-sonore-shure-se210','','','','Ecouteurs a isolation sonore Shure SE210','',NULL),(10,1,'','','maillot-de-bain','','','','Maillot de Bain','',''),(10,2,'','','maillot-de-bain','','','','Maillot de Bain','',''),(11,1,'','','short','','','','Short','',''),(11,2,'','','short','','','','Short','','');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_product_sale`;
CREATE TABLE `ps_product_sale` (
  `id_product` int(10) unsigned NOT NULL,
  `quantity` int(10) unsigned NOT NULL default '0',
  `sale_nbr` int(10) unsigned NOT NULL default '0',
  `date_upd` date NOT NULL,
  PRIMARY KEY  (`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_product_sale` WRITE;
INSERT INTO `ps_product_sale` VALUES (11,13,2,'2009-09-17'),(10,29,8,'2009-09-17');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_product_tag`;
CREATE TABLE `ps_product_tag` (
  `id_product` int(10) unsigned NOT NULL,
  `id_tag` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_product`,`id_tag`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_product_tag` WRITE;
INSERT INTO `ps_product_tag` VALUES (1,2),(1,6),(1,7),(1,8),(2,6),(2,18),(5,8),(5,19),(5,20),(5,21),(6,5),(6,22),(7,23),(7,24),(9,25),(9,26),(9,27);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_state`;
CREATE TABLE `ps_state` (
  `id_state` int(10) unsigned NOT NULL auto_increment,
  `id_country` int(11) NOT NULL,
  `id_zone` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `iso_code` char(4) NOT NULL,
  `tax_behavior` smallint(1) NOT NULL default '0',
  `active` tinyint(1) NOT NULL default '0',
  PRIMARY KEY  (`id_state`)
) ENGINE=MyISAM AUTO_INCREMENT=53 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_state` WRITE;
INSERT INTO `ps_state` VALUES (1,21,2,'Alabama','AL',0,1),(2,21,2,'Alaska','AK',0,1),(3,21,2,'Arizona','AZ',0,1),(4,21,2,'Arkansas','AR',0,1),(5,21,2,'California','CA',0,1),(6,21,2,'Colorado','CO',0,1),(7,21,2,'Connecticut','CT',0,1),(8,21,2,'Delaware','DE',0,1),(9,21,2,'Florida','FL',0,1),(10,21,2,'Georgia','GA',0,1),(11,21,2,'Hawaii','HI',0,1),(12,21,2,'Idaho','ID',0,1),(13,21,2,'Illinois','IL',0,1),(14,21,2,'Indiana','IN',0,1),(15,21,2,'Iowa','IA',0,1),(16,21,2,'Kansas','KS',0,1),(17,21,2,'Kentucky','KY',0,1),(18,21,2,'Louisiana','LA',0,1),(19,21,2,'Maine','ME',0,1),(20,21,2,'Maryland','MD',0,1),(21,21,2,'Massachusetts','MA',0,1),(22,21,2,'Michigan','MI',0,1),(23,21,2,'Minnesota','MN',0,1),(24,21,2,'Mississippi','MS',0,1),(25,21,2,'Missouri','MO',0,1),(26,21,2,'Montana','MT',0,1),(27,21,2,'Nebraska','NE',0,1),(28,21,2,'Nevada','NV',0,1),(29,21,2,'New Hampshire','NH',0,1),(30,21,2,'New Jersey','NJ',0,1),(31,21,2,'New Mexico','NM',0,1),(32,21,2,'New York','NY',0,1),(33,21,2,'North Carolina','NC',0,1),(34,21,2,'North Dakota','ND',0,1),(35,21,2,'Ohio','OH',0,1),(36,21,2,'Oklahoma','OK',0,1),(37,21,2,'Oregon','OR',0,1),(38,21,2,'Pennsylvania','PA',0,1),(39,21,2,'Rhode Island','RI',0,1),(40,21,2,'South Carolina','SC',0,1),(41,21,2,'South Dakota','SD',0,1),(42,21,2,'Tennessee','TN',0,1),(43,21,2,'Texas','TX',0,1),(44,21,2,'Utah','UT',0,1),(45,21,2,'Vermont','VT',0,1),(46,21,2,'Virginia','VA',0,1),(47,21,2,'Washington','WA',0,1),(48,21,2,'West Virginia','WV',0,1),(49,21,2,'Wisconsin','WI',0,1),(50,21,2,'Wyoming','WY',0,1),(51,21,2,'Puerto Rico','PR',0,1),(52,21,2,'US Virgin Islands','VI',0,1);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_supplier`;
CREATE TABLE `ps_supplier` (
  `id_supplier` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_supplier`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_supplier` WRITE;
INSERT INTO `ps_supplier` VALUES (1,'AppleStore','2009-09-17 09:48:51','2009-09-17 09:48:51'),(2,'Shure Online Store','2009-09-17 09:48:51','2009-09-17 09:48:51');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_supplier_lang`;
CREATE TABLE `ps_supplier_lang` (
  `id_supplier` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `description` text,
  `meta_title` varchar(254) default NULL,
  `meta_keywords` varchar(254) default NULL,
  `meta_description` varchar(254) default NULL,
  PRIMARY KEY  (`id_supplier`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_tag`;
CREATE TABLE `ps_tag` (
  `id_tag` int(10) unsigned NOT NULL auto_increment,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY  (`id_tag`),
  KEY `tag_name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_tag` WRITE;
INSERT INTO `ps_tag` VALUES (5,1,'apple'),(6,2,'ipod'),(7,2,'nano'),(8,2,'apple'),(18,2,'shuffle'),(19,2,'macbook'),(20,2,'macbookair'),(21,2,'air'),(22,1,'superdrive'),(27,2,'marche'),(26,2,'casque'),(25,2,'ecouteurs'),(24,2,'ipod touch tacticle'),(23,1,'Ipod touch');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_tax`;
CREATE TABLE `ps_tax` (
  `id_tax` int(10) unsigned NOT NULL auto_increment,
  `rate` float NOT NULL,
  PRIMARY KEY  (`id_tax`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_tax` WRITE;
INSERT INTO `ps_tax` VALUES (1,19.6),(2,5.5),(3,17.5);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_tax_lang`;
CREATE TABLE `ps_tax_lang` (
  `id_tax` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  UNIQUE KEY `tax_lang_index` (`id_tax`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_tax_lang` WRITE;
INSERT INTO `ps_tax_lang` VALUES (1,1,'VAT 19.6%'),(1,2,'TVA 19.6%'),(2,1,'VAT 5.5%'),(2,2,'TVA 5.5%'),(3,1,'VAT 17.5%'),(3,2,'TVA UK 17.5%');
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_tax_state`;
CREATE TABLE `ps_tax_state` (
  `id_tax` int(10) unsigned NOT NULL,
  `id_state` int(10) unsigned NOT NULL,
  KEY `tax_state_index` (`id_tax`,`id_state`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ps_tax_zone`;
CREATE TABLE `ps_tax_zone` (
  `id_tax` int(10) unsigned NOT NULL,
  `id_zone` int(10) unsigned NOT NULL,
  KEY `tax_zone_index` (`id_tax`,`id_zone`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

LOCK TABLES `ps_tax_zone` WRITE;
INSERT INTO `ps_tax_zone` VALUES (1,1),(2,1);
UNLOCK TABLES;


DROP TABLE IF EXISTS `ps_zone`;
CREATE TABLE `ps_zone` (
  `id_zone` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  `enabled` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_zone`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

LOCK TABLES `ps_zone` WRITE;
INSERT INTO `ps_zone` VALUES (1,'Europe',1,1),(2,'US',1,1),(3,'Asia',1,1),(4,'Africa',1,1),(5,'Oceania',1,1);
UNLOCK TABLES;

