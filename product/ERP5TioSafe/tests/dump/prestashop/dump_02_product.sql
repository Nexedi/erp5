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
-- Table structure for table `ps_attribute`
--

DROP TABLE IF EXISTS `ps_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attribute` (
  `id_attribute` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_attribute_group` int(10) unsigned NOT NULL,
  `color` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id_attribute`),
  KEY `attribute_group` (`id_attribute_group`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute`
--

LOCK TABLES `ps_attribute` WRITE;
/*!40000 ALTER TABLE `ps_attribute` DISABLE KEYS */;
INSERT INTO `ps_attribute` VALUES (1,1,NULL),(2,1,NULL),(3,2,'#D2D6D5'),(4,2,'#008CB7'),(5,2,'#F3349E'),(6,2,'#93D52D'),(7,2,'#FD9812'),(8,1,NULL),(9,1,NULL),(10,3,NULL),(11,3,NULL),(12,1,NULL),(13,1,NULL),(14,2,NULL),(15,1,''),(16,1,''),(17,1,''),(18,2,'#7800F0'),(19,2,'#F6EF04'),(20,2,'#F60409'),(21,5,'#000000'),(22,5,'#000000'),(23,5,'#000000'),(24,5,'#000000'),(25,5,'#000000');
/*!40000 ALTER TABLE `ps_attribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_attribute_group`
--

DROP TABLE IF EXISTS `ps_attribute_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attribute_group` (
  `id_attribute_group` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `is_color_group` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_attribute_group`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute_group`
--

LOCK TABLES `ps_attribute_group` WRITE;
/*!40000 ALTER TABLE `ps_attribute_group` DISABLE KEYS */;
INSERT INTO `ps_attribute_group` VALUES (1,0),(2,1),(3,0),(5,0);
/*!40000 ALTER TABLE `ps_attribute_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_attribute_group_lang`
--

DROP TABLE IF EXISTS `ps_attribute_group_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attribute_group_lang` (
  `id_attribute_group` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  `public_name` varchar(64) NOT NULL,
  PRIMARY KEY (`id_attribute_group`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute_group_lang`
--

LOCK TABLES `ps_attribute_group_lang` WRITE;
/*!40000 ALTER TABLE `ps_attribute_group_lang` DISABLE KEYS */;
INSERT INTO `ps_attribute_group_lang` VALUES (1,1,'Disk space','Disk space'),(1,2,'CapacitÃ©','CapacitÃ©'),(2,1,'Color','Color'),(2,2,'Couleur','Couleur'),(3,1,'ICU','Processor'),(3,2,'ICU','Processeur'),(5,2,'size','Taille'),(5,1,'size','Taille');
/*!40000 ALTER TABLE `ps_attribute_group_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_attribute_lang`
--

DROP TABLE IF EXISTS `ps_attribute_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attribute_lang` (
  `id_attribute` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  UNIQUE KEY `attribute_lang_index` (`id_attribute`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute_lang`
--

LOCK TABLES `ps_attribute_lang` WRITE;
/*!40000 ALTER TABLE `ps_attribute_lang` DISABLE KEYS */;
INSERT INTO `ps_attribute_lang` VALUES (1,1,'2GB'),(1,2,'2Go'),(2,1,'4GB'),(2,2,'4Go'),(3,1,'Metal'),(3,2,'Metal'),(4,1,'Blue'),(4,2,'Bleu'),(5,1,'Pink'),(5,2,'Rose'),(6,1,'Green'),(6,2,'Vert'),(7,1,'Orange'),(7,2,'Orange'),(8,1,'Optional 64GB solid-state drive'),(8,2,'Disque dur SSD (solid-state drive) de 64 Go '),(9,1,'80GB Parallel ATA Drive @ 4200 rpm'),(9,2,'Disque dur PATA de 80 Go Ã|  4 200 tr/min'),(10,1,'1.60GHz Intel Core 2 Duo'),(10,2,'Intel Core 2 Duo Ã|  1,6 GHz'),(11,1,'1.80GHz Intel Core 2 Duo'),(11,2,'Intel Core 2 Duo Ã|  1,8 GHz'),(12,1,'80GB: 20,000 Songs'),(12,2,'80 Go : 20 000 chansons'),(13,1,'160GB: 40,000 Songs'),(13,2,'160 Go : 40 000 chansons'),(14,2,'Noir'),(14,1,'Black'),(15,1,'8Go'),(15,2,'8Go'),(16,1,'16Go'),(16,2,'16Go'),(17,1,'32Go'),(17,2,'32Go'),(18,1,'Purple'),(18,2,'Violet'),(19,1,'Yellow'),(19,2,'Jaune'),(20,1,'Red'),(20,2,'Rouge'),(21,1,'S'),(21,2,'S'),(22,1,'M'),(22,2,'M'),(23,1,'L'),(23,2,'L'),(24,1,'XL'),(24,2,'XL'),(25,1,'XXL'),(25,2,'XXL');
/*!40000 ALTER TABLE `ps_attribute_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_category_product`
--

DROP TABLE IF EXISTS `ps_category_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_category_product` (
  `id_category` int(10) unsigned NOT NULL,
  `id_product` int(10) unsigned NOT NULL,
  `position` int(10) unsigned NOT NULL DEFAULT '0',
  KEY `category_product_index` (`id_category`,`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_category_product`
--

LOCK TABLES `ps_category_product` WRITE;
/*!40000 ALTER TABLE `ps_category_product` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_category_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_image`
--

DROP TABLE IF EXISTS `ps_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_image` (
  `id_image` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_product` int(10) unsigned NOT NULL,
  `position` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `cover` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_image`),
  KEY `image_product` (`id_product`)
) ENGINE=MyISAM AUTO_INCREMENT=58 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_image`
--

LOCK TABLES `ps_image` WRITE;
/*!40000 ALTER TABLE `ps_image` DISABLE KEYS */;
INSERT INTO `ps_image` VALUES (40,1,4,0),(39,1,3,0),(38,1,2,0),(37,1,1,1),(48,2,3,0),(47,2,2,0),(49,2,4,0),(46,2,1,1),(15,5,1,1),(16,5,2,0),(17,5,3,0),(18,6,4,0),(19,6,5,0),(20,6,1,1),(24,7,1,1),(33,8,1,1),(27,7,3,0),(26,7,2,0),(29,7,4,0),(30,7,5,0),(32,7,6,0),(36,9,1,1),(41,1,5,0),(42,1,6,0),(44,1,7,0),(45,1,8,0),(50,51,1,1),(51,53,1,1),(54,59,1,1),(53,58,1,1),(56,174,1,1),(57,173,1,1);
/*!40000 ALTER TABLE `ps_image` ENABLE KEYS */;
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
-- Table structure for table `ps_product`
--

DROP TABLE IF EXISTS `ps_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_product` (
  `id_product` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_supplier` int(10) unsigned DEFAULT NULL,
  `id_manufacturer` int(10) unsigned DEFAULT NULL,
  `id_tax` int(10) unsigned NOT NULL,
  `id_category_default` int(10) unsigned DEFAULT NULL,
  `id_color_default` int(10) unsigned DEFAULT NULL,
  `on_sale` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `ean13` varchar(13) DEFAULT NULL,
  `ecotax` decimal(10,2) NOT NULL DEFAULT '0.00',
  `quantity` int(10) unsigned NOT NULL DEFAULT '0',
  `price` decimal(13,6) NOT NULL DEFAULT '0.000000',
  `wholesale_price` decimal(13,6) NOT NULL DEFAULT '0.000000',
  `reduction_price` decimal(10,2) DEFAULT NULL,
  `reduction_percent` float DEFAULT NULL,
  `reduction_from` date DEFAULT NULL,
  `reduction_to` date DEFAULT NULL,
  `reference` varchar(32) DEFAULT NULL,
  `supplier_reference` varchar(32) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `weight` float NOT NULL DEFAULT '0',
  `out_of_stock` int(10) unsigned NOT NULL DEFAULT '2',
  `quantity_discount` tinyint(1) DEFAULT '0',
  `customizable` tinyint(2) NOT NULL DEFAULT '0',
  `uploadable_files` tinyint(4) NOT NULL DEFAULT '0',
  `text_fields` tinyint(4) NOT NULL DEFAULT '0',
  `active` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY (`id_product`),
  KEY `product_supplier` (`id_supplier`),
  KEY `product_manufacturer` (`id_manufacturer`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product`
--

LOCK TABLES `ps_product` WRITE;
/*!40000 ALTER TABLE `ps_product` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product_attribute`
--

DROP TABLE IF EXISTS `ps_product_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_product_attribute` (
  `id_product_attribute` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_image` int(10) unsigned DEFAULT NULL,
  `id_product` int(10) unsigned NOT NULL,
  `reference` varchar(32) DEFAULT NULL,
  `supplier_reference` varchar(32) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `ean13` varchar(13) DEFAULT NULL,
  `wholesale_price` decimal(13,6) NOT NULL DEFAULT '0.000000',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `ecotax` decimal(10,2) NOT NULL DEFAULT '0.00',
  `quantity` int(10) unsigned NOT NULL DEFAULT '0',
  `weight` float NOT NULL DEFAULT '0',
  `default_on` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_product_attribute`),
  KEY `product_attribute_product` (`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_attribute`
--

LOCK TABLES `ps_product_attribute` WRITE;
/*!40000 ALTER TABLE `ps_product_attribute` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_attribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product_attribute_combination`
--

DROP TABLE IF EXISTS `ps_product_attribute_combination`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_product_attribute_combination` (
  `id_attribute` int(10) unsigned NOT NULL,
  `id_product_attribute` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id_attribute`,`id_product_attribute`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_attribute_combination`
--

LOCK TABLES `ps_product_attribute_combination` WRITE;
/*!40000 ALTER TABLE `ps_product_attribute_combination` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_attribute_combination` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product_lang`
--

DROP TABLE IF EXISTS `ps_product_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_product_lang` (
  `id_product` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `description` text,
  `description_short` text,
  `link_rewrite` varchar(128) NOT NULL,
  `meta_description` varchar(255) DEFAULT NULL,
  `meta_keywords` varchar(255) DEFAULT NULL,
  `meta_title` varchar(128) DEFAULT NULL,
  `name` varchar(128) NOT NULL,
  `available_now` varchar(255) DEFAULT NULL,
  `available_later` varchar(255) DEFAULT NULL,
  UNIQUE KEY `product_lang_index` (`id_product`,`id_lang`),
  FULLTEXT KEY `fts` (`name`,`description_short`,`description`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_lang`
--

LOCK TABLES `ps_product_lang` WRITE;
/*!40000 ALTER TABLE `ps_product_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_lang` ENABLE KEYS */;
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
-- Table structure for table `ps_tax`
--

DROP TABLE IF EXISTS `ps_tax`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_tax` (
  `id_tax` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `rate` float NOT NULL,
  PRIMARY KEY (`id_tax`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_tax`
--

LOCK TABLES `ps_tax` WRITE;
/*!40000 ALTER TABLE `ps_tax` DISABLE KEYS */;
INSERT INTO `ps_tax` VALUES (1,19.6),(2,5.5),(3,17.5);
/*!40000 ALTER TABLE `ps_tax` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_tax_lang`
--

DROP TABLE IF EXISTS `ps_tax_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_tax_lang` (
  `id_tax` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  UNIQUE KEY `tax_lang_index` (`id_tax`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_tax_lang`
--

LOCK TABLES `ps_tax_lang` WRITE;
/*!40000 ALTER TABLE `ps_tax_lang` DISABLE KEYS */;
INSERT INTO `ps_tax_lang` VALUES (1,1,'VAT 19.6%'),(1,2,'TVA 19.6%'),(2,1,'VAT 5.5%'),(2,2,'TVA 5.5%'),(3,1,'VAT 17.5%'),(3,2,'TVA UK 17.5%');
/*!40000 ALTER TABLE `ps_tax_lang` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-10-15  8:44:23
