-- MySQL dump 10.11
--
-- Host: localhost    Database: ps_dump
-- ------------------------------------------------------
-- Server version	5.0.87-Max

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
-- Table structure for table `ps_access`
--

DROP TABLE IF EXISTS `ps_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_access` (
  `id_profile` int(10) unsigned NOT NULL,
  `id_tab` int(10) unsigned NOT NULL,
  `view` int(11) NOT NULL,
  `add` int(11) NOT NULL,
  `edit` int(11) NOT NULL,
  `delete` int(11) NOT NULL,
  PRIMARY KEY  (`id_profile`,`id_tab`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_access`
--

LOCK TABLES `ps_access` WRITE;
/*!40000 ALTER TABLE `ps_access` DISABLE KEYS */;
INSERT INTO `ps_access` VALUES (1,1,1,1,1,1),(1,2,1,1,1,1),(1,3,1,1,1,1),(1,4,1,1,1,1),(1,5,1,1,1,1),(1,6,1,1,1,1),(1,7,1,1,1,1),(1,8,1,1,1,1),(1,9,1,1,1,1),(1,10,1,1,1,1),(1,11,1,1,1,1),(1,12,1,1,1,1),(1,13,1,1,1,1),(1,14,1,1,1,1),(1,15,1,1,1,1),(1,16,1,1,1,1),(1,17,1,1,1,1),(1,18,1,1,1,1),(1,19,1,1,1,1),(1,20,1,1,1,1),(1,21,1,1,1,1),(1,22,1,1,1,1),(1,23,1,1,1,1),(1,24,1,1,1,1),(1,26,1,1,1,1),(1,27,1,1,1,1),(1,28,1,1,1,1),(1,29,1,1,1,1),(1,30,1,1,1,1),(1,31,1,1,1,1),(1,32,1,1,1,1),(1,33,1,1,1,1),(1,34,1,1,1,1),(1,35,1,1,1,1),(1,36,1,1,1,1),(1,37,1,1,1,1),(1,38,1,1,1,1),(1,39,1,1,1,1),(1,40,1,1,1,1),(1,41,1,1,1,1),(1,42,1,1,1,1),(1,43,1,1,1,1),(1,44,1,1,1,1),(1,46,1,1,1,1),(1,47,1,1,1,1),(1,48,1,1,1,1),(1,49,1,1,1,1),(1,50,1,1,1,1),(1,51,1,1,1,1),(1,52,1,1,1,1),(1,53,1,1,1,1),(1,54,1,1,1,1),(1,55,1,1,1,1),(1,56,1,1,1,1),(1,57,1,1,1,1),(1,58,1,1,1,1),(1,59,1,1,1,1),(1,60,1,1,1,1),(1,61,1,1,1,1),(1,62,1,1,1,1),(1,63,1,1,1,1),(1,64,1,1,1,1),(1,65,1,1,1,1),(1,66,1,1,1,1),(1,67,1,1,1,1),(1,68,1,1,1,1);
/*!40000 ALTER TABLE `ps_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_accessory`
--

DROP TABLE IF EXISTS `ps_accessory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_accessory` (
  `id_product_1` int(10) unsigned NOT NULL,
  `id_product_2` int(10) unsigned NOT NULL,
  KEY `accessory_product` (`id_product_1`,`id_product_2`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_accessory`
--

LOCK TABLES `ps_accessory` WRITE;
/*!40000 ALTER TABLE `ps_accessory` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_accessory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_address`
--

DROP TABLE IF EXISTS `ps_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_address`
--

LOCK TABLES `ps_address` WRITE;
/*!40000 ALTER TABLE `ps_address` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_address` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_alias`
--

DROP TABLE IF EXISTS `ps_alias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_alias` (
  `id_alias` int(10) unsigned NOT NULL auto_increment,
  `alias` varchar(255) NOT NULL,
  `search` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL default '1',
  PRIMARY KEY  (`id_alias`),
  UNIQUE KEY `alias` (`alias`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_alias`
--

LOCK TABLES `ps_alias` WRITE;
/*!40000 ALTER TABLE `ps_alias` DISABLE KEYS */;
INSERT INTO `ps_alias` VALUES (4,'piod','ipod',1),(3,'ipdo','ipod',1);
/*!40000 ALTER TABLE `ps_alias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_attachment`
--

DROP TABLE IF EXISTS `ps_attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attachment` (
  `id_attachment` int(10) unsigned NOT NULL auto_increment,
  `file` varchar(40) NOT NULL,
  `mime` varchar(32) NOT NULL,
  PRIMARY KEY  (`id_attachment`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attachment`
--

LOCK TABLES `ps_attachment` WRITE;
/*!40000 ALTER TABLE `ps_attachment` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_attachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_attachment_lang`
--

DROP TABLE IF EXISTS `ps_attachment_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attachment_lang` (
  `id_attachment` int(10) unsigned NOT NULL auto_increment,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) default NULL,
  `description` text,
  PRIMARY KEY  (`id_attachment`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attachment_lang`
--

LOCK TABLES `ps_attachment_lang` WRITE;
/*!40000 ALTER TABLE `ps_attachment_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_attachment_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_attribute`
--

DROP TABLE IF EXISTS `ps_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attribute` (
  `id_attribute` int(10) unsigned NOT NULL auto_increment,
  `id_attribute_group` int(10) unsigned NOT NULL,
  `color` varchar(32) default NULL,
  PRIMARY KEY  (`id_attribute`),
  KEY `attribute_group` (`id_attribute_group`)
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute`
--

LOCK TABLES `ps_attribute` WRITE;
/*!40000 ALTER TABLE `ps_attribute` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_attribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_attribute_group`
--

DROP TABLE IF EXISTS `ps_attribute_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attribute_group` (
  `id_attribute_group` int(10) unsigned NOT NULL auto_increment,
  `is_color_group` tinyint(1) NOT NULL default '0',
  PRIMARY KEY  (`id_attribute_group`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute_group`
--

LOCK TABLES `ps_attribute_group` WRITE;
/*!40000 ALTER TABLE `ps_attribute_group` DISABLE KEYS */;
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
  PRIMARY KEY  (`id_attribute_group`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute_group_lang`
--

LOCK TABLES `ps_attribute_group_lang` WRITE;
/*!40000 ALTER TABLE `ps_attribute_group_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_attribute_group_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_attribute_impact`
--

DROP TABLE IF EXISTS `ps_attribute_impact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_attribute_impact` (
  `id_attribute_impact` int(10) unsigned NOT NULL auto_increment,
  `id_product` int(11) NOT NULL,
  `id_attribute` int(11) NOT NULL,
  `weight` float NOT NULL,
  `price` decimal(10,2) NOT NULL,
  PRIMARY KEY  (`id_attribute_impact`),
  UNIQUE KEY `id_product` (`id_product`,`id_attribute`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute_impact`
--

LOCK TABLES `ps_attribute_impact` WRITE;
/*!40000 ALTER TABLE `ps_attribute_impact` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_attribute_impact` ENABLE KEYS */;
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
  PRIMARY KEY  (`id_attribute`,`id_lang`),
  KEY `id_lang` (`id_lang`,`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_attribute_lang`
--

LOCK TABLES `ps_attribute_lang` WRITE;
/*!40000 ALTER TABLE `ps_attribute_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_attribute_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_block_cms`
--

DROP TABLE IF EXISTS `ps_block_cms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_block_cms` (
  `id_block` int(10) NOT NULL,
  `id_cms` int(10) NOT NULL,
  PRIMARY KEY  (`id_block`,`id_cms`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_block_cms`
--

LOCK TABLES `ps_block_cms` WRITE;
/*!40000 ALTER TABLE `ps_block_cms` DISABLE KEYS */;
INSERT INTO `ps_block_cms` VALUES (12,1),(12,2),(12,3),(12,4),(23,3),(23,4);
/*!40000 ALTER TABLE `ps_block_cms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_carrier`
--

DROP TABLE IF EXISTS `ps_carrier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_carrier`
--

LOCK TABLES `ps_carrier` WRITE;
/*!40000 ALTER TABLE `ps_carrier` DISABLE KEYS */;
INSERT INTO `ps_carrier` VALUES (1,0,'0',NULL,1,0,0,0,0),(2,1,'My carrier',NULL,1,0,1,0,0);
/*!40000 ALTER TABLE `ps_carrier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_carrier_lang`
--

DROP TABLE IF EXISTS `ps_carrier_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_carrier_lang` (
  `id_carrier` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `delay` varchar(128) default NULL,
  UNIQUE KEY `shipper_lang_index` (`id_lang`,`id_carrier`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_carrier_lang`
--

LOCK TABLES `ps_carrier_lang` WRITE;
/*!40000 ALTER TABLE `ps_carrier_lang` DISABLE KEYS */;
INSERT INTO `ps_carrier_lang` VALUES (1,1,'Pick up in-store'),(1,2,'Retrait au magasin'),(2,1,'Delivery next day!'),(2,2,'Livraison le lendemain !');
/*!40000 ALTER TABLE `ps_carrier_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_carrier_zone`
--

DROP TABLE IF EXISTS `ps_carrier_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_carrier_zone` (
  `id_carrier` int(10) unsigned NOT NULL,
  `id_zone` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_carrier`,`id_zone`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_carrier_zone`
--

LOCK TABLES `ps_carrier_zone` WRITE;
/*!40000 ALTER TABLE `ps_carrier_zone` DISABLE KEYS */;
INSERT INTO `ps_carrier_zone` VALUES (1,1),(2,1),(2,2);
/*!40000 ALTER TABLE `ps_carrier_zone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_cart`
--

DROP TABLE IF EXISTS `ps_cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_cart` (
  `id_cart` int(10) unsigned NOT NULL auto_increment,
  `id_carrier` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `id_address_delivery` int(10) unsigned NOT NULL,
  `id_address_invoice` int(10) unsigned NOT NULL,
  `id_currency` int(10) unsigned NOT NULL,
  `id_customer` int(10) unsigned NOT NULL,
  `id_guest` int(10) unsigned NOT NULL,
  `recyclable` tinyint(1) unsigned NOT NULL default '1',
  `gift` tinyint(1) unsigned NOT NULL default '0',
  `gift_message` text,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_cart`),
  KEY `cart_customer` (`id_customer`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_cart`
--

LOCK TABLES `ps_cart` WRITE;
/*!40000 ALTER TABLE `ps_cart` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_cart_discount`
--

DROP TABLE IF EXISTS `ps_cart_discount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_cart_discount` (
  `id_cart` int(10) unsigned NOT NULL,
  `id_discount` int(10) unsigned NOT NULL,
  KEY `cart_discount_index` (`id_cart`,`id_discount`),
  KEY `id_discount` (`id_discount`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_cart_discount`
--

LOCK TABLES `ps_cart_discount` WRITE;
/*!40000 ALTER TABLE `ps_cart_discount` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_cart_discount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_cart_product`
--

DROP TABLE IF EXISTS `ps_cart_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_cart_product` (
  `id_cart` int(10) unsigned NOT NULL,
  `id_product` int(10) unsigned NOT NULL,
  `id_product_attribute` int(10) unsigned default NULL,
  `quantity` int(10) unsigned NOT NULL default '0',
  `date_add` datetime NOT NULL,
  KEY `cart_product_index` (`id_cart`,`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_cart_product`
--

LOCK TABLES `ps_cart_product` WRITE;
/*!40000 ALTER TABLE `ps_cart_product` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_cart_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_category`
--

DROP TABLE IF EXISTS `ps_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_category`
--

LOCK TABLES `ps_category` WRITE;
/*!40000 ALTER TABLE `ps_category` DISABLE KEYS */;
INSERT INTO `ps_category` VALUES (1,0,0,1,'2010-06-08 14:08:09','2010-06-08 14:08:09'),(2,1,1,1,'2010-06-08 14:08:09','2010-06-08 14:08:09'),(3,1,1,1,'2010-06-08 14:08:09','2010-06-08 14:08:09'),(4,1,1,1,'2010-06-08 14:08:09','2010-06-08 14:08:09');
/*!40000 ALTER TABLE `ps_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_category_group`
--

DROP TABLE IF EXISTS `ps_category_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_category_group` (
  `id_category` int(10) unsigned NOT NULL,
  `id_group` int(10) unsigned NOT NULL,
  KEY `category_group_index` (`id_category`,`id_group`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_category_group`
--

LOCK TABLES `ps_category_group` WRITE;
/*!40000 ALTER TABLE `ps_category_group` DISABLE KEYS */;
INSERT INTO `ps_category_group` VALUES (1,1),(2,1),(3,1),(4,1);
/*!40000 ALTER TABLE `ps_category_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_category_lang`
--

DROP TABLE IF EXISTS `ps_category_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_category_lang`
--

LOCK TABLES `ps_category_lang` WRITE;
/*!40000 ALTER TABLE `ps_category_lang` DISABLE KEYS */;
INSERT INTO `ps_category_lang` VALUES (1,1,'Home','','home',NULL,NULL,NULL),(1,2,'Accueil','','home',NULL,NULL,NULL),(2,1,'iPods','Now that you can buy movies from the iTunes Store and sync them to your iPod, the whole world is your theater.','music-ipods','','',''),(2,2,'iPods','Il est temps, pour le meilleur lecteur de musique, de remonter sur scène pour un rappel. Avec le nouvel iPod, le monde est votre scène.','musique-ipods','','',''),(3,1,'Accessories','Wonderful accessories for your iPod','accessories-ipod','','',''),(3,2,'Accessoires','Tous les accessoires à la mode pour votre iPod','accessoires-ipod','','',''),(4,1,'Laptops','The latest Intel processor, a bigger hard drive, plenty of memory, and even more new features all fit inside just one liberating inch. The new Mac laptops have the performance, power, and connectivity of a desktop computer. Without the desk part.','laptops','Apple laptops','Apple laptops MacBook Air','Powerful and chic Apple laptops'),(4,2,'Portables','Le tout dernier processeur Intel, un disque dur plus spacieux, de la mémoire à profusion et d\'autres nouveautés. Le tout, dans à peine 2,59 cm qui vous libèrent de toute entrave. Les nouveaux portables Mac réunissent les performances, la puissance et la connectivité d\'un ordinateur de bureau. Sans la partie bureau.','portables-apple','Portables Apple','portables apple macbook air','portables apple puissants et design');
/*!40000 ALTER TABLE `ps_category_lang` ENABLE KEYS */;
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
  `position` int(10) unsigned NOT NULL default '0',
  KEY `category_product_index` (`id_category`,`id_product`),
  KEY `id_product` (`id_product`)
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
-- Table structure for table `ps_cms`
--

DROP TABLE IF EXISTS `ps_cms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_cms` (
  `id_cms` int(10) unsigned NOT NULL auto_increment,
  PRIMARY KEY  (`id_cms`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_cms`
--

LOCK TABLES `ps_cms` WRITE;
/*!40000 ALTER TABLE `ps_cms` DISABLE KEYS */;
INSERT INTO `ps_cms` VALUES (1),(2),(3),(4),(5);
/*!40000 ALTER TABLE `ps_cms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_cms_lang`
--

DROP TABLE IF EXISTS `ps_cms_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_cms_lang` (
  `id_cms` int(10) unsigned NOT NULL auto_increment,
  `id_lang` int(10) unsigned NOT NULL,
  `meta_title` varchar(128) NOT NULL,
  `meta_description` varchar(255) default NULL,
  `meta_keywords` varchar(255) default NULL,
  `content` longtext,
  `link_rewrite` varchar(128) NOT NULL,
  PRIMARY KEY  (`id_cms`,`id_lang`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_cms_lang`
--

LOCK TABLES `ps_cms_lang` WRITE;
/*!40000 ALTER TABLE `ps_cms_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_cms_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_configuration`
--

DROP TABLE IF EXISTS `ps_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_configuration` (
  `id_configuration` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(32) NOT NULL,
  `value` text,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_configuration`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=83 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_configuration`
--

LOCK TABLES `ps_configuration` WRITE;
/*!40000 ALTER TABLE `ps_configuration` DISABLE KEYS */;
INSERT INTO `ps_configuration` VALUES (1,'PS_LANG_DEFAULT','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(2,'PS_CURRENCY_DEFAULT','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(3,'PS_COUNTRY_DEFAULT','8','2010-06-08 14:08:09','2010-06-08 14:08:09'),(4,'PS_REWRITING_SETTINGS','0','2010-06-08 14:08:09','2010-06-08 14:08:09'),(5,'PS_ORDER_OUT_OF_STOCK','0','2010-06-08 14:08:09','2010-06-08 14:08:09'),(6,'PS_LAST_QTIES','3','2010-06-08 14:08:09','2010-06-08 14:08:09'),(7,'PS_CART_REDIRECT','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(8,'PS_HELPBOX','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(9,'PS_CONDITIONS','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(10,'PS_RECYCLABLE_PACK','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(11,'PS_GIFT_WRAPPING','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(12,'PS_GIFT_WRAPPING_PRICE','0','2010-06-08 14:08:09','2010-06-08 14:08:09'),(13,'PS_STOCK_MANAGEMENT','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(14,'PS_NAVIGATION_PIPE','>','2010-06-08 14:08:09','2010-06-08 14:08:09'),(15,'PS_PRODUCTS_PER_PAGE','10','2010-06-08 14:08:09','2010-06-08 14:08:09'),(16,'PS_PURCHASE_MINIMUM','0','2010-06-08 14:08:09','2010-06-08 14:08:09'),(17,'PS_PRODUCTS_ORDER_WAY','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(18,'PS_PRODUCTS_ORDER_BY','4','2010-06-08 14:08:09','2010-06-08 14:08:09'),(19,'PS_DISPLAY_QTIES','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(20,'PS_SHIPPING_HANDLING','2','2010-06-08 14:08:09','2010-06-08 14:08:09'),(21,'PS_SHIPPING_FREE_PRICE','300','2010-06-08 14:08:09','2010-06-08 14:08:09'),(22,'PS_SHIPPING_FREE_WEIGHT','20','2010-06-08 14:08:09','2010-06-08 14:08:09'),(23,'PS_SHIPPING_METHOD','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(24,'PS_TAX','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(25,'PS_SHOP_ENABLE','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(26,'PS_NB_DAYS_NEW_PRODUCT','20','2010-06-08 14:08:09','2010-06-08 14:08:09'),(27,'PS_SSL_ENABLED','0','2010-06-08 14:08:09','2010-06-08 14:08:09'),(28,'PS_WEIGHT_UNIT','kg','2010-06-08 14:08:09','2010-06-08 14:08:09'),(29,'PS_BLOCK_CART_AJAX','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(30,'PS_ORDER_RETURN','0','2010-06-08 14:08:09','2010-06-08 14:08:09'),(31,'PS_ORDER_RETURN_NB_DAYS','7','2010-06-08 14:08:09','2010-06-08 14:08:09'),(32,'PS_MAIL_TYPE','3','2010-06-08 14:08:09','2010-06-08 14:08:09'),(33,'PS_PRODUCT_PICTURE_MAX_SIZE','131072','2010-06-08 14:08:09','2010-06-08 14:08:09'),(34,'PS_PRODUCT_PICTURE_WIDTH','64','2010-06-08 14:08:09','2010-06-08 14:08:09'),(35,'PS_PRODUCT_PICTURE_HEIGHT','64','2010-06-08 14:08:09','2010-06-08 14:08:09'),(36,'PS_INVOICE_PREFIX','IN','2010-06-08 14:08:09','2010-06-08 14:08:09'),(37,'PS_INVOICE_NUMBER','2','2010-06-08 14:08:09','2010-06-08 14:08:09'),(38,'PS_DELIVERY_PREFIX','DE','2010-06-08 14:08:09','2010-06-08 14:08:09'),(39,'PS_DELIVERY_NUMBER','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(40,'PS_INVOICE','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(41,'PS_PASSWD_TIME_BACK','360','2010-06-08 14:08:09','2010-06-08 14:08:09'),(42,'PS_PASSWD_TIME_FRONT','360','2010-06-08 14:08:09','2010-06-08 14:08:09'),(43,'PS_DISP_UNAVAILABLE_ATTR','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(44,'PS_VOUCHERS','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(45,'PS_SEARCH_MINWORDLEN','3','2010-06-08 14:08:09','2010-06-08 14:08:09'),(46,'PS_SEARCH_BLACKLIST','','2010-06-08 14:08:09','2010-06-08 14:08:09'),(47,'PS_SEARCH_WEIGHT_PNAME','6','2010-06-08 14:08:09','2010-06-08 14:08:09'),(48,'PS_SEARCH_WEIGHT_REF','10','2010-06-08 14:08:09','2010-06-08 14:08:09'),(49,'PS_SEARCH_WEIGHT_SHORTDESC','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(50,'PS_SEARCH_WEIGHT_DESC','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(51,'PS_SEARCH_WEIGHT_CNAME','3','2010-06-08 14:08:09','2010-06-08 14:08:09'),(52,'PS_SEARCH_WEIGHT_MNAME','3','2010-06-08 14:08:09','2010-06-08 14:08:09'),(53,'PS_SEARCH_WEIGHT_TAG','4','2010-06-08 14:08:09','2010-06-08 14:08:09'),(54,'PS_SEARCH_WEIGHT_ATTRIBUTE','2','2010-06-08 14:08:09','2010-06-08 14:08:09'),(55,'PS_SEARCH_WEIGHT_FEATURE','2','2010-06-08 14:08:09','2010-06-08 14:08:09'),(56,'PS_SEARCH_AJAX','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(57,'PS_TIMEZONE','374','2010-06-08 14:08:09','2010-06-08 14:08:09'),(58,'PS_THEME_V11','0','2010-06-08 14:08:09','2010-06-08 14:08:09'),(59,'PS_CARRIER_DEFAULT','2','2010-06-08 14:08:09','2010-06-08 14:08:09'),(60,'PAYPAL_BUSINESS','paypal@prestashop.com','2010-06-08 14:08:09','2010-06-08 14:08:09'),(61,'PAYPAL_SANDBOX','0','2010-06-08 14:08:09','2010-06-08 14:08:09'),(62,'PAYPAL_CURRENCY','customer','2010-06-08 14:08:09','2010-06-08 14:08:09'),(63,'BANK_WIRE_CURRENCIES','2,1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(64,'CHEQUE_CURRENCIES','2,1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(65,'PRODUCTS_VIEWED_NBR','2','2010-06-08 14:08:09','2010-06-08 14:08:09'),(66,'BLOCK_CATEG_DHTML','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(67,'BLOCK_CATEG_MAX_DEPTH','3','2010-06-08 14:08:09','2010-06-08 14:08:09'),(68,'MANUFACTURER_DISPLAY_FORM','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(69,'MANUFACTURER_DISPLAY_TEXT','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(70,'MANUFACTURER_DISPLAY_TEXT_NB','5','2010-06-08 14:08:09','2010-06-08 14:08:09'),(71,'NEW_PRODUCTS_NBR','5','2010-06-08 14:08:09','2010-06-08 14:08:09'),(72,'STATSHOME_YEAR_FROM','2010','2010-06-08 14:08:09','2010-06-08 14:08:09'),(73,'STATSHOME_MONTH_FROM','06','2010-06-08 14:08:09','2010-06-08 14:08:09'),(74,'STATSHOME_DAY_FROM','08','2010-06-08 14:08:09','2010-06-08 14:08:09'),(75,'STATSHOME_YEAR_TO','2010','2010-06-08 14:08:09','2010-06-08 14:08:09'),(76,'STATSHOME_MONTH_TO','06','2010-06-08 14:08:09','2010-06-08 14:08:09'),(77,'STATSHOME_DAY_TO','08','2010-06-08 14:08:09','2010-06-08 14:08:09'),(78,'PS_TOKEN_ENABLE','1','2010-06-08 14:08:09','2010-06-08 14:08:09'),(79,'PS_STATS_RENDER','graphxmlswfcharts','2010-06-08 14:08:09','2010-06-08 14:08:09'),(80,'PS_STATS_OLD_CONNECT_AUTO_CLEAN','never','2010-06-08 14:08:09','2010-06-08 14:08:09'),(81,'PS_STATS_GRID_RENDER','gridextjs','2010-06-08 14:08:09','2010-06-08 14:08:09'),(82,'BLOCKTAGS_NBR','10','2010-06-08 14:08:09','2010-06-08 14:08:09');
/*!40000 ALTER TABLE `ps_configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_configuration_lang`
--

DROP TABLE IF EXISTS `ps_configuration_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_configuration_lang` (
  `id_configuration` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `value` text,
  `date_upd` datetime default NULL,
  PRIMARY KEY  (`id_configuration`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_configuration_lang`
--

LOCK TABLES `ps_configuration_lang` WRITE;
/*!40000 ALTER TABLE `ps_configuration_lang` DISABLE KEYS */;
INSERT INTO `ps_configuration_lang` VALUES (36,1,'IN','2010-06-08 14:08:09'),(36,2,'FA','2010-06-08 14:08:09'),(38,1,'DE','2010-06-08 14:08:09'),(38,2,'LI','2010-06-08 14:08:09'),(46,1,'a|the|of|on|in|and|to','2010-06-08 14:08:09'),(46,2,'le|les|de|et|en|des|les|une','2010-06-08 14:08:09');
/*!40000 ALTER TABLE `ps_configuration_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_connections`
--

DROP TABLE IF EXISTS `ps_connections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_connections` (
  `id_connections` int(10) unsigned NOT NULL auto_increment,
  `id_guest` int(10) unsigned NOT NULL,
  `id_page` int(10) unsigned NOT NULL,
  `ip_address` varchar(16) default NULL,
  `date_add` datetime NOT NULL,
  `http_referer` varchar(255) default NULL,
  PRIMARY KEY  (`id_connections`),
  KEY `id_guest` (`id_guest`),
  KEY `date_add` (`date_add`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_connections`
--

LOCK TABLES `ps_connections` WRITE;
/*!40000 ALTER TABLE `ps_connections` DISABLE KEYS */;
INSERT INTO `ps_connections` VALUES (1,1,1,'2130706433','2010-06-08 14:08:09','http://www.prestashop.com');
/*!40000 ALTER TABLE `ps_connections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_connections_page`
--

DROP TABLE IF EXISTS `ps_connections_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_connections_page` (
  `id_connections` int(10) unsigned NOT NULL,
  `id_page` int(10) unsigned NOT NULL,
  `time_start` datetime NOT NULL,
  `time_end` datetime default NULL,
  PRIMARY KEY  (`id_connections`,`id_page`,`time_start`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_connections_page`
--

LOCK TABLES `ps_connections_page` WRITE;
/*!40000 ALTER TABLE `ps_connections_page` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_connections_page` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_connections_source`
--

DROP TABLE IF EXISTS `ps_connections_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_connections_source` (
  `id_connections_source` int(10) unsigned NOT NULL auto_increment,
  `id_connections` int(10) unsigned NOT NULL,
  `http_referer` varchar(255) default NULL,
  `request_uri` varchar(255) default NULL,
  `keywords` varchar(255) default NULL,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_connections_source`),
  KEY `connections` (`id_connections`),
  KEY `orderby` (`date_add`),
  KEY `http_referer` (`http_referer`),
  KEY `request_uri` (`request_uri`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_connections_source`
--

LOCK TABLES `ps_connections_source` WRITE;
/*!40000 ALTER TABLE `ps_connections_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_connections_source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_contact`
--

DROP TABLE IF EXISTS `ps_contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_contact` (
  `id_contact` int(10) unsigned NOT NULL auto_increment,
  `email` varchar(128) NOT NULL,
  `position` tinyint(2) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_contact`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_contact`
--

LOCK TABLES `ps_contact` WRITE;
/*!40000 ALTER TABLE `ps_contact` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_contact_lang`
--

DROP TABLE IF EXISTS `ps_contact_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_contact_lang` (
  `id_contact` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  `description` text,
  UNIQUE KEY `contact_lang_index` (`id_contact`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_contact_lang`
--

LOCK TABLES `ps_contact_lang` WRITE;
/*!40000 ALTER TABLE `ps_contact_lang` DISABLE KEYS */;
INSERT INTO `ps_contact_lang` VALUES (1,1,'Webmaster','If a technical problem occurs on this website'),(1,2,'Webmaster','Si un problème technique survient sur le site'),(2,1,'Customer service','For any question about a product, an order'),(2,2,'Service client','Pour toute question ou réclamation sur une commande');
/*!40000 ALTER TABLE `ps_contact_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_country`
--

DROP TABLE IF EXISTS `ps_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_country`
--

LOCK TABLES `ps_country` WRITE;
/*!40000 ALTER TABLE `ps_country` DISABLE KEYS */;
INSERT INTO `ps_country` VALUES (1,1,'DE',1,0),(2,1,'AT',1,0),(3,1,'BE',1,0),(4,2,'CA',1,0),(5,3,'CN',1,0),(6,1,'ES',1,0),(7,1,'FI',1,0),(8,1,'FR',1,0),(9,1,'GR',1,0),(10,1,'IT',1,0),(11,3,'JP',1,0),(12,1,'LU',1,0),(13,1,'NL',1,0),(14,1,'PL',1,0),(15,1,'PT',1,0),(16,1,'CZ',1,0),(17,1,'GB',1,0),(18,1,'SE',1,0),(19,1,'CH',1,0),(20,1,'DK',1,0),(21,2,'US',1,1),(22,3,'HK',1,0),(23,1,'NO',1,0),(24,5,'AU',1,0),(25,3,'SG',1,0),(26,1,'IE',1,0),(27,5,'NZ',1,0),(28,3,'KR',1,0),(29,3,'IL',1,0),(30,4,'ZA',1,0),(31,4,'NG',1,0),(32,4,'CI',1,0),(33,4,'TG',1,0),(34,2,'BO',1,0),(35,4,'MU',1,0),(143,1,'HU',1,0),(36,1,'RO',1,0),(37,1,'SK',1,0),(38,4,'DZ',1,0),(39,2,'AS',1,0),(40,1,'AD',1,0),(41,4,'AO',1,0),(42,2,'AI',1,0),(43,2,'AG',1,0),(44,2,'AR',1,0),(45,3,'AM',1,0),(46,2,'AW',1,0),(47,3,'AZ',1,0),(48,2,'BS',1,0),(49,3,'BH',1,0),(50,3,'BD',1,0),(51,2,'BB',1,0),(52,1,'BY',1,0),(53,2,'BZ',1,0),(54,4,'BJ',1,0),(55,2,'BM',1,0),(56,3,'BT',1,0),(57,4,'BW',1,0),(58,2,'BR',1,0),(59,3,'BN',1,0),(60,4,'BF',1,0),(61,3,'MM',1,0),(62,4,'BI',1,0),(63,3,'KH',1,0),(64,4,'CM',1,0),(65,4,'CV',1,0),(66,4,'CF',1,0),(67,4,'TD',1,0),(68,2,'CL',1,0),(69,2,'CO',1,0),(70,4,'KM',1,0),(71,4,'CD',1,0),(72,4,'CG',1,0),(73,2,'CR',1,0),(74,1,'HR',1,0),(75,2,'CU',1,0),(76,1,'CY',1,0),(77,4,'DJ',1,0),(78,2,'DM',1,0),(79,2,'DO',1,0),(80,3,'TL',1,0),(81,2,'EC',1,0),(82,4,'EG',1,0),(83,2,'SV',1,0),(84,4,'GQ',1,0),(85,4,'ER',1,0),(86,1,'EE',1,0),(87,4,'ET',1,0),(88,2,'FK',1,0),(89,1,'FO',1,0),(90,5,'FJ',1,0),(91,4,'GA',1,0),(92,4,'GM',1,0),(93,3,'GE',1,0),(94,4,'GH',1,0),(95,2,'GD',1,0),(96,1,'GL',1,0),(97,1,'GI',1,0),(98,2,'GP',1,0),(99,2,'GU',1,0),(100,2,'GT',1,0),(101,1,'GG',1,0),(102,4,'GN',1,0),(103,4,'GW',1,0),(104,2,'GY',1,0),(105,2,'HT',1,0),(106,5,'HM',1,0),(107,1,'VA',1,0),(108,2,'HN',1,0),(109,1,'IS',1,0),(110,3,'IN',1,0),(111,3,'ID',1,0),(112,3,'IR',1,0),(113,3,'IQ',1,0),(114,1,'IM',1,0),(115,2,'JM',1,0),(116,1,'JE',1,0),(117,3,'JO',1,0),(118,3,'KZ',1,0),(119,4,'KE',1,0),(120,1,'KI',1,0),(121,3,'KP',1,0),(122,3,'KW',1,0),(123,3,'KG',1,0),(124,3,'LA',1,0),(125,1,'LV',1,0),(126,3,'LB',1,0),(127,4,'LS',1,0),(128,4,'LR',1,0),(129,4,'LY',1,0),(130,1,'LI',1,0),(131,1,'LT',1,0),(132,3,'MO',1,0),(133,1,'MK',1,0),(134,4,'MG',1,0),(135,4,'MW',1,0),(136,3,'MY',1,0),(137,3,'MV',1,0),(138,4,'ML',1,0),(139,1,'MT',1,0),(140,5,'MH',1,0),(141,2,'MQ',1,0),(142,4,'MR',1,0),(144,4,'YT',1,0),(145,2,'MX',1,0),(146,5,'FM',1,0),(147,1,'MD',1,0),(148,1,'MC',1,0),(149,3,'MN',1,0),(150,1,'ME',1,0),(151,2,'MS',1,0),(152,4,'MA',1,0),(153,4,'MZ',1,0),(154,4,'NA',1,0),(155,5,'NR',1,0),(156,3,'NP',1,0),(157,2,'AN',1,0),(158,5,'NC',1,0),(159,2,'NI',1,0),(160,4,'NE',1,0),(161,5,'NU',1,0),(162,5,'NF',1,0),(163,5,'MP',1,0),(164,3,'OM',1,0),(165,3,'PK',1,0),(166,5,'PW',1,0),(167,3,'PS',1,0),(168,2,'PA',1,0),(169,5,'PG',1,0),(170,2,'PY',1,0),(171,2,'PE',1,0),(172,3,'PH',1,0),(173,5,'PN',1,0),(174,2,'PR',1,0),(175,3,'QA',1,0),(176,4,'RE',1,0),(177,1,'RU',1,0),(178,4,'RW',1,0),(179,2,'BL',1,0),(180,2,'KN',1,0),(181,2,'LC',1,0),(182,2,'MF',1,0),(183,2,'PM',1,0),(184,2,'VC',1,0),(185,5,'WS',1,0),(186,1,'SM',1,0),(187,4,'ST',1,0),(188,3,'SA',1,0),(189,4,'SN',1,0),(190,1,'RS',1,0),(191,4,'SC',1,0),(192,4,'SL',1,0),(193,1,'SI',1,0),(194,5,'SB',1,0),(195,4,'SO',1,0),(196,2,'GS',1,0),(197,3,'LK',1,0),(198,4,'SD',1,0),(199,2,'SR',1,0),(200,1,'SJ',1,0),(201,4,'SZ',1,0),(202,3,'SY',1,0),(203,3,'TW',1,0),(204,3,'TJ',1,0),(205,4,'TZ',1,0),(206,3,'TH',1,0),(207,5,'TK',1,0),(208,5,'TO',1,0),(209,2,'TT',1,0),(210,4,'TN',1,0),(211,1,'TR',1,0),(212,3,'TM',1,0),(213,2,'TC',1,0),(214,5,'TV',1,0),(215,4,'UG',1,0),(216,1,'UA',1,0),(217,3,'AE',1,0),(218,2,'UY',1,0),(219,3,'UZ',1,0),(220,5,'VU',1,0),(221,2,'VE',1,0),(222,3,'VN',1,0),(223,2,'VG',1,0),(224,2,'VI',1,0),(225,5,'WF',1,0),(226,4,'EH',1,0),(227,3,'YE',1,0),(228,4,'ZM',1,0),(229,4,'ZW',1,0),(230,1,'AL',1,0),(231,3,'AF',1,0),(232,5,'AQ',1,0),(233,1,'BA',1,0),(234,5,'BV',1,0),(235,5,'IO',1,0),(236,1,'BG',1,0),(237,2,'KY',1,0),(238,3,'CX',1,0),(239,3,'CC',1,0),(240,5,'CK',1,0),(241,2,'GF',1,0),(242,5,'PF',1,0),(243,5,'TF',1,0),(244,1,'AX',1,0);
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
INSERT INTO `ps_country_lang` VALUES (1,1,'Germany'),(1,2,'Allemagne'),(2,1,'Austria'),(2,2,'Autriche'),(3,1,'Belgium'),(3,2,'Belgique'),(4,1,'Canada'),(4,2,'Canada'),(5,1,'China'),(5,2,'Chine'),(6,1,'Spain'),(6,2,'Espagne'),(7,1,'Finland'),(7,2,'Finlande'),(8,1,'France'),(8,2,'France'),(9,1,'Greece'),(9,2,'Grèce'),(10,1,'Italy'),(10,2,'Italie'),(11,1,'Japan'),(11,2,'Japon'),(12,1,'Luxemburg'),(12,2,'Luxembourg'),(13,1,'Netherlands'),(13,2,'Pays-bas'),(14,1,'Poland'),(14,2,'Pologne'),(15,1,'Portugal'),(15,2,'Portugal'),(16,1,'Czech Republic'),(16,2,'République Tchèque'),(17,1,'United Kingdom'),(17,2,'Royaume-Uni'),(18,1,'Sweden'),(18,2,'Suède'),(19,1,'Switzerland'),(19,2,'Suisse'),(20,1,'Denmark'),(20,2,'Danemark'),(21,1,'USA'),(21,2,'USA'),(22,1,'HongKong'),(22,2,'Hong-Kong'),(23,1,'Norway'),(23,2,'Norvège'),(24,1,'Australia'),(24,2,'Australie'),(25,1,'Singapore'),(25,2,'Singapour'),(26,1,'Ireland'),(26,2,'Eire'),(27,1,'New Zealand'),(27,2,'Nouvelle-Zélande'),(28,1,'South Korea'),(28,2,'Corée du Sud'),(29,1,'Israel'),(29,2,'Israël'),(30,1,'South Africa'),(30,2,'Afrique du Sud'),(31,1,'Nigeria'),(31,2,'Nigeria'),(32,1,'Ivory Coast'),(32,2,'Côte d\'Ivoire'),(33,1,'Togo'),(33,2,'Togo'),(34,1,'Bolivia'),(34,2,'Bolivie'),(35,1,'Mauritius'),(35,2,'Ile Maurice'),(143,1,'Hungary'),(143,2,'Hongrie'),(36,1,'Romania'),(36,2,'Roumanie'),(37,1,'Slovakia'),(37,2,'Slovaquie'),(38,1,'Algeria'),(38,2,'Algérie'),(39,1,'American Samoa'),(39,2,'Samoa Américaines'),(40,1,'Andorra'),(40,2,'Andorre'),(41,1,'Angola'),(41,2,'Angola'),(42,1,'Anguilla'),(42,2,'Anguilla'),(43,1,'Antigua and Barbuda'),(43,2,'Antigua et Barbuda'),(44,1,'Argentina'),(44,2,'Argentine'),(45,1,'Armenia'),(45,2,'Arménie'),(46,1,'Aruba'),(46,2,'Aruba'),(47,1,'Azerbaijan'),(47,2,'Azerbaïdjan'),(48,1,'Bahamas'),(48,2,'Bahamas'),(49,1,'Bahrain'),(49,2,'Bahreïn'),(50,1,'Bangladesh'),(50,2,'Bangladesh'),(51,1,'Barbados'),(51,2,'Barbade'),(52,1,'Belarus'),(52,2,'Bélarus'),(53,1,'Belize'),(53,2,'Belize'),(54,1,'Benin'),(54,2,'Bénin'),(55,1,'Bermuda'),(55,2,'Bermudes'),(56,1,'Bhutan'),(56,2,'Bhoutan'),(57,1,'Botswana'),(57,2,'Botswana'),(58,1,'Brazil'),(58,2,'Brésil'),(59,1,'Brunei'),(59,2,'Brunéi Darussalam'),(60,1,'Burkina Faso'),(60,2,'Burkina Faso'),(61,1,'Burma (Myanmar)'),(61,2,'Burma (Myanmar)'),(62,1,'Burundi'),(62,2,'Burundi'),(63,1,'Cambodia'),(63,2,'Cambodge'),(64,1,'Cameroon'),(64,2,'Cameroun'),(65,1,'Cape Verde'),(65,2,'Cap-Vert'),(66,1,'Central African Republic'),(66,2,'Centrafricaine, République'),(67,1,'Chad'),(67,2,'Tchad'),(68,1,'Chile'),(68,2,'Chili'),(69,1,'Colombia'),(69,2,'Colombie'),(70,1,'Comoros'),(70,2,'Comores'),(71,1,'Congo, Dem. Republic'),(71,2,'Congo, Rép. Dém.'),(72,1,'Congo, Republic'),(72,2,'Congo, Rép.'),(73,1,'Costa Rica'),(73,2,'Costa Rica'),(74,1,'Croatia'),(74,2,'Croatie'),(75,1,'Cuba'),(75,2,'Cuba'),(76,1,'Cyprus'),(76,2,'Chypre'),(77,1,'Djibouti'),(77,2,'Djibouti'),(78,1,'Dominica'),(78,2,'Dominica'),(79,1,'Dominican Republic'),(79,2,'République Dominicaine'),(80,1,'East Timor'),(80,2,'Timor oriental'),(81,1,'Ecuador'),(81,2,'Équateur'),(82,1,'Egypt'),(82,2,'Égypte'),(83,1,'El Salvador'),(83,2,'El Salvador'),(84,1,'Equatorial Guinea'),(84,2,'Guinée Équatoriale'),(85,1,'Eritrea'),(85,2,'Érythrée'),(86,1,'Estonia'),(86,2,'Estonie'),(87,1,'Ethiopia'),(87,2,'Éthiopie'),(88,1,'Falkland Islands'),(88,2,'Falkland, Îles'),(89,1,'Faroe Islands'),(89,2,'Féroé, Îles'),(90,1,'Fiji'),(90,2,'Fidji'),(91,1,'Gabon'),(91,2,'Gabon'),(92,1,'Gambia'),(92,2,'Gambie'),(93,1,'Georgia'),(93,2,'Géorgie'),(94,1,'Ghana'),(94,2,'Ghana'),(95,1,'Grenada'),(95,2,'Grenade'),(96,1,'Greenland'),(96,2,'Groenland'),(97,1,'Gibraltar'),(97,2,'Gibraltar'),(98,1,'Guadeloupe'),(98,2,'Guadeloupe'),(99,1,'Guam'),(99,2,'Guam'),(100,1,'Guatemala'),(100,2,'Guatemala'),(101,1,'Guernsey'),(101,2,'Guernesey'),(102,1,'Guinea'),(102,2,'Guinée'),(103,1,'Guinea-Bissau'),(103,2,'Guinée-Bissau'),(104,1,'Guyana'),(104,2,'Guyana'),(105,1,'Haiti'),(105,2,'Haîti'),(106,1,'Heard Island and McDonald Islands'),(106,2,'Heard, Île et Mcdonald, Îles'),(107,1,'Vatican City State'),(107,2,'Saint-Siege (État de la Cité du Vatican)'),(108,1,'Honduras'),(108,2,'Honduras'),(109,1,'Iceland'),(109,2,'Islande'),(110,1,'India'),(110,2,'Indie'),(111,1,'Indonesia'),(111,2,'Indonésie'),(112,1,'Iran'),(112,2,'Iran'),(113,1,'Iraq'),(113,2,'Iraq'),(114,1,'Isle of Man'),(114,2,'Île de Man'),(115,1,'Jamaica'),(115,2,'Jamaique'),(116,1,'Jersey'),(116,2,'Jersey'),(117,1,'Jordan'),(117,2,'Jordanie'),(118,1,'Kazakhstan'),(118,2,'Kazakhstan'),(119,1,'Kenya'),(119,2,'Kenya'),(120,1,'Kiribati'),(120,2,'Kiribati'),(121,1,'Korea, Dem. Republic of'),(121,2,'Corée, Rép. Populaire Dém. de'),(122,1,'Kuwait'),(122,2,'Koweït'),(123,1,'Kyrgyzstan'),(123,2,'Kirghizistan'),(124,1,'Laos'),(124,2,'Laos'),(125,1,'Latvia'),(125,2,'Lettonie'),(126,1,'Lebanon'),(126,2,'Liban'),(127,1,'Lesotho'),(127,2,'Lesotho'),(128,1,'Liberia'),(128,2,'Libéria'),(129,1,'Libya'),(129,2,'Libyenne, Jamahiriya Arabe'),(130,1,'Liechtenstein'),(130,2,'Liechtenstein'),(131,1,'Lithuania'),(131,2,'Lituanie'),(132,1,'Macau'),(132,2,'Macao'),(133,1,'Macedonia'),(133,2,'Macédoine'),(134,1,'Madagascar'),(134,2,'Madagascar'),(135,1,'Malawi'),(135,2,'Malawi'),(136,1,'Malaysia'),(136,2,'Malaisie'),(137,1,'Maldives'),(137,2,'Maldives'),(138,1,'Mali'),(138,2,'Mali'),(139,1,'Malta'),(139,2,'Malte'),(140,1,'Marshall Islands'),(140,2,'Marshall, Îles'),(141,1,'Martinique'),(141,2,'Martinique'),(142,1,'Mauritania'),(142,2,'Mauritanie'),(144,1,'Mayotte'),(144,2,'Mayotte'),(145,1,'Mexico'),(145,2,'Mexique'),(146,1,'Micronesia'),(146,2,'Micronésie'),(147,1,'Moldova'),(147,2,'Moldova'),(148,1,'Monaco'),(148,2,'Monaco'),(149,1,'Mongolia'),(149,2,'Mongolie'),(150,1,'Montenegro'),(150,2,'Monténégro'),(151,1,'Montserrat'),(151,2,'Montserrat'),(152,1,'Morocco'),(152,2,'Maroc'),(153,1,'Mozambique'),(153,2,'Mozambique'),(154,1,'Namibia'),(154,2,'Namibie'),(155,1,'Nauru'),(155,2,'Nauru'),(156,1,'Nepal'),(156,2,'Népal'),(157,1,'Netherlands Antilles'),(157,2,'Antilles Néerlandaises'),(158,1,'New Caledonia'),(158,2,'Nouvelle-Calédonie'),(159,1,'Nicaragua'),(159,2,'Nicaragua'),(160,1,'Niger'),(160,2,'Niger'),(161,1,'Niue'),(161,2,'Niué'),(162,1,'Norfolk Island'),(162,2,'Norfolk, Île'),(163,1,'Northern Mariana Islands'),(163,2,'Mariannes du Nord, Îles'),(164,1,'Oman'),(164,2,'Oman'),(165,1,'Pakistan'),(165,2,'Pakistan'),(166,1,'Palau'),(166,2,'Palaos'),(167,1,'Palestinian Territories'),(167,2,'Palestinien Occupé, Territoire'),(168,1,'Panama'),(168,2,'Panama'),(169,1,'Papua New Guinea'),(169,2,'Papouasie-Nouvelle-Guinée'),(170,1,'Paraguay'),(170,2,'Paraguay'),(171,1,'Peru'),(171,2,'Pérou'),(172,1,'Philippines'),(172,2,'Philippines'),(173,1,'Pitcairn'),(173,2,'Pitcairn'),(174,1,'Puerto Rico'),(174,2,'Porto Rico'),(175,1,'Qatar'),(175,2,'Qatar'),(176,1,'Réunion'),(176,2,'Réunion'),(177,1,'Russian Federation'),(177,2,'Russie, Fédération de'),(178,1,'Rwanda'),(178,2,'Rwanda'),(179,1,'Saint Barthélemy'),(179,2,'Saint-Barthélemy'),(180,1,'Saint Kitts and Nevis'),(180,2,'Saint-Kitts-et-Nevis'),(181,1,'Saint Lucia'),(181,2,'Sainte-Lucie'),(182,1,'Saint Martin'),(182,2,'Saint-Martin'),(183,1,'Saint Pierre and Miquelon'),(183,2,'Saint-Pierre-et-Miquelon'),(184,1,'Saint Vincent and the Grenadines'),(184,2,'Saint-Vincent-et-Les Grenadines'),(185,1,'Samoa'),(185,2,'Samoa'),(186,1,'San Marino'),(186,2,'Saint-Marin'),(187,1,'São Tomé and Príncipe'),(187,2,'Sao Tomé-et-Principe'),(188,1,'Saudi Arabia'),(188,2,'Arabie Saoudite'),(189,1,'Senegal'),(189,2,'Sénégal'),(190,1,'Serbia'),(190,2,'Serbie'),(191,1,'Seychelles'),(191,2,'Seychelles'),(192,1,'Sierra Leone'),(192,2,'Sierra Leone'),(193,1,'Slovenia'),(193,2,'Slovénie'),(194,1,'Solomon Islands'),(194,2,'Salomon, Îles'),(195,1,'Somalia'),(195,2,'Somalie'),(196,1,'South Georgia and the South Sandwich Islands'),(196,2,'Géorgie du Sud et les Îles Sandwich du Sud'),(197,1,'Sri Lanka'),(197,2,'Sri Lanka'),(198,1,'Sudan'),(198,2,'Soudan'),(199,1,'Suriname'),(199,2,'Suriname'),(200,1,'Svalbard and Jan Mayen'),(200,2,'Svalbard et Île Jan Mayen'),(201,1,'Swaziland'),(201,2,'Swaziland'),(202,1,'Syria'),(202,2,'Syrienne'),(203,1,'Taiwan'),(203,2,'Taïwan'),(204,1,'Tajikistan'),(204,2,'Tadjikistan'),(205,1,'Tanzania'),(205,2,'Tanzanie'),(206,1,'Thailand'),(206,2,'Thaïlande'),(207,1,'Tokelau'),(207,2,'Tokelau'),(208,1,'Tonga'),(208,2,'Tonga'),(209,1,'Trinidad and Tobago'),(209,2,'Trinité-et-Tobago'),(210,1,'Tunisia'),(210,2,'Tunisie'),(211,1,'Turkey'),(211,2,'Turquie'),(212,1,'Turkmenistan'),(212,2,'Turkménistan'),(213,1,'Turks and Caicos Islands'),(213,2,'Turks et Caiques, Îles'),(214,1,'Tuvalu'),(214,2,'Tuvalu'),(215,1,'Uganda'),(215,2,'Ouganda'),(216,1,'Ukraine'),(216,2,'Ukraine'),(217,1,'United Arab Emirates'),(217,2,'Émirats Arabes Unis'),(218,1,'Uruguay'),(218,2,'Uruguay'),(219,1,'Uzbekistan'),(219,2,'Ouzbékistan'),(220,1,'Vanuatu'),(220,2,'Vanuatu'),(221,1,'Venezuela'),(221,2,'Venezuela'),(222,1,'Vietnam'),(222,2,'Vietnam'),(223,1,'Virgin Islands (British)'),(223,2,'Îles Vierges Britanniques'),(224,1,'Virgin Islands (U.S.)'),(224,2,'Îles Vierges des États-Unis'),(225,1,'Wallis and Futuna'),(225,2,'Wallis et Futuna'),(226,1,'Western Sahara'),(226,2,'Sahara Occidental'),(227,1,'Yemen'),(227,2,'Yémen'),(228,1,'Zambia'),(228,2,'Zambie'),(229,1,'Zimbabwe'),(229,2,'Zimbabwe'),(230,1,'Albania'),(230,2,'Albanie'),(231,1,'Afghanistan'),(231,2,'Afghanistan'),(232,1,'Antarctica'),(232,2,'Antarctique'),(233,1,'Bosnia and Herzegovina'),(233,2,'Bosnie-Herzégovine'),(234,1,'Bouvet Island'),(234,2,'Bouvet, Île'),(235,1,'British Indian Ocean Territory'),(235,2,'Océan Indien, Territoire Britannique de L\''),(236,1,'Bulgaria'),(236,2,'Bulgarie'),(237,1,'Cayman Islands'),(237,2,'Caïmans, Îles'),(238,1,'Christmas Island'),(238,2,'Christmas, Île'),(239,1,'Cocos (Keeling) Islands'),(239,2,'Cocos (Keeling), Îles'),(240,1,'Cook Islands'),(240,2,'Cook, Îles'),(241,1,'French Guiana'),(241,2,'Guyane Française'),(242,1,'French Polynesia'),(242,2,'Polynésie Française'),(243,1,'French Southern Territories'),(243,2,'Terres Australes Françaises'),(244,1,'Åland Islands'),(244,2,'Åland, Îles');
/*!40000 ALTER TABLE `ps_country_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_currency`
--

DROP TABLE IF EXISTS `ps_currency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_currency`
--

LOCK TABLES `ps_currency` WRITE;
/*!40000 ALTER TABLE `ps_currency` DISABLE KEYS */;
INSERT INTO `ps_currency` VALUES (1,'Euro','EUR','€',1,2,1,'1.000000',0),(2,'Dollar','USD','$',0,1,1,'1.470000',0),(3,'Pound','GBP','£',0,1,1,'0.800000',0);
/*!40000 ALTER TABLE `ps_currency` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_customer`
--

DROP TABLE IF EXISTS `ps_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_customer`
--

LOCK TABLES `ps_customer` WRITE;
/*!40000 ALTER TABLE `ps_customer` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_customer_group`
--

DROP TABLE IF EXISTS `ps_customer_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_customer_group` (
  `id_customer` int(10) unsigned NOT NULL,
  `id_group` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_customer`,`id_group`),
  KEY `customer_login` (`id_group`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_customer_group`
--

LOCK TABLES `ps_customer_group` WRITE;
/*!40000 ALTER TABLE `ps_customer_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_customer_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_customization`
--

DROP TABLE IF EXISTS `ps_customization`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_customization` (
  `id_customization` int(10) unsigned NOT NULL auto_increment,
  `id_product_attribute` int(10) NOT NULL default '0',
  `id_cart` int(10) NOT NULL,
  `id_product` int(10) NOT NULL,
  `quantity` int(10) NOT NULL,
  `quantity_refunded` int(11) NOT NULL default '0',
  `quantity_returned` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id_customization`,`id_cart`,`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_customization`
--

LOCK TABLES `ps_customization` WRITE;
/*!40000 ALTER TABLE `ps_customization` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_customization` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_customization_field`
--

DROP TABLE IF EXISTS `ps_customization_field`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_customization_field` (
  `id_customization_field` int(10) unsigned NOT NULL auto_increment,
  `id_product` int(10) NOT NULL,
  `type` tinyint(1) NOT NULL,
  `required` tinyint(1) NOT NULL,
  PRIMARY KEY  (`id_customization_field`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_customization_field`
--

LOCK TABLES `ps_customization_field` WRITE;
/*!40000 ALTER TABLE `ps_customization_field` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_customization_field` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_customization_field_lang`
--

DROP TABLE IF EXISTS `ps_customization_field_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_customization_field_lang` (
  `id_customization_field` int(10) NOT NULL,
  `id_lang` int(10) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY  (`id_customization_field`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_customization_field_lang`
--

LOCK TABLES `ps_customization_field_lang` WRITE;
/*!40000 ALTER TABLE `ps_customization_field_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_customization_field_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_customized_data`
--

DROP TABLE IF EXISTS `ps_customized_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_customized_data` (
  `id_customization` int(10) NOT NULL,
  `type` tinyint(1) NOT NULL,
  `index` int(3) NOT NULL,
  `value` varchar(255) NOT NULL,
  PRIMARY KEY  (`id_customization`,`type`,`index`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_customized_data`
--

LOCK TABLES `ps_customized_data` WRITE;
/*!40000 ALTER TABLE `ps_customized_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_customized_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_date_range`
--

DROP TABLE IF EXISTS `ps_date_range`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_date_range` (
  `id_date_range` int(10) unsigned NOT NULL auto_increment,
  `time_start` datetime NOT NULL,
  `time_end` datetime NOT NULL,
  PRIMARY KEY  (`id_date_range`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_date_range`
--

LOCK TABLES `ps_date_range` WRITE;
/*!40000 ALTER TABLE `ps_date_range` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_date_range` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_delivery`
--

DROP TABLE IF EXISTS `ps_delivery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_delivery` (
  `id_delivery` int(10) unsigned NOT NULL auto_increment,
  `id_carrier` int(10) unsigned NOT NULL,
  `id_range_price` int(10) unsigned default NULL,
  `id_range_weight` int(10) unsigned default NULL,
  `id_zone` int(10) unsigned NOT NULL,
  `price` decimal(10,2) NOT NULL,
  PRIMARY KEY  (`id_delivery`),
  KEY `id_zone` (`id_zone`),
  KEY `id_carrier` (`id_carrier`,`id_zone`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_delivery`
--

LOCK TABLES `ps_delivery` WRITE;
/*!40000 ALTER TABLE `ps_delivery` DISABLE KEYS */;
INSERT INTO `ps_delivery` VALUES (1,2,NULL,1,1,'5.00'),(2,2,NULL,1,2,'5.00'),(4,2,1,NULL,1,'5.00'),(5,2,1,NULL,2,'5.00');
/*!40000 ALTER TABLE `ps_delivery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_discount`
--

DROP TABLE IF EXISTS `ps_discount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_discount` (
  `id_discount` int(10) unsigned NOT NULL auto_increment,
  `id_discount_type` int(10) unsigned NOT NULL,
  `id_customer` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  `value` decimal(10,2) NOT NULL default '0.00',
  `quantity` int(10) unsigned NOT NULL default '0',
  `quantity_per_user` int(10) unsigned NOT NULL default '1',
  `cumulable` tinyint(1) unsigned NOT NULL default '0',
  `cumulable_reduction` tinyint(1) unsigned NOT NULL default '0',
  `date_from` datetime NOT NULL,
  `date_to` datetime NOT NULL,
  `minimal` decimal(10,2) default NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_discount`),
  KEY `discount_name` (`name`),
  KEY `discount_customer` (`id_customer`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_discount`
--

LOCK TABLES `ps_discount` WRITE;
/*!40000 ALTER TABLE `ps_discount` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_discount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_discount_category`
--

DROP TABLE IF EXISTS `ps_discount_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_discount_category` (
  `id_category` int(11) NOT NULL,
  `id_discount` int(11) NOT NULL,
  PRIMARY KEY  (`id_category`,`id_discount`),
  KEY `discount` (`id_discount`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_discount_category`
--

LOCK TABLES `ps_discount_category` WRITE;
/*!40000 ALTER TABLE `ps_discount_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_discount_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_discount_lang`
--

DROP TABLE IF EXISTS `ps_discount_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_discount_lang` (
  `id_discount` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `description` text,
  PRIMARY KEY  (`id_discount`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_discount_lang`
--

LOCK TABLES `ps_discount_lang` WRITE;
/*!40000 ALTER TABLE `ps_discount_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_discount_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_discount_quantity`
--

DROP TABLE IF EXISTS `ps_discount_quantity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_discount_quantity` (
  `id_discount_quantity` int(10) unsigned NOT NULL auto_increment,
  `id_discount_type` int(10) unsigned NOT NULL,
  `id_product` int(10) unsigned NOT NULL,
  `id_product_attribute` int(10) unsigned default NULL,
  `quantity` int(10) unsigned NOT NULL,
  `value` decimal(10,2) unsigned NOT NULL,
  PRIMARY KEY  (`id_discount_quantity`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_discount_quantity`
--

LOCK TABLES `ps_discount_quantity` WRITE;
/*!40000 ALTER TABLE `ps_discount_quantity` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_discount_quantity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_discount_type`
--

DROP TABLE IF EXISTS `ps_discount_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_discount_type` (
  `id_discount_type` int(10) unsigned NOT NULL auto_increment,
  PRIMARY KEY  (`id_discount_type`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_discount_type`
--

LOCK TABLES `ps_discount_type` WRITE;
/*!40000 ALTER TABLE `ps_discount_type` DISABLE KEYS */;
INSERT INTO `ps_discount_type` VALUES (1),(2),(3);
/*!40000 ALTER TABLE `ps_discount_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_discount_type_lang`
--

DROP TABLE IF EXISTS `ps_discount_type_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_discount_type_lang` (
  `id_discount_type` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY  (`id_discount_type`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_discount_type_lang`
--

LOCK TABLES `ps_discount_type_lang` WRITE;
/*!40000 ALTER TABLE `ps_discount_type_lang` DISABLE KEYS */;
INSERT INTO `ps_discount_type_lang` VALUES (1,1,'Discount on order (%)'),(2,1,'Discount on order (amount)'),(3,1,'Free shipping'),(1,2,'Réduction sur la commande (%)'),(2,2,'Réduction sur la commande (montant)'),(3,2,'Frais de port gratuits');
/*!40000 ALTER TABLE `ps_discount_type_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_employee`
--

DROP TABLE IF EXISTS `ps_employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_employee` (
  `id_employee` int(10) unsigned NOT NULL auto_increment,
  `id_profile` int(10) unsigned NOT NULL,
  `lastname` varchar(32) NOT NULL,
  `firstname` varchar(32) NOT NULL,
  `email` varchar(128) NOT NULL,
  `passwd` varchar(32) NOT NULL,
  `last_passwd_gen` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `stats_date_from` date default NULL,
  `stats_date_to` date default NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_employee`),
  KEY `employee_login` (`email`,`passwd`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_employee`
--

LOCK TABLES `ps_employee` WRITE;
/*!40000 ALTER TABLE `ps_employee` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_employee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_feature`
--

DROP TABLE IF EXISTS `ps_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_feature` (
  `id_feature` int(10) unsigned NOT NULL auto_increment,
  PRIMARY KEY  (`id_feature`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_feature`
--

LOCK TABLES `ps_feature` WRITE;
/*!40000 ALTER TABLE `ps_feature` DISABLE KEYS */;
INSERT INTO `ps_feature` VALUES (1),(2),(3),(4),(5);
/*!40000 ALTER TABLE `ps_feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_feature_lang`
--

DROP TABLE IF EXISTS `ps_feature_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_feature_lang` (
  `id_feature` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(128) default NULL,
  PRIMARY KEY  (`id_feature`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_feature_lang`
--

LOCK TABLES `ps_feature_lang` WRITE;
/*!40000 ALTER TABLE `ps_feature_lang` DISABLE KEYS */;
INSERT INTO `ps_feature_lang` VALUES (1,1,'Height'),(1,2,'Hauteur'),(2,1,'Width'),(2,2,'Largeur'),(3,1,'Depth'),(3,2,'Profondeur'),(4,1,'Weight'),(4,2,'Poids'),(5,1,'Headphone'),(5,2,'Prise casque');
/*!40000 ALTER TABLE `ps_feature_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_feature_product`
--

DROP TABLE IF EXISTS `ps_feature_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_feature_product` (
  `id_feature` int(10) unsigned NOT NULL,
  `id_product` int(10) unsigned NOT NULL,
  `id_feature_value` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_feature`,`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_feature_product`
--

LOCK TABLES `ps_feature_product` WRITE;
/*!40000 ALTER TABLE `ps_feature_product` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_feature_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_feature_value`
--

DROP TABLE IF EXISTS `ps_feature_value`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_feature_value` (
  `id_feature_value` int(10) unsigned NOT NULL auto_increment,
  `id_feature` int(10) unsigned NOT NULL,
  `custom` tinyint(3) unsigned default NULL,
  PRIMARY KEY  (`id_feature_value`),
  KEY `feature` (`id_feature`)
) ENGINE=MyISAM AUTO_INCREMENT=27 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_feature_value`
--

LOCK TABLES `ps_feature_value` WRITE;
/*!40000 ALTER TABLE `ps_feature_value` DISABLE KEYS */;
INSERT INTO `ps_feature_value` VALUES (11,1,1),(15,1,1),(12,2,1),(16,2,1),(14,3,1),(18,3,1),(13,4,1),(17,4,1),(26,3,1),(25,4,1),(24,2,1),(23,1,1),(9,5,NULL),(10,5,NULL);
/*!40000 ALTER TABLE `ps_feature_value` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_feature_value_lang`
--

DROP TABLE IF EXISTS `ps_feature_value_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_feature_value_lang` (
  `id_feature_value` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `value` varchar(255) default NULL,
  PRIMARY KEY  (`id_feature_value`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_feature_value_lang`
--

LOCK TABLES `ps_feature_value_lang` WRITE;
/*!40000 ALTER TABLE `ps_feature_value_lang` DISABLE KEYS */;
INSERT INTO `ps_feature_value_lang` VALUES (13,1,'49.2 grams'),(13,2,'49,2 grammes'),(12,2,'52,3 mm'),(12,1,'52.3 mm'),(11,2,'69,8 mm'),(11,1,'69.8 mm'),(17,2,'15,5 g'),(17,1,'15.5 g'),(16,2,'41,2 mm'),(16,1,'41.2 mm'),(15,2,'27,3 mm'),(15,1,'27.3 mm'),(9,1,'Jack stereo'),(9,2,'Jack stéréo'),(10,1,'Mini-jack stereo'),(10,2,'Mini-jack stéréo'),(14,1,'6,5 mm'),(14,2,'6,5 mm'),(18,1,'10,5 mm (clip compris)'),(18,2,'10,5 mm (clip compris)'),(26,2,'8mm'),(26,1,'8mm'),(25,2,'120g'),(25,1,'120g'),(24,2,'70mm'),(24,1,'70mm'),(23,2,'110mm'),(23,1,'110mm');
/*!40000 ALTER TABLE `ps_feature_value_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_group`
--

DROP TABLE IF EXISTS `ps_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_group` (
  `id_group` int(10) unsigned NOT NULL auto_increment,
  `reduction` decimal(10,2) NOT NULL default '0.00',
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_group`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_group`
--

LOCK TABLES `ps_group` WRITE;
/*!40000 ALTER TABLE `ps_group` DISABLE KEYS */;
INSERT INTO `ps_group` VALUES (1,'0.00','2010-06-08 14:08:09','2010-06-08 14:08:09');
/*!40000 ALTER TABLE `ps_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_group_lang`
--

DROP TABLE IF EXISTS `ps_group_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_group_lang` (
  `id_group` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  UNIQUE KEY `attribute_lang_index` (`id_group`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_group_lang`
--

LOCK TABLES `ps_group_lang` WRITE;
/*!40000 ALTER TABLE `ps_group_lang` DISABLE KEYS */;
INSERT INTO `ps_group_lang` VALUES (1,1,'Default'),(1,2,'Défaut');
/*!40000 ALTER TABLE `ps_group_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_guest`
--

DROP TABLE IF EXISTS `ps_guest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_guest` (
  `id_guest` int(10) unsigned NOT NULL auto_increment,
  `id_operating_system` int(10) unsigned default NULL,
  `id_web_browser` int(10) unsigned default NULL,
  `id_customer` int(10) unsigned default NULL,
  `javascript` tinyint(1) default '0',
  `screen_resolution_x` smallint(5) unsigned default NULL,
  `screen_resolution_y` smallint(5) unsigned default NULL,
  `screen_color` tinyint(3) unsigned default NULL,
  `sun_java` tinyint(1) default NULL,
  `adobe_flash` tinyint(1) default NULL,
  `adobe_director` tinyint(1) default NULL,
  `apple_quicktime` tinyint(1) default NULL,
  `real_player` tinyint(1) default NULL,
  `windows_media` tinyint(1) default NULL,
  `accept_language` varchar(8) default NULL,
  PRIMARY KEY  (`id_guest`),
  KEY `id_customer` (`id_customer`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_guest`
--

LOCK TABLES `ps_guest` WRITE;
/*!40000 ALTER TABLE `ps_guest` DISABLE KEYS */;
INSERT INTO `ps_guest` VALUES (1,1,3,1,1,1680,1050,32,1,1,0,1,1,0,'en-us');
/*!40000 ALTER TABLE `ps_guest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_hook`
--

DROP TABLE IF EXISTS `ps_hook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_hook` (
  `id_hook` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `title` varchar(64) NOT NULL,
  `description` text,
  `position` tinyint(1) NOT NULL default '1',
  PRIMARY KEY  (`id_hook`),
  UNIQUE KEY `hook_name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=50 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_hook`
--

LOCK TABLES `ps_hook` WRITE;
/*!40000 ALTER TABLE `ps_hook` DISABLE KEYS */;
INSERT INTO `ps_hook` VALUES (1,'payment','Payment',NULL,1),(2,'newOrder','New orders',NULL,0),(3,'paymentConfirm','Payment confirmation',NULL,0),(4,'paymentReturn','Payment return',NULL,0),(5,'updateQuantity','Quantity update','Quantity is updated only when the customer effectively <b>place</b> his order.',0),(6,'rightColumn','Right column blocks',NULL,1),(7,'leftColumn','Left column blocks',NULL,1),(8,'home','Homepage content',NULL,1),(9,'header','Header of pages','A hook which allow you to do things in the header of each pages',1),(10,'cart','Cart creation and update',NULL,0),(11,'authentication','Successful customer authentication',NULL,0),(12,'addproduct','Product creation',NULL,0),(13,'updateproduct','Product Update',NULL,0),(14,'top','Top of pages','A hook which allow you to do things a the top of each pages.',1),(15,'extraRight','Extra actions on the product page (right column).',NULL,0),(16,'deleteproduct','Product deletion','This hook is called when a product is deleted',0),(17,'productfooter','Product footer','Add new blocks under the product description',1),(18,'invoice','Invoice','Add blocks to invoice (order)',1),(19,'updateOrderStatus','Order\'s status update event','Launch modules when the order\'s status of an order change.',0),(20,'adminOrder','Display in Back-Office, tab AdminOrder','Launch modules when the tab AdminOrder is displayed on back-office.',0),(21,'footer','Footer','Add block in footer',1),(22,'PDFInvoice','PDF Invoice','Allow the display of extra informations into the PDF invoice',0),(23,'adminCustomers','Display in Back-Office, tab AdminCustomers','Launch modules when the tab AdminCustomers is displayed on back-office.',0),(24,'orderConfirmation','Order confirmation page','Called on order confirmation page',0),(25,'createAccount','Successful customer create account','Called when new customer create account successfuled',0),(26,'customerAccount','Customer account page display in front office','Display on page account of the customer',1),(27,'orderSlip','Called when a order slip is created','Called when a quantity of one product change in an order.',0),(28,'productTab','Tabs on product page','Called on order product page tabs',0),(29,'productTabContent','Content of tabs on product page','Called on order product page tabs',0),(30,'shoppingCart','Shopping cart footer','Display some specific informations on the shopping cart page',0),(31,'createAccountForm','Customer account creation form','Display some information on the form to create a customer account',1),(32,'AdminStatsModules','Stats - Modules',NULL,1),(33,'GraphEngine','Graph Engines',NULL,0),(34,'orderReturn','Product returned',NULL,0),(35,'productActions','Product actions','Put new action buttons on product page',1),(36,'backOfficeHome','Administration panel homepage',NULL,1),(37,'GridEngine','Grid Engines',NULL,0),(38,'watermark','Watermark',NULL,0),(39,'cancelProduct','Product cancelled','This hook is called when you cancel a product in an order',0),(40,'extraLeft','Extra actions on the product page (left column).',NULL,0),(41,'productOutOfStock','Product out of stock','Make action while product is out of stock',1),(42,'updateProductAttribute','Product attribute update',NULL,0),(43,'extraCarrier','Extra carrier (module mode)',NULL,0),(44,'shoppingCartExtra','Shopping cart extra button','Display some specific informations',1),(45,'search','Search',NULL,0),(46,'backBeforePayment','Redirect in order process','Redirect user to the module instead of displaying payment modules',0),(47,'updateCarrier','Carrier Update','This hook is called when a carrier is updated',0),(48,'postUpdateOrderStatus','Post update of order status',NULL,0),(49,'myAccountBlock','My account block','Display extra informations inside the \"my account\" block',1);
/*!40000 ALTER TABLE `ps_hook` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_hook_module`
--

DROP TABLE IF EXISTS `ps_hook_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_hook_module` (
  `id_module` int(10) unsigned NOT NULL,
  `id_hook` int(10) unsigned NOT NULL,
  `position` tinyint(2) unsigned NOT NULL,
  PRIMARY KEY  (`id_module`,`id_hook`),
  KEY `id_hook` (`id_hook`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_hook_module`
--

LOCK TABLES `ps_hook_module` WRITE;
/*!40000 ALTER TABLE `ps_hook_module` DISABLE KEYS */;
INSERT INTO `ps_hook_module` VALUES (3,1,1),(6,1,2),(4,1,3),(8,2,1),(3,4,1),(6,4,2),(9,6,1),(16,6,2),(8,6,3),(20,6,4),(15,7,1),(21,7,2),(10,7,3),(24,7,4),(14,7,5),(12,7,6),(7,7,7),(17,7,8),(5,8,1),(1,8,2),(19,9,1),(11,14,1),(13,14,2),(18,14,3),(19,14,4),(22,14,5),(8,19,1),(23,21,1),(25,11,1),(25,21,2),(26,32,1),(27,32,2),(28,32,3),(30,32,4),(31,32,5),(32,32,6),(33,32,7),(34,33,1),(35,33,2),(36,33,3),(37,33,4),(38,36,1),(39,37,1),(40,32,8),(41,32,9),(42,32,10),(43,32,11),(42,14,6),(43,14,7),(44,32,12),(45,32,13),(46,32,15),(47,32,14),(48,32,16),(49,32,17),(50,32,18),(51,32,19),(51,45,1),(25,25,1),(41,20,2);
/*!40000 ALTER TABLE `ps_hook_module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_hook_module_exceptions`
--

DROP TABLE IF EXISTS `ps_hook_module_exceptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_hook_module_exceptions` (
  `id_hook_module_exceptions` int(10) unsigned NOT NULL auto_increment,
  `id_module` int(10) unsigned NOT NULL,
  `id_hook` int(10) unsigned NOT NULL,
  `file_name` varchar(255) default NULL,
  PRIMARY KEY  (`id_hook_module_exceptions`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_hook_module_exceptions`
--

LOCK TABLES `ps_hook_module_exceptions` WRITE;
/*!40000 ALTER TABLE `ps_hook_module_exceptions` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_hook_module_exceptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_image`
--

DROP TABLE IF EXISTS `ps_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_image` (
  `id_image` int(10) unsigned NOT NULL auto_increment,
  `id_product` int(10) unsigned NOT NULL,
  `position` tinyint(2) unsigned NOT NULL default '0',
  `cover` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_image`),
  KEY `image_product` (`id_product`)
) ENGINE=MyISAM AUTO_INCREMENT=50 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_image`
--

LOCK TABLES `ps_image` WRITE;
/*!40000 ALTER TABLE `ps_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_image_lang`
--

DROP TABLE IF EXISTS `ps_image_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_image_lang` (
  `id_image` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `legend` varchar(128) default NULL,
  UNIQUE KEY `image_lang_index` (`id_image`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_image_lang`
--

LOCK TABLES `ps_image_lang` WRITE;
/*!40000 ALTER TABLE `ps_image_lang` DISABLE KEYS */;
INSERT INTO `ps_image_lang` VALUES (40,2,'iPod Nano'),(40,1,'iPod Nano'),(39,2,'iPod Nano'),(39,1,'iPod Nano'),(38,2,'iPod Nano'),(38,1,'iPod Nano'),(37,2,'iPod Nano'),(37,1,'iPod Nano'),(48,2,'iPod shuffle'),(48,1,'iPod shuffle'),(47,2,'iPod shuffle'),(47,1,'iPod shuffle'),(49,2,'iPod shuffle'),(49,1,'iPod shuffle'),(46,2,'iPod shuffle'),(46,1,'iPod shuffle'),(10,1,'luxury-cover-for-ipod-video'),(10,2,'housse-luxe-pour-ipod-video'),(11,1,'cover'),(11,2,'housse'),(12,1,'myglove-ipod-nano'),(12,2,'myglove-ipod-nano'),(13,1,'myglove-ipod-nano'),(13,2,'myglove-ipod-nano'),(14,1,'myglove-ipod-nano'),(14,2,'myglove-ipod-nano'),(15,1,'MacBook Air'),(15,2,'macbook-air-1'),(16,1,'MacBook Air'),(16,2,'macbook-air-2'),(17,1,'MacBook Air'),(17,2,'macbook-air-3'),(18,1,'MacBook Air'),(18,2,'macbook-air-4'),(19,1,'MacBook Air'),(19,2,'macbook-air-5'),(20,1,' MacBook Air SuperDrive'),(20,2,'superdrive-pour-macbook-air-1'),(24,2,'iPod touch'),(24,1,'iPod touch'),(33,1,'housse-portefeuille-en-cuir'),(26,1,'iPod touch'),(26,2,'iPod touch'),(27,1,'iPod touch'),(27,2,'iPod touch'),(29,1,'iPod touch'),(29,2,'iPod touch'),(30,1,'iPod touch'),(30,2,'iPod touch'),(32,1,'iPod touch'),(32,2,'iPod touch'),(33,2,'housse-portefeuille-en-cuir-ipod-nano'),(36,2,'Écouteurs à isolation sonore Shure SE210'),(36,1,'Shure SE210 Sound-Isolating Earphones for iPod and iPhone'),(41,1,'iPod Nano'),(41,2,'iPod Nano'),(42,1,'iPod Nano'),(42,2,'iPod Nano'),(44,1,'iPod Nano'),(44,2,'iPod Nano'),(45,1,'iPod Nano'),(45,2,'iPod Nano');
/*!40000 ALTER TABLE `ps_image_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_image_type`
--

DROP TABLE IF EXISTS `ps_image_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_image_type`
--

LOCK TABLES `ps_image_type` WRITE;
/*!40000 ALTER TABLE `ps_image_type` DISABLE KEYS */;
INSERT INTO `ps_image_type` VALUES (1,'small',45,45,1,1,1,1,0),(2,'medium',80,80,1,1,1,1,0),(3,'large',300,300,1,1,1,1,0),(4,'thickbox',600,600,1,0,0,0,0),(5,'category',500,150,0,1,0,0,0),(6,'home',129,129,1,0,0,0,0),(7,'large_scene',556,200,0,0,0,0,1),(8,'thumb_scene',161,58,0,0,0,0,1);
/*!40000 ALTER TABLE `ps_image_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_lang`
--

DROP TABLE IF EXISTS `ps_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_lang` (
  `id_lang` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(32) NOT NULL,
  `active` tinyint(3) unsigned NOT NULL default '0',
  `iso_code` char(2) NOT NULL,
  PRIMARY KEY  (`id_lang`),
  KEY `lang_iso_code` (`iso_code`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_lang`
--

LOCK TABLES `ps_lang` WRITE;
/*!40000 ALTER TABLE `ps_lang` DISABLE KEYS */;
INSERT INTO `ps_lang` VALUES (1,'English (English)',1,'en'),(2,'Français (French)',1,'fr');
/*!40000 ALTER TABLE `ps_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_manufacturer`
--

DROP TABLE IF EXISTS `ps_manufacturer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_manufacturer` (
  `id_manufacturer` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_manufacturer`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_manufacturer`
--

LOCK TABLES `ps_manufacturer` WRITE;
/*!40000 ALTER TABLE `ps_manufacturer` DISABLE KEYS */;
INSERT INTO `ps_manufacturer` VALUES (1,'Apple Computer, Inc','2010-06-08 14:08:09','2010-06-08 14:08:09'),(2,'Shure Incorporated','2010-06-08 14:08:09','2010-06-08 14:08:09');
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
  `short_description` varchar(254) default NULL,
  `meta_title` varchar(254) default NULL,
  `meta_keywords` varchar(254) default NULL,
  `meta_description` varchar(254) default NULL,
  PRIMARY KEY  (`id_manufacturer`,`id_lang`)
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
-- Table structure for table `ps_message`
--

DROP TABLE IF EXISTS `ps_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_message` (
  `id_message` int(10) unsigned NOT NULL auto_increment,
  `id_cart` int(10) unsigned default NULL,
  `id_customer` int(10) unsigned NOT NULL,
  `id_employee` int(10) unsigned default NULL,
  `id_order` int(10) unsigned NOT NULL,
  `message` text NOT NULL,
  `private` tinyint(1) unsigned NOT NULL default '1',
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_message`),
  KEY `message_order` (`id_order`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_message`
--

LOCK TABLES `ps_message` WRITE;
/*!40000 ALTER TABLE `ps_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_message_readed`
--

DROP TABLE IF EXISTS `ps_message_readed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_message_readed` (
  `id_message` int(10) unsigned NOT NULL,
  `id_employee` int(10) unsigned NOT NULL,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_message`,`id_employee`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_message_readed`
--

LOCK TABLES `ps_message_readed` WRITE;
/*!40000 ALTER TABLE `ps_message_readed` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_message_readed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_meta`
--

DROP TABLE IF EXISTS `ps_meta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_meta` (
  `id_meta` int(10) unsigned NOT NULL auto_increment,
  `page` varchar(64) NOT NULL,
  PRIMARY KEY  (`id_meta`),
  KEY `meta_name` (`page`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_meta`
--

LOCK TABLES `ps_meta` WRITE;
/*!40000 ALTER TABLE `ps_meta` DISABLE KEYS */;
INSERT INTO `ps_meta` VALUES (1,'404'),(2,'best-sales'),(3,'contact-form'),(4,'index'),(5,'manufacturer'),(6,'new-products'),(7,'password'),(8,'prices-drop'),(9,'sitemap'),(10,'supplier');
/*!40000 ALTER TABLE `ps_meta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_meta_lang`
--

DROP TABLE IF EXISTS `ps_meta_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_meta_lang` (
  `id_meta` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `title` varchar(255) default NULL,
  `description` varchar(255) default NULL,
  `keywords` varchar(255) default NULL,
  PRIMARY KEY  (`id_meta`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_meta_lang`
--

LOCK TABLES `ps_meta_lang` WRITE;
/*!40000 ALTER TABLE `ps_meta_lang` DISABLE KEYS */;
INSERT INTO `ps_meta_lang` VALUES (1,1,'404 error','This page cannot be found','error, 404, not found'),(1,2,'Erreur 404','Cette page est introuvable','erreur, 404, introuvable'),(2,1,'Best sales','Our best sales','best sales'),(2,2,'Meilleures ventes','Liste de nos produits les mieux vendus','meilleures ventes'),(3,1,'Contact us','Use our form to contact us','contact, form, e-mail'),(3,2,'Contactez-nous','Utilisez notre formulaire pour nous contacter','contact, formulaire, e-mail'),(4,1,'','Shop powered by PrestaShop','shop, prestashop'),(4,2,'','Boutique propulsée par PrestaShop','boutique, prestashop'),(5,1,'Manufacturers','Manufacturers list','manufacturer'),(5,2,'Fabricants','Liste de nos fabricants','fabricants'),(6,1,'New products','Our new products','new, products'),(6,2,'Nouveaux produits','Liste de nos nouveaux produits','nouveau, produit'),(7,1,'Forgot your password','Enter your e-mail address used to register in goal to get e-mail with your new password','forgot, password, e-mail, new, reset'),(7,2,'Mot de passe oublié','Renseignez votre adresse e-mail afin de recevoir votre nouveau mot de passe.','mot de passe, oublié, e-mail, nouveau, regénération'),(8,1,'Specials','Our special products','special, prices drop'),(8,2,'Promotions','Nos produits en promotion','promotion, réduction'),(9,1,'Sitemap','Lost ? Find what your are looking for','sitemap'),(9,2,'Plan du site','Perdu ? Trouvez ce que vous cherchez','plan, site'),(10,1,'Suppliers','Suppliers list','supplier'),(10,2,'Fournisseurs','Liste de nos fournisseurs','fournisseurs');
/*!40000 ALTER TABLE `ps_meta_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_module`
--

DROP TABLE IF EXISTS `ps_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_module` (
  `id_module` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_module`),
  KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=52 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_module`
--

LOCK TABLES `ps_module` WRITE;
/*!40000 ALTER TABLE `ps_module` DISABLE KEYS */;
INSERT INTO `ps_module` VALUES (1,'homefeatured',1),(2,'gsitemap',1),(3,'cheque',1),(4,'paypal',1),(5,'editorial',1),(6,'bankwire',1),(7,'blockadvertising',1),(8,'blockbestsellers',1),(9,'blockcart',1),(10,'blockcategories',1),(11,'blockcurrencies',1),(12,'blockinfos',1),(13,'blocklanguages',1),(14,'blockmanufacturer',1),(15,'blockmyaccount',1),(16,'blocknewproducts',1),(17,'blockpaymentlogo',1),(18,'blockpermanentlinks',1),(19,'blocksearch',1),(20,'blockspecials',1),(21,'blocktags',1),(22,'blockuserinfo',1),(23,'blockvariouslinks',1),(24,'blockviewed',1),(25,'statsdata',1),(26,'statsvisits',1),(27,'statssales',1),(28,'statsregistrations',1),(30,'statspersonalinfos',1),(31,'statslive',1),(32,'statsequipment',1),(33,'statscatalog',1),(34,'graphvisifire',1),(35,'graphxmlswfcharts',1),(36,'graphgooglechart',1),(37,'graphartichow',1),(38,'statshome',1),(39,'gridextjs',1),(40,'statsbestcustomers',1),(41,'statsorigin',1),(42,'pagesnotfound',1),(43,'sekeywords',1),(44,'statsproduct',1),(45,'statsbestproducts',1),(46,'statsbestcategories',1),(47,'statsbestvouchers',1),(48,'statsbestsuppliers',1),(49,'statscarrier',1),(50,'statsnewsletter',1),(51,'statssearch',1);
/*!40000 ALTER TABLE `ps_module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_module_country`
--

DROP TABLE IF EXISTS `ps_module_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_module_country` (
  `id_module` int(10) unsigned NOT NULL,
  `id_country` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_module`,`id_country`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_module_country`
--

LOCK TABLES `ps_module_country` WRITE;
/*!40000 ALTER TABLE `ps_module_country` DISABLE KEYS */;
INSERT INTO `ps_module_country` VALUES (3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7),(3,8),(3,9),(3,10),(3,11),(3,12),(3,13),(3,14),(3,15),(3,16),(3,17),(3,18),(3,19),(3,20),(3,21),(3,22),(3,23),(3,24),(3,25),(3,26),(3,27),(3,28),(3,29),(3,30),(3,31),(3,32),(3,33),(3,34),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),(4,10),(4,11),(4,12),(4,13),(4,14),(4,15),(4,16),(4,17),(4,18),(4,19),(4,20),(4,21),(4,22),(4,23),(4,24),(4,25),(4,26),(4,27),(4,28),(4,29),(4,30),(4,31),(4,32),(4,33),(4,34),(6,1),(6,2),(6,3),(6,4),(6,5),(6,6),(6,7),(6,8),(6,9),(6,10),(6,11),(6,12),(6,13),(6,14),(6,15),(6,16),(6,17),(6,18),(6,19),(6,20),(6,21),(6,22),(6,23),(6,24),(6,25),(6,26),(6,27),(6,28),(6,29),(6,30),(6,31),(6,32),(6,33),(6,34);
/*!40000 ALTER TABLE `ps_module_country` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_module_currency`
--

DROP TABLE IF EXISTS `ps_module_currency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_module_currency` (
  `id_module` int(10) unsigned NOT NULL,
  `id_currency` int(11) NOT NULL,
  PRIMARY KEY  (`id_module`,`id_currency`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_module_currency`
--

LOCK TABLES `ps_module_currency` WRITE;
/*!40000 ALTER TABLE `ps_module_currency` DISABLE KEYS */;
INSERT INTO `ps_module_currency` VALUES (3,1),(3,2),(3,3),(4,-2),(6,1),(6,2),(6,3);
/*!40000 ALTER TABLE `ps_module_currency` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_module_group`
--

DROP TABLE IF EXISTS `ps_module_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_module_group` (
  `id_module` int(10) unsigned NOT NULL,
  `id_group` int(11) NOT NULL,
  PRIMARY KEY  (`id_module`,`id_group`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_module_group`
--

LOCK TABLES `ps_module_group` WRITE;
/*!40000 ALTER TABLE `ps_module_group` DISABLE KEYS */;
INSERT INTO `ps_module_group` VALUES (3,1),(4,1),(6,1);
/*!40000 ALTER TABLE `ps_module_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_operating_system`
--

DROP TABLE IF EXISTS `ps_operating_system`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_operating_system` (
  `id_operating_system` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) default NULL,
  PRIMARY KEY  (`id_operating_system`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_operating_system`
--

LOCK TABLES `ps_operating_system` WRITE;
/*!40000 ALTER TABLE `ps_operating_system` DISABLE KEYS */;
INSERT INTO `ps_operating_system` VALUES (1,'Windows XP'),(2,'Windows Vista'),(3,'MacOsX'),(4,'Linux');
/*!40000 ALTER TABLE `ps_operating_system` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_detail`
--

DROP TABLE IF EXISTS `ps_order_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_detail`
--

LOCK TABLES `ps_order_detail` WRITE;
/*!40000 ALTER TABLE `ps_order_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_order_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_discount`
--

DROP TABLE IF EXISTS `ps_order_discount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_discount` (
  `id_order_discount` int(10) unsigned NOT NULL auto_increment,
  `id_order` int(10) unsigned NOT NULL,
  `id_discount` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  `value` decimal(10,2) NOT NULL default '0.00',
  PRIMARY KEY  (`id_order_discount`),
  KEY `order_discount_order` (`id_order`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_discount`
--

LOCK TABLES `ps_order_discount` WRITE;
/*!40000 ALTER TABLE `ps_order_discount` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_order_discount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_history`
--

DROP TABLE IF EXISTS `ps_order_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_history` (
  `id_order_history` int(10) unsigned NOT NULL auto_increment,
  `id_employee` int(10) unsigned NOT NULL,
  `id_order` int(10) unsigned NOT NULL,
  `id_order_state` int(10) unsigned NOT NULL,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_order_history`),
  KEY `order_history_order` (`id_order`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_history`
--

LOCK TABLES `ps_order_history` WRITE;
/*!40000 ALTER TABLE `ps_order_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_order_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_message`
--

DROP TABLE IF EXISTS `ps_order_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_message` (
  `id_order_message` int(10) unsigned NOT NULL auto_increment,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_order_message`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_message`
--

LOCK TABLES `ps_order_message` WRITE;
/*!40000 ALTER TABLE `ps_order_message` DISABLE KEYS */;
INSERT INTO `ps_order_message` VALUES (1,'2010-06-08 14:08:09');
/*!40000 ALTER TABLE `ps_order_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_message_lang`
--

DROP TABLE IF EXISTS `ps_order_message_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_message_lang` (
  `id_order_message` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  `message` text NOT NULL,
  PRIMARY KEY  (`id_order_message`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_message_lang`
--

LOCK TABLES `ps_order_message_lang` WRITE;
/*!40000 ALTER TABLE `ps_order_message_lang` DISABLE KEYS */;
INSERT INTO `ps_order_message_lang` VALUES (1,1,'Delay','Hi,\n\nUnfortunately, an item on your order is currently out of stock. This may cause a slight delay in delivery.\nPlease accept our apologies and rest assured that we are working hard to rectify this.\n\nBest regards,\n'),(1,2,'Délai','Bonjour,\n\nUn des éléments de votre commande est actuellement en réapprovisionnement, ce qui peut légèrement retarder son envoi.\n\nMerci de votre compréhension.\n\nCordialement, \n');
/*!40000 ALTER TABLE `ps_order_message_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_return`
--

DROP TABLE IF EXISTS `ps_order_return`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_return`
--

LOCK TABLES `ps_order_return` WRITE;
/*!40000 ALTER TABLE `ps_order_return` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_order_return` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_return_detail`
--

DROP TABLE IF EXISTS `ps_order_return_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_return_detail` (
  `id_order_return` int(10) unsigned NOT NULL,
  `id_order_detail` int(10) unsigned NOT NULL,
  `id_customization` int(10) NOT NULL default '0',
  `product_quantity` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_order_return`,`id_order_detail`,`id_customization`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_return_detail`
--

LOCK TABLES `ps_order_return_detail` WRITE;
/*!40000 ALTER TABLE `ps_order_return_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_order_return_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_return_state`
--

DROP TABLE IF EXISTS `ps_order_return_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_return_state` (
  `id_order_return_state` int(10) unsigned NOT NULL auto_increment,
  `color` varchar(32) default NULL,
  PRIMARY KEY  (`id_order_return_state`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_return_state`
--

LOCK TABLES `ps_order_return_state` WRITE;
/*!40000 ALTER TABLE `ps_order_return_state` DISABLE KEYS */;
INSERT INTO `ps_order_return_state` VALUES (1,'#ADD8E6'),(2,'#EEDDFF'),(3,'#DDFFAA'),(4,'#FFD3D3'),(5,'#FFFFBB');
/*!40000 ALTER TABLE `ps_order_return_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_return_state_lang`
--

DROP TABLE IF EXISTS `ps_order_return_state_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_return_state_lang` (
  `id_order_return_state` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  UNIQUE KEY `order_state_lang_index` (`id_order_return_state`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_return_state_lang`
--

LOCK TABLES `ps_order_return_state_lang` WRITE;
/*!40000 ALTER TABLE `ps_order_return_state_lang` DISABLE KEYS */;
INSERT INTO `ps_order_return_state_lang` VALUES (1,1,'Waiting for confirmation'),(2,1,'Waiting for package'),(3,1,'Package received'),(4,1,'Return denied'),(5,1,'Return completed'),(1,2,'En attente de confirmation'),(2,2,'En attente du colis'),(3,2,'Colis reçu'),(4,2,'Retour refusé'),(5,2,'Retour terminé');
/*!40000 ALTER TABLE `ps_order_return_state_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_slip`
--

DROP TABLE IF EXISTS `ps_order_slip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_slip`
--

LOCK TABLES `ps_order_slip` WRITE;
/*!40000 ALTER TABLE `ps_order_slip` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_order_slip` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_slip_detail`
--

DROP TABLE IF EXISTS `ps_order_slip_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_slip_detail` (
  `id_order_slip` int(10) unsigned NOT NULL,
  `id_order_detail` int(10) unsigned NOT NULL,
  `product_quantity` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_order_slip`,`id_order_detail`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_slip_detail`
--

LOCK TABLES `ps_order_slip_detail` WRITE;
/*!40000 ALTER TABLE `ps_order_slip_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_order_slip_detail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_state`
--

DROP TABLE IF EXISTS `ps_order_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_state`
--

LOCK TABLES `ps_order_state` WRITE;
/*!40000 ALTER TABLE `ps_order_state` DISABLE KEYS */;
INSERT INTO `ps_order_state` VALUES (1,0,1,'lightblue',1,0,0,0),(2,1,1,'#DDEEFF',1,0,1,0),(3,1,1,'#FFDD99',1,0,1,1),(4,1,1,'#EEDDFF',1,0,1,1),(5,1,0,'#DDFFAA',1,0,1,1),(6,1,1,'#DADADA',1,0,0,0),(7,1,1,'#FFFFBB',1,0,0,0),(8,0,1,'#FFDFDF',1,0,0,0),(9,1,1,'#FFD3D3',1,0,0,0),(10,0,1,'lightblue',1,0,0,0),(11,0,0,'lightblue',1,0,0,0);
/*!40000 ALTER TABLE `ps_order_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_order_state_lang`
--

DROP TABLE IF EXISTS `ps_order_state_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_order_state_lang` (
  `id_order_state` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  `template` varchar(64) NOT NULL,
  UNIQUE KEY `order_state_lang_index` (`id_order_state`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_order_state_lang`
--

LOCK TABLES `ps_order_state_lang` WRITE;
/*!40000 ALTER TABLE `ps_order_state_lang` DISABLE KEYS */;
INSERT INTO `ps_order_state_lang` VALUES (1,1,'Awaiting cheque payment','cheque'),(2,1,'Payment accepted','payment'),(3,1,'Preparation in progress','preparation'),(4,1,'Shipped','shipped'),(5,1,'Delivered',''),(6,1,'Canceled','order_canceled'),(7,1,'Refund','refund'),(8,1,'Payment error','payment_error'),(9,1,'Out of stock','outofstock'),(10,1,'Awaiting bank wire payment','bankwire'),(11,1,'Awaiting PayPal payment',''),(1,2,'En attente du paiement par chèque','cheque'),(2,2,'Paiement accepté','payment'),(3,2,'Préparation en cours','preparation'),(4,2,'En cours de livraison','shipped'),(5,2,'Livré',''),(6,2,'Annulé','order_canceled'),(7,2,'Remboursé','refund'),(8,2,'Erreur de paiement','payment_error'),(9,2,'Produit(s) indisponibles','outofstock'),(10,2,'En attente du paiement par virement bancaire','bankwire'),(11,2,'En attente du paiement par PayPal','');
/*!40000 ALTER TABLE `ps_order_state_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_orders`
--

DROP TABLE IF EXISTS `ps_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_orders`
--

LOCK TABLES `ps_orders` WRITE;
/*!40000 ALTER TABLE `ps_orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_pack`
--

DROP TABLE IF EXISTS `ps_pack`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_pack` (
  `id_product_pack` int(10) unsigned NOT NULL,
  `id_product_item` int(10) unsigned NOT NULL,
  `quantity` int(10) unsigned NOT NULL default '1',
  PRIMARY KEY  (`id_product_pack`,`id_product_item`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_pack`
--

LOCK TABLES `ps_pack` WRITE;
/*!40000 ALTER TABLE `ps_pack` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_pack` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_page`
--

DROP TABLE IF EXISTS `ps_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_page` (
  `id_page` int(10) unsigned NOT NULL auto_increment,
  `id_page_type` int(10) unsigned NOT NULL,
  `id_object` int(10) unsigned default NULL,
  PRIMARY KEY  (`id_page`),
  KEY `id_page_type` (`id_page_type`),
  KEY `id_object` (`id_object`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_page`
--

LOCK TABLES `ps_page` WRITE;
/*!40000 ALTER TABLE `ps_page` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_page` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_page_type`
--

DROP TABLE IF EXISTS `ps_page_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_page_type` (
  `id_page_type` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY  (`id_page_type`),
  KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_page_type`
--

LOCK TABLES `ps_page_type` WRITE;
/*!40000 ALTER TABLE `ps_page_type` DISABLE KEYS */;
INSERT INTO `ps_page_type` VALUES (1,'product.php'),(2,'category.php'),(3,'order.php'),(4,'manufacturer.php');
/*!40000 ALTER TABLE `ps_page_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_page_viewed`
--

DROP TABLE IF EXISTS `ps_page_viewed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_page_viewed` (
  `id_page` int(10) unsigned NOT NULL,
  `id_date_range` int(10) unsigned NOT NULL,
  `counter` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_page`,`id_date_range`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_page_viewed`
--

LOCK TABLES `ps_page_viewed` WRITE;
/*!40000 ALTER TABLE `ps_page_viewed` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_page_viewed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_pagenotfound`
--

DROP TABLE IF EXISTS `ps_pagenotfound`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_pagenotfound` (
  `id_pagenotfound` int(10) unsigned NOT NULL auto_increment,
  `request_uri` varchar(256) NOT NULL,
  `http_referer` varchar(256) NOT NULL,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_pagenotfound`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_pagenotfound`
--

LOCK TABLES `ps_pagenotfound` WRITE;
/*!40000 ALTER TABLE `ps_pagenotfound` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_pagenotfound` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product`
--

DROP TABLE IF EXISTS `ps_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product`
--

LOCK TABLES `ps_product` WRITE;
/*!40000 ALTER TABLE `ps_product` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product_attachment`
--

DROP TABLE IF EXISTS `ps_product_attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_product_attachment` (
  `id_product` int(10) NOT NULL,
  `id_attachment` int(10) NOT NULL,
  PRIMARY KEY  (`id_product`,`id_attachment`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_attachment`
--

LOCK TABLES `ps_product_attachment` WRITE;
/*!40000 ALTER TABLE `ps_product_attachment` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_attachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product_attribute`
--

DROP TABLE IF EXISTS `ps_product_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
) ENGINE=MyISAM AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;
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
  PRIMARY KEY  (`id_attribute`,`id_product_attribute`)
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
-- Table structure for table `ps_product_attribute_image`
--

DROP TABLE IF EXISTS `ps_product_attribute_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_product_attribute_image` (
  `id_product_attribute` int(10) NOT NULL,
  `id_image` int(10) NOT NULL,
  PRIMARY KEY  (`id_product_attribute`,`id_image`),
  KEY `id_image` (`id_image`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_attribute_image`
--

LOCK TABLES `ps_product_attribute_image` WRITE;
/*!40000 ALTER TABLE `ps_product_attribute_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_attribute_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product_download`
--

DROP TABLE IF EXISTS `ps_product_download`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_download`
--

LOCK TABLES `ps_product_download` WRITE;
/*!40000 ALTER TABLE `ps_product_download` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_download` ENABLE KEYS */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_lang`
--

LOCK TABLES `ps_product_lang` WRITE;
/*!40000 ALTER TABLE `ps_product_lang` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product_sale`
--

DROP TABLE IF EXISTS `ps_product_sale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_product_sale` (
  `id_product` int(10) unsigned NOT NULL,
  `quantity` int(10) unsigned NOT NULL default '0',
  `sale_nbr` int(10) unsigned NOT NULL default '0',
  `date_upd` date NOT NULL,
  PRIMARY KEY  (`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_sale`
--

LOCK TABLES `ps_product_sale` WRITE;
/*!40000 ALTER TABLE `ps_product_sale` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_sale` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_product_tag`
--

DROP TABLE IF EXISTS `ps_product_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_product_tag` (
  `id_product` int(10) unsigned NOT NULL,
  `id_tag` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_product`,`id_tag`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_product_tag`
--

LOCK TABLES `ps_product_tag` WRITE;
/*!40000 ALTER TABLE `ps_product_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_product_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_profile`
--

DROP TABLE IF EXISTS `ps_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_profile` (
  `id_profile` int(10) unsigned NOT NULL auto_increment,
  PRIMARY KEY  (`id_profile`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_profile`
--

LOCK TABLES `ps_profile` WRITE;
/*!40000 ALTER TABLE `ps_profile` DISABLE KEYS */;
INSERT INTO `ps_profile` VALUES (1);
/*!40000 ALTER TABLE `ps_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_profile_lang`
--

DROP TABLE IF EXISTS `ps_profile_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_profile_lang` (
  `id_lang` int(10) unsigned NOT NULL,
  `id_profile` int(10) unsigned NOT NULL,
  `name` varchar(128) NOT NULL,
  PRIMARY KEY  (`id_profile`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_profile_lang`
--

LOCK TABLES `ps_profile_lang` WRITE;
/*!40000 ALTER TABLE `ps_profile_lang` DISABLE KEYS */;
INSERT INTO `ps_profile_lang` VALUES (1,1,'Administrator'),(2,1,'Administrateur');
/*!40000 ALTER TABLE `ps_profile_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_quick_access`
--

DROP TABLE IF EXISTS `ps_quick_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_quick_access` (
  `id_quick_access` int(10) unsigned NOT NULL auto_increment,
  `new_window` tinyint(1) NOT NULL default '0',
  `link` varchar(128) NOT NULL,
  PRIMARY KEY  (`id_quick_access`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_quick_access`
--

LOCK TABLES `ps_quick_access` WRITE;
/*!40000 ALTER TABLE `ps_quick_access` DISABLE KEYS */;
INSERT INTO `ps_quick_access` VALUES (1,0,'index.php'),(2,1,'../'),(3,0,'index.php?tab=AdminCatalog&addcategory'),(4,0,'index.php?tab=AdminCatalog&addproduct'),(5,0,'index.php?tab=AdminDiscounts&adddiscount');
/*!40000 ALTER TABLE `ps_quick_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_quick_access_lang`
--

DROP TABLE IF EXISTS `ps_quick_access_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_quick_access_lang` (
  `id_quick_access` int(10) unsigned NOT NULL,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY  (`id_quick_access`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_quick_access_lang`
--

LOCK TABLES `ps_quick_access_lang` WRITE;
/*!40000 ALTER TABLE `ps_quick_access_lang` DISABLE KEYS */;
INSERT INTO `ps_quick_access_lang` VALUES (1,1,'Home'),(1,2,'Accueil'),(2,1,'My Shop'),(2,2,'Ma boutique'),(3,1,'New category'),(3,2,'Nouvelle catégorie'),(4,1,'New product'),(4,2,'Nouveau produit'),(5,1,'New voucher'),(5,2,'Nouveau bon de réduction');
/*!40000 ALTER TABLE `ps_quick_access_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_range_price`
--

DROP TABLE IF EXISTS `ps_range_price`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_range_price` (
  `id_range_price` int(10) unsigned NOT NULL auto_increment,
  `id_carrier` int(10) unsigned NOT NULL,
  `delimiter1` decimal(13,6) NOT NULL,
  `delimiter2` decimal(13,6) NOT NULL,
  PRIMARY KEY  (`id_range_price`),
  UNIQUE KEY `id_carrier` (`id_carrier`,`delimiter1`,`delimiter2`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_range_price`
--

LOCK TABLES `ps_range_price` WRITE;
/*!40000 ALTER TABLE `ps_range_price` DISABLE KEYS */;
INSERT INTO `ps_range_price` VALUES (1,2,'0.000000','10000.000000');
/*!40000 ALTER TABLE `ps_range_price` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_range_weight`
--

DROP TABLE IF EXISTS `ps_range_weight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_range_weight` (
  `id_range_weight` int(10) unsigned NOT NULL auto_increment,
  `id_carrier` int(10) unsigned NOT NULL,
  `delimiter1` decimal(13,6) NOT NULL,
  `delimiter2` decimal(13,6) NOT NULL,
  PRIMARY KEY  (`id_range_weight`),
  UNIQUE KEY `id_carrier` (`id_carrier`,`delimiter1`,`delimiter2`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_range_weight`
--

LOCK TABLES `ps_range_weight` WRITE;
/*!40000 ALTER TABLE `ps_range_weight` DISABLE KEYS */;
INSERT INTO `ps_range_weight` VALUES (1,2,'0.000000','10000.000000');
/*!40000 ALTER TABLE `ps_range_weight` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_referrer`
--

DROP TABLE IF EXISTS `ps_referrer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_referrer` (
  `id_referrer` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `passwd` varchar(32) default NULL,
  `http_referer_regexp` varchar(64) default NULL,
  `http_referer_like` varchar(64) default NULL,
  `request_uri_regexp` varchar(64) default NULL,
  `request_uri_like` varchar(64) default NULL,
  `http_referer_regexp_not` varchar(64) default NULL,
  `http_referer_like_not` varchar(64) default NULL,
  `request_uri_regexp_not` varchar(64) default NULL,
  `request_uri_like_not` varchar(64) default NULL,
  `base_fee` decimal(5,2) NOT NULL default '0.00',
  `percent_fee` decimal(5,2) NOT NULL default '0.00',
  `click_fee` decimal(5,2) NOT NULL default '0.00',
  `cache_visitors` int(11) default NULL,
  `cache_visits` int(11) default NULL,
  `cache_pages` int(11) default NULL,
  `cache_registrations` int(11) default NULL,
  `cache_orders` int(11) default NULL,
  `cache_sales` decimal(10,2) default NULL,
  `cache_reg_rate` decimal(5,4) default NULL,
  `cache_order_rate` decimal(5,4) default NULL,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_referrer`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_referrer`
--

LOCK TABLES `ps_referrer` WRITE;
/*!40000 ALTER TABLE `ps_referrer` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_referrer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_referrer_cache`
--

DROP TABLE IF EXISTS `ps_referrer_cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_referrer_cache` (
  `id_connections_source` int(11) NOT NULL,
  `id_referrer` int(11) NOT NULL,
  PRIMARY KEY  (`id_connections_source`,`id_referrer`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_referrer_cache`
--

LOCK TABLES `ps_referrer_cache` WRITE;
/*!40000 ALTER TABLE `ps_referrer_cache` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_referrer_cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_scene`
--

DROP TABLE IF EXISTS `ps_scene`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_scene` (
  `id_scene` int(10) unsigned NOT NULL auto_increment,
  `active` tinyint(1) NOT NULL default '1',
  PRIMARY KEY  (`id_scene`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_scene`
--

LOCK TABLES `ps_scene` WRITE;
/*!40000 ALTER TABLE `ps_scene` DISABLE KEYS */;
INSERT INTO `ps_scene` VALUES (1,1),(2,1),(3,1);
/*!40000 ALTER TABLE `ps_scene` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_scene_category`
--

DROP TABLE IF EXISTS `ps_scene_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_scene_category` (
  `id_scene` int(10) NOT NULL,
  `id_category` int(10) NOT NULL,
  PRIMARY KEY  (`id_scene`,`id_category`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_scene_category`
--

LOCK TABLES `ps_scene_category` WRITE;
/*!40000 ALTER TABLE `ps_scene_category` DISABLE KEYS */;
INSERT INTO `ps_scene_category` VALUES (1,2),(2,2),(3,4);
/*!40000 ALTER TABLE `ps_scene_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_scene_lang`
--

DROP TABLE IF EXISTS `ps_scene_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_scene_lang` (
  `id_scene` int(10) NOT NULL,
  `id_lang` int(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY  (`id_scene`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_scene_lang`
--

LOCK TABLES `ps_scene_lang` WRITE;
/*!40000 ALTER TABLE `ps_scene_lang` DISABLE KEYS */;
INSERT INTO `ps_scene_lang` VALUES (1,1,'The iPods Nano'),(1,2,'Les iPods Nano'),(2,1,'The iPods'),(2,2,'Les iPods'),(3,1,'The MacBooks'),(3,2,'Les MacBooks');
/*!40000 ALTER TABLE `ps_scene_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_scene_products`
--

DROP TABLE IF EXISTS `ps_scene_products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_scene_products` (
  `id_scene` int(10) NOT NULL,
  `id_product` int(10) NOT NULL,
  `x_axis` int(4) NOT NULL,
  `y_axis` int(4) NOT NULL,
  `zone_width` int(3) NOT NULL,
  `zone_height` int(3) NOT NULL,
  PRIMARY KEY  (`id_scene`,`id_product`,`x_axis`,`y_axis`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_scene_products`
--

LOCK TABLES `ps_scene_products` WRITE;
/*!40000 ALTER TABLE `ps_scene_products` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_scene_products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_search_engine`
--

DROP TABLE IF EXISTS `ps_search_engine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_search_engine` (
  `id_search_engine` int(10) unsigned NOT NULL auto_increment,
  `server` varchar(64) NOT NULL,
  `getvar` varchar(16) NOT NULL,
  PRIMARY KEY  (`id_search_engine`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_search_engine`
--

LOCK TABLES `ps_search_engine` WRITE;
/*!40000 ALTER TABLE `ps_search_engine` DISABLE KEYS */;
INSERT INTO `ps_search_engine` VALUES (1,'google','q'),(2,'search.aol','query'),(3,'yandex.ru','text'),(4,'ask.com','q'),(5,'nhl.com','q'),(6,'search.yahoo','p'),(7,'baidu.com','wd'),(8,'search.lycos','query'),(9,'exalead','q'),(10,'search.live.com','q'),(11,'search.ke.voila','rdata'),(12,'altavista','q'),(13,'bing.com','q');
/*!40000 ALTER TABLE `ps_search_engine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_search_index`
--

DROP TABLE IF EXISTS `ps_search_index`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_search_index` (
  `id_product` int(11) NOT NULL,
  `id_word` int(11) NOT NULL,
  `weight` tinyint(4) NOT NULL default '1',
  PRIMARY KEY  (`id_word`,`id_product`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_search_index`
--

LOCK TABLES `ps_search_index` WRITE;
/*!40000 ALTER TABLE `ps_search_index` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_search_index` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_search_word`
--

DROP TABLE IF EXISTS `ps_search_word`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_search_word` (
  `id_word` int(10) unsigned NOT NULL auto_increment,
  `id_lang` int(10) unsigned NOT NULL,
  `word` varchar(15) NOT NULL,
  PRIMARY KEY  (`id_word`),
  UNIQUE KEY `id_lang` (`id_lang`,`word`)
) ENGINE=MyISAM AUTO_INCREMENT=1036 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_search_word`
--

LOCK TABLES `ps_search_word` WRITE;
/*!40000 ALTER TABLE `ps_search_word` DISABLE KEYS */;
INSERT INTO `ps_search_word` VALUES (1,1,'ipod'),(2,1,'nano'),(3,1,'design'),(4,1,'features'),(5,1,'16gb'),(6,1,'rocks'),(7,1,'like'),(8,1,'never'),(9,1,'before'),(10,1,'curved'),(11,1,'ahead'),(12,1,'curve'),(13,1,'those'),(14,1,'about'),(15,1,'rock,'),(16,1,'give'),(17,1,'nine'),(18,1,'amazing'),(19,1,'colors'),(20,1,'that'),(21,1,'only'),(22,1,'part'),(23,1,'story'),(24,1,'feel'),(25,1,'curved,'),(26,1,'allaluminum'),(27,1,'glass'),(28,1,'want'),(29,1,'down'),(30,1,'great'),(31,1,'looks'),(32,1,'brains,'),(33,1,'genius'),(34,1,'feature'),(35,1,'turns'),(36,1,'into'),(37,1,'your'),(38,1,'highly'),(39,1,'intelligent,'),(40,1,'personal'),(41,1,'creates'),(42,1,'playlists'),(43,1,'finding'),(44,1,'songs'),(45,1,'library'),(46,1,'together'),(47,1,'made'),(48,1,'move'),(49,1,'with'),(50,1,'moves'),(51,1,'accelerometer'),(52,1,'comes'),(53,1,'shake'),(54,1,'shuffle'),(55,1,'music'),(56,1,'turn'),(57,1,'sideways'),(58,1,'view'),(59,1,'cover'),(60,1,'flow'),(61,1,'play'),(62,1,'games'),(63,1,'designed'),(64,1,'mind'),(65,1,'ipods'),(66,1,'apple'),(67,1,'computer,'),(68,1,'metal'),(69,1,'16go'),(70,1,'yellow'),(71,1,'blue'),(72,1,'black'),(73,1,'orange'),(74,1,'pink'),(75,1,'green'),(76,1,'purple'),(77,1,'grams'),(78,1,'minijack'),(79,1,'stereo'),(80,2,'ipod'),(81,2,'nano'),(82,2,'nouveau'),(83,2,'design'),(84,2,'nouvelles'),(85,2,'fonctionnalités'),(86,2,'désormais'),(87,2,'nano,'),(88,2,'plus'),(89,2,'rock'),(90,2,'jamais'),(91,2,'courbes'),(92,2,'avantageuses'),(93,2,'pour'),(94,2,'amateurs'),(95,2,'sensations,'),(96,2,'voici'),(97,2,'neuf'),(98,2,'nouveaux'),(99,2,'coloris'),(100,2,'n\'est'),(101,2,'tout'),(102,2,'faites'),(103,2,'l\'expérience'),(104,2,'elliptique'),(105,2,'aluminum'),(106,2,'verre'),(107,2,'vous'),(108,2,'voudrez'),(109,2,'lâcher'),(110,2,'beau'),(111,2,'intelligent'),(112,2,'nouvelle'),(113,2,'fonctionnalité'),(114,2,'genius'),(115,2,'fait'),(116,2,'d\'ipod'),(117,2,'votre'),(118,2,'personnel'),(119,2,'crée'),(120,2,'listes'),(121,2,'lecture'),(122,2,'recherchant'),(123,2,'dans'),(124,2,'bibliothèque'),(125,2,'chansons'),(126,2,'vont'),(127,2,'bien'),(128,2,'ensemble'),(129,2,'bouger'),(130,2,'avec'),(131,2,'équipé'),(132,2,'l\'accéléromètre'),(133,2,'secouezle'),(134,2,'mélanger'),(135,2,'musique'),(136,2,'basculezle'),(137,2,'afficher'),(138,2,'cover'),(139,2,'flow'),(140,2,'découvrez'),(141,2,'jeux'),(142,2,'adaptés'),(143,2,'mouvements'),(144,2,'ipods'),(145,2,'apple'),(146,2,'computer,'),(147,2,'metal'),(148,2,'16go'),(149,2,'jaune'),(150,2,'bleu'),(151,2,'noir'),(152,2,'orange'),(153,2,'rose'),(154,2,'vert'),(155,2,'violet'),(156,2,'grammes'),(157,2,'minijack'),(158,2,'stéréo'),(159,1,'shuffle,'),(160,1,'world'),(161,1,'most'),(162,1,'wearable'),(163,1,'player,'),(164,1,'clips'),(165,1,'more'),(166,1,'vibrant'),(167,1,'blue,'),(168,1,'green,'),(169,1,'pink,'),(170,1,'instant'),(171,1,'attachment'),(172,1,'wear'),(173,1,'sleeve'),(174,1,'belt'),(175,1,'shorts'),(176,1,'badge'),(177,1,'musical'),(178,1,'devotion'),(179,1,'new,'),(180,1,'brilliant'),(181,1,'feed'),(182,1,'itunes'),(183,1,'entertainment'),(184,1,'superstore'),(185,1,'ultraorganized'),(186,1,'collection'),(187,1,'jukebox'),(188,1,'load'),(189,1,'click'),(190,1,'beauty'),(191,1,'beat'),(192,1,'intensely'),(193,1,'colorful'),(194,1,'anodized'),(195,1,'aluminum'),(196,1,'complements'),(197,1,'simple'),(198,1,'red,'),(199,1,'original'),(200,1,'silver'),(201,1,'(clip'),(202,1,'compris)'),(203,2,'shuffle'),(204,2,'shuffle,'),(205,2,'baladeur'),(206,2,'portable'),(207,2,'monde,'),(208,2,'clippe'),(209,2,'maintenant'),(210,2,'bleu,'),(211,2,'vert,'),(212,2,'rouge'),(213,2,'lien'),(214,2,'immédiat'),(215,2,'portez'),(217,2,'accrochées'),(218,2,'manche,'),(219,2,'ceinture'),(220,2,'short'),(221,2,'arborez'),(222,2,'comme'),(223,2,'signe'),(224,2,'extérieur'),(225,2,'passion'),(226,2,'existe'),(227,2,'quatre'),(228,2,'encore'),(229,2,'éclatants'),(230,2,'emplissez'),(231,2,'itunes'),(232,2,'immense'),(233,2,'magasin'),(234,2,'dédié'),(235,2,'divertissement,'),(236,2,'collection'),(237,2,'musicale'),(238,2,'parfaitement'),(239,2,'organisée'),(240,2,'jukebox'),(241,2,'pouvez'),(242,2,'seul'),(243,2,'clic'),(244,2,'remplir'),(245,2,'technicolor'),(246,2,'s\'affiche'),(247,2,'intenses'),(248,2,'rehaussent'),(249,2,'épuré'),(250,2,'boîtier'),(251,2,'aluminium'),(252,2,'anodisé'),(253,2,'choisissez'),(254,2,'parmi'),(255,2,'rose,'),(256,2,'l\'argenté'),(257,2,'d\'origine'),(258,2,'(clip'),(259,2,'compris)'),(260,1,'macbook'),(261,1,'ultrathin,'),(262,1,'ultraportable,'),(263,1,'ultra'),(264,1,'unlike'),(265,1,'anything'),(266,1,'else'),(267,1,'lose'),(268,1,'inches'),(269,1,'pounds'),(270,1,'overnight'),(271,1,'result'),(272,1,'rethinking'),(273,1,'conventions'),(274,1,'multiple'),(275,1,'wireless'),(276,1,'innovations'),(277,1,'breakthrough'),(278,1,'air,'),(279,1,'mobile'),(280,1,'computing'),(281,1,'suddenly'),(282,1,'standard'),(283,1,'nearly'),(284,1,'thin'),(285,1,'index'),(286,1,'finger'),(287,1,'practically'),(288,1,'every'),(289,1,'detail'),(290,1,'could'),(291,1,'streamlined'),(292,1,'been'),(293,1,'still'),(294,1,'133inch'),(295,1,'widescreen'),(296,1,'display,'),(297,1,'fullsize'),(298,1,'keyboard,'),(299,1,'large'),(300,1,'multitouch'),(301,1,'trackpad'),(302,1,'incomparably'),(303,1,'portable'),(304,1,'without'),(305,1,'usual'),(306,1,'ultraportable'),(307,1,'screen'),(308,1,'keyboard'),(309,1,'compromisesthe'),(310,1,'incredible'),(311,1,'thinness'),(312,1,'numerous'),(313,1,'size'),(314,1,'weightshaving'),(315,1,'from'),(316,1,'slimmer'),(317,1,'hard'),(318,1,'drive'),(319,1,'strategically'),(320,1,'hidden'),(321,1,'ports'),(322,1,'lowerprofile'),(323,1,'battery,'),(324,1,'everything'),(325,1,'considered'),(326,1,'reconsidered'),(327,1,'mindmacbook'),(328,1,'engineered'),(329,1,'take'),(330,1,'full'),(331,1,'advantage'),(332,1,'which'),(333,1,'80211n'),(334,1,'wifi'),(335,1,'fast'),(336,1,'available,'),(337,1,'people'),(338,1,'truly'),(339,1,'living'),(340,1,'untethered'),(341,1,'buying'),(342,1,'renting'),(343,1,'movies'),(344,1,'online,'),(345,1,'downloading'),(346,1,'software,'),(347,1,'sharing'),(348,1,'storing'),(349,1,'files'),(350,1,'laptops'),(351,1,'80gb'),(352,1,'parallel'),(353,1,'4200'),(354,1,'160ghz'),(355,1,'intel'),(356,1,'core'),(357,1,'optional'),(358,1,'64gb'),(359,1,'solidstate'),(360,1,'180ghz'),(361,2,'macbook'),(362,2,'ultra'),(363,2,'fin,'),(364,2,'différent'),(365,2,'reste'),(366,2,'mais'),(367,2,'perd'),(368,2,'kilos'),(369,2,'centimètres'),(370,2,'nuit'),(371,2,'c\'est'),(372,2,'résultat'),(373,2,'d\'une'),(374,2,'réinvention'),(375,2,'normes'),(376,2,'multitude'),(377,2,'d\'innovations'),(378,2,'sans'),(379,2,'révolution'),(380,2,'air,'),(381,2,'l\'informatique'),(382,2,'mobile'),(383,2,'prend'),(384,2,'soudain'),(385,2,'dimension'),(386,2,'presque'),(387,2,'aussi'),(388,2,'index'),(389,2,'pratiquement'),(390,2,'pouvait'),(391,2,'être'),(392,2,'simplifié'),(393,2,'n\'en'),(394,2,'dispose'),(395,2,'moins'),(396,2,'d\'un'),(397,2,'écran'),(398,2,'panoramique'),(399,2,'pouces,'),(400,2,'clavier'),(401,2,'complet'),(402,2,'vaste'),(403,2,'trackpad'),(404,2,'multitouch'),(405,2,'incomparablemen'),(406,2,'évite'),(407,2,'compromis'),(408,2,'habituels'),(409,2,'matière'),(410,2,'d\'écran'),(411,2,'ultraportablesl'),(412,2,'finesse'),(413,2,'grand'),(414,2,'nombre'),(415,2,'termes'),(416,2,'réduction'),(417,2,'taille'),(418,2,'poids'),(419,2,'disque'),(420,2,'ports'),(421,2,'habilement'),(422,2,'dissimulés'),(423,2,'passant'),(424,2,'batterie'),(425,2,'plate,'),(426,2,'chaque'),(427,2,'détail'),(428,2,'considéré'),(429,2,'reconsidéré'),(430,2,'l\'espritmacbook'),(431,2,'conçu'),(432,2,'élaboré'),(433,2,'profiter'),(434,2,'pleinement'),(435,2,'monde'),(436,2,'lequel'),(437,2,'norme'),(438,2,'wifi'),(439,2,'80211n'),(440,2,'rapide'),(441,2,'accessible'),(442,2,'qu\'elle'),(443,2,'permet'),(444,2,'véritablement'),(445,2,'libérer'),(446,2,'toute'),(447,2,'attache'),(448,2,'acheter'),(449,2,'vidéos'),(450,2,'ligne,'),(451,2,'télécharger'),(452,2,'logicééééiels,'),(453,2,'stocker'),(454,2,'partager'),(455,2,'fichiers'),(456,2,'portables'),(457,2,'macbookair'),(458,2,'pata'),(459,2,'intel'),(460,2,'core'),(461,2,'(solidstate'),(462,2,'drive)'),(463,1,'makes'),(464,1,'easy'),(465,1,'road'),(466,1,'thanks'),(467,1,'tough'),(468,1,'polycarbonate'),(469,1,'case,'),(470,1,'builtin'),(471,1,'technologies,'),(472,1,'innovative'),(473,1,'magsafe'),(474,1,'power'),(475,1,'adapter'),(476,1,'releases'),(477,1,'automatically'),(478,1,'someone'),(479,1,'accidentally'),(480,1,'trips'),(481,1,'cord'),(482,1,'larger'),(483,1,'drive,'),(484,1,'250gb,'),(485,1,'store'),(486,1,'growing'),(487,1,'media'),(488,1,'collections'),(489,1,'valuable'),(490,1,'datathe'),(491,1,'24ghz'),(492,1,'models'),(493,1,'include'),(494,1,'memory'),(495,1,'perfect'),(496,1,'running'),(497,1,'favorite'),(498,1,'applications'),(499,1,'smoothly'),(500,1,'superdrive'),(501,2,'offre'),(502,2,'liberté'),(503,2,'mouvement'),(504,2,'grâce'),(505,2,'résistant'),(506,2,'polycarbonate,'),(507,2,'technologies'),(508,2,'intégrées'),(509,2,'adaptateur'),(510,2,'secteur'),(511,2,'magsafe'),(512,2,'novateur'),(513,2,'déconnecte'),(514,2,'automatiquement'),(515,2,'quelqu\'un'),(516,2,'pieds'),(517,2,'spacieux,'),(518,2,'capacité'),(519,2,'atteignant'),(520,2,'collections'),(521,2,'multimédia'),(522,2,'expansion'),(523,2,'données'),(524,2,'précieusesle'),(525,2,'modèle'),(526,2,'intègre'),(527,2,'mémoire'),(528,2,'standard'),(529,2,'l\'idéal'),(530,2,'exécuter'),(531,2,'souplesse'),(532,2,'applications'),(533,2,'préférées'),(534,1,'touch'),(535,1,'revolutionary'),(536,1,'interface'),(537,1,'35inch'),(538,1,'color'),(539,1,'display'),(540,1,'(80211b'),(541,1,'safari,'),(542,1,'youtube,'),(543,1,'mail,'),(544,1,'stocks,'),(545,1,'weather,'),(546,1,'notes,'),(547,1,'store,'),(548,1,'maps'),(549,1,'five'),(550,1,'handson'),(551,1,'rich'),(552,1,'html'),(553,1,'email'),(554,1,'photos'),(555,1,'well'),(556,1,'pdf,'),(557,1,'word,'),(558,1,'excel'),(559,1,'attachments'),(560,1,'maps,'),(561,1,'directions,'),(562,1,'realtime'),(563,1,'traffic'),(564,1,'information'),(565,1,'notes'),(566,1,'read'),(567,1,'stock'),(568,1,'weather'),(569,1,'reports'),(570,1,'music,'),(571,1,'movies,'),(572,1,'technology'),(573,1,'built'),(574,1,'gorgeous'),(575,1,'lets'),(576,1,'pinch,'),(577,1,'zoom,'),(578,1,'scroll,'),(579,1,'flick'),(580,1,'fingers'),(581,1,'internet'),(582,1,'pocket'),(583,1,'safari'),(584,1,'browser,'),(585,1,'websites'),(586,1,'they'),(587,1,'were'),(588,1,'seen'),(589,1,'zoom'),(590,1,'tap2'),(591,1,'home'),(592,1,'quick'),(593,1,'access'),(594,1,'sites'),(595,1,'what'),(596,1,'earphones'),(597,1,'cable'),(598,1,'dock'),(599,1,'polishing'),(600,1,'cloth'),(601,1,'stand'),(602,1,'start'),(603,1,'guide'),(604,1,'32go'),(605,1,'jack'),(606,1,'120g'),(607,1,'70mm'),(608,1,'110mm'),(609,2,'touch'),(610,2,'interface'),(611,2,'révolutionnaire'),(612,2,'couleur'),(613,2,'pouceswifi'),(614,2,'(80211b'),(615,2,'d\'épaisseursafa'),(616,2,'youtube,'),(617,2,'music'),(618,2,'store,'),(619,2,'courrier,'),(620,2,'cartes,'),(621,2,'bourse,'),(622,2,'météo,'),(623,2,'notes'),(624,2,'titre'),(625,2,'paragraphe'),(626,2,'cinq'),(627,2,'sous'),(628,2,'main'),(629,2,'consultez'),(630,2,'emails'),(631,2,'format'),(632,2,'html'),(633,2,'enrichi,'),(634,2,'photos'),(635,2,'pieces'),(636,2,'jointes'),(637,2,'pdf,'),(638,2,'word'),(639,2,'excel'),(640,2,'obtenez'),(641,2,'itinéraires'),(642,2,'informations'),(643,2,'l\'état'),(644,2,'circulation'),(645,2,'temps'),(646,2,'réel'),(647,2,'rédigez'),(648,2,'cours'),(649,2,'bourse'),(650,2,'bulletins'),(651,2,'météo'),(652,2,'touchez'),(653,2,'doigt'),(654,2,'entre'),(655,2,'autres'),(656,2,'technologie'),(657,2,'intégrée'),(658,2,'superbe'),(659,2,'pouces'),(660,2,'d\'effectuer'),(661,2,'zooms'),(662,2,'avant'),(663,2,'arrière,'),(664,2,'faire'),(665,2,'défiler'),(666,2,'feuilleter'),(667,2,'pages'),(668,2,'l\'aide'),(669,2,'seuls'),(670,2,'doigts'),(671,2,'internet'),(672,2,'poche'),(673,2,'navigateur'),(674,2,'safari,'),(675,2,'consulter'),(676,2,'sites'),(677,2,'leur'),(678,2,'mise'),(679,2,'page'),(680,2,'effectuer'),(681,2,'zoom'),(682,2,'arrière'),(683,2,'simple'),(684,2,'pression'),(685,2,'l\'écran'),(686,2,'contenu'),(687,2,'coffret'),(688,2,'écouteurs'),(689,2,'câble'),(690,2,'dock'),(691,2,'chiffon'),(692,2,'nettoyage'),(693,2,'support'),(694,2,'guide'),(695,2,'démarrage'),(696,2,'tacticle'),(697,2,'32go'),(698,2,'jack'),(699,2,'120g'),(700,2,'70mm'),(701,2,'110mm'),(702,1,'housse'),(703,1,'portefeuille'),(704,1,'cuir'),(705,1,'belkin'),(706,1,'pour'),(707,1,'noir'),(708,1,'chocolat'),(709,1,'lorem'),(710,1,'ipsum'),(711,1,'accessories'),(712,2,'housse'),(713,2,'portefeuille'),(714,2,'cuir'),(715,2,'(ipod'),(716,2,'nano)'),(717,2,'chocolat'),(718,2,'étui'),(719,2,'tendance'),(720,2,'assure'),(721,2,'protection'),(722,2,'complète'),(723,2,'contre'),(724,2,'éraflures'),(725,2,'petits'),(726,2,'aléas'),(727,2,'quotidienne'),(728,2,'conception'),(729,2,'élégante'),(730,2,'compacte'),(731,2,'glisser'),(732,2,'directement'),(733,2,'caractéristique'),(734,2,'doux'),(735,2,'accès'),(736,2,'bouton'),(737,2,'hold'),(738,2,'fermeture'),(739,2,'magnétique'),(740,2,'connector'),(741,2,'protègeécran'),(742,2,'accessoires'),(743,1,'shure'),(744,1,'se210'),(745,1,'soundisolating'),(746,1,'iphone'),(747,1,'evolved'),(748,1,'monitor'),(749,1,'roadtested'),(750,1,'musicians'),(751,1,'perfected'),(752,1,'engineers,'),(753,1,'lightweight'),(754,1,'stylish'),(755,1,'delivers'),(756,1,'fullrange'),(757,1,'audio'),(758,1,'that\'s'),(759,1,'free'),(760,1,'outside'),(761,1,'noise'),(762,1,'using'),(763,1,'hidefinition'),(764,1,'microspeakers'),(765,1,'deliver'),(766,1,'audio,'),(767,1,'ergonomic'),(768,1,'ideal'),(769,1,'premium'),(770,1,'onthego'),(771,1,'listening'),(772,1,'offer'),(773,1,'accurate'),(774,1,'reproduction'),(775,1,'both'),(776,1,'sourcesfor'),(777,1,'ultimate'),(778,1,'precision'),(779,1,'highs'),(780,1,'addition,'),(781,1,'flexible'),(782,1,'allows'),(783,1,'choose'),(784,1,'comfortable'),(785,1,'variety'),(786,1,'wearing'),(787,1,'positions'),(788,1,'microspeaker'),(789,1,'single'),(790,1,'balanced'),(791,1,'armature'),(792,1,'driver'),(793,1,'detachable,'),(794,1,'modular'),(795,1,'make'),(796,1,'longer'),(797,1,'shorter'),(798,1,'depending'),(799,1,'activity'),(800,1,'connector'),(801,1,'compatible'),(802,1,'earphone'),(803,1,'specifications'),(804,1,'speaker'),(805,1,'type'),(806,1,'frequency'),(807,1,'range'),(808,1,'25hz185khz'),(809,1,'impedance'),(810,1,'(1khz)'),(811,1,'ohms'),(812,1,'sensitivity'),(813,1,'(1mw)'),(814,1,'length'),(815,1,'(with'),(816,1,'extension)'),(817,1,'(540'),(818,1,'1371'),(819,1,'extension'),(820,1,'(360'),(821,1,'three'),(822,1,'pairs'),(823,1,'foam'),(824,1,'earpiece'),(825,1,'sleeves'),(826,1,'(small,'),(827,1,'medium,'),(828,1,'large)'),(829,1,'soft'),(830,1,'flex'),(831,1,'pair'),(832,1,'tripleflange'),(833,1,'carrying'),(834,1,'case'),(835,1,'warranty'),(836,1,'twoyear'),(837,1,'limited'),(838,1,'(for'),(839,1,'details,'),(840,1,'please'),(841,1,'visit'),(842,1,'wwwshurecom'),(843,1,'personalaudio'),(844,1,'customersupport'),(845,1,'productreturnsa'),(846,1,'indexhtm)'),(847,1,'se210aefs'),(848,1,'note'),(849,1,'products'),(850,1,'sold'),(851,1,'through'),(852,1,'this'),(853,1,'website'),(854,1,'bear'),(855,1,'brand'),(856,1,'name'),(857,1,'serviced'),(858,1,'supported'),(859,1,'exclusively'),(860,1,'their'),(861,1,'manufacturers'),(862,1,'accordance'),(863,1,'terms'),(864,1,'conditions'),(865,1,'packaged'),(866,1,'apple\'s'),(867,1,'does'),(868,1,'apply'),(869,1,'applebranded,'),(870,1,'even'),(871,1,'contact'),(872,1,'manufacturer'),(873,1,'directly'),(874,1,'technical'),(875,1,'support'),(876,1,'customer'),(877,1,'service'),(878,1,'incorporated'),(879,2,'isolation'),(880,2,'sonore'),(881,2,'shure'),(882,2,'se210'),(883,2,'ergonomiques'),(884,2,'légers'),(885,2,'offrent'),(886,2,'reproduction'),(887,2,'audio'),(888,2,'fidèle'),(889,2,'provenance'),(890,2,'sources'),(891,2,'salon'),(892,2,'basés'),(893,2,'moniteurs'),(894,2,'personnels'),(895,2,'testée'),(896,2,'route'),(897,2,'musiciens'),(898,2,'professionnels'),(899,2,'perfectionnée'),(900,2,'ingénieurs'),(901,2,'shure,'),(902,2,'se210,'),(903,2,'élégants,'),(904,2,'fournissent'),(905,2,'sortie'),(906,2,'gamme'),(907,2,'étendue'),(908,2,'exempte'),(909,2,'bruit'),(910,2,'externe'),(911,2,'embouts'),(912,2,'fournis'),(913,2,'bloquent'),(914,2,'ambiant'),(915,2,'combinés'),(916,2,'ergonomique'),(917,2,'séduisant'),(918,2,'modulaire,'),(919,2,'minimisent'),(920,2,'intrusions'),(921,2,'extérieur,'),(922,2,'permettant'),(923,2,'concentrer'),(924,2,'conçus'),(925,2,'amoureux'),(926,2,'souhaitent'),(927,2,'évoluer'),(928,2,'appareil'),(929,2,'portable,'),(930,2,'permettent'),(931,2,'d\'emmener'),(932,2,'performance'),(933,2,'microtransducte'),(934,2,'haute'),(935,2,'définition'),(936,2,'développés'),(937,2,'écoute'),(938,2,'qualité'),(939,2,'supérieure'),(940,2,'déplacement,'),(941,2,'utilisent'),(942,2,'transducteur'),(943,2,'armature'),(944,2,'équilibrée'),(945,2,'bénéficier'),(946,2,'confort'),(947,2,'d\'écoute'),(948,2,'époustouflant'),(949,2,'restitue'),(950,2,'tous'),(951,2,'détails'),(952,2,'spectacle'),(953,2,'live'),(954,2,'universel'),(955,2,'deluxe'),(956,2,'comprend'),(957,2,'éléments'),(958,2,'suivants'),(959,2,'inclus'),(960,2,'double'),(961,2,'rôle'),(962,2,'bloquer'),(963,2,'bruits'),(964,2,'ambiants'),(965,2,'garantir'),(966,2,'maintien'),(967,2,'personnalisés'),(968,2,'oreille'),(969,2,'différente,'),(970,2,'trois'),(971,2,'tailles'),(972,2,'d\'embouts'),(973,2,'mousse'),(974,2,'flexibles'),(975,2,'style'),(976,2,'d\'embout'),(977,2,'conviennent'),(978,2,'mieux'),(979,2,'bonne'),(980,2,'étanchéité'),(981,2,'facteur'),(982,2,'optimiser'),(983,2,'l\'isolation'),(984,2,'réponse'),(985,2,'basses,'),(986,2,'ainsi'),(987,2,'accroître'),(988,2,'prolongée'),(989,2,'modulaire'),(990,2,'basant'),(991,2,'commentaires'),(992,2,'nombreux'),(993,2,'utilisateurs,'),(994,2,'développé'),(995,2,'solution'),(996,2,'détachable'),(997,2,'permettre'),(998,2,'degré'),(999,2,'personnalisatio'),(1000,2,'précédent'),(1001,2,'mètre'),(1002,2,'fourni'),(1003,2,'d\'adapter'),(1004,2,'fonction'),(1005,2,'l\'activité'),(1006,2,'l\'application'),(1007,2,'transport'),(1008,2,'outre'),(1009,2,'compact'),(1010,2,'ranger'),(1011,2,'manière'),(1012,2,'pratique'),(1013,2,'encombres'),(1014,2,'garantie'),(1015,2,'limitée'),(1016,2,'deux'),(1017,2,'achetée'),(1018,2,'couverte'),(1019,2,'maind\'œuvre'),(1020,2,'anscaractéristi'),(1021,2,'techniques'),(1022,2,'type'),(1023,2,'sensibilité'),(1024,2,'acoustique'),(1025,2,'impédance'),(1026,2,'khz)'),(1027,2,'fréquences'),(1028,2,'longueur'),(1029,2,'rallonge'),(1030,2,'(embouts'),(1031,2,'sonore,'),(1032,2,'transport)'),(1033,2,'incorporated'),(1034,2,'casque'),(1035,2,'marche');
/*!40000 ALTER TABLE `ps_search_word` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_sekeyword`
--

DROP TABLE IF EXISTS `ps_sekeyword`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_sekeyword` (
  `id_sekeyword` int(10) unsigned NOT NULL auto_increment,
  `keyword` varchar(256) NOT NULL,
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_sekeyword`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_sekeyword`
--

LOCK TABLES `ps_sekeyword` WRITE;
/*!40000 ALTER TABLE `ps_sekeyword` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_sekeyword` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_state`
--

DROP TABLE IF EXISTS `ps_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
-- Table structure for table `ps_statssearch`
--

DROP TABLE IF EXISTS `ps_statssearch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_statssearch` (
  `id_statssearch` int(10) unsigned NOT NULL auto_increment,
  `keywords` varchar(255) NOT NULL,
  `results` int(6) NOT NULL default '0',
  `date_add` datetime NOT NULL,
  PRIMARY KEY  (`id_statssearch`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_statssearch`
--

LOCK TABLES `ps_statssearch` WRITE;
/*!40000 ALTER TABLE `ps_statssearch` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_statssearch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_subdomain`
--

DROP TABLE IF EXISTS `ps_subdomain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_subdomain` (
  `id_subdomain` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(16) NOT NULL,
  PRIMARY KEY  (`id_subdomain`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_subdomain`
--

LOCK TABLES `ps_subdomain` WRITE;
/*!40000 ALTER TABLE `ps_subdomain` DISABLE KEYS */;
INSERT INTO `ps_subdomain` VALUES (1,'www');
/*!40000 ALTER TABLE `ps_subdomain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_supplier`
--

DROP TABLE IF EXISTS `ps_supplier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_supplier` (
  `id_supplier` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `date_add` datetime NOT NULL,
  `date_upd` datetime NOT NULL,
  PRIMARY KEY  (`id_supplier`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_supplier`
--

LOCK TABLES `ps_supplier` WRITE;
/*!40000 ALTER TABLE `ps_supplier` DISABLE KEYS */;
INSERT INTO `ps_supplier` VALUES (1,'AppleStore','2010-06-08 14:08:09','2010-06-08 14:08:09'),(2,'Shure Online Store','2010-06-08 14:08:09','2010-06-08 14:08:09');
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
  `meta_title` varchar(254) default NULL,
  `meta_keywords` varchar(254) default NULL,
  `meta_description` varchar(254) default NULL,
  PRIMARY KEY  (`id_supplier`,`id_lang`)
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
-- Table structure for table `ps_tab`
--

DROP TABLE IF EXISTS `ps_tab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_tab` (
  `id_tab` int(10) unsigned NOT NULL auto_increment,
  `id_parent` int(11) NOT NULL,
  `class_name` varchar(64) NOT NULL,
  `module` varchar(64) default NULL,
  `position` int(10) unsigned NOT NULL,
  PRIMARY KEY  (`id_tab`)
) ENGINE=MyISAM AUTO_INCREMENT=69 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_tab`
--

LOCK TABLES `ps_tab` WRITE;
/*!40000 ALTER TABLE `ps_tab` DISABLE KEYS */;
INSERT INTO `ps_tab` VALUES (1,0,'AdminCatalog',NULL,1),(2,0,'AdminCustomers',NULL,2),(3,0,'AdminOrders',NULL,3),(4,0,'AdminPayment',NULL,4),(5,0,'AdminShipping',NULL,5),(6,0,'AdminStats',NULL,6),(7,0,'AdminModules',NULL,7),(29,0,'AdminEmployees',NULL,8),(8,0,'AdminPreferences',NULL,9),(9,0,'AdminTools',NULL,10),(60,1,'AdminTracking',NULL,1),(10,1,'AdminManufacturers',NULL,2),(34,1,'AdminSuppliers',NULL,3),(11,1,'AdminAttributesGroups',NULL,4),(36,1,'AdminFeatures',NULL,5),(58,1,'AdminScenes',NULL,6),(66,1,'AdminTags',NULL,7),(68,1,'AdminAttachments',NULL,7),(12,2,'AdminAddresses',NULL,1),(63,2,'AdminGroups',NULL,2),(65,2,'AdminCarts',NULL,3),(42,3,'AdminInvoices',NULL,1),(55,3,'AdminDeliverySlip',NULL,2),(47,3,'AdminReturn',NULL,3),(49,3,'AdminSlip',NULL,4),(59,3,'AdminMessages',NULL,5),(13,3,'AdminStatuses',NULL,6),(54,3,'AdminOrderMessage',NULL,7),(14,4,'AdminDiscounts',NULL,3),(15,4,'AdminCurrencies',NULL,1),(16,4,'AdminTaxes',NULL,2),(17,5,'AdminCarriers',NULL,1),(46,5,'AdminStates',NULL,2),(18,5,'AdminCountries',NULL,3),(19,5,'AdminZones',NULL,4),(20,5,'AdminRangePrice',NULL,5),(21,5,'AdminRangeWeight',NULL,6),(50,6,'AdminStatsModules',NULL,1),(51,6,'AdminStatsConf',NULL,2),(61,6,'AdminSearchEngines',NULL,3),(62,6,'AdminReferrers',NULL,4),(22,7,'AdminModulesPositions',NULL,1),(30,29,'AdminProfiles',NULL,1),(31,29,'AdminAccess',NULL,2),(28,29,'AdminContacts',NULL,3),(39,8,'AdminContact',NULL,1),(38,8,'AdminAppearance',NULL,2),(56,8,'AdminMeta',NULL,3),(27,8,'AdminPPreferences',NULL,4),(24,8,'AdminEmails',NULL,5),(26,8,'AdminImages',NULL,6),(23,8,'AdminDb',NULL,7),(48,8,'AdminPDF',NULL,8),(44,8,'AdminLocalization',NULL,9),(67,8,'AdminSearchConf',NULL,10),(32,9,'AdminLanguages',NULL,1),(33,9,'AdminTranslations',NULL,2),(35,9,'AdminTabs',NULL,3),(37,9,'AdminQuickAccesses',NULL,4),(40,9,'AdminAliases',NULL,5),(41,9,'AdminImport',NULL,6),(52,9,'AdminSubDomains',NULL,7),(53,9,'AdminBackup',NULL,8),(57,9,'AdminCMS',NULL,9),(64,9,'AdminGenerator',NULL,10),(43,-1,'AdminSearch',NULL,0);
/*!40000 ALTER TABLE `ps_tab` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_tab_lang`
--

DROP TABLE IF EXISTS `ps_tab_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_tab_lang` (
  `id_lang` int(10) unsigned NOT NULL,
  `id_tab` int(10) unsigned NOT NULL,
  `name` varchar(32) default NULL,
  PRIMARY KEY  (`id_tab`,`id_lang`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_tab_lang`
--

LOCK TABLES `ps_tab_lang` WRITE;
/*!40000 ALTER TABLE `ps_tab_lang` DISABLE KEYS */;
INSERT INTO `ps_tab_lang` VALUES (1,1,'Catalog'),(1,2,'Customers'),(1,3,'Orders'),(1,4,'Payment'),(1,5,'Shipping'),(1,6,'Stats'),(1,7,'Modules'),(1,8,'Preferences'),(1,9,'Tools'),(1,10,'Manufacturers'),(1,11,'Attributes and groups'),(1,12,'Addresses'),(1,13,'Statuses'),(1,14,'Vouchers'),(1,15,'Currencies'),(1,16,'Taxes'),(1,17,'Carriers'),(1,18,'Countries'),(1,19,'Zones'),(1,20,'Price ranges'),(1,21,'Weight ranges'),(1,22,'Positions'),(1,23,'Database'),(1,24,'Email'),(1,26,'Image'),(1,27,'Products'),(1,28,'Contacts'),(1,29,'Employees'),(1,30,'Profiles'),(1,31,'Permissions'),(1,32,'Languages'),(1,33,'Translations'),(1,34,'Suppliers'),(1,35,'Tabs'),(1,36,'Features'),(1,37,'Quick Accesses'),(1,38,'Appearance'),(1,39,'Contact'),(1,40,'Aliases'),(1,41,'Import'),(1,42,'Invoices'),(1,43,'Search'),(1,44,'Localization'),(1,46,'States'),(1,47,'Merchandise return'),(1,48,'PDF'),(1,49,'Credit slips'),(1,50,'Modules'),(1,51,'Settings'),(1,52,'Subdomains'),(1,53,'DB backup'),(1,54,'Order Messages'),(1,55,'Delivery slips'),(1,56,'Meta-Tags'),(1,57,'CMS'),(1,58,'Image mapping'),(1,59,'Customer messages'),(1,60,'Tracking'),(1,61,'Search engines'),(1,62,'Referrers'),(1,63,'Groups'),(1,64,'Generators'),(1,65,'Carts'),(1,66,'Tags'),(1,67,'Search'),(1,68,'Attachments'),(2,1,'Catalogue'),(2,2,'Clients'),(2,3,'Commandes'),(2,4,'Paiement'),(2,5,'Transport'),(2,6,'Stats'),(2,7,'Modules'),(2,8,'Préférences'),(2,9,'Outils'),(2,10,'Fabricants'),(2,11,'Attributs et groupes'),(2,12,'Adresses'),(2,13,'Statuts'),(2,14,'Bons de réduction'),(2,15,'Devises'),(2,16,'Taxes'),(2,17,'Transporteurs'),(2,18,'Pays'),(2,19,'Zones'),(2,20,'Tranches de prix'),(2,21,'Tranches de poids'),(2,22,'Positions'),(2,23,'Base de données'),(2,24,'Emails'),(2,26,'Images'),(2,27,'Produits'),(2,28,'Contacts'),(2,29,'Employés'),(2,30,'Profils'),(2,31,'Permissions'),(2,32,'Langues'),(2,33,'Traductions'),(2,34,'Fournisseurs'),(2,35,'Onglets'),(2,36,'Caractéristiques'),(2,37,'Accès rapide'),(2,38,'Apparence'),(2,39,'Coordonnées'),(2,40,'Alias'),(2,41,'Import'),(2,42,'Factures'),(2,43,'Recherche'),(2,44,'Localisation'),(2,46,'Etats'),(2,47,'Retours produits'),(2,48,'PDF'),(2,49,'Avoirs'),(2,50,'Modules'),(2,51,'Configuration'),(2,52,'Sous domaines'),(2,53,'Sauvegarde BDD'),(2,54,'Messages prédéfinis'),(2,55,'Bons de livraison'),(2,56,'Méta-Tags'),(2,57,'CMS'),(2,58,'Scènes'),(2,59,'Messages clients'),(2,60,'Suivi'),(2,61,'Moteurs de recherche'),(2,62,'Sites affluents'),(2,63,'Groupes'),(2,64,'Générateurs'),(2,65,'Paniers'),(2,66,'Tags'),(2,67,'Recherche'),(2,68,'Documents joints');
/*!40000 ALTER TABLE `ps_tab_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_tag`
--

DROP TABLE IF EXISTS `ps_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_tag` (
  `id_tag` int(10) unsigned NOT NULL auto_increment,
  `id_lang` int(10) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY  (`id_tag`),
  KEY `tag_name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_tag`
--

LOCK TABLES `ps_tag` WRITE;
/*!40000 ALTER TABLE `ps_tag` DISABLE KEYS */;
INSERT INTO `ps_tag` VALUES (5,1,'apple'),(6,2,'ipod'),(7,2,'nano'),(8,2,'apple'),(18,2,'shuffle'),(19,2,'macbook'),(20,2,'macbookair'),(21,2,'air'),(22,1,'superdrive'),(27,2,'marche'),(26,2,'casque'),(25,2,'écouteurs'),(24,2,'ipod touch tacticle'),(23,1,'Ipod touch');
/*!40000 ALTER TABLE `ps_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_tax`
--

DROP TABLE IF EXISTS `ps_tax`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_tax` (
  `id_tax` int(10) unsigned NOT NULL auto_increment,
  `rate` float NOT NULL,
  PRIMARY KEY  (`id_tax`)
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

--
-- Table structure for table `ps_tax_state`
--

DROP TABLE IF EXISTS `ps_tax_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_tax_state` (
  `id_tax` int(10) unsigned NOT NULL,
  `id_state` int(10) unsigned NOT NULL,
  KEY `tax_state_index` (`id_tax`,`id_state`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_tax_state`
--

LOCK TABLES `ps_tax_state` WRITE;
/*!40000 ALTER TABLE `ps_tax_state` DISABLE KEYS */;
/*!40000 ALTER TABLE `ps_tax_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_tax_zone`
--

DROP TABLE IF EXISTS `ps_tax_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_tax_zone` (
  `id_tax` int(10) unsigned NOT NULL,
  `id_zone` int(10) unsigned NOT NULL,
  KEY `tax_zone_index` (`id_tax`,`id_zone`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_tax_zone`
--

LOCK TABLES `ps_tax_zone` WRITE;
/*!40000 ALTER TABLE `ps_tax_zone` DISABLE KEYS */;
INSERT INTO `ps_tax_zone` VALUES (1,1),(2,1);
/*!40000 ALTER TABLE `ps_tax_zone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_timezone`
--

DROP TABLE IF EXISTS `ps_timezone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_timezone` (
  `id_timezone` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY  (`id_timezone`)
) ENGINE=MyISAM AUTO_INCREMENT=561 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_timezone`
--

LOCK TABLES `ps_timezone` WRITE;
/*!40000 ALTER TABLE `ps_timezone` DISABLE KEYS */;
INSERT INTO `ps_timezone` VALUES (1,'Africa/Abidjan'),(2,'Africa/Accra'),(3,'Africa/Addis_Ababa'),(4,'Africa/Algiers'),(5,'Africa/Asmara'),(6,'Africa/Asmera'),(7,'Africa/Bamako'),(8,'Africa/Bangui'),(9,'Africa/Banjul'),(10,'Africa/Bissau'),(11,'Africa/Blantyre'),(12,'Africa/Brazzaville'),(13,'Africa/Bujumbura'),(14,'Africa/Cairo'),(15,'Africa/Casablanca'),(16,'Africa/Ceuta'),(17,'Africa/Conakry'),(18,'Africa/Dakar'),(19,'Africa/Dar_es_Salaam'),(20,'Africa/Djibouti'),(21,'Africa/Douala'),(22,'Africa/El_Aaiun'),(23,'Africa/Freetown'),(24,'Africa/Gaborone'),(25,'Africa/Harare'),(26,'Africa/Johannesburg'),(27,'Africa/Kampala'),(28,'Africa/Khartoum'),(29,'Africa/Kigali'),(30,'Africa/Kinshasa'),(31,'Africa/Lagos'),(32,'Africa/Libreville'),(33,'Africa/Lome'),(34,'Africa/Luanda'),(35,'Africa/Lubumbashi'),(36,'Africa/Lusaka'),(37,'Africa/Malabo'),(38,'Africa/Maputo'),(39,'Africa/Maseru'),(40,'Africa/Mbabane'),(41,'Africa/Mogadishu'),(42,'Africa/Monrovia'),(43,'Africa/Nairobi'),(44,'Africa/Ndjamena'),(45,'Africa/Niamey'),(46,'Africa/Nouakchott'),(47,'Africa/Ouagadougou'),(48,'Africa/Porto-Novo'),(49,'Africa/Sao_Tome'),(50,'Africa/Timbuktu'),(51,'Africa/Tripoli'),(52,'Africa/Tunis'),(53,'Africa/Windhoek'),(54,'America/Adak'),(55,'America/Anchorage '),(56,'America/Anguilla'),(57,'America/Antigua'),(58,'America/Araguaina'),(59,'America/Argentina/Buenos_Aires'),(60,'America/Argentina/Catamarca'),(61,'America/Argentina/ComodRivadavia'),(62,'America/Argentina/Cordoba'),(63,'America/Argentina/Jujuy'),(64,'America/Argentina/La_Rioja'),(65,'America/Argentina/Mendoza'),(66,'America/Argentina/Rio_Gallegos'),(67,'America/Argentina/Salta'),(68,'America/Argentina/San_Juan'),(69,'America/Argentina/San_Luis'),(70,'America/Argentina/Tucuman'),(71,'America/Argentina/Ushuaia'),(72,'America/Aruba'),(73,'America/Asuncion'),(74,'America/Atikokan'),(75,'America/Atka'),(76,'America/Bahia'),(77,'America/Barbados'),(78,'America/Belem'),(79,'America/Belize'),(80,'America/Blanc-Sablon'),(81,'America/Boa_Vista'),(82,'America/Bogota'),(83,'America/Boise'),(84,'America/Buenos_Aires'),(85,'America/Cambridge_Bay'),(86,'America/Campo_Grande'),(87,'America/Cancun'),(88,'America/Caracas'),(89,'America/Catamarca'),(90,'America/Cayenne'),(91,'America/Cayman'),(92,'America/Chicago'),(93,'America/Chihuahua'),(94,'America/Coral_Harbour'),(95,'America/Cordoba'),(96,'America/Costa_Rica'),(97,'America/Cuiaba'),(98,'America/Curacao'),(99,'America/Danmarkshavn'),(100,'America/Dawson'),(101,'America/Dawson_Creek'),(102,'America/Denver'),(103,'America/Detroit'),(104,'America/Dominica'),(105,'America/Edmonton'),(106,'America/Eirunepe'),(107,'America/El_Salvador'),(108,'America/Ensenada'),(109,'America/Fort_Wayne'),(110,'America/Fortaleza'),(111,'America/Glace_Bay'),(112,'America/Godthab'),(113,'America/Goose_Bay'),(114,'America/Grand_Turk'),(115,'America/Grenada'),(116,'America/Guadeloupe'),(117,'America/Guatemala'),(118,'America/Guayaquil'),(119,'America/Guyana'),(120,'America/Halifax'),(121,'America/Havana'),(122,'America/Hermosillo'),(123,'America/Indiana/Indianapolis'),(124,'America/Indiana/Knox'),(125,'America/Indiana/Marengo'),(126,'America/Indiana/Petersburg'),(127,'America/Indiana/Tell_City'),(128,'America/Indiana/Vevay'),(129,'America/Indiana/Vincennes'),(130,'America/Indiana/Winamac'),(131,'America/Indianapolis'),(132,'America/Inuvik'),(133,'America/Iqaluit'),(134,'America/Jamaica'),(135,'America/Jujuy'),(136,'America/Juneau'),(137,'America/Kentucky/Louisville'),(138,'America/Kentucky/Monticello'),(139,'America/Knox_IN'),(140,'America/La_Paz'),(141,'America/Lima'),(142,'America/Los_Angeles'),(143,'America/Louisville'),(144,'America/Maceio'),(145,'America/Managua'),(146,'America/Manaus'),(147,'America/Marigot'),(148,'America/Martinique'),(149,'America/Mazatlan'),(150,'America/Mendoza'),(151,'America/Menominee'),(152,'America/Merida'),(153,'America/Mexico_City'),(154,'America/Miquelon'),(155,'America/Moncton'),(156,'America/Monterrey'),(157,'America/Montevideo'),(158,'America/Montreal'),(159,'America/Montserrat'),(160,'America/Nassau'),(161,'America/New_York'),(162,'America/Nipigon'),(163,'America/Nome'),(164,'America/Noronha'),(165,'America/North_Dakota/Center'),(166,'America/North_Dakota/New_Salem'),(167,'America/Panama'),(168,'America/Pangnirtung'),(169,'America/Paramaribo'),(170,'America/Phoenix'),(171,'America/Port-au-Prince'),(172,'America/Port_of_Spain'),(173,'America/Porto_Acre'),(174,'America/Porto_Velho'),(175,'America/Puerto_Rico'),(176,'America/Rainy_River'),(177,'America/Rankin_Inlet'),(178,'America/Recife'),(179,'America/Regina'),(180,'America/Resolute'),(181,'America/Rio_Branco'),(182,'America/Rosario'),(183,'America/Santarem'),(184,'America/Santiago'),(185,'America/Santo_Domingo'),(186,'America/Sao_Paulo'),(187,'America/Scoresbysund'),(188,'America/Shiprock'),(189,'America/St_Barthelemy'),(190,'America/St_Johns'),(191,'America/St_Kitts'),(192,'America/St_Lucia'),(193,'America/St_Thomas'),(194,'America/St_Vincent'),(195,'America/Swift_Current'),(196,'America/Tegucigalpa'),(197,'America/Thule'),(198,'America/Thunder_Bay'),(199,'America/Tijuana'),(200,'America/Toronto'),(201,'America/Tortola'),(202,'America/Vancouver'),(203,'America/Virgin'),(204,'America/Whitehorse'),(205,'America/Winnipeg'),(206,'America/Yakutat'),(207,'America/Yellowknife'),(208,'Antarctica/Casey'),(209,'Antarctica/Davis'),(210,'Antarctica/DumontDUrville'),(211,'Antarctica/Mawson'),(212,'Antarctica/McMurdo'),(213,'Antarctica/Palmer'),(214,'Antarctica/Rothera'),(215,'Antarctica/South_Pole'),(216,'Antarctica/Syowa'),(217,'Antarctica/Vostok'),(218,'Arctic/Longyearbyen'),(219,'Asia/Aden'),(220,'Asia/Almaty'),(221,'Asia/Amman'),(222,'Asia/Anadyr'),(223,'Asia/Aqtau'),(224,'Asia/Aqtobe'),(225,'Asia/Ashgabat'),(226,'Asia/Ashkhabad'),(227,'Asia/Baghdad'),(228,'Asia/Bahrain'),(229,'Asia/Baku'),(230,'Asia/Bangkok'),(231,'Asia/Beirut'),(232,'Asia/Bishkek'),(233,'Asia/Brunei'),(234,'Asia/Calcutta'),(235,'Asia/Choibalsan'),(236,'Asia/Chongqing'),(237,'Asia/Chungking'),(238,'Asia/Colombo'),(239,'Asia/Dacca'),(240,'Asia/Damascus'),(241,'Asia/Dhaka'),(242,'Asia/Dili'),(243,'Asia/Dubai'),(244,'Asia/Dushanbe'),(245,'Asia/Gaza'),(246,'Asia/Harbin'),(247,'Asia/Ho_Chi_Minh'),(248,'Asia/Hong_Kong'),(249,'Asia/Hovd'),(250,'Asia/Irkutsk'),(251,'Asia/Istanbul'),(252,'Asia/Jakarta'),(253,'Asia/Jayapura'),(254,'Asia/Jerusalem'),(255,'Asia/Kabul'),(256,'Asia/Kamchatka'),(257,'Asia/Karachi'),(258,'Asia/Kashgar'),(259,'Asia/Kathmandu'),(260,'Asia/Katmandu'),(261,'Asia/Kolkata'),(262,'Asia/Krasnoyarsk'),(263,'Asia/Kuala_Lumpur'),(264,'Asia/Kuching'),(265,'Asia/Kuwait'),(266,'Asia/Macao'),(267,'Asia/Macau'),(268,'Asia/Magadan'),(269,'Asia/Makassar'),(270,'Asia/Manila'),(271,'Asia/Muscat'),(272,'Asia/Nicosia'),(273,'Asia/Novosibirsk'),(274,'Asia/Omsk'),(275,'Asia/Oral'),(276,'Asia/Phnom_Penh'),(277,'Asia/Pontianak'),(278,'Asia/Pyongyang'),(279,'Asia/Qatar'),(280,'Asia/Qyzylorda'),(281,'Asia/Rangoon'),(282,'Asia/Riyadh'),(283,'Asia/Saigon'),(284,'Asia/Sakhalin'),(285,'Asia/Samarkand'),(286,'Asia/Seoul'),(287,'Asia/Shanghai'),(288,'Asia/Singapore'),(289,'Asia/Taipei'),(290,'Asia/Tashkent'),(291,'Asia/Tbilisi'),(292,'Asia/Tehran'),(293,'Asia/Tel_Aviv'),(294,'Asia/Thimbu'),(295,'Asia/Thimphu'),(296,'Asia/Tokyo'),(297,'Asia/Ujung_Pandang'),(298,'Asia/Ulaanbaatar'),(299,'Asia/Ulan_Bator'),(300,'Asia/Urumqi'),(301,'Asia/Vientiane'),(302,'Asia/Vladivostok'),(303,'Asia/Yakutsk'),(304,'Asia/Yekaterinburg'),(305,'Asia/Yerevan'),(306,'Atlantic/Azores'),(307,'Atlantic/Bermuda'),(308,'Atlantic/Canary'),(309,'Atlantic/Cape_Verde'),(310,'Atlantic/Faeroe'),(311,'Atlantic/Faroe'),(312,'Atlantic/Jan_Mayen'),(313,'Atlantic/Madeira'),(314,'Atlantic/Reykjavik'),(315,'Atlantic/South_Georgia'),(316,'Atlantic/St_Helena'),(317,'Atlantic/Stanley'),(318,'Australia/ACT'),(319,'Australia/Adelaide'),(320,'Australia/Brisbane'),(321,'Australia/Broken_Hill'),(322,'Australia/Canberra'),(323,'Australia/Currie'),(324,'Australia/Darwin'),(325,'Australia/Eucla'),(326,'Australia/Hobart'),(327,'Australia/LHI'),(328,'Australia/Lindeman'),(329,'Australia/Lord_Howe'),(330,'Australia/Melbourne'),(331,'Australia/North'),(332,'Australia/NSW'),(333,'Australia/Perth'),(334,'Australia/Queensland'),(335,'Australia/South'),(336,'Australia/Sydney'),(337,'Australia/Tasmania'),(338,'Australia/Victoria'),(339,'Australia/West'),(340,'Australia/Yancowinna'),(341,'Europe/Amsterdam'),(342,'Europe/Andorra'),(343,'Europe/Athens'),(344,'Europe/Belfast'),(345,'Europe/Belgrade'),(346,'Europe/Berlin'),(347,'Europe/Bratislava'),(348,'Europe/Brussels'),(349,'Europe/Bucharest'),(350,'Europe/Budapest'),(351,'Europe/Chisinau'),(352,'Europe/Copenhagen'),(353,'Europe/Dublin'),(354,'Europe/Gibraltar'),(355,'Europe/Guernsey'),(356,'Europe/Helsinki'),(357,'Europe/Isle_of_Man'),(358,'Europe/Istanbul'),(359,'Europe/Jersey'),(360,'Europe/Kaliningrad'),(361,'Europe/Kiev'),(362,'Europe/Lisbon'),(363,'Europe/Ljubljana'),(364,'Europe/London'),(365,'Europe/Luxembourg'),(366,'Europe/Madrid'),(367,'Europe/Malta'),(368,'Europe/Mariehamn'),(369,'Europe/Minsk'),(370,'Europe/Monaco'),(371,'Europe/Moscow'),(372,'Europe/Nicosia'),(373,'Europe/Oslo'),(374,'Europe/Paris'),(375,'Europe/Podgorica'),(376,'Europe/Prague'),(377,'Europe/Riga'),(378,'Europe/Rome'),(379,'Europe/Samara'),(380,'Europe/San_Marino'),(381,'Europe/Sarajevo'),(382,'Europe/Simferopol'),(383,'Europe/Skopje'),(384,'Europe/Sofia'),(385,'Europe/Stockholm'),(386,'Europe/Tallinn'),(387,'Europe/Tirane'),(388,'Europe/Tiraspol'),(389,'Europe/Uzhgorod'),(390,'Europe/Vaduz'),(391,'Europe/Vatican'),(392,'Europe/Vienna'),(393,'Europe/Vilnius'),(394,'Europe/Volgograd'),(395,'Europe/Warsaw'),(396,'Europe/Zagreb'),(397,'Europe/Zaporozhye'),(398,'Europe/Zurich'),(399,'Indian/Antananarivo'),(400,'Indian/Chagos'),(401,'Indian/Christmas'),(402,'Indian/Cocos'),(403,'Indian/Comoro'),(404,'Indian/Kerguelen'),(405,'Indian/Mahe'),(406,'Indian/Maldives'),(407,'Indian/Mauritius'),(408,'Indian/Mayotte'),(409,'Indian/Reunion'),(410,'Pacific/Apia'),(411,'Pacific/Auckland'),(412,'Pacific/Chatham'),(413,'Pacific/Easter'),(414,'Pacific/Efate'),(415,'Pacific/Enderbury'),(416,'Pacific/Fakaofo'),(417,'Pacific/Fiji'),(418,'Pacific/Funafuti'),(419,'Pacific/Galapagos'),(420,'Pacific/Gambier'),(421,'Pacific/Guadalcanal'),(422,'Pacific/Guam'),(423,'Pacific/Honolulu'),(424,'Pacific/Johnston'),(425,'Pacific/Kiritimati'),(426,'Pacific/Kosrae'),(427,'Pacific/Kwajalein'),(428,'Pacific/Majuro'),(429,'Pacific/Marquesas'),(430,'Pacific/Midway'),(431,'Pacific/Nauru'),(432,'Pacific/Niue'),(433,'Pacific/Norfolk'),(434,'Pacific/Noumea'),(435,'Pacific/Pago_Pago'),(436,'Pacific/Palau'),(437,'Pacific/Pitcairn'),(438,'Pacific/Ponape'),(439,'Pacific/Port_Moresby'),(440,'Pacific/Rarotonga'),(441,'Pacific/Saipan'),(442,'Pacific/Samoa'),(443,'Pacific/Tahiti'),(444,'Pacific/Tarawa'),(445,'Pacific/Tongatapu'),(446,'Pacific/Truk'),(447,'Pacific/Wake'),(448,'Pacific/Wallis'),(449,'Pacific/Yap'),(450,'Brazil/Acre'),(451,'Brazil/DeNoronha'),(452,'Brazil/East'),(453,'Brazil/West'),(454,'Canada/Atlantic'),(455,'Canada/Central'),(456,'Canada/East-Saskatchewan'),(457,'Canada/Eastern'),(458,'Canada/Mountain'),(459,'Canada/Newfoundland'),(460,'Canada/Pacific'),(461,'Canada/Saskatchewan'),(462,'Canada/Yukon'),(463,'CET'),(464,'Chile/Continental'),(465,'Chile/EasterIsland'),(466,'CST6CDT'),(467,'Cuba'),(468,'EET'),(469,'Egypt'),(470,'Eire'),(471,'EST'),(472,'EST5EDT'),(473,'Etc/GMT'),(474,'Etc/GMT+0'),(475,'Etc/GMT+1'),(476,'Etc/GMT+10'),(477,'Etc/GMT+11'),(478,'Etc/GMT+12'),(479,'Etc/GMT+2'),(480,'Etc/GMT+3'),(481,'Etc/GMT+4'),(482,'Etc/GMT+5'),(483,'Etc/GMT+6'),(484,'Etc/GMT+7'),(485,'Etc/GMT+8'),(486,'Etc/GMT+9'),(487,'Etc/GMT-0'),(488,'Etc/GMT-1'),(489,'Etc/GMT-10'),(490,'Etc/GMT-11'),(491,'Etc/GMT-12'),(492,'Etc/GMT-13'),(493,'Etc/GMT-14'),(494,'Etc/GMT-2'),(495,'Etc/GMT-3'),(496,'Etc/GMT-4'),(497,'Etc/GMT-5'),(498,'Etc/GMT-6'),(499,'Etc/GMT-7'),(500,'Etc/GMT-8'),(501,'Etc/GMT-9'),(502,'Etc/GMT0'),(503,'Etc/Greenwich'),(504,'Etc/UCT'),(505,'Etc/Universal'),(506,'Etc/UTC'),(507,'Etc/Zulu'),(508,'Factory'),(509,'GB'),(510,'GB-Eire'),(511,'GMT'),(512,'GMT+0'),(513,'GMT-0'),(514,'GMT0'),(515,'Greenwich'),(516,'Hongkong'),(517,'HST'),(518,'Iceland'),(519,'Iran'),(520,'Israel'),(521,'Jamaica'),(522,'Japan'),(523,'Kwajalein'),(524,'Libya'),(525,'MET'),(526,'Mexico/BajaNorte'),(527,'Mexico/BajaSur'),(528,'Mexico/General'),(529,'MST'),(530,'MST7MDT'),(531,'Navajo'),(532,'NZ'),(533,'NZ-CHAT'),(534,'Poland'),(535,'Portugal'),(536,'PRC'),(537,'PST8PDT'),(538,'ROC'),(539,'ROK'),(540,'Singapore'),(541,'Turkey'),(542,'UCT'),(543,'Universal'),(544,'US/Alaska'),(545,'US/Aleutian'),(546,'US/Arizona'),(547,'US/Central'),(548,'US/East-Indiana'),(549,'US/Eastern'),(550,'US/Hawaii'),(551,'US/Indiana-Starke'),(552,'US/Michigan'),(553,'US/Mountain'),(554,'US/Pacific'),(555,'US/Pacific-New'),(556,'US/Samoa'),(557,'UTC'),(558,'W-SU'),(559,'WET'),(560,'Zulu');
/*!40000 ALTER TABLE `ps_timezone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_web_browser`
--

DROP TABLE IF EXISTS `ps_web_browser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_web_browser` (
  `id_web_browser` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) default NULL,
  PRIMARY KEY  (`id_web_browser`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ps_web_browser`
--

LOCK TABLES `ps_web_browser` WRITE;
/*!40000 ALTER TABLE `ps_web_browser` DISABLE KEYS */;
INSERT INTO `ps_web_browser` VALUES (1,'Safari'),(2,'Firefox 2.x'),(3,'Firefox 3.x'),(4,'Opera'),(5,'IE 6.x'),(6,'IE 7.x'),(7,'IE 8.x'),(8,'Google Chrome');
/*!40000 ALTER TABLE `ps_web_browser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ps_zone`
--

DROP TABLE IF EXISTS `ps_zone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ps_zone` (
  `id_zone` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(64) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL default '0',
  `enabled` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id_zone`)
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

-- Dump completed on 2010-06-08 14:09:22
