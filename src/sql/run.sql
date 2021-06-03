--
-- Table structure for table `inbox`
--

CREATE TABLE `inbox` (
    `msgid` blob DEFAULT NULL,
    `toaddress` text DEFAULT NULL,
    `fromaddress` text DEFAULT NULL,
    `subject` text DEFAULT NULL,
    `received` text DEFAULT NULL,
    `message` text DEFAULT NULL,
    `folder` text DEFAULT NULL,
    `encodingtype` int DEFAULT NULL,
    `read` bool DEFAULT NULL,
    `sighash` blob DEFAULT NULL,
    UNIQUE(msgid) ON CONFLICT REPLACE
) ;

--
-- Table structure for table `sent`
--

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
    `sleeptill` integer DEFAULT NULL,
    `status` text DEFAULT NULL,
    `retrynumber` integer DEFAULT NULL,
    `folder` text DEFAULT NULL,
    `encodingtype` int DEFAULT NULL,
    `ttl` int DEFAULT NULL
) ;


--
-- Table structure for table `subscriptions`
--

CREATE TABLE `subscriptions` (
    `label` text DEFAULT NULL,
    `address` text DEFAULT NULL,
    `enabled` bool DEFAULT NULL
) ;


--
-- Table structure for table `addressbook`
--

CREATE TABLE `addressbook` (
    `label` text DEFAULT NULL,
    `address` text DEFAULT NULL,
    UNIQUE(address) ON CONFLICT IGNORE
) ;

--
-- Table structure for table `blacklist`
--

CREATE TABLE `blacklist` (
    `label` text DEFAULT NULL,
    `address` text DEFAULT NULL,
    `enabled` bool DEFAULT NULL
) ;

--
-- Table structure for table `whitelist`
--

CREATE TABLE `whitelist` (
    `label` text DEFAULT NULL,
    `address` text DEFAULT NULL,
    `enabled` bool DEFAULT NULL
) ;


--
-- Table structure for table `pubkeys`
--

CREATE TABLE `pubkeys` (
    `address` text DEFAULT NULL,
    `addressversion` int DEFAULT NULL,
    `transmitdata` blob DEFAULT NULL,
    `time` int DEFAULT NULL,
    `usedpersonally` text DEFAULT NULL,
    UNIQUE(address) ON CONFLICT REPLACE
) ;

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
    `hash` blob DEFAULT NULL,
    `objecttype` int DEFAULT NULL,
    `streamnumber` int DEFAULT NULL,
    `payload` blob DEFAULT NULL,
    `expirestime` integer DEFAULT NULL,
    `tag` blob DEFAULT NULL,
    UNIQUE(hash) ON CONFLICT REPLACE
) ;

--
-- Insert data for table `subscriptions`
--

INSERT INTO subscriptions VALUES ('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1);


--
-- Table structure for table `settings`
--

CREATE TABLE `settings` (
    `key` blob DEFAULT NULL,
    `value` blob DEFAULT NULL,
    UNIQUE(key) ON CONFLICT REPLACE
) ;
