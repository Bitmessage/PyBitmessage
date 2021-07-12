DROP TABLE objectprocessorqueue;

CREATE TABLE IF NOT EXISTS `knownnodes` (
  `hash` blob NOT NULL,
  `objecttype` int DEFAULT NULL,
  `streamnumber` int NOT NULL,
  `payload` blob DEFAULT NULL,
  `integer` integer NOT NULL,
  UNIQUE(hash) ON CONFLICT REPLACE
) ;
