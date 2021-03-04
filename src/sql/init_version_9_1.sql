-- --
-- --  Table structure for table `pubkeys_backup`
-- --


CREATE TEMPORARY TABLE `pubkeys_backup` (
    `address` text DEFAULT NULL,
    `addressversion` int DEFAULT NULL,
    `transmitdata` blob DEFAULT NULL,
    `time` int DEFAULT NULL,
    `usedpersonally` text DEFAULT NULL,
    UNIQUE(address) ON CONFLICT REPLACE
) ;


-- --
-- -- Dumping data for table `pubkeys_backup`
-- --

INSERT INTO pubkeys_backup SELECT address, addressversion, transmitdata, time, usedpersonally FROM pubkeys;


-- --
-- -- Drope table `pubkeys`
-- --

    DROP TABLE pubkeys;


-- --
-- --  Table structure for table `pubkeys`
-- --

CREATE TABLE `pubkeys` (
    `address` text DEFAULT NULL,
    `addressversion` int DEFAULT NULL,
    `transmitdata` blob DEFAULT NULL,
    `time` int DEFAULT NULL,
    `usedpersonally` text DEFAULT NULL,
    UNIQUE(address) ON CONFLICT REPLACE
) ;


-- --
-- -- Dumping data for table `pubkeys`
-- --

INSERT INTO pubkeys SELECT address, addressversion, transmitdata, time, usedpersonally FROM pubkeys_backup;



        -- self.cur.execute(
        --     '''CREATE TEMPORARY TABLE pubkeys_backup'''
        --     ''' (address text, addressversion int, transmitdata blob, time int,'''
        --     ''' usedpersonally text, UNIQUE(address) ON CONFLICT REPLACE)''')
        -- self.cur.execute(
        --     '''INSERT INTO pubkeys_backup'''
        --     ''' SELECT address, addressversion, transmitdata, time, usedpersonally FROM pubkeys;''')
        -- self.cur.execute('''DROP TABLE pubkeys''')

        -- self.cur.execute(
        --     '''CREATE TABLE pubkeys'''
        --     ''' (address text, addressversion int, transmitdata blob, time int, usedpersonally text,'''
        --     ''' UNIQUE(address) ON CONFLICT REPLACE)''')
        -- self.cur.execute(
        --     '''INSERT INTO pubkeys SELECT'''
        --     ''' address, addressversion, transmitdata, time, usedpersonally FROM pubkeys_backup;''')
        -- self.cur.execute('''DROP TABLE pubkeys_backup''')
