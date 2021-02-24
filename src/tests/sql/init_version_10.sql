--
-- Table structure for table `addressbook`
--

CREATE TABLE IF NOT EXISTS `addressbook` (
  `label` blob NOT NULL,
  `address` text DEFAULT NULL,
  UNIQUE(address) ON CONFLICT IGNORE
) ;
