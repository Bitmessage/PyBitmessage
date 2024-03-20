CREATE TABLE `inbox` (
   `msgid` blob,
   `toaddress` text,
   `fromaddress` text,
   `subject` text,
   `received` text,
   `message` text,
   `folder` text,
   `encodingtype` int,
   `read` bool,
UNIQUE(msgid) ON CONFLICT REPLACE
);

CREATE TABLE `sent` (
   `msgid` blob,
   `toaddress` text,
   `toripe` blob,
   `fromaddress` text,
   `subject` text,
   `message` text,
   `ackdata` blob,
   `lastactiontime` integer,
   `status` text,
   `pubkeyretrynumber` integer,
   `msgretrynumber` integer,
   `folder` text,
   `encodingtype` int
);

CREATE TABLE `subscriptions` (
   `label` text,
   `address` text,
   `enabled` bool
);

CREATE TABLE `addressbook` (
   `label` text,
   `address` text
);

CREATE TABLE `blacklist` (
   `label` text,
   `address` text,
   `enabled` bool
);

CREATE TABLE `whitelist` (
   `label` text,
   `address` text,
   `enabled` bool
);

CREATE TABLE `pubkeys` (
   `hash` blob,
   `transmitdata` blob,
   `time` int,
   `usedpersonally` text,
UNIQUE(hash) ON CONFLICT REPLACE
);

CREATE TABLE `inventory` (
   `hash` blob,
   `objecttype` text,
   `streamnumber` int,
   `payload` blob,
   `receivedtime` integer,
UNIQUE(hash) ON CONFLICT REPLACE
);

CREATE TABLE `knownnodes` (
   `timelastseen` int,
   `stream` int,
   `services` blob,
   `host` blob,
   `port` blob,
UNIQUE(host, stream, port) ON CONFLICT REPLACE
);

CREATE TABLE `settings` (
   `key` blob,
   `value` blob,
UNIQUE(key) ON CONFLICT REPLACE
);

INSERT INTO subscriptions VALUES ('Bitmessage new releases/announcements', 'BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw', 1);

INSERT INTO settings VALUES('version', 1);

INSERT INTO settings VALUES('lastvacuumtime', CAST(strftime('%s', 'now') AS STR) );

INSERT INTO inventory VALUES( '', 'pubkey', 1, '', 1);

