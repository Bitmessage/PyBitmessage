-- --
-- --  Table structure for table `sent_backup`
-- --


CREATE TEMPORARY TABLE `sent_backup` (
    `msgid` blob DEFAULT NULL,
    `toaddress` text DEFAULT NULL,
    `toripe` blob DEFAULT NULL,
    `fromaddress` text DEFAULT NULL,
    `subject` text DEFAULT NULL,
    `message` text DEFAULT NULL,
    `ackdata` blob DEFAULT NULL,
    `lastactiontime` integer DEFAULT NULL,
    `status` text DEFAULT NULL,
    `retrynumber` integer DEFAULT NULL,
    `folder` text DEFAULT NULL,
    `encodingtype` int DEFAULT NULL
) ;


 -- --
 -- -- Dumping data for table `sent_backup`
 -- --

INSERT INTO sent_backup SELECT msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, 0, folder, encodingtype FROM sent; 


-- --
-- -- Drope table `sent`
-- --

    DROP TABLE sent;


-- --
-- --  Table structure for table `sent_backup`
-- --


CREATE TABLE `sent` (
    `msgid` blob DEFAULT NULL,
    `toaddress` text DEFAULT NULL,
    `toripe` blob DEFAULT NULL,
    `fromaddress` text DEFAULT NULL,
    `subject` text DEFAULT NULL,
    `message` text DEFAULT NULL,
    `ackdata` blob DEFAULT NULL,
    `senttime` integer DEFAULT NULL,
    `lastactiontime` integer DEFAULT NULL,
    `sleeptill` int DEFAULT NULL,
    `status` text DEFAULT NULL,
    `retrynumber` integer DEFAULT NULL,
    `folder` text DEFAULT NULL,
    `encodingtype` int DEFAULT NULL,
    `ttl` int DEFAULT NULL
) ;


-- --
-- -- Dumping data for table `sent`
-- --


INSERT INTO sent SELECT msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, lastactiontime, 0, status, 0, folder, encodingtype, 216000 FROM sent_backup;


--UPDATE pubkeys SET address= (select enaddr(?, ?, ?)", (addressVersion, 1, addressHash)) WHERE hash=?

-- --
-- -- Drop table `sent`
-- --

    DROP TABLE sent_backup;
