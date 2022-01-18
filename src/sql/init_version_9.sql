CREATE TEMPORARY TABLE `sent_backup` (
    `msgid` blob,
    `toaddress` text,
    `toripe` blob,
    `fromaddress` text,
    `subject` text,
    `message` text,
    `ackdata` blob,
    `lastactiontime` integer,
    `status` text,
    `retrynumber` integer,
    `folder` text,
    `encodingtype` int
) ;

INSERT INTO sent_backup SELECT msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, 0, folder, encodingtype FROM sent;

DROP TABLE sent;

CREATE TABLE `sent` (
    `msgid` blob,
    `toaddress` text,
    `toripe` blob,
    `fromaddress` text,
    `subject` text,
    `message` text,
    `ackdata` blob,
    `senttime` integer,
    `lastactiontime` integer,
    `sleeptill` int,
    `status` text,
    `retrynumber` integer,
    `folder` text,
    `encodingtype` int,
    `ttl` int
) ;

INSERT INTO sent SELECT msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, lastactiontime, 0, status, 0, folder, encodingtype, 216000 FROM sent_backup;

DROP TABLE sent_backup;

ALTER TABLE pubkeys ADD address text DEFAULT '' ;

--
-- replica for loop to update hashed address
--

UPDATE pubkeys SET address=(enaddr(pubkeys.addressversion, 1, hash));

CREATE TEMPORARY TABLE `pubkeys_backup` (
    `address` text,
    `addressversion` int,
    `transmitdata` blob,
    `time` int,
    `usedpersonally` text,
    UNIQUE(address) ON CONFLICT REPLACE
) ;

INSERT INTO pubkeys_backup SELECT address, addressversion, transmitdata, `time`, usedpersonally FROM pubkeys;

DROP TABLE pubkeys;

CREATE TABLE `pubkeys` (
    `address` text,
    `addressversion` int,
    `transmitdata` blob,
    `time` int,
    `usedpersonally` text,
    UNIQUE(address) ON CONFLICT REPLACE
) ;

INSERT INTO pubkeys SELECT address, addressversion, transmitdata, `time`, usedpersonally FROM pubkeys_backup;

DROP TABLE pubkeys_backup;
