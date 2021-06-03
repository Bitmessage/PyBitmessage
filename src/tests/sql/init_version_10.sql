CREATE TABLE IF NOT EXISTS `addressbook` (
  `label` blob NOT NULL,
  `address` text DEFAULT NULL,
  UNIQUE(address) ON CONFLICT IGNORE
) ;

ALTER TABLE addressbook RENAME TO old_addressbook;

CREATE TABLE IF NOT EXISTS `addressbook` (
  `label` text NOT NULL,
  `address` text DEFAULT NULL,
  UNIQUE(address) ON CONFLICT IGNORE
) ;

INSERT INTO addressbook SELECT label, address FROM old_addressbook;

DROP TABLE old_addressbook;
