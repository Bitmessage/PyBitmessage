CREATE TABLE `testhash` (
    `addressversion` int DEFAULT NULL,
    `hash` blob DEFAULT NULL,
    `address` text DEFAULT NULL,
    UNIQUE(address) ON CONFLICT IGNORE
);



INSERT INTO testhash (addressversion, hash) VALUES(4, "21122112211221122112");

