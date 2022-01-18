 --
 -- Add a new column to the pubkeys table to store the address version.
 -- We're going to trash all of our pubkeys and let them be redownloaded.
 --

DROP TABLE pubkeys;

CREATE TABLE `pubkeys` (
    `hash` blob ,
    `addressversion` int ,
    `transmitdata` blob ,
    `time` int ,
    `usedpersonally` text ,
    UNIQUE(hash, addressversion) ON CONFLICT REPLACE
) ;

DELETE FROM inventory WHERE objecttype = 'pubkey';
