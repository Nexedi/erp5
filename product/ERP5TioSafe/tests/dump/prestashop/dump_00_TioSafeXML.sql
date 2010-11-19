-- MySQL dump 10.13  Distrib 5.1.34, for mandriva-linux-gnu (x86_64)
--
-- Host: localhost    Database: dump_test
-- ------------------------------------------------------
-- Server version	5.1.34-Max

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ps_address`
--

DROP TABLE IF EXISTS `ps_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_address` (
  `id_address` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_country` int(10) unsigned NOT NULL,
  `id_state` int(10) unsigned DEFAULT NULL,
  `id_customer` int(10) unsigned NOT NULL DEFAULT '0',
  `id_manufacturer` int(10) unsigned NOT NULL DEFAULT '0',
  `id_supplier` int(10) unsigned NOT NULL DEFAULT '0',
  `alias` varchar(32) NOT NULL,
  `company` varchar(32) DEFAULT NULL,
  `lastname` varchar(32) NOT NULL,
  `firstname` varchar(32) NOT NULL,
  `address1` varchar(128) NOT NULL,
  `address2` varchar(128) DEFAULT NULL,
  `postcode` varchar(12) DEFAULT NULL,
  `city` varchar(64) NOT NULL,
  `other` text,
  `phone` varchar(16) DEFAULT NULL,
  `phone_mobile` varchar(16) DEFAULT NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  `active` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `deleted` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_address`),
  KEY `address_customer` (`id_customer`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_address`
--

LOCK TABLES `ps_address` WRITE;
/*!40000 ALTER TABLE `ps_address` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_country`
--

DROP TABLE IF EXISTS `ps_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_country` (
  `id_country` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_zone` int(10) unsigned NOT NULL,
  `iso_code` varchar(3) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `contains_states` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_country`),
  KEY `country_iso_code` (`iso_code`),
  KEY `country_` (`id_zone`)
) ENGINE=MyISAM AUTO_INCREMENT=35 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_country`
--

LOCK TABLES `ps_country` WRITE;
/*!40000 ALTER TABLE `ps_country` DISABLE KEYS */;
INSERT INTO `ps_country` VALUES (1,1,'DE',1,0),(2,1,'AT',1,0),(3,1,'BE',1,0),(4,2,'CA',1,0),(5,3,'CN',1,0),(6,1,'ES',1,0),(7,1,'FI',1,0),(8,1,'FR',1,0),(9,1,'GR',1,0),(10,1,'IT',1,0),(11,3,'JP',1,0),(12,1,'LU',1,0),(13,1,'NL',1,0),(14,1,'PL',1,0),(15,1,'PT',1,0),(16,1,'CZ',1,0),(17,1,'GB',1,0),(18,1,'SE',1,0),(19,1,'CH',1,0),(20,1,'DK',1,0),(21,2,'US',1,1),(22,3,'HK',1,0),(23,1,'NO',1,0),(24,5,'AU',1,0),(25,3,'SG',1,0),(26,1,'IE',1,0),(27,5,'NZ',1,0),(28,3,'KR',1,0),(29,3,'IL',1,0),(30,4,'ZA',1,0),(31,4,'NG',1,0),(32,4,'CI',1,0),(33,4,'TG',1,0),(34,2,'BO',1,0);
/*!40000 ALTER TABLE `ps_country` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_country_lang`
--

DROP TABLE IF EXISTS `ps_country_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_country_lang` (
  `id_country` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  UNIQUE KEY `country_lang_index` (`id_country`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_country_lang`
--

LOCK TABLES `ps_country_lang` WRITE;
/*!40000 ALTER TABLE `ps_country_lang` DISABLE KEYS */;
INSERT INTO `ps_country_lang` VALUES (1,1,'Germany'),(1,2,'Allemagne'),(2,1,'Austria'),(2,2,'Autriche'),(3,1,'Belgium'),(3,2,'Belgique'),(4,1,'Canada'),(4,2,'Canada'),(5,1,'China'),(5,2,'Chine'),(6,1,'Spain'),(6,2,'Espagne'),(7,1,'Finland'),(7,2,'Finlande'),(8,1,'France'),(8,2,'France'),(9,1,'Greece'),(9,2,'GrÃ¨ce'),(10,1,'Italy'),(10,2,'Italie'),(11,1,'Japan'),(11,2,'Japon'),(12,1,'Luxemburg'),(12,2,'Luxembourg'),(13,1,'Netherlands'),(13,2,'Pays-bas'),(14,1,'Poland'),(14,2,'Pologne'),(15,1,'Portugal'),(15,2,'Portugal'),(16,1,'Czech Republic'),(16,2,'RÃ©publique TchÃ¨que'),(17,1,'United Kingdom'),(17,2,'Royaume-Uni'),(18,1,'Sweden'),(18,2,'SuÃ¨de'),(19,1,'Switzerland'),(19,2,'Suisse'),(20,1,'Denmark'),(20,2,'Danemark'),(21,1,'USA'),(21,2,'USA'),(22,1,'HongKong'),(22,2,'Hong-Kong'),(23,1,'Norway'),(23,2,'NorvÃ¨ge'),(24,1,'Australia'),(24,2,'Australie'),(25,1,'Singapore'),(25,2,'Singapour'),(26,1,'Ireland'),(26,2,'Eire'),(27,1,'New Zealand'),(27,2,'Nouvelle-ZÃ©lande'),(28,1,'South Korea'),(28,2,'CorÃ©e du Sud'),(29,1,'Israel'),(29,2,'IsraÃ«l'),(30,1,'South Africa'),(30,2,'Afrique du Sud'),(31,1,'Nigeria'),(31,2,'Nigeria'),(32,1,'Ivory Coast'),(32,2,'CÃ´te d\'Ivoire'),(33,1,'Togo'),(33,2,'Togo'),(34,1,'Bolivia'),(34,2,'Bolivie');
/*!40000 ALTER TABLE `ps_country_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_customer`
--

DROP TABLE IF EXISTS `ps_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_customer` (
  `id_customer` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_gender` int(10) unsigned NOT NULL,
  `secure_key` varchar(32) NOT NULL DEFAULT '-1',
  `email` varchar(128) NOT NULL,
  `passwd` varchar(32) NOT NULL,
  `last_passwd_gen` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `birthday` date DEFAULT NULL,
  `lastname` varchar(32) NOT NULL,
  `newsletter` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `ip_registration_newsletter` varchar(15) DEFAULT NULL,
  `newsletter_date_add` datetime DEFAULT NULL,
  `optin` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `firstname` varchar(32) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `deleted` tinyint(1) NOT NULL DEFAULT '0',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY (`id_customer`),
  UNIQUE KEY `customer_email` (`email`),
  KEY `customer_login` (`email`,`passwd`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_customer`
--

LOCK TABLES `ps_customer` WRITE;
/*!40000 ALTER TABLE `ps_customer` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_lang`
--

DROP TABLE IF EXISTS `ps_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_lang` (
  `id_lang` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `active` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `iso_code` char(2) NOT NULL,
  PRIMARY KEY (`id_lang`),
  KEY `lang_iso_code` (`iso_code`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_lang`
--

LOCK TABLES `ps_lang` WRITE;
/*!40000 ALTER TABLE `ps_lang` DISABLE KEYS */;
INSERT INTO `ps_lang` VALUES (1,'English (English)',1,'en'),(2,'FranÃ§ais (French)',1,'fr');
/*!40000 ALTER TABLE `ps_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_manufacturer`
--

DROP TABLE IF EXISTS `ps_manufacturer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_manufacturer` (
  `id_manufacturer` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY (`id_manufacturer`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_manufacturer`
--

LOCK TABLES `ps_manufacturer` WRITE;
/*!40000 ALTER TABLE `ps_manufacturer` DISABLE KEYS */;
INSERT INTO `ps_manufacturer` VALUES (1,'Apple Computer, Inc','2009-06-09 11:36:02','2009-06-09 11:36:02'),(2,'Shure Incorporated','2009-06-09 11:36:02','2009-06-09 11:36:02');
/*!40000 ALTER TABLE `ps_manufacturer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_manufacturer_lang`
--

DROP TABLE IF EXISTS `ps_manufacturer_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_manufacturer_lang` (
  `id_manufacturer` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `description` text,
  PRIMARY KEY (`id_manufacturer`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_manufacturer_lang`
--

LOCK TABLES `ps_manufacturer_lang` WRITE;
/*!40000 ALTER TABLE `ps_manufacturer_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_manufacturer_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_state`
--

DROP TABLE IF EXISTS `ps_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_state` (
  `id_state` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_country` int(11) NOT NULL,
  `id_zone` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `iso_code` varchar(3) NOT NULL,
  `tax_behavior` smallint(1) NOT NULL DEFAULT '0',
  `active` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_state`)
) ENGINE=MyISAM AUTO_INCREMENT=53 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_state`
--

LOCK TABLES `ps_state` WRITE;
/*!40000 ALTER TABLE `ps_state` DISABLE KEYS */;
INSERT INTO `ps_state` VALUES (1,21,2,'Alabama','AL',0,1),(2,21,2,'Alaska','AK',0,1),(3,21,2,'Arizona','AZ',0,1),(4,21,2,'Arkansas','AR',0,1),(5,21,2,'California','CA',0,1),(6,21,2,'Colorado','CO',0,1),(7,21,2,'Connecticut','CT',0,1),(8,21,2,'Delaware','DE',0,1),(9,21,2,'Florida','FL',0,1),(10,21,2,'Georgia','GA',0,1),(11,21,2,'Hawaii','HI',0,1),(12,21,2,'Idaho','ID',0,1),(13,21,2,'Illinois','IL',0,1),(14,21,2,'Indiana','IN',0,1),(15,21,2,'Iowa','IA',0,1),(16,21,2,'Kansas','KS',0,1),(17,21,2,'Kentucky','KY',0,1),(18,21,2,'Louisiana','LA',0,1),(19,21,2,'Maine','ME',0,1),(20,21,2,'Maryland','MD',0,1),(21,21,2,'Massachusetts','MA',0,1),(22,21,2,'Michigan','MI',0,1),(23,21,2,'Minnesota','MN',0,1),(24,21,2,'Mississippi','MS',0,1),(25,21,2,'Missouri','MO',0,1),(26,21,2,'Montana','MT',0,1),(27,21,2,'Nebraska','NE',0,1),(28,21,2,'Nevada','NV',0,1),(29,21,2,'New Hampshire','NH',0,1),(30,21,2,'New Jersey','NJ',0,1),(31,21,2,'New Mexico','NM',0,1),(32,21,2,'New York','NY',0,1),(33,21,2,'North Carolina','NC',0,1),(34,21,2,'North Dakota','ND',0,1),(35,21,2,'Ohio','OH',0,1),(36,21,2,'Oklahoma','OK',0,1),(37,21,2,'Oregon','OR',0,1),(38,21,2,'Pennsylvania','PA',0,1),(39,21,2,'Rhode Island','RI',0,1),(40,21,2,'South Carolina','SC',0,1),(41,21,2,'South Dakota','SD',0,1),(42,21,2,'Tennessee','TN',0,1),(43,21,2,'Texas','TX',0,1),(44,21,2,'Utah','UT',0,1),(45,21,2,'Vermont','VT',0,1),(46,21,2,'Virginia','VA',0,1),(47,21,2,'Washington','WA',0,1),(48,21,2,'West Virginia','WV',0,1),(49,21,2,'Wisconsin','WI',0,1),(50,21,2,'Wyoming','WY',0,1),(51,21,2,'Puerto Rico','PR',0,1),(52,21,2,'US Virgin Islands','VI',0,1);
/*!40000 ALTER TABLE `ps_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_supplier`
--

DROP TABLE IF EXISTS `ps_supplier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_supplier` (
  `id_supplier` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY (`id_supplier`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_supplier`
--

LOCK TABLES `ps_supplier` WRITE;
/*!40000 ALTER TABLE `ps_supplier` DISABLE KEYS */;
INSERT INTO `ps_supplier` VALUES (1,'AppleStore','2009-06-09 11:36:02','2009-06-09 11:36:02'),(2,'Shure Online Store','2009-06-09 11:36:02','2009-06-09 11:36:02');
/*!40000 ALTER TABLE `ps_supplier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_supplier_lang`
--

DROP TABLE IF EXISTS `ps_supplier_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_supplier_lang` (
  `id_supplier` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `description` text,
  PRIMARY KEY (`id_supplier`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_supplier_lang`
--

LOCK TABLES `ps_supplier_lang` WRITE;
/*!40000 ALTER TABLE `ps_supplier_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_supplier_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_zone`
--

DROP TABLE IF EXISTS `ps_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_zone` (
  `id_zone` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `enabled` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_zone`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_zone`
--

LOCK TABLES `ps_zone` WRITE;
/*!40000 ALTER TABLE `ps_zone` DISABLE KEYS */;
INSERT INTO `ps_zone` VALUES (1,'Europe',1,1),(2,'US',1,1),(3,'Asia',1,1),(4,'Africa',1,1),(5,'Oceania',1,1);
/*!40000 ALTER TABLE `ps_zone` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-10-15  8:39:34
