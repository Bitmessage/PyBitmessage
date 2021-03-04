-- --
-- -- Alter table `addressbook`
-- --

ALTER TABLE addressbook RENAME TO old_addressbook;



-- --
-- --  Table structure for table `addressbook`
-- --


CREATE TABLE `addressbook` (
    `label` text NOT NULL,
    `address` text NOT NULL,
    UNIQUE(address) ON CONFLICT IGNORE
) ;


-- --
-- -- Dumping data for table `addressbook`
-- --

INSERT INTO addressbook SELECT label, address FROM old_addressbook;


-- --
-- -- Drop table `old_addressbook`
-- --

DROP TABLE old_addressbook;
