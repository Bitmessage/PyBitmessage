-- --
-- -- Drop table `inventory`
-- --

    DELETE FROM inventory WHERE objecttype = 1;

-- --
-- -- Drop table `pubkeys`
-- --

    DELETE FROM pubkeys;


-- --
-- -- Update table `pubkeys`
-- --

    UPDATE sent SET status='msgqueued' WHERE status='doingmsgpow' or status='badkey';
