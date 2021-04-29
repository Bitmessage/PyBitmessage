CREATE TEMPORARY TABLE `pubkeys_backup` (
    `address` text DEFAULT NULL,
    `addressversion` int DEFAULT NULL,
    `transmitdata` blob DEFAULT NULL,
    `time` int DEFAULT NULL,
    `usedpersonally` text DEFAULT NULL,
    UNIQUE(address) ON CONFLICT REPLACE
) ;

INSERT INTO pubkeys_backup SELECT address, addressversion, transmitdata, time, usedpersonally FROM pubkeys;

DROP TABLE pubkeys;

CREATE TABLE `pubkeys` (
    `address` text DEFAULT NULL,
    `addressversion` int DEFAULT NULL,
    `transmitdata` blob DEFAULT NULL,
    `time` int DEFAULT NULL,
    `usedpersonally` text DEFAULT NULL,
    UNIQUE(address) ON CONFLICT REPLACE
);

INSERT INTO pubkeys SELECT address, addressversion, transmitdata, time, usedpersonally FROM pubkeys_backup;

DROP TABLE pubkeys_backup;