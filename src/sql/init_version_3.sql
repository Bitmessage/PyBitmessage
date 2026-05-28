--
-- Add a new column to the inventory table to store tags.
--

ALTER TABLE inventory ADD tag blob DEFAULT '';

UPDATE settings SET value = 4 WHERE key = 'version';
