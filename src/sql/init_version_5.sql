 --
 -- Add a new table: objectprocessorqueue with which to hold objects
 -- that have yet to be processed if the user shuts down Bitmessage.
 --

DROP TABLE knownnodes;

CREATE TABLE `objectprocessorqueue` (
    `objecttype` text,
    `data` blob,
    UNIQUE(objecttype, data) ON CONFLICT REPLACE
) ;
