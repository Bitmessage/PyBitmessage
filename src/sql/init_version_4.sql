 --
 -- Drop Table `pubkeys`
 --

	DROP TABLE pubkeys;


--
--  Table structure for table `pubkeys`
--


	CREATE TABLE `pubkeys` (
		`hash` blob NOT NULL,
		`addressversion` int DEFAULT NULL,
		`transmitdata` blob NOT NULL,
		`time` int NOT NULL,
		`usedpersonally` text DEFAULT NULL,
		UNIQUE(hash, addressversion) ON CONFLICT REPLACE
	) ;

 --
 -- Drop from Table `pubkeys`
 --

	DELETE FROM inventory WHERE objecttype = 'pubkey';
