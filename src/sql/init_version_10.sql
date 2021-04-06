ALTER TABLE addressbook RENAME TO old_addressbook;

CREATE TABLE `addressbook` (
    `label` text NOT NULL,
    `address` text NOT NULL,
    UNIQUE(address) ON CONFLICT IGNORE
) ;


INSERT INTO addressbook SELECT label, address FROM old_addressbook;

DROP TABLE old_addressbook;
