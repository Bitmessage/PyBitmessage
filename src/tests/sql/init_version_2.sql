--
-- Table structure for table `inventory`
--

CREATE TABLE IF NOT EXISTS `inventory` (
  `hash` blob NOT NULL,
  `objecttype` int DEFAULT NULL,
  `streamnumber` int NOT NULL,
  `receivedtime` int NOT NULL,
  `payload` blob DEFAULT NULL,
  `integer` integer NOT NULL,
  -- `tag` blob DEFAULT NULL,
  UNIQUE(hash) ON CONFLICT REPLACE
) ;

--
-- Dumping data for table `inventory`
--

INSERT INTO `inventory` VALUES ('hash', 1, 1,1, 1,'test');
