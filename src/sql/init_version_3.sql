--
-- Add a new column to the inventory table to store tags.
--

ALTER TABLE inventory ADD tag blob DEFAULT '';
