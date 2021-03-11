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








            self.cur.execute(
                '''CREATE TABLE inbox (msgid blob, toaddress text, fromaddress text, subject text,'''
                ''' received text, message text, folder text, encodingtype int, read bool, sighash blob,'''
                ''' UNIQUE(msgid) ON CONFLICT REPLACE)''')
            self.cur.execute(
                '''CREATE TABLE sent (msgid blob, toaddress text, toripe blob, fromaddress text, subject text,'''
                ''' message text, ackdata blob, senttime integer, lastactiontime integer,'''
                ''' sleeptill integer, status text, retrynumber integer, folder text, encodingtype int, ttl int)''')
            self.cur.execute(
                '''CREATE TABLE subscriptions (label text, address text, enabled bool)''')
            self.cur.execute(
                '''CREATE TABLE addressbook (label text, address text, UNIQUE(address) ON CONFLICT IGNORE)''')
            self.cur.execute(
                '''CREATE TABLE blacklist (label text, address text, enabled bool)''')
            self.cur.execute(
                '''CREATE TABLE whitelist (label text, address text, enabled bool)''')
            self.cur.execute(
                '''CREATE TABLE pubkeys (address text, addressversion int, transmitdata blob, time int,'''
                ''' usedpersonally text, UNIQUE(address) ON CONFLICT REPLACE)''')
            self.cur.execute(
                '''CREATE TABLE inventory (hash blob, objecttype int, streamnumber int, payload blob,'''
                ''' expirestime integer, tag blob, UNIQUE(hash) ON CONFLICT REPLACE)''')
            self.cur.execute(
                '''INSERT INTO subscriptions VALUES'''
                '''('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1)''')
            self.cur.execute(
                '''CREATE TABLE settings (key blob, value blob, UNIQUE(key) ON CONFLICT REPLACE)''')
            self.cur.execute('''INSERT INTO settings VALUES('version','11')''')
            self.cur.execute('''INSERT INTO settings VALUES('lastvacuumtime',?)''', (
                int(time.time()),))
            self.cur.execute(
                '''CREATE TABLE objectprocessorqueue'''
                ''' (objecttype int, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''')
