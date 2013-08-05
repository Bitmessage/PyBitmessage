PyBitmessage AUTO-UPDATE WHITEPAPER
============

Auto update in PyBitmessage - how we can do this

1) Subscribe ALL users to chan user auto-update (BM adress)
2) Hide this service subscription
3) When update release - compile it and make .torrent file, then HASH them
4) Push to auto-update chan MAGNET link to .torrent, OS Prefix  and hash sum 
5) When Pybitmessage get message it start download using opensource bittorrent client (rtorrent maby) after download it check hash sum (i know that bittorent do that but that way - more secure way)
6) Show popup for user that bitmessage have update
7) remove old client and unpack new
8) start new bitmessage
9) seed bitmessage with (maby rtorrent) for 1 week or 1GB seeded info.
10) make menu in option with infinite seed checkbox
11) send info to update chanel every 3 days

_____
Example

To: [chan] oficial-client-update
From: BM-Some-long-address
Subject: [Windows-7] Pybitmessage-1.0-DATE-05.08.2013
magnet:?xt=urn:btih:some_hashAD3E662E69В13898A4DС9853BEC4D31568E0D643&dn=PyBitmessage&tr=http://some.open.torrent.tracker.com/ 

hash_sum = some_different_hashAD3E662E69В13898A4DС9853BEC4D31568E0D643
____

And make chanels:
Stable
Beta
Dev

 