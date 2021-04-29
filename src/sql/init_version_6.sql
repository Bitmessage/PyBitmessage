-- --
-- -- Drop table `inventory`
-- --

    DROP TABLE inventory;


-- --
-- --  Table structure for table `inventory`
-- --


CREATE TABLE `inventory` (
    `hash` blob NOT NULL,
    `objecttype` int DEFAULT NULL,
    `streamnumber` int NOT NULL,
    `payload` blob NOT NULL,
    `expirestime` integer DEFAULT NULL,
    `tag` blob DEFAULT NULL,
    UNIQUE(hash) ON CONFLICT REPLACE
) ;

-- --
-- -- Drop table `inventory`
-- --

    DROP TABLE objectprocessorqueue;


-- --
-- --  Table structure for table `objectprocessorqueue`
-- --


CREATE TABLE `objectprocessorqueue` (
    `objecttype` int DEFAULT NULL,
    `data` blob DEFAULT NULL,
    UNIQUE(objecttype, data) ON CONFLICT REPLACE
) ;
