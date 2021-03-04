--
-- Table structure for table `settings`
--

CREATE TABLE IF NOT EXISTS `settings` (
  `key` blob NOT NULL,
  `value` text DEFAULT NULL,
  UNIQUE(key) ON CONFLICT REPLACE
) ;


--
-- Dumping data for table `settings`
--


INSERT INTO `settings` VALUES ('version','1');

--
-- Table structure for table `inventory`
--

CREATE TABLE IF NOT EXISTS `inventory` (
  `hash` blob NOT NULL,
  `objecttype` int DEFAULT NULL,
  `streamnumber` int NOT NULL,
  `payload` blob DEFAULT NULL,
  `integer` integer NOT NULL,
  -- `tag` blob DEFAULT NULL,
  UNIQUE(hash) ON CONFLICT REPLACE
) ;
