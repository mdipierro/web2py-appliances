DROP TABLE IF EXISTS `wwwsqldesigner`;
CREATE TABLE `wwwsqldesigner` (
  `keyword` varchar(20) NOT NULL default '',
  `data` mediumtext NOT NULL,
  `dt` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`keyword`)
);
