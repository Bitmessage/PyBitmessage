<?xml version="1.0" ?><!DOCTYPE TS><TS language="eo" sourcelanguage="en" version="2.0">
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
        <translation>Stato de retpoŝt-kluza konto</translation>
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
        <location filename="../bitmessageqt/__init__.py" line="2263"/>
        <source>Registration failed:</source>
        <translation>Registrado malsukcesis:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2263"/>
        <source>The requested email address is not available, please try a new one. Fill out the new desired email address (including @mailchuck.com) below:</source>
        <translation>La dezirata retpoŝtadreso ne estas disponebla, bonvolu provi alian. Entajpu novan deziratan adreson (kune kun @mailchuck.com) sube:</translation>
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
        <location filename="../bitmessageqt/account.py" line="241"/>
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
# Kunsendaĵoj estos ignorataj.
#
# archive: yes
# Viaj alvenontaj retmesaĝoj estos arĥivitaj en la servilo. Uzu tion, se vi
# bezonas helpon kun senerarigado aŭ vi bezonas eksterliveritan pruvon de
# retmesaĝoj. Tamen tio signifas, ke la manipulisto de servo eblos legi viajn
# retmesaĝojn eĉ kiam, tiam oni estos liverinta ilin al vi.
#
# archive: no
# Alvenaj mesaĝoj estos forigitaj de la servilo tuj post ili estos liveritaj al vi.
#
# masterpubkey_btc: BIP44 xpub ŝlosilo aŭ electrum v1 publika fontsendo (seed)
# offset_btc: entjera (integer) datumtipo (implicite 0)
# feeamount: nombro kun maksimume 8 decimalaj lokoj
# feecurrency: BTC, XBT, USD, EUR aŭ GBP
# Uzu tiujn se vi volas pagoŝarĝi homojn kiuj sendos al vi retmesaĝojn. Se tiu
# agordo estas ŝaltita kaj iu ajn sendos al vi retmesaĝon, li devos pagi difinan
# sendokoston. Por remalaktivigi ĝin, agordu &quot;feeamount&quot; al 0. Bezonas abonon.
</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="207"/>
        <source>Reply to sender</source>
        <translation>Respondi al sendinto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="209"/>
        <source>Reply to channel</source>
        <translation>Respondi al kanalo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="211"/>
        <source>Add sender to your Address Book</source>
        <translation>Aldoni sendinton al via adresaro</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="215"/>
        <source>Add sender to your Blacklist</source>
        <translation>Aldoni sendinton al via nigra listo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="397"/>
        <source>Move to Trash</source>
        <translation>Movi al rubujo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="222"/>
        <source>Undelete</source>
        <translation>Malforviŝi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="225"/>
        <source>View HTML code as formatted text</source>
        <translation>Montri HTML-n kiel aranĝitan tekston</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="229"/>
        <source>Save message as...</source>
        <translation>Konservi mesaĝon kiel…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="233"/>
        <source>Mark Unread</source>
        <translation>Marki kiel nelegitan</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="369"/>
        <source>New</source>
        <translation>Nova</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="121"/>
        <source>Enable</source>
        <translation>Ŝalti</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="124"/>
        <source>Disable</source>
        <translation>Malŝalti</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="127"/>
        <source>Set avatar...</source>
        <translation>Agordi avataron…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="117"/>
        <source>Copy address to clipboard</source>
        <translation>Kopii adreson al tondejo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="320"/>
        <source>Special address behavior...</source>
        <translation>Speciala sinteno de adreso…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="281"/>
        <source>Email gateway</source>
        <translation>Retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="114"/>
        <source>Delete</source>
        <translation>Forigi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="336"/>
        <source>Send message to this address</source>
        <translation>Sendi mesaĝon al tiu adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="344"/>
        <source>Subscribe to this address</source>
        <translation>Aboni tiun adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="352"/>
        <source>Add New Address</source>
        <translation>Aldoni novan adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="400"/>
        <source>Copy destination address to clipboard</source>
        <translation>Kopii cel-adreson al tondejo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="404"/>
        <source>Force send</source>
        <translation>Devigi sendadon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="618"/>
        <source>One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?</source>
        <translation>Iu de viaj adresoj, %1, estas malnova versio 1 adreso. Versioj 1 adresoj ne estas jam subtenataj. Ĉu ni povas forviŝi ĝin?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1026"/>
        <source>Waiting for their encryption key. Will request it again soon.</source>
        <translation>Atendado je ilia ĉifroŝlosilo. Baldaŭ petos ĝin denove.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="990"/>
        <source>Encryption key request queued.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1032"/>
        <source>Queued.</source>
        <translation>En atendovico.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1035"/>
        <source>Message sent. Waiting for acknowledgement. Sent at %1</source>
        <translation>Mesaĝo sendita. Atendado je konfirmo. Sendita je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1038"/>
        <source>Message sent. Sent at %1</source>
        <translation>Mesaĝo sendita. Sendita je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1002"/>
        <source>Need to do work to send message. Work is queued.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1044"/>
        <source>Acknowledgement of the message received %1</source>
        <translation>Ricevis konfirmon de la mesaĝo je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2132"/>
        <source>Broadcast queued.</source>
        <translation>Elsendo en atendovico.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1053"/>
        <source>Broadcast on %1</source>
        <translation>Elsendo je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1056"/>
        <source>Problem: The work demanded by the recipient is more difficult than you are willing to do. %1</source>
        <translation>Problemo: la demandita laboro de la ricevonto estas pli malfacila ol vi pretas fari. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1059"/>
        <source>Problem: The recipient&apos;s encryption key is no good. Could not encrypt message. %1</source>
        <translation>Problemo: la ĉifroŝlosilo de la ricevonto estas rompita. Ne povis ĉifri la mesaĝon. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1062"/>
        <source>Forced difficulty override. Send should start soon.</source>
        <translation>Devigita superado de limito de malfacilaĵo. Sendado devus baldaŭ komenci.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1065"/>
        <source>Unknown status: %1 %2</source>
        <translation>Nekonata stato: %1 %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1684"/>
        <source>Not Connected</source>
        <translation>Ne konektita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1194"/>
        <source>Show Bitmessage</source>
        <translation>Montri Bitmesaĝon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="688"/>
        <source>Send</source>
        <translation>Sendi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1209"/>
        <source>Subscribe</source>
        <translation>Aboni</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1215"/>
        <source>Channel</source>
        <translation>Kanalo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="734"/>
        <source>Quit</source>
        <translation>Eliri</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1558"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.</source>
        <translation>Vi povas administri viajn ŝlosilojn per redakti la dosieron keys.dat en la sama dosierujo kiel tiu programo. Estas grava, ke vi faru sekurkopion de tiu dosiero.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1562"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file.</source>
        <translation>Vi povas administri viajn ŝlosilojn per redakti la dosieron keys.dat en la dosierujo
%1.
Estas grava, ke vi faru sekurkopion de tiu dosiero.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1569"/>
        <source>Open keys.dat?</source>
        <translation>Ĉu malfermi keys.dat?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1566"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Vi povas administri viajn ŝlosilojn per redakti la dosieron keys.dat en la sama dosierujo kiel tiu programo. Estas grava ke vi faru sekurkopion de tiu dosiero. Ĉu vi volas malfermi la dosieron nun? (Bonvolu certigi ke Bitmesaĝo estas fermita antaŭ fari ŝanĝojn.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1569"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Vi povas administri viajn ŝlosilojn per redakti la dosieron keys.dat en la dosierujo
%1.
Estas grava, ke vi faru sekurkopion de tiu dosiero. Ĉu vi volas malfermi la dosieron nun? (Bonvolu certigi ke Bitmesaĝo estas fermita antaŭ fari ŝanĝojn.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1576"/>
        <source>Delete trash?</source>
        <translation>Ĉu malplenigi rubujon?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1576"/>
        <source>Are you sure you want to delete all trashed messages?</source>
        <translation>Ĉu vi certe volas forviŝi ĉiujn mesaĝojn el la rubujo?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1596"/>
        <source>bad passphrase</source>
        <translation>malprava pasvorto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1596"/>
        <source>You must type your passphrase. If you don&apos;t have one then this is not the form for you.</source>
        <translation>Vi devas tajpi vian pasvorton. Se vi ne havas pasvorton, tiu ĉi ne estas la prava formularo por vi.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1609"/>
        <source>Bad address version number</source>
        <translation>Erara numero de adresversio</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1605"/>
        <source>Your address version number must be a number: either 3 or 4.</source>
        <translation>Via numero de adresversio devas esti: aŭ 3 aŭ 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1609"/>
        <source>Your address version number must be either 3 or 4.</source>
        <translation>Via numero de adresversio devas esti: aŭ 3 aŭ 4.</translation>
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
        <location filename="../bitmessageqt/__init__.py" line="1674"/>
        <source>Connection lost</source>
        <translation>Perdis konekton</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1717"/>
        <source>Connected</source>
        <translation>Konektita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1834"/>
        <source>Message trashed</source>
        <translation>Movis mesaĝon al rubujo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1918"/>
        <source>The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate.</source>
        <translation>La vivdaŭro signifas ĝis kiam la reto tenos la mesaĝon. La ricevonto devos elŝuti ĝin dum tiu tempo. Se via bitmesaĝa kliento ne ricevos konfirmon, ĝi resendos mesaĝon aŭtomate. Ju pli longa vivdaŭro, des pli laboron via komputilo bezonos fari por sendi mesaĝon. Vivdaŭro proksimume kvin aŭ kvar horoj estas ofte konvena.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1956"/>
        <source>Message too long</source>
        <translation>Mesaĝo tro longa</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1956"/>
        <source>The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.</source>
        <translation>La mesaĝon kiun vi provis sendi estas tro longa je %1 bitokoj. (La maksimumo estas 261644 bitokoj.) Bonvolu mallongigi ĝin antaŭ sendado.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1988"/>
        <source>Error: Your account wasn&apos;t registered at an email gateway. Sending registration now as %1, please wait for the registration to be processed before retrying sending.</source>
        <translation>Eraro: Via konto ne estas registrita je retpoŝta kluzo. Registranta nun kiel %1, bonvolu atendi ĝis la registrado finos antaŭ vi reprovos sendi iun ajn.</translation>
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
        <location filename="../bitmessageqt/__init__.py" line="2090"/>
        <source>Error: You must specify a From address. If you don&apos;t have one, go to the &apos;Your Identities&apos; tab.</source>
        <translation>Eraro: Vi devas elekti sendontan adreson. Se vi ne havas iun, iru al langeto &apos;Viaj identigoj&apos;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2031"/>
        <source>Address version number</source>
        <translation>Numero de adresversio</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2031"/>
        <source>Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Dum prilaborado de adreso adreso %1, Bitmesaĝo ne povas kompreni numerojn %2 de adresversioj. Eble ĝisdatigu Bitmesaĝon al la plej nova versio.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2035"/>
        <source>Stream number</source>
        <translation>Fluo numero</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2035"/>
        <source>Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Dum prilaborado de adreso %1, Bitmesaĝo ne povas priservi %2 fluojn numerojn. Eble ĝisdatigu Bitmesaĝon al la plej nova versio.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2040"/>
        <source>Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won&apos;t send until you connect.</source>
        <translation>Atentu: Vi ne estas nun konektita. Bitmesaĝo faros necesan laboron por sendi mesaĝon, tamen ĝi ne sendos ĝin antaŭ vi konektos.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2082"/>
        <source>Message queued.</source>
        <translation>Mesaĝo envicigita.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2086"/>
        <source>Your &apos;To&apos; field is empty.</source>
        <translation>Via &quot;Ricevonto&quot;-kampo malplenas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2141"/>
        <source>Right click one or more entries in your address book and select &apos;Send message to this address&apos;.</source>
        <translation>Dekstre alklaku kelka(j)n elemento(j)n en via adresaro kaj elektu &apos;Sendi mesaĝon al tiu adreso&apos;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2154"/>
        <source>Fetched address from namecoin identity.</source>
        <translation>Venigis adreson de namecoin-a identigo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2257"/>
        <source>New Message</source>
        <translation>Nova mesaĝo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2257"/>
        <source>From </source>
        <translation>De </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2642"/>
        <source>Sending email gateway registration request</source>
        <translation>Sendado de peto pri registrado je retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="59"/>
        <source>Address is valid.</source>
        <translation>Adreso estas ĝusta.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="93"/>
        <source>The address you entered was invalid. Ignoring it.</source>
        <translation>La adreso kiun vi enmetis estas malĝusta. Ignoras ĝin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3081"/>
        <source>Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.</source>
        <translation>Eraro: Vi ne povas duoble aldoni la saman adreson al via adresaro. Provu renomi la ekzistan se vi volas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3329"/>
        <source>Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want.</source>
        <translation>Eraro: Vi ne povas aldoni duoble la saman adreson al viaj abonoj. Eble renomi la ekzistan se vi volas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2402"/>
        <source>Restart</source>
        <translation>Restartigi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2388"/>
        <source>You must restart Bitmessage for the port number change to take effect.</source>
        <translation>Vi devas restartigi Bitmesaĝon por ke la ŝanĝo de la numero de pordo (Port Number) efektivigu.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2402"/>
        <source>Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any).</source>
        <translation>Bitmesaĝo uzos vian prokurilon (proxy) ekde nun, sed eble vi volas permane restartigi Bitmesaĝon nun, por ke ĝi fermu eblajn ekzistajn konektojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2431"/>
        <source>Number needed</source>
        <translation>Numero bezonata</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2431"/>
        <source>Your maximum download and upload rate must be numbers. Ignoring what you typed.</source>
        <translation>Maksimumaj elŝutrapido kaj alŝutrapido devas esti numeroj. Ignoras kion vi enmetis.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2511"/>
        <source>Will not resend ever</source>
        <translation>Resendos neniam</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2511"/>
        <source>Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent.</source>
        <translation>Rigardu, ke la templimon vi enmetis estas pli malgrandan ol tempo dum kiu Bitmesaĝo atendas por resendi unuafoje, do viaj mesaĝoj estos senditaj neniam.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2615"/>
        <source>Sending email gateway unregistration request</source>
        <translation>Sendado de peto pri malregistrado de retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2619"/>
        <source>Sending email gateway status request</source>
        <translation>Sendado de peto pri stato de retpoŝta kluzo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2719"/>
        <source>Passphrase mismatch</source>
        <translation>Pasfrazoj malsamas</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2719"/>
        <source>The passphrase you entered twice doesn&apos;t match. Try again.</source>
        <translation>La pasfrazo kiun vi duoble enmetis malsamas. Provu denove.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2722"/>
        <source>Choose a passphrase</source>
        <translation>Elektu pasfrazon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2722"/>
        <source>You really do need a passphrase.</source>
        <translation>Vi ja vere bezonas pasfrazon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3022"/>
        <source>Address is gone</source>
        <translation>Adreso foriris</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3022"/>
        <source>Bitmessage cannot find your address %1. Perhaps you removed it?</source>
        <translation>Bitmesaĝo ne povas trovi vian adreson %1. Ĉu eble vi forviŝis ĝin?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3025"/>
        <source>Address disabled</source>
        <translation>Adreso malŝaltita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3025"/>
        <source>Error: The address from which you are trying to send is disabled. You&apos;ll have to enable it on the &apos;Your Identities&apos; tab before using it.</source>
        <translation>Eraro: La adreso kun kiu vi provas sendi estas malŝaltita. Vi devos ĝin ŝalti en la langeto &apos;Viaj identigoj&apos; antaŭ uzi ĝin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3078"/>
        <source>Entry added to the Address Book. Edit the label to your liking.</source>
        <translation>Aldonis elementon al adresaro. Redaktu la etikedon laŭvole.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3103"/>
        <source>Entry added to the blacklist. Edit the label to your liking.</source>
        <translation>Aldonis elementon al la nigra listo. Redaktu la etikedon laŭvole.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3106"/>
        <source>Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want.</source>
        <translation>Eraro: Vi ne povas duoble aldoni la saman adreson al via nigra listo. Provu renomi la jaman se vi volas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3234"/>
        <source>Moved items to trash.</source>
        <translation>Movis elementojn al rubujo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3174"/>
        <source>Undeleted item.</source>
        <translation>Malforviŝis elementon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3202"/>
        <source>Save As...</source>
        <translation>Konservi kiel…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3211"/>
        <source>Write error.</source>
        <translation>Skriberaro.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3315"/>
        <source>No addresses selected.</source>
        <translation>Neniu adreso elektita.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3361"/>
        <source>If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the subscription?</source>
        <translation>Se vi forviŝos abonon, mesaĝojn kiujn vi jam ricevis, igos neatingeblajn. Eble vi devus anstataŭ malaktivigi abonon. Malaktivaj abonoj ne ricevos novajn mesaĝojn, tamen vi plu povos legi mesaĝojn kiujn ci jam ricevis.

Ĉu vi certe volas forviŝi la abonon?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3591"/>
        <source>If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the channel?</source>
        <translation>Se vi forviŝos kanalon, mesaĝojn kiujn vi jam ricevis, igos neatingeblajn. Eble vi devus anstataŭ malaktivigi kanalon. Malaktivaj kanaloj ne ricevos novajn mesaĝojn, tamen vi plu povos legi mesaĝojn kiujn ci jam ricevis.

Ĉu vi certe volas forviŝi la kanalon?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3706"/>
        <source>Do you really want to remove this avatar?</source>
        <translation>Ĉu vi certe volas forviŝi tiun ĉi avataron?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3714"/>
        <source>You have already set an avatar for this address. Do you really want to overwrite it?</source>
        <translation>Vi jam agordis avataron por tiu ĉi adreso. Ĉu vi vere volas superskribi ĝin?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4115"/>
        <source>Start-on-login not yet supported on your OS.</source>
        <translation>Starto-dum-ensaluto ne estas ankoraŭ ebla en via operaciumo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4108"/>
        <source>Minimize-to-tray not yet supported on your OS.</source>
        <translation>Plejetigo al taskopleto ne estas ankoraŭ ebla en via operaciumo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4111"/>
        <source>Tray notifications not yet supported on your OS.</source>
        <translation>Taskopletaj sciigoj ne estas ankoraŭ eblaj en via operaciumo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4282"/>
        <source>Testing...</source>
        <translation>Testado…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4322"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation>Tio ĉi estas kanaladreso. Vi ne povas ĝin uzi kiel kvazaŭ-dissendolisto.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4382"/>
        <source>The address should start with &apos;&apos;BM-&apos;&apos;</source>
        <translation>La adreso komencu kun &quot;BM-&quot;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4385"/>
        <source>The address is not typed or copied correctly (the checksum failed).</source>
        <translation>La adreso ne estis prave tajpita aŭ kopiita (kontrolsumo malsukcesis).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4388"/>
        <source>The version number of this address is higher than this software can support. Please upgrade Bitmessage.</source>
        <translation>La numero de adresversio estas pli alta ol tiun, kiun la programo poveblas subteni. Bonvolu ĝisdatigi Bitmesaĝon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4391"/>
        <source>The address contains invalid characters.</source>
        <translation>La adreso enhavas malpermesitajn simbolojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4394"/>
        <source>Some data encoded in the address is too short.</source>
        <translation>Kelkaj datumoj koditaj en la adreso estas tro mallongaj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4397"/>
        <source>Some data encoded in the address is too long.</source>
        <translation>Kelkaj datumoj koditaj en la adreso estas tro longaj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4400"/>
        <source>Some data encoded in the address is malformed.</source>
        <translation>Kelkaj datumoj koditaj en la adreso estas misformitaj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4374"/>
        <source>Enter an address above.</source>
        <translation>Enmetu adreson supre.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4406"/>
        <source>Address is an old type. We cannot display its past broadcasts.</source>
        <translation>Malnova speco de adreso. Ne povas montri ĝiajn antaŭajn elsendojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4415"/>
        <source>There are no recent broadcasts from this address to display.</source>
        <translation>Neniaj lastatempaj elsendoj de tiu ĉi adreso por montri.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4449"/>
        <source>You are using TCP port %1. (This can be changed in the settings).</source>
        <translation>Vi uzas TCP-pordon %1 (tio ĉi estas ŝanĝebla en la agordoj).</translation>
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
        <location filename="../bitmessageqt/bitmessageui.py" line="709"/>
        <source>Search</source>
        <translation>Serĉi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="710"/>
        <source>All</source>
        <translation>Ĉio</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="717"/>
        <source>To</source>
        <translation>Al</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="719"/>
        <source>From</source>
        <translation>De</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="721"/>
        <source>Subject</source>
        <translation>Temo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="714"/>
        <source>Message</source>
        <translation>Mesaĝo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="723"/>
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
        <translation>Etikedo</translation>
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
        <location filename="../bitmessageqt/bitmessageui.py" line="706"/>
        <source>Subscriptions</source>
        <translation>Abonoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="690"/>
        <source>Add new Subscription</source>
        <translation>Aldoni novan abonon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="724"/>
        <source>Chans</source>
        <translation>Kanaloj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="708"/>
        <source>Add Chan</source>
        <translation>Aldoni kanalon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="729"/>
        <source>File</source>
        <translation>Dosiero</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="740"/>
        <source>Settings</source>
        <translation>Agordoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="736"/>
        <source>Help</source>
        <translation>Helpo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="732"/>
        <source>Import keys</source>
        <translation>Enporti ŝlosilojn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="733"/>
        <source>Manage keys</source>
        <translation>Administri ŝlosilojn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="735"/>
        <source>Ctrl+Q</source>
        <translation>Stir+Q</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="737"/>
        <source>F1</source>
        <translation>F1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="738"/>
        <source>Contact support</source>
        <translation>Peti pri helpo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="739"/>
        <source>About</source>
        <translation>Pri</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="741"/>
        <source>Regenerate deterministic addresses</source>
        <translation>Regeneri antaŭkalkuleblan adreson</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="742"/>
        <source>Delete all trashed messages</source>
        <translation>Forviŝi ĉiujn mesaĝojn el rubujo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="743"/>
        <source>Join / Create chan</source>
        <translation>Aniĝi / Krei kanalon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="172"/>
        <source>All accounts</source>
        <translation>Ĉiuj kontoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="47"/>
        <source>Zoom level %1%</source>
        <translation>Pligrandigo: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="90"/>
        <source>Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.</source>
        <translation>Eraro: Vi ne povas aldoni duoble la saman adreson al via listo. Eble renomi la jaman se vi volas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="111"/>
        <source>Add new entry</source>
        <translation>Aldoni novan elementon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4419"/>
        <source>Display the %1 recent broadcast(s) from this address.</source>
        <translation>Montri la %1 lasta(j)n elsendo(j)n de tiu adreso.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1843"/>
        <source>New version of PyBitmessage is available: %1. Download it from https://github.com/Bitmessage/PyBitmessage/releases/latest</source>
        <translation>La nova versio de PyBitmessage estas disponebla: %1. Elŝutu ĝin de https://github.com/Bitmessage/PyBitmessage/releases/latest</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2815"/>
        <source>Waiting for PoW to finish... %1%</source>
        <translation>Atendado ĝis laborpruvo finos… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2819"/>
        <source>Shutting down Pybitmessage... %1%</source>
        <translation>Fermado de PyBitmessage… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2830"/>
        <source>Waiting for objects to be sent... %1%</source>
        <translation>Atendado ĝis objektoj estos senditaj… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2840"/>
        <source>Saving settings... %1%</source>
        <translation>Konservado de agordoj… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2849"/>
        <source>Shutting down core... %1%</source>
        <translation>Fermado de kerno… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2852"/>
        <source>Stopping notifications... %1%</source>
        <translation>Haltigado de sciigoj… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2858"/>
        <source>Shutdown imminent... %1%</source>
        <translation>Fermado tuj… %1%</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/bitmessageui.py" line="686"/>
        <source>%n hour(s)</source>
        <translation><numerusform>%n horo</numerusform><numerusform>%n horoj</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="855"/>
        <source>%n day(s)</source>
        <translation><numerusform>%n tago</numerusform><numerusform>%n tagoj</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2787"/>
        <source>Shutting down PyBitmessage... %1%</source>
        <translation>Fermado de PyBitmessage… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1139"/>
        <source>Sent</source>
        <translation>Senditaj</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="91"/>
        <source>Generating one new address</source>
        <translation>Kreado de unu nova adreso</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="153"/>
        <source>Done generating address. Doing work necessary to broadcast it...</source>
        <translation>Adreso kreita. Kalkulado de laborpruvo, kiu endas por elsendi ĝin…</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="170"/>
        <source>Generating %1 new addresses.</source>
        <translation>Kreado de %1 novaj adresoj.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="247"/>
        <source>%1 is already in &apos;Your Identities&apos;. Not adding it again.</source>
        <translation>%1 jam estas en &apos;Viaj Identigoj&apos;. Ĝi ne estos aldonita ree.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="283"/>
        <source>Done generating address</source>
        <translation>Ĉiuj adresoj estas kreitaj</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="228"/>
        <source>SOCKS5 Authentication problem: %1</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="584"/>
        <source>Disk full</source>
        <translation>Disko plenplena</translation>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="584"/>
        <source>Alert: Your disk or data storage volume is full. Bitmessage will now exit.</source>
        <translation>Atentu: Via disko aŭ subdisko estas plenplena. Bitmesaĝo fermiĝos.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="752"/>
        <source>Error! Could not find sender address (your address) in the keys.dat file.</source>
        <translation>Eraro! Ne povas trovi adreson de sendanto (vian adreson) en la dosiero keys.dat.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="496"/>
        <source>Doing work necessary to send broadcast...</source>
        <translation>Kalkulado de laborpruvo, kiu endas por sendi elsendon…</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="523"/>
        <source>Broadcast sent on %1</source>
        <translation>Elsendo sendita je %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="592"/>
        <source>Encryption key was requested earlier.</source>
        <translation>Peto pri ĉifroŝlosilo jam sendita.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="629"/>
        <source>Sending a request for the recipient&apos;s encryption key.</source>
        <translation>Sendado de peto pri ĉifroŝlosilo de ricevonto.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="644"/>
        <source>Looking up the receiver&apos;s public key</source>
        <translation>Serĉado de publika ĉifroŝlosilo de ricevonto</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="678"/>
        <source>Problem: Destination is a mobile device who requests that the destination be included in the message but this is disallowed in your settings.  %1</source>
        <translation>Eraro: celadreso estas portebla aparato kiu necesas, ke la celadreso estu enhavita en la mesaĝo, sed tio estas malpermesita ne viaj agordoj. %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="692"/>
        <source>Doing work necessary to send message.
There is no required difficulty for version 2 addresses like this.</source>
        <translation>Kalkulado de laborpruvo, kiu endas por sendi mesaĝon.
Malfacilaĵo ne estas bezonata por adresoj versioj 2, kiel tiu ĉi adreso.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="706"/>
        <source>Doing work necessary to send message.
Receiver&apos;s required difficulty: %1 and %2</source>
        <translation>Kalkulado de laborpruvo, kiu endas por sendi mesaĝon.
Ricevonto postulas malfacilaĵon: %1 kaj %2</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="715"/>
        <source>Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do. %3</source>
        <translation>Eraro: la demandita laboro de la ricevonto (%1 kaj %2) estas pli malfacila ol vi pretas fari. %3</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="727"/>
        <source>Problem: You are trying to send a message to yourself or a chan but your encryption key could not be found in the keys.dat file. Could not encrypt message. %1</source>
        <translation>Eraro: Vi provis sendi mesaĝon al vi mem aŭ al kanalo, tamen via ĉifroŝlosilo ne estas trovebla en la dosiero keys.dat. Mesaĝo ne povis esti ĉifrita. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1041"/>
        <source>Doing work necessary to send message.</source>
        <translation>Kalkulado de laborpruvo, kiu endas por sendi mesaĝon.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="850"/>
        <source>Message sent. Waiting for acknowledgement. Sent on %1</source>
        <translation>Mesaĝo sendita. Atendado je konfirmo. Sendita je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1029"/>
        <source>Doing work necessary to request encryption key.</source>
        <translation>Kalkulado de laborpruvo, kiu endas por peti pri ĉifroŝlosilo.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="974"/>
        <source>Broadcasting the public key request. This program will auto-retry if they are offline.</source>
        <translation>Elsendado de peto pri publika ĉifroŝlosilo. La programo reprovos se ili estas eksterrete.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="976"/>
        <source>Sending public key request. Waiting for reply. Requested at %1</source>
        <translation>Sendado de peto pri publika ĉifroŝlosilo. Atendado je respondo. Petis je %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="224"/>
        <source>UPnP port mapping established on port %1</source>
        <translation>UPnP pord-mapigo farita je pordo %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="253"/>
        <source>UPnP port mapping removed</source>
        <translation>UPnP pord-mapigo forigita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="285"/>
        <source>Mark all messages as read</source>
        <translation>Marki ĉiujn mesaĝojn kiel legitajn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2661"/>
        <source>Are you sure you would like to mark all messages read?</source>
        <translation>Ĉu vi certe volas marki ĉiujn mesaĝojn kiel legitajn?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1050"/>
        <source>Doing work necessary to send broadcast.</source>
        <translation>Kalkulado de laborpruvo, kiu endas por sendi elsendon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2754"/>
        <source>Proof of work pending</source>
        <translation>Laborpruvo haltigita</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2754"/>
        <source>%n object(s) pending proof of work</source>
        <translation><numerusform>Haltigis laborpruvon por %n objekto</numerusform><numerusform>Haltigis laborpruvon por %n objektoj</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2754"/>
        <source>%n object(s) waiting to be distributed</source>
        <translation><numerusform>%n objekto atendas je sendato</numerusform><numerusform>%n objektoj atendas je sendato</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2754"/>
        <source>Wait until these tasks finish?</source>
        <translation>Ĉu atendi ĝis tiujn taskojn finos?</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="211"/>
        <source>Problem communicating with proxy: %1. Please check your network settings.</source>
        <translation>Eraro dum komunikado kun prokurilo: %1. Bonvolu kontroli viajn retajn agordojn.</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="240"/>
        <source>SOCKS5 Authentication problem: %1. Please check your SOCKS5 settings.</source>
        <translation>Eraro dum SOCKS5 aŭtentigado: %1. Bonvolu kontroli viajn SOCKS5-agordojn.</translation>
    </message>
    <message>
        <location filename="../class_receiveDataThread.py" line="171"/>
        <source>The time on your computer, %1, may be wrong. Please verify your settings.</source>
        <translation>La horloĝo de via komputilo, %1, eble eraras. Bonvolu kontroli viajn agordojn.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="101"/>
        <source>The name %1 was not found.</source>
        <translation>La nomo %1 ne trovita.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="110"/>
        <source>The namecoin query failed (%1)</source>
        <translation>La namecoin-peto fiaskis (%1)</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="113"/>
        <source>The namecoin query failed.</source>
        <translation>La namecoin-peto fiaskis.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="119"/>
        <source>The name %1 has no valid JSON data.</source>
        <translation>La nomo %1 ne havas ĝustajn JSON-datumojn.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="127"/>
        <source>The name %1 has no associated Bitmessage address.</source>
        <translation>La nomo %1 ne estas atribuita kun bitmesaĝa adreso.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="147"/>
        <source>Success!  Namecoind version %1 running.</source>
        <translation>Sukceso! Namecoind versio %1 funkcias.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="153"/>
        <source>Success!  NMControll is up and running.</source>
        <translation>Sukceso! NMControl funkcias ĝuste.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="156"/>
        <source>Couldn&apos;t understand NMControl.</source>
        <translation>Ne povis kompreni NMControl.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="118"/>
        <source>Your GPU(s) did not calculate correctly, disabling OpenCL. Please report to the developers.</source>
        <translation>Via(j) vidprocesoro(j) ne kalkulis senerare, malaktiviganta OpenCL. Bonvolu raporti tion al programistoj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="668"/>
        <source>
        Welcome to easy and secure Bitmessage
            * send messages to other people
            * send broadcast messages like twitter or
            * discuss in chan(nel)s with other people
        </source>
        <translation>
Bonvenon al facila kaj sekura Bitmesaĝo
* sendi mesaĝojn al aliaj homoj
* sendi elsendajn mesaĝojn (kiel per Tvitero)
* babili kun aliaj uloj en mesaĝ-kanaloj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="846"/>
        <source>not recommended for chans</source>
        <translation>malkonsilinda por kanaloj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1679"/>
        <source>Problems connecting? Try enabling UPnP in the Network Settings</source>
        <translation>Ĉu problemo kun konektado? Provu aktivigi UPnP en retaj agordoj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2001"/>
        <source>Error: Bitmessage addresses start with BM-   Please check the recipient address %1</source>
        <translation>Eraro: bitmesaĝaj adresoj komenciĝas kun BM-. Bonvolu kontroli la adreson de ricevonto %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2004"/>
        <source>Error: The recipient address %1 is not typed or copied correctly. Please check it.</source>
        <translation>Eraro: la adreso de ricevonto %1 estas malprave tajpita aŭ kopiita. Bonvolu kontroli ĝin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2007"/>
        <source>Error: The recipient address %1 contains invalid characters. Please check it.</source>
        <translation>Eraro: la adreso de ricevonto %1 enhavas malpermesatajn simbolojn. Bonvolu kontroli ĝin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2010"/>
        <source>Error: The version of the recipient address %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</source>
        <translation>Eraro: la versio de adreso de ricevonto %1 estas tro alta. Eble vi devas ĝisdatigi vian bitmesaĝan programon aŭ via sagaca konato uzas alian programon.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2013"/>
        <source>Error: Some data encoded in the recipient address %1 is too short. There might be something wrong with the software of your acquaintance.</source>
        <translation>Eraro: kelkaj datumoj koditaj en la adreso de ricevonto %1 estas tro mallongaj. Povus esti ke io en la programo de via konato malfunkcias.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2016"/>
        <source>Error: Some data encoded in the recipient address %1 is too long. There might be something wrong with the software of your acquaintance.</source>
        <translation>Eraro: kelkaj datumoj koditaj en la adreso de ricevonto %1 estas tro longaj. Povus esti ke io en la programo de via konato malfunkcias.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2019"/>
        <source>Error: Some data encoded in the recipient address %1 is malformed. There might be something wrong with the software of your acquaintance.</source>
        <translation>Eraro: kelkaj datumoj koditaj en la adreso de ricevonto %1 estas misformitaj. Povus esti ke io en la programo de via konato malfunkcias.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2022"/>
        <source>Error: Something is wrong with the recipient address %1.</source>
        <translation>Eraro: io malĝustas kun la adreso de ricevonto %1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2765"/>
        <source>Synchronisation pending</source>
        <translation>Samtempigado haltigita</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2765"/>
        <source>Bitmessage hasn&apos;t synchronised with the network, %n object(s) to be downloaded. If you quit now, it may cause delivery delays. Wait until the synchronisation finishes?</source>
        <translation><numerusform>Bitmesaĝo ne estas samtempigita kun la reto, %n objekto elŝutendas. Se vi eliros nun, tio povas igi malfruiĝojn de liveradoj. Ĉu atendi ĝis la samtempigado finiĝos?</numerusform><numerusform>Bitmesaĝo ne estas samtempigita kun la reto, %n objektoj elŝutendas. Se vi eliros nun, tio povas igi malfruiĝojn de liveradoj. Ĉu atendi ĝis la samtempigado finiĝos?</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2776"/>
        <source>Not connected</source>
        <translation>Nekonektita</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2776"/>
        <source>Bitmessage isn&apos;t connected to the network. If you quit now, it may cause delivery delays. Wait until connected and the synchronisation finishes?</source>
        <translation>Bitmesaĝo ne estas konektita al la reto. Se vi eliros nun, tio povas igi malfruiĝojn de liveradoj. Ĉu atendi ĝis ĝi konektos kaj la samtempigado finiĝos?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2791"/>
        <source>Waiting for network connection...</source>
        <translation>Atendado je retkonekto…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2799"/>
        <source>Waiting for finishing synchronisation...</source>
        <translation>Atendado ĝis samtempigado finiĝos…</translation>
    </message>
</context>
<context>
    <name>MessageView</name>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="67"/>
        <source>Follow external link</source>
        <translation>Sekvi la eksteran ligilon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="67"/>
        <source>The link &quot;%1&quot; will open in a browser. It may be a security risk, it could de-anonymise you or download malicious data. Are you sure?</source>
        <translation>La ligilo &quot;%1&quot; estos malfermita per foliumilo. Tio povas esti malsekura, ĝi povos malanonimigi vin aŭ elŝuti malicajn datumojn. Ĉu vi certas?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="112"/>
        <source>HTML detected, click here to display</source>
        <translation>HTML detektita, alklaku ĉi tie por montri</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="121"/>
        <source>Click here to disable HTML</source>
        <translation>Alklaku ĉi tie por malaktivigi HTML</translation>
    </message>
</context>
<context>
    <name>MsgDecode</name>
    <message>
        <location filename="../helper_msgcoding.py" line="72"/>
        <source>The message has an unknown encoding.
Perhaps you should upgrade Bitmessage.</source>
        <translation>La mesaĝo enhavas nekonatan kodoprezenton.
Eble vi devas ĝisdatigi Bitmesaĝon.</translation>
    </message>
    <message>
        <location filename="../helper_msgcoding.py" line="73"/>
        <source>Unknown encoding</source>
        <translation>Nekonata kodoprezento</translation>
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
        <translation>Tie ĉi vi povas generi tiom da adresoj, kiom vi volas. Ververe kreado kaj forlasado de adresoj estas konsilinda. Vi povas krei adresojn uzante hazardajn nombrojn aŭ pasfrazon. Se vi uzos pasfrazon, la adreso estas nomita kiel &apos;antaŭkalkulebla&apos; (determinisma) adreso.
La &apos;hazardnombra&apos; adreso estas antaŭagordita, sed antaŭkalkuleblaj adresoj havas kelkajn bonaĵojn kaj malbonaĵojn:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="176"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Pros:&lt;br/&gt;&lt;/span&gt;You can recreate your addresses on any computer from memory. &lt;br/&gt;You need-not worry about backing up your keys.dat file as long as you can remember your passphrase. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Cons:&lt;br/&gt;&lt;/span&gt;You must remember (or write down) your passphrase if you expect to be able to recreate your keys if they are lost. &lt;br/&gt;You must remember the address version number and the stream number along with your passphrase. &lt;br/&gt;If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Bonaĵoj:&lt;br/&gt;&lt;/span&gt;Vi poveblas rekrei viajn adresojn per iu ajn komputilo elkape.&lt;br/&gt;Vi ne devas klopodi fari sekurkopion de keys.dat dosiero tiel longe, dum vi memoras vian pasfrazon.&lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Malbonaĵoj:&lt;br/&gt;&lt;/span&gt;Vi devas memori (aŭ konservi) vian pasfrazon se vi volas rekrei viajn ŝlosilojn kiam vi perdos ilin.&lt;br/&gt;Vi devas memori nombron de adresversio kaj de fluo kune kun vian pasfrazon.&lt;br/&gt;Se vi elektos malfortan pasfrazon kaj iu ajn Interrete eblos brutforti ĝin, li povos legi ĉiujn viajn mesaĝojn kaj sendi mesaĝojn kiel vi.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
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
        <translation>Fari antaŭkalkuleblan adreson</translation>
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
        <translation>Nombro da farotaj adresoj bazante sur via pasfrazo:</translation>
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
        <translation>(plej bone se tiun ĉi estas la unuan de ĉiuj adresojn vi kreos)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="191"/>
        <source>Use the same stream as an existing address</source>
        <translation>Uzi saman fluon kiel ekzistan adreson</translation>
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
        <location filename="../bitmessageqt/about.py" line="68"/>
        <source>About</source>
        <translation>Pri</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="69"/>
        <source>PyBitmessage</source>
        <translation>PyBitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>version ?</source>
        <translation>versio ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="72"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distributed under the MIT/X11 software license; see &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distribuata laŭ la permesilo &quot;MIT/X11 software license&quot;; vidu &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="73"/>
        <source>This is Beta software.</source>
        <translation>Tio ĉi estas beta-eldono.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright Â© 2012-2016 Jonathan Warren&lt;br/&gt;Copyright Â© 2013-2016 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="71"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright &amp;copy; 2012-2016 Jonathan Warren&lt;br/&gt;Copyright &amp;copy; 2013-2016 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Kopirajto &amp;copy; 2012-2016 Jonathan WARREN&lt;br/&gt;Kopirajto &amp;copy; 2013-2016 La programistoj de Bitmesaĝo&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
</context>
<context>
    <name>blacklist</name>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="17"/>
        <source>Use a Blacklist (Allow all incoming messages except those on the Blacklist)</source>
        <translation>Uzi nigran liston (permesas ĉiujn alvenajn mesaĝojn escepte tiujn en la nigra listo)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="27"/>
        <source>Use a Whitelist (Block all incoming messages except those on the Whitelist)</source>
        <translation>Uzi blankan liston (blokas ĉiujn alvenajn mesaĝojn escepte tiujn en la blanka listo)</translation>
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
        <location filename="../bitmessageqt/blacklist.py" line="150"/>
        <source>Blacklist</source>
        <translation>Nigra listo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="152"/>
        <source>Whitelist</source>
        <translation>Blanka listo</translation>
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
        <translation>Vi havas neniujn konektojn al aliaj samtavolanoj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="84"/>
        <source>You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn&apos;t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.</source>
        <translation>Vi konektis almenaŭ al unu samtavolano uzante elirantan konekton, sed vi ankoraŭ ne ricevis enirantajn konektojn. Via fajroŝirmilo (firewall) aŭ hejma enkursigilo (router) verŝajne estas agordita por ne plusendi enirantajn TCP konektojn al via komputilo. Bitmesaĝo funkcios sufiĉe bone, sed helpus al la bitmesaĝa reto se vi permesus enirantajn konektojn kaj tiel estus pli bone konektita nodo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="85"/>
        <source>You are using TCP port ?. (This can be changed in the settings).</source>
        <translation>Vi uzas TCP-pordon ?. (Ĝi estas ŝanĝebla en la agordoj).</translation>
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
        <location filename="../bitmessageqt/networkstatus.ui" line="159"/>
        <source>Since startup:</source>
        <translation>Ekde starto:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="175"/>
        <source>Processed 0 person-to-person messages.</source>
        <translation>Pritraktis 0 inter-personajn mesaĝojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="204"/>
        <source>Processed 0 public keys.</source>
        <translation>Pritraktis 0 publikajn ŝlosilojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="191"/>
        <source>Processed 0 broadcasts.</source>
        <translation>Pritraktis 0 elsendojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="256"/>
        <source>Inventory lookups per second: 0</source>
        <translation>Petoj pri inventaro en sekundo: 0</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="217"/>
        <source>Objects to be synced:</source>
        <translation>Samtempigotaj eroj:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="129"/>
        <source>Stream #</source>
        <translation>Fluo #</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="116"/>
        <source>Connections</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="129"/>
        <source>Since startup on %1</source>
        <translation>Ekde lanĉo de la programo je %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="73"/>
        <source>Down: %1/s  Total: %2</source>
        <translation>Elŝuto: %1/s Sume: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="75"/>
        <source>Up: %1/s  Total: %2</source>
        <translation>Alŝuto: %1/s Sume: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="108"/>
        <source>Total Connections: %1</source>
        <translation>Ĉiuj konektoj: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="118"/>
        <source>Inventory lookups per second: %1</source>
        <translation>Petoj pri inventaro en sekundo: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="230"/>
        <source>Up: 0 kB/s</source>
        <translation>Alŝuto: 0 kB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="243"/>
        <source>Down: 0 kB/s</source>
        <translation>Elŝuto: 0 kB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="728"/>
        <source>Network Status</source>
        <translation>Reta stato</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="40"/>
        <source>byte(s)</source>
        <translation><numerusform>bitoko</numerusform><numerusform>bitokoj</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="51"/>
        <source>Object(s) to be synced: %n</source>
        <translation><numerusform>Objekto por samtempigi: %n</numerusform><numerusform>Objektoj por samtempigi: %n</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="55"/>
        <source>Processed %n person-to-person message(s).</source>
        <translation><numerusform>Pritraktis %n inter-personan mesaĝon.</numerusform><numerusform>Pritraktis %n inter-personajn mesaĝojn.</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="60"/>
        <source>Processed %n broadcast message(s).</source>
        <translation><numerusform>Pritraktis %n elsendon.</numerusform><numerusform>Pritraktis %n elsendojn.</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="65"/>
        <source>Processed %n public key(s).</source>
        <translation><numerusform>Pritraktis %n publikan ŝlosilon.</numerusform><numerusform>Pritraktis %n publikajn ŝlosilojn.</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="114"/>
        <source>Peer</source>
        <translation>Samtavolano</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="119"/>
        <source>User agent</source>
        <translation>Klienta aplikaĵo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="124"/>
        <source>TLS</source>
        <translation>TLS</translation>
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
        <translation>Krei aŭ aniĝi kanalon</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="41"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly, then the chan will be secure and private. However if you and someone else both create a chan with the same chan name, the same chan will be shared.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Kanalo ekzistas kiam grupo da personoj kunhavas la komunajn malĉifrajn ŝlosilojn. La ŝlosiloj kaj bitmesaĝa adreso uzataj de kanalo estas generitaj el hom-legebla vorto aŭ frazo (la kanala nomo). Por sendi mesaĝon al ĉiuj en la kanalo, sendu mesaĝon al la kanala adreso.&lt;/p&gt;&lt;p&gt;Kanaloj estas eksperimentaj kaj tute neadministreblaj.&lt;/p&gt;&lt;p&gt;Entajpu nomon por via kanalo. Se vi elektos sufiĉe ampleksan kanalan nomon (kiel fortan kaj unikan pasfrazon) kaj neniu de viaj amikoj komunikos ĝin publike, la kanalo estos sekura kaj privata. Tamen se vi kaj iu ajn kreos kanalon kun la sama nomo, tiam ili iĝos tre verŝajne la saman kanalon.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="56"/>
        <source>Chan passhphrase/name:</source>
        <translation>Kanala pasfrazo/nomo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="63"/>
        <source>Optional, for advanced usage</source>
        <translation>Malnepra, por sperta uzado</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="76"/>
        <source>Chan address</source>
        <translation>Kanala adreso</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="101"/>
        <source>Please input chan name/passphrase:</source>
        <translation>Bonvolu entajpu kanalan nomon/pasfrazon:</translation>
    </message>
</context>
<context>
    <name>newchandialog</name>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="40"/>
        <source>Successfully created / joined chan %1</source>
        <translation>Sukcese kreis / aniĝis al la kanalo %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="44"/>
        <source>Chan creation / joining failed</source>
        <translation>Kreado / aniĝado al kanalo malsukcesis</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="50"/>
        <source>Chan creation / joining cancelled</source>
        <translation>Kreado / aniĝado al kanalo nuligita</translation>
    </message>
</context>
<context>
    <name>proofofwork</name>
    <message>
        <location filename="../proofofwork.py" line="161"/>
        <source>C PoW module built successfully.</source>
        <translation>C PoW modulo konstruita sukcese.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="163"/>
        <source>Failed to build C PoW module. Please build it manually.</source>
        <translation>Malsukcesis konstrui C PoW modulon. Bonvolu konstrui ĝin permane.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="165"/>
        <source>C PoW module unavailable. Please build it.</source>
        <translation>C PoW modulo nedisponebla. Bonvolu konstrui ĝin.</translation>
    </message>
</context>
<context>
    <name>qrcodeDialog</name>
    <message>
        <location filename="../plugins/qrcodeui.py" line="67"/>
        <source>QR-code</source>
        <translation>QR-kodo</translation>
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
        <translation>Nombro da farotaj adresoj bazante sur via pasfrazo:</translation>
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
        <translation>Vi devas marki (aŭ ne marki) ĉi tiun markobutonon samkiel vi faris kiam vi generis vian adreson unuafoje.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="123"/>
        <source>If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.</source>
        <translation>Se vi antaŭe kreis antaŭkalkuleblajn (determinismajn) adresojn sed perdis ilin akcidente (ekz. en diska paneo), vi povas regeneri ilin ĉi tie. Se vi uzis la generilo de hazardnombroj por krei vian adreson tiu formularo ne taŭgos por vi.</translation>
    </message>
</context>
<context>
    <name>settingsDialog</name>
    <message>
        <location filename="../bitmessageqt/settings.py" line="453"/>
        <source>Settings</source>
        <translation>Agordoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="454"/>
        <source>Start Bitmessage on user login</source>
        <translation>Startigi Bitmesaĝon dum ensaluto de uzanto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="455"/>
        <source>Tray</source>
        <translation>Taskopleto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="456"/>
        <source>Start Bitmessage in the tray (don&apos;t show main window)</source>
        <translation>Startigi Bitmesaĝon en la taskopleto (tray) ne montrante tiun fenestron</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="457"/>
        <source>Minimize to tray</source>
        <translation>Plejetigi al taskopleto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="458"/>
        <source>Close to tray</source>
        <translation>Fermi al taskopleto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="460"/>
        <source>Show notification when message received</source>
        <translation>Montri sciigon kiam mesaĝo alvenas</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="461"/>
        <source>Run in Portable Mode</source>
        <translation>Ekzekucii en Portebla Reĝimo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="462"/>
        <source>In Portable Mode, messages and config files are stored in the same directory as the program rather than the normal application-data folder. This makes it convenient to run Bitmessage from a USB thumb drive.</source>
        <translation>En Portebla Reĝimo, mesaĝoj kaj agordoj estas enmemorigitaj en la sama dosierujo kiel la programo mem anstataŭ en la dosierujo por datumoj de aplikaĵoj. Tio igas ĝin komforta ekzekucii Bitmesaĝon el USB poŝmemorilo.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="463"/>
        <source>Willingly include unencrypted destination address when sending to a mobile device</source>
        <translation>Volonte inkluzivi malĉifritan cel-adreson dum sendado al portebla aparato.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="464"/>
        <source>Use Identicons</source>
        <translation>Uzi ID-avatarojn</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="465"/>
        <source>Reply below Quote</source>
        <translation>Respondi sub citaĵo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="466"/>
        <source>Interface Language</source>
        <translation>Fasada lingvo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="467"/>
        <source>System Settings</source>
        <comment>system</comment>
        <translation>Sistemaj agordoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="468"/>
        <source>User Interface</source>
        <translation>Fasado</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="469"/>
        <source>Listening port</source>
        <translation>Aŭskultanta pordo (port)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="470"/>
        <source>Listen for connections on port:</source>
        <translation>Aŭskulti pri konektoj ĉe pordo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="471"/>
        <source>UPnP:</source>
        <translation>UPnP:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="472"/>
        <source>Bandwidth limit</source>
        <translation>Rettrafika limo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Maximum download rate (kB/s): [0: unlimited]</source>
        <translation>Maksimuma rapido de elŝuto (kB/s): [0: senlima]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="474"/>
        <source>Maximum upload rate (kB/s): [0: unlimited]</source>
        <translation>Maksimuma rapido de alŝuto (kB/s): [0: senlima]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="476"/>
        <source>Proxy server / Tor</source>
        <translation>Prokurila (proxy) servilo / Tor</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="477"/>
        <source>Type:</source>
        <translation>Speco:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="478"/>
        <source>Server hostname:</source>
        <translation>Servilo gastiga nomo (hostname):</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="501"/>
        <source>Port:</source>
        <translation>Pordo (port):</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="480"/>
        <source>Authentication</source>
        <translation>Aŭtentigo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="502"/>
        <source>Username:</source>
        <translation>Uzantnomo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="482"/>
        <source>Pass:</source>
        <translation>Pasvorto:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="483"/>
        <source>Listen for incoming connections when using proxy</source>
        <translation>Aŭskulti pri alvenaj konektoj kiam dum uzado de prokurilo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="484"/>
        <source>none</source>
        <translation>neniu</translation>
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
        <translation>Retaj agordoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="488"/>
        <source>Total difficulty:</source>
        <translation>Tuta malfacilaĵo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="489"/>
        <source>The &apos;Total difficulty&apos; affects the absolute amount of work the sender must complete. Doubling this value doubles the amount of work.</source>
        <translation>La &apos;Tuta malfacilaĵo&apos; efikas sur la tuta kvalito da laboro, kiun la sendonto devos fari. Duobligo de tiu valoro, duobligas la kvanton de laboro.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="490"/>
        <source>Small message difficulty:</source>
        <translation>Et-mesaĝa malfacilaĵo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="491"/>
        <source>When someone sends you a message, their computer must first complete some work. The difficulty of this work, by default, is 1. You may raise this default for new addresses you create by changing the values here. Any new addresses you create will require senders to meet the higher difficulty. There is one exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically notify them when you next send a message that they need only complete the minimum amount of work: difficulty 1. </source>
        <translation>Kiam iu ajn sendas al vi mesaĝon, lia komputilo devas unue fari iom da laboro. La malfacilaĵo de tiu laboro implicite estas 1. Vi povas pligrandigi tiun valoron por novaj adresoj, kiujn vi generos per ŝanĝo de ĉi-tiaj valoroj. Ĉiuj novaj adresoj kreotaj de vi bezonos por ke sendontoj akceptu pli altan malfacilaĵon. Estas unu escepto: se vi aldonos kolegon al vi adresaro, Bitmesaĝo aŭtomate sciigos lin kiam vi sendos mesaĝon, ke li bezonos fari nur minimuman kvaliton da laboro: malfacilaĵo 1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="492"/>
        <source>The &apos;Small message difficulty&apos; mostly only affects the difficulty of sending small messages. Doubling this value makes it almost twice as difficult to send a small message but doesn&apos;t really affect large messages.</source>
        <translation>La &apos;Et-mesaĝa malfacilaĵo&apos; ĉefe efikas malfacilaĵon por sendi malgrandajn mesaĝojn. Duobligo de tiu valoro, preskaŭ duobligas malfacilaĵon por sendi malgrandajn mesaĝojn, sed preskaŭ ne efikas grandajn mesaĝojn.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="493"/>
        <source>Demanded difficulty</source>
        <translation>Postulata malfacilaĵo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="494"/>
        <source>Here you may set the maximum amount of work you are willing to do to send a message to another person. Setting these values to 0 means that any value is acceptable.</source>
        <translation>Tie ĉi vi povas agordi maksimuman kvanton da laboro kiun vi faru por sendi mesaĝon al alian persono. Se vi agordos ilin al 0, ĉiuj valoroj estos akceptitaj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="495"/>
        <source>Maximum acceptable total difficulty:</source>
        <translation>Maksimuma akceptata tuta malfacilaĵo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="496"/>
        <source>Maximum acceptable small message difficulty:</source>
        <translation>Maksimuma akceptata malfacilaĵo por et-mesaĝoj:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="497"/>
        <source>Max acceptable difficulty</source>
        <translation>Maksimuma akcepta malfacilaĵo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Hardware GPU acceleration (OpenCL)</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="499"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage can utilize a different Bitcoin-based program called Namecoin to make addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage address, you can simply tell him to send a message to &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Getting your own Bitmessage address into Namecoin is still rather difficult).&lt;/p&gt;&lt;p&gt;Bitmessage can use either namecoind directly or a running nmcontrol instance.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmesaĝo povas apliki alian Bitmono-bazitan programon - Namecoin - por fari adresojn hom-legeblajn. Ekzemple anstataŭ diri al via amiko longan Bitmesaĝan adreson, vi povas simple peti lin pri sendi mesaĝon al &lt;span style=&quot; font-style:italic;&quot;&gt;id/kashnomo. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Kreado de sia propra Bitmesaĝa adreso en Namecoin-on estas ankoraŭ ete malfacila).&lt;/p&gt;&lt;p&gt;Bitmesaĝo eblas uzi aŭ na namecoind rekte aŭ jaman aktivan aperon de nmcontrol.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="500"/>
        <source>Host:</source>
        <translation>Gastiga servilo:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="503"/>
        <source>Password:</source>
        <translation>Pasvorto:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="504"/>
        <source>Test</source>
        <translation>Testi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="505"/>
        <source>Connect to:</source>
        <translation>Konekti al:</translation>
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
        <translation>Integrigo kun Namecoin</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="509"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;By default, if you send a message to someone and he is offline for more than two days, Bitmessage will send the message again after an additional two days. This will be continued with exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain number of days or months.&lt;/p&gt;&lt;p&gt;Leave these input fields blank for the default behavior. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Implicite se vi sendas mesaĝon al iu kaj li estos eksterrete por iomete da tempo, Bitmesaĝo provos resendi mesaĝon iam poste, kaj iam pli poste. La programo pluigos resendi mesaĝon ĝis sendonto konfirmos liveron. Tie ĉi vi povas ŝanĝi kiam Bitmesaĝo devos rezigni je sendado.&lt;/p&gt;&lt;p&gt;Lasu tiujn kampojn malplenaj por antaŭagordita sinteno.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="510"/>
        <source>Give up after</source>
        <translation>Rezigni post</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="511"/>
        <source>and</source>
        <translation>kaj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="512"/>
        <source>days</source>
        <translation>tagoj</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="513"/>
        <source>months.</source>
        <translation>monatoj.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="514"/>
        <source>Resends Expire</source>
        <translation>Resenda fortempiĝo</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="459"/>
        <source>Hide connection notifications</source>
        <translation>Ne montri sciigojn pri konekto</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="475"/>
        <source>Maximum outbound connections: [0: none]</source>
        <translation>Maksimumo de eligaj konektoj: [0: senlima]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="498"/>
        <source>Hardware GPU acceleration (OpenCL):</source>
        <translation>Aparatara GPU-a plirapidigo (OpenCL):</translation>
    </message>
</context>
</TS>