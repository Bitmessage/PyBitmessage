<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS><TS version="2.0" language="en" sourcelanguage="en">
<context>
    <name>AddAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="62"/>
        <source>Add new entry</source>
        <translation>Add new entry</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="63"/>
        <source>Label</source>
        <translation>Label</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="64"/>
        <source>Address</source>
        <translation>Address</translation>
    </message>
</context>
<context>
    <name>EmailGatewayDialog</name>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="67"/>
        <source>Email gateway</source>
        <translation>Email gateway</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="68"/>
        <source>Register on email gateway</source>
        <translation>Register on email gateway</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="69"/>
        <source>Account status at email gateway</source>
        <translation>Account status at email gateway</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="70"/>
        <source>Change account settings at email gateway</source>
        <translation>Change account settings at email gateway</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="71"/>
        <source>Unregister from email gateway</source>
        <translation>Unregister from email gateway</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="72"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.</source>
        <translation>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="73"/>
        <source>Desired email address (including @mailchuck.com):</source>
        <translation>Desired email address (including @mailchuck.com):</translation>
    </message>
</context>
<context>
    <name>EmailGatewayRegistrationDialog</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2266"/>
        <source>Registration failed:</source>
        <translation>Registration failed:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2266"/>
        <source>The requested email address is not available, please try a new one. Fill out the new desired email address (including @mailchuck.com) below:</source>
        <translation>The requested email address is not available, please try a new one. Fill out the new desired email address (including @mailchuck.com) below:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="102"/>
        <source>Email gateway registration</source>
        <translation>Email gateway registration</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="103"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.
Please type the desired email address (including @mailchuck.com) below:</source>
        <translation>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.
Please type the desired email address (including @mailchuck.com) below:</translation>
    </message>
</context>
<context>
    <name>Mailchuck</name>
    <message>
        <location filename="../bitmessageqt/account.py" line="225"/>
        <source># You can use this to configure your email gateway account
# Uncomment the setting you want to use
# Here are the options:
# 
# pgp: server
# The email gateway will create and maintain PGP keys for you and sign, verify,
# encrypt and decrypt on your behalf. When you want to use PGP but are lazy,
# use this. Requires subscription.
#
# pgp: local
# The email gateway will not conduct PGP operations on your behalf. You can
# either not use PGP at all, or use it locally.
#
# attachments: yes
# Incoming attachments in the email will be uploaded to MEGA.nz, and you can
# download them from there by following the link. Requires a subscription.
#
# attachments: no
# Attachments will be ignored.
# 
# archive: yes
# Your incoming emails will be archived on the server. Use this if you need
# help with debugging problems or you need a third party proof of emails. This
# however means that the operator of the service will be able to read your
# emails even after they have been delivered to you.
#
# archive: no
# Incoming emails will be deleted from the server as soon as they are relayed
# to you.
#
# masterpubkey_btc: BIP44 xpub key or electrum v1 public seed
# offset_btc: integer (defaults to 0)
# feeamount: number with up to 8 decimal places
# feecurrency: BTC, XBT, USD, EUR or GBP
# Use these if you want to charge people who send you emails. If this is on and
# an unknown person sends you an email, they will be requested to pay the fee
# specified. As this scheme uses deterministic public keys, you will receive
# the money directly. To turn it off again, set &quot;feeamount&quot; to 0. Requires
# subscription.
</source>
        <translation># You can use this to configure your email gateway account
# Uncomment the setting you want to use
# Here are the options:
# 
# pgp: server
# The email gateway will create and maintain PGP keys for you and sign, verify,
# encrypt and decrypt on your behalf. When you want to use PGP but are lazy,
# use this. Requires subscription.
#
# pgp: local
# The email gateway will not conduct PGP operations on your behalf. You can
# either not use PGP at all, or use it locally.
#
# attachments: yes
# Incoming attachments in the email will be uploaded to MEGA.nz, and you can
# download them from there by following the link. Requires a subscription.
#
# attachments: no
# Attachments will be ignored.
# 
# archive: yes
# Your incoming emails will be archived on the server. Use this if you need
# help with debugging problems or you need a third party proof of emails. This
# however means that the operator of the service will be able to read your
# emails even after they have been delivered to you.
#
# archive: no
# Incoming emails will be deleted from the server as soon as they are relayed
# to you.
#
# masterpubkey_btc: BIP44 xpub key or electrum v1 public seed
# offset_btc: integer (defaults to 0)
# feeamount: number with up to 8 decimal places
# feecurrency: BTC, XBT, USD, EUR or GBP
# Use these if you want to charge people who send you emails. If this is on and
# an unknown person sends you an email, they will be requested to pay the fee
# specified. As this scheme uses deterministic public keys, you will receive
# the money directly. To turn it off again, set &quot;feeamount&quot; to 0. Requires
# subscription.
</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="190"/>
        <source>Reply to sender</source>
        <translation>Reply to sender</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="192"/>
        <source>Reply to channel</source>
        <translation>Reply to channel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="194"/>
        <source>Add sender to your Address Book</source>
        <translation>Add sender to your Address Book</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="198"/>
        <source>Add sender to your Blacklist</source>
        <translation>Add sender to your Blacklist</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="380"/>
        <source>Move to Trash</source>
        <translation>Move to Trash</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="205"/>
        <source>Undelete</source>
        <translation>Undelete</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="208"/>
        <source>View HTML code as formatted text</source>
        <translation>View HTML code as formatted text</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="212"/>
        <source>Save message as...</source>
        <translation>Save message as...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="216"/>
        <source>Mark Unread</source>
        <translation>Mark Unread</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="352"/>
        <source>New</source>
        <translation>New</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="122"/>
        <source>Enable</source>
        <translation>Enable</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="125"/>
        <source>Disable</source>
        <translation>Disable</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="128"/>
        <source>Set avatar...</source>
        <translation>Set avatar...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="118"/>
        <source>Copy address to clipboard</source>
        <translation>Copy address to clipboard</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="303"/>
        <source>Special address behavior...</source>
        <translation>Special address behavior...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="264"/>
        <source>Email gateway</source>
        <translation>Email gateway</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="115"/>
        <source>Delete</source>
        <translation>Delete</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="319"/>
        <source>Send message to this address</source>
        <translation>Send message to this address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="327"/>
        <source>Subscribe to this address</source>
        <translation>Subscribe to this address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="335"/>
        <source>Add New Address</source>
        <translation>Add New Address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="383"/>
        <source>Copy destination address to clipboard</source>
        <translation>Copy destination address to clipboard</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="387"/>
        <source>Force send</source>
        <translation>Force send</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="599"/>
        <source>One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?</source>
        <translation>One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="992"/>
        <source>Waiting for their encryption key. Will request it again soon.</source>
        <translation>Waiting for their encryption key. Will request it again soon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="990"/>
        <source>Encryption key request queued.</source>
        <translation type="obsolete">Encryption key request queued.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="998"/>
        <source>Queued.</source>
        <translation>Queued.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1001"/>
        <source>Message sent. Waiting for acknowledgement. Sent at %1</source>
        <translation>Message sent. Waiting for acknowledgement. Sent at %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1004"/>
        <source>Message sent. Sent at %1</source>
        <translation>Message sent. Sent at %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1002"/>
        <source>Need to do work to send message. Work is queued.</source>
        <translation type="obsolete">Need to do work to send message. Work is queued.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1010"/>
        <source>Acknowledgement of the message received %1</source>
        <translation>Acknowledgement of the message received %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2139"/>
        <source>Broadcast queued.</source>
        <translation>Broadcast queued.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1019"/>
        <source>Broadcast on %1</source>
        <translation>Broadcast on %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1022"/>
        <source>Problem: The work demanded by the recipient is more difficult than you are willing to do. %1</source>
        <translation>Problem: The work demanded by the recipient is more difficult than you are willing to do. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1025"/>
        <source>Problem: The recipient&apos;s encryption key is no good. Could not encrypt message. %1</source>
        <translation>Problem: The recipient&apos;s encryption key is no good. Could not encrypt message. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1028"/>
        <source>Forced difficulty override. Send should start soon.</source>
        <translation>Forced difficulty override. Send should start soon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1031"/>
        <source>Unknown status: %1 %2</source>
        <translation>Unknown status: %1 %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1697"/>
        <source>Not Connected</source>
        <translation>Not Connected</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1156"/>
        <source>Show Bitmessage</source>
        <translation>Show Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="691"/>
        <source>Send</source>
        <translation>Send</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1171"/>
        <source>Subscribe</source>
        <translation>Subscribe</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1177"/>
        <source>Channel</source>
        <translation>Channel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="737"/>
        <source>Quit</source>
        <translation>Quit</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1527"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.</source>
        <translation>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1531"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file.</source>
        <translation>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1538"/>
        <source>Open keys.dat?</source>
        <translation>Open keys.dat?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1535"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1538"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1545"/>
        <source>Delete trash?</source>
        <translation>Delete trash?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1545"/>
        <source>Are you sure you want to delete all trashed messages?</source>
        <translation>Are you sure you want to delete all trashed messages?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1565"/>
        <source>bad passphrase</source>
        <translation>bad passphrase</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1565"/>
        <source>You must type your passphrase. If you don&apos;t have one then this is not the form for you.</source>
        <translation>You must type your passphrase. If you don&apos;t have one then this is not the form for you.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1578"/>
        <source>Bad address version number</source>
        <translation>Bad address version number</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1574"/>
        <source>Your address version number must be a number: either 3 or 4.</source>
        <translation>Your address version number must be a number: either 3 or 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1578"/>
        <source>Your address version number must be either 3 or 4.</source>
        <translation>Your address version number must be either 3 or 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1608"/>
        <source>Chan name needed</source>
        <translation>Chan name needed</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1608"/>
        <source>You didn&apos;t enter a chan name.</source>
        <translation>You didn&apos;t enter a chan name.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1628"/>
        <source>Address already present</source>
        <translation>Address already present</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1628"/>
        <source>Could not add chan because it appears to already be one of your identities.</source>
        <translation>Could not add chan because it appears to already be one of your identities.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1632"/>
        <source>Success</source>
        <translation>Success</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1603"/>
        <source>Successfully created chan. To let others join your chan, give them the chan name and this Bitmessage address: %1. This address also appears in &apos;Your Identities&apos;.</source>
        <translation>Successfully created chan. To let others join your chan, give them the chan name and this Bitmessage address: %1. This address also appears in &apos;Your Identities&apos;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1612"/>
        <source>Address too new</source>
        <translation>Address too new</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1612"/>
        <source>Although that Bitmessage address might be valid, its version number is too new for us to handle. Perhaps you need to upgrade Bitmessage.</source>
        <translation>Although that Bitmessage address might be valid, its version number is too new for us to handle. Perhaps you need to upgrade Bitmessage.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1616"/>
        <source>Address invalid</source>
        <translation>Address invalid</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1616"/>
        <source>That Bitmessage address is not valid.</source>
        <translation>That Bitmessage address is not valid.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1624"/>
        <source>Address does not match chan name</source>
        <translation>Address does not match chan name</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1624"/>
        <source>Although the Bitmessage address you entered was valid, it doesn&apos;t match the chan name.</source>
        <translation>Although the Bitmessage address you entered was valid, it doesn&apos;t match the chan name.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1632"/>
        <source>Successfully joined chan. </source>
        <translation>Successfully joined chan. </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1691"/>
        <source>Connection lost</source>
        <translation>Connection lost</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1730"/>
        <source>Connected</source>
        <translation>Connected</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1847"/>
        <source>Message trashed</source>
        <translation>Message trashed</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1931"/>
        <source>The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate.</source>
        <translation>The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1967"/>
        <source>Message too long</source>
        <translation>Message too long</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1967"/>
        <source>The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.</source>
        <translation>The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1999"/>
        <source>Error: Your account wasn&apos;t registered at an email gateway. Sending registration now as %1, please wait for the registration to be processed before retrying sending.</source>
        <translation>Error: Your account wasn&apos;t registered at an email gateway. Sending registration now as %1, please wait for the registration to be processed before retrying sending.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2008"/>
        <source>Error: Bitmessage addresses start with BM-   Please check %1</source>
        <translation>Error: Bitmessage addresses start with BM-   Please check %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2011"/>
        <source>Error: The address %1 is not typed or copied correctly. Please check it.</source>
        <translation>Error: The address %1 is not typed or copied correctly. Please check it.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2014"/>
        <source>Error: The address %1 contains invalid characters. Please check it.</source>
        <translation>Error: The address %1 contains invalid characters. Please check it.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2017"/>
        <source>Error: The address version in %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</source>
        <translation>Error: The address version in %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2020"/>
        <source>Error: Some data encoded in the address %1 is too short. There might be something wrong with the software of your acquaintance.</source>
        <translation>Error: Some data encoded in the address %1 is too short. There might be something wrong with the software of your acquaintance.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2023"/>
        <source>Error: Some data encoded in the address %1 is too long. There might be something wrong with the software of your acquaintance.</source>
        <translation>Error: Some data encoded in the address %1 is too long. There might be something wrong with the software of your acquaintance.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2026"/>
        <source>Error: Some data encoded in the address %1 is malformed. There might be something wrong with the software of your acquaintance.</source>
        <translation>Error: Some data encoded in the address %1 is malformed. There might be something wrong with the software of your acquaintance.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2029"/>
        <source>Error: Something is wrong with the address %1.</source>
        <translation>Error: Something is wrong with the address %1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2097"/>
        <source>Error: You must specify a From address. If you don&apos;t have one, go to the &apos;Your Identities&apos; tab.</source>
        <translation>Error: You must specify a From address. If you don&apos;t have one, go to the &apos;Your Identities&apos; tab.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2038"/>
        <source>Address version number</source>
        <translation>Address version number</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2038"/>
        <source>Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2042"/>
        <source>Stream number</source>
        <translation>Stream number</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2042"/>
        <source>Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2047"/>
        <source>Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won&apos;t send until you connect.</source>
        <translation>Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won&apos;t send until you connect.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2089"/>
        <source>Message queued.</source>
        <translation>Message queued.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2093"/>
        <source>Your &apos;To&apos; field is empty.</source>
        <translation>Your &apos;To&apos; field is empty.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2148"/>
        <source>Right click one or more entries in your address book and select &apos;Send message to this address&apos;.</source>
        <translation>Right click one or more entries in your address book and select &apos;Send message to this address&apos;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2161"/>
        <source>Fetched address from namecoin identity.</source>
        <translation>Fetched address from namecoin identity.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2260"/>
        <source>New Message</source>
        <translation>New Message</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2260"/>
        <source>From </source>
        <translation>From </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2638"/>
        <source>Sending email gateway registration request</source>
        <translation>Sending email gateway registration request</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="60"/>
        <source>Address is valid.</source>
        <translation>Address is valid.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="94"/>
        <source>The address you entered was invalid. Ignoring it.</source>
        <translation>The address you entered was invalid. Ignoring it.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3023"/>
        <source>Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.</source>
        <translation>Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3271"/>
        <source>Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want.</source>
        <translation>Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2398"/>
        <source>Restart</source>
        <translation>Restart</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2384"/>
        <source>You must restart Bitmessage for the port number change to take effect.</source>
        <translation>You must restart Bitmessage for the port number change to take effect.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2398"/>
        <source>Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any).</source>
        <translation>Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2426"/>
        <source>Number needed</source>
        <translation>Number needed</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2426"/>
        <source>Your maximum download and upload rate must be numbers. Ignoring what you typed.</source>
        <translation>Your maximum download and upload rate must be numbers. Ignoring what you typed.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2499"/>
        <source>Will not resend ever</source>
        <translation>Will not resend ever</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2499"/>
        <source>Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent.</source>
        <translation>Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2611"/>
        <source>Sending email gateway unregistration request</source>
        <translation>Sending email gateway unregistration request</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2615"/>
        <source>Sending email gateway status request</source>
        <translation>Sending email gateway status request</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2704"/>
        <source>Passphrase mismatch</source>
        <translation>Passphrase mismatch</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2704"/>
        <source>The passphrase you entered twice doesn&apos;t match. Try again.</source>
        <translation>The passphrase you entered twice doesn&apos;t match. Try again.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2707"/>
        <source>Choose a passphrase</source>
        <translation>Choose a passphrase</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2707"/>
        <source>You really do need a passphrase.</source>
        <translation>You really do need a passphrase.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2964"/>
        <source>Address is gone</source>
        <translation>Address is gone</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2964"/>
        <source>Bitmessage cannot find your address %1. Perhaps you removed it?</source>
        <translation>Bitmessage cannot find your address %1. Perhaps you removed it?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2967"/>
        <source>Address disabled</source>
        <translation>Address disabled</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2967"/>
        <source>Error: The address from which you are trying to send is disabled. You&apos;ll have to enable it on the &apos;Your Identities&apos; tab before using it.</source>
        <translation>Error: The address from which you are trying to send is disabled. You&apos;ll have to enable it on the &apos;Your Identities&apos; tab before using it.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3020"/>
        <source>Entry added to the Address Book. Edit the label to your liking.</source>
        <translation>Entry added to the Address Book. Edit the label to your liking.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3045"/>
        <source>Entry added to the blacklist. Edit the label to your liking.</source>
        <translation>Entry added to the blacklist. Edit the label to your liking.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3048"/>
        <source>Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want.</source>
        <translation>Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3176"/>
        <source>Moved items to trash.</source>
        <translation>Moved items to trash.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3116"/>
        <source>Undeleted item.</source>
        <translation>Undeleted item.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3144"/>
        <source>Save As...</source>
        <translation>Save As...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3153"/>
        <source>Write error.</source>
        <translation>Write error.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3257"/>
        <source>No addresses selected.</source>
        <translation>No addresses selected.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3303"/>
        <source>If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the subscription?</source>
        <translation>If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the subscription?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3533"/>
        <source>If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the channel?</source>
        <translation>If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the channel?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3647"/>
        <source>Do you really want to remove this avatar?</source>
        <translation>Do you really want to remove this avatar?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3655"/>
        <source>You have already set an avatar for this address. Do you really want to overwrite it?</source>
        <translation>You have already set an avatar for this address. Do you really want to overwrite it?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4032"/>
        <source>Start-on-login not yet supported on your OS.</source>
        <translation>Start-on-login not yet supported on your OS.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4025"/>
        <source>Minimize-to-tray not yet supported on your OS.</source>
        <translation>Minimize-to-tray not yet supported on your OS.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4028"/>
        <source>Tray notifications not yet supported on your OS.</source>
        <translation>Tray notifications not yet supported on your OS.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4197"/>
        <source>Testing...</source>
        <translation>Testing...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4237"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation>This is a chan address. You cannot use it as a pseudo-mailing list.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4297"/>
        <source>The address should start with &apos;&apos;BM-&apos;&apos;</source>
        <translation>The address should start with &apos;&apos;BM-&apos;&apos;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4300"/>
        <source>The address is not typed or copied correctly (the checksum failed).</source>
        <translation>The address is not typed or copied correctly (the checksum failed).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4303"/>
        <source>The version number of this address is higher than this software can support. Please upgrade Bitmessage.</source>
        <translation>The version number of this address is higher than this software can support. Please upgrade Bitmessage.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4306"/>
        <source>The address contains invalid characters.</source>
        <translation>The address contains invalid characters.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4309"/>
        <source>Some data encoded in the address is too short.</source>
        <translation>Some data encoded in the address is too short.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4312"/>
        <source>Some data encoded in the address is too long.</source>
        <translation>Some data encoded in the address is too long.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4315"/>
        <source>Some data encoded in the address is malformed.</source>
        <translation>Some data encoded in the address is malformed.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4289"/>
        <source>Enter an address above.</source>
        <translation>Enter an address above.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4321"/>
        <source>Address is an old type. We cannot display its past broadcasts.</source>
        <translation>Address is an old type. We cannot display its past broadcasts.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4330"/>
        <source>There are no recent broadcasts from this address to display.</source>
        <translation>There are no recent broadcasts from this address to display.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4374"/>
        <source>You are using TCP port %1. (This can be changed in the settings).</source>
        <translation>You are using TCP port %1. (This can be changed in the settings).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="648"/>
        <source>Bitmessage</source>
        <translation>Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="649"/>
        <source>Identities</source>
        <translation>Identities</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="650"/>
        <source>New Identity</source>
        <translation>New Identity</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="712"/>
        <source>Search</source>
        <translation>Search</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="713"/>
        <source>All</source>
        <translation>All</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="720"/>
        <source>To</source>
        <translation>To</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="722"/>
        <source>From</source>
        <translation>From</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="724"/>
        <source>Subject</source>
        <translation>Subject</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="717"/>
        <source>Message</source>
        <translation>Message</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="726"/>
        <source>Received</source>
        <translation>Received</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="666"/>
        <source>Messages</source>
        <translation>Messages</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="669"/>
        <source>Address book</source>
        <translation>Address book</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="671"/>
        <source>Address</source>
        <translation>Address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="672"/>
        <source>Add Contact</source>
        <translation>Add Contact</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="673"/>
        <source>Fetch Namecoin ID</source>
        <translation>Fetch Namecoin ID</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="680"/>
        <source>Subject:</source>
        <translation>Subject:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="679"/>
        <source>From:</source>
        <translation>From:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="676"/>
        <source>To:</source>
        <translation>To:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="678"/>
        <source>Send ordinary Message</source>
        <translation>Send ordinary Message</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="682"/>
        <source>Send Message to your Subscribers</source>
        <translation>Send Message to your Subscribers</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="683"/>
        <source>TTL:</source>
        <translation>TTL:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="709"/>
        <source>Subscriptions</source>
        <translation>Subscriptions</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="693"/>
        <source>Add new Subscription</source>
        <translation>Add new Subscription</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="727"/>
        <source>Chans</source>
        <translation>Chans</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="711"/>
        <source>Add Chan</source>
        <translation>Add Chan</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="732"/>
        <source>File</source>
        <translation>File</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="743"/>
        <source>Settings</source>
        <translation>Settings</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="739"/>
        <source>Help</source>
        <translation>Help</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="735"/>
        <source>Import keys</source>
        <translation>Import keys</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="736"/>
        <source>Manage keys</source>
        <translation>Manage keys</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="738"/>
        <source>Ctrl+Q</source>
        <translation>Ctrl+Q</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="740"/>
        <source>F1</source>
        <translation>F1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="741"/>
        <source>Contact support</source>
        <translation>Contact support</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="742"/>
        <source>About</source>
        <translation>About</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="744"/>
        <source>Regenerate deterministic addresses</source>
        <translation>Regenerate deterministic addresses</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="745"/>
        <source>Delete all trashed messages</source>
        <translation>Delete all trashed messages</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="746"/>
        <source>Join / Create chan</source>
        <translation>Join / Create chan</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="172"/>
        <source>All accounts</source>
        <translation>All accounts</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="44"/>
        <source>Zoom level %1%</source>
        <translation>Zoom level %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="91"/>
        <source>Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.</source>
        <translation>Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="112"/>
        <source>Add new entry</source>
        <translation>Add new entry</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4334"/>
        <source>Display the %1 recent broadcast(s) from this address.</source>
        <translation>Display the %1 recent broadcast(s) from this address.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1856"/>
        <source>New version of PyBitmessage is available: %1. Download it from https://github.com/Bitmessage/PyBitmessage/releases/latest</source>
        <translation>New version of PyBitmessage is available: %1. Download it from https://github.com/Bitmessage/PyBitmessage/releases/latest</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2756"/>
        <source>Waiting for PoW to finish... %1%</source>
        <translation>Waiting for PoW to finish... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2760"/>
        <source>Shutting down Pybitmessage... %1%</source>
        <translation>Shutting down Pybitmessage... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2776"/>
        <source>Waiting for objects to be sent... %1%</source>
        <translation>Waiting for objects to be sent... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2786"/>
        <source>Saving settings... %1%</source>
        <translation>Saving settings... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2795"/>
        <source>Shutting down core... %1%</source>
        <translation>Shutting down core... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2798"/>
        <source>Stopping notifications... %1%</source>
        <translation>Stopping notifications... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2804"/>
        <source>Shutdown imminent... %1%</source>
        <translation>Shutdown imminent... %1%</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/bitmessageui.py" line="689"/>
        <source>%n hour(s)</source>
        <translation>
            <numerusform>%n hour</numerusform>
            <numerusform>%n hours</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="824"/>
        <source>%n day(s)</source>
        <translation>
            <numerusform>%n day</numerusform>
            <numerusform>%n days</numerusform>
        </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2730"/>
        <source>Shutting down PyBitmessage... %1%</source>
        <translation>Shutting down PyBitmessage... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1104"/>
        <source>Sent</source>
        <translation>Sent</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="86"/>
        <source>Generating one new address</source>
        <translation>Generating one new address</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="148"/>
        <source>Done generating address. Doing work necessary to broadcast it...</source>
        <translation>Done generating address. Doing work necessary to broadcast it...</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="165"/>
        <source>Generating %1 new addresses.</source>
        <translation>Generating %1 new addresses.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="242"/>
        <source>%1 is already in &apos;Your Identities&apos;. Not adding it again.</source>
        <translation>%1 is already in &apos;Your Identities&apos;. Not adding it again.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="278"/>
        <source>Done generating address</source>
        <translation>Done generating address</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="228"/>
        <source>SOCKS5 Authentication problem: %1</source>
        <translation>SOCKS5 Authentication problem: %1</translation>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="565"/>
        <source>Disk full</source>
        <translation>Disk full</translation>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="565"/>
        <source>Alert: Your disk or data storage volume is full. Bitmessage will now exit.</source>
        <translation>Alert: Your disk or data storage volume is full. Bitmessage will now exit.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="721"/>
        <source>Error! Could not find sender address (your address) in the keys.dat file.</source>
        <translation>Error! Could not find sender address (your address) in the keys.dat file.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="467"/>
        <source>Doing work necessary to send broadcast...</source>
        <translation>Doing work necessary to send broadcast...</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="490"/>
        <source>Broadcast sent on %1</source>
        <translation>Broadcast sent on %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="559"/>
        <source>Encryption key was requested earlier.</source>
        <translation>Encryption key was requested earlier.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="596"/>
        <source>Sending a request for the recipient&apos;s encryption key.</source>
        <translation>Sending a request for the recipient&apos;s encryption key.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="613"/>
        <source>Looking up the receiver&apos;s public key</source>
        <translation>Looking up the receiver&apos;s public key</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="647"/>
        <source>Problem: Destination is a mobile device who requests that the destination be included in the message but this is disallowed in your settings.  %1</source>
        <translation>Problem: Destination is a mobile device who requests that the destination be included in the message but this is disallowed in your settings.  %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="661"/>
        <source>Doing work necessary to send message.
There is no required difficulty for version 2 addresses like this.</source>
        <translation>Doing work necessary to send message.
There is no required difficulty for version 2 addresses like this.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="675"/>
        <source>Doing work necessary to send message.
Receiver&apos;s required difficulty: %1 and %2</source>
        <translation>Doing work necessary to send message.
Receiver&apos;s required difficulty: %1 and %2</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="684"/>
        <source>Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do. %3</source>
        <translation>Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do. %3</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="696"/>
        <source>Problem: You are trying to send a message to yourself or a chan but your encryption key could not be found in the keys.dat file. Could not encrypt message. %1</source>
        <translation>Problem: You are trying to send a message to yourself or a chan but your encryption key could not be found in the keys.dat file. Could not encrypt message. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1007"/>
        <source>Doing work necessary to send message.</source>
        <translation>Doing work necessary to send message.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="819"/>
        <source>Message sent. Waiting for acknowledgement. Sent on %1</source>
        <translation>Message sent. Waiting for acknowledgement. Sent on %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="995"/>
        <source>Doing work necessary to request encryption key.</source>
        <translation>Doing work necessary to request encryption key.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="940"/>
        <source>Broadcasting the public key request. This program will auto-retry if they are offline.</source>
        <translation>Broadcasting the public key request. This program will auto-retry if they are offline.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="942"/>
        <source>Sending public key request. Waiting for reply. Requested at %1</source>
        <translation>Sending public key request. Waiting for reply. Requested at %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="220"/>
        <source>UPnP port mapping established on port %1</source>
        <translation>UPnP port mapping established on port %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="244"/>
        <source>UPnP port mapping removed</source>
        <translation>UPnP port mapping removed</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="268"/>
        <source>Mark all messages as read</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2647"/>
        <source>Are you sure you would like to mark all messages read?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1016"/>
        <source>Doing work necessary to send broadcast.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2738"/>
        <source>Proof of work pending</source>
        <translation type="unfinished"></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2738"/>
        <source>%n object(s) pending proof of work</source>
        <translation type="unfinished">
            <numerusform></numerusform>
            <numerusform></numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2738"/>
        <source>%n object(s) waiting to be distributed</source>
        <translation type="unfinished">
            <numerusform></numerusform>
            <numerusform></numerusform>
        </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2738"/>
        <source>Wait until these tasks finish?</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>NewAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="173"/>
        <source>Create new Address</source>
        <translation>Create new Address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="174"/>
        <source>Here you may generate as many addresses as you like. Indeed, creating and abandoning addresses is encouraged. You may generate addresses by using either random numbers or by using a passphrase. If you use a passphrase, the address is called a &quot;deterministic&quot; address.
The &apos;Random Number&apos; option is selected by default but deterministic addresses have several pros and cons:</source>
        <translation>Here you may generate as many addresses as you like. Indeed, creating and abandoning addresses is encouraged. You may generate addresses by using either random numbers or by using a passphrase. If you use a passphrase, the address is called a &quot;deterministic&quot; address.
The &apos;Random Number&apos; option is selected by default but deterministic addresses have several pros and cons:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="176"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Pros:&lt;br/&gt;&lt;/span&gt;You can recreate your addresses on any computer from memory. &lt;br/&gt;You need-not worry about backing up your keys.dat file as long as you can remember your passphrase. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Cons:&lt;br/&gt;&lt;/span&gt;You must remember (or write down) your passphrase if you expect to be able to recreate your keys if they are lost. &lt;br/&gt;You must remember the address version number and the stream number along with your passphrase. &lt;br/&gt;If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Pros:&lt;br/&gt;&lt;/span&gt;You can recreate your addresses on any computer from memory. &lt;br/&gt;You need-not worry about backing up your keys.dat file as long as you can remember your passphrase. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Cons:&lt;br/&gt;&lt;/span&gt;You must remember (or write down) your passphrase if you expect to be able to recreate your keys if they are lost. &lt;br/&gt;You must remember the address version number and the stream number along with your passphrase. &lt;br/&gt;If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="177"/>
        <source>Use a random number generator to make an address</source>
        <translation>Use a random number generator to make an address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="178"/>
        <source>Use a passphrase to make addresses</source>
        <translation>Use a passphrase to make addresses</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="179"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="180"/>
        <source>Make deterministic addresses</source>
        <translation>Make deterministic addresses</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="181"/>
        <source>Address version number: 4</source>
        <translation>Address version number: 4</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="182"/>
        <source>In addition to your passphrase, you must remember these numbers:</source>
        <translation>In addition to your passphrase, you must remember these numbers:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="183"/>
        <source>Passphrase</source>
        <translation>Passphrase</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="184"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Number of addresses to make based on your passphrase:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="185"/>
        <source>Stream number: 1</source>
        <translation>Stream number: 1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="186"/>
        <source>Retype passphrase</source>
        <translation>Retype passphrase</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="187"/>
        <source>Randomly generate address</source>
        <translation>Randomly generate address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="188"/>
        <source>Label (not shown to anyone except you)</source>
        <translation>Label (not shown to anyone except you)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="189"/>
        <source>Use the most available stream</source>
        <translation>Use the most available stream</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="190"/>
        <source> (best if this is the first of many addresses you will create)</source>
        <translation> (best if this is the first of many addresses you will create)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="191"/>
        <source>Use the same stream as an existing address</source>
        <translation>Use the same stream as an existing address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="192"/>
        <source>(saves you some bandwidth and processing power)</source>
        <translation>(saves you some bandwidth and processing power)</translation>
    </message>
</context>
<context>
    <name>NewSubscriptionDialog</name>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="65"/>
        <source>Add new entry</source>
        <translation>Add new entry</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="66"/>
        <source>Label</source>
        <translation>Label</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="67"/>
        <source>Address</source>
        <translation>Address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="68"/>
        <source>Enter an address above.</source>
        <translation>Enter an address above.</translation>
    </message>
</context>
<context>
    <name>SpecialAddressBehaviorDialog</name>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="59"/>
        <source>Special Address Behavior</source>
        <translation>Special Address Behavior</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="60"/>
        <source>Behave as a normal address</source>
        <translation>Behave as a normal address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="61"/>
        <source>Behave as a pseudo-mailing-list address</source>
        <translation>Behave as a pseudo-mailing-list address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="62"/>
        <source>Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).</source>
        <translation>Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="63"/>
        <source>Name of the pseudo-mailing-list:</source>
        <translation>Name of the pseudo-mailing-list:</translation>
    </message>
</context>
<context>
    <name>aboutDialog</name>
    <message>
        <location filename="../bitmessageqt/about.py" line="67"/>
        <source>About</source>
        <translation>About</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="68"/>
        <source>PyBitmessage</source>
        <translation>PyBitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="69"/>
        <source>version ?</source>
        <translation>version ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="71"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distributed under the MIT/X11 software license; see &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distributed under the MIT/X11 software license; see &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="72"/>
        <source>This is Beta software.</source>
        <translation>This is Beta software.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright &#xc2;&#xa9; 2012-2016 Jonathan Warren&lt;br/&gt;Copyright &#xc2;&#xa9; 2013-2016 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished">&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright Â© 2012-2016 Jonathan Warren&lt;br/&gt;Copyright Â© 2013-2016 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
</context>
<context>
    <name>blacklist</name>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="17"/>
        <source>Use a Blacklist (Allow all incoming messages except those on the Blacklist)</source>
        <translation>Use a Blacklist (Allow all incoming messages except those on the Blacklist)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="27"/>
        <source>Use a Whitelist (Block all incoming messages except those on the Whitelist)</source>
        <translation>Use a Whitelist (Block all incoming messages except those on the Whitelist)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="34"/>
        <source>Add new entry</source>
        <translation>Add new entry</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="85"/>
        <source>Name or Label</source>
        <translation>Name or Label</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="90"/>
        <source>Address</source>
        <translation>Address</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="151"/>
        <source>Blacklist</source>
        <translation>Blacklist</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="153"/>
        <source>Whitelist</source>
        <translation>Whitelist</translation>
    </message>
</context>
<context>
    <name>connectDialog</name>
    <message>
        <location filename="../bitmessageqt/connect.py" line="56"/>
        <source>Bitmessage</source>
        <translation>Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="57"/>
        <source>Bitmessage won&apos;t connect to anyone until you let it. </source>
        <translation>Bitmessage won&apos;t connect to anyone until you let it. </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="58"/>
        <source>Connect now</source>
        <translation>Connect now</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="59"/>
        <source>Let me configure special network settings first</source>
        <translation>Let me configure special network settings first</translation>
    </message>
</context>
<context>
    <name>helpDialog</name>
    <message>
        <location filename="../bitmessageqt/help.py" line="45"/>
        <source>Help</source>
        <translation>Help</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.py" line="46"/>
        <source>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</source>
        <translation>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.py" line="47"/>
        <source>As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:</source>
        <translation>As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:</translation>
    </message>
</context>
<context>
    <name>iconGlossaryDialog</name>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="82"/>
        <source>Icon Glossary</source>
        <translation>Icon Glossary</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="83"/>
        <source>You have no connections with other peers. </source>
        <translation>You have no connections with other peers. </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="84"/>
        <source>You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn&apos;t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.</source>
        <translation>You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn&apos;t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="85"/>
        <source>You are using TCP port ?. (This can be changed in the settings).</source>
        <translation>You are using TCP port ?. (This can be changed in the settings).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="86"/>
        <source>You do have connections with other peers and your firewall is correctly configured.</source>
        <translation>You do have connections with other peers and your firewall is correctly configured.</translation>
    </message>
</context>
<context>
    <name>networkstatus</name>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="39"/>
        <source>Total connections:</source>
        <translation>Total connections:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="143"/>
        <source>Since startup:</source>
        <translation>Since startup:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="159"/>
        <source>Processed 0 person-to-person messages.</source>
        <translation>Processed 0 person-to-person messages.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="188"/>
        <source>Processed 0 public keys.</source>
        <translation>Processed 0 public keys.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="175"/>
        <source>Processed 0 broadcasts.</source>
        <translation>Processed 0 broadcasts.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="240"/>
        <source>Inventory lookups per second: 0</source>
        <translation>Inventory lookups per second: 0</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="201"/>
        <source>Objects to be synced:</source>
        <translation>Objects to be synced:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="111"/>
        <source>Stream #</source>
        <translation>Stream #</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="116"/>
        <source>Connections</source>
        <translation>Connections</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="137"/>
        <source>Since startup on %1</source>
        <translation>Since startup on %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="71"/>
        <source>Down: %1/s  Total: %2</source>
        <translation>Down: %1/s  Total: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="73"/>
        <source>Up: %1/s  Total: %2</source>
        <translation>Up: %1/s  Total: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="120"/>
        <source>Total Connections: %1</source>
        <translation>Total Connections: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="129"/>
        <source>Inventory lookups per second: %1</source>
        <translation>Inventory lookups per second: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="214"/>
        <source>Up: 0 kB/s</source>
        <translation>Up: 0 kB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="227"/>
        <source>Down: 0 kB/s</source>
        <translation>Down: 0 kB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="731"/>
        <source>Network Status</source>
        <translation>Network Status</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="38"/>
        <source>byte(s)</source>
        <translation>
            <numerusform>byte</numerusform>
            <numerusform>bytes</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="49"/>
        <source>Object(s) to be synced: %n</source>
        <translation>
            <numerusform>Object to be synced: %n</numerusform>
            <numerusform>Objects to be synced: %n</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="53"/>
        <source>Processed %n person-to-person message(s).</source>
        <translation>
            <numerusform>Processed %n person-to-person message.</numerusform>
            <numerusform>Processed %n person-to-person messages.</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="58"/>
        <source>Processed %n broadcast message(s).</source>
        <translation>
            <numerusform>Processed %n broadcast message.</numerusform>
            <numerusform>Processed %n broadcast messages.</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="63"/>
        <source>Processed %n public key(s).</source>
        <translation>
            <numerusform>Processed %n public key.</numerusform>
            <numerusform>Processed %n public keys.</numerusform>
        </translation>
    </message>
</context>
<context>
    <name>newChanDialog</name>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="97"/>
        <source>Dialog</source>
        <translation>Dialog</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="98"/>
        <source>Create a new chan</source>
        <translation>Create a new chan</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="103"/>
        <source>Join a chan</source>
        <translation>Join a chan</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="100"/>
        <source>Create a chan</source>
        <translation>Create a chan</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="101"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly then the chan will be secure and private. If you and someone else both create a chan with the same chan name then it is currently very likely that they will be the same chan.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly then the chan will be secure and private. If you and someone else both create a chan with the same chan name then it is currently very likely that they will be the same chan.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="105"/>
        <source>Chan name:</source>
        <translation>Chan name:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="104"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a normal person-to-person message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a normal person-to-person message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="106"/>
        <source>Chan bitmessage address:</source>
        <translation>Chan bitmessage address:</translation>
    </message>
</context>
<context>
    <name>regenerateAddressesDialog</name>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="114"/>
        <source>Regenerate Existing Addresses</source>
        <translation>Regenerate Existing Addresses</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="115"/>
        <source>Regenerate existing addresses</source>
        <translation>Regenerate existing addresses</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="116"/>
        <source>Passphrase</source>
        <translation>Passphrase</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="117"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Number of addresses to make based on your passphrase:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="118"/>
        <source>Address version number:</source>
        <translation>Address version number:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="119"/>
        <source>Stream number:</source>
        <translation>Stream number:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="120"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="121"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="122"/>
        <source>You must check (or not check) this box just like you did (or didn&apos;t) when you made your addresses the first time.</source>
        <translation>You must check (or not check) this box just like you did (or didn&apos;t) when you made your addresses the first time.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="123"/>
        <source>If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.</source>
        <translation>If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.</translation>
    </message>
</context>
<context>
    <name>settingsDialog</name>
    <message>
        <location filename="../bitmessageqt/settings.py" line="430"/>
        <source>Settings</source>
        <translation>Settings</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="431"/>
        <source>Start Bitmessage on user login</source>
        <translation>Start Bitmessage on user login</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="432"/>
        <source>Tray</source>
        <translation>Tray</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="433"/>
        <source>Start Bitmessage in the tray (don&apos;t show main window)</source>
        <translation>Start Bitmessage in the tray (don&apos;t show main window)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="434"/>
        <source>Minimize to tray</source>
        <translation>Minimize to tray</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="435"/>
        <source>Close to tray</source>
        <translation>Close to tray</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="436"/>
        <source>Show notification when message received</source>
        <translation>Show notification when message received</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="437"/>
        <source>Run in Portable Mode</source>
        <translation>Run in Portable Mode</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="438"/>
        <source>In Portable Mode, messages and config files are stored in the same directory as the program rather than the normal application-data folder. This makes it convenient to run Bitmessage from a USB thumb drive.</source>
        <translation>In Portable Mode, messages and config files are stored in the same directory as the program rather than the normal application-data folder. This makes it convenient to run Bitmessage from a USB thumb drive.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="439"/>
        <source>Willingly include unencrypted destination address when sending to a mobile device</source>
        <translation>Willingly include unencrypted destination address when sending to a mobile device</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="440"/>
        <source>Use Identicons</source>
        <translation>Use Identicons</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="441"/>
        <source>Reply below Quote</source>
        <translation>Reply below Quote</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="442"/>
        <source>Interface Language</source>
        <translation>Interface Language</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="443"/>
        <source>System Settings</source>
        <comment>system</comment>
        <translation>System Settings</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="444"/>
        <source>User Interface</source>
        <translation>User Interface</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="445"/>
        <source>Listening port</source>
        <translation>Listening port</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="446"/>
        <source>Listen for connections on port:</source>
        <translation>Listen for connections on port:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="447"/>
        <source>UPnP:</source>
        <translation>UPnP:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="448"/>
        <source>Bandwidth limit</source>
        <translation>Bandwidth limit</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="449"/>
        <source>Maximum download rate (kB/s): [0: unlimited]</source>
        <translation>Maximum download rate (kB/s): [0: unlimited]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="450"/>
        <source>Maximum upload rate (kB/s): [0: unlimited]</source>
        <translation>Maximum upload rate (kB/s): [0: unlimited]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="451"/>
        <source>Proxy server / Tor</source>
        <translation>Proxy server / Tor</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="452"/>
        <source>Type:</source>
        <translation>Type:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="453"/>
        <source>Server hostname:</source>
        <translation>Server hostname:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="476"/>
        <source>Port:</source>
        <translation>Port:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="455"/>
        <source>Authentication</source>
        <translation>Authentication</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="477"/>
        <source>Username:</source>
        <translation>Username:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="457"/>
        <source>Pass:</source>
        <translation>Pass:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="458"/>
        <source>Listen for incoming connections when using proxy</source>
        <translation>Listen for incoming connections when using proxy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="459"/>
        <source>none</source>
        <translation>none</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="460"/>
        <source>SOCKS4a</source>
        <translation>SOCKS4a</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="461"/>
        <source>SOCKS5</source>
        <translation>SOCKS5</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="462"/>
        <source>Network Settings</source>
        <translation>Network Settings</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="463"/>
        <source>Total difficulty:</source>
        <translation>Total difficulty:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="464"/>
        <source>The &apos;Total difficulty&apos; affects the absolute amount of work the sender must complete. Doubling this value doubles the amount of work.</source>
        <translation>The &apos;Total difficulty&apos; affects the absolute amount of work the sender must complete. Doubling this value doubles the amount of work.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="465"/>
        <source>Small message difficulty:</source>
        <translation>Small message difficulty:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="466"/>
        <source>When someone sends you a message, their computer must first complete some work. The difficulty of this work, by default, is 1. You may raise this default for new addresses you create by changing the values here. Any new addresses you create will require senders to meet the higher difficulty. There is one exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically notify them when you next send a message that they need only complete the minimum amount of work: difficulty 1. </source>
        <translation>When someone sends you a message, their computer must first complete some work. The difficulty of this work, by default, is 1. You may raise this default for new addresses you create by changing the values here. Any new addresses you create will require senders to meet the higher difficulty. There is one exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically notify them when you next send a message that they need only complete the minimum amount of work: difficulty 1. </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="467"/>
        <source>The &apos;Small message difficulty&apos; mostly only affects the difficulty of sending small messages. Doubling this value makes it almost twice as difficult to send a small message but doesn&apos;t really affect large messages.</source>
        <translation>The &apos;Small message difficulty&apos; mostly only affects the difficulty of sending small messages. Doubling this value makes it almost twice as difficult to send a small message but doesn&apos;t really affect large messages.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="468"/>
        <source>Demanded difficulty</source>
        <translation>Demanded difficulty</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="469"/>
        <source>Here you may set the maximum amount of work you are willing to do to send a message to another person. Setting these values to 0 means that any value is acceptable.</source>
        <translation>Here you may set the maximum amount of work you are willing to do to send a message to another person. Setting these values to 0 means that any value is acceptable.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="470"/>
        <source>Maximum acceptable total difficulty:</source>
        <translation>Maximum acceptable total difficulty:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="471"/>
        <source>Maximum acceptable small message difficulty:</source>
        <translation>Maximum acceptable small message difficulty:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="472"/>
        <source>Max acceptable difficulty</source>
        <translation>Max acceptable difficulty</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Hardware GPU acceleration (OpenCL)</source>
        <translation>Hardware GPU acceleration (OpenCL)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="474"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage can utilize a different Bitcoin-based program called Namecoin to make addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage address, you can simply tell him to send a message to &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Getting your own Bitmessage address into Namecoin is still rather difficult).&lt;/p&gt;&lt;p&gt;Bitmessage can use either namecoind directly or a running nmcontrol instance.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage can utilize a different Bitcoin-based program called Namecoin to make addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage address, you can simply tell him to send a message to &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Getting your own Bitmessage address into Namecoin is still rather difficult).&lt;/p&gt;&lt;p&gt;Bitmessage can use either namecoind directly or a running nmcontrol instance.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="475"/>
        <source>Host:</source>
        <translation>Host:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="478"/>
        <source>Password:</source>
        <translation>Password:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="479"/>
        <source>Test</source>
        <translation>Test</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="480"/>
        <source>Connect to:</source>
        <translation>Connect to:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="481"/>
        <source>Namecoind</source>
        <translation>Namecoind</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="482"/>
        <source>NMControl</source>
        <translation>NMControl</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="483"/>
        <source>Namecoin integration</source>
        <translation>Namecoin integration</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="484"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;By default, if you send a message to someone and he is offline for more than two days, Bitmessage will send the message again after an additional two days. This will be continued with exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain number of days or months.&lt;/p&gt;&lt;p&gt;Leave these input fields blank for the default behavior. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;By default, if you send a message to someone and he is offline for more than two days, Bitmessage will send the message again after an additional two days. This will be continued with exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain number of days or months.&lt;/p&gt;&lt;p&gt;Leave these input fields blank for the default behavior. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="485"/>
        <source>Give up after</source>
        <translation>Give up after</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="486"/>
        <source>and</source>
        <translation>and</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="487"/>
        <source>days</source>
        <translation>days</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="488"/>
        <source>months.</source>
        <translation>months.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="489"/>
        <source>Resends Expire</source>
        <translation>Resends Expire</translation>
    </message>
</context>
</TS>
