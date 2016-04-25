<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS><TS version="2.0" language="de" sourcelanguage="en">
<context>
    <name>AddAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="62"/>
        <source>Add new entry</source>
        <translation>Neuen Eintrag erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="63"/>
        <source>Label</source>
        <translation>Name oder Bezeichnung</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="64"/>
        <source>Address</source>
        <translation>Adresse</translation>
    </message>
</context>
<context>
    <name>EmailGatewayDialog</name>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="67"/>
        <source>Email gateway</source>
        <translation>E-Mail Schnittstelle</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="68"/>
        <source>Register on email gateway</source>
        <translation>An E-Mailschnittstelle registrieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="69"/>
        <source>Account status at email gateway</source>
        <translation>Statusanfrage der E-Mailschnittstelle</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="70"/>
        <source>Change account settings at email gateway</source>
        <translation>E-Mailschnittstelleneinstellungen ändern</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="71"/>
        <source>Unregister from email gateway</source>
        <translation>Von der E-Mailschnittstelle abmelden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="72"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.</source>
        <translation>E-Mailschnittstelle ermöglicht es mit anderen E-Mailnutzern zu kommunizieren. Zur Zeit ist nur die Mailchuck-E-Mailschnittstelle (@mailchuck.com) verfügbar.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="73"/>
        <source>Desired email address (including @mailchuck.com):</source>
        <translation>Gewünschte E-Mailaddresse (inkl. @mailchuck.com):</translation>
    </message>
</context>
<context>
    <name>EmailGatewayRegistrationDialog</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2238"/>
        <source>Registration failed:</source>
        <translation>Registrierung fehlgeschlagen:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2238"/>
        <source>The requested email address is not available, please try a new one. Fill out the new desired email address (including @mailchuck.com) below:</source>
        <translation>Die gewünschte E-Mailaddresse ist nicht verfügbar, bitte probieren Sie eine neue. Die gewünschte E-Mailaddresse (inkl. @mailchuck.com) unten ausfüllen:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="102"/>
        <source>Email gateway registration</source>
        <translation>E-Mailschnittstellenregistrierung</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="103"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.
Please type the desired email address (including @mailchuck.com) below:</source>
        <translation>E-Mail-Schnittstelle ermöglicht es, mit anderen E-Mail-Nutzern zu kommunizieren. Zur Zeit ist nur die Mailchuck-E-Mail-Schnittstelle verfügbar (@mailchuck.com).
Bitte füllen Sie die gewünschte E-Mail-Address (inkl. @mailchuck.com) unten:</translation>
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
        <translation>
# Diese Nachricht können Sie für die Änderung Ihrer Einstellungen an der
# E-Mail-Schnittstelle verwenden. Unkommentieren Sie die Einstellung, die Sie
# ändern möchten. Dies sind die verfügbaren Einstellungen:
# 
# pgp: server
# The E-Mail-Schnittstelle wird für Sie PGP-Schlüssel erzeugen, und die
# Nachrichten für Sie unterschreiben, Unterschriften überprüfen, ver- und
# entschlüsseln. Verwenden Sie diese Option, wenn Sie PGP verwenden möchten
# aber es sonst zu umständig finden. Erfordert Abonnement.
#
# pgp: local
# Die E-Mail-Schnittstelle wird keine PGP-verarbeitung für Sie machen. Sie
# können auf die Verwendung von PGP entweder ganz verzichten, oder es lokal
# machen.
#
# attachments: yes
# Eingehende Dateianhänge von E-Mails werden zu MEGA.nz hochgeladen, und Sie
# können diese über einen Link in der Nachricht herunterladen. Erfordert
# Abonnement.
#
# attachments: no
# Anhänge werden ignoriert.
# 
# archive: yes
# Ihre eingehende E-Mails werden auf dem Server archiviert. Nutzen Sie dies,
# wenn Sie Hilfe bei Debugging benötigen, oder eine Bestätigung von dritter
# Partei über die E-Mails benötigen. Diese Einstellung bedeutet jedoch, dass
# der Betreiber der Dienstleistung Ihre E-Mails auch lesen kann nachdem sie
# diese erhalten haben.
#
# archive: no
# Eingehende E-Mails werden gleich nach dem Übertragen zu Ihnen bei dem
# Schnittstellenbetreiber gelöscht.
#
# masterpubkey_btc: BIP44-xpub-Schlüssel oder electrum v1 Seed
# offset_btc: Ganzzahl (Voreingestellt auf 0)
# feeamount: Zahl mit bis zu 8 Nachkommastellen
# feecurrency: BTC, XBT, USD, EUR oder GBP
# Nutzen Sie diese Variablen, wenn Sie von den Absendern eine Zahlung
# verlangen. Wenn diese Option eingeschaltet ist und Sie eine E-Mail von einer
# noch nicht bekannten E-Mail-Addresse erhalten, wird die E-Mail abgelehnt und
# der Absender erhällt eine Zahlungsaufforderung in der spezifizierten Höhe. Da
# diese Methode deterministische öffentliche Schlüssel verwendet, erhaltne Sie
# die Zalungen direkt. Um es wieder auszuschalten, ändern Sie die
# &quot;feeamount&quot;-Variable auf 0. Erfordert Abonnement.</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="177"/>
        <source>Reply to sender</source>
        <translation>Dem Absender Antworten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="179"/>
        <source>Reply to channel</source>
        <translation>Antworten ins Chan</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="181"/>
        <source>Add sender to your Address Book</source>
        <translation>Absender zum Adressbuch hinzufügen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="185"/>
        <source>Add sender to your Blacklist</source>
        <translation>Absender in die Blacklist eintragen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="363"/>
        <source>Move to Trash</source>
        <translation>In den Papierkorb verschieben</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="192"/>
        <source>Undelete</source>
        <translation>Wiederherstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="195"/>
        <source>View HTML code as formatted text</source>
        <translation>HTML als formatierten Text anzeigen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="199"/>
        <source>Save message as...</source>
        <translation>Nachricht speichern unter...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="203"/>
        <source>Mark Unread</source>
        <translation>Als ungelesen markieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="335"/>
        <source>New</source>
        <translation>Neu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="122"/>
        <source>Enable</source>
        <translation>Aktivieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="125"/>
        <source>Disable</source>
        <translation>Deaktivieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="128"/>
        <source>Set avatar...</source>
        <translation>Avatar wählen...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="118"/>
        <source>Copy address to clipboard</source>
        <translation>Adresse in die Zwischenablage kopieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="286"/>
        <source>Special address behavior...</source>
        <translation>Spezielles Verhalten der Adresse...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="251"/>
        <source>Email gateway</source>
        <translation>E-Mail Schnittstelle</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="115"/>
        <source>Delete</source>
        <translation>Löschen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="302"/>
        <source>Send message to this address</source>
        <translation>Nachricht an diese Adresse senden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="310"/>
        <source>Subscribe to this address</source>
        <translation>Diese Adresse abonnieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="318"/>
        <source>Add New Address</source>
        <translation>Neue Adresse hinzufügen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="366"/>
        <source>Copy destination address to clipboard</source>
        <translation>Zieladresse in die Zwischenablage kopieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="370"/>
        <source>Force send</source>
        <translation>Senden erzwingen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="578"/>
        <source>One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?</source>
        <translation>Eine Ihrer Adressen, %1, ist eine alte Version 1 Adresse. Version 1 Adressen werden nicht mehr unterstützt. Soll sie jetzt gelöscht werden?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="798"/>
        <source>1 hour</source>
        <translation>1 Stunde</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="800"/>
        <source>%1 hours</source>
        <translation>%1 Stunden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="803"/>
        <source>%1 days</source>
        <translation>%1 Tage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="979"/>
        <source>Waiting for their encryption key. Will request it again soon.</source>
        <translation>Warte auf den Verschlüsselungscode. Wird bald erneut angefordert.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="982"/>
        <source>Encryption key request queued.</source>
        <translation>Verschlüsselungscode-Anforderung steht aus.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="985"/>
        <source>Queued.</source>
        <translation>In Warteschlange.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="988"/>
        <source>Message sent. Waiting for acknowledgement. Sent at %1</source>
        <translation>Nachricht gesendet. Warte auf Bestätigung. Gesendet %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="991"/>
        <source>Message sent. Sent at %1</source>
        <translation>Nachricht gesendet. gesendet am %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="994"/>
        <source>Need to do work to send message. Work is queued.</source>
        <translation>Es muss Arbeit verrichtet werden um die Nachricht zu versenden. Arbeit ist in Warteschlange.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="997"/>
        <source>Acknowledgement of the message received %1</source>
        <translation>Bestätigung der Nachricht erhalten %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2113"/>
        <source>Broadcast queued.</source>
        <translation>Rundruf in Warteschlange.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1003"/>
        <source>Broadcast on %1</source>
        <translation>Rundruf um %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1006"/>
        <source>Problem: The work demanded by the recipient is more difficult than you are willing to do. %1</source>
        <translation>Problem: Die vom Empfänger geforderte Arbeit ist schwerer als Sie bereit sind, zu berechnen. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1009"/>
        <source>Problem: The recipient&apos;s encryption key is no good. Could not encrypt message. %1</source>
        <translation>Problem: Der Verschlüsselungscode des Empfängers ist nicht in Ordnung. Nachricht konnte nicht verschlüsselt werden. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1012"/>
        <source>Forced difficulty override. Send should start soon.</source>
        <translation>Schwierigkeitslimit überschrieben. Senden sollte bald beginnen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1015"/>
        <source>Unknown status: %1 %2</source>
        <translation>Unbekannter Status: %1 %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1678"/>
        <source>Not Connected</source>
        <translation>Nicht verbunden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1138"/>
        <source>Show Bitmessage</source>
        <translation>Bitmessage anzeigen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="683"/>
        <source>Send</source>
        <translation>Senden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1153"/>
        <source>Subscribe</source>
        <translation>Abonnieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1159"/>
        <source>Channel</source>
        <translation>Chan</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="728"/>
        <source>Quit</source>
        <translation>Schließen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1509"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.</source>
        <translation>Sie können Ihre Schlüssel verwalten, indem Sie die keys.dat Datei bearbeiten, die im gleichen Ordner wie das Programm liegt. Es ist wichtig, dass Sie diese Datei sichern.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1513"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file.</source>
        <translation>Sie können Ihre Schlüssel verwalten, indem Sie die keys.dat Datei bearbeiten, die im Ordner
%1 liegt.
Es ist wichtig, dass Sie diese Datei sichern.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1520"/>
        <source>Open keys.dat?</source>
        <translation>Datei keys.dat öffnen?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1517"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Sie können Ihre Schlüssel verwalten, indem Sie die keys.dat Datei bearbeiten, die im gleichen Ordner wie das Programm liegt. Es ist wichtig, dass Sie diese Datei sichern. Möchten Sie die Datei jetzt öffnen? (Stellen Sie sicher, dass Bitmessage geschlossen ist, bevor Sie etwas ändern.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1520"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Sie können Ihre Schlüssel verwalten, indem Sie die keys.dat Datei bearbeiten,
die im Ordner %1 liegt.
Es ist wichtig, dass Sie diese Datei sichern. Möchten Sie die Datei jetzt öffnen?
(Stellen Sie sicher, dass Bitmessage geschlossen ist, bevor Sie etwas ändern.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1527"/>
        <source>Delete trash?</source>
        <translation>Papierkorb leeren?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1527"/>
        <source>Are you sure you want to delete all trashed messages?</source>
        <translation>Sind Sie sicher, dass Sie alle Nachrichten im Papierkorb löschen möchten?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1547"/>
        <source>bad passphrase</source>
        <translation>Falscher Passwort-Satz</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1547"/>
        <source>You must type your passphrase. If you don&apos;t have one then this is not the form for you.</source>
        <translation>Sie müssen Ihren Passwort-Satz eingeben. Wenn Sie keinen haben, ist dies das falsche Formular für Sie.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1560"/>
        <source>Bad address version number</source>
        <translation>Falsche Addressenversionnummer</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1556"/>
        <source>Your address version number must be a number: either 3 or 4.</source>
        <translation>Die Addressenversionnummer muss eine Zahl sein, entweder 3 oder 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1560"/>
        <source>Your address version number must be either 3 or 4.</source>
        <translation>Die Addressenversionnnummer muss entweder 3 oder 4 sein.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1590"/>
        <source>Chan name needed</source>
        <translation>Chan name benötigt</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1590"/>
        <source>You didn&apos;t enter a chan name.</source>
        <translation>Sie haben keinen Chan-Namen eingegeben.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1610"/>
        <source>Address already present</source>
        <translation>Adresse bereits vorhanden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1610"/>
        <source>Could not add chan because it appears to already be one of your identities.</source>
        <translation>Chan konnte nicht erstellt werden, da es sich bereits um eine Ihrer Identitäten handelt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1614"/>
        <source>Success</source>
        <translation>Erfolgreich</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1585"/>
        <source>Successfully created chan. To let others join your chan, give them the chan name and this Bitmessage address: %1. This address also appears in &apos;Your Identities&apos;.</source>
        <translation>Chan erfolgreich erstellt. Um andere diesem Chan beitreten zu lassen, geben Sie ihnen den Chan-Namen und die Bitmessage-Adresse: %1. Diese Adresse befindet sich auch unter &quot;Ihre Identitäten&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1594"/>
        <source>Address too new</source>
        <translation>Adresse zu neu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1594"/>
        <source>Although that Bitmessage address might be valid, its version number is too new for us to handle. Perhaps you need to upgrade Bitmessage.</source>
        <translation>Obwohl diese Bitmessage-Adresse gültig ist, ist ihre Versionsnummer zu hoch um verarbeitet zu werden. Vermutlich müssen Sie eine neuere Version von Bitmessage installieren.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1598"/>
        <source>Address invalid</source>
        <translation>Adresse ungültig</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1598"/>
        <source>That Bitmessage address is not valid.</source>
        <translation>Diese Bitmessage-Adresse ist nicht gültig.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1606"/>
        <source>Address does not match chan name</source>
        <translation>Adresse stimmt nicht mit dem Chan-Namen überein</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1606"/>
        <source>Although the Bitmessage address you entered was valid, it doesn&apos;t match the chan name.</source>
        <translation>Obwohl die Bitmessage-Adresse die Sie eingegeben haben gültig ist, stimmt diese nicht mit dem Chan-Namen überein.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1614"/>
        <source>Successfully joined chan. </source>
        <translation>Chan erfolgreich beigetreten.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1672"/>
        <source>Connection lost</source>
        <translation>Verbindung verloren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1711"/>
        <source>Connected</source>
        <translation>Verbunden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1828"/>
        <source>Message trashed</source>
        <translation>Nachricht in den Papierkorb verschoben</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1909"/>
        <source>The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate.</source>
        <translation>Der Ablauf, oder Time-To-Live, ist die Dauer, für die das Netzwerk die Nachricht speichern wird. Der Empfänger muss es während dieser Zeit empfangen. Wenn Ihr Bitmessage-Client keine Empfangsbestätigung erhält, wird die Nachricht automatisch erneut verschickt. Je länger die Time-To-Live, desto mehr Arbeit muss Ihr Rechner verrichten, um die Nachricht zu senden. Ein Time-To-Live von vier oder fünf Tage ist meist ausreichend.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1945"/>
        <source>Message too long</source>
        <translation>Narchricht zu lang</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1945"/>
        <source>The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.</source>
        <translation>Die Nachricht, die Sie versuchen zu senden ist %1 Byte zu lange. (Maximum 261.644 Bytes). Bitte kürzen Sie sie vor dem Senden ab.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1973"/>
        <source>Error: Your account wasn&apos;t registered at an email gateway. Sending registration now as %1, please wait for the registration to be processed before retrying sending.</source>
        <translation>Fehler: Ihr Konto war an keiner E-Mailschnittstelle registriert. Registrierung als %1 wird versandt, bitte vor einem erneutem Sendeversuch auf die Registrierungsverarbeitung warten.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1982"/>
        <source>Error: Bitmessage addresses start with BM-   Please check %1</source>
        <translation>Fehler: Bitmessage Adressen starten mit BM-   Bitte überprüfen Sie %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1985"/>
        <source>Error: The address %1 is not typed or copied correctly. Please check it.</source>
        <translation>Fehler: Die Adresse %1 wurde nicht korrekt getippt oder kopiert. Bitte überprüfen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1988"/>
        <source>Error: The address %1 contains invalid characters. Please check it.</source>
        <translation>Fehler: Die Adresse %1 beinhaltet ungültig Zeichen. Bitte überprüfen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1991"/>
        <source>Error: The address version in %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</source>
        <translation>Fehler: Die Adressversion von %1 ist zu hoch. Entweder Sie müssen Ihre Bitmessage Software aktualisieren oder Ihr Bekannter ist sehr clever.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1994"/>
        <source>Error: Some data encoded in the address %1 is too short. There might be something wrong with the software of your acquaintance.</source>
        <translation>Fehler: Einige Daten die in der Adresse %1 codiert sind, sind zu kurz. Es könnte sein, dass etwas mit der Software Ihres Bekannten nicht stimmt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1997"/>
        <source>Error: Some data encoded in the address %1 is too long. There might be something wrong with the software of your acquaintance.</source>
        <translation>Fehler: Einige Daten die in der Adresse %1 codiert sind, sind zu lang. Es könnte sein, dass etwas mit der Software Ihres Bekannten nicht stimmt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2000"/>
        <source>Error: Some data encoded in the address %1 is malformed. There might be something wrong with the software of your acquaintance.</source>
        <translation>Fehler: Einige codierte Daten in der Adresse %1 sind ungültig. Es könnte etwas mit der Software Ihres Bekannten sein.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2003"/>
        <source>Error: Something is wrong with the address %1.</source>
        <translation>Fehler: Mit der Adresse %1 stimmt etwas nicht.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2071"/>
        <source>Error: You must specify a From address. If you don&apos;t have one, go to the &apos;Your Identities&apos; tab.</source>
        <translation>Fehler: Sie müssen eine Absenderadresse auswählen. Sollten Sie keine haben, wechseln Sie zum Reiter &quot;Ihre Identitäten&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2012"/>
        <source>Address version number</source>
        <translation>Adressversion</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2012"/>
        <source>Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Bezüglich der Adresse %1, Bitmessage kann Adressen mit der Version %2 nicht verarbeiten. Möglicherweise müssen Sie Bitmessage auf die aktuelle Version aktualisieren.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2016"/>
        <source>Stream number</source>
        <translation>Datenstrom Nummer</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2016"/>
        <source>Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Bezüglich der Adresse %1, Bitmessage kann den Datenstrom  mit der Version %2 nicht verarbeiten. Möglicherweise müssen Sie Bitmessage auf die aktuelle Version aktualisieren.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2021"/>
        <source>Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won&apos;t send until you connect.</source>
        <translation>Warnung: Sie sind aktuell nicht verbunden. Bitmessage wird die nötige Arbeit zum versenden verrichten, aber erst senden, wenn Sie verbunden sind.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2063"/>
        <source>Message queued.</source>
        <translation>Nachricht befindet sich in der Warteschleife.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2067"/>
        <source>Your &apos;To&apos; field is empty.</source>
        <translation>Ihr &quot;Empfänger&quot;-Feld ist leer.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2122"/>
        <source>Right click one or more entries in your address book and select &apos;Send message to this address&apos;.</source>
        <translation>Klicken Sie mit rechts auf eine oder mehrere Einträge aus Ihrem Adressbuch und wählen Sie &quot;Nachricht an diese Adresse senden&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2133"/>
        <source>Fetched address from namecoin identity.</source>
        <translation>Adresse aus Namecoin Identität geholt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2232"/>
        <source>New Message</source>
        <translation>Neue Nachricht</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2232"/>
        <source>From </source>
        <translation>Von </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2611"/>
        <source>Sending email gateway registration request</source>
        <translation>E-Mailschnittstelle-Registrierungsantrag wird versandt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="60"/>
        <source>Address is valid.</source>
        <translation>Adresse ist gültig.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="94"/>
        <source>The address you entered was invalid. Ignoring it.</source>
        <translation>Die von Ihnen eingegebene Adresse ist ungültig, sie wird ignoriert.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2952"/>
        <source>Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.</source>
        <translation>Fehler: Sie können eine Adresse nicht doppelt im Adressbuch speichern. Wenn Sie möchten, benennen Sie den existierenden Eintrag um.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3197"/>
        <source>Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want.</source>
        <translation>Fehler: Dieselbe Addresse kann nicht doppelt in die Abonnements eingetragen werden. Alternativ können Sie die bestehende umbenennen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2371"/>
        <source>Restart</source>
        <translation>Neustart</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2357"/>
        <source>You must restart Bitmessage for the port number change to take effect.</source>
        <translation>Sie müssen Bitmessage neu starten, um den geänderten Port zu verwenden.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2371"/>
        <source>Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any).</source>
        <translation>Bitmessage wird ab sofort den Proxy-Server verwenden, aber eventuell möchten Sie Bitmessage neu starten um bereits bestehende Verbindungen zu schließen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2399"/>
        <source>Number needed</source>
        <translation>Zahl erforderlich</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2399"/>
        <source>Your maximum download and upload rate must be numbers. Ignoring what you typed.</source>
        <translation>Ihre maximale Herungerlade- und Hochladegeschwindigkeit müssen Zahlen sein. Die eingetragenen Werte werden ignoriert.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2472"/>
        <source>Will not resend ever</source>
        <translation>Wird nie wiederversendet</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2472"/>
        <source>Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent.</source>
        <translation>Bitte beachten Sie, dass der eingetratene Dauer kürzer als die, die Bitmessage auf das erste Wiederversenden wartet. Deswegen werden Ihre Nachrichten nie wiederversendet.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2584"/>
        <source>Sending email gateway unregistration request</source>
        <translation>E-Mailschnittestelle-Abmeldeantrag wird versandt</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2588"/>
        <source>Sending email gateway status request</source>
        <translation>E-Mailschnittstelle Statusantrag wird versandt</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2644"/>
        <source>Passphrase mismatch</source>
        <translation>Kennwortsatz nicht identisch</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2644"/>
        <source>The passphrase you entered twice doesn&apos;t match. Try again.</source>
        <translation>Die von Ihnen eingegebenen Kennwortsätze sind nicht identisch. Bitte neu versuchen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2647"/>
        <source>Choose a passphrase</source>
        <translation>Wählen Sie einen Kennwortsatz</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2647"/>
        <source>You really do need a passphrase.</source>
        <translation>Sie benötigen wirklich einen Kennwortsatz.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2689"/>
        <source>All done. Closing user interface...</source>
        <translation type="obsolete">Alles fertig. Benutzer interface wird geschlossen...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2899"/>
        <source>Address is gone</source>
        <translation>Adresse ist verloren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2899"/>
        <source>Bitmessage cannot find your address %1. Perhaps you removed it?</source>
        <translation>Bitmessage kann Ihre Adresse %1 nicht finden. Haben Sie sie gelöscht?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2902"/>
        <source>Address disabled</source>
        <translation>Adresse deaktiviert</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2902"/>
        <source>Error: The address from which you are trying to send is disabled. You&apos;ll have to enable it on the &apos;Your Identities&apos; tab before using it.</source>
        <translation>Fehler: Die Adresse von der Sie versuchen zu senden ist deaktiviert. Sie müssen sie unter dem Reiter &quot;Ihre Identitäten&quot; aktivieren bevor Sie fortfahren.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2949"/>
        <source>Entry added to the Address Book. Edit the label to your liking.</source>
        <translation>Eintrag dem Adressbuch hinzugefügt. Editieren Sie den Eintrag nach Belieben.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2974"/>
        <source>Entry added to the blacklist. Edit the label to your liking.</source>
        <translation>Eintrag in die Blacklist hinzugefügt. Die Beschriftung können Sie ändern.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2977"/>
        <source>Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want.</source>
        <translation>Fehler: Dieselbe Addresse kann nicht doppelt in die Blacklist eingetragen werden. Alternativ können Sie die bestehende umbenennen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3105"/>
        <source>Moved items to trash.</source>
        <translation>Objekt in den Papierkorb verschoben.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3045"/>
        <source>Undeleted item.</source>
        <translation>Nachricht wiederhergestellt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3073"/>
        <source>Save As...</source>
        <translation>Speichern unter...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3082"/>
        <source>Write error.</source>
        <translation>Fehler beim speichern.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3183"/>
        <source>No addresses selected.</source>
        <translation>Keine Adresse ausgewählt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3229"/>
        <source>If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the subscription?</source>
        <translation>Wenn Sie das Abonnement löschen, die bereits erhaltene Nachrichten werden unaufrufbar. Überlegen Sie sich vielleicht das Abonnement statdessen zu deaktivieren. Deaktivierte Abonnements erhalten keine neue Nachrichten, aber Sie können die bereits erhaltene aufrufen.

Sind Sie sicher, dass Sie das Abonnement löschen möchten?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3458"/>
        <source>If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the channel?</source>
        <translation>Wenn Sie das Chan löschen, die bereits erhaltene Nachrichten werden unaufrufbar. Überlegen Sie sich vielleicht das Chan statdessen zu deaktivieren. Deaktivierte Chans erhalten keine neue Nachrichten, aber Sie können die bereits erhaltene aufrufen.

Sind Sie sicher, dass Sie das Chan löschen möchten?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3572"/>
        <source>Do you really want to remove this avatar?</source>
        <translation>Wollen Sie diesen Avatar wirklich entfernen?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3580"/>
        <source>You have already set an avatar for this address. Do you really want to overwrite it?</source>
        <translation>Sie haben bereits einen Avatar für diese Adresse gewählt. Wollen Sie ihn wirklich überschreiben?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3952"/>
        <source>Start-on-login not yet supported on your OS.</source>
        <translation>Mit Betriebssystem starten, noch nicht von Ihrem Betriebssystem unterstützt</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3945"/>
        <source>Minimize-to-tray not yet supported on your OS.</source>
        <translation>Ins System Tray minimieren von Ihrem Betriebssytem noch nicht unterstützt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3948"/>
        <source>Tray notifications not yet supported on your OS.</source>
        <translation>Trach-Benachrichtigungen von Ihrem Betriebssystem noch nicht unterstützt.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4117"/>
        <source>Testing...</source>
        <translation>teste...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4157"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation>Dies ist eine Chan-Adresse. Sie können sie nicht als Pseudo-Mailingliste verwenden.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4217"/>
        <source>The address should start with &apos;&apos;BM-&apos;&apos;</source>
        <translation>Die Adresse sollte mit &quot;BM-&quot; beginnen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4220"/>
        <source>The address is not typed or copied correctly (the checksum failed).</source>
        <translation>Die Adresse wurde nicht korrekt getippt oder kopiert (Prüfsumme falsch).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4223"/>
        <source>The version number of this address is higher than this software can support. Please upgrade Bitmessage.</source>
        <translation>Die Versionsnummer dieser Adresse ist höher als diese Software unterstützt. Bitte installieren Sie die neuste Bitmessage Version.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4226"/>
        <source>The address contains invalid characters.</source>
        <translation>Diese Adresse beinhaltet ungültige Zeichen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4229"/>
        <source>Some data encoded in the address is too short.</source>
        <translation>Die in der Adresse codierten Daten sind zu kurz.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4232"/>
        <source>Some data encoded in the address is too long.</source>
        <translation>Die in der Adresse codierten Daten sind zu lang.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4235"/>
        <source>Some data encoded in the address is malformed.</source>
        <translation>Einige in der Adresse kodierten Daten sind ungültig.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4209"/>
        <source>Enter an address above.</source>
        <translation>Eine Addresse oben ausfüllen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4241"/>
        <source>Address is an old type. We cannot display its past broadcasts.</source>
        <translation>Alter Addressentyp. Wir können deren vorige Rundrufe nicht anzeigen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4250"/>
        <source>There are no recent broadcasts from this address to display.</source>
        <translation>Es gibt keine neuen Rundrufe von dieser Adresse die angezeigt werden können.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4294"/>
        <source>You are using TCP port %1. (This can be changed in the settings).</source>
        <translation>Sie benutzen TCP-Port %1 (Dieser kann in den Einstellungen verändert werden).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="645"/>
        <source>Bitmessage</source>
        <translation>Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="646"/>
        <source>Identities</source>
        <translation>Identitäten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="647"/>
        <source>New Identity</source>
        <translation>Neue Identität</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="704"/>
        <source>Search</source>
        <translation>Suchen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="705"/>
        <source>All</source>
        <translation>Alle</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="712"/>
        <source>To</source>
        <translation>An</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="714"/>
        <source>From</source>
        <translation>Von</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="716"/>
        <source>Subject</source>
        <translation>Betreff</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="709"/>
        <source>Message</source>
        <translation>Nachricht</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="718"/>
        <source>Received</source>
        <translation>Erhalten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="663"/>
        <source>Messages</source>
        <translation>Nachrichten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="666"/>
        <source>Address book</source>
        <translation>Addressbuch</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="668"/>
        <source>Address</source>
        <translation>Adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="669"/>
        <source>Add Contact</source>
        <translation>Kontakt hinzufügen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="670"/>
        <source>Fetch Namecoin ID</source>
        <translation>Hole Namecoin ID</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="677"/>
        <source>Subject:</source>
        <translation>Betreff:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="676"/>
        <source>From:</source>
        <translation>Von:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="673"/>
        <source>To:</source>
        <translation>An:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="675"/>
        <source>Send ordinary Message</source>
        <translation>Ordentliche Nachricht senden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="679"/>
        <source>Send Message to your Subscribers</source>
        <translation>Rundruf an Ihre Abonnenten senden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="680"/>
        <source>TTL:</source>
        <translation>Ablauf:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="681"/>
        <source>X days</source>
        <translation>X Tage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="701"/>
        <source>Subscriptions</source>
        <translation>Abonnements</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="685"/>
        <source>Add new Subscription</source>
        <translation>Neues Abonnement anlegen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="719"/>
        <source>Chans</source>
        <translation>Chans</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="703"/>
        <source>Add Chan</source>
        <translation>Chan hinzufügen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="720"/>
        <source>Network Status</source>
        <translation>Netzwerkstatus</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="723"/>
        <source>File</source>
        <translation>Datei</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="734"/>
        <source>Settings</source>
        <translation>Einstellungen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="730"/>
        <source>Help</source>
        <translation>Hilfe</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="726"/>
        <source>Import keys</source>
        <translation>Schlüssel importieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="727"/>
        <source>Manage keys</source>
        <translation>Schlüssel verwalten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="729"/>
        <source>Ctrl+Q</source>
        <translation>Strg+Q</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="731"/>
        <source>F1</source>
        <translation>F1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="732"/>
        <source>Contact support</source>
        <translation>Unterstütung anfordern</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="733"/>
        <source>About</source>
        <translation>Über</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="735"/>
        <source>Regenerate deterministic addresses</source>
        <translation>Deterministische Adressen neu generieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="736"/>
        <source>Delete all trashed messages</source>
        <translation>Alle Nachrichten im Papierkorb löschen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="737"/>
        <source>Join / Create chan</source>
        <translation>Chan beitreten / erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="171"/>
        <source>All accounts</source>
        <translation>Alle Identitäten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="44"/>
        <source>Zoom level %1%</source>
        <translation>Zoom-Stufe %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="91"/>
        <source>Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.</source>
        <translation>Fehler: Sie können eine Adresse nicht doppelt zur Liste hinzufügen. Wenn Sie möchten, benennen Sie den existierenden Eintrag um.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="112"/>
        <source>Add new entry</source>
        <translation>Neuen Eintrag erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4254"/>
        <source>Display the %1 recent broadcast(s) from this address.</source>
        <translation>Die letzten %1 Rundruf(e) von dieser Addresse anzeigen.</translation>
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
        <translation>Neue Adresse erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="174"/>
        <source>Here you may generate as many addresses as you like. Indeed, creating and abandoning addresses is encouraged. You may generate addresses by using either random numbers or by using a passphrase. If you use a passphrase, the address is called a &quot;deterministic&quot; address.
The &apos;Random Number&apos; option is selected by default but deterministic addresses have several pros and cons:</source>
        <translation>Sie können so viele Adressen generieren wie Sie möchten. Es ist sogar empfohlen neue Adressen zu verwenden und alte fallen zu lassen. Sie können Adressen durch Zufallszahlen erstellen lassen, oder unter Verwendung eines Kennwortsatzes. Wenn Sie einen Kennwortsatz verwenden, nennt man dies eine &quot;deterministische&quot; Adresse.
Die Zufallszahlen-Option ist standard, jedoch haben deterministische Adressen einige Vor- und Nachteile:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="176"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Pros:&lt;br/&gt;&lt;/span&gt;You can recreate your addresses on any computer from memory. &lt;br/&gt;You need-not worry about backing up your keys.dat file as long as you can remember your passphrase. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Cons:&lt;br/&gt;&lt;/span&gt;You must remember (or write down) your passphrase if you expect to be able to recreate your keys if they are lost. &lt;br/&gt;You must remember the address version number and the stream number along with your passphrase. &lt;br/&gt;If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Vorteile:&lt;br/&gt;&lt;/span&gt;Sie können ihre Adresse an jedem Computer aus dem Gedächtnis regenerieren. &lt;br/&gt;Sie brauchen sich keine Sorgen um das Sichern ihrer Schlüssel machen solange Sie sich den Kennwortsatz merken. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Nachteile:&lt;br/&gt;&lt;/span&gt;Sie müssen sich den Kennwortsatz merken (oder aufschreiben) wenn Sie in der Lage sein wollen ihre Schlüssel wiederherzustellen. &lt;br/&gt;Sie müssen sich die Adressversion und die Datenstrom Nummer zusammen mit dem Kennwortsatz merken. &lt;br/&gt;Wenn Sie einen schwachen Kennwortsatz wählen und jemand kann ihn erraten oder durch ausprobieren herausbekommen, kann dieser Ihre Nachrichten lesen, oder in ihrem Namen Nachrichten senden..&lt;/p&gt;&lt;/body&gt;&lt;/html&gt; </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="177"/>
        <source>Use a random number generator to make an address</source>
        <translation>Lassen Sie eine Adresse mittels Zufallsgenerator erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="178"/>
        <source>Use a passphrase to make addresses</source>
        <translation>Benutzen Sie einen Kennwortsatz um eine Adresse erstellen zu lassen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="179"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Verwenden Sie einige Minuten extra Rechenleistung um die Adresse(n) ein bis zwei Zeichen kürzer zu machen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="180"/>
        <source>Make deterministic addresses</source>
        <translation>Deterministische Adresse erzeugen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="181"/>
        <source>Address version number: 4</source>
        <translation>Adress-Versionsnummer: 4</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="182"/>
        <source>In addition to your passphrase, you must remember these numbers:</source>
        <translation>Zusätzlich zu Ihrem Kennwortsatz müssen Sie sich diese Zahlen merken:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="183"/>
        <source>Passphrase</source>
        <translation>Kennwortsatz</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="184"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Anzahl Adressen die basierend auf diesem Kennwortsatz erzeugt werden sollen:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="185"/>
        <source>Stream number: 1</source>
        <translation>Datenstrom Nummer: 1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="186"/>
        <source>Retype passphrase</source>
        <translation>Kennwortsatz erneut eingeben</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="187"/>
        <source>Randomly generate address</source>
        <translation>Zufällig generierte Adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="188"/>
        <source>Label (not shown to anyone except you)</source>
        <translation>Bezeichnung (Wird niemandem außer Ihnen gezeigt)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="189"/>
        <source>Use the most available stream</source>
        <translation>Verwendung des am besten verfügbaren Datenstroms</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="190"/>
        <source> (best if this is the first of many addresses you will create)</source>
        <translation>(Zum Generieren der ersten Adresse empfohlen)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="191"/>
        <source>Use the same stream as an existing address</source>
        <translation>Verwendung des gleichen Datenstroms wie eine bestehende Adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="192"/>
        <source>(saves you some bandwidth and processing power)</source>
        <translation>(Dies erspart Ihnen etwas an Bandbreite und Rechenleistung)</translation>
    </message>
</context>
<context>
    <name>NewSubscriptionDialog</name>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="65"/>
        <source>Add new entry</source>
        <translation>Neuen Eintrag erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="66"/>
        <source>Label</source>
        <translation>Name oder Bezeichnung</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="67"/>
        <source>Address</source>
        <translation>Adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="68"/>
        <source>Enter an address above.</source>
        <translation>Bitte geben Sie oben eine Adresse ein.</translation>
    </message>
</context>
<context>
    <name>SpecialAddressBehaviorDialog</name>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="59"/>
        <source>Special Address Behavior</source>
        <translation>Spezielles Adressverhalten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="60"/>
        <source>Behave as a normal address</source>
        <translation>Wie eine normale Adresse verhalten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="61"/>
        <source>Behave as a pseudo-mailing-list address</source>
        <translation>Wie eine Pseudo-Mailinglistenadresse verhalten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="62"/>
        <source>Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).</source>
        <translation>Nachrichten an eine Pseudo-Mailinglistenadresse werden automatisch an alle Abonnenten weitergeleitet (Der Inhalt ist dann öffentlich).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="63"/>
        <source>Name of the pseudo-mailing-list:</source>
        <translation>Name der Pseudo-Mailingliste:</translation>
    </message>
</context>
<context>
    <name>aboutDialog</name>
    <message>
        <location filename="../bitmessageqt/about.py" line="66"/>
        <source>About</source>
        <translation>Über</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="67"/>
        <source>PyBitmessage</source>
        <translation>PyBitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="68"/>
        <source>version ?</source>
        <translation>Version ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="69"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright &#xc2;&#xa9; 2012-2014 Jonathan Warren&lt;br/&gt;Copyright &#xc2;&#xa9; 2013-2014 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distributed under the MIT/X11 software license; see &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Veröffentlicht unter der MIT/X11 Software-Lizenz; see &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="71"/>
        <source>This is Beta software.</source>
        <translation>Dies ist Beta-Software.</translation>
    </message>
</context>
<context>
    <name>blacklist</name>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="17"/>
        <source>Use a Blacklist (Allow all incoming messages except those on the Blacklist)</source>
        <translation>Liste als Blacklist verwenden (Erlaubt alle eingehenden Nachrichten, außer von Adressen auf der Blacklist)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="27"/>
        <source>Use a Whitelist (Block all incoming messages except those on the Whitelist)</source>
        <translation>Liste als Whitelist verwenden (Erlaubt keine eingehenden Nachrichten, außer von Adressen auf der Whitelist)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="34"/>
        <source>Add new entry</source>
        <translation>Neuen Eintrag erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="85"/>
        <source>Name or Label</source>
        <translation>Name oder Bezeichnung</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="90"/>
        <source>Address</source>
        <translation>Adresse</translation>
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
        <translation>Internetverbindung</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="57"/>
        <source>Bitmessage won&apos;t connect to anyone until you let it. </source>
        <translation>Bitmessage wird sich nicht verbinden, wenn Sie es nicht möchten.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="58"/>
        <source>Connect now</source>
        <translation>Jetzt verbinden</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="59"/>
        <source>Let me configure special network settings first</source>
        <translation>Zunächst spezielle Nertzwerkeinstellungen vornehmen</translation>
    </message>
</context>
<context>
    <name>helpDialog</name>
    <message>
        <location filename="../bitmessageqt/help.py" line="45"/>
        <source>Help</source>
        <translation>Hilfe</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.py" line="46"/>
        <source>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.py" line="47"/>
        <source>As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:</source>
        <translation>Bitmessage ist ein kollaboratives Projekt. Hilfe finden Sie online im Bitmessage-Wiki:</translation>
    </message>
</context>
<context>
    <name>iconGlossaryDialog</name>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="82"/>
        <source>Icon Glossary</source>
        <translation>Icon Glossar</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="83"/>
        <source>You have no connections with other peers. </source>
        <translation>Sie haben keine Verbindung mit anderen Netzwerkteilnehmern.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="84"/>
        <source>You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn&apos;t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.</source>
        <translation>Sie haben mindestes eine Verbindung mit einem Netzwerkteilnehmer über eine ausgehende Verbindung, aber Sie haben noch keine eingehende Verbindung. Ihre Firewall oder Ihr Router ist vermutlich nicht richtig konfiguriert, um eingehende TCP-Verbindungen an Ihren Computer weiterzuleiten. Bitmessage wird gut funktionieren, jedoch helfen Sie dem Netzwerk, wenn Sie eingehende Verbindungen erlauben. Es hilft auch Ihnen schneller und mehr Verbindungen ins Netzwerk aufzubauen.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="85"/>
        <source>You are using TCP port ?. (This can be changed in the settings).</source>
        <translation>Sie benutzen TCP-Port ?. (Dies kann in den Einstellungen verändert werden).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="86"/>
        <source>You do have connections with other peers and your firewall is correctly configured.</source>
        <translation>Sie haben Verbindungen mit anderen Netzwerkteilnehmern und Ihre Firewall ist richtig konfiguriert.</translation>
    </message>
</context>
<context>
    <name>networkstatus</name>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="39"/>
        <source>Total connections:</source>
        <translation>Verbindungen insgesamt:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="143"/>
        <source>Since startup:</source>
        <translation>Seit Start:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="159"/>
        <source>Processed 0 person-to-person messages.</source>
        <translation>0 Person-zu-Person-Nachrichten verarbeitet.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="188"/>
        <source>Processed 0 public keys.</source>
        <translation>0 öffentliche Schlüssel verarbeitet.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="175"/>
        <source>Processed 0 broadcasts.</source>
        <translation>0 Rundrufe verarbeitet.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="240"/>
        <source>Inventory lookups per second: 0</source>
        <translation>Inventory lookups pro Sekunde: 0</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="101"/>
        <source>Down: 0 KB/s</source>
        <translation type="obsolete">Herunter: 0 KB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="114"/>
        <source>Up: 0 KB/s</source>
        <translation type="obsolete">Hoch: 0 KB/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="201"/>
        <source>Objects to be synced:</source>
        <translation>Zu synchronisierende Objektanzahl:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="111"/>
        <source>Stream #</source>
        <translation>Datenstrom #</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="116"/>
        <source>Connections</source>
        <translation>Verbindungen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="133"/>
        <source>Since startup on %1</source>
        <translation>Seit Start der Anwendung am %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="59"/>
        <source>Objects to be synced: %1</source>
        <translation>Zu synchronisierende Objektanzahl: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="50"/>
        <source>Processed %1 person-to-person messages.</source>
        <translation>%1 Person-zu-Person-Nachrichten bearbeitet.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="55"/>
        <source>Processed %1 broadcast messages.</source>
        <translation>%1 Rundruf-Nachrichten bearbeitet.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="60"/>
        <source>Processed %1 public keys.</source>
        <translation>%1 öffentliche Schlüssel bearbeitet.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="68"/>
        <source>Down: %1/s  Total: %2</source>
        <translation>Herunter: %1/s  Insg.: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="70"/>
        <source>Up: %1/s  Total: %2</source>
        <translation>Hoch: %1/s Insg.: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="117"/>
        <source>Total Connections: %1</source>
        <translation>Verbindungen insgesamt: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="126"/>
        <source>Inventory lookups per second: %1</source>
        <translation>Inventory lookups pro Sekunde: %1</translation>
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
        <translation>Chan beitreten / erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="98"/>
        <source>Create a new chan</source>
        <translation>Neuen Chan erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="103"/>
        <source>Join a chan</source>
        <translation>Einem Chan beitreten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="100"/>
        <source>Create a chan</source>
        <translation>Chan erstellen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="101"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly then the chan will be secure and private. If you and someone else both create a chan with the same chan name then it is currently very likely that they will be the same chan.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Geben Sie einen Namen für Ihren Chan ein. Wenn Sie einen ausreichend komplexen Chan-Namen wählen (wie einen starken, einzigartigen Kennwortsatz) und keiner Ihrer Freunde ihn öffentlich weitergibt, wird der Chan sicher und privat bleiben. Wenn eine andere Person einen Chan mit dem gleichen Namen erzeugt, werden diese zu einem Chan.&lt;/p&gt;&lt;br&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="105"/>
        <source>Chan name:</source>
        <translation>Chan-Name:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="104"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a normal person-to-person message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Ein Chan existiert, wenn eine Gruppe von Leuten sich den gleichen Entschlüsselungscode teilen. Die Schlüssel und Bitmessage-Adressen werden basierend auf einem lesbaren Wort oder Satz generiert (dem Chan-Namen). Um eine Nachricht an den Chan zu senden, senden Sie eine normale Person-zu-Person-Nachricht an die Chan-Adresse.&lt;/p&gt;&lt;p&gt;Chans sind experimentell und völlig unmoderierbar.&lt;/p&gt;&lt;br&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="106"/>
        <source>Chan bitmessage address:</source>
        <translation>Chan-Bitmessage-Adresse:</translation>
    </message>
</context>
<context>
    <name>regenerateAddressesDialog</name>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="114"/>
        <source>Regenerate Existing Addresses</source>
        <translation>Bestehende Adresse regenerieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="115"/>
        <source>Regenerate existing addresses</source>
        <translation>Bestehende Adresse regenerieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="116"/>
        <source>Passphrase</source>
        <translation>Kennwortsatz</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="117"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Anzahl der Adressen, die basierend auf diesem Kennwortsatz erzeugt werden sollen:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="118"/>
        <source>Address version number:</source>
        <translation>Adress-Versionsnummer:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="119"/>
        <source>Stream number:</source>
        <translation>Stream-Nummer:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="120"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="121"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Verwenden Sie einige Minuten extra Rechenleistung, um die Adresse(n) ein bis zwei Zeichen kürzer zu machen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="122"/>
        <source>You must check (or not check) this box just like you did (or didn&apos;t) when you made your addresses the first time.</source>
        <translation>Sie müssen diese Option auswählen (oder nicht auswählen) wie Sie es gemacht haben, als Sie Ihre Adresse das erste mal erstellt haben.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="123"/>
        <source>If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.</source>
        <translation>Wenn Sie bereits deterministische Adressen erstellt haben, aber diese durch einen Unfall (zum Beispiel durch eine defekte Festplatte) verloren haben, können Sie sie hier regenerieren. Dies funktioniert nur dann, wenn Sie bei der erstmaligen Erstellung Ihrer Adressen nicht den Zufallsgenerator verwendet haben.</translation>
    </message>
</context>
<context>
    <name>settingsDialog</name>
    <message>
        <location filename="../bitmessageqt/settings.py" line="430"/>
        <source>Settings</source>
        <translation>Einstellungen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="431"/>
        <source>Start Bitmessage on user login</source>
        <translation>Bitmessage nach dem Hochfahren automatisch starten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="432"/>
        <source>Tray</source>
        <translation>Infobereich (Taskleiste)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="433"/>
        <source>Start Bitmessage in the tray (don&apos;t show main window)</source>
        <translation>Bitmessage minimiert starten (zeigt das Hauptfenster nicht an)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="434"/>
        <source>Minimize to tray</source>
        <translation>In den Systemtray minimieren</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="435"/>
        <source>Close to tray</source>
        <translation>Schliessen ins Infobereich</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="436"/>
        <source>Show notification when message received</source>
        <translation>Benachrichtigung anzeigen, wenn eine Nachricht eintrifft</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="437"/>
        <source>Run in Portable Mode</source>
        <translation>Im portablen Modus arbeiten</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="438"/>
        <source>In Portable Mode, messages and config files are stored in the same directory as the program rather than the normal application-data folder. This makes it convenient to run Bitmessage from a USB thumb drive.</source>
        <translation>Im portablen Modus werden Nachrichten und Konfigurationen im gleichen Ordner abgelegt, in dem sich das Programm selbst befindet (anstatt im normalen Anwendungsdaten-Ordner). Das macht es möglich, Bitmessage auf einem USB-Stick zu betreiben.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="439"/>
        <source>Willingly include unencrypted destination address when sending to a mobile device</source>
        <translation>Willentlich die unverschlüsselte Adresse des Empfängers übertragen, wenn an ein mobiles Gerät gesendet wird</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="440"/>
        <source>Use Identicons</source>
        <translation>Benutze Identicons (Automatisch generierte Icons zu einer Bitcoinadresse)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="441"/>
        <source>Reply below Quote</source>
        <translation>Antworte unter zitierter Nachricht</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="442"/>
        <source>Interface Language</source>
        <translation>Sprachauswahl</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="443"/>
        <source>System Settings</source>
        <comment>system</comment>
        <translation>Vom System übernehmen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="470"/>
        <source>Pirate English</source>
        <comment>en_pirate</comment>
        <translation type="obsolete">Piraten-Englisch</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="471"/>
        <source>Other (set in keys.dat)</source>
        <comment>other</comment>
        <translation type="obsolete">Andere (in keys.dat einstellen)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="444"/>
        <source>User Interface</source>
        <translation>Benutzerinterface</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="445"/>
        <source>Listening port</source>
        <translation>TCP-Port</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="446"/>
        <source>Listen for connections on port:</source>
        <translation>Wartet auf Verbindungen auf Port:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="447"/>
        <source>UPnP:</source>
        <translation>UPnP:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="448"/>
        <source>Bandwidth limit</source>
        <translation>Bandbreite begrenzen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="449"/>
        <source>Maximum download rate (kB/s): [0: unlimited]</source>
        <translation>Maximale Downloadrate in kB/s, 0 bedeutet kein Limit</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="450"/>
        <source>Maximum upload rate (kB/s): [0: unlimited]</source>
        <translation>Maximale Uploadrate in kB/s, 0 bedeutet kein Limit</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="451"/>
        <source>Proxy server / Tor</source>
        <translation>Proxy-Server / Tor</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="452"/>
        <source>Type:</source>
        <translation>Typ:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="453"/>
        <source>Server hostname:</source>
        <translation>Servername:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="476"/>
        <source>Port:</source>
        <translation>Port:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="455"/>
        <source>Authentication</source>
        <translation>Authentifizierung</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="477"/>
        <source>Username:</source>
        <translation>Benutzername:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="457"/>
        <source>Pass:</source>
        <translation>Kennwort:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="458"/>
        <source>Listen for incoming connections when using proxy</source>
        <translation>Auf eingehende Verbindungen warten, auch wenn ein Proxy-Server verwendet wird</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="459"/>
        <source>none</source>
        <translation>keiner</translation>
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
        <translation>Netzwerkeinstellungen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="463"/>
        <source>Total difficulty:</source>
        <translation>Gesamtschwierigkeit:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="464"/>
        <source>The &apos;Total difficulty&apos; affects the absolute amount of work the sender must complete. Doubling this value doubles the amount of work.</source>
        <translation>Die &quot;Gesamtschwierigkeit&quot; beeinflusst die absolute Menge Arbeit, die ein Sender verrichten muss. Verdoppelung dieses Wertes verdoppelt die Menge der Arbeit.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="465"/>
        <source>Small message difficulty:</source>
        <translation>Schwierigkeit für kurze Nachrichten:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="466"/>
        <source>When someone sends you a message, their computer must first complete some work. The difficulty of this work, by default, is 1. You may raise this default for new addresses you create by changing the values here. Any new addresses you create will require senders to meet the higher difficulty. There is one exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically notify them when you next send a message that they need only complete the minimum amount of work: difficulty 1. </source>
        <translation>Wenn jemand Ihnen eine Nachricht schickt, muss der absendende Computer erst einige Arbeit verrichten. Die Schwierigkeit dieser Arbeit ist standardmäßig 1. Sie können diesen Wert für alle neuen Adressen, die Sie generieren, hier ändern. Es gibt eine Ausnahme: Wenn Sie einen Freund oder Bekannten in Ihr Adressbuch übernehmen, wird Bitmessage ihn mit der nächsten Nachricht automatisch informieren, dass er nur noch die minimale Arbeit verrichten muss: Schwierigkeit 1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="467"/>
        <source>The &apos;Small message difficulty&apos; mostly only affects the difficulty of sending small messages. Doubling this value makes it almost twice as difficult to send a small message but doesn&apos;t really affect large messages.</source>
        <translation>Die &quot;Schwierigkeit für kurze Nachrichten&quot; trifft nur auf das Senden kurzer Nachrichten zu. Verdoppelung dieses Wertes macht es fast doppelt so schwer, kurze Nachrichten zu senden, aber hat keinen Effekt bei langen Nachrichten.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="468"/>
        <source>Demanded difficulty</source>
        <translation>Geforderte Schwierigkeit</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="469"/>
        <source>Here you may set the maximum amount of work you are willing to do to send a message to another person. Setting these values to 0 means that any value is acceptable.</source>
        <translation>Hier setzen Sie die maximale Arbeit, die Sie bereit sind zu verrichten, um eine Nachricht an eine andere Person zu versenden. Ein Wert von 0 bedeutet, dass Sie jede Arbeit akzeptieren.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="470"/>
        <source>Maximum acceptable total difficulty:</source>
        <translation>Maximale akzeptierte Gesamtschwierigkeit:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="471"/>
        <source>Maximum acceptable small message difficulty:</source>
        <translation>Maximale akzeptierte Schwierigkeit für kurze Nachrichten:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="472"/>
        <source>Max acceptable difficulty</source>
        <translation>Maximale akzeptierte Schwierigkeit</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Hardware GPU acceleration (OpenCL)</source>
        <translation>Hardwaregrafikkartenbeschleunigung (OpenCL)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="474"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage can utilize a different Bitcoin-based program called Namecoin to make addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage address, you can simply tell him to send a message to &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Getting your own Bitmessage address into Namecoin is still rather difficult).&lt;/p&gt;&lt;p&gt;Bitmessage can use either namecoind directly or a running nmcontrol instance.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage kann ein anderes Bitcoin basiertes Programm namens Namecoin nutzen, um Adressen leserlicher zu machen. Zum Beispiel: Anstelle Ihrem Bekannten Ihre lange Bitmessage-Adresse vorzulesen, können Sie ihm einfach sagen, er soll eine Nachricht an &lt;span style=&quot; font-style:italic;&quot;&gt;test &lt;/span&gt;senden.&lt;/p&gt;&lt;p&gt; (Ihre Bitmessage-Adresse in Namecoin zu speichern ist noch sehr umständlich)&lt;/p&gt;&lt;p&gt;Bitmessage kann direkt namecoind verwenden, oder eine nmcontrol Instanz.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="475"/>
        <source>Host:</source>
        <translation>Server:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="478"/>
        <source>Password:</source>
        <translation>Kennwort:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="479"/>
        <source>Test</source>
        <translation>Verbindung testen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="480"/>
        <source>Connect to:</source>
        <translation>Verbinde mit:</translation>
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
        <translation>Namecoin Integration</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="484"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;By default, if you send a message to someone and he is offline for more than two days, Bitmessage will send the message again after an additional two days. This will be continued with exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain number of days or months.&lt;/p&gt;&lt;p&gt;Leave these input fields blank for the default behavior. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Wenn der Empfänger eine Nachricht nicht bis zum Ablauf herunterlädt, zum Beisplel weil er für längere Zeit nicht mit dem Netz verbunden ist, wird die Nachricht erneut versendet. Dies passiert solange, bis eine Empfangsbestätigung erhalten wird. Hier können Sie dieses Verhalten ändern, indem Sie Bitmessage die Viederersandversuche nach einer bestimmten Anzahl von Tagen oder Monaten aufgeben lassen.&lt;/p&gt;&lt;p&gt;Für die Standardeinstellung (ohne zeitliche Einschränkung) lassen Sie diese Eingabefelder leer.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="485"/>
        <source>Give up after</source>
        <translation>Gib auf nach</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="486"/>
        <source>and</source>
        <translation>und</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="487"/>
        <source>days</source>
        <translation>Tagen</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="488"/>
        <source>months.</source>
        <translation>Monaten.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="489"/>
        <source>Resends Expire</source>
        <translation>Neusendungsablauf</translation>
    </message>
</context>
</TS>
