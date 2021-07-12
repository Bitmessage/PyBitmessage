DROP TABLE `inventory`;

CREATE TABLE IF NOT EXISTS `inventory` (
  `hash` blob NOT NULL,
  `objecttype` int DEFAULT NULL,
  `streamnumber` int NOT NULL,
  `payload` blob DEFAULT NULL,
  `integer` integer NOT NULL,
  UNIQUE(hash) ON CONFLICT REPLACE
) ;

INSERT INTO `inventory` VALUES ('hash', 1, 1, 1,'test');

CREATE TABLE IF NOT EXISTS `pubkeys` (
  `hash` text,
  `addressversion` int,
  `transmitdata` blob,
  `time` int,
  `usedpersonally` text,
  UNIQUE(hash) ON CONFLICT REPLACE
) ;

INSERT INTO `pubkeys` VALUES ('hash','1','1','1','test');

CREATE TABLE IF NOT EXISTS `sent` (
  `msgid` blob DEFAULT NULL,
  `toaddress` text DEFAULT NULL,
  `toripe` blob DEFAULT NULL,
  `fromaddress` text DEFAULT NULL,
  `subject` text DEFAULT NULL,
  `message` text DEFAULT NULL,
  `ackdata` blob DEFAULT NULL,
  `senttime` integer DEFAULT NULL,
  `lastactiontime` integer DEFAULT NULL,
  `sleeptill` integer DEFAULT NULL,
  `status` text DEFAULT NULL,
  `retrynumber` integer DEFAULT NULL,
  `folder` text DEFAULT NULL,
  `encodingtype` int DEFAULT NULL,
  `ttl` int DEFAULT NULL
) ;

INSERT INTO `sent` VALUES
('msgid','toaddress','toripe','fromaddress','subject','message','ackdata','senttime','lastactiontime','sleeptill','doingmsgpow','retrynumber','folder','encodingtype','ttl'),
('msgid','toaddress','toripe','fromaddress','subject','message','ackdata','senttime','lastactiontime','sleeptill','badkey','retrynumber','folder','encodingtype','ttl');
