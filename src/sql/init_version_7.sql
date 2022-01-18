--
-- The format of data stored in the pubkeys table has changed. Let's
-- clear it, and the pubkeys from inventory, so that they'll
-- be re-downloaded.
--

DELETE FROM inventory WHERE objecttype = 1;

DELETE FROM pubkeys;

UPDATE sent SET status='msgqueued' WHERE status='doingmsgpow' or status='badkey';
