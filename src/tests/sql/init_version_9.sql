--
-- Table structure for table `sent`
--


CREATE TABLE IF NOT EXISTS `sent` (
  `msgid` blob NOT NULL,
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
  `ttl` int DEFAULT NULL,
  UNIQUE(msgid) ON CONFLICT REPLACE
) ;


--
-- Table structure for table `pubkeys`
--

CREATE TABLE IF NOT EXISTS `pubkeys` (
  `hash` text,
  `addressversion` int,
  `transmitdata` blob,
  `time` int,
  `usedpersonally` text,
  UNIQUE(hash) ON CONFLICT REPLACE
) ;
