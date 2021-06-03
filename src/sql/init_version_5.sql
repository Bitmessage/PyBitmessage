 --
 -- Drop Table `knownnodes`
 --

 DROP TABLE knownnodes;


 --
 --  Table structure for table `objectprocessorqueue`
 --


 CREATE TABLE `objectprocessorqueue` (
   `objecttype` text DEFAULT NULL,
   `data` blob DEFAULT NULL,
    UNIQUE(objecttype, data) ON CONFLICT REPLACE
 ) ;
