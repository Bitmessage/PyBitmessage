--- CREATE TABLE IF NOT EXISTS inbox (msgid blob, toaddress text, fromaddress text, subject text, received text, message text, folder text, encodingtype int, read bool, sighash blob,  UNIQUE(msgid) ON CONFLICT REPLACE));

-- CREATE TABLE IF NOT EXISTS `inbox` (
--   `msgid` blob NOT NULL,
--   `toaddress` text DEFAULT NULL,
--   `fromaddress` text DEFAULT NULL,
--   `subject` text DEFAULT NULL,
--   `received` text DEFAULT NULL,
--   `message` text DEFAULT NULL,
--   `folder` text DEFAULT NULL,
--   `encodingtype` int DEFAULT NULL,
--   `read` bool DEFAULT NULL,
--   `sighash` blob DEFAULT NULL,
--   UNIQUE(msgid) ON CONFLICT REPLACE
-- ) ;

-- CREATE TABLE IF NOT EXISTS `sent` (
--   `msgid` blob NOT NULL,
--   `toaddress` text DEFAULT NULL,
--   `toripe` blob DEFAULT NULL,
--   `fromaddress` text DEFAULT NULL,
--   `subject` text DEFAULT NULL,
--   `message` text DEFAULT NULL,
--   `ackdata` blob DEFAULT NULL,
--   `senttime` integer DEFAULT NULL,
--   `lastactiontime` integer DEFAULT NULL,
--   `sleeptill` integer DEFAULT NULL,
--   `status` text DEFAULT NULL,
--   `retrynumber` integer DEFAULT NULL,
--   `folder` text DEFAULT NULL,
--   `encodingtype` int DEFAULT NULL,
--   `ttl` int DEFAULT NULL,
--   UNIQUE(msgid) ON CONFLICT REPLACE
-- ) ;

--
-- Table structure for table `settings`
--

CREATE TABLE IF NOT EXISTS `settings` (
  `key` blob NOT NULL,
  `value` text DEFAULT NULL,
  UNIQUE(key) ON CONFLICT REPLACE
) ;


--
-- Dumping data for table `settings`
--


INSERT INTO `settings` VALUES ('version','1');

--
-- Table structure for table `inventory`
--

CREATE TABLE IF NOT EXISTS `inventory` (
  `hash` blob NOT NULL,
  `objecttype` int DEFAULT NULL,
  `streamnumber` int NOT NULL,
  `payload` blob DEFAULT NULL,
  `integer` integer NOT NULL,
  -- `tag` blob DEFAULT NULL,
  UNIQUE(hash) ON CONFLICT REPLACE
) ;


            -- self.cur.execute(
            --     '''CREATE TABLE inbox (msgid blob, toaddress text, fromaddress text, subject text,'''
            --     ''' received text, message text, folder text, encodingtype int, read bool, sighash blob,'''
            --     ''' UNIQUE(msgid) ON CONFLICT REPLACE)''')
            -- self.cur.execute(
            --     '''CREATE TABLE sent (msgid blob, toaddress text, toripe blob, fromaddress text, subject text,'''
            --     ''' message text, ackdata blob, senttime integer, lastactiontime integer,'''
            --     ''' sleeptill integer, status text, retrynumber integer, folder text, encodingtype int, ttl int)''')
            -- self.cur.execute(
            --     '''CREATE TABLE subscriptions (label text, address text, enabled bool)''')
            -- self.cur.execute(
            --     '''CREATE TABLE addressbook (label text, address text, UNIQUE(address) ON CONFLICT IGNORE)''')
            -- self.cur.execute(
            --     '''CREATE TABLE blacklist (label text, address text, enabled bool)''')
            -- self.cur.execute(
            --     '''CREATE TABLE whitelist (label text, address text, enabled bool)''')
            -- self.cur.execute(
            --     '''CREATE TABLE pubkeys (address text, addressversion int, transmitdata blob, time int,'''
            --     ''' usedpersonally text, UNIQUE(address) ON CONFLICT REPLACE)''')
            -- # self.cur.execute(
            -- #     '''CREATE TABLE inventory (hash blob, objecttype int, streamnumber int, payload blob,'''
            -- #     ''' expirestime integer, tag blob, UNIQUE(hash) ON CONFLICT REPLACE)''')
            -- self.cur.execute(
            --     '''CREATE TABLE inventory (hash blob, objecttype int, streamnumber int, payload blob,'''
            --     ''' expirestime integer, UNIQUE(hash) ON CONFLICT REPLACE)''')
            -- # self.cur.execute(
            -- #     '''INSERT INTO subscriptions VALUES'''
            -- #     '''('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1)''')
            -- self.cur.execute('''CREATE TABLE settings (key blob, value blob, UNIQUE(key) ON CONFLICT REPLACE)''')
            -- # self.cur.execute('''INSERT INTO settings VALUES('version','11')''')
            -- # self.cur.execute('''INSERT INTO settings VALUES('lastvacuumtime',?)''', (
            -- #     int(time.time()),))
            -- self.cur.execute(
            --     '''CREATE TABLE objectprocessorqueue'''
            --     ''' (objecttype int, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''')
            -- self.conn.commit()
