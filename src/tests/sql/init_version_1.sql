CREATE TABLE IF NOT EXISTS `settings` (
  `key` blob NOT NULL,
  `value` text DEFAULT NULL,
  UNIQUE(key) ON CONFLICT REPLACE
) ;

INSERT INTO `settings` VALUES ('version','1');

CREATE TABLE IF NOT EXISTS `inventory` (
  `hash` blob NOT NULL,
  `objecttype` int DEFAULT NULL,
  `streamnumber` int NOT NULL,
  `payload` blob DEFAULT NULL,
  `integer` integer NOT NULL,
  UNIQUE(hash) ON CONFLICT REPLACE
) ;