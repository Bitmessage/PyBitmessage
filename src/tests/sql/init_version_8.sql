CREATE TABLE IF NOT EXISTS `inbox` (
  `msgid` blob NOT NULL,
  `toaddress` text DEFAULT NULL,
  `fromaddress` text DEFAULT NULL,
  `subject` text DEFAULT NULL,
  `received` text DEFAULT NULL,
  `message` text DEFAULT NULL,
  `folder` text DEFAULT NULL,
  `encodingtype` int DEFAULT NULL,
  `read` bool DEFAULT NULL,
  UNIQUE(msgid) ON CONFLICT REPLACE
) ;
