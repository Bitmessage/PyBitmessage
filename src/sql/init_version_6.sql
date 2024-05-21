--
-- changes related to protocol v3
-- In table inventory and objectprocessorqueue, objecttype is now
-- an integer (it was a human-friendly string previously)
--

DROP TABLE inventory;

CREATE TABLE `inventory` (
    `hash` blob,
    `objecttype` int,
    `streamnumber` int,
    `payload` blob,
    `expirestime` integer,
    `tag` blob,
    UNIQUE(hash) ON CONFLICT REPLACE
) ;

DROP TABLE objectprocessorqueue;

CREATE TABLE `objectprocessorqueue` (
    `objecttype` int,
    `data` blob,
    UNIQUE(objecttype, data) ON CONFLICT REPLACE
) ;
