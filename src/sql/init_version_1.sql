ALTER TABLE inventory ADD first20bytesofencryptedmessage blob DEFAULT '';

UPDATE settings SET value = 2 WHERE key = 'version';