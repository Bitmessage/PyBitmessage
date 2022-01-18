CREATE TEMPORARY TABLE `pubkeys_backup` (
    `hash` blob,
    `transmitdata` blob,
    `time` int,
    `usedpersonally` text,
    UNIQUE(hash) ON CONFLICT REPLACE
) ;

INSERT INTO `pubkeys_backup` SELECT hash, transmitdata, `time`, usedpersonally FROM `pubkeys`;

DROP TABLE `pubkeys`

CREATE TABLE `pubkeys` (
    `hash` blob,
    `transmitdata` blob,
    `time` int,
    `usedpersonally` text,
    UNIQUE(hash) ON CONFLICT REPLACE
) ;


INSERT INTO `pubkeys` SELECT hash, transmitdata, `time`, usedpersonally FROM `pubkeys_backup`;

DROP TABLE `pubkeys_backup`;

DELETE FROM inventory WHERE objecttype = 'pubkey';

DELETE FROM subscriptions WHERE address='BM-BbkPSZbzPwpVcYZpU4yHwf9ZPEapN5Zx'

INSERT INTO subscriptions VALUES('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1)
