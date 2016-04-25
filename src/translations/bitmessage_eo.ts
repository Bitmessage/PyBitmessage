<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS><TS version="2.0" language="eo" sourcelanguage="en">
<context>
    <name>AddAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="62"/>
        <source>Add new entry</source>
        <translation>Aldoni novan elementon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="63"/>
        <source>Label</source>
        <translation>Etikedo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="64"/>
        <source>Address</source>
        <translation>Adreso</translation>
    </message>
</context>
<context>
    <name>EmailGatewayDialog</name>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="67"/>
        <source>Email gateway</source>
        <translation>Retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="68"/>
        <source>Register on email gateway</source>
        <translation>Registri je retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="69"/>
        <source>Account status at email gateway</source>
        <translation>Stato de retpoŝta kluza konto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="70"/>
        <source>Change account settings at email gateway</source>
        <translation>Ŝanĝu agordojn de konto ĉe retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="71"/>
        <source>Unregister from email gateway</source>
        <translation>Malregistri de retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="72"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.</source>
        <translation>Retpoŝta kluzo ebligas al vi komunikadi kun retpoŝtaj uzantoj. Nuntempe, nur la retpoŝta kluzo de Mailchuck (@mailchuck.com) estas disponebla.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="73"/>
        <source>Desired email address (including @mailchuck.com):</source>
        <translation>Dezirata retpoŝta adreso (kune kun @mailchuck.com):</translation>
    </message>
</context>
<context>
    <name>EmailGatewayRegistrationDialog</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2238"/>
        <source>Registration failed:</source>
        <translation>Registrado malsukcesis:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2238"/>
        <source>The requested email address is not available, please try a new one. Fill out the new desired email address (including @mailchuck.com) below:</source>
        <translation>La dezirata retpoŝtadreso ne estas disponebla, bonvolu provi kun alia. Entajpu novan deziratan adreson (kune kun @mailchuck.com) sube:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="102"/>
        <source>Email gateway registration</source>
        <translation>Registrado je retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="103"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.
Please type the desired email address (including @mailchuck.com) below:</source>
        <translation>Retpoŝta kluzo ebligas al vi komunikadi kun retpoŝtaj uzantoj. Nuntempe, nur la retpoŝta kluzo de Mailchuck (@mailchuck.com) estas disponebla.
Bonvolu entajpi deziratan retpoŝtadreson (kune kun @mailchuck.com) sube:</translation>
    </message>
</context>
<context>
    <name>Mailchuck</name>
    <message>
        <location filename="../bitmessageqt/account.py" line="220"/>
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
        <translation># Tie ĉi vi povas agordi vian konton ĉe retpoŝta kluzo
# Malkomenti agordojn kiujn vi volas uzi
# Jenaj agordoj:
#
# pgp: server
# La retpoŝta kluzo kreos kaj prizorgos PGP-ŝlosilojn por vi por subskribi,
# verigi, ĉifri kaj deĉifri kiel vi. Se vi volas uzi PGP-on, sed vi estas laca,
# uzu tion. Bezonas abonon.
#
# pgp: local
# La retpoŝta kluzo ne faros PGP-operaciojn kiel vi. Vi povas aŭ ne uzi PGP-on
# ĝenerale aŭ uzi ĝin loke.
#
# attachments: yes
# Alvenaj kunsendaĵoj en retmesaĝoj estos alŝutitaj al MEGA.nz, kaj vi povos
# elŝuti ilin de tie per alklaki ligilon. Bezonas abonon.
#
# attachments: no
# Oni ignoros kunsendaĵojn.
#
# archive: yes
# Viaj alvenontaj retmesaĝoj estos arĥivitaj en la servilo. Uzu tion, se vi
# bezonas helpon kun senerarigado aŭ vi bezonas ekstere-liveritan pruvon de
# retmesaĝoj. Tamen tio signifas, ke la manipulisto de servo eblos legi viajn
# retmesaĝojn eĉ kiam tiam oni estos liverinta ilin al vi.
#
# archive: no
# Alvenaj mesaĝoj estos forigitaj de la servilo tuj post ili estos liveritaj al vi.
#
# masterpubkey_btc: BIP44 xpub ŝlosilo aŭ electrum v1 publika fontsendo (seed)
# offset_btc: entjera (integer) datumtipo (defaŭlte 0)
# feeamount: nombro kun maksimume 8 decimalaj lokoj
# feecurrency: BTC, XBT, USD, EUR aŭ GBP
# Uzu tiujn se vi volas pagoŝarĝi homojn kiuj sendos al vi retmesaĝojn. Se tiu
# agordo estas ŝaltita kaj iu ajn sendos al vi retmesaĝon, li devos pagi difinan
# sendokoston. Por re-malaktivigi ĝin, agordu &quot;feeamount&quot; al 0. Bezonas abonon.
</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="177"/>
        <source>Reply to sender</source>
        <translation>Respondi al sendinto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="179"/>
        <source>Reply to channel</source>
        <translation>Respondi al kanalo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="181"/>
        <source>Add sender to your Address Book</source>
        <translation>Aldoni sendinton al via adresaro</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="185"/>
        <source>Add sender to your Blacklist</source>
        <translation>Aldoni sendinton al via nigra listo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="363"/>
        <source>Move to Trash</source>
        <translation>Movi al rubujo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="192"/>
        <source>Undelete</source>
        <translation>Malforviŝi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="195"/>
        <source>View HTML code as formatted text</source>
        <translation>Montri HTML-n kiel aranĝita teksto </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="199"/>
        <source>Save message as...</source>
        <translation>Konservi mesaĝon kiel...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="203"/>
        <source>Mark Unread</source>
        <translation>Marki kiel nelegita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="335"/>
        <source>New</source>
        <translation>Nova</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="122"/>
        <source>Enable</source>
        <translation>Ŝalti</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="125"/>
        <source>Disable</source>
        <translation>Malŝalti</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="128"/>
        <source>Set avatar...</source>
        <translation>Agordi avataron...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="118"/>
        <source>Copy address to clipboard</source>
        <translation>Kopii adreson al tondejo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="286"/>
        <source>Special address behavior...</source>
        <translation>Speciala sinteno de adreso...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="251"/>
        <source>Email gateway</source>
        <translation>Retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="115"/>
        <source>Delete</source>
        <translation>Forviŝi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="302"/>
        <source>Send message to this address</source>
        <translation>Sendi mesaĝon al tiu adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="310"/>
        <source>Subscribe to this address</source>
        <translation>Aboni tiun adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="318"/>
        <source>Add New Address</source>
        <translation>Aldoni novan adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="366"/>
        <source>Copy destination address to clipboard</source>
        <translation>Kopii cel-adreson al tondejo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="370"/>
        <source>Force send</source>
        <translation>Devigi sendadon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="578"/>
        <source>One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?</source>
        <translation>Iu de viaj adresoj, %1, estas malnova versio 1 adreso. Versioj 1 adresoj ne estas jam subtenataj. Ĉu ni povas forviŝi ĝin?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="798"/>
        <source>1 hour</source>
        <translation>1 horo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="800"/>
        <source>%1 hours</source>
        <translation>%1 horoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="803"/>
        <source>%1 days</source>
        <translation>%1 tagoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="979"/>
        <source>Waiting for their encryption key. Will request it again soon.</source>
        <translation>Atendante ilian ĉifroŝlosilon. Baldaŭ petos ĝin denove.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="982"/>
        <source>Encryption key request queued.</source>
        <translation>Peto por ĉifroŝlosilo envicigita.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="985"/>
        <source>Queued.</source>
        <translation>En atendovico.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="988"/>
        <source>Message sent. Waiting for acknowledgement. Sent at %1</source>
        <translation>Mesaĝo sendita. Atendante konfirmon. Sendita je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="991"/>
        <source>Message sent. Sent at %1</source>
        <translation>Mesaĝo sendita. Sendita je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="994"/>
        <source>Need to do work to send message. Work is queued.</source>
        <translation>Devas labori por sendi mesaĝon. Laboro en atendovico.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="997"/>
        <source>Acknowledgement of the message received %1</source>
        <translation>Ricevis konfirmon de la mesaĝo je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2113"/>
        <source>Broadcast queued.</source>
        <translation>Elsendo en atendovico.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1003"/>
        <source>Broadcast on %1</source>
        <translation>Elsendo je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1006"/>
        <source>Problem: The work demanded by the recipient is more difficult than you are willing to do. %1</source>
        <translation>Problemo: la demandita laboro de la ricevonto estas pli malfacila ol vi pretas fari. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1009"/>
        <source>Problem: The recipient&apos;s encryption key is no good. Could not encrypt message. %1</source>
        <translation>Problemo: la ĉifroŝlosilo de la ricevonto estas rompita. Ne povis ĉifri la mesaĝon. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1012"/>
        <source>Forced difficulty override. Send should start soon.</source>
        <translation>Devigita superado de limito de malfacilaĵo. Sendado devus baldaŭ komenci.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1015"/>
        <source>Unknown status: %1 %2</source>
        <translation>Nekonata stato: %1 %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1678"/>
        <source>Not Connected</source>
        <translation>Ne konektita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1138"/>
        <source>Show Bitmessage</source>
        <translation>Montri Bitmesaĝon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="683"/>
        <source>Send</source>
        <translation>Sendi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1153"/>
        <source>Subscribe</source>
        <translation>Aboni</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1159"/>
        <source>Channel</source>
        <translation>Kanalo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="728"/>
        <source>Quit</source>
        <translation>Eliri</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1509"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.</source>
        <translation>Vi povas administri viajn ŝlosilojn redaktante la dosieron keys.dat en la sama dosierujo kiel tiu programo. Estas grava ke vi faru savkopion de tiu dosiero.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1513"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file.</source>
        <translation>Vi povas administri viajn ŝlosilojn redaktante la dosieron keys.dat en la dosierujo
%1.
Estas grava ke vi faru savkopion de tiu dosiero.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1520"/>
        <source>Open keys.dat?</source>
        <translation>Ĉu malfermi keys.dat?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1517"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Vi povas administri viajn ŝlosilojn redaktante la dosieron keys.dat en la sama dosierujo kiel tiu programo. Estas grava ke vi faru savkopion de tiu dosiero. Ĉu vi volas malfermi la dosieron nun? (Bonvolu certigi ke Bitmesaĝo estas fermita antaŭ fari ŝanĝojn.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1520"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Vi povas administri viajn ŝlosilojn redaktante la dosieron keys.dat en la dosierujo
%1.
Estas grava ke vi faru savkopion de tiu dosiero. Ĉu vi volas malfermi la dosieron nun? (Bonvolu certigi ke Bitmesaĝo estas fermita antaŭ fari ŝanĝojn.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1527"/>
        <source>Delete trash?</source>
        <translation>Malplenigi rubujon?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1527"/>
        <source>Are you sure you want to delete all trashed messages?</source>
        <translation>Ĉu vi certe volas forviŝi ĉiujn mesaĝojn el la rubujo?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1547"/>
        <source>bad passphrase</source>
        <translation>malprava pasvorto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1547"/>
        <source>You must type your passphrase. If you don&apos;t have one then this is not the form for you.</source>
        <translation>Vi devas tajpi vian pasvorton. Se vi ne havas pasvorton tiu ne estas la prava formularo por vi.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1560"/>
        <source>Bad address version number</source>
        <translation>Malkorekta numero de adresversio</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1556"/>
        <source>Your address version number must be a number: either 3 or 4.</source>
        <translation>Via numero de adresversio devas esti: aŭ 3 aŭ 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1560"/>
        <source>Your address version number must be either 3 or 4.</source>
        <translation>Via numero de adresversio devas esti: aŭ 3 aŭ 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1590"/>
        <source>Chan name needed</source>
        <translation>Bezonas nomon de kanalo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1590"/>
        <source>You didn&apos;t enter a chan name.</source>
        <translation>Vi ne enmetis nomon de kanalo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1610"/>
        <source>Address already present</source>
        <translation>Adreso jam ĉi tie</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1610"/>
        <source>Could not add chan because it appears to already be one of your identities.</source>
        <translation>Ne povis aldoni kanalon ĉar ŝajne jam estas unu el viaj indentigoj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1614"/>
        <source>Success</source>
        <translation>Sukceso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1585"/>
        <source>Successfully created chan. To let others join your chan, give them the chan name and this Bitmessage address: %1. This address also appears in &apos;Your Identities&apos;.</source>
        <translation>Sukcese kreis kanalon. Por ebligi al aliaj aniĝi vian kanalon, sciigu al ili la nomon de la kanalo kaj ties Bitmesaĝa adreso: %1. Tiu adreso ankaŭ aperas en &apos;Viaj identigoj&apos;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1594"/>
        <source>Address too new</source>
        <translation>Adreso tro nova</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1594"/>
        <source>Although that Bitmessage address might be valid, its version number is too new for us to handle. Perhaps you need to upgrade Bitmessage.</source>
        <translation>Kvankam tiu Bitmesaĝa adreso povus esti ĝusta, ĝia versionumero estas tro nova por pritrakti ĝin. Eble vi devas ĝisdatigi vian Bitmesaĝon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1598"/>
        <source>Address invalid</source>
        <translation>Adreso estas malĝusta</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1598"/>
        <source>That Bitmessage address is not valid.</source>
        <translation>Tiu Bitmesaĝa adreso ne estas ĝusta.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1606"/>
        <source>Address does not match chan name</source>
        <translation>Adreso ne kongruas kun kanalonomo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1606"/>
        <source>Although the Bitmessage address you entered was valid, it doesn&apos;t match the chan name.</source>
        <translation>Kvankam la Bitmesaĝa adreso kiun vi enigis estas ĝusta, ĝi ne kongruas kun la kanalonomo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1614"/>
        <source>Successfully joined chan. </source>
        <translation>Sukcese aniĝis al kanalo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1672"/>
        <source>Connection lost</source>
        <translation>Perdis konekton</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1711"/>
        <source>Connected</source>
        <translation>Konektita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1828"/>
        <source>Message trashed</source>
        <translation>Movis mesaĝon al rubujo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1909"/>
        <source>The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate.</source>
        <translation>La vivdaŭro signifas ĝis kiam la reto tenos la mesaĝon. La ricevonto devos elŝuti ĝin dum tiu tempo. Se via Bitmesaĝa kliento ne ricevos konfirmon, ĝi resendos mesaĝon aŭtomate. Ju pli longa vivdaŭro, des pli laboron via komputilo bezonos fari por sendi mesaĝon. Vivdaŭro proksimume kvin aŭ kvar horoj estas ofte konvena.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1945"/>
        <source>Message too long</source>
        <translation>Mesaĝo tro longa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1945"/>
        <source>The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.</source>
        <translation>La mesaĝon kiun vi provis sendi estas tro longa pro %1 bitokoj. (La maksimumo estas 261644 bitokoj.) Bonvolu mallongigi ĝin antaŭ sendado.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1973"/>
        <source>Error: Your account wasn&apos;t registered at an email gateway. Sending registration now as %1, please wait for the registration to be processed before retrying sending.</source>
        <translation>Eraro: Via konto ne estas registrita je retpoŝta kluzo. Registranta nun kiel %1, bonvolu atendi ĝis la registrado finos antaŭ vi reprovos sendi iun ajn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1982"/>
        <source>Error: Bitmessage addresses start with BM-   Please check %1</source>
        <translation>Eraro: Bitmesaĝaj adresoj komencas kun BM- Bonvolu kontroli %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1985"/>
        <source>Error: The address %1 is not typed or copied correctly. Please check it.</source>
        <translation>Eraro: La adreso %1 ne estis prave tajpita aŭ kopiita. Bonvolu kontroli ĝin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1988"/>
        <source>Error: The address %1 contains invalid characters. Please check it.</source>
        <translation>Eraro: La adreso %1 enhavas malpermesitajn simbolojn. Bonvolu kontroli ĝin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1991"/>
        <source>Error: The address version in %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</source>
        <translation>Eraro: La adresversio %1 estas tro alta. Eble vi devas ĝisdatigi vian Bitmesaĝan programon aŭ via sagaca konato uzas alian programon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1994"/>
        <source>Error: Some data encoded in the address %1 is too short. There might be something wrong with the software of your acquaintance.</source>
        <translation>Eraro: Kelkaj datumoj koditaj en la adreso %1 estas tro mallongaj. Povus esti ke io en la programo de via konato malfunkcias.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1997"/>
        <source>Error: Some data encoded in the address %1 is too long. There might be something wrong with the software of your acquaintance.</source>
        <translation>Eraro: Kelkaj datumoj koditaj en la adreso %1 estas tro longaj. Povus esti ke io en la programo de via konato malfunkcias.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2000"/>
        <source>Error: Some data encoded in the address %1 is malformed. There might be something wrong with the software of your acquaintance.</source>
        <translation>Eraro: Kelkaj datumoj koditaj en la adreso %1 estas misformitaj. Povus esti ke io en la programo de via konato malfunkcias.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2003"/>
        <source>Error: Something is wrong with the address %1.</source>
        <translation>Eraro: Io malĝustas kun la adreso %1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2071"/>
        <source>Error: You must specify a From address. If you don&apos;t have one, go to the &apos;Your Identities&apos; tab.</source>
        <translation>Eraro: Vi devas elekti sendontan adreson. Se vi ne havas iun, iru al langeto &apos;Viaj identigoj&apos;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2012"/>
        <source>Address version number</source>
        <translation>Numero de adresversio</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2012"/>
        <source>Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Priaboranta adreson %1, Bitmesaĝo ne povas kompreni numerojn %2 de adresversioj. Eble ĝisdatigu Bitmesaĝon al la plej nova versio.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2016"/>
        <source>Stream number</source>
        <translation>Fluo numero</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2016"/>
        <source>Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Priaboranta adreson %1, Bitmesaĝo ne povas priservi %2 fluojn numerojn. Eble ĝisdatigu Bitmesaĝon al la plej nova versio.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2021"/>
        <source>Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won&apos;t send until you connect.</source>
        <translation>Atentu: Vi ne estas nun konektita. Bitmesaĝo faros necesan laboron por sendi mesaĝon, tamen ĝi ne sendos ĝin antaŭ vi konektos.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2063"/>
        <source>Message queued.</source>
        <translation>Mesaĝo envicigita.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2067"/>
        <source>Your &apos;To&apos; field is empty.</source>
        <translation>Via &quot;Ricevonto&quot;-kampo malplenas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2122"/>
        <source>Right click one or more entries in your address book and select &apos;Send message to this address&apos;.</source>
        <translation>Dekstre alklaku kelka(j)n ero(j)n en via adresaro kaj elektu &apos;Sendi mesaĝon al tiu adreso&apos;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2133"/>
        <source>Fetched address from namecoin identity.</source>
        <translation>Venigis adreson de Namecoin-a identigo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2232"/>
        <source>New Message</source>
        <translation>Nova mesaĝo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2232"/>
        <source>From </source>
        <translation>De </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2611"/>
        <source>Sending email gateway registration request</source>
        <translation>Sendanta peton pri registrado je retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="60"/>
        <source>Address is valid.</source>
        <translation>Adreso estas ĝusta.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="94"/>
        <source>The address you entered was invalid. Ignoring it.</source>
        <translation>La adreso kiun vi enmetis estas malĝusta. Ignoras ĝin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2952"/>
        <source>Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.</source>
        <translation>Eraro: Vi ne povas duoble aldoni la saman adreson al via adresaro. Provu renomi la jaman se vi volas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3197"/>
        <source>Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want.</source>
        <translation>Eraro: Vi ne povas aldoni duoble la saman adreson al viaj abonoj. Eble renomi la jaman se vi volas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2371"/>
        <source>Restart</source>
        <translation>Restartigi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2357"/>
        <source>You must restart Bitmessage for the port number change to take effect.</source>
        <translation>Vi devas restartigi Bitmesaĝon por ke la ŝanĝo de la numero de pordo (Port Number) efektivigu.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2371"/>
        <source>Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any).</source>
        <translation>Bitmesaĝo uzos vian prokurilon (proxy) ekde nun sed eble vi volas permane restartigi Bitmesaĝon nun por ke ĝi fermu eblajn jamajn konektojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2399"/>
        <source>Number needed</source>
        <translation>Numero bezonata</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2399"/>
        <source>Your maximum download and upload rate must be numbers. Ignoring what you typed.</source>
        <translation>Maksimumaj elŝutrapido kaj alŝutrapido devas esti numeroj. Ignoras kion vi enmetis.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2472"/>
        <source>Will not resend ever</source>
        <translation>Resendos neniam</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2472"/>
        <source>Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent.</source>
        <translation>Rigardu, ke la templimon vi enmetis estas pli malgrandan ol tempo dum kiu Bitmesaĝo atendas por resendi unuafoje, do viaj mesaĝoj estos senditaj neniam.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2584"/>
        <source>Sending email gateway unregistration request</source>
        <translation>Sendanta peton pri malregistrado de retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2588"/>
        <source>Sending email gateway status request</source>
        <translation>Sendanta peton pri stato de retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2644"/>
        <source>Passphrase mismatch</source>
        <translation>Pasfrazoj malsamas</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2644"/>
        <source>The passphrase you entered twice doesn&apos;t match. Try again.</source>
        <translation>La pasfrazo kiun vi duoble enmetis malsamas. Provu denove.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2647"/>
        <source>Choose a passphrase</source>
        <translation>Elektu pasfrazon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2647"/>
        <source>You really do need a passphrase.</source>
        <translation>Vi ja vere bezonas pasfrazon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2689"/>
        <source>All done. Closing user interface...</source>
        <translation type="obsolete">Ĉiu preta. Fermante fasadon...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2899"/>
        <source>Address is gone</source>
        <translation>Adreso foriris</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2899"/>
        <source>Bitmessage cannot find your address %1. Perhaps you removed it?</source>
        <translation>Bitmesaĝo ne povas trovi vian adreson %1. Ĉu eble vi forviŝis ĝin?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2902"/>
        <source>Address disabled</source>
        <translation>Adreso malŝaltita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2902"/>
        <source>Error: The address from which you are trying to send is disabled. You&apos;ll have to enable it on the &apos;Your Identities&apos; tab before using it.</source>
        <translation>Eraro: La adreso kun kiu vi provas sendi estas malŝaltita. Vi devos ĝin ŝalti en la langeto &apos;Viaj identigoj&apos; antaŭ uzi ĝin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2949"/>
        <source>Entry added to the Address Book. Edit the label to your liking.</source>
        <translation>Aldonis elementon al adresaro. Redaktu la etikedon laŭvole.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2974"/>
        <source>Entry added to the blacklist. Edit the label to your liking.</source>
        <translation>Aldonis elementon al la nigra listo. Redaktu la etikedon laŭvole.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2977"/>
        <source>Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want.</source>
        <translation>Eraro: Vi ne povas duoble aldoni la saman adreson al via nigra listo. Provu renomi la jaman se vi volas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3105"/>
        <source>Moved items to trash.</source>
        <translation>Movis elementojn al rubujo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3045"/>
        <source>Undeleted item.</source>
        <translation>Malforviŝis elementon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3073"/>
        <source>Save As...</source>
        <translation>Konservi kiel...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3082"/>
        <source>Write error.</source>
        <translation>Skriberaro.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3183"/>
        <source>No addresses selected.</source>
        <translation>Neniu adreso elektita.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3229"/>
        <source>If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the subscription?</source>
        <translation>Se vi forviŝos abonon, mesaĝojn kiujn vi jam ricevis igos neatingeblajn. Eble vi devus anstataŭ malaktivigi abonon. Malaktivaj abonoj ne ricevos novajn mesaĝojn, tamen vi plu povos legi mesaĝojn kiujn ci jam ricevis.

Ĉu vi certe volas forviŝi la abonon?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3458"/>
        <source>If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the channel?</source>
        <translation>Se vi forviŝos kanalon, mesaĝojn kiujn vi jam ricevis igos neatingeblajn. Eble vi devus anstataŭ malaktivigi kanalon. Malaktivaj kanaloj ne ricevos novajn mesaĝojn, tamen vi plu povos legi mesaĝojn kiujn ci jam ricevis.

Ĉu vi certe volas forviŝi la kanalon?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3572"/>
        <source>Do you really want to remove this avatar?</source>
        <translation>Ĉu vi certe volas forviŝi tiun avataron?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3580"/>
        <source>You have already set an avatar for this address. Do you really want to overwrite it?</source>
        <translation>Vi jam agordis avataron por tiu adreso. Ĉu vi vere volas superskribi ĝin?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3952"/>
        <source>Start-on-login not yet supported on your OS.</source>
        <translation>Starto-dum-ensaluto ne estas ankoraŭ ebla en via operaciumo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3945"/>
        <source>Minimize-to-tray not yet supported on your OS.</source>
        <translation>Plejetigo al taskopleto ne estas ankoraŭ ebla en via operaciumo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3948"/>
        <source>Tray notifications not yet supported on your OS.</source>
        <translation>Taskopletaj sciigoj ne estas ankoraŭ eblaj en via operaciumo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4117"/>
        <source>Testing...</source>
        <translation>Testante...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4157"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation>Tio estas kanaladreso. Vi ne povas ĝin uzi kiel kvazaŭ-dissendolisto.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4217"/>
        <source>The address should start with &apos;&apos;BM-&apos;&apos;</source>
        <translation>La adreso komencu kun &quot;BM-&quot;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4220"/>
        <source>The address is not typed or copied correctly (the checksum failed).</source>
        <translation>La adreso ne estis prave tajpita aŭ kopiita (kontrolsumo malsukcesis).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4223"/>
        <source>The version number of this address is higher than this software can support. Please upgrade Bitmessage.</source>
        <translation>La numero de adresversio estas pli alta ol tiun, kiun la programo poveblas subteni. Bonvolu ĝisdatigi Bitmesaĝon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4226"/>
        <source>The address contains invalid characters.</source>
        <translation>La adreso enhavas malpermesitajn simbolojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4229"/>
        <source>Some data encoded in the address is too short.</source>
        <translation>Kelkaj datumoj kodita en la adreso estas tro mallongaj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4232"/>
        <source>Some data encoded in the address is too long.</source>
        <translation>Kelkaj datumoj kodita en la adreso estas tro longaj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4235"/>
        <source>Some data encoded in the address is malformed.</source>
        <translation>Kelkaj datumoj koditaj en la adreso estas misformitaj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4209"/>
        <source>Enter an address above.</source>
        <translation>Enmetu adreson supre.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4241"/>
        <source>Address is an old type. We cannot display its past broadcasts.</source>
        <translation>Malnova speco de adreso. Ne povas montri ĝiajn antaŭajn elsendojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4250"/>
        <source>There are no recent broadcasts from this address to display.</source>
        <translation>Neniaj lastatempaj elsendoj de tiu adreso por montri.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4294"/>
        <source>You are using TCP port %1. (This can be changed in the settings).</source>
        <translation>Vi estas uzanta TCP pordo %1 (Tio estas ŝanĝebla en la agordoj).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="645"/>
        <source>Bitmessage</source>
        <translation>Bitmesaĝo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="646"/>
        <source>Identities</source>
        <translation>Identigoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="647"/>
        <source>New Identity</source>
        <translation>Nova identigo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="704"/>
        <source>Search</source>
        <translation>Serĉi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="705"/>
        <source>All</source>
        <translation>Ĉio</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="712"/>
        <source>To</source>
        <translation>Al</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="714"/>
        <source>From</source>
        <translation>De</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="716"/>
        <source>Subject</source>
        <translation>Temo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="709"/>
        <source>Message</source>
        <translation>Mesaĝo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="718"/>
        <source>Received</source>
        <translation>Ricevita je</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="663"/>
        <source>Messages</source>
        <translation>Mesaĝoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="666"/>
        <source>Address book</source>
        <translation>Adresaro</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="668"/>
        <source>Address</source>
        <translation>Adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="669"/>
        <source>Add Contact</source>
        <translation>Aldoni kontakton</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="670"/>
        <source>Fetch Namecoin ID</source>
        <translation>Venigu Namecoin ID</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="677"/>
        <source>Subject:</source>
        <translation>Temo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="676"/>
        <source>From:</source>
        <translation>De:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="673"/>
        <source>To:</source>
        <translation>Al:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="675"/>
        <source>Send ordinary Message</source>
        <translation>Sendi ordinaran mesaĝon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="679"/>
        <source>Send Message to your Subscribers</source>
        <translation>Sendi mesaĝon al viaj abonantoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="680"/>
        <source>TTL:</source>
        <translation>Vivdaŭro:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="681"/>
        <source>X days</source>
        <translation>X tagoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="701"/>
        <source>Subscriptions</source>
        <translation>Abonoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="685"/>
        <source>Add new Subscription</source>
        <translation>Aldoni novan abonon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="719"/>
        <source>Chans</source>
        <translation>Kanaloj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="703"/>
        <source>Add Chan</source>
        <translation>Aldoni kanalon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="720"/>
        <source>Network Status</source>
        <translation>Reta Stato</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="723"/>
        <source>File</source>
        <translation>Dosiero</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="734"/>
        <source>Settings</source>
        <translation>Agordoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="730"/>
        <source>Help</source>
        <translation>Helpo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="726"/>
        <source>Import keys</source>
        <translation>Enporti ŝlosilojn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="727"/>
        <source>Manage keys</source>
        <translation>Administri ŝlosilojn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="729"/>
        <source>Ctrl+Q</source>
        <translation>Stir+Q</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="731"/>
        <source>F1</source>
        <translation>F1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="732"/>
        <source>Contact support</source>
        <translation>Peti pri helpo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="733"/>
        <source>About</source>
        <translation>Pri</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="735"/>
        <source>Regenerate deterministic addresses</source>
        <translation>Regeneri determinisman adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="736"/>
        <source>Delete all trashed messages</source>
        <translation>Forviŝi ĉiujn mesaĝojn el rubujo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="737"/>
        <source>Join / Create chan</source>
        <translation>Aniĝi / Krei kanalon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="171"/>
        <source>All accounts</source>
        <translation>Ĉiuj kontoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="44"/>
        <source>Zoom level %1%</source>
        <translation>Pligrandigo: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="91"/>
        <source>Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.</source>
        <translation>Eraro: Vi ne povas aldoni duoble la saman adreson al via listo. Eble renomi la jaman se vi volas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="112"/>
        <source>Add new entry</source>
        <translation>Aldoni novan elementon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4254"/>
        <source>Display the %1 recent broadcast(s) from this address.</source>
        <translation>Montri la %1 lasta(j)n elsendo(j)n de tiu adreso.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1837"/>
        <source>New version of PyBitmessage is available: %1. Download it from https://github.com/Bitmessage/PyBitmessage/releases/latest</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2666"/>
        <source>Shutting down PyBitmessage... %1%%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2685"/>
        <source>Waiting for PoW to finish... %1%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2689"/>
        <source>Shutting down Pybitmessage... %1%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2711"/>
        <source>Waiting for objects to be sent... %1%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2721"/>
        <source>Saving settings... %1%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2730"/>
        <source>Shutting down core... %1%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2733"/>
        <source>Stopping notifications... %1%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2739"/>
        <source>Shutdown imminent... %1%</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>NewAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="173"/>
        <source>Create new Address</source>
        <translation>Krei novan adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="174"/>
        <source>Here you may generate as many addresses as you like. Indeed, creating and abandoning addresses is encouraged. You may generate addresses by using either random numbers or by using a passphrase. If you use a passphrase, the address is called a &quot;deterministic&quot; address.
The &apos;Random Number&apos; option is selected by default but deterministic addresses have several pros and cons:</source>
        <translation>Tie ĉi vi povas generi tiom adresojn, kiom vi volas. Ververe kreado kaj forlasado de adresoj estas konsilinda. Vi povas krei adresojn uzante hazardajn nombrojn aŭ pasfrazon. Se vi uzos pasfrazon, la adreso estas nomita kiel &apos;determinisma&apos; adreso.
La &apos;hazardnombra&apos; adreso estas elektita defaŭlte, sed determinismaj adresoj havas kelkajn bonaĵojn kaj malbonaĵojn:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="176"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Pros:&lt;br/&gt;&lt;/span&gt;You can recreate your addresses on any computer from memory. &lt;br/&gt;You need-not worry about backing up your keys.dat file as long as you can remember your passphrase. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Cons:&lt;br/&gt;&lt;/span&gt;You must remember (or write down) your passphrase if you expect to be able to recreate your keys if they are lost. &lt;br/&gt;You must remember the address version number and the stream number along with your passphrase. &lt;br/&gt;If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Bonaĵoj:&lt;br/&gt;&lt;/span&gt;Vi poveblas rekrei viajn adresojn per iu ajn komputilo elkape.&lt;br/&gt;Vi ne devas klopodi fari savkopion de keys.dat dosiero tiel longe dum vi memoras vian pasfrazon.&lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Malbonaĵoj:&lt;br/&gt;&lt;/span&gt;Vi devas memori (aŭ konservi) vian pasfrazon se vi volas rekrei viajn ŝlosilojn kiam vi perdos ilin.&lt;br/&gt;Vi devas memori nombro de adresversio kaj de fluo kune kun vian pasfrazon.&lt;br/&gt;Se vi elektos malfortan pasfrazon kaj iu ajn Interrete eblos brutforti ĝin, li povos legi ĉiujn viajn mesaĝojn kaj sendi mesaĝojn kiel vi.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="177"/>
        <source>Use a random number generator to make an address</source>
        <translation>Uzi hazardnombran generilon por krei adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="178"/>
        <source>Use a passphrase to make addresses</source>
        <translation>Uzi pasfrazon por krei adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="179"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Pasigi kelkajn minutojn aldone kompute por fari la adreso(j)n 1 aŭ 2 signoj pli mallongaj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="180"/>
        <source>Make deterministic addresses</source>
        <translation>Fari determinisman adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="181"/>
        <source>Address version number: 4</source>
        <translation>Numero de adresversio: 4</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="182"/>
        <source>In addition to your passphrase, you must remember these numbers:</source>
        <translation>Kune kun vian pasfrazon vi devas memori jenajn numerojn:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="183"/>
        <source>Passphrase</source>
        <translation>Pasfrazo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="184"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Kvanto de farotaj adresoj bazante sur via pasfrazo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="185"/>
        <source>Stream number: 1</source>
        <translation>Fluo numero: 1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="186"/>
        <source>Retype passphrase</source>
        <translation>Reenmeti pasfrazon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="187"/>
        <source>Randomly generate address</source>
        <translation>Hazardnombra adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="188"/>
        <source>Label (not shown to anyone except you)</source>
        <translation>Etikedo (ne montrata al iu ajn escepte de vi)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="189"/>
        <source>Use the most available stream</source>
        <translation>Uzi la plej disponeblan fluon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="190"/>
        <source> (best if this is the first of many addresses you will create)</source>
        <translation>(plej bone se tiun estas la unuan de ĉiuj adresojn vi kreos)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="191"/>
        <source>Use the same stream as an existing address</source>
        <translation>Uzi saman fluon kiel jama adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="192"/>
        <source>(saves you some bandwidth and processing power)</source>
        <translation>(konservas iomete rettrafikon kaj komputopovon)</translation>
    </message>
</context>
<context>
    <name>NewSubscriptionDialog</name>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="65"/>
        <source>Add new entry</source>
        <translation>Aldoni novan elementon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="66"/>
        <source>Label</source>
        <translation>Etikedo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="67"/>
        <source>Address</source>
        <translation>Adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="68"/>
        <source>Enter an address above.</source>
        <translation>Enmetu adreson supre.</translation>
    </message>
</context>
<context>
    <name>SpecialAddressBehaviorDialog</name>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="59"/>
        <source>Special Address Behavior</source>
        <translation>Speciala sinteno de adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="60"/>
        <source>Behave as a normal address</source>
        <translation>Sintenadi kiel normala adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="61"/>
        <source>Behave as a pseudo-mailing-list address</source>
        <translation>Sintenadi kiel kvazaŭ-elsendlista adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="62"/>
        <source>Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).</source>
        <translation>Mesaĝoj alvenintaj al kvazaŭ-dissendlisto estos aŭtomate dissenditaj al abonantoj (do ili estos publikaj).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="63"/>
        <source>Name of the pseudo-mailing-list:</source>
        <translation>Nomo de la kvazaŭ-dissendlisto:</translation>
    </message>
</context>
<context>
    <name>aboutDialog</name>
    <message>
        <location filename="../bitmessageqt/about.py" line="66"/>
        <source>About</source>
        <translation>Pri</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="67"/>
        <source>PyBitmessage</source>
        <translation>PyBitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="68"/>
        <source>version ?</source>
        <translation>versio ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="69"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright &#xc2;&#xa9; 2012-2014 Jonathan Warren&lt;br/&gt;Copyright &#xc2;&#xa9; 2013-2014 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Aŭtorrajto © 2012-2014 Jonathan Warren&lt;br/&gt;Aŭtorrajto © 2013-2014 La Programistoj de Bitmesaĝo&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distributed under the MIT/X11 software license; see &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distribuita sub la permesilo &quot;MIT/X11 software license&quot;; vidu &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="71"/>
        <source>This is Beta software.</source>
        <translation>Tio estas beta-eldono.</translation>
    </message>
</context>
<context>
    <name>blacklist</name>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="17"/>
        <source>Use a Blacklist (Allow all incoming messages except those on the Blacklist)</source>
        <translation>Uzi nigran liston (Permesas ĉiujn alvenajn mesaĝojn escepte tiujn en la nigra listo)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="27"/>
        <source>Use a Whitelist (Block all incoming messages except those on the Whitelist)</source>
        <translation>Uzi blankan liston (Blokas ĉiujn alvenajn mesaĝojn escepte tiujn en la blanka listo)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="34"/>
        <source>Add new entry</source>
        <translation>Aldoni novan elementon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="85"/>
        <source>Name or Label</source>
        <translation>Nomo aŭ etikedo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="90"/>
        <source>Address</source>
        <translation>Adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="151"/>
        <source>Blacklist</source>
        <translation>Nigra Listo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="153"/>
        <source>Whitelist</source>
        <translation>Blanka Listo</translation>
    </message>
</context>
<context>
    <name>connectDialog</name>
    <message>
        <location filename="../bitmessageqt/connect.py" line="56"/>
        <source>Bitmessage</source>
        <translation>Bitmesaĝo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="57"/>
        <source>Bitmessage won&apos;t connect to anyone until you let it. </source>
        <translation>Bitmesaĝo ne konektos antaŭ vi permesos al ĝi.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="58"/>
        <source>Connect now</source>
        <translation>Konekti nun</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="59"/>
        <source>Let me configure special network settings first</source>
        <translation>Lasu min unue fari specialajn retajn agordojn</translation>
    </message>
</context>
<context>
    <name>helpDialog</name>
    <message>
        <location filename="../bitmessageqt/help.py" line="45"/>
        <source>Help</source>
        <translation>Helpo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.py" line="46"/>
        <source>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</source>
        <translation>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.py" line="47"/>
        <source>As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:</source>
        <translation>Ĉar Bitmesaĝo estas kunlabora projekto, vi povas trovi helpon enrete ĉe la vikio de Bitmesaĝo:</translation>
    </message>
</context>
<context>
    <name>iconGlossaryDialog</name>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="82"/>
        <source>Icon Glossary</source>
        <translation>Piktograma Glosaro</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="83"/>
        <source>You have no connections with other peers. </source>
        <translation>Vi havas neniun konekton al aliaj samtavolano.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="84"/>
        <source>You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn&apos;t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.</source>
        <translation>Vi konektis almenaŭ al unu samtavolano uzante eliranta konekto, sed vi ankoraŭ ne ricevis enirantajn konetkojn. Via fajroŝirmilo (firewall) aŭ hejma enkursigilo (router) verŝajne estas agordita ne plusendi enirantajn TCP konektojn al via komputilo. Bitmesaĝo funkcios sufiĉe bone sed helpus al la Bitmesaĝa reto se vi permesus enirantajn konektojn kaj tiel estus pli bone konektita nodo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="85"/>
        <source>You are using TCP port ?. (This can be changed in the settings).</source>
        <translation>Ĉu vi estas uzanta TCP pordon ?. (Tio estas ŝanĝebla en la agordoj).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="86"/>
        <source>You do have connections with other peers and your firewall is correctly configured.</source>
        <translation>Vi havas konektojn al aliaj samtavolanoj kaj via fajroŝirmilo estas ĝuste agordita.</translation>
    </message>
</context>
<context>
    <name>networkstatus</name>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="39"/>
        <source>Total connections:</source>
        <translation>Ĉiuj konektoj:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="143"/>
        <source>Since startup:</source>
        <translation>Ekde starto:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="159"/>
        <source>Processed 0 person-to-person messages.</source>
        <translation>Pritraktis 0 inter-personajn mesaĝojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="188"/>
        <source>Processed 0 public keys.</source>
        <translation>Pritraktis 0 publikajn ŝlosilojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="175"/>
        <source>Processed 0 broadcasts.</source>
        <translation>Pritraktis 0 elsendojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="240"/>
        <source>Inventory lookups per second: 0</source>
        <translation>Petoj pri inventaro en sekundo: 0</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="101"/>
        <source>Down: 0 KB/s</source>
        <translation type="obsolete">Elŝuto: 0 KB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="114"/>
        <source>Up: 0 KB/s</source>
        <translation type="obsolete">Alŝuto: 0 KB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="201"/>
        <source>Objects to be synced:</source>
        <translation>Samtempigotaj eroj:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="111"/>
        <source>Stream #</source>
        <translation>Fluo #</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="116"/>
        <source>Connections</source>
        <translation>Konetkoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="133"/>
        <source>Since startup on %1</source>
        <translation>Ekde lanĉo de la programo je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="59"/>
        <source>Objects to be synced: %1</source>
        <translation>Eroj por samtempigi: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="50"/>
        <source>Processed %1 person-to-person messages.</source>
        <translation>Pritraktis %1 inter-personajn mesaĝojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="55"/>
        <source>Processed %1 broadcast messages.</source>
        <translation>Pritraktis %1 elsendojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="60"/>
        <source>Processed %1 public keys.</source>
        <translation>Pritraktis %1 publikajn ŝlosilojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="68"/>
        <source>Down: %1/s  Total: %2</source>
        <translation>Elŝuto: %1/s Entute: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="70"/>
        <source>Up: %1/s  Total: %2</source>
        <translation>Alŝuto: %1/s Entute: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="117"/>
        <source>Total Connections: %1</source>
        <translation>Ĉiuj konektoj: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="126"/>
        <source>Inventory lookups per second: %1</source>
        <translation>Petoj pri inventaro en sekundo: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="214"/>
        <source>Up: 0 kB/s</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="227"/>
        <source>Down: 0 kB/s</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="38"/>
        <source>byte(s)</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>newChanDialog</name>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="97"/>
        <source>Dialog</source>
        <translation>Dialogo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="98"/>
        <source>Create a new chan</source>
        <translation>Krei novan kanalon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="103"/>
        <source>Join a chan</source>
        <translation>Aniĝi al kanalo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="100"/>
        <source>Create a chan</source>
        <translation>Krei kanalon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="101"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly then the chan will be secure and private. If you and someone else both create a chan with the same chan name then it is currently very likely that they will be the same chan.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Enmetu nomon por via kanalo. Se vi elektas sufiĉe ampleksan kanalnomon (kiel fortan kaj unikan pasfrazon) kaj neniu el viaj amikoj komunikas ĝin publike la kanalo estos sekura kaj privata. Se vi kaj iu ajn kreas kanalon kun la sama nomo tiam en la momento estas tre verŝajne ke estos la sama kanalo.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="105"/>
        <source>Chan name:</source>
        <translation>Nomo de kanalo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="104"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a normal person-to-person message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Kanalo ekzistas kiam grupo de personoj havas komunajn malĉifrajn ŝlosilojn. La ŝlosiloj kaj Bitmesaĝa adreso uzita de kanalo estas generita el hom-legebla vorto aŭ frazo (la nomo de la kanalo). Por sendi mesaĝon al ĉiu en la kanalo, sendu normalan inter-personan mesaĝon al la adreso de la kanalo.&lt;/p&gt;&lt;p&gt;Kanaloj estas eksperimentaj kaj tute malkontroleblaj.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="106"/>
        <source>Chan bitmessage address:</source>
        <translation>Bitmesaĝa adreso de kanalo:</translation>
    </message>
</context>
<context>
    <name>regenerateAddressesDialog</name>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="114"/>
        <source>Regenerate Existing Addresses</source>
        <translation>Regeneri ekzistantajn adresojn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="115"/>
        <source>Regenerate existing addresses</source>
        <translation>Regeneri ekzistantajn adresojn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="116"/>
        <source>Passphrase</source>
        <translation>Pasfrazo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="117"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Kvanto de farotaj adresoj bazante sur via pasfrazo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="118"/>
        <source>Address version number:</source>
        <translation>Numero de adresversio:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="119"/>
        <source>Stream number:</source>
        <translation>Fluo numero:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="120"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="121"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Pasigi kelkajn minutojn aldone kompute por krei la adreso(j)n 1 aŭ 2 signoj pli mallongaj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="122"/>
        <source>You must check (or not check) this box just like you did (or didn&apos;t) when you made your addresses the first time.</source>
        <translation>Vi devas marki (aŭ ne marki) tiun markobutono samkiel vi faris kiam vi generis vian adreson unuafoje.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="123"/>
        <source>If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.</source>
        <translation>Se vi antaŭe kreis determinismajn adresojn sed perdis ilin akcidente (ekz. en diska paneo), vi povas regeneri ilin ĉi tie. Se vi uzis la generilo de hazardnombroj por krei vian adreson tiu formularo ne taŭgos por vi.</translation>
    </message>
</context>
<context>
    <name>settingsDialog</name>
    <message>
        <location filename="../bitmessageqt/settings.py" line="430"/>
        <source>Settings</source>
        <translation>Agordoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="431"/>
        <source>Start Bitmessage on user login</source>
        <translation>Startigi Bitmesaĝon dum ensaluto de uzanto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="432"/>
        <source>Tray</source>
        <translation>Taskopleto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="433"/>
        <source>Start Bitmessage in the tray (don&apos;t show main window)</source>
        <translation>Startigi Bitmesaĝon en la taskopleto (tray) ne montrante tiun fenestron</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="434"/>
        <source>Minimize to tray</source>
        <translation>Plejetigi al taskopleto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="435"/>
        <source>Close to tray</source>
        <translation>Fermi al taskopleto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="436"/>
        <source>Show notification when message received</source>
        <translation>Montri sciigon kiam mesaĝo alvenas</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="437"/>
        <source>Run in Portable Mode</source>
        <translation>Ekzekucii en Portebla Reĝimo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="438"/>
        <source>In Portable Mode, messages and config files are stored in the same directory as the program rather than the normal application-data folder. This makes it convenient to run Bitmessage from a USB thumb drive.</source>
        <translation>En Portebla Reĝimo, mesaĝoj kaj agordoj estas enmemorigitaj en la sama dosierujo kiel la programo mem anstataŭ en la dosierujo por datumoj de aplikaĵoj. Tio igas ĝin komforta ekzekucii Bitmesaĝon el USB poŝmemorilo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="439"/>
        <source>Willingly include unencrypted destination address when sending to a mobile device</source>
        <translation>Volonte inkluzivi malĉifritan cel-adreson dum sendado al portebla aparato.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="440"/>
        <source>Use Identicons</source>
        <translation>Uzi ID-avatarojn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="441"/>
        <source>Reply below Quote</source>
        <translation>Respondi sub citaĵo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="442"/>
        <source>Interface Language</source>
        <translation>Fasada lingvo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="443"/>
        <source>System Settings</source>
        <comment>system</comment>
        <translation>Sistemaj agordoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="470"/>
        <source>Pirate English</source>
        <comment>en_pirate</comment>
        <translation type="obsolete">Pirate English</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="471"/>
        <source>Other (set in keys.dat)</source>
        <comment>other</comment>
        <translation type="obsolete">Alia (agordi en keys.dat)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="444"/>
        <source>User Interface</source>
        <translation>Fasado</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="445"/>
        <source>Listening port</source>
        <translation>Aŭskultanta pordo (port)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="446"/>
        <source>Listen for connections on port:</source>
        <translation>Aŭskulti pri konektoj ĉe pordo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="447"/>
        <source>UPnP:</source>
        <translation>UPnP:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="448"/>
        <source>Bandwidth limit</source>
        <translation>Rettrafika limo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="449"/>
        <source>Maximum download rate (kB/s): [0: unlimited]</source>
        <translation>Maksimuma rapido de elŝuto (kB/s): [0: senlima]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="450"/>
        <source>Maximum upload rate (kB/s): [0: unlimited]</source>
        <translation>Maksimuma rapido de alŝuto (kB/s): [0: senlima]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="451"/>
        <source>Proxy server / Tor</source>
        <translation>Prokurila (proxy) servilo / Tor</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="452"/>
        <source>Type:</source>
        <translation>Speco:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="453"/>
        <source>Server hostname:</source>
        <translation>Servilo gastiga nomo (hostname):</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="476"/>
        <source>Port:</source>
        <translation>Pordo (port):</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="455"/>
        <source>Authentication</source>
        <translation>Aŭtentigo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="477"/>
        <source>Username:</source>
        <translation>Uzantnomo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="457"/>
        <source>Pass:</source>
        <translation>Pasvorto:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="458"/>
        <source>Listen for incoming connections when using proxy</source>
        <translation>Aŭskulti pri alvenaj konektoj kiam dum uzado de prokurilo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="459"/>
        <source>none</source>
        <translation>neniu</translation>
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
        <translation>Retaj agordoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="463"/>
        <source>Total difficulty:</source>
        <translation>Tuta malfacilaĵo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="464"/>
        <source>The &apos;Total difficulty&apos; affects the absolute amount of work the sender must complete. Doubling this value doubles the amount of work.</source>
        <translation>La &apos;Tuta malfacilaĵo&apos; efikas sur la tuta kvalito da laboro kiu la sendonto devos fari. Duobligo de tiu valoro, duobligas la kvanton de laboro.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="465"/>
        <source>Small message difficulty:</source>
        <translation>Et-mesaĝa malfacilaĵo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="466"/>
        <source>When someone sends you a message, their computer must first complete some work. The difficulty of this work, by default, is 1. You may raise this default for new addresses you create by changing the values here. Any new addresses you create will require senders to meet the higher difficulty. There is one exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically notify them when you next send a message that they need only complete the minimum amount of work: difficulty 1. </source>
        <translation>Kiam iu ajn sendas al vi mesaĝon, lia komputilo devas unue fari iom da laboro. La malfacilaĵo de tiu laboro defaŭlte estas 1. Vi povas pligrandigi tiun valoron por novaj adresoj kiuj vi generos per ŝanĝo de ĉi-tiaj valoroj. Ĉiuj novaj adresoj kreotaj de vi bezonos por ke sendontoj akceptu pli altan malfacilaĵon. Estas unu escepto: se vi aldonos kolegon al vi adresaro, Bitmesaĝo aŭtomate sciigos lin kiam vi sendos mesaĝon, ke li bezonos fari nur minimuman kvaliton da laboro: malfacilaĵo 1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="467"/>
        <source>The &apos;Small message difficulty&apos; mostly only affects the difficulty of sending small messages. Doubling this value makes it almost twice as difficult to send a small message but doesn&apos;t really affect large messages.</source>
        <translation>La &apos;Et-mesaĝa malfacilaĵo&apos; ĉefe efikas malfacilaĵon por sendi malgrandajn mesaĝojn. Duobligo de tiu valoro, preskaŭ duobligas malfacilaĵon por sendi malgrandajn mesaĝojn, sed preskaŭ ne efikas grandajn mesaĝojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="468"/>
        <source>Demanded difficulty</source>
        <translation>Postulata malfacilaĵo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="469"/>
        <source>Here you may set the maximum amount of work you are willing to do to send a message to another person. Setting these values to 0 means that any value is acceptable.</source>
        <translation>Tie ĉi vi povas agordi maksimuman kvanton da laboro kiun vi faru por sendi mesaĝon al alian persono. Se vi agordos ilin al 0, ĉiuj valoroj estos akceptitaj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="470"/>
        <source>Maximum acceptable total difficulty:</source>
        <translation>Maksimuma akceptata tuta malfacilaĵo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="471"/>
        <source>Maximum acceptable small message difficulty:</source>
        <translation>Maksimuma akceptata malfacilaĵo por et-mesaĝoj:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="472"/>
        <source>Max acceptable difficulty</source>
        <translation>Maksimuma akcepta malfacilaĵo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Hardware GPU acceleration (OpenCL)</source>
        <translation>Aparatara GPU-a plirapidigo (OpenCL)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="474"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage can utilize a different Bitcoin-based program called Namecoin to make addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage address, you can simply tell him to send a message to &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Getting your own Bitmessage address into Namecoin is still rather difficult).&lt;/p&gt;&lt;p&gt;Bitmessage can use either namecoind directly or a running nmcontrol instance.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmesaĝo povas apliki alian Bitmono-bazitan programon - Namecoin - por fari adresojn hom-legeblajn. Ekzemple anstataŭ diri al via amiko longan Bitmesaĝan adreson, vi povas simple peti lin pri sendi mesaĝon al &lt;span style=&quot; font-style:italic;&quot;&gt;testo. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Kreado de sia propra Bitmesaĝa adreso en Namecoin-on estas ankoraŭ ete malfacila).&lt;/p&gt;&lt;p&gt;Bitmesaĝo eblas uzi aŭ na namecoind rekte aŭ jaman aktivan aperon de nmcontrol.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="475"/>
        <source>Host:</source>
        <translation>Gastiga servilo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="478"/>
        <source>Password:</source>
        <translation>Pasvorto:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="479"/>
        <source>Test</source>
        <translation>Testo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="480"/>
        <source>Connect to:</source>
        <translation>Konekti al:</translation>
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
        <translation>Integrigo kun Namecoin</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="484"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;By default, if you send a message to someone and he is offline for more than two days, Bitmessage will send the message again after an additional two days. This will be continued with exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain number of days or months.&lt;/p&gt;&lt;p&gt;Leave these input fields blank for the default behavior. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Defaŭlte se vi sendas mesaĝon al iu kaj li estos eksterrete por iomete da tempo, Bitmesaĝo provos resendi mesaĝon iam poste, kaj iam pli poste. La programo pluigos resendi mesaĝon ĝis sendonto konfirmos liveron. Tie ĉi vi eblas ŝanĝi kiam Bitmesaĝo devos rezigni je sendado.&lt;/p&gt;&lt;p&gt;Lasu tiujn kampojn malplenaj por defaŭlta sinteno.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="485"/>
        <source>Give up after</source>
        <translation>Rezigni post</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="486"/>
        <source>and</source>
        <translation>kaj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="487"/>
        <source>days</source>
        <translation>tagoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="488"/>
        <source>months.</source>
        <translation>monatoj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="489"/>
        <source>Resends Expire</source>
        <translation>Resenda fortempiĝo</translation>
    </message>
</context>
</TS>
