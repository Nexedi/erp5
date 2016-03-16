# Host:
# Database: test
# Table: 'compatibility'
#
CREATE TABLE `compatibility` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `Creator` varchar(255) default '',
  `Date` datetime default '0000-00-00 00:00:00',
  `PrincipiaSearchSource` text,
  `SearchableText` text,
  `CreationDate` datetime default '0000-00-00 00:00:00',
  `EffectiveDate` datetime default '0000-00-00 00:00:00',
  `ExpiresDate` datetime default '0000-00-00 00:00:00',
  `ModificationDate` datetime default '0000-00-00 00:00:00',
  `Type` varchar(255) default '',
  `bobobase_modification_time` datetime default '0000-00-00 00:00:00',
  `created` datetime default '0000-00-00 00:00:00',
  `effective` datetime default '0000-00-00 00:00:00',
  `expires` datetime default '0000-00-00 00:00:00',
  `getIcon` varchar(255) default '',
  `in_reply_to` varchar(255) default '',
  `modified` datetime default '0000-00-00 00:00:00',
  `review_state` varchar(255) default '',
  `summary` text,
  PRIMARY KEY  (`uid`),
  KEY `Type` (`Type`),
  KEY `review_state` (`review_state`)
) TYPE=ndb;
