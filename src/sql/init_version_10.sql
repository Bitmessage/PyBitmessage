-- --
-- --  Update the address colunm to unique in addressbook table
-- --

ALTER TABLE addressbook RENAME TO old_addressbook;

CREATE TABLE `addressbook` (
    `label` text ,
    `address` text ,
    UNIQUE(address) ON CONFLICT IGNORE
) ;

INSERT INTO addressbook SELECT label, address FROM old_addressbook;

DROP TABLE old_addressbook;
