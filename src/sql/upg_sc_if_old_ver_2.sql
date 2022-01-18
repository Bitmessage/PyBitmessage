UPDATE `sent` SET status='doingmsgpow' WHERE status='doingpow';

UPDATE `sent` SET status='msgsent' WHERE status='sentmessage';

UPDATE `sent` SET status='doingpubkeypow' WHERE status='findingpubkey';

UPDATE `sent` SET status='broadcastqueued' WHERE status='broadcastpending';
