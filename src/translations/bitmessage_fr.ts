<?xml version="1.0" ?><!DOCTYPE TS><TS language="fr" sourcelanguage="en" version="2.0">
<context>
    <name>AddAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.ui" line="20"/>
        <source>Add new entry</source>
        <translation>Ajouter une nouvelle entrée</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.ui" line="29"/>
        <source>Label</source>
        <translation>Étiquette</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.ui" line="39"/>
        <source>Address</source>
        <translation>Adresse</translation>
    </message>
</context>
<context>
    <name>EmailGatewayDialog</name>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="14"/>
        <source>Email gateway</source>
        <translation>Passerelle de courriel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="30"/>
        <source>Register on email gateway</source>
        <translation>S’inscrire sur la passerelle de courriel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="82"/>
        <source>Account status at email gateway</source>
        <translation>Statut du compte sur la passerelle de courriel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="95"/>
        <source>Change account settings at email gateway</source>
        <translation>Changer les paramètres de compte sur la passerelle de courriel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="108"/>
        <source>Unregister from email gateway</source>
        <translation>Se désabonner de la passerelle de courriel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="69"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.</source>
        <translation>La passerelle de courriel vous permet de communiquer avec des utilisateurs de courriel. Actuellement, seulement la passerelle de courriel de Mailchuck (@mailchuck.com) est disponible.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="23"/>
        <source>Desired email address (including @mailchuck.com):</source>
        <translation>Adresse de courriel désirée (incluant @mailchuck.com) :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.ui" line="59"/>
        <source>@mailchuck.com</source>
        <translation>@mailchuck.com</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="286"/>
        <source>Registration failed:</source>
        <translation>L’inscription a échoué :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="288"/>
        <source>The requested email address is not available, please try a new one.</source>
        <translation>L&apos;adresse électronique demandée n&apos;est pas disponible, veuillez essayer une nouvelle.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="334"/>
        <source>Sending email gateway registration request</source>
        <translation>Envoi de la demande d’inscription de la passerelle de courriel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="342"/>
        <source>Sending email gateway unregistration request</source>
        <translation>Envoi de la demande de désinscription de la passerelle de courriel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="348"/>
        <source>Sending email gateway status request</source>
        <translation>Envoi à la passerelle de courriel d’une demande de statut</translation>
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
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/account.py" line="299"/>
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
        <translation type="unfinished"/>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="166"/>
        <source>Reply to sender</source>
        <translation>Répondre à l’expéditeur</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="168"/>
        <source>Reply to channel</source>
        <translation>Répondre au canal</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="170"/>
        <source>Add sender to your Address Book</source>
        <translation>Ajouter l’expéditeur au carnet d’adresses</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="174"/>
        <source>Add sender to your Blacklist</source>
        <translation>Ajouter l’expéditeur à votre liste noire</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="374"/>
        <source>Move to Trash</source>
        <translation>Envoyer à la Corbeille</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="181"/>
        <source>Undelete</source>
        <translation>Restaurer</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="184"/>
        <source>View HTML code as formatted text</source>
        <translation>Voir le code HTML comme du texte formaté</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="188"/>
        <source>Save message as...</source>
        <translation>Enregistrer le message sous…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="192"/>
        <source>Mark Unread</source>
        <translation>Marquer comme non-lu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="346"/>
        <source>New</source>
        <translation>Nouvelle</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="122"/>
        <source>Enable</source>
        <translation>Activer</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="125"/>
        <source>Disable</source>
        <translation>Désactiver</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="128"/>
        <source>Set avatar...</source>
        <translation>Configurer l’avatar</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="118"/>
        <source>Copy address to clipboard</source>
        <translation>Copier l’adresse dans le presse-papier</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="293"/>
        <source>Special address behavior...</source>
        <translation>Comportement spécial de l’adresse…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="240"/>
        <source>Email gateway</source>
        <translation>Passerelle de courriel</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="115"/>
        <source>Delete</source>
        <translation>Effacer</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="309"/>
        <source>Send message to this address</source>
        <translation>Envoyer un message à cette adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="317"/>
        <source>Subscribe to this address</source>
        <translation>S’abonner à cette adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="329"/>
        <source>Add New Address</source>
        <translation>Ajouter une nouvelle adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="377"/>
        <source>Copy destination address to clipboard</source>
        <translation>Copier l’adresse de destination dans le presse-papier</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="381"/>
        <source>Force send</source>
        <translation>Forcer l’envoi</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="597"/>
        <source>One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?</source>
        <translation>Une de vos adresses, %1, est une vieille adresse de la version 1. Les adresses de la version 1 ne sont plus supportées. Nous pourrions la supprimer maintenant?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1042"/>
        <source>Waiting for their encryption key. Will request it again soon.</source>
        <translation>En attente de la clé de chiffrement. Une nouvelle requête sera bientôt lancée.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="990"/>
        <source>Encryption key request queued.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1048"/>
        <source>Queued.</source>
        <translation>En attente.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1051"/>
        <source>Message sent. Waiting for acknowledgement. Sent at %1</source>
        <translation>Message envoyé. En attente de l’accusé de réception. Envoyé %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1054"/>
        <source>Message sent. Sent at %1</source>
        <translation>Message envoyé. Envoyé %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1002"/>
        <source>Need to do work to send message. Work is queued.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1060"/>
        <source>Acknowledgement of the message received %1</source>
        <translation>Accusé de réception reçu %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2152"/>
        <source>Broadcast queued.</source>
        <translation>Message de diffusion en attente.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1069"/>
        <source>Broadcast on %1</source>
        <translation>Message de diffusion du %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1072"/>
        <source>Problem: The work demanded by the recipient is more difficult than you are willing to do. %1</source>
        <translation>Problème : Le travail demandé par le destinataire est plus difficile que ce que vous avez paramétré. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1075"/>
        <source>Problem: The recipient&apos;s encryption key is no good. Could not encrypt message. %1</source>
        <translation>Problème : la clé de chiffrement du destinataire n’est pas bonne. Il n’a pas été possible de chiffrer le message. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1078"/>
        <source>Forced difficulty override. Send should start soon.</source>
        <translation>Neutralisation forcée de la difficulté. L’envoi devrait bientôt commencer.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1081"/>
        <source>Unknown status: %1 %2</source>
        <translation>Statut inconnu : %1 %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1622"/>
        <source>Not Connected</source>
        <translation>Déconnecté</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1212"/>
        <source>Show Bitmessage</source>
        <translation>Afficher Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="709"/>
        <source>Send</source>
        <translation>Envoyer</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1235"/>
        <source>Subscribe</source>
        <translation>S’abonner</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1241"/>
        <source>Channel</source>
        <translation>Canal</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="755"/>
        <source>Quit</source>
        <translation>Quitter</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1467"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.</source>
        <translation>Vous pouvez éditer vos clés en éditant le fichier keys.dat stocké dans le même répertoire que ce programme. Il est important de faire des sauvegardes de ce fichier.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1471"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file.</source>
        <translation>Vous pouvez éditer vos clés en éditant le fichier keys.dat stocké dans le répertoire %1.
Il est important de faire des sauvegardes de ce fichier.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1478"/>
        <source>Open keys.dat?</source>
        <translation>Ouvrir keys.dat ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1475"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Vous pouvez éditer vos clés en éditant le fichier keys.dat stocké dans le même répertoire que ce programme. Il est important de faire des sauvegardes de ce fichier. Souhaitez-vous l’ouvrir maintenant ? (Assurez-vous de fermer Bitmessage avant d’effectuer des changements.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1478"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Vous pouvez éditer vos clés en éditant le fichier keys.dat stocké dans le répertoire %1. Il est important de faire des sauvegardes de ce fichier. Souhaitez-vous l’ouvrir maintenant? (Assurez-vous de fermer Bitmessage avant d’effectuer des changements.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1485"/>
        <source>Delete trash?</source>
        <translation>Supprimer la corbeille ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1485"/>
        <source>Are you sure you want to delete all trashed messages?</source>
        <translation>Êtes-vous sûr de vouloir supprimer tous les messages dans la corbeille ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1503"/>
        <source>bad passphrase</source>
        <translation>Mauvaise phrase secrète</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1503"/>
        <source>You must type your passphrase. If you don&apos;t have one then this is not the form for you.</source>
        <translation>Vous devez taper votre phrase secrète. Si vous n’en avez pas, ce formulaire n’est pas pour vous.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1526"/>
        <source>Bad address version number</source>
        <translation>Mauvais numéro de version d’adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1516"/>
        <source>Your address version number must be a number: either 3 or 4.</source>
        <translation>Votre numéro de version d’adresse doit être un nombre : soit 3 soit 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1526"/>
        <source>Your address version number must be either 3 or 4.</source>
        <translation>Votre numéro de version d’adresse doit être soit 3 soit 4.</translation>
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
        <location filename="../bitmessageqt/__init__.py" line="1607"/>
        <source>Connection lost</source>
        <translation>Connexion perdue</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1657"/>
        <source>Connected</source>
        <translation>Connecté</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1777"/>
        <source>Message trashed</source>
        <translation>Message envoyé à la corbeille</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1866"/>
        <source>The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate.</source>
        <translation>Le TTL, ou Time-To-Live (temps à vivre) est la durée de temps durant laquelle le réseau va détenir le message.
Le destinataire doit l’obtenir avant ce temps. Si votre client Bitmessage ne reçoit pas de confirmation de réception, il va le ré-envoyer automatiquement. Plus le Time-To-Live est long, plus grand est le travail que votre ordinateur doit effectuer pour envoyer le message. Un Time-To-Live de quatre ou cinq jours est souvent approprié.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1911"/>
        <source>Message too long</source>
        <translation>Message trop long</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1911"/>
        <source>The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.</source>
        <translation>Le message que vous essayez d’envoyer est trop long de %1 octets (le  maximum est 261644 octets). Veuillez le réduire avant de l’envoyer.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1953"/>
        <source>Error: Your account wasn&apos;t registered at an email gateway. Sending registration now as %1, please wait for the registration to be processed before retrying sending.</source>
        <translation>Erreur : votre compte n’a pas été inscrit à une passerelle de courrier électronique. Envoi de l’inscription maintenant en tant que %1, veuillez patienter tandis que l’inscription est en cours de traitement, avant de retenter l’envoi.</translation>
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
        <location filename="../bitmessageqt/__init__.py" line="2104"/>
        <source>Error: You must specify a From address. If you don&apos;t have one, go to the &apos;Your Identities&apos; tab.</source>
        <translation>Erreur : Vous devez spécifier une adresse d’expéditeur. Si vous n’en avez pas, rendez-vous dans l’onglet &quot;Vos identités&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2038"/>
        <source>Address version number</source>
        <translation>Numéro de version de l’adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2038"/>
        <source>Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Concernant l’adresse %1, Bitmessage ne peut pas comprendre les numéros de version de %2. Essayez de mettre à jour Bitmessage vers la dernière version.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2042"/>
        <source>Stream number</source>
        <translation>Numéro de flux</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2042"/>
        <source>Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>Concernant l’adresse %1, Bitmessage ne peut pas supporter les nombres de flux de %2. Essayez de mettre à jour Bitmessage vers la dernière version.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2047"/>
        <source>Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won&apos;t send until you connect.</source>
        <translation>Avertissement : Vous êtes actuellement déconnecté. Bitmessage fera le travail nécessaire pour envoyer le message mais il ne sera pas envoyé tant que vous ne vous connecterez pas.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2096"/>
        <source>Message queued.</source>
        <translation>Message mis en file d’attente.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2100"/>
        <source>Your &apos;To&apos; field is empty.</source>
        <translation>Votre champ &quot;Vers&quot; est vide.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2161"/>
        <source>Right click one or more entries in your address book and select &apos;Send message to this address&apos;.</source>
        <translation>Cliquez droit sur une ou plusieurs entrées dans votre carnet d’adresses puis sélectionnez &quot;Envoyer un message à ces adresses&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2177"/>
        <source>Fetched address from namecoin identity.</source>
        <translation>Récupération avec succès de l’adresse de l’identité Namecoin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2289"/>
        <source>New Message</source>
        <translation>Nouveau message</translation>
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
        <location filename="../bitmessageqt/blacklist.py" line="60"/>
        <source>Address is valid.</source>
        <translation>L’adresse est valide.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="94"/>
        <source>The address you entered was invalid. Ignoring it.</source>
        <translation>L’adresse que vous avez entrée est invalide. Adresse ignorée.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2319"/>
        <source>Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.</source>
        <translation>Erreur : Vous ne pouvez pas ajouter une adresse déjà présente dans votre carnet d’adresses. Essayez de renommer l’adresse existante.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3359"/>
        <source>Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want.</source>
        <translation>Erreur : vous ne pouvez pas ajouter la même adresse deux fois à vos abonnements. Peut-être que vous pouvez renommer celle qui existe si vous le souhaitez.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2441"/>
        <source>Restart</source>
        <translation>Redémarrer</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2427"/>
        <source>You must restart Bitmessage for the port number change to take effect.</source>
        <translation>Vous devez redémarrer Bitmessage pour que le changement de port prenne effet.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2441"/>
        <source>Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any).</source>
        <translation>Bitmessage utilisera votre proxy dorénavant, mais vous pouvez redémarrer manuellement Bitmessage maintenant afin de fermer des connexions existantes (si il y en existe).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2470"/>
        <source>Number needed</source>
        <translation>Nombre requis</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2470"/>
        <source>Your maximum download and upload rate must be numbers. Ignoring what you typed.</source>
        <translation>Vos taux maximum de téléchargement et de téléversement doivent être des nombres. Ce que vous avez tapé est ignoré.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2550"/>
        <source>Will not resend ever</source>
        <translation>Ne renverra jamais</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2550"/>
        <source>Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent.</source>
        <translation>Notez que la limite de temps que vous avez entrée est plus courte que le temps d’attente respecté par Bitmessage avant le premier essai de renvoi, par conséquent votre message ne sera jamais renvoyé.</translation>
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
        <translation>Phrases secrètes différentes</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="136"/>
        <source>The passphrase you entered twice doesn&apos;t match. Try again.</source>
        <translation>Les phrases secrètes entrées sont différentes. Réessayez.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="144"/>
        <source>Choose a passphrase</source>
        <translation>Choisissez une phrase secrète</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="144"/>
        <source>You really do need a passphrase.</source>
        <translation>Vous devez vraiment utiliser une phrase secrète.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3038"/>
        <source>Address is gone</source>
        <translation>L’adresse a disparu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3038"/>
        <source>Bitmessage cannot find your address %1. Perhaps you removed it?</source>
        <translation>Bitmessage ne peut pas trouver votre adresse %1. Peut-être l’avez-vous supprimée?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3041"/>
        <source>Address disabled</source>
        <translation>Adresse désactivée</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3041"/>
        <source>Error: The address from which you are trying to send is disabled. You&apos;ll have to enable it on the &apos;Your Identities&apos; tab before using it.</source>
        <translation>Erreur : L’adresse avec laquelle vous essayez de communiquer est désactivée. Vous devez d’abord l’activer dans l’onglet &quot;Vos identités&quot; avant de l’utiliser.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3020"/>
        <source>Entry added to the Address Book. Edit the label to your liking.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3116"/>
        <source>Entry added to the blacklist. Edit the label to your liking.</source>
        <translation>Entrée ajoutée à la liste noire. Éditez l’étiquette à votre convenance.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3121"/>
        <source>Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want.</source>
        <translation>Erreur : vous ne pouvez pas ajouter la même adresse deux fois à votre liste noire. Essayez de renommer celle qui existe si vous le souhaitez.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3263"/>
        <source>Moved items to trash.</source>
        <translation>Messages déplacés dans la corbeille.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3207"/>
        <source>Undeleted item.</source>
        <translation>Articles restaurés.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3231"/>
        <source>Save As...</source>
        <translation>Enregistrer sous…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3240"/>
        <source>Write error.</source>
        <translation>Erreur d’écriture.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3343"/>
        <source>No addresses selected.</source>
        <translation>Aucune adresse sélectionnée.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3398"/>
        <source>If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the subscription?</source>
        <translation>Si vous supprimez cet abonnement, les messages que vous avez déjà reçus deviendront inaccessibles. Peut-être que vous devriez considérez d’abord de désactiver l’abonnement. Les abonnements désactivés ne reçoivent pas de nouveaux messages, mais vous pouvez encore voir ceux que vous avez déjà reçus.

Êtes-vous sur de vouloir supprimer cet abonnement ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3645"/>
        <source>If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the channel?</source>
        <translation>Si vous supprimez ce canal, les messages que vous avez déjà reçus deviendront inaccessibles. Peut-être que vous devriez considérez d’abord de désactiver le canal. Les canaux désactivés ne reçoivent pas de nouveaux messages, mais vous pouvez encore voir ceux que vous avez déjà reçus.

Êtes-vous sûr de vouloir supprimer ce canal ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3775"/>
        <source>Do you really want to remove this avatar?</source>
        <translation>Voulez-vous vraiment enlever cet avatar ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3783"/>
        <source>You have already set an avatar for this address. Do you really want to overwrite it?</source>
        <translation>Vous avez déjà mis un avatar pour cette adresse. Voulez-vous vraiment l’écraser ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4185"/>
        <source>Start-on-login not yet supported on your OS.</source>
        <translation>Le démarrage dès l’ouverture de session n’est pas encore supporté sur votre OS.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4178"/>
        <source>Minimize-to-tray not yet supported on your OS.</source>
        <translation>La minimisation en zone système n’est pas encore supportée sur votre OS.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4181"/>
        <source>Tray notifications not yet supported on your OS.</source>
        <translation>Les notifications en zone système ne sont pas encore supportées sur votre OS.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4352"/>
        <source>Testing...</source>
        <translation>Tester…</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4237"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="35"/>
        <source>The address should start with &apos;&apos;BM-&apos;&apos;</source>
        <translation>L’adresse devrait commencer avec &quot;BM-&quot;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="40"/>
        <source>The address is not typed or copied correctly (the checksum failed).</source>
        <translation>L’adresse n’est pas correcte (la somme de contrôle a échoué).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="46"/>
        <source>The version number of this address is higher than this software can support. Please upgrade Bitmessage.</source>
        <translation>Le numéro de version de cette adresse est supérieur à celui que le programme peut supporter. Veuiller mettre Bitmessage à jour.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="52"/>
        <source>The address contains invalid characters.</source>
        <translation>L’adresse contient des caractères invalides.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="57"/>
        <source>Some data encoded in the address is too short.</source>
        <translation>Certaines données encodées dans l’adresse sont trop courtes.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="62"/>
        <source>Some data encoded in the address is too long.</source>
        <translation>Certaines données encodées dans l’adresse sont trop longues.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="67"/>
        <source>Some data encoded in the address is malformed.</source>
        <translation>Quelques données codées dans l’adresse sont mal formées.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4289"/>
        <source>Enter an address above.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="171"/>
        <source>Address is an old type. We cannot display its past broadcasts.</source>
        <translation>L’adresse est d’ancien type. Nous ne pouvons pas montrer ses messages de diffusion passés.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="186"/>
        <source>There are no recent broadcasts from this address to display.</source>
        <translation>Il n’y a aucun message de diffusion récent de cette adresse à afficher.</translation>
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
        <translation>Identités</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="667"/>
        <source>New Identity</source>
        <translation>Nouvelle identité</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="730"/>
        <source>Search</source>
        <translation>Chercher</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="731"/>
        <source>All</source>
        <translation>Tous</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="738"/>
        <source>To</source>
        <translation>Vers</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="740"/>
        <source>From</source>
        <translation>De</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="742"/>
        <source>Subject</source>
        <translation>Sujet</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="735"/>
        <source>Message</source>
        <translation>Message</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="744"/>
        <source>Received</source>
        <translation>Reçu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="683"/>
        <source>Messages</source>
        <translation>Messages</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="686"/>
        <source>Address book</source>
        <translation>Carnet d’adresses</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="688"/>
        <source>Address</source>
        <translation>Adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="689"/>
        <source>Add Contact</source>
        <translation>Ajouter un contact</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="690"/>
        <source>Fetch Namecoin ID</source>
        <translation>Récupère l’ID Namecoin</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="697"/>
        <source>Subject:</source>
        <translation>Sujet :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="696"/>
        <source>From:</source>
        <translation>De :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="693"/>
        <source>To:</source>
        <translation>Vers :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="695"/>
        <source>Send ordinary Message</source>
        <translation>Envoyer un message ordinaire</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="699"/>
        <source>Send Message to your Subscribers</source>
        <translation>Envoyer un message à vos abonnés</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="700"/>
        <source>TTL:</source>
        <translation>TTL :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="727"/>
        <source>Subscriptions</source>
        <translation>Abonnements</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="711"/>
        <source>Add new Subscription</source>
        <translation>Ajouter un nouvel abonnement</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="745"/>
        <source>Chans</source>
        <translation>Canaux</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="729"/>
        <source>Add Chan</source>
        <translation>Ajouter un canal</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="750"/>
        <source>File</source>
        <translation>Fichier</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="761"/>
        <source>Settings</source>
        <translation>Paramètres</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="757"/>
        <source>Help</source>
        <translation>Aide</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="753"/>
        <source>Import keys</source>
        <translation>Importer les clés</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="754"/>
        <source>Manage keys</source>
        <translation>Gérer les clés</translation>
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
        <translation>Contacter le support</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="760"/>
        <source>About</source>
        <translation>À propos</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="762"/>
        <source>Regenerate deterministic addresses</source>
        <translation>Regénérer les clés déterministes</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="763"/>
        <source>Delete all trashed messages</source>
        <translation>Supprimer tous les messages dans la corbeille</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="764"/>
        <source>Join / Create chan</source>
        <translation>Rejoindre / créer un canal</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="206"/>
        <source>All accounts</source>
        <translation>Tous les comptes</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="47"/>
        <source>Zoom level %1%</source>
        <translation>Niveau de zoom %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="91"/>
        <source>Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.</source>
        <translation>Erreur : vous ne pouvez pas ajouter la même adresse deux fois à votre liste. Vous pouvez  peut-être, si vous le souhaitez, renommer celle qui existe déjà.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="112"/>
        <source>Add new entry</source>
        <translation>Ajouter une nouvelle entrée</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4334"/>
        <source>Display the %1 recent broadcast(s) from this address.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1786"/>
        <source>New version of PyBitmessage is available: %1. Download it from https://github.com/Bitmessage/PyBitmessage/releases/latest</source>
        <translation>Une nouvelle version de PyBitmessage est disponible : %1. Veuillez la télécharger depuis https://github.com/Bitmessage/PyBitmessage/releases/latest</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2801"/>
        <source>Waiting for PoW to finish... %1%</source>
        <translation>En attente de la fin de la PoW… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2811"/>
        <source>Shutting down Pybitmessage... %1%</source>
        <translation>Pybitmessage en cours d’arrêt… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2830"/>
        <source>Waiting for objects to be sent... %1%</source>
        <translation>En attente de l’envoi des objets… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2848"/>
        <source>Saving settings... %1%</source>
        <translation>Enregistrement des paramètres… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2861"/>
        <source>Shutting down core... %1%</source>
        <translation>Cœur en cours d’arrêt… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2867"/>
        <source>Stopping notifications... %1%</source>
        <translation>Arrêt des notifications… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2871"/>
        <source>Shutdown imminent... %1%</source>
        <translation>Arrêt imminent… %1%</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/bitmessageui.py" line="706"/>
        <source>%n hour(s)</source>
        <translation><numerusform>%n heure</numerusform><numerusform>%n heures</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="837"/>
        <source>%n day(s)</source>
        <translation><numerusform>%n jour</numerusform><numerusform>%n jours</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2769"/>
        <source>Shutting down PyBitmessage... %1%</source>
        <translation>PyBitmessage en cours d’arrêt… %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1156"/>
        <source>Sent</source>
        <translation>Envoyé</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="115"/>
        <source>Generating one new address</source>
        <translation>Production d’une nouvelle adresse</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="193"/>
        <source>Done generating address. Doing work necessary to broadcast it...</source>
        <translation>La production de l’adresse a été effectuée. Travail en cours afin de l’émettre…</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="219"/>
        <source>Generating %1 new addresses.</source>
        <translation>Production de %1 nouvelles adresses.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="323"/>
        <source>%1 is already in &apos;Your Identities&apos;. Not adding it again.</source>
        <translation>%1 est déjà dans &quot;Vos identités&quot;. Il ne sera pas ajouté de nouveau.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="377"/>
        <source>Done generating address</source>
        <translation>La production d’une adresse a été effectuée</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="228"/>
        <source>SOCKS5 Authentication problem: %1</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="481"/>
        <source>Disk full</source>
        <translation>Disque plein</translation>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="481"/>
        <source>Alert: Your disk or data storage volume is full. Bitmessage will now exit.</source>
        <translation>Alerte : votre disque ou le volume de stockage de données est plein. Bitmessage va maintenant se fermer.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="1060"/>
        <source>Error! Could not find sender address (your address) in the keys.dat file.</source>
        <translation>Erreur ! Il n’a pas été possible de trouver l’adresse d’expéditeur (votre adresse) dans le fichier keys.dat.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="580"/>
        <source>Doing work necessary to send broadcast...</source>
        <translation>Travail en cours afin d’envoyer le message de diffusion…</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="613"/>
        <source>Broadcast sent on %1</source>
        <translation>Message de diffusion envoyé %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="721"/>
        <source>Encryption key was requested earlier.</source>
        <translation>La clé de chiffrement a été demandée plus tôt.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="795"/>
        <source>Sending a request for the recipient&apos;s encryption key.</source>
        <translation>Envoi d’une demande de la clé de chiffrement du destinataire.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="820"/>
        <source>Looking up the receiver&apos;s public key</source>
        <translation>Recherche de la clé publique du récepteur</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="878"/>
        <source>Problem: Destination is a mobile device who requests that the destination be included in the message but this is disallowed in your settings.  %1</source>
        <translation>Problème : la destination est un dispositif mobile qui nécessite que la destination soit incluse dans le message mais ceci n’est pas autorisé dans vos paramètres. %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="909"/>
        <source>Doing work necessary to send message.
There is no required difficulty for version 2 addresses like this.</source>
        <translation>Travail en cours afin d’envoyer le message.
Il n’y a pas de difficulté requise pour les adresses version 2 comme celle-ci.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="944"/>
        <source>Doing work necessary to send message.
Receiver&apos;s required difficulty: %1 and %2</source>
        <translation>Travail en cours afin d’envoyer le message.
Difficulté requise du destinataire : %1 et %2</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="984"/>
        <source>Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do. %3</source>
        <translation>Problème : Le travail demandé par le destinataire (%1 and %2) est plus difficile que ce que vous avez paramétré. %3</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="1012"/>
        <source>Problem: You are trying to send a message to yourself or a chan but your encryption key could not be found in the keys.dat file. Could not encrypt message. %1</source>
        <translation>Problème : Vous essayez d’envoyer un message à un canal ou à vous-même mais votre clef de chiffrement n’a pas été trouvée dans le fichier keys.dat. Le message ne peut pas être chiffré. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1057"/>
        <source>Doing work necessary to send message.</source>
        <translation>Travail en cours afin d’envoyer le message.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="1218"/>
        <source>Message sent. Waiting for acknowledgement. Sent on %1</source>
        <translation>Message envoyé. En attente de l’accusé de réception. Envoyé %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1045"/>
        <source>Doing work necessary to request encryption key.</source>
        <translation>Travail en cours afin d’obtenir la clé de chiffrement.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="1380"/>
        <source>Broadcasting the public key request. This program will auto-retry if they are offline.</source>
        <translation>Diffusion de la demande de clef publique. Ce programme réessaiera automatiquement si ils sont déconnectés. </translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="1387"/>
        <source>Sending public key request. Waiting for reply. Requested at %1</source>
        <translation>Envoi d’une demande de clef publique. En attente d’une réponse. Demandée à %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="235"/>
        <source>UPnP port mapping established on port %1</source>
        <translation>Transfert de port UPnP établi sur le port %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="264"/>
        <source>UPnP port mapping removed</source>
        <translation>Transfert de port UPnP retiré</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="244"/>
        <source>Mark all messages as read</source>
        <translation>Marquer tous les messages comme lus</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2648"/>
        <source>Are you sure you would like to mark all messages read?</source>
        <translation>Êtes-vous sûr(e) de vouloir marquer tous les messages comme lus ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1066"/>
        <source>Doing work necessary to send broadcast.</source>
        <translation>Travail en cours afin d’envoyer la diffusion.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2737"/>
        <source>Proof of work pending</source>
        <translation>En attente de preuve de fonctionnement</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2737"/>
        <source>%n object(s) pending proof of work</source>
        <translation><numerusform>%n objet en attente de preuve de fonctionnement</numerusform><numerusform>%n objet(s) en attente de preuve de fonctionnement</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2737"/>
        <source>%n object(s) waiting to be distributed</source>
        <translation><numerusform>%n objet en attente d&apos;être distribué</numerusform><numerusform>%n objet(s) en attente d&apos;être distribués</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2737"/>
        <source>Wait until these tasks finish?</source>
        <translation>Attendre jusqu&apos;à ce que ces tâches se terminent ?</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="115"/>
        <source>The name %1 was not found.</source>
        <translation>Le nom %1 n&apos;a pas été trouvé.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="124"/>
        <source>The namecoin query failed (%1)</source>
        <translation>La requête Namecoin a échouée (%1)</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="127"/>
        <source>The namecoin query failed.</source>
        <translation>La requête Namecoin a échouée.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="133"/>
        <source>The name %1 has no valid JSON data.</source>
        <translation>Le nom %1 n&apos;a aucune donnée JSON valide.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="141"/>
        <source>The name %1 has no associated Bitmessage address.</source>
        <translation>Le nom %1 n&apos;a aucune adresse Bitmessage d&apos;associée.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="171"/>
        <source>Success!  Namecoind version %1 running.</source>
        <translation>Succès ! Namecoind version %1 en cours d&apos;exécution.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="182"/>
        <source>Success!  NMControll is up and running.</source>
        <translation>Succès ! NMControll est debout et en cours d&apos;exécution.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="185"/>
        <source>Couldn&apos;t understand NMControl.</source>
        <translation>Ne pouvait pas comprendre NMControl.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="195"/>
        <source>The connection to namecoin failed.</source>
        <translation>La connexion à Namecoin a échouée.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="120"/>
        <source>Your GPU(s) did not calculate correctly, disabling OpenCL. Please report to the developers.</source>
        <translation>Votre GPU(s) n&apos;a pas calculé correctement, mettant OpenCL hors service. Veuillez remonter ceci aux développeurs s&apos;il vous plaît.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3823"/>
        <source>Set notification sound...</source>
        <translation>Mettre un son de notification ...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="647"/>
        <source>
        Welcome to easy and secure Bitmessage
            * send messages to other people
            * send broadcast messages like twitter or
            * discuss in chan(nel)s with other people
        </source>
        <translation>
Bienvenue dans le facile et sécurisé Bitmessage
* envoyer des messages à d&apos;autres personnes
* envoyer des messages par diffusion (broadcast) à la manière de Twitter ou
* discuter dans des canaux (channels) avec d&apos;autres personnes
</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="828"/>
        <source>not recommended for chans</source>
        <translation>pas recommandé pour les canaux</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1221"/>
        <source>Quiet Mode</source>
        <translation>Mode tranquille</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1613"/>
        <source>Problems connecting? Try enabling UPnP in the Network Settings</source>
        <translation>Des difficultés à se connecter ? Essayez de permettre UPnP dans les &quot;Paramètres réseau&quot;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1940"/>
        <source>You are trying to send an email instead of a bitmessage. This requires registering with a gateway. Attempt to register?</source>
        <translation>Vous essayez d&apos;envoyer un courrier électronique au lieu d&apos;un bitmessage. Ceci exige votre inscription à une passerelle. Essayer de vous inscrire ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1972"/>
        <source>Error: Bitmessage addresses start with BM-   Please check the recipient address %1</source>
        <translation>Erreur : Les adresses Bitmessage commencent par BM- Veuillez vérifier l&apos;adresse du destinataire %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1978"/>
        <source>Error: The recipient address %1 is not typed or copied correctly. Please check it.</source>
        <translation>Erreur : L’adresse du destinataire %1 n’est pas correctement tapée ou recopiée. Veuillez la vérifier.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1984"/>
        <source>Error: The recipient address %1 contains invalid characters. Please check it.</source>
        <translation>Erreur : L’adresse du destinataire %1 contient des caractères invalides. Veuillez la vérifier.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1990"/>
        <source>Error: The version of the recipient address %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</source>
        <translation>Erreur : la version de l’adresse destinataire %1 est trop élevée. Vous devez mettre à niveau votre logiciel Bitmessage ou alors celui de votre connaissance est plus intelligent.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1998"/>
        <source>Error: Some data encoded in the recipient address %1 is too short. There might be something wrong with the software of your acquaintance.</source>
        <translation>Erreur : quelques données codées dans l’adresse destinataire %1 sont trop courtes. Il pourrait y avoir un soucis avec le logiciel de votre connaissance.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2006"/>
        <source>Error: Some data encoded in the recipient address %1 is too long. There might be something wrong with the software of your acquaintance.</source>
        <translation>Erreur : quelques données codées dans l’adresse destinataire %1 sont trop longues. Il pourrait y avoir un soucis avec le logiciel de votre connaissance.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2014"/>
        <source>Error: Some data encoded in the recipient address %1 is malformed. There might be something wrong with the software of your acquaintance.</source>
        <translation>Erreur : quelques données codées dans l’adresse destinataire %1 sont mal formées. Il pourrait y avoir un soucis avec le logiciel de votre connaissance.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2022"/>
        <source>Error: Something is wrong with the recipient address %1.</source>
        <translation>Erreur : quelque chose ne va pas avec l&apos;adresse de destinataire %1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2172"/>
        <source>Error: %1</source>
        <translation>Erreur : %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2289"/>
        <source>From %1</source>
        <translation>De %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2692"/>
        <source>Disconnecting</source>
        <translation>Déconnexion</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2692"/>
        <source>Connecting</source>
        <translation>Connexion</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2692"/>
        <source>Bitmessage will now drop all connectins. Are you sure?</source>
        <translation>Bitmessage va maintenant laisser tomber toutes les connections. Êtes-vous sûr(e) ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2692"/>
        <source>Bitmessage will now start connecting to network. Are you sure?</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2748"/>
        <source>Synchronisation pending</source>
        <translation>En attente de synchronisation</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2748"/>
        <source>Bitmessage hasn&apos;t synchronised with the network, %n object(s) to be downloaded. If you quit now, it may cause delivery delays. Wait until the synchronisation finishes?</source>
        <translation><numerusform>Bitmessage ne s&apos;est pas synchronisé avec le réseau, %n objet(s) à télécharger. Si vous quittez maintenant, cela pourrait causer des retards de livraison. Attendre jusqu&apos;à ce que la synchronisation aboutisse ?</numerusform><numerusform>Bitmessage ne s&apos;est pas synchronisé avec le réseau, %n objet(s) à télécharger. Si vous quittez maintenant, cela pourrait causer des retards de livraison. Attendre jusqu&apos;à ce que la synchronisation aboutisse ?</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2758"/>
        <source>Not connected</source>
        <translation>Non connecté</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2758"/>
        <source>Bitmessage isn&apos;t connected to the network. If you quit now, it may cause delivery delays. Wait until connected and the synchronisation finishes?</source>
        <translation>Bitmessage n&apos;est pas connecté au réseau. Si vous quittez maintenant, cela pourrait causer des retards de livraison. Attendre jusqu&apos;à ce qu&apos;il soit connecté et que la synchronisation se termine ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2773"/>
        <source>Waiting for network connection...</source>
        <translation>En attente de connexion réseau...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2783"/>
        <source>Waiting for finishing synchronisation...</source>
        <translation>En attente d&apos;achèvement de la synchronisation...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3841"/>
        <source>You have already set a notification sound for this address book entry. Do you really want to overwrite it?</source>
        <translation>Vous avez déjà mis un son de notification pour cette adresse. Voulez-vous vraiment l’écraser ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4062"/>
        <source>Error occurred: could not load message from disk.</source>
        <translation>Une erreur a eu lieu : ne peut pas charger de message depuis le disque.</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/address_dialogs.py" line="194"/>
        <source>Display the %n recent broadcast(s) from this address.</source>
        <translation><numerusform>Afficher le messages de diffusion le plus récent originaire de cette adresse.</numerusform><numerusform>Afficher les %n messages de diffusion les plus récents originaires de cette adresse.</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="658"/>
        <source>Go online</source>
        <translation>Passer en-ligne</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="658"/>
        <source>Go offline</source>
        <translation>Passer hors-ligne</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="707"/>
        <source>Clear</source>
        <translation>Vider</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="10"/>
        <source>inbox</source>
        <translation>entrant</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="11"/>
        <source>new</source>
        <translation>nouveau</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="12"/>
        <source>sent</source>
        <translation>envoyé</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="13"/>
        <source>trash</source>
        <translation>corbeille</translation>
    </message>
</context>
<context>
    <name>MessageView</name>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="72"/>
        <source>Follow external link</source>
        <translation>Suivre lien externe</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="72"/>
        <source>The link &quot;%1&quot; will open in a browser. It may be a security risk, it could de-anonymise you or download malicious data. Are you sure?</source>
        <translation>Le lien &quot;%1&quot; s&apos;ouvrira dans un navigateur. Cela pourrait être un risque de sécurité, cela pourrait vous désanonymiser ou télécharger des données malveillantes. Êtes-vous sûr(e) ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="117"/>
        <source>HTML detected, click here to display</source>
        <translation>HTML détecté, cliquer ici pour l&apos;afficher</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="126"/>
        <source>Click here to disable HTML</source>
        <translation>Cliquer ici pour mettre hors de service le HTML</translation>
    </message>
</context>
<context>
    <name>MsgDecode</name>
    <message>
        <location filename="../helper_msgcoding.py" line="81"/>
        <source>The message has an unknown encoding.
Perhaps you should upgrade Bitmessage.</source>
        <translation>Le message est codé de façon inconnue.
Peut-être que vous devriez mettre à niveau Bitmessage.</translation>
    </message>
    <message>
        <location filename="../helper_msgcoding.py" line="82"/>
        <source>Unknown encoding</source>
        <translation>Encodage inconnu</translation>
    </message>
</context>
<context>
    <name>NewAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="14"/>
        <source>Create new Address</source>
        <translation>Créer une nouvelle adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="23"/>
        <source>Here you may generate as many addresses as you like. Indeed, creating and abandoning addresses is encouraged. You may generate addresses by using either random numbers or by using a passphrase. If you use a passphrase, the address is called a &quot;deterministic&quot; address.
The &apos;Random Number&apos; option is selected by default but deterministic addresses have several pros and cons:</source>
        <translation>Vous pouvez générer autant d’adresses que vous le souhaitez. En effet, nous vous encourageons à créer et à délaisser vos adresses. Vous pouvez générer des adresses en utilisant des nombres aléatoires ou en utilisant une phrase secrète. Si vous utilisez une phrase secrète, l’adresse sera une adresse &quot;déterministe&quot;.
L’option &quot;Nombre Aléatoire&quot; est sélectionnée par défaut mais les adresses déterministes ont certains avantages et inconvénients :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="37"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Pros:&lt;br/&gt;&lt;/span&gt;You can recreate your addresses on any computer from memory. &lt;br/&gt;You need-not worry about backing up your keys.dat file as long as you can remember your passphrase. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Cons:&lt;br/&gt;&lt;/span&gt;You must remember (or write down) your passphrase if you expect to be able to recreate your keys if they are lost. &lt;br/&gt;You must remember the address version number and the stream number along with your passphrase. &lt;br/&gt;If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Avantages :&lt;br/&gt;&lt;/span&gt;Vous pouvez recréer vos adresses sur n’importe quel ordinateur. &lt;br/&gt;Vous n’avez pas à vous inquiéter à propos de la sauvegarde de votre fichier keys.dat tant que vous vous rappelez de votre phrase secrète. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Inconvénients :&lt;br/&gt;&lt;/span&gt;Vous devez vous rappeler (ou noter) votre phrase secrète si vous souhaitez être capable de récréer vos clés si vous les perdez. &lt;br/&gt;Vous devez vous rappeler du numéro de version de l’adresse et du numéro de flux en plus de votre phrase secrète. &lt;br/&gt;Si vous choisissez une phrase secrète faible et que quelqu’un sur Internet parvient à la brute-forcer, il pourra lire vos messages et vous en envoyer.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="66"/>
        <source>Use a random number generator to make an address</source>
        <translation>Utiliser un générateur de nombres aléatoires pour créer une adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="79"/>
        <source>Use a passphrase to make addresses</source>
        <translation>Utiliser une phrase secrète pour créer une adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="89"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Créer une adresse plus courte d’un ou deux caractères (nécessite plusieurs minutes de temps de calcul supplémentaires)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="96"/>
        <source>Make deterministic addresses</source>
        <translation>Créer une adresse déterministe</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="102"/>
        <source>Address version number: 4</source>
        <translation>Numéro de version de l’adresse : 4</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="109"/>
        <source>In addition to your passphrase, you must remember these numbers:</source>
        <translation>En plus de votre phrase secrète, vous devez vous rappeler ces numéros:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="126"/>
        <source>Passphrase</source>
        <translation>Phrase secrète</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="133"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Nombre d’adresses basées sur votre phrase secrète à créer :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="153"/>
        <source>Stream number: 1</source>
        <translation>Nombre de flux : 1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="173"/>
        <source>Retype passphrase</source>
        <translation>Retapez la phrase secrète</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="200"/>
        <source>Randomly generate address</source>
        <translation>Générer une adresse de manière aléatoire</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="206"/>
        <source>Label (not shown to anyone except you)</source>
        <translation>Étiquette (seulement visible par vous)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="216"/>
        <source>Use the most available stream</source>
        <translation>Utiliser le flux le plus disponible</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="226"/>
        <source> (best if this is the first of many addresses you will create)</source>
        <translation>(préférable si vous générez votre première adresse)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="236"/>
        <source>Use the same stream as an existing address</source>
        <translation>Utiliser le même flux qu’une adresse existante</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.ui" line="246"/>
        <source>(saves you some bandwidth and processing power)</source>
        <translation>(économise de la bande passante et de la puissance de calcul)</translation>
    </message>
</context>
<context>
    <name>NewSubscriptionDialog</name>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.ui" line="20"/>
        <source>Add new entry</source>
        <translation>Ajouter une nouvelle entrée</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.ui" line="26"/>
        <source>Label</source>
        <translation>Étiquette</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.ui" line="36"/>
        <source>Address</source>
        <translation>Adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.ui" line="59"/>
        <source>Enter an address above.</source>
        <translation>Entrez ci-dessus une adresse.</translation>
    </message>
</context>
<context>
    <name>SpecialAddressBehaviorDialog</name>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="14"/>
        <source>Special Address Behavior</source>
        <translation>Comportement spécial de l’adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="20"/>
        <source>Behave as a normal address</source>
        <translation>Se comporter comme une adresse normale</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="30"/>
        <source>Behave as a pseudo-mailing-list address</source>
        <translation>Se comporter comme une adresse d’une pseudo liste de diffusion</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="37"/>
        <source>Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).</source>
        <translation>Un mail reçu sur une adresse d’une pseudo liste de diffusion sera automatiquement diffusé aux abonnés (et sera donc public).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.ui" line="47"/>
        <source>Name of the pseudo-mailing-list:</source>
        <translation>Nom de la pseudo liste de diffusion :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/address_dialogs.py" line="230"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation>Ceci est une adresse de canal. Vous ne pouvez pas l’utiliser en tant que pseudo liste de diffusion.</translation>
    </message>
</context>
<context>
    <name>aboutDialog</name>
    <message>
        <location filename="../bitmessageqt/about.ui" line="14"/>
        <source>About</source>
        <translation>À propos</translation>
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
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distribué sous la licence logicielle MIT/X11; voir &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.ui" line="59"/>
        <source>This is Beta software.</source>
        <translation>Version bêta.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright Â© 2012-2016 Jonathan Warren&lt;br/&gt;Copyright Â© 2013-2016 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"/>
    </message>
    <message encoding="UTF-8">
        <location filename="../bitmessageqt/about.ui" line="49"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright © 2012-2016 Jonathan Warren&lt;br/&gt;Copyright © 2013-2017 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright © 2012-2016 Jonathan Warren&lt;br/&gt;Copyright © 2013-2017 Les développeurs de Bitmessage&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
</context>
<context>
    <name>blacklist</name>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="17"/>
        <source>Use a Blacklist (Allow all incoming messages except those on the Blacklist)</source>
        <translation>Utiliser une liste noire (Blacklist. Cela autorise tous les messages entrants sauf ceux présents sur la liste noire)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="27"/>
        <source>Use a Whitelist (Block all incoming messages except those on the Whitelist)</source>
        <translation>Utiliser une liste blanche (Whitelist. Bloque tous les messages entrants sauf ceux présents sur cette liste blanche)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="34"/>
        <source>Add new entry</source>
        <translation>Ajouter une nouvelle entrée</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="85"/>
        <source>Name or Label</source>
        <translation>Nom ou Étiquette</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="90"/>
        <source>Address</source>
        <translation>Adresse</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="151"/>
        <source>Blacklist</source>
        <translation>Liste noire</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="153"/>
        <source>Whitelist</source>
        <translation>Liste blanche</translation>
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
        <translation>Bitmessage ne connectera à personne avant que vous ne le laissiez faire.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.ui" line="27"/>
        <source>Connect now</source>
        <translation>Connexion maintenant</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.ui" line="37"/>
        <source>Let me configure special network settings first</source>
        <translation>Me laisser d’abord configurer des paramètres spéciaux de réseau</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.ui" line="44"/>
        <source>Work offline</source>
        <translation>Travailler hors-ligne</translation>
    </message>
</context>
<context>
    <name>helpDialog</name>
    <message>
        <location filename="../bitmessageqt/help.ui" line="14"/>
        <source>Help</source>
        <translation>Aide</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.ui" line="20"/>
        <source>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</source>
        <translation>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.ui" line="30"/>
        <source>As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:</source>
        <translation>Bitmessage étant un projet collaboratif, une aide peut être trouvée en ligne sur le Wiki de Bitmessage:</translation>
    </message>
</context>
<context>
    <name>iconGlossaryDialog</name>
    <message>
        <location filename="../bitmessageqt/iconglossary.ui" line="20"/>
        <source>Icon Glossary</source>
        <translation>Glossaire des icônes</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.ui" line="36"/>
        <source>You have no connections with other peers. </source>
        <translation>Vous n’avez aucune connexion avec d’autres pairs.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.ui" line="53"/>
        <source>You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn&apos;t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.</source>
        <translation>Vous avez au moins une connexion sortante avec un pair mais vous n’avez encore reçu aucune connexion entrante. Votre pare-feu ou routeur n’est probablement pas configuré pour transmettre les connexions TCP vers votre ordinateur. Bitmessage fonctionnera correctement, mais le réseau Bitmessage se portera mieux si vous autorisez les connexions entrantes. Cela vous permettra d’être un nœud mieux connecté.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="85"/>
        <source>You are using TCP port ?. (This can be changed in the settings).</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.ui" line="96"/>
        <source>You do have connections with other peers and your firewall is correctly configured.</source>
        <translation>Vous avez des connexions avec d’autres pairs et votre pare-feu est configuré correctement.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/dialogs.py" line="58"/>
        <source>You are using TCP port %1. (This can be changed in the settings).</source>
        <translation>Vous utilisez le port TCP %1. (Ceci peut être changé dans les paramètres).</translation>
    </message>
</context>
<context>
    <name>networkstatus</name>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="39"/>
        <source>Total connections:</source>
        <translation>Total de connexions:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="185"/>
        <source>Since startup:</source>
        <translation>Depuis le démarrage :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="201"/>
        <source>Processed 0 person-to-person messages.</source>
        <translation>Traité 0 messages de personne à personne.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="230"/>
        <source>Processed 0 public keys.</source>
        <translation>Traité 0 clés publiques.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="217"/>
        <source>Processed 0 broadcasts.</source>
        <translation>Traité 0 message de diffusion.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="282"/>
        <source>Inventory lookups per second: 0</source>
        <translation>Consultations d’inventaire par seconde : 0</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="243"/>
        <source>Objects to be synced:</source>
        <translation>Objets à synchroniser :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="152"/>
        <source>Stream #</source>
        <translation>Flux N°</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="116"/>
        <source>Connections</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="171"/>
        <source>Since startup on %1</source>
        <translation>Démarré depuis le %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="90"/>
        <source>Down: %1/s  Total: %2</source>
        <translation>Téléchargées : %1/s  Total : %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="92"/>
        <source>Up: %1/s  Total: %2</source>
        <translation>Téléversées : %1/s  Total : %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="153"/>
        <source>Total Connections: %1</source>
        <translation>Total des connexions : %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="163"/>
        <source>Inventory lookups per second: %1</source>
        <translation>Consultations d’inventaire par seconde : %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="256"/>
        <source>Up: 0 kB/s</source>
        <translation>Téléversement : 0 kO/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="269"/>
        <source>Down: 0 kB/s</source>
        <translation>Téléchargement : 0 kO/s</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="749"/>
        <source>Network Status</source>
        <translation>Statut du réseau</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="57"/>
        <source>byte(s)</source>
        <translation><numerusform>octet</numerusform><numerusform>octets</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="68"/>
        <source>Object(s) to be synced: %n</source>
        <translation><numerusform>Objet à synchroniser : %n</numerusform><numerusform>Objets à synchroniser : %n</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="72"/>
        <source>Processed %n person-to-person message(s).</source>
        <translation><numerusform>Traité %n message de personne à personne.</numerusform><numerusform>Traité %n messages de personne à personne.</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="77"/>
        <source>Processed %n broadcast message(s).</source>
        <translation><numerusform>Traité %n message de diffusion.</numerusform><numerusform>Traité %n messages de diffusion.</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="82"/>
        <source>Processed %n public key(s).</source>
        <translation><numerusform>Traité %n clé publique.</numerusform><numerusform>Traité %n clés publiques.</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="120"/>
        <source>Peer</source>
        <translation>Pair</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="123"/>
        <source>IP address or hostname</source>
        <translation>Adresse IP ou nom d&apos;hôte</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="128"/>
        <source>Rating</source>
        <translation>Évaluation</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="131"/>
        <source>PyBitmessage tracks the success rate of connection attempts to individual nodes. The rating ranges from -1 to 1 and affects the likelihood of selecting the node in the future</source>
        <translation>PyBitmessage suit à la trace le taux de réussites de connexions tentées vers les noeuds individuels. L&apos;évaluation s&apos;étend de -1 à 1 et affecte la probabilité de choisir ce noeud dans l&apos;avenir</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="136"/>
        <source>User agent</source>
        <translation>Agent utilisateur</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="139"/>
        <source>Peer&apos;s self-reported software</source>
        <translation>Logiciel, auto-rapporté par le pair</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="144"/>
        <source>TLS</source>
        <translation>TLS</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="147"/>
        <source>Connection encryption</source>
        <translation>Chiffrement de la connexion</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="155"/>
        <source>List of streams negotiated between you and the peer</source>
        <translation>Liste de flux négociés entre vous et le pair</translation>
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
        <translation>Créer ou rejoindre un canal</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="41"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly, then the chan will be secure and private. However if you and someone else both create a chan with the same chan name, the same chan will be shared.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Un canal existe lorsqu&apos;un groupe de personnes partage les mêmes clés de décryptage. Les clés et l&apos;adresse bitmessage utilisées par un canal sont produites à partir d&apos;un mot ou d&apos;une phrase faciles à mémoriser par des hommes. Pour envoyer un message à tout le monde dans le canal, envoyez un message à l&apos;adresse du canal.&lt;/p&gt;&lt;p&gt;Les canaux sont expérimentaux et complètement sans modération.&lt;/p&gt;&lt;p&gt;Entrez un nom pour votre canal. Si vous le choisissez un nom de canal suffisamment complexe (comme par exemple une phrase mot de passe qui soit forte et unique) et qu&apos;aucun de vos amis ne le partage publiquement, alors le canal sera sécurisé et privé. Cependant si vous et quelqu&apos;un d&apos;autre créez tous les deux un canal ayant le même nom, ces canaux identiques seront partagés.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="56"/>
        <source>Chan passphrase/name:</source>
        <translation>Phrase passe ou nom :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="63"/>
        <source>Optional, for advanced usage</source>
        <translation>Facultatif, pour une utilisation avancée</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="76"/>
        <source>Chan address</source>
        <translation>Adresse de canal</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="101"/>
        <source>Please input chan name/passphrase:</source>
        <translation>Veuillez saisir le nom du canal ou la phrase mot de passe :</translation>
    </message>
</context>
<context>
    <name>newchandialog</name>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="38"/>
        <source>Successfully created / joined chan %1</source>
        <translation>Le canal %1 a été rejoint ou créé avec succès.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="44"/>
        <source>Chan creation / joining failed</source>
        <translation>Échec lors de la création du canal ou de la tentative de le rejoindre</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="50"/>
        <source>Chan creation / joining cancelled</source>
        <translation>Annulation de la création du canal ou de la tentative de le rejoindre</translation>
    </message>
</context>
<context>
    <name>proofofwork</name>
    <message>
        <location filename="../proofofwork.py" line="163"/>
        <source>C PoW module built successfully.</source>
        <translation>Module PoW C construit avec succès.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="165"/>
        <source>Failed to build C PoW module. Please build it manually.</source>
        <translation>Échec à construire le module PoW C. Veuillez le construire manuellement.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="167"/>
        <source>C PoW module unavailable. Please build it.</source>
        <translation>Module PoW C non disponible. Veuillez le construire.</translation>
    </message>
</context>
<context>
    <name>regenerateAddressesDialog</name>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="14"/>
        <source>Regenerate Existing Addresses</source>
        <translation>Regénérer des adresses existantes</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="30"/>
        <source>Regenerate existing addresses</source>
        <translation>Adresses existantes régénérées</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="36"/>
        <source>Passphrase</source>
        <translation>Phrase secrète</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="53"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Nombre d’adresses basées sur votre phrase secrète à créer :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="89"/>
        <source>Address version number:</source>
        <translation>Numéro de version de l’adresse :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="131"/>
        <source>Stream number:</source>
        <translation>Numéro du flux :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="153"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="173"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Créer une adresse plus courte d’un ou deux caractères (nécessite plusieurs minutes de temps de calcul supplémentaires)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="180"/>
        <source>You must check (or not check) this box just like you did (or didn&apos;t) when you made your addresses the first time.</source>
        <translation>Vous devez cocher (ou décocher) cette case comme vous l’aviez fait (ou non) lors de la création de vos adresses la première fois.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.ui" line="190"/>
        <source>If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.</source>
        <translation>Si vous aviez généré des adresses déterministes mais les avez perdues à cause d’un accident (comme une panne de disque dur), vous pouvez les régénérer ici. Si vous aviez utilisé le générateur de nombres aléatoires pour créer vos adresses, ce formulaire ne vous sera d’aucune utilité.</translation>
    </message>
</context>
<context>
    <name>settingsDialog</name>
    <message>
        <location filename="../bitmessageqt/settings.py" line="483"/>
        <source>Settings</source>
        <translation>Paramètres</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="484"/>
        <source>Start Bitmessage on user login</source>
        <translation>Démarrer Bitmessage à la connexion de l’utilisateur</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="485"/>
        <source>Tray</source>
        <translation>Zone de notification</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="486"/>
        <source>Start Bitmessage in the tray (don&apos;t show main window)</source>
        <translation>Démarrer Bitmessage dans la barre des tâches (ne pas montrer la fenêtre principale)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="491"/>
        <source>Minimize to tray</source>
        <translation>Minimiser dans la barre des tâches</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="492"/>
        <source>Close to tray</source>
        <translation>Fermer vers la zone de notification</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="495"/>
        <source>Show notification when message received</source>
        <translation>Montrer une notification lorsqu’un message est reçu</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="500"/>
        <source>Run in Portable Mode</source>
        <translation>Lancer en Mode Portable</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="501"/>
        <source>In Portable Mode, messages and config files are stored in the same directory as the program rather than the normal application-data folder. This makes it convenient to run Bitmessage from a USB thumb drive.</source>
        <translation>En Mode Portable, les messages et les fichiers de configuration sont stockés dans le même dossier que le programme plutôt que le dossier de l’application. Cela rend l’utilisation de Bitmessage plus facile depuis une clé USB.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="508"/>
        <source>Willingly include unencrypted destination address when sending to a mobile device</source>
        <translation>Inclure volontairement l’adresse de destination non chiffrée lors de l’envoi vers un dispositif mobile</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="513"/>
        <source>Use Identicons</source>
        <translation>Utilise des Identicônes.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="514"/>
        <source>Reply below Quote</source>
        <translation>Réponse en dessous de la citation</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="515"/>
        <source>Interface Language</source>
        <translation>Langue de l’interface</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="516"/>
        <source>System Settings</source>
        <comment>system</comment>
        <translation>Paramètres système</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="517"/>
        <source>User Interface</source>
        <translation>Interface utilisateur</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="522"/>
        <source>Listening port</source>
        <translation>Port d’écoute</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="523"/>
        <source>Listen for connections on port:</source>
        <translation>Écouter les connexions sur le port :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="524"/>
        <source>UPnP:</source>
        <translation>UPnP :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="525"/>
        <source>Bandwidth limit</source>
        <translation>Limite de bande passante</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="526"/>
        <source>Maximum download rate (kB/s): [0: unlimited]</source>
        <translation>Taux de téléchargement maximal (kO/s) : [0 : illimité]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="527"/>
        <source>Maximum upload rate (kB/s): [0: unlimited]</source>
        <translation>Taux de téléversement maximal (kO/s) : [0 : illimité]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="529"/>
        <source>Proxy server / Tor</source>
        <translation>Serveur proxy / Tor</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="530"/>
        <source>Type:</source>
        <translation>Type :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="531"/>
        <source>Server hostname:</source>
        <translation>Nom du serveur:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="601"/>
        <source>Port:</source>
        <translation>Port :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="533"/>
        <source>Authentication</source>
        <translation>Authentification</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="602"/>
        <source>Username:</source>
        <translation>Utilisateur :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="535"/>
        <source>Pass:</source>
        <translation>Mot de passe :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="536"/>
        <source>Listen for incoming connections when using proxy</source>
        <translation>Écoute les connexions entrantes lors de l’utilisation du proxy</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="541"/>
        <source>none</source>
        <translation>aucun</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="542"/>
        <source>SOCKS4a</source>
        <translation>SOCKS4a</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="543"/>
        <source>SOCKS5</source>
        <translation>SOCKS5</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="544"/>
        <source>Network Settings</source>
        <translation>Paramètres réseau</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="549"/>
        <source>Total difficulty:</source>
        <translation>Difficulté totale :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="550"/>
        <source>The &apos;Total difficulty&apos; affects the absolute amount of work the sender must complete. Doubling this value doubles the amount of work.</source>
        <translation>La &quot;difficulté totale&quot; affecte le montant total de travail que l’envoyeur devra accomplir. Doubler cette valeur double la charge de travail.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="556"/>
        <source>Small message difficulty:</source>
        <translation>Difficulté d’un message court :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="557"/>
        <source>When someone sends you a message, their computer must first complete some work. The difficulty of this work, by default, is 1. You may raise this default for new addresses you create by changing the values here. Any new addresses you create will require senders to meet the higher difficulty. There is one exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically notify them when you next send a message that they need only complete the minimum amount of work: difficulty 1. </source>
        <translation>Lorsque quelqu’un vous envoie un message, son ordinateur doit d’abord effectuer un travail. La difficulté de ce travail, par défaut, est de 1. Vous pouvez augmenter cette valeur pour les adresses que vous créez en changeant la valeur ici. Chaque nouvelle adresse que vous créez requerra à l’envoyeur de faire face à une difficulté supérieure. Il existe une exception : si vous ajoutez un ami ou une connaissance à votre carnet d’adresses, Bitmessage les notifiera automatiquement lors du prochain message que vous leur envoyez qu’ils ne doivent compléter que la charge de travail minimale : difficulté 1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="566"/>
        <source>The &apos;Small message difficulty&apos; mostly only affects the difficulty of sending small messages. Doubling this value makes it almost twice as difficult to send a small message but doesn&apos;t really affect large messages.</source>
        <translation>La &quot;difficulté d’un message court&quot; affecte principalement la difficulté d’envoyer des messages courts. Doubler cette valeur rend la difficulté à envoyer un court message presque double, tandis qu’un message plus long ne sera pas réellement affecté.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="573"/>
        <source>Demanded difficulty</source>
        <translation>Difficulté exigée</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="578"/>
        <source>Here you may set the maximum amount of work you are willing to do to send a message to another person. Setting these values to 0 means that any value is acceptable.</source>
        <translation>Vous pouvez préciser quelle charge de travail vous êtes prêt à effectuer afin d’envoyer un message à une personne. Placer cette valeur à 0 signifie que n’importe quelle valeur est acceptée.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="584"/>
        <source>Maximum acceptable total difficulty:</source>
        <translation>Difficulté maximale acceptée :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="585"/>
        <source>Maximum acceptable small message difficulty:</source>
        <translation>Difficulté maximale acceptée pour les messages courts :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="586"/>
        <source>Max acceptable difficulty</source>
        <translation>Difficulté maximale acceptée</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Hardware GPU acceleration (OpenCL)</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="592"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage can utilize a different Bitcoin-based program called Namecoin to make addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage address, you can simply tell him to send a message to &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Getting your own Bitmessage address into Namecoin is still rather difficult).&lt;/p&gt;&lt;p&gt;Bitmessage can use either namecoind directly or a running nmcontrol instance.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage peut utiliser Namecoin, un autre programme basé sur Bitcoin, pour avoir des adresses plus parlantes. Par exemple, plutôt que de donner à votre ami votre longue adresse Bitmessage, vous pouvez simplement lui dire d’envoyer un message à &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Obtenir votre propre adresse Bitmessage au sein de Namecoin est encore assez difficile).&lt;/p&gt;&lt;p&gt;Bitmessage peut soit utiliser directement namecoind soit exécuter une instance de nmcontrol.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="600"/>
        <source>Host:</source>
        <translation>Hôte :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="603"/>
        <source>Password:</source>
        <translation>Mot de passe :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="604"/>
        <source>Test</source>
        <translation>Test</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="605"/>
        <source>Connect to:</source>
        <translation>Connexion à :</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="606"/>
        <source>Namecoind</source>
        <translation>Namecoind</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="607"/>
        <source>NMControl</source>
        <translation>NMControl</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="608"/>
        <source>Namecoin integration</source>
        <translation>Intégration avec Namecoin</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="613"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;By default, if you send a message to someone and he is offline for more than two days, Bitmessage will send the message again after an additional two days. This will be continued with exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain number of days or months.&lt;/p&gt;&lt;p&gt;Leave these input fields blank for the default behavior. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Par défaut, si vous envoyez un message à quelqu’un et que cette personne est hors connexion pendant plus de deux jours, Bitmessage enverra le message de nouveau après des deux jours supplémentaires. Ceci sera continué avec reculement (backoff) exponentiel pour toujours; les messages seront réenvoyés après 5, 10, 20 jours etc. jusqu’à ce que le récepteur accuse leur réception. Ici vous pouvez changer ce comportement en faisant en sorte que Bitmessage renonce après un certain nombre de jours ou de mois.&lt;/p&gt; &lt;p&gt;Si vous souhaitez obtenir le comportement par défaut alors laissez vides ces champs de saisie. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="622"/>
        <source>Give up after</source>
        <translation>Abandonner après</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="623"/>
        <source>and</source>
        <translation>et</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="624"/>
        <source>days</source>
        <translation>jours</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="625"/>
        <source>months.</source>
        <translation>mois.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="626"/>
        <source>Resends Expire</source>
        <translation>Expiration des renvois automatiques</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="493"/>
        <source>Hide connection notifications</source>
        <translation>Cacher les notifications de connexion</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="528"/>
        <source>Maximum outbound connections: [0: none]</source>
        <translation>Connexions sortantes maximum: [0: aucune]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="591"/>
        <source>Hardware GPU acceleration (OpenCL):</source>
        <translation>Accélération matérielle GPU (OpenCL) :</translation>
    </message>
</context>
</TS>