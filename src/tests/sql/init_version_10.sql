--
-- Table structure for table `addressbook`
--

CREATE TABLE IF NOT EXISTS `addressbook` (
  `label` blob NOT NULL,
  `address` text DEFAULT NULL,
  UNIQUE(address) ON CONFLICT IGNORE
) ;

--
-- Alter table `addressbook`
--

ALTER TABLE addressbook RENAME TO old_addressbook;


--
-- Table structure for table `addressbook`
--

CREATE TABLE IF NOT EXISTS `addressbook` (
  `label` text NOT NULL,
  `address` text DEFAULT NULL,
  UNIQUE(address) ON CONFLICT IGNORE
) ;


--
-- Insert data into table `addressbook`
--

INSERT INTO addressbook SELECT label, address FROM old_addressbook;


--
-- Insert data into table `addressbook`
--

DROP TABLE old_addressbook;
