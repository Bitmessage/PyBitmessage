 --
 -- Temp Table structure for table `inventory_backup`
 --

 CREATE TEMP TABLE `inventory_backup` (
   `hash` blob NOT NULL,
   `objecttype` text DEFAULT NULL,
   `streamnumber` int NOT NULL,
   `receivedtime` int NOT NULL,
   `payload` blob DEFAULT NULL,
   -- `integer` integer NOT NULL,
   -- `tag` blob DEFAULT NULL,
   UNIQUE(hash) ON CONFLICT REPLACE
 ) ;

 --
 -- Dumping data for table `inventory_backup`
 --

 INSERT INTO `inventory_backup` SELECT  hash, objecttype, streamnumber, payload, receivedtime FROM inventory;


 --
 -- Drop table `inventory`
 --

 DROP TABLE inventory;


 --
 --  Table structure for table `inventory`
 --


 CREATE TABLE `inventory` (
   `hash` blob NOT NULL,
   `objecttype` text DEFAULT NULL,
   `streamnumber` int NOT NULL,
   `receivedtime` int NOT NULL,
   `payload` blob DEFAULT NULL,
   UNIQUE(hash) ON CONFLICT REPLACE
 ) ;


 --
 -- Dumping data for table `inventory`
 --

 INSERT INTO inventory SELECT hash, objecttype, streamnumber, payload, receivedtime FROM inventory_backup;

 --
 -- Drop data for table `inventory_backup`
 --

 DROP TABLE inventory_backup;
