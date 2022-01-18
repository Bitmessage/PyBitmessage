--
-- Add a new column to the inbox table to store the hash of
-- the message signature. We'll use this as temporary message UUID
-- in order to detect duplicates.
--

ALTER TABLE inbox ADD sighash blob DEFAULT '';
