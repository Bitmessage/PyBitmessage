--
-- Let's get rid of the first20bytesofencryptedmessage field in the inventory table.
--

CREATE TEMP TABLE `inventory_backup` (
    `hash` blob ,
    `objecttype` text ,
    `streamnumber` int ,
    `payload` blob ,
    `receivedtime` int ,
    UNIQUE(hash) ON CONFLICT REPLACE
) ;

INSERT INTO `inventory_backup` SELECT  hash, objecttype, streamnumber, payload, receivedtime FROM inventory;

DROP TABLE inventory;

CREATE TABLE `inventory` (
    `hash` blob ,
    `objecttype` text ,
    `streamnumber` int ,
    `payload` blob ,
    `receivedtime` int ,
    UNIQUE(hash) ON CONFLICT REPLACE
) ;

INSERT INTO inventory SELECT hash, objecttype, streamnumber, payload, receivedtime FROM inventory_backup;

DROP TABLE inventory_backup;
