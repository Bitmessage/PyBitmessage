<?xml version="1.0" ?><!DOCTYPE TS><TS language="sk" sourcelanguage="en" version="2.0">
<context>
    <name>AddAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.ui" line="20"/>
        <source>Add new entry</source>
        <translation>Pridať nový záznam</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.ui" line="29"/>
        <source>Label</source>
        <translation>Označenie</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.ui" line="39"/>
        <source>Address</source>
        <translation>Adresa</translation>
    </message>
</context>
<context>
    <name>EmailGatewayDialog</name>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="14"/>
        <source>Email gateway</source>
        <translation>E-mailová brána</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="30"/>
        <source>Register on email gateway</source>
        <translation>Registrácia na e-mailovej bráne</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="82"/>
        <source>Account status at email gateway</source>
        <translation>Stav účtu na e-mailovej bráne</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="95"/>
        <source>Change account settings at email gateway</source>
        <translation>Zmena nastavení účtu na e-mailovej bráne</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="108"/>
        <source>Unregister from email gateway</source>
        <translation>Zrušiť registráciu na e-mailovej bráne</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="69"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.</source>
        <translation>E-mailové brány umožňujú komunikovať s užívateľmi e-mailu. Momentálne je k dispozícii iba e-mailová brána Mailchuck (@mailchuck.com).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="23"/>
        <source>Desired email address (including @mailchuck.com):</source>
        <translation>Požadovaná e-mailová adresa (vrátane @ mailchuck.com):</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="59"/>
        <source>@mailchuck.com</source>
        <translation>@mailchuck.com</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="286"/>
        <source>Registration failed:</source>
        <translation>Registrácia zlyhala:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="288"/>
        <source>The requested email address is not available, please try a new one.</source>
        <translation>Požadovaná e-mailová adresa nie je k dispozícii, skúste znova.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="334"/>
        <source>Sending email gateway registration request</source>
        <translation>Odosielam žiadosť o registráciu na e-mailovej bráne</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="342"/>
        <source>Sending email gateway unregistration request</source>
        <translation>Odosielam žiadosť o odhlásenie z e-mailovej brány</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="348"/>
        <source>Sending email gateway status request</source>
        <translation>Odosielam žiadosť o stav e-mailovej brány</translation>
    </message>
</context>
<context>
    <name>EmailGatewayRegistrationDialog</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2266"/>
        <source>Registration failed:</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2266"/>
        <source>The requested email address is not available, please try a new one. Fill out the new desired email address (including @mailchuck.com) below:</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="102"/>
        <source>Email gateway registration</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="103"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.
Please type the desired email address (including @mailchuck.com) below:</source>
        <translation type="unfinished"/>
    </message>
</context>
<context>
    <name>Mailchuck</name>
    <message>
        <location filename="../bitmessageqt/account.py" line="243"/>
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
        <translation># Tento text môžete použiť na konfiguráciu vášho účtu na e-mailovej bráne
# odkomentujte nastavenia, ktoré chcete použiť
# Tu sú možnosti:
#
# pgp: server
# E-mailová brána bude za vás vytvárať a udržiavať PGP kľúče a podpisovať, overovať,
# šifrovať a dešifrovať vaše e-maily. Ak chcete používať PGP, ale ste leniví,
# toto je voľba pre vás. Vyžaduje predplatné.
#
# pgp: local
# E-mailová brána nebude za vás vykonávať operácie PGP. Môžete buď
# nepoužívať PGP vôbec, alebo ho použiť lokálne.
#
# attachments: yes
# Prichádzajúce prílohy v e-maile budú nahrané na MEGA.nz, a môžete si ich odtiaľ stiahnuť
# pomocou odkazu v správe. Vyžaduje predplatné.
#
# attachments: no
# Prílohy budú ignorované.
#
# archive: yes
# Prichádzajúce e-maily budú archivované na serveri. Použite, ak potrebujete
# pomoc s problémami, alebo potrebujete doklad pre tretie strán o obsahu e-mailov. Táto voľba však
# znamená, že prevádzkovateľ služby budú môcť čítať vaše e-maily
# aj potom, ako vám budú doručené
#
# archive: no
# Prichádzajúce e-maily budú odstránené zo servera, akonáhle vám budú doručené
#
# masterpubkey_btc: BIP44 xpub kľúč alebo electrum v1 základ (seed)
# offset_btc: celé číslo (predvolená 0)
# feeamount: číslo s max. 8 desatinnými miest
# feecurrency: BTC, XBT, USD, EUR alebo GBP
# Ak chcete účtovať ľuďom, ktorí vám posielať e-maily, použite tieto parametre. Ak vám potom
# neznáma osoba pošle e-mail, bude požiadaná o zaplatenie poplatku
# určeného týmito premennými.
# feeamount je výška platby
# feecurrency je mena, v ktorej sa bude počítať
# Keďže systém používa deterministické verejné kľúče, platby obdržíte priamo vy
# Ak ju chcete túto funkciu opäť vypnúť, nastavte &quot;feeamount&quot; na 0. Vyžaduje
# predplatné.
</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="170"/>
        <source>Reply to sender</source>
        <translation>Odpovedať odosielateľovi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="172"/>
        <source>Reply to channel</source>
        <translation>Odpoveď na kanál</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="174"/>
        <source>Add sender to your Address Book</source>
        <translation>Pridať odosielateľa do adresára</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="178"/>
        <source>Add sender to your Blacklist</source>
        <translation>Pridať odosielateľa do svojho zoznamu zakázaných</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="364"/>
        <source>Move to Trash</source>
        <translation>Presunúť do koša</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="185"/>
        <source>Undelete</source>
        <translation>Obnoviť</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="188"/>
        <source>View HTML code as formatted text</source>
        <translation>Zobraziť HTML kód ako formátovaný text</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="192"/>
        <source>Save message as...</source>
        <translation>Uložiť správu ako...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="196"/>
        <source>Mark Unread</source>
        <translation>Označiť ako neprečítané</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="336"/>
        <source>New</source>
        <translation>Nová</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="121"/>
        <source>Enable</source>
        <translation>Aktivovať</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="124"/>
        <source>Disable</source>
        <translation>Deaktivovať</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="127"/>
        <source>Set avatar...</source>
        <translation>Nastaviť avatar ...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="117"/>
        <source>Copy address to clipboard</source>
        <translation>Kopírovať adresu do clipboardu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="283"/>
        <source>Special address behavior...</source>
        <translation>Zvláštne správanie adresy...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="244"/>
        <source>Email gateway</source>
        <translation>E-mailová brána</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="114"/>
        <source>Delete</source>
        <translation>Zmazať</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="299"/>
        <source>Send message to this address</source>
        <translation>Poslať správu na túto adresu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="307"/>
        <source>Subscribe to this address</source>
        <translation>Prihlásiť sa k odberu tejto adresy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="319"/>
        <source>Add New Address</source>
        <translation>Pridať novú adresu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="367"/>
        <source>Copy destination address to clipboard</source>
        <translation>Kopírovať cieľovú adresu do clipboardu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="371"/>
        <source>Force send</source>
        <translation>Vynútiť odoslanie</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="587"/>
        <source>One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?</source>
        <translation>Jedna z vašich adries, %1, je stará verzia adresy, 1. Verzie adresy 1 už nie sú podporované. Odstrániť ju teraz?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1034"/>
        <source>Waiting for their encryption key. Will request it again soon.</source>
        <translation>Čakanie na šifrovací kľúč príjemcu. Čoskoro bude vyžiadaný znova.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="990"/>
        <source>Encryption key request queued.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1040"/>
        <source>Queued.</source>
        <translation>Vo fronte.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1043"/>
        <source>Message sent. Waiting for acknowledgement. Sent at %1</source>
        <translation>Správa odoslaná. Čakanie na potvrdenie. Odoslaná %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1046"/>
        <source>Message sent. Sent at %1</source>
        <translation>Správa odoslaná. Odoslaná %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1002"/>
        <source>Need to do work to send message. Work is queued.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1052"/>
        <source>Acknowledgement of the message received %1</source>
        <translation>Potvrdenie prijatia správy %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2140"/>
        <source>Broadcast queued.</source>
        <translation>Rozoslanie vo fronte.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1061"/>
        <source>Broadcast on %1</source>
        <translation>Rozoslané 1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1064"/>
        <source>Problem: The work demanded by the recipient is more difficult than you are willing to do. %1</source>
        <translation>Problém: práca požadovná príjemcom je oveľa ťažšia, než je povolené v nastaveniach. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1067"/>
        <source>Problem: The recipient&apos;s encryption key is no good. Could not encrypt message. %1</source>
        <translation>Problém: šifrovací kľúč príjemcu je nesprávny. Nie je možné zašifrovať správu. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1070"/>
        <source>Forced difficulty override. Send should start soon.</source>
        <translation>Obmedzenie obtiažnosti práce zrušené. Odosielanie by malo čoskoro začať.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1073"/>
        <source>Unknown status: %1 %2</source>
        <translation>Neznámy stav: %1 %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1612"/>
        <source>Not Connected</source>
        <translation>Nepripojený</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1204"/>
        <source>Show Bitmessage</source>
        <translation>Ukázať Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="709"/>
        <source>Send</source>
        <translation>Odoslať</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1227"/>
        <source>Subscribe</source>
        <translation>Prihlásiť sa k odberu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1233"/>
        <source>Channel</source>
        <translation>Kanál</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="755"/>
        <source>Quit</source>
        <translation>Ukončiť</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1459"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.</source>
        <translation>Kľúče môžete spravovať úpravou súboru keys.dat, ktorý je uložený v rovnakom adresári ako tento program. Tento súbor je dôležité zálohovať.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1463"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file.</source>
        <translation>Kľúče môžete spravovať úpravou súboru keys.dat, ktorý je uložený v adresári
%1 
Tento súbor je dôležité zálohovať.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1470"/>
        <source>Open keys.dat?</source>
        <translation>Otvoriť keys.dat?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1467"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Kľúče môžete spravovať úpravou súboru keys.dat, ktorý je uložený v rovnakom adresári ako tento program. Tento súbor je dôležité zálohovať. Chcete tento súbor teraz otvoriť? (Nezabudnite zatvoriť Bitmessage pred vykonaním akýchkoľvek zmien.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1470"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Kľúče môžete spravovať úpravou súboru keys.dat, ktorý je uložený v adresári
%1 
Tento súbor je dôležité zálohovať. Chcete tento súbor teraz otvoriť? (Nezabudnite zatvoriť Bitmessage pred vykonaním akýchkoľvek zmien.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1477"/>
        <source>Delete trash?</source>
        <translation>Vyprázdniť kôš?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1477"/>
        <source>Are you sure you want to delete all trashed messages?</source>
        <translation>Ste si istí, že chcete všetky správy z koša odstrániť?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1495"/>
        <source>bad passphrase</source>
        <translation>zlé heslo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1495"/>
        <source>You must type your passphrase. If you don&apos;t have one then this is not the form for you.</source>
        <translation>Je nutné zadať prístupové heslo. Ak heslo nemáte, tento formulár nie je pre Vás.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1518"/>
        <source>Bad address version number</source>
        <translation>Nesprávne číslo verzie adresy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1508"/>
        <source>Your address version number must be a number: either 3 or 4.</source>
        <translation>Číslo verzie adresy musí byť číslo: buď 3 alebo 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1518"/>
        <source>Your address version number must be either 3 or 4.</source>
        <translation>Vaše číslo verzie adresy musí byť buď 3 alebo 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1608"/>
        <source>Chan name needed</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1608"/>
        <source>You didn&apos;t enter a chan name.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1628"/>
        <source>Address already present</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1628"/>
        <source>Could not add chan because it appears to already be one of your identities.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1632"/>
        <source>Success</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1603"/>
        <source>Successfully created chan. To let others join your chan, give them the chan name and this Bitmessage address: %1. This address also appears in &apos;Your Identities&apos;.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1612"/>
        <source>Address too new</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1612"/>
        <source>Although that Bitmessage address might be valid, its version number is too new for us to handle. Perhaps you need to upgrade Bitmessage.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1616"/>
        <source>Address invalid</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1616"/>
        <source>That Bitmessage address is not valid.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1624"/>
        <source>Address does not match chan name</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1624"/>
        <source>Although the Bitmessage address you entered was valid, it doesn&apos;t match the chan name.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1632"/>
        <source>Successfully joined chan. </source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1597"/>
        <source>Connection lost</source>
        <translation>Spojenie bolo stratené</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1647"/>
        <source>Connected</source>
        <translation>Spojený</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1765"/>
        <source>Message trashed</source>
        <translation>Správa odstránenia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1854"/>
        <source>The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate.</source>
        <translation>TTL (doba životnosti) je čas, počas ktorého bude sieť udržiavať správu. Príjemca musí správu prijať počas tejto životnosti. Keď odosielateľov Bitmessage nedostane po vypršaní životnosti potvrdenie o prijatí, automaticky správu odošle znova. Čím vyššia doba životnosti, tým viac práce musí počítač odosielateľa vykonat na odoslanie správy. Zvyčajne je vhodná doba životnosti okolo štyroch-piatich dní.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1899"/>
        <source>Message too long</source>
        <translation>Správa je príliš dlhá</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1899"/>
        <source>The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.</source>
        <translation>Správa, ktorú skúšate poslať, má %1 bajtov naviac. (Maximum je 261 644 bajtov). Prosím pred odoslaním skrátiť.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1941"/>
        <source>Error: Your account wasn&apos;t registered at an email gateway. Sending registration now as %1, please wait for the registration to be processed before retrying sending.</source>
        <translation>Chyba: Váš účet nebol registrovaný na e-mailovej bráne. Skúšam registrovať ako %1, prosím počkajte na spracovanie registrácie pred opakovaným odoslaním správy.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2008"/>
        <source>Error: Bitmessage addresses start with BM-   Please check %1</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2011"/>
        <source>Error: The address %1 is not typed or copied correctly. Please check it.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2014"/>
        <source>Error: The address %1 contains invalid characters. Please check it.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2017"/>
        <source>Error: The address version in %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2020"/>
        <source>Error: Some data encoded in the address %1 is too short. There might be something wrong with the software of your acquaintance.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2023"/>
        <source>Error: Some data encoded in the address %1 is too long. There might be something wrong with the software of your acquaintance.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2026"/>
        <source>Error: Some data encoded in the address %1 is malformed. There might be something wrong with the software of your acquaintance.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2029"/>
        <source>Error: Something is wrong with the address %1.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2092"/>
        <source>Error: You must specify a From address. If you don&apos;t have one, go to the &apos;Your Identities&apos; tab.</source>
        <translation>Chyba: musíte zadať adresu &quot;Od&quot;. Ak žiadnu nemáte, prejdite na kartu &quot;Vaše identity&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2026"/>
        <source>Address version number</source>
        <translation>Číslo verzie adresy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2026"/>
        <source>Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Čo sa týka adresy %1, Bitmessage nepozná číslo verzie adresy %2. Možno by ste mali upgradenúť Bitmessage na najnovšiu verziu.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2030"/>
        <source>Stream number</source>
        <translation>Číslo prúdu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2030"/>
        <source>Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Čo sa týka adresy %1, Bitmessage nespracováva číslo prúdu %2. Možno by ste mali upgradenúť Bitmessage na najnovšiu verziu.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2035"/>
        <source>Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won&apos;t send until you connect.</source>
        <translation>Upozornenie: momentálne nie ste pripojení. Bitmessage vykoná prácu potrebnú na odoslanie správy, ale odoslať ju môže, až keď budete pripojení.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2084"/>
        <source>Message queued.</source>
        <translation>Správa vo fronte.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2088"/>
        <source>Your &apos;To&apos; field is empty.</source>
        <translation>Pole &quot;Komu&quot; je prázdne.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2149"/>
        <source>Right click one or more entries in your address book and select &apos;Send message to this address&apos;.</source>
        <translation>Vybertie jednu alebo viacero položiek v adresári, pravým tlačidlom myši zvoľte &quot;Odoslať správu na túto adresu&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2165"/>
        <source>Fetched address from namecoin identity.</source>
        <translation>Prebratá adresa z namecoin-ovej identity.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2277"/>
        <source>New Message</source>
        <translation>Nová správa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2260"/>
        <source>From </source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2638"/>
        <source>Sending email gateway registration request</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="59"/>
        <source>Address is valid.</source>
        <translation>Adresa je platná.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="93"/>
        <source>The address you entered was invalid. Ignoring it.</source>
        <translation>Zadaná adresa bola neplatná a bude ignorovaná.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2307"/>
        <source>Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.</source>
        <translation>Chyba: tú istú adresu nemožno pridať do adresára dvakrát. Ak chcete, môžete skúsiť premenovať existujúcu menovku.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3333"/>
        <source>Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want.</source>
        <translation>Chyba: nemožno pridať rovnakú adresu k odberu dvakrát. Keď chcete, môžete premenovať existujúci záznam.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2429"/>
        <source>Restart</source>
        <translation>Reštart</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2415"/>
        <source>You must restart Bitmessage for the port number change to take effect.</source>
        <translation>Aby sa zmena čísla portu prejavila, musíte reštartovať Bitmessage.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2429"/>
        <source>Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any).</source>
        <translation>Bitmessage bude odteraz používať proxy, ale ak chcete ukončiť existujúce spojenia, musíte Bitmessage manuálne reštartovať.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2458"/>
        <source>Number needed</source>
        <translation>Číslo potrebné</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2458"/>
        <source>Your maximum download and upload rate must be numbers. Ignoring what you typed.</source>
        <translation>Maxímálna rýchlosť príjmu a odoslania musí byť uvedená v číslach. Ignorujem zadané údaje.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2538"/>
        <source>Will not resend ever</source>
        <translation>Nikdy opätovne neodosielať</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2538"/>
        <source>Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent.</source>
        <translation>Upozornenie: časový limit, ktorý ste zadali, je menší ako čas, ktorý Bitmessage čaká na prvý pokus o opätovné zaslanie, a preto vaše správy nebudú nikdy opätovne odoslané.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2611"/>
        <source>Sending email gateway unregistration request</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2615"/>
        <source>Sending email gateway status request</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="136"/>
        <source>Passphrase mismatch</source>
        <translation>Nezhoda hesla</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="136"/>
        <source>The passphrase you entered twice doesn&apos;t match. Try again.</source>
        <translation>Zadané heslá sa rôznia. Skúste znova.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="144"/>
        <source>Choose a passphrase</source>
        <translation>Vyberte heslo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="144"/>
        <source>You really do need a passphrase.</source>
        <translation>Heslo je skutočne potrebné.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3012"/>
        <source>Address is gone</source>
        <translation>Adresa zmizla</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3012"/>
        <source>Bitmessage cannot find your address %1. Perhaps you removed it?</source>
        <translation>Bitmessage nemôže nájsť vašu adresu %1. Možno ste ju odstránili?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3015"/>
        <source>Address disabled</source>
        <translation>Adresa deaktivovaná</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3015"/>
        <source>Error: The address from which you are trying to send is disabled. You&apos;ll have to enable it on the &apos;Your Identities&apos; tab before using it.</source>
        <translation>Chyba: adresa, z ktorej sa pokúšate odoslať, je neaktívna. Pred použitím ju musíte aktivovať v karte &quot;Vaše identity&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3020"/>
        <source>Entry added to the Address Book. Edit the label to your liking.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3090"/>
        <source>Entry added to the blacklist. Edit the label to your liking.</source>
        <translation>Záznam pridaný na zoznam zakázaných. Upravte označenie podľa vašich predstáv.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3095"/>
        <source>Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want.</source>
        <translation>Chyba: tú istú adresu nemožno pridať na zoznam zakázaných dvakrát. Ak chcete, môžete skúsiť premenovať existujúce označenie.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3237"/>
        <source>Moved items to trash.</source>
        <translation>Položky presunuté do koša.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3181"/>
        <source>Undeleted item.</source>
        <translation>Položka obnovená.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3205"/>
        <source>Save As...</source>
        <translation>Uložiť ako...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3214"/>
        <source>Write error.</source>
        <translation>Chyba pri zapisovaní.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3317"/>
        <source>No addresses selected.</source>
        <translation>Nevybraná žiadna adresa.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3372"/>
        <source>If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the subscription?</source>
        <translation>Ak odstránite odber, správy, ktoré ste už prijali, sa stanú nedostupné. Možno by ste mali zvážit namiesto toho odber deaktivovať. Deaktivované odbery nebudú prijímať nové správy, ale stále si môžete pozrieť správy, ktoré ste už prijali.

Ste si istý, že chcete odber odstrániť?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3615"/>
        <source>If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the channel?</source>
        <translation>Ak odstránite kanál, správy, ktoré ste už prijali, sa stanú nedostupné. Možno by ste mali zvážit namiesto toho kanál deaktivovať. Deaktivované kanály nebudú prijímať nové správy, ale stále si môžete pozrieť správy, ktoré ste už prijali.

Ste si istý, že chcete kanál odstrániť?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3745"/>
        <source>Do you really want to remove this avatar?</source>
        <translation>Naozaj chcete odstrániť tento avatar?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3753"/>
        <source>You have already set an avatar for this address. Do you really want to overwrite it?</source>
        <translation>Pre túto adresu ste už ste nastavili avatar. Naozaj ho chcete ho zmeniť?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4151"/>
        <source>Start-on-login not yet supported on your OS.</source>
        <translation>Spustenie pri prihlásení zatiaľ pre váš operačný systém nie je podporované.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4144"/>
        <source>Minimize-to-tray not yet supported on your OS.</source>
        <translation>Minimalizovanie do panelu úloh zatiaľ pre váš operačný systém nie je podporované.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4147"/>
        <source>Tray notifications not yet supported on your OS.</source>
        <translation>Oblasť oznámení zatiaľ pre váš operačný systém nie je podporovaná.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4318"/>
        <source>Testing...</source>
        <translation>Testujem...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4237"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="35"/>
        <source>The address should start with &apos;&apos;BM-&apos;&apos;</source>
        <translation>Adresa by mala začínať &apos;&apos;BM-&apos;&apos;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="40"/>
        <source>The address is not typed or copied correctly (the checksum failed).</source>
        <translation>Nesprávne zadaná alebo skopírovaná adresa (kontrolný súčet zlyhal).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="46"/>
        <source>The version number of this address is higher than this software can support. Please upgrade Bitmessage.</source>
        <translation>Číslo verzie tejto adresy je vyššie ako tento softvér podporuje. Prosím inovujte Bitmessage.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="52"/>
        <source>The address contains invalid characters.</source>
        <translation>Adresa obsahuje neplatné znaky.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="57"/>
        <source>Some data encoded in the address is too short.</source>
        <translation>Niektoré dáta zakódované v adrese sú príliš krátke.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="62"/>
        <source>Some data encoded in the address is too long.</source>
        <translation>Niektoré dáta zakódované v adrese sú príliš dlhé.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="67"/>
        <source>Some data encoded in the address is malformed.</source>
        <translation>Niektoré dáta zakódované v adrese sú poškodené.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4289"/>
        <source>Enter an address above.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="171"/>
        <source>Address is an old type. We cannot display its past broadcasts.</source>
        <translation>Starý typ adresy. Nie je možné zobraziť jej predchádzajúce hromadné správy.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="186"/>
        <source>There are no recent broadcasts from this address to display.</source>
        <translation>Neboli nájdené žiadne nedávne hromadé správy z tejto adresy.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4374"/>
        <source>You are using TCP port %1. (This can be changed in the settings).</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="665"/>
        <source>Bitmessage</source>
        <translation>Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="666"/>
        <source>Identities</source>
        <translation>Identity</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="667"/>
        <source>New Identity</source>
        <translation>Nová identita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="730"/>
        <source>Search</source>
        <translation>Hľadaj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="731"/>
        <source>All</source>
        <translation>Všetky</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="738"/>
        <source>To</source>
        <translation>Príjemca</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="740"/>
        <source>From</source>
        <translation>Odosielateľ</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="742"/>
        <source>Subject</source>
        <translation>Predmet</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="735"/>
        <source>Message</source>
        <translation>Správa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="744"/>
        <source>Received</source>
        <translation>Prijaté</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="683"/>
        <source>Messages</source>
        <translation>Správy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="686"/>
        <source>Address book</source>
        <translation>Adresár</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="688"/>
        <source>Address</source>
        <translation>Adresa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="689"/>
        <source>Add Contact</source>
        <translation>Pridať kontakt</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="690"/>
        <source>Fetch Namecoin ID</source>
        <translation>Získať identifikátor namecoin-u</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="697"/>
        <source>Subject:</source>
        <translation>Predmet:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="696"/>
        <source>From:</source>
        <translation>Odosielateľ:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="693"/>
        <source>To:</source>
        <translation>Príjemca:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="695"/>
        <source>Send ordinary Message</source>
        <translation>Poslať obyčajnú správu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="699"/>
        <source>Send Message to your Subscribers</source>
        <translation>Poslať správu vašim odberateľom</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="700"/>
        <source>TTL:</source>
        <translation>Doba životnosti:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="727"/>
        <source>Subscriptions</source>
        <translation>Odbery</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="711"/>
        <source>Add new Subscription</source>
        <translation>Pridať nový odber</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="745"/>
        <source>Chans</source>
        <translation>Kanály</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="729"/>
        <source>Add Chan</source>
        <translation>Pridať kanál</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="750"/>
        <source>File</source>
        <translation>Súbor</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="761"/>
        <source>Settings</source>
        <translation>Nastavenia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="757"/>
        <source>Help</source>
        <translation>Pomoc</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="753"/>
        <source>Import keys</source>
        <translation>Importovať kľúče</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="754"/>
        <source>Manage keys</source>
        <translation>Spravovať kľúče</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="756"/>
        <source>Ctrl+Q</source>
        <translation>Ctrl+Q</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="758"/>
        <source>F1</source>
        <translation>F1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="759"/>
        <source>Contact support</source>
        <translation>Kontaktovať používateľskú podporu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="760"/>
        <source>About</source>
        <translation>O</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="762"/>
        <source>Regenerate deterministic addresses</source>
        <translation>Znova vytvoriť deterministické adresy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="763"/>
        <source>Delete all trashed messages</source>
        <translation>Odstrániť všetky správy z koša</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="764"/>
        <source>Join / Create chan</source>
        <translation>Pripojiť / vytvoriť kanál</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="181"/>
        <source>All accounts</source>
        <translation>Všetky účty</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="47"/>
        <source>Zoom level %1%</source>
        <translation>Úroveň priblíženia %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="90"/>
        <source>Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.</source>
        <translation>Chyba: nemožno pridať rovnakú adresu do vášho zoznamu dvakrát. Keď chcete, môžete premenovať existujúci záznam.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="111"/>
        <source>Add new entry</source>
        <translation>Pridať nový záznam</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4334"/>
        <source>Display the %1 recent broadcast(s) from this address.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1774"/>
        <source>New version of PyBitmessage is available: %1. Download it from https://github.com/Bitmessage/PyBitmessage/releases/latest</source>
        <translation>K dispozícii je nová verzia PyBitmessage: %1. Môžete ju stiahnuť na https://github.com/Bitmessage/PyBitmessage/releases/latest</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2774"/>
        <source>Waiting for PoW to finish... %1%</source>
        <translation>Čakám na ukončenie práce... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2784"/>
        <source>Shutting down Pybitmessage... %1%</source>
        <translation>Ukončujem PyBitmessage... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2802"/>
        <source>Waiting for objects to be sent... %1%</source>
        <translation>Čakám na odoslanie objektov... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2822"/>
        <source>Saving settings... %1%</source>
        <translation>Ukladám nastavenia... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2835"/>
        <source>Shutting down core... %1%</source>
        <translation>Ukončujem jadro... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2841"/>
        <source>Stopping notifications... %1%</source>
        <translation>Zastavujem oznámenia... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2845"/>
        <source>Shutdown imminent... %1%</source>
        <translation>Posledná fáza ukončenia... %1%</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/bitmessageui.py" line="706"/>
        <source>%n hour(s)</source>
        <translation><numerusform>%n hodina</numerusform><numerusform>%n hodiny</numerusform><numerusform>%n hodín</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="829"/>
        <source>%n day(s)</source>
        <translation><numerusform>%n deň</numerusform><numerusform>%n dni</numerusform><numerusform>%n dní</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2742"/>
        <source>Shutting down PyBitmessage... %1%</source>
        <translation>Ukončujem PyBitmessage... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1148"/>
        <source>Sent</source>
        <translation>Odoslané</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="91"/>
        <source>Generating one new address</source>
        <translation>Vytváram jednu novú adresu</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="153"/>
        <source>Done generating address. Doing work necessary to broadcast it...</source>
        <translation>Vytváranie adresy ukončené. Vykonávam prácu potrebnú na rozoslanie...</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="170"/>
        <source>Generating %1 new addresses.</source>
        <translation>Vytváram %1 nových adries.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="247"/>
        <source>%1 is already in &apos;Your Identities&apos;. Not adding it again.</source>
        <translation>%1 sa už nachádza medzi vášmi identitami, nepridávam dvojmo.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="283"/>
        <source>Done generating address</source>
        <translation>Vytváranie adresy ukončené</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="228"/>
        <source>SOCKS5 Authentication problem: %1</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="584"/>
        <source>Disk full</source>
        <translation>Disk plný</translation>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="584"/>
        <source>Alert: Your disk or data storage volume is full. Bitmessage will now exit.</source>
        <translation>Upozornenie: Váš disk alebo priestor na ukladanie dát je plný. Bitmessage bude teraz ukončený.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="747"/>
        <source>Error! Could not find sender address (your address) in the keys.dat file.</source>
        <translation>Chyba! Nemožno nájsť adresu odosielateľa (vašu adresu) v súbore keys.dat.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="495"/>
        <source>Doing work necessary to send broadcast...</source>
        <translation>Vykonávam prácu potrebnú na rozoslanie...</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="518"/>
        <source>Broadcast sent on %1</source>
        <translation>Rozoslané %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="587"/>
        <source>Encryption key was requested earlier.</source>
        <translation>Šifrovací klúč bol vyžiadaný.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="624"/>
        <source>Sending a request for the recipient&apos;s encryption key.</source>
        <translation>Odosielam požiadavku na kľúč príjemcu.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="639"/>
        <source>Looking up the receiver&apos;s public key</source>
        <translation>Hľadám príjemcov verejný kľúč</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="673"/>
        <source>Problem: Destination is a mobile device who requests that the destination be included in the message but this is disallowed in your settings.  %1</source>
        <translation>Problém: adresa príjemcu je na mobilnom zariadení a požaduje, aby správy obsahovali nezašifrovanú adresu príjemcu. Vaše nastavenia však túto možnost nemajú povolenú. %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="687"/>
        <source>Doing work necessary to send message.
There is no required difficulty for version 2 addresses like this.</source>
        <translation>Vykonávam prácu potrebnú na odoslanie správy.
Adresy verzie dva, ako táto, nepožadujú obtiažnosť.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="701"/>
        <source>Doing work necessary to send message.
Receiver&apos;s required difficulty: %1 and %2</source>
        <translation>Vykonávam prácu potrebnú na odoslanie správy.
Priímcova požadovaná obtiažnosť: %1 a %2</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="710"/>
        <source>Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do. %3</source>
        <translation>Problém: Práca požadovná príjemcom (%1 a %2) je obtiažnejšia, ako máte povolené. %3</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="722"/>
        <source>Problem: You are trying to send a message to yourself or a chan but your encryption key could not be found in the keys.dat file. Could not encrypt message. %1</source>
        <translation>Problém: skúšate odslať správu sami sebe, ale nemôžem nájsť šifrovací kľúč v súbore keys.dat. Nemožno správu zašifrovať: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1049"/>
        <source>Doing work necessary to send message.</source>
        <translation>Vykonávam prácu potrebnú na odoslanie...</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="845"/>
        <source>Message sent. Waiting for acknowledgement. Sent on %1</source>
        <translation>Správa odoslaná. Čakanie na potvrdenie. Odoslaná %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1037"/>
        <source>Doing work necessary to request encryption key.</source>
        <translation>Vykonávam prácu potrebnú na vyžiadanie šifrovacieho kľúča.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="961"/>
        <source>Broadcasting the public key request. This program will auto-retry if they are offline.</source>
        <translation>Rozosielam požiadavku na verejný kľúč. Ak nebude príjemca spojený zo sieťou, budem skúšať znova.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="963"/>
        <source>Sending public key request. Waiting for reply. Requested at %1</source>
        <translation>Odosielam požiadavku na verejný kľúč. Čakám na odpoveď. Vyžiadaný %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="235"/>
        <source>UPnP port mapping established on port %1</source>
        <translation>Mapovanie portov UPnP vytvorené na porte %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="264"/>
        <source>UPnP port mapping removed</source>
        <translation>Mapovanie portov UPnP zrušené</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="248"/>
        <source>Mark all messages as read</source>
        <translation>Označiť všetky správy ako prečítané</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2636"/>
        <source>Are you sure you would like to mark all messages read?</source>
        <translation>Ste si istý, že chcete označiť všetky správy ako prečítané?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1058"/>
        <source>Doing work necessary to send broadcast.</source>
        <translation>Vykonávam prácu potrebnú na rozoslanie.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2708"/>
        <source>Proof of work pending</source>
        <translation>Vykonávaná práca</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2708"/>
        <source>%n object(s) pending proof of work</source>
        <translation><numerusform>%n objekt čaká na vykonanie práce</numerusform><numerusform>%n objekty čakajú na vykonanie práce</numerusform><numerusform>%n objektov čaká na vykonanie práce</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2708"/>
        <source>%n object(s) waiting to be distributed</source>
        <translation><numerusform>%n objekt čaká na rozoslanie</numerusform><numerusform>%n objekty čakajú na rozoslanie</numerusform><numerusform>%n objektov čaká na rozoslanie</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2708"/>
        <source>Wait until these tasks finish?</source>
        <translation>Počkať, kým tieto úlohy skončia?</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="211"/>
        <source>Problem communicating with proxy: %1. Please check your network settings.</source>
        <translation>Problém komunikácie s proxy: %1. Prosím skontrolujte nastavenia siete.</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="240"/>
        <source>SOCKS5 Authentication problem: %1. Please check your SOCKS5 settings.</source>
        <translation>Problém autentikácie SOCKS5: %1. Prosím skontrolujte nastavenia SOCKS5.</translation>
    </message>
    <message>
        <location filename="../class_receiveDataThread.py" line="171"/>
        <source>The time on your computer, %1, may be wrong. Please verify your settings.</source>
        <translation>Čas na vašom počítači, %1, možno nie je správny. Prosím, skontrolujete nastavenia.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="101"/>
        <source>The name %1 was not found.</source>
        <translation>Meno % nenájdené.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="110"/>
        <source>The namecoin query failed (%1)</source>
        <translation>Dotaz prostredníctvom namecoinu zlyhal (%1)</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="113"/>
        <source>The namecoin query failed.</source>
        <translation>Dotaz prostredníctvom namecoinu zlyhal.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="119"/>
        <source>The name %1 has no valid JSON data.</source>
        <translation>Meno %1 neobsahuje planté JSON dáta.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="127"/>
        <source>The name %1 has no associated Bitmessage address.</source>
        <translation>Meno %1 nemá priradenú žiadnu adresu Bitmessage.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="147"/>
        <source>Success!  Namecoind version %1 running.</source>
        <translation>Úspech! Namecoind verzia %1 spustený.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="153"/>
        <source>Success!  NMControll is up and running.</source>
        <translation>Úspech! NMControl spustený.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="156"/>
        <source>Couldn&apos;t understand NMControl.</source>
        <translation>Nie je rozumieť NMControl-u.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="120"/>
        <source>Your GPU(s) did not calculate correctly, disabling OpenCL. Please report to the developers.</source>
        <translation>Vaša grafická karta vykonala nesprávny výpočet, deaktivujem OpenCL. Prosím, pošlite správu vývojárom.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3793"/>
        <source>Set notification sound...</source>
        <translation>Nastaviť zvuk oznámenia...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="637"/>
        <source>
        Welcome to easy and secure Bitmessage
            * send messages to other people
            * send broadcast messages like twitter or
            * discuss in chan(nel)s with other people
        </source>
        <translation>
Vitajte v jednoduchom a bezpečnom Bitmessage
* posielajte správy druhým ľuďom
* posielajte hromadné správy ako na twitteri alebo
* diskutuje s druhými v kanáloch
</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="820"/>
        <source>not recommended for chans</source>
        <translation>nie je odporúčaná pre kanály</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1213"/>
        <source>Quiet Mode</source>
        <translation>Tichý režim</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1603"/>
        <source>Problems connecting? Try enabling UPnP in the Network Settings</source>
        <translation>Problémy so spojením? Skúste zapnúť UPnP v Nastaveniach siete</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1928"/>
        <source>You are trying to send an email instead of a bitmessage. This requires registering with a gateway. Attempt to register?</source>
        <translation>Pokúšate sa odoslať e-mail namiesto bitmessage. To si vyžaduje registráciu na bráne. Pokúsiť sa o registráciu?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1960"/>
        <source>Error: Bitmessage addresses start with BM-   Please check the recipient address %1</source>
        <translation>Chyba: Bitmessage adresy začínajú s BM- Prosím skontrolujte adresu príjemcu %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1966"/>
        <source>Error: The recipient address %1 is not typed or copied correctly. Please check it.</source>
        <translation>Chyba: adresa príjemcu %1 nie je na správne napísaná alebo skopírovaná. Prosím skontrolujte ju.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1972"/>
        <source>Error: The recipient address %1 contains invalid characters. Please check it.</source>
        <translation>Chyba: adresa príjemcu %1 obsahuje neplatné znaky. Prosím skontrolujte ju.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1978"/>
        <source>Error: The version of the recipient address %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</source>
        <translation>Chyba: verzia adresy príjemcu %1 je príliš veľká. Buď musíte aktualizovať program Bitmessage alebo váš známy s vami žartuje.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1986"/>
        <source>Error: Some data encoded in the recipient address %1 is too short. There might be something wrong with the software of your acquaintance.</source>
        <translation>Chyba: niektoré údaje zakódované v adrese príjemcu %1 sú príliš krátke. Softér vášho známeho možno nefunguje správne.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1994"/>
        <source>Error: Some data encoded in the recipient address %1 is too long. There might be something wrong with the software of your acquaintance.</source>
        <translation>Chyba: niektoré údaje zakódované v adrese príjemcu %1 sú príliš dlhé. Softvér vášho známeho možno nefunguje správne.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2002"/>
        <source>Error: Some data encoded in the recipient address %1 is malformed. There might be something wrong with the software of your acquaintance.</source>
        <translation>Chyba: niektoré údaje zakódované v adrese príjemcu %1 sú poškodené. Softvér vášho známeho možno nefunguje správne.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2010"/>
        <source>Error: Something is wrong with the recipient address %1.</source>
        <translation>Chyba: niečo s adresou príjemcu %1 je nie je v poriadku.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2160"/>
        <source>Error: %1</source>
        <translation>Chyba: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2277"/>
        <source>From %1</source>
        <translation>Od %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2719"/>
        <source>Synchronisation pending</source>
        <translation>Prebieha synchronizácia</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2719"/>
        <source>Bitmessage hasn&apos;t synchronised with the network, %n object(s) to be downloaded. If you quit now, it may cause delivery delays. Wait until the synchronisation finishes?</source>
        <translation><numerusform>Bitmessage sa nezosynchronizoval so sieťou, treba prevzať ešte %n objekt. Keď program ukončíte teraz, môže dôjsť k spozdeniu doručenia. Počkať, kým sa synchronizácia ukončí?</numerusform><numerusform>Bitmessage sa nezosynchronizoval so sieťou, treba prevzať ešte %n objekty. Keď program ukončíte teraz, môže dôjsť k spozdeniu doručenia. Počkať, kým sa synchronizácia ukončí?</numerusform><numerusform>Bitmessage sa nezosynchronizoval so sieťou, treba prevzať ešte %n objektov. Keď program ukončíte teraz, môže dôjsť k spozdeniu doručenia. Počkať, kým sa synchronizácia ukončí?</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2731"/>
        <source>Not connected</source>
        <translation>Nepripojený</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2731"/>
        <source>Bitmessage isn&apos;t connected to the network. If you quit now, it may cause delivery delays. Wait until connected and the synchronisation finishes?</source>
        <translation>Bitmessage nie je pripojený do siete. Keď program ukončíte teraz, môže dôjsť k spozdeniu doručenia. Počkať, kým dôjde k spojeniu a prebehne synchronizácia?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2746"/>
        <source>Waiting for network connection...</source>
        <translation>Čakám na pripojenie do siete...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2756"/>
        <source>Waiting for finishing synchronisation...</source>
        <translation>Čakám na ukončenie synchronizácie...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3811"/>
        <source>You have already set a notification sound for this address book entry. Do you really want to overwrite it?</source>
        <translation>Pre túto adresu ste už ste nastavili zvuk oznámenia. Naozaj ho chcete ho zmeniť?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4028"/>
        <source>Error occurred: could not load message from disk.</source>
        <translation>Chyba pri načítaní správy.</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/address_dialogs.py" line="194"/>
        <source>Display the %n recent broadcast(s) from this address.</source>
        <translation><numerusform>Zobraziť poslednú %1 hromadnú správu z tejto adresy.</numerusform><numerusform>Zobraziť posledné %1 hromadné správy z tejto adresy.</numerusform><numerusform>Zobraziť posledných %1 hromadných správ z tejto adresy.</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="658"/>
        <source>Go online</source>
        <translation>Pripojiť k sieti</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="658"/>
        <source>Go offline</source>
        <translation>Odpojiť od siete</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="707"/>
        <source>Clear</source>
        <translation>Vymazať</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="11"/>
        <source>inbox</source>
        <translation>Doručená pošta</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="12"/>
        <source>new</source>
        <translation>Nová doručená pošta</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="13"/>
        <source>sent</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="14"/>
        <source>trash</source>
        <translation type="unfinished"/>
    </message>
</context>
<context>
    <name>MessageView</name>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="72"/>
        <source>Follow external link</source>
        <translation>Nasledovať externý odkaz</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="72"/>
        <source>The link &quot;%1&quot; will open in a browser. It may be a security risk, it could de-anonymise you or download malicious data. Are you sure?</source>
        <translation>Odkaz &quot;%1&quot; bude otvorený v prehliadači. Tento úkon môže predstavovať bezpečnostné riziko a Vás deanonymizovať, alebo vykonať škodlivú činnost. Ste si istý?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="117"/>
        <source>HTML detected, click here to display</source>
        <translation>Nájdené HTML, kliknite sem ak chcete zobraziť</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="126"/>
        <source>Click here to disable HTML</source>
        <translation>Kliknite sem na vypnutie HTML</translation>
    </message>
</context>
<context>
    <name>MsgDecode</name>
    <message>
        <location filename="../helper_msgcoding.py" line="72"/>
        <source>The message has an unknown encoding.
Perhaps you should upgrade Bitmessage.</source>
        <translation>Správa má neznáme kódovanie.
Možno by ste mali inovovať Bitmessage.</translation>
    </message>
    <message>
        <location filename="../helper_msgcoding.py" line="73"/>
        <source>Unknown encoding</source>
        <translation>Neznáme kódovanie</translation>
    </message>
</context>
<context>
    <name>NewAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="14"/>
        <source>Create new Address</source>
        <translation>Vytvoriť novú adresu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="23"/>
        <source>Here you may generate as many addresses as you like. Indeed, creating and abandoning addresses is encouraged. You may generate addresses by using either random numbers or by using a passphrase. If you use a passphrase, the address is called a &quot;deterministic&quot; address.
The &apos;Random Number&apos; option is selected by default but deterministic addresses have several pros and cons:</source>
        <translation>Tu si môžete vygenerovať toľko adries, koľko chcete. Vytváranie a opúšťanie adries je vrelo odporúčané. Adresy môžete generovať buď pomocou náhodných čísel alebo pomocou hesla. Ak používate heslo, takáto adresa sa nazýva &quot;deterministická&quot;.
Predvoľba je pomocou generátora náhodných čísiel, ale deterministické adresy majú niekoľko výhod a nevýhod:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="37"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Pros:&lt;br/&gt;&lt;/span&gt;You can recreate your addresses on any computer from memory. &lt;br/&gt;You need-not worry about backing up your keys.dat file as long as you can remember your passphrase. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Cons:&lt;br/&gt;&lt;/span&gt;You must remember (or write down) your passphrase if you expect to be able to recreate your keys if they are lost. &lt;br/&gt;You must remember the address version number and the stream number along with your passphrase. &lt;br/&gt;If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt; &lt;span style=&quot; font-weight:600;&quot;&gt;Pros: &lt;br/&gt;&lt;/span&gt;Svoje adresy môžete znovu vytvoriť na ľubovoľnom počítači z pamäte.&lt;br/&gt;Dokým si pamätáte heslo, nemusíte sa starať o zálohovanie keys.dat&lt;br/&gt; &lt;span style=&quot; font-weight:600;&quot;Nevýhody: &lt;br/&gt;&lt;/span&gt;Ak chcete znovu vytvoriť kľúče ak ich stratíte, musíte si pamätať (alebo niekam zapísať) heslo. &lt;br/&gt; Zároveň si musíte si zapamätať aj číslo verzie adresy a číslo toku.&lt;br/&gt;Ak si zvolíte slabé prístupové heslo a niekto na internete ho uhádne, napr. hrubou silou, môže čítať vaše správy a odosielať ich za vás.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="66"/>
        <source>Use a random number generator to make an address</source>
        <translation>Vytvoriť novú adresu pomocou generátora náhodných čísel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="79"/>
        <source>Use a passphrase to make addresses</source>
        <translation>Vytvoriť novú adresu pomocou hesla</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="89"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Stráviť niekoľko minút výpočtového času navyše, aby adresa(y) bola o 1 alebo 2 znakov kratšia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="96"/>
        <source>Make deterministic addresses</source>
        <translation>Vytvoriť deterministické adresy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="102"/>
        <source>Address version number: 4</source>
        <translation>Číslo verzie adresy: 4</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="109"/>
        <source>In addition to your passphrase, you must remember these numbers:</source>
        <translation>Okrem svojho hesla si musíte zapamätať tiejto údaje:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="126"/>
        <source>Passphrase</source>
        <translation>Heslo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="133"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Počet adries, ktoré majú byť na základe vášho hesla vytvorené:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="153"/>
        <source>Stream number: 1</source>
        <translation>Číslo prúdu: 1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="173"/>
        <source>Retype passphrase</source>
        <translation>Opakovať heslo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="200"/>
        <source>Randomly generate address</source>
        <translation>Adresu generovať náhodne</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="206"/>
        <source>Label (not shown to anyone except you)</source>
        <translation>Označenie (zobrazené len vám a nikomu inému)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="216"/>
        <source>Use the most available stream</source>
        <translation>Použiť najviac prístupný prúd</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="226"/>
        <source> (best if this is the first of many addresses you will create)</source>
        <translation>(najlepšie, ak ide o prvú z mnohých vytvorených adries)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="236"/>
        <source>Use the same stream as an existing address</source>
        <translation>Použiť ten istý prúd ako existujúca adresa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="246"/>
        <source>(saves you some bandwidth and processing power)</source>
        <translation>(ušetrí nejaké množstvo prenesených dát a výpočtový výkon)</translation>
    </message>
</context>
<context>
    <name>NewSubscriptionDialog</name>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.ui" line="20"/>
        <source>Add new entry</source>
        <translation>Pridať nový záznam</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.ui" line="26"/>
        <source>Label</source>
        <translation>Označenie</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.ui" line="36"/>
        <source>Address</source>
        <translation>Adresa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.ui" line="59"/>
        <source>Enter an address above.</source>
        <translation>Zadajte adresu vyššie.</translation>
    </message>
</context>
<context>
    <name>SpecialAddressBehaviorDialog</name>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="14"/>
        <source>Special Address Behavior</source>
        <translation>Zvláštne správanie adresy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="20"/>
        <source>Behave as a normal address</source>
        <translation>Správanie ako normálna adresa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="30"/>
        <source>Behave as a pseudo-mailing-list address</source>
        <translation>Správanie ako pseudo poštový zoznam</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="37"/>
        <source>Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).</source>
        <translation>Správy prijaté na adresu pseudo poštového zoznamu budú automaticky rozoslaná odberateľom (a teda budú zverejnené).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="47"/>
        <source>Name of the pseudo-mailing-list:</source>
        <translation>Meno pseudo poštového zoznamu:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="230"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation>Toto je adresa kanálu. Nie je možné ju používať ako pseudo poštový zoznam.</translation>
    </message>
</context>
<context>
    <name>aboutDialog</name>
    <message>
        <location filename="../bitmessageqt/about.ui" line="14"/>
        <source>About</source>
        <translation>O</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="68"/>
        <source>PyBitmessage</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="69"/>
        <source>version ?</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/about.ui" line="69"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distributed under the MIT/X11 software license; see &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Šírený pod licenciou na softvér MIT / X11; pozri &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.ui" line="59"/>
        <source>This is Beta software.</source>
        <translation>Toto je beta softvér.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright Â© 2012-2016 Jonathan Warren&lt;br/&gt;Copyright Â© 2013-2016 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"/>
    </message>
    <message encoding="UTF-8">
        <location filename="../bitmessageqt/about.ui" line="49"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright © 2012-2016 Jonathan Warren&lt;br/&gt;Copyright © 2013-2017 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright © 2012-2016 Jonathan Warren&lt;br/&gt;Copyright © 2013-2017 Vývojári Bitmessage&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
</context>
<context>
    <name>blacklist</name>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="17"/>
        <source>Use a Blacklist (Allow all incoming messages except those on the Blacklist)</source>
        <translation>Použiť ako zoznam zakázaných (prijať všetky prichádzajúce správy s výnimkou odosielateľov na zozname)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="27"/>
        <source>Use a Whitelist (Block all incoming messages except those on the Whitelist)</source>
        <translation>Použiť ako zoznam povolených (blokovať všetky prichádzajúce správy s výnimkou odosielateľov na zozname)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="34"/>
        <source>Add new entry</source>
        <translation>Pridať nový záznam</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="85"/>
        <source>Name or Label</source>
        <translation>Meno alebo popis</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="90"/>
        <source>Address</source>
        <translation>Adresa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="150"/>
        <source>Blacklist</source>
        <translation>Zoznam zakázaných</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="152"/>
        <source>Whitelist</source>
        <translation>Zoznam povolených</translation>
    </message>
</context>
<context>
    <name>connectDialog</name>
    <message>
        <location filename="../bitmessageqt/connect.ui" line="14"/>
        <source>Bitmessage</source>
        <translation>Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.ui" line="20"/>
        <source>Bitmessage won&apos;t connect to anyone until you let it. </source>
        <translation>Bitmessage sa s nikým nespojí, dokým to nepovolíte.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.ui" line="27"/>
        <source>Connect now</source>
        <translation>Spojiť teraz</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.ui" line="37"/>
        <source>Let me configure special network settings first</source>
        <translation>Najprv upraviť zvláštne sieťové nastavenia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.ui" line="44"/>
        <source>Work offline</source>
        <translation>Zostať odpojený</translation>
    </message>
</context>
<context>
    <name>helpDialog</name>
    <message>
        <location filename="../bitmessageqt/help.ui" line="14"/>
        <source>Help</source>
        <translation>Pomoc</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.ui" line="20"/>
        <source>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</source>
        <translation>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.ui" line="30"/>
        <source>As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:</source>
        <translation>Keďže Bitmessage je projekt založený na spolupráci, pomoc možno nájsť na internete v Bitmessage Wiki:</translation>
    </message>
</context>
<context>
    <name>iconGlossaryDialog</name>
    <message>
        <location filename="../bitmessageqt/iconglossary.ui" line="20"/>
        <source>Icon Glossary</source>
        <translation>Legenda ikon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.ui" line="36"/>
        <source>You have no connections with other peers. </source>
        <translation>Nemáte žiadne spojenia s partnerskými uzlami.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.ui" line="53"/>
        <source>You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn&apos;t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.</source>
        <translation>Vykonali ste aspoň jedno vychádzajúce spojenie do siete, ale ešte ste nenaviazali žiadne prichádzajúce spojenia. Váš firewall alebo domáci router pravdepodobne nie je nakonfigurovaný tak, aby presmeroval prichádzajúce TCP spojenia k vášmu počítaču. Bitmessage bude fungovať v pohode, keby ste však mali fungujúce prichádzajúce spojenia, pomôžete sieti Bitmessage a váš uzol bude lepšie pripojený.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="85"/>
        <source>You are using TCP port ?. (This can be changed in the settings).</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.ui" line="96"/>
        <source>You do have connections with other peers and your firewall is correctly configured.</source>
        <translation>Máte spojenia s partnerskými uzlami a vaša brána firewall je nastavená správne.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/dialogs.py" line="58"/>
        <source>You are using TCP port %1. (This can be changed in the settings).</source>
        <translation>Používate port TCP %1. (Možno zmeniť v nastaveniach).</translation>
    </message>
</context>
<context>
    <name>networkstatus</name>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="39"/>
        <source>Total connections:</source>
        <translation>Spojení spolu:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="185"/>
        <source>Since startup:</source>
        <translation>Od spustenia:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="201"/>
        <source>Processed 0 person-to-person messages.</source>
        <translation>Spracovaných 0 bežných správ.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="230"/>
        <source>Processed 0 public keys.</source>
        <translation>Spracovaných 0 verejných kľúčov.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="217"/>
        <source>Processed 0 broadcasts.</source>
        <translation>Spracovaných 0 hromadných správ.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="282"/>
        <source>Inventory lookups per second: 0</source>
        <translation>Vyhľadaní v inventári za sekundu: 0</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="243"/>
        <source>Objects to be synced:</source>
        <translation>Zostáva synchronizovať objektov:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="152"/>
        <source>Stream #</source>
        <translation>Prúd #</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="116"/>
        <source>Connections</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="171"/>
        <source>Since startup on %1</source>
        <translation>Od spustenia %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="90"/>
        <source>Down: %1/s  Total: %2</source>
        <translation>Prijatých: %1/s  Spolu: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="92"/>
        <source>Up: %1/s  Total: %2</source>
        <translation>Odoslaných: %1/s  Spolu: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="153"/>
        <source>Total Connections: %1</source>
        <translation>Spojení spolu: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="163"/>
        <source>Inventory lookups per second: %1</source>
        <translation>Vyhľadaní v inventári za sekundu: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="256"/>
        <source>Up: 0 kB/s</source>
        <translation>Odoslaných: 0 kB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="269"/>
        <source>Down: 0 kB/s</source>
        <translation>Prijatých: 0 kB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="749"/>
        <source>Network Status</source>
        <translation>Stav siete</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="57"/>
        <source>byte(s)</source>
        <translation><numerusform>bajt</numerusform><numerusform>bajty</numerusform><numerusform>bajtov</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="68"/>
        <source>Object(s) to be synced: %n</source>
        <translation><numerusform>Zostáva synchronizovať %n objekt</numerusform><numerusform>Zostáva synchronizovať %n objekty</numerusform><numerusform>Zostáva synchronizovať %n objektov</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="72"/>
        <source>Processed %n person-to-person message(s).</source>
        <translation><numerusform>Spracovaná %n bežná správa.</numerusform><numerusform>Spracované %n bežné správy.</numerusform><numerusform>Spracovaných %n bežných správ.</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="77"/>
        <source>Processed %n broadcast message(s).</source>
        <translation><numerusform>Spracovaná %n hromadná správa.</numerusform><numerusform>Spracované %n hromadné správy.</numerusform><numerusform>Spracovaných %n hromadných správ.</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="82"/>
        <source>Processed %n public key(s).</source>
        <translation><numerusform>Spracovaný %n verejný kľúč.</numerusform><numerusform>Spracované %n verejné kľúče.</numerusform><numerusform>Spracovaných %n verejných kľúčov.</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="120"/>
        <source>Peer</source>
        <translation>Partnerský uzol</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="123"/>
        <source>IP address or hostname</source>
        <translation>IP adresa alebo názov hostiteľa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="128"/>
        <source>Rating</source>
        <translation>Hodnotenie</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="131"/>
        <source>PyBitmessage tracks the success rate of connection attempts to individual nodes. The rating ranges from -1 to 1 and affects the likelihood of selecting the node in the future</source>
        <translation>PyBitmessage sleduje úspešnosť pokusov o pripojenie k jednotlivým uzlom. Hodnotenie sa pohybuje od -1 do 1 a ovplyvňuje pravdepodobnosť výberu uzla v budúcnosti</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="136"/>
        <source>User agent</source>
        <translation>Užívateľský agent</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="139"/>
        <source>Peer&apos;s self-reported software</source>
        <translation>Software hlásený partnerským uzlom</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="144"/>
        <source>TLS</source>
        <translation>TLS</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="147"/>
        <source>Connection encryption</source>
        <translation>Šifrovanie pripojenia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="155"/>
        <source>List of streams negotiated between you and the peer</source>
        <translation>Zoznam prúdov dohodnutých medzi vami a partnerom</translation>
    </message>
</context>
<context>
    <name>newChanDialog</name>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="97"/>
        <source>Dialog</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="98"/>
        <source>Create a new chan</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="103"/>
        <source>Join a chan</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="100"/>
        <source>Create a chan</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="101"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly then the chan will be secure and private. If you and someone else both create a chan with the same chan name then it is currently very likely that they will be the same chan.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="105"/>
        <source>Chan name:</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="104"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a normal person-to-person message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="106"/>
        <source>Chan bitmessage address:</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="26"/>
        <source>Create or join a chan</source>
        <translation>Vytvoriť alebo pripojiť sa ku kanálu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="41"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly, then the chan will be secure and private. However if you and someone else both create a chan with the same chan name, the same chan will be shared.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Kanál existuje, keď skupina ľudí zdieľa tie isté dešifrovacie kľúče. Kľúče a bitmessage adresa používané v kanáli sú generované zo slova alebo frázy (názov kanálu). Ak chcete poslať správu všetkým užívateľom v kanáli, pošlite bežnú správu na adresu kanálu.&lt;/p&gt;&lt;p&gt;Kanály sú experimentálne a vôbec sa nedajú moderovať/cenzúrovať.&lt;/p&gt;&lt;p&gt;Zadajte názov pre váš kanál. Ak zvolíte dostatočne zložitý názov kanálu (napríklad zložité a jedinečné heslo) a nikto z vašich známych ho nebude verejne zdieľať, potom bude kanál bezpečný a súkromný. Ak vy a niekto iný vytvoríte kanál s rovnakým názvom, bude to v skutočnosti ten istý kanál, ktorý budete zdieľať.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="56"/>
        <source>Chan passphrase/name:</source>
        <translation>Názov kanálu:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="63"/>
        <source>Optional, for advanced usage</source>
        <translation>Nepovinné, pre pokročilé možnosti</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="76"/>
        <source>Chan address</source>
        <translation>Adresa kanálu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="101"/>
        <source>Please input chan name/passphrase:</source>
        <translation>Prosím zadajte názov kanálu</translation>
    </message>
</context>
<context>
    <name>newchandialog</name>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="38"/>
        <source>Successfully created / joined chan %1</source>
        <translation>Kanál %1 úspešne vytvorený/pripojený</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="44"/>
        <source>Chan creation / joining failed</source>
        <translation>Vytvorenie/pripojenie kanálu zlyhalo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="50"/>
        <source>Chan creation / joining cancelled</source>
        <translation>Vytvorenie/pripojenie kanálu zrušené</translation>
    </message>
</context>
<context>
    <name>proofofwork</name>
    <message>
        <location filename="../proofofwork.py" line="163"/>
        <source>C PoW module built successfully.</source>
        <translation>C PoW modul úspešne zostavený.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="165"/>
        <source>Failed to build C PoW module. Please build it manually.</source>
        <translation>Zostavenie C PoW modulu zlyhalo. Prosím, zostavte ho manuálne.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="167"/>
        <source>C PoW module unavailable. Please build it.</source>
        <translation>C PoW modul nie je dostupný. Prosím, zostavte ho.</translation>
    </message>
</context>
<context>
    <name>qrcodeDialog</name>
    <message>
        <location filename="../plugins/qrcodeui.py" line="67"/>
        <source>QR-code</source>
        <translation>QR kód</translation>
    </message>
</context>
<context>
    <name>regenerateAddressesDialog</name>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="14"/>
        <source>Regenerate Existing Addresses</source>
        <translation>Znova vytvoriť existujúce adresy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="30"/>
        <source>Regenerate existing addresses</source>
        <translation>Znova vytvoriť existujúce adresy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="36"/>
        <source>Passphrase</source>
        <translation>Heslo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="53"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Počet adries, ktoré majú byť na základe vášho hesla vytvorené:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="89"/>
        <source>Address version number:</source>
        <translation>Číslo verzie adresy:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="131"/>
        <source>Stream number:</source>
        <translation>Číslo prúdu:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="153"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="173"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Stráviť niekoľko minút výpočtového času navyše, aby adresa(y) bola o 1 alebo 2 znakov kratšia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="180"/>
        <source>You must check (or not check) this box just like you did (or didn&apos;t) when you made your addresses the first time.</source>
        <translation>Je nutné začiarknuť (alebo nezačiarknuť) toto políčko tak isto, ako keď ste vytvárali svoje adresy prvýkrát.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="190"/>
        <source>If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.</source>
        <translation>Ak ste v minulosti používali deterministické adresy, ale stratili ich kvôli nehode (ako je napráklad zlyhanie pevného disku), môžete ich vytvoriť znova. Ak ste na vytvorenie adries použili generátor náhodných čísel, potom je vám tento formulár zbytočný.</translation>
    </message>
</context>
<context>
    <name>settingsDialog</name>
    <message>
        <location filename="../bitmessageqt/settings.py" line="453"/>
        <source>Settings</source>
        <translation>Nastavenia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="454"/>
        <source>Start Bitmessage on user login</source>
        <translation>Spustiť Bitmessage pri prihlásení používateľa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="455"/>
        <source>Tray</source>
        <translation>Panel úloh</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="456"/>
        <source>Start Bitmessage in the tray (don&apos;t show main window)</source>
        <translation>Spustiť Bitmessage v paneli úloh (nezobrazovať hlavné okno)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="457"/>
        <source>Minimize to tray</source>
        <translation>Minimalizovať do panelu úloh</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="458"/>
        <source>Close to tray</source>
        <translation>Zavrieť do panelu úloh</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="460"/>
        <source>Show notification when message received</source>
        <translation>Zobraziť oznámenie, ked obdržíte správu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="461"/>
        <source>Run in Portable Mode</source>
        <translation>Spustiť v prenosnom režime</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="462"/>
        <source>In Portable Mode, messages and config files are stored in the same directory as the program rather than the normal application-data folder. This makes it convenient to run Bitmessage from a USB thumb drive.</source>
        <translation>V prenosnom režime budú správy a konfiguračné súbory uložené v rovnakom priečinku ako program, namiesto v bežnom priečinku pre údaje aplikácie. Vďaka tomu je pohodlné používať Bitmessage na USB kľúči.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="463"/>
        <source>Willingly include unencrypted destination address when sending to a mobile device</source>
        <translation>Povoliť pridanie nezašifrovanej adresy prijímateľa pri posielaní na mobilné zariadenie</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="464"/>
        <source>Use Identicons</source>
        <translation>Zobrazuj identikony (ikony automaticky vytvorené pre každú adresu)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="465"/>
        <source>Reply below Quote</source>
        <translation>Odpovedať pod citáciou</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="466"/>
        <source>Interface Language</source>
        <translation>Jazyk rozhrania</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="467"/>
        <source>System Settings</source>
        <comment>system</comment>
        <translation>Systémové nastavenia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="468"/>
        <source>User Interface</source>
        <translation>Užívateľské rozhranie</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="469"/>
        <source>Listening port</source>
        <translation>Prijímajúci port</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="470"/>
        <source>Listen for connections on port:</source>
        <translation>Prijímať spojenia na porte:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="471"/>
        <source>UPnP:</source>
        <translation>UPnP:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="472"/>
        <source>Bandwidth limit</source>
        <translation>Obmedzenie šírky pásma</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Maximum download rate (kB/s): [0: unlimited]</source>
        <translation>Maximálna rýchlosť sťahovania (kB/s): [0: bez obmedzenia]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="474"/>
        <source>Maximum upload rate (kB/s): [0: unlimited]</source>
        <translation>Maximálna rýchlosť odosielania (kB/s): [0: bez obmedzenia]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="476"/>
        <source>Proxy server / Tor</source>
        <translation>Proxy server / Tor</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="477"/>
        <source>Type:</source>
        <translation>Typ:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="478"/>
        <source>Server hostname:</source>
        <translation>Názov hostiteľského servera:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="501"/>
        <source>Port:</source>
        <translation>Port:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="480"/>
        <source>Authentication</source>
        <translation>Overovanie</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="502"/>
        <source>Username:</source>
        <translation>Používateľské meno:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="482"/>
        <source>Pass:</source>
        <translation>Heslo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="483"/>
        <source>Listen for incoming connections when using proxy</source>
        <translation>Prijímať prichádzajúce spojenia ak je používaný proxy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="484"/>
        <source>none</source>
        <translation>žiadny</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="485"/>
        <source>SOCKS4a</source>
        <translation>SOCKS4a</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="486"/>
        <source>SOCKS5</source>
        <translation>SOCKS5</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="487"/>
        <source>Network Settings</source>
        <translation>Nastavenia siete</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="488"/>
        <source>Total difficulty:</source>
        <translation>Celková obtiažnosť:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="489"/>
        <source>The &apos;Total difficulty&apos; affects the absolute amount of work the sender must complete. Doubling this value doubles the amount of work.</source>
        <translation>&apos;Celková obtiažnosť&apos; ovplyvňuje celkové množstvo práce, ktorú musí odosielateľ vykonať. Zdvojnásobenie tejto hodnoty zdvojnásobí potrebné množstvo práce.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="490"/>
        <source>Small message difficulty:</source>
        <translation>Obtiažnosť malých správ:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="491"/>
        <source>When someone sends you a message, their computer must first complete some work. The difficulty of this work, by default, is 1. You may raise this default for new addresses you create by changing the values here. Any new addresses you create will require senders to meet the higher difficulty. There is one exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically notify them when you next send a message that they need only complete the minimum amount of work: difficulty 1. </source>
        <translation>Keď vám niekto pošle správu, ich počítač musí najprv vykonať nejakú prácu. Obtiažnosť tejto práce je predvolená na 1. Túto predvoľbu môžete zvýšiť nastavením parametrov. Každá novo vygenerovaná adresa bude od odosielateľa požadovať túto zvýšenú obtiažnosť. Existuje však výnimka: ak vášho známeho máte v adresári, pri poslaní nasledujúcej správy im Bitmessage automaticky oznámi, že im stačí minimálne množstvo práce: obtiažnosť 1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="492"/>
        <source>The &apos;Small message difficulty&apos; mostly only affects the difficulty of sending small messages. Doubling this value makes it almost twice as difficult to send a small message but doesn&apos;t really affect large messages.</source>
        <translation>&apos;Obtiažnosť malých správ&apos; ovplyvňuje najmä náročnosť odosielania malých správ. Zdvojnásobenie tejto hodnoty zdvojnásobí potrebné množstvo práce na odoslanie malých správ, ale veľké správy príliš neovplyvňuje.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="493"/>
        <source>Demanded difficulty</source>
        <translation>Požadovaná obtiažnosť</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="494"/>
        <source>Here you may set the maximum amount of work you are willing to do to send a message to another person. Setting these values to 0 means that any value is acceptable.</source>
        <translation>Tu môžete nastaviť maximálne množstvo práce, ktorú váš počítač je ochotný urobiť pre odoslanie správy inej osobe. Nastavenie týchto hodnôt na 0 znamená, že ľubovoľné množtvo práce je prijateľné.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="495"/>
        <source>Maximum acceptable total difficulty:</source>
        <translation>Maximálna prijateľná celková obtiažnosť:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="496"/>
        <source>Maximum acceptable small message difficulty:</source>
        <translation>Maximálna prijateľná obtiažnost malých správ:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="497"/>
        <source>Max acceptable difficulty</source>
        <translation>Max. prijateľná obtiažnosť</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Hardware GPU acceleration (OpenCL)</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="499"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage can utilize a different Bitcoin-based program called Namecoin to make addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage address, you can simply tell him to send a message to &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Getting your own Bitmessage address into Namecoin is still rather difficult).&lt;/p&gt;&lt;p&gt;Bitmessage can use either namecoind directly or a running nmcontrol instance.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage sa môže pripojiť k systému s názvom Namecoin, ktorý je podobný Bitcoinu, a s jeho pomocou používať používateľsky príjemné identifikátory. Napríklad namiesto zverejňovania dlhej Bitmessage adresy môžete jednoducho zverejniť meno, povedzme &lt;span style=&quot; font-style:italic;&quot;&gt;test.&lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Dostať vašu vlastnú adresu do Namecoin-u je však zatiaľ pomerne zložité).&lt;/p&gt;&lt;p&gt;Bitmessage sa môže pripojiť priamo na namecoind, alebo na aktívnu inštanciu nmcontrol.&lt;/p&gt;&lt;/body&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="500"/>
        <source>Host:</source>
        <translation>Hostiteľ:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="503"/>
        <source>Password:</source>
        <translation>Heslo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="504"/>
        <source>Test</source>
        <translation>Test</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="505"/>
        <source>Connect to:</source>
        <translation>Pripojiť ku:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="506"/>
        <source>Namecoind</source>
        <translation>Namecoind</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="507"/>
        <source>NMControl</source>
        <translation>NMControl</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="508"/>
        <source>Namecoin integration</source>
        <translation>Integrácia namecoin-u</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="509"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;By default, if you send a message to someone and he is offline for more than two days, Bitmessage will send the message again after an additional two days. This will be continued with exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain number of days or months.&lt;/p&gt;&lt;p&gt;Leave these input fields blank for the default behavior. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Predvoľba spôsobí opätovné odoslanie správy ak nebude príjemca pripojený na sieť viac ako dva dni. Tieto pokusy budú opakované, dokým príjemca nepotvrdí obdržanie správy. Toto správanie môžete zmeniť zadaním počtu dní alebo mesiacov, po ktorých má Bitmessage s opätovným odosielaním prestať.&lt;/p&gt;&lt;p&gt;Vstupné polia nechajte prázdne, ak chcete predvolené správanie. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="510"/>
        <source>Give up after</source>
        <translation>Vzdať po</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="511"/>
        <source>and</source>
        <translation>a</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="512"/>
        <source>days</source>
        <translation>dňoch</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="513"/>
        <source>months.</source>
        <translation>mesiacoch.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="514"/>
        <source>Resends Expire</source>
        <translation>Vypršanie opätovného odosielania</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="459"/>
        <source>Hide connection notifications</source>
        <translation>Skryť oznámenia o stave pripojenia</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="475"/>
        <source>Maximum outbound connections: [0: none]</source>
        <translation>Maximálny počet odchádzajúcich spojení: [0: žiadne]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="498"/>
        <source>Hardware GPU acceleration (OpenCL):</source>
        <translation>Hardvérové GPU urýchľovanie (OpenCL):</translation>
    </message>
</context>
</TS>