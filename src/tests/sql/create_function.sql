-- --
-- --  Table structure for table `testhash`
-- --


CREATE TEMPORARY TABLE `testhash` (
    `addressversion` int DEFAULT NULL,
    `hash` blob DEFAULT NULL,
    `address` text DEFAULT NULL,
    UNIQUE(address) ON CONFLICT IGNORE
) ;


-- --
-- -- Dumping data for table `testhash`
-- --

INSERT INTO testhash (addressversion, hash) VALUES(1, "21122112211221122112");

