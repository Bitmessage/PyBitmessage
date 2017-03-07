<?xml version="1.0" ?><!DOCTYPE TS><TS language="ru" sourcelanguage="en" version="2.0">
<context>
    <name>AddAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="62"/>
        <source>Add new entry</source>
        <translation>Добавить новую запись</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="63"/>
        <source>Label</source>
        <translation>Имя</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/addaddressdialog.py" line="64"/>
        <source>Address</source>
        <translation>Адрес</translation>
    </message>
</context>
<context>
    <name>EmailGatewayDialog</name>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="67"/>
        <source>Email gateway</source>
        <translation>Email-шлюз</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="68"/>
        <source>Register on email gateway</source>
        <translation>Зарегистрироваться на Email-шлюзе </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="69"/>
        <source>Account status at email gateway</source>
        <translation>Статус аккаунта Email-шлюза</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="70"/>
        <source>Change account settings at email gateway</source>
        <translation>Изменить настройки аккаунта Email-шлюза</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="71"/>
        <source>Unregister from email gateway</source>
        <translation>Отменить регистрацию на Email-шлюзе</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="72"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.</source>
        <translation>Email-шлюз позволяет вам обмениваться сообщениями с пользователями обычной электронной почты. В настоящий момент доступен только 1 шлюз Mailchuck (@mailchuck.com).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="73"/>
        <source>Desired email address (including @mailchuck.com):</source>
        <translation>Введите желаемый email-адрес (включая @mailchuck.com)</translation>
    </message>
</context>
<context>
    <name>EmailGatewayRegistrationDialog</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2262"/>
        <source>Registration failed:</source>
        <translation>Регистрация не удалась:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2262"/>
        <source>The requested email address is not available, please try a new one. Fill out the new desired email address (including @mailchuck.com) below:</source>
        <translation>Запрашиваемый адрес email недоступен, попробуйте ввести другой. Введите желаемый адрес (включая @mailchuck.com) ниже:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="102"/>
        <source>Email gateway registration</source>
        <translation>Регистрация на Email-шлюзе</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/emailgateway.py" line="103"/>
        <source>Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.
Please type the desired email address (including @mailchuck.com) below:</source>
        <translation>Email-шлюз позволяет вам обмениваться сообщениями с пользователями обычной электронной почты. В настоящий момент доступен только шлюз Mailchuck (@mailchuck.com).
Пожалуйста, введите желаемый адрес email (включая @mailchuck.com) ниже:</translation>
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
        <translation># Эти параметры можно использовать для настройки аккаунта email-шлюза
# Раскомментируйте (уберите символ #) те параметры, которые хотите использовать
# Параметры:
# 
# pgp: server
# Email-шлюз будет создавать и управлять PGP-ключами за вас, а также подписывать, проверять,
# шифровать и дешифровать от вашего имени. Используйте это, если вы желаете использовать PGP, но очень ленивы.
# Этот настройка требует подписки.
#
# pgp: local
# Шлюз электронной почты не будет проводить операции PGP от вашего имени. 
# Вы можете не использовать PGP, или использовать его локально.
#
# attachments: yes
# Вложения во входящий email-сообщениях будут загружены на MEGA.nz, 
# вы сможете скачать из оттуда по ссылке. Требуется подписка.
#
# attachments: no
# Вложения будут проигнорированы.
# 
# archive: yes
# Входящие email-сообщения будут заархивированы на сервере. Используйте эту настройку 
# в целях отладки, или если вам нужно подтверждение email третьей стороной.
# Конечно, это означает, что оператор сервиса будет иметь возможность читать ваши email
# даже после доставки их вам.
#
# archive: no
# Входящие email-сообщения будут удалены с сервера после доставки их вам.
#
# masterpubkey_btc: BIP44 xpub key или electrum v1 public seed
# offset_btc: целое число (по умолчанию 0)
# feeamount: число, содержащее до 8 десятичных цифр
# feecurrency: BTC, XBT, USD, EUR или GBP
# Используйте эту настроку, если хотите чтобы отправитель уплатил вознаграждение за отправку email вам.
# Если настройка включена, и неизвестный отправитель посылает вам email,
# то отправителю будет предложено уплатить указанное вознаграждение.
# Схема использует детерминистические открытые ключи, вы получите деньги напрямую. 
# Чтобы выключить уплату вознаграждения, установите  &quot;feeamount&quot; равным 0. 
# Требует подписки.</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="207"/>
        <source>Reply to sender</source>
        <translation>Ответить отправителю</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="209"/>
        <source>Reply to channel</source>
        <translation>Ответить в канал</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="211"/>
        <source>Add sender to your Address Book</source>
        <translation>Добавить отправителя в адресную книгу</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="215"/>
        <source>Add sender to your Blacklist</source>
        <translation>Добавить отправителя в чёрный список</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="397"/>
        <source>Move to Trash</source>
        <translation>Поместить в корзину</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="222"/>
        <source>Undelete</source>
        <translation>Отменить удаление</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="225"/>
        <source>View HTML code as formatted text</source>
        <translation>Просмотреть HTML код как отформатированный текст</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="229"/>
        <source>Save message as...</source>
        <translation>Сохранить сообщение как ...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="233"/>
        <source>Mark Unread</source>
        <translation>Отметить как непрочитанное</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="369"/>
        <source>New</source>
        <translation>Новый адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="121"/>
        <source>Enable</source>
        <translation>Включить</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="124"/>
        <source>Disable</source>
        <translation>Выключить</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="127"/>
        <source>Set avatar...</source>
        <translation>Установить аватар...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="117"/>
        <source>Copy address to clipboard</source>
        <translation>Скопировать адрес в буфер обмена</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="320"/>
        <source>Special address behavior...</source>
        <translation>Особое поведение адресов...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="281"/>
        <source>Email gateway</source>
        <translation>Email-шлюз</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="114"/>
        <source>Delete</source>
        <translation>Удалить</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="336"/>
        <source>Send message to this address</source>
        <translation>Отправить сообщение на этот адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="344"/>
        <source>Subscribe to this address</source>
        <translation>Подписаться на рассылку с этого адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="352"/>
        <source>Add New Address</source>
        <translation>Добавить новый адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="400"/>
        <source>Copy destination address to clipboard</source>
        <translation>Скопировать адрес отправки в буфер обмена</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="404"/>
        <source>Force send</source>
        <translation>Форсировать отправку</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="618"/>
        <source>One of your addresses, %1, is an old version 1 address. Version 1 addresses are no longer supported. May we delete it now?</source>
        <translation>Один из Ваших адресов, %1, является устаревшим адресом версии 1. Адреса версии 1 больше не поддерживаются. Хотите ли Вы удалить его сейчас?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1026"/>
        <source>Waiting for their encryption key. Will request it again soon.</source>
        <translation>Ожидаем ключ шифрования от Вашего собеседника. Запрос будет повторен через некоторое время.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="990"/>
        <source>Encryption key request queued.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1032"/>
        <source>Queued.</source>
        <translation>В очереди.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1035"/>
        <source>Message sent. Waiting for acknowledgement. Sent at %1</source>
        <translation>Сообщение отправлено. Ожидаем подтверждения. Отправлено в %1 </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1038"/>
        <source>Message sent. Sent at %1</source>
        <translation>Сообщение отправлено в %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1002"/>
        <source>Need to do work to send message. Work is queued.</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1044"/>
        <source>Acknowledgement of the message received %1</source>
        <translation>Сообщение доставлено в %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2131"/>
        <source>Broadcast queued.</source>
        <translation>Рассылка ожидает очереди.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1053"/>
        <source>Broadcast on %1</source>
        <translation>Рассылка на %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1056"/>
        <source>Problem: The work demanded by the recipient is more difficult than you are willing to do. %1</source>
        <translation>Проблема: Ваш получатель требует более сложных вычислений, чем максимум, указанный в Ваших настройках. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1059"/>
        <source>Problem: The recipient&apos;s encryption key is no good. Could not encrypt message. %1</source>
        <translation>Проблема: ключ получателя неправильный. Невозможно зашифровать сообщение. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1062"/>
        <source>Forced difficulty override. Send should start soon.</source>
        <translation>Форсирована смена сложности. Отправляем через некоторое время.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1065"/>
        <source>Unknown status: %1 %2</source>
        <translation>Неизвестный статус: %1 %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1683"/>
        <source>Not Connected</source>
        <translation>Не соединено</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1194"/>
        <source>Show Bitmessage</source>
        <translation>Показать Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="688"/>
        <source>Send</source>
        <translation>Отправить</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1209"/>
        <source>Subscribe</source>
        <translation>Подписки</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1215"/>
        <source>Channel</source>
        <translation>Канал</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="734"/>
        <source>Quit</source>
        <translation>Выйти</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1558"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file.</source>
        <translation>Вы можете управлять Вашими ключами, отредактировав файл keys.dat, находящийся в той же папке, что и эта программа. 
Создайте резервную копию этого файла перед тем как будете его редактировать.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1562"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file.</source>
        <translation>Вы можете управлять Вашими ключами, отредактировав файл keys.dat, находящийся в
 %1 
Создайте резервную копию этого файла перед тем как будете его редактировать.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1569"/>
        <source>Open keys.dat?</source>
        <translation>Открыть файл keys.dat?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1566"/>
        <source>You may manage your keys by editing the keys.dat file stored in the same directory as this program. It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Вы можете управлять Вашими ключами, отредактировав файл keys.dat, находящийся в той же папке, что и эта программа. 
Создайте резервную копию этого файла перед тем как будете его редактировать. Хотели бы Вы открыть этот файл сейчас? 
(пожалуйста, закройте Bitmessage до того как Вы внесёте в этот файл какие-либо изменения.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1569"/>
        <source>You may manage your keys by editing the keys.dat file stored in
 %1 
It is important that you back up this file. Would you like to open the file now? (Be sure to close Bitmessage before making any changes.)</source>
        <translation>Вы можете управлять Вашими ключами, отредактировав файл keys.dat, находящийся в
 %1 
Создайте резервную копию этого файла перед тем как будете его редактировать. Хотели бы Вы открыть этот файл сейчас? 
(пожалуйста, закройте Bitmessage до того как Вы внесёте в этот файл какие-либо изменения.)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1576"/>
        <source>Delete trash?</source>
        <translation>Очистить корзину?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1576"/>
        <source>Are you sure you want to delete all trashed messages?</source>
        <translation>Вы уверены что хотите очистить корзину?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1596"/>
        <source>bad passphrase</source>
        <translation>Неподходящая секретная фраза</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1596"/>
        <source>You must type your passphrase. If you don&apos;t have one then this is not the form for you.</source>
        <translation>Вы должны ввести секретную фразу. Если Вы не хотите этого делать, то Вы выбрали неправильную опцию.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1609"/>
        <source>Bad address version number</source>
        <translation>Неверный номер версии адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1605"/>
        <source>Your address version number must be a number: either 3 or 4.</source>
        <translation>Адрес номера версии должен быть числом: либо 3, либо 4.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1609"/>
        <source>Your address version number must be either 3 or 4.</source>
        <translation>Адрес номера версии должен быть либо 3, либо 4.</translation>
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
        <location filename="../bitmessageqt/__init__.py" line="1673"/>
        <source>Connection lost</source>
        <translation>Соединение потеряно</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1716"/>
        <source>Connected</source>
        <translation>Соединено</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1833"/>
        <source>Message trashed</source>
        <translation>Сообщение удалено</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1917"/>
        <source>The TTL, or Time-To-Live is the length of time that the network will hold the message.
 The recipient must get it during this time. If your Bitmessage client does not hear an acknowledgement, it
 will resend the message automatically. The longer the Time-To-Live, the
 more work your computer must do to send the message. A Time-To-Live of four or five days is often appropriate.</source>
        <translation>TTL или Time-To-Live (время жизни) это время, в течение которого сеть хранит ваше сообщение. 
Получатель должен получить сообщение в течение этого времени. Если ваш клиент Bitmessage не получит подтверждение доставки,
он переотправит сообщение автоматически. Чем больше TTL, тем больше расчётов ваш компьютер должен сделать, чтобы отправить
сообщение. Часто разумным вариантом будет установка TTL на 4 или 5 дней.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1955"/>
        <source>Message too long</source>
        <translation>Сообщение слишком длинное</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1955"/>
        <source>The message that you are trying to send is too long by %1 bytes. (The maximum is 261644 bytes). Please cut it down before sending.</source>
        <translation>Сообщение, которое вы пытаетесь отправить, длиннее максимально допустимого на %1 байт. (Максимально допустимое значение 261644 байта). Пожалуйста, сократите сообщение перед отправкой.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1987"/>
        <source>Error: Your account wasn&apos;t registered at an email gateway. Sending registration now as %1, please wait for the registration to be processed before retrying sending.</source>
        <translation>Ошибка: ваш аккаунт не зарегистрирован на Email-шлюзе. Отправка регистрации %1, пожалуйста, подождите пока процесс регистрации не завершится, прежде чем попытаться отправить сообщение заново.</translation>
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
        <location filename="../bitmessageqt/__init__.py" line="2089"/>
        <source>Error: You must specify a From address. If you don&apos;t have one, go to the &apos;Your Identities&apos; tab.</source>
        <translation>Вы должны указать адрес в поле &quot;От кого&quot;. Вы можете найти Ваш адрес во вкладке &quot;Ваши Адреса&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2030"/>
        <source>Address version number</source>
        <translation>Версия адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2030"/>
        <source>Concerning the address %1, Bitmessage cannot understand address version numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>По поводу адреса %1: Bitmessage не поддерживаем адреса версии %2. Возможно, Вам нужно обновить клиент Bitmessage.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2034"/>
        <source>Stream number</source>
        <translation>Номер потока</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2034"/>
        <source>Concerning the address %1, Bitmessage cannot handle stream numbers of %2. Perhaps upgrade Bitmessage to the latest version.</source>
        <translation>По поводу адреса %1: Bitmessage не поддерживаем стрим номер %2. Возможно, Вам нужно обновить клиент Bitmessage.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2039"/>
        <source>Warning: You are currently not connected. Bitmessage will do the work necessary to send the message but it won&apos;t send until you connect.</source>
        <translation>Внимание: Вы не подключены к сети. Bitmessage выполнит работу, требуемую для отправки сообщения, но не отправит его до тех пор, пока Вы не подключитесь.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2081"/>
        <source>Message queued.</source>
        <translation>Сообщение в очереди.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2085"/>
        <source>Your &apos;To&apos; field is empty.</source>
        <translation>Вы не заполнили поле &apos;Кому&apos;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2140"/>
        <source>Right click one or more entries in your address book and select &apos;Send message to this address&apos;.</source>
        <translation>Нажмите правую кнопку мыши на каком-либо адресе и выберите &quot;Отправить сообщение на этот адрес&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2153"/>
        <source>Fetched address from namecoin identity.</source>
        <translation>Получить адрес через Namecoin.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2256"/>
        <source>New Message</source>
        <translation>Новое сообщение</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2256"/>
        <source>From </source>
        <translation>От </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2636"/>
        <source>Sending email gateway registration request</source>
        <translation>Отправка запроса на регистрацию на Email-шлюзе</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="59"/>
        <source>Address is valid.</source>
        <translation>Адрес введен правильно.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="93"/>
        <source>The address you entered was invalid. Ignoring it.</source>
        <translation>Вы ввели неправильный адрес. Это адрес проигнорирован.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3075"/>
        <source>Error: You cannot add the same address to your address book twice. Try renaming the existing one if you want.</source>
        <translation>Ошибка: Вы не можете добавлять один и тот же адрес в Адресную Книгу несколько раз. Попробуйте переименовать существующий адрес.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3323"/>
        <source>Error: You cannot add the same address to your subscriptions twice. Perhaps rename the existing one if you want.</source>
        <translation>Ошибка: вы не можете добавить один и тот же адрес в ваши подписки дважды. Пожалуйста, переименуйте имеющийся адрес, если хотите.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2396"/>
        <source>Restart</source>
        <translation>Перезапустить</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2382"/>
        <source>You must restart Bitmessage for the port number change to take effect.</source>
        <translation>Вы должны перезапустить Bitmessage, чтобы смена номера порта имела эффект.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2396"/>
        <source>Bitmessage will use your proxy from now on but you may want to manually restart Bitmessage now to close existing connections (if any).</source>
        <translation>Bitmessage будет использовать Ваш прокси, начиная прямо сейчас. Тем не менее Вам имеет смысл перезапустить Bitmessage, чтобы закрыть уже существующие соединения.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2425"/>
        <source>Number needed</source>
        <translation>Требуется число</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2425"/>
        <source>Your maximum download and upload rate must be numbers. Ignoring what you typed.</source>
        <translation>Скорости загрузки и выгрузки должны быть числами. Игнорирую то, что вы набрали.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2505"/>
        <source>Will not resend ever</source>
        <translation>Не пересылать никогда</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2505"/>
        <source>Note that the time limit you entered is less than the amount of time Bitmessage waits for the first resend attempt therefore your messages will never be resent.</source>
        <translation>Обратите внимание, что лимит времени, который вы ввели, меньше чем время, которое Bitmessage ждет перед первой попыткой переотправки сообщения, поэтому ваши сообщения никогда не будут переотправлены.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2609"/>
        <source>Sending email gateway unregistration request</source>
        <translation>Отправка запроса на отмену регистрации на Email-шлюзе</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2613"/>
        <source>Sending email gateway status request</source>
        <translation>Отправка запроса статуса аккаунта на Email-шлюзе</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2713"/>
        <source>Passphrase mismatch</source>
        <translation>Секретная фраза не подходит</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2713"/>
        <source>The passphrase you entered twice doesn&apos;t match. Try again.</source>
        <translation>Вы ввели две разные секретные фразы. Пожалуйста, повторите заново.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2716"/>
        <source>Choose a passphrase</source>
        <translation>Придумайте секретную фразу</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2716"/>
        <source>You really do need a passphrase.</source>
        <translation>Вы действительно должны ввести секретную фразу.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3016"/>
        <source>Address is gone</source>
        <translation>Адрес утерян</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3016"/>
        <source>Bitmessage cannot find your address %1. Perhaps you removed it?</source>
        <translation>Bitmessage не может найти Ваш адрес %1. Возможно Вы удалили его?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3019"/>
        <source>Address disabled</source>
        <translation>Адрес выключен</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3019"/>
        <source>Error: The address from which you are trying to send is disabled. You&apos;ll have to enable it on the &apos;Your Identities&apos; tab before using it.</source>
        <translation>Ошибка: адрес, с которого Вы пытаетесь отправить, выключен. Вам нужно будет включить этот адрес во вкладке &quot;Ваши адреса&quot;.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3072"/>
        <source>Entry added to the Address Book. Edit the label to your liking.</source>
        <translation>Запись добавлена в Адресную Книгу. Вы можете её отредактировать.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3097"/>
        <source>Entry added to the blacklist. Edit the label to your liking.</source>
        <translation>Запись добавлена в чёрный список. Измените название по своему вкусу.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3100"/>
        <source>Error: You cannot add the same address to your blacklist twice. Try renaming the existing one if you want.</source>
        <translation>Ошибка: вы не можете добавить один и тот же адрес в чёрный список дважды. Попробуйте переименовать существующий адрес.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3228"/>
        <source>Moved items to trash.</source>
        <translation>Удалено в корзину.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3168"/>
        <source>Undeleted item.</source>
        <translation>Отменить удаление записи</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3196"/>
        <source>Save As...</source>
        <translation>Сохранить как ...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3205"/>
        <source>Write error.</source>
        <translation>Ошибка записи.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3309"/>
        <source>No addresses selected.</source>
        <translation>Вы не выбрали адрес.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3355"/>
        <source>If you delete the subscription, messages that you already received will become inaccessible. Maybe you can consider disabling the subscription instead. Disabled subscriptions will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the subscription?</source>
        <translation>Если вы отмените подписку, уже принятые сообщения станут недоступны! Возможно, вам стоит выключить подписку вместо ее отмены. Сообщения не приходят в отключенные подписки, но вы можете читать сообщения, которые уже приняты.

Вы уверены, что хотите отменить подписку?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3585"/>
        <source>If you delete the channel, messages that you already received will become inaccessible. Maybe you can consider disabling the channel instead. Disabled channels will not receive new messages, but you can still view messages you already received.

Are you sure you want to delete the channel?</source>
        <translation>Если вы удалите канал, уже принятые сообщения станут недоступны! Возможно, вам стоит выключить канал вместо его удаления. Сообщения не приходят в отключенные каналы, но вы можете читать сообщения, которые уже были приняты.

Вы уверены, что хотите удалить канал?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3700"/>
        <source>Do you really want to remove this avatar?</source>
        <translation>Вы уверены, что хотите удалить этот аватар?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="3708"/>
        <source>You have already set an avatar for this address. Do you really want to overwrite it?</source>
        <translation>У вас уже есть аватар для этого адреса. Вы уверены, что хотите перезаписать аватар?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4109"/>
        <source>Start-on-login not yet supported on your OS.</source>
        <translation>Запуск программы при входе в систему ещё не поддерживается в вашей операционной системе.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4102"/>
        <source>Minimize-to-tray not yet supported on your OS.</source>
        <translation>Сворачивание в трей ещё не поддерживается в вашей операционной системе.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4105"/>
        <source>Tray notifications not yet supported on your OS.</source>
        <translation>Уведомления в трее ещё не поддерживаеются в вашей операционной системе.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4276"/>
        <source>Testing...</source>
        <translation>Проверяем...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4316"/>
        <source>This is a chan address. You cannot use it as a pseudo-mailing list.</source>
        <translation>Это адрес chan-а. Вы не можете его использовать как адрес рассылки.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4376"/>
        <source>The address should start with &apos;&apos;BM-&apos;&apos;</source>
        <translation>Адрес должен начинаться с &quot;BM-&quot;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4379"/>
        <source>The address is not typed or copied correctly (the checksum failed).</source>
        <translation>Адрес введен или скопирован неверно (контрольная сумма не сходится).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4382"/>
        <source>The version number of this address is higher than this software can support. Please upgrade Bitmessage.</source>
        <translation>Версия этого адреса более поздняя, чем Ваша программа. Пожалуйста, обновите программу Bitmessage.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4385"/>
        <source>The address contains invalid characters.</source>
        <translation>Адрес содержит запрещённые символы.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4388"/>
        <source>Some data encoded in the address is too short.</source>
        <translation>Данные, закодированные в адресе, слишком короткие.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4391"/>
        <source>Some data encoded in the address is too long.</source>
        <translation>Данные, закодированные в адресе, слишком длинные.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4394"/>
        <source>Some data encoded in the address is malformed.</source>
        <translation>Данные, закодированные в адресе, имеют неверный формат.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4368"/>
        <source>Enter an address above.</source>
        <translation>Введите адрес выше.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4400"/>
        <source>Address is an old type. We cannot display its past broadcasts.</source>
        <translation>Адрес старого типа. Мы не можем отобразить его прошлые рассылки.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4409"/>
        <source>There are no recent broadcasts from this address to display.</source>
        <translation>Нет недавних рассылок с этого адреса для отображения.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4443"/>
        <source>You are using TCP port %1. (This can be changed in the settings).</source>
        <translation>Вы используете TCP порт %1. (Его можно поменять в настройках).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="645"/>
        <source>Bitmessage</source>
        <translation>Bitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="646"/>
        <source>Identities</source>
        <translation>Адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="647"/>
        <source>New Identity</source>
        <translation>Создать новый адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="709"/>
        <source>Search</source>
        <translation>Поиск</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="710"/>
        <source>All</source>
        <translation>По всем полям</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="717"/>
        <source>To</source>
        <translation>Кому</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="719"/>
        <source>From</source>
        <translation>От кого</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="721"/>
        <source>Subject</source>
        <translation>Тема</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="714"/>
        <source>Message</source>
        <translation>Текст сообщения</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="723"/>
        <source>Received</source>
        <translation>Получено</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="663"/>
        <source>Messages</source>
        <translation>Сообщения</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="666"/>
        <source>Address book</source>
        <translation>Адресная книга</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="668"/>
        <source>Address</source>
        <translation>Адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="669"/>
        <source>Add Contact</source>
        <translation>Добавить контакт</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="670"/>
        <source>Fetch Namecoin ID</source>
        <translation>Получить Namecoin ID</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="677"/>
        <source>Subject:</source>
        <translation>Тема:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="676"/>
        <source>From:</source>
        <translation>От:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="673"/>
        <source>To:</source>
        <translation>Кому:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="675"/>
        <source>Send ordinary Message</source>
        <translation>Отправить обычное сообщение</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="679"/>
        <source>Send Message to your Subscribers</source>
        <translation>Отправить сообщение для ваших подписчиков</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="680"/>
        <source>TTL:</source>
        <translation>TTL:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="706"/>
        <source>Subscriptions</source>
        <translation>Подписки</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="690"/>
        <source>Add new Subscription</source>
        <translation>Добавить новую подписку</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="724"/>
        <source>Chans</source>
        <translation>Чаны</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="708"/>
        <source>Add Chan</source>
        <translation>Добавить чан</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="729"/>
        <source>File</source>
        <translation>Файл</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="740"/>
        <source>Settings</source>
        <translation>Настройки</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="736"/>
        <source>Help</source>
        <translation>Помощь</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="732"/>
        <source>Import keys</source>
        <translation>Импортировать ключи</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="733"/>
        <source>Manage keys</source>
        <translation>Управлять ключами</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="735"/>
        <source>Ctrl+Q</source>
        <translation>Ctrl+Q</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="737"/>
        <source>F1</source>
        <translation>F1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="738"/>
        <source>Contact support</source>
        <translation>Связаться с поддержкой</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="739"/>
        <source>About</source>
        <translation>О программе</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="741"/>
        <source>Regenerate deterministic addresses</source>
        <translation>Сгенерировать заново все адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="742"/>
        <source>Delete all trashed messages</source>
        <translation>Стереть все сообщения из корзины</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="743"/>
        <source>Join / Create chan</source>
        <translation>Подключить или создать чан</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/foldertree.py" line="172"/>
        <source>All accounts</source>
        <translation>Все аккаунты</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="47"/>
        <source>Zoom level %1%</source>
        <translation>Увеличение %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="90"/>
        <source>Error: You cannot add the same address to your list twice. Perhaps rename the existing one if you want.</source>
        <translation>Ошибка: вы не можете добавить один и тот же адрес в ваш лист дважды. Попробуйте переименовать существующий адрес.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="111"/>
        <source>Add new entry</source>
        <translation>Добавить новую запись</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="4413"/>
        <source>Display the %1 recent broadcast(s) from this address.</source>
        <translation>Показать %1 прошлых рассылок с этого адреса.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1842"/>
        <source>New version of PyBitmessage is available: %1. Download it from https://github.com/Bitmessage/PyBitmessage/releases/latest</source>
        <translation>Доступна новая версия PyBitmessage: %1. Загрузите её:  https://github.com/Bitmessage/PyBitmessage/releases/latest</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2809"/>
        <source>Waiting for PoW to finish... %1%</source>
        <translation>Ожидание окончания PoW... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2813"/>
        <source>Shutting down Pybitmessage... %1%</source>
        <translation>Завершение PyBitmessage... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2824"/>
        <source>Waiting for objects to be sent... %1%</source>
        <translation>Ожидание отправки объектов... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2834"/>
        <source>Saving settings... %1%</source>
        <translation>Сохранение настроек... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2843"/>
        <source>Shutting down core... %1%</source>
        <translation>Завершение работы ядра... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2846"/>
        <source>Stopping notifications... %1%</source>
        <translation>Остановка сервиса уведомлений... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2852"/>
        <source>Shutdown imminent... %1%</source>
        <translation>Завершение вот-вот произойдет... %1%</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/bitmessageui.py" line="686"/>
        <source>%n hour(s)</source>
        <translation><numerusform>%n час</numerusform><numerusform>%n часа</numerusform><numerusform>%n часов</numerusform><numerusform>%n час(а/ов)</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="855"/>
        <source>%n day(s)</source>
        <translation><numerusform>%n день</numerusform><numerusform>%n дня</numerusform><numerusform>%n дней</numerusform><numerusform>%n дней</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2781"/>
        <source>Shutting down PyBitmessage... %1%</source>
        <translation>Завершение PyBitmessage... %1%</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1139"/>
        <source>Sent</source>
        <translation>Отправленные</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="91"/>
        <source>Generating one new address</source>
        <translation>Создание одного нового адреса</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="153"/>
        <source>Done generating address. Doing work necessary to broadcast it...</source>
        <translation>Создание адреса завершено. Выполнение работы, требуемой для его рассылки...</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="170"/>
        <source>Generating %1 new addresses.</source>
        <translation>Создание %1 новых адресов.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="247"/>
        <source>%1 is already in &apos;Your Identities&apos;. Not adding it again.</source>
        <translation>%1 уже имеется в ваших адресах. Не добавляю его снова.</translation>
    </message>
    <message>
        <location filename="../class_addressGenerator.py" line="283"/>
        <source>Done generating address</source>
        <translation>Создание адресов завершено.</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="228"/>
        <source>SOCKS5 Authentication problem: %1</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="584"/>
        <source>Disk full</source>
        <translation>Диск переполнен</translation>
    </message>
    <message>
        <location filename="../class_sqlThread.py" line="584"/>
        <source>Alert: Your disk or data storage volume is full. Bitmessage will now exit.</source>
        <translation>Внимание: свободное место на диске закончилось. Bitmessage завершит свою работу.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="740"/>
        <source>Error! Could not find sender address (your address) in the keys.dat file.</source>
        <translation>Ошибка: невозможно найти адрес отправителя (ваш адрес) в файле ключей keys.dat</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="487"/>
        <source>Doing work necessary to send broadcast...</source>
        <translation>Выполнение работы, требуемой для рассылки...</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="511"/>
        <source>Broadcast sent on %1</source>
        <translation>Рассылка отправлена на %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="580"/>
        <source>Encryption key was requested earlier.</source>
        <translation>Ключ шифрования запрошен ранее.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="617"/>
        <source>Sending a request for the recipient&apos;s encryption key.</source>
        <translation>Отправка запроса ключа шифрования получателя.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="632"/>
        <source>Looking up the receiver&apos;s public key</source>
        <translation>Поиск открытого ключа получателя</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="666"/>
        <source>Problem: Destination is a mobile device who requests that the destination be included in the message but this is disallowed in your settings.  %1</source>
        <translation>Проблема: адресат является мобильным устройством, которое требует, чтобы адрес назначения был включен в сообщение, однако, это запрещено в ваших настройках. %1</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="680"/>
        <source>Doing work necessary to send message.
There is no required difficulty for version 2 addresses like this.</source>
        <translation>Выполнение работы, требуемой для отправки сообщения.
Для адреса версии 2 (как этот), не требуется указание сложности.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="694"/>
        <source>Doing work necessary to send message.
Receiver&apos;s required difficulty: %1 and %2</source>
        <translation>Выполнение работы, требуемой для отправки сообщения.
Получатель запросил сложность: %1 и %2</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="703"/>
        <source>Problem: The work demanded by the recipient (%1 and %2) is more difficult than you are willing to do. %3</source>
        <translation>Проблема: сложность, затребованная получателем (%1 и %2) гораздо больше, чем вы готовы сделать. %3</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="715"/>
        <source>Problem: You are trying to send a message to yourself or a chan but your encryption key could not be found in the keys.dat file. Could not encrypt message. %1</source>
        <translation>Проблема: вы пытаетесь отправить сообщение самому себе или в чан, но ваш ключ шифрования не найден в файле ключей keys.dat. Невозможно зашифровать сообщение. %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1041"/>
        <source>Doing work necessary to send message.</source>
        <translation>Выполнение работы, требуемой для отправки сообщения.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="838"/>
        <source>Message sent. Waiting for acknowledgement. Sent on %1</source>
        <translation>Сообщение отправлено. Ожидаем подтверждения. Отправлено на %1 </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1029"/>
        <source>Doing work necessary to request encryption key.</source>
        <translation>Выполнение работы, требуемой для запроса ключа шифрования.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="956"/>
        <source>Broadcasting the public key request. This program will auto-retry if they are offline.</source>
        <translation>Рассылка запросов открытого ключа шифрования. Программа будет повторять попытки, если они оффлайн.</translation>
    </message>
    <message>
        <location filename="../class_singleWorker.py" line="958"/>
        <source>Sending public key request. Waiting for reply. Requested at %1</source>
        <translation>Отправка запроса открытого ключа шифрования. Ожидание ответа. Запрошено в %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="224"/>
        <source>UPnP port mapping established on port %1</source>
        <translation>Распределение портов UPnP завершилось выделением порта %1</translation>
    </message>
    <message>
        <location filename="../upnp.py" line="253"/>
        <source>UPnP port mapping removed</source>
        <translation>Распределение портов UPnP отменено</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="285"/>
        <source>Mark all messages as read</source>
        <translation>Отметить все сообщения как прочтенные</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2655"/>
        <source>Are you sure you would like to mark all messages read?</source>
        <translation>Вы уверены, что хотите отметить все сообщения как прочтенные?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1050"/>
        <source>Doing work necessary to send broadcast.</source>
        <translation>Выполнение работы, требуемой для отправки рассылки.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2748"/>
        <source>Proof of work pending</source>
        <translation>Ожидается доказательство работы</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2748"/>
        <source>%n object(s) pending proof of work</source>
        <translation><numerusform>%n объект в ожидании доказательства работы</numerusform><numerusform>%n объекта в ожидании доказательства работы</numerusform><numerusform>%n объектов в ожидании доказательства работы</numerusform><numerusform>%n объектов в ожидании доказательства работы</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2748"/>
        <source>%n object(s) waiting to be distributed</source>
        <translation><numerusform>%n объект ожидает раздачи</numerusform><numerusform>%n объекта ожидают раздачи</numerusform><numerusform>%n объектов ожидают раздачи</numerusform><numerusform>%n объектов ожидают раздачи</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2748"/>
        <source>Wait until these tasks finish?</source>
        <translation>Подождать завершения этих задач?</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="214"/>
        <source>Problem communicating with proxy: %1. Please check your network settings.</source>
        <translation>Проблема коммуникации с прокси: %1. Пожалуйста, проверьте ваши сетевые настройки.</translation>
    </message>
    <message>
        <location filename="../class_outgoingSynSender.py" line="243"/>
        <source>SOCKS5 Authentication problem: %1. Please check your SOCKS5 settings.</source>
        <translation>Проблема аутентификации SOCKS5: %1. Пожалуйста, проверьте настройки SOCKS5.</translation>
    </message>
    <message>
        <location filename="../class_receiveDataThread.py" line="173"/>
        <source>The time on your computer, %1, may be wrong. Please verify your settings.</source>
        <translation>Время на компьютере, %1, возможно неправильное. Пожалуйста, проверьте ваши настройки.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="101"/>
        <source>The name %1 was not found.</source>
        <translation>Имя %1  не найдено.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="110"/>
        <source>The namecoin query failed (%1)</source>
        <translation>Запрос к namecoin не удался (%1).</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="113"/>
        <source>The namecoin query failed.</source>
        <translation>Запрос к namecoin не удался.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="119"/>
        <source>The name %1 has no valid JSON data.</source>
        <translation>Имя %1 не содержит корректных данных JSON.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="127"/>
        <source>The name %1 has no associated Bitmessage address.</source>
        <translation>Имя %1 не имеет связанного адреса Bitmessage.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="147"/>
        <source>Success!  Namecoind version %1 running.</source>
        <translation>Успех! Namecoind версии %1 работает.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="153"/>
        <source>Success!  NMControll is up and running.</source>
        <translation>Успех!  NMControl запущен и работает.</translation>
    </message>
    <message>
        <location filename="../namecoin.py" line="156"/>
        <source>Couldn&apos;t understand NMControl.</source>
        <translation>Не удалось разобрать ответ NMControl.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="118"/>
        <source>Your GPU(s) did not calculate correctly, disabling OpenCL. Please report to the developers.</source>
        <translation>Ваша видеокарта вычислила неправильно, отключаем OpenCL. Пожалуйста, сообщите разработчикам.</translation>
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
Добро пожаловать в простой и безопасный Bitmessage
* отправляйте сообщения другим людям
* вещайте, как в twitter или
* участвуйте в обсуждениях в чанах</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="846"/>
        <source>not recommended for chans</source>
        <translation>не рекомендовано для чанов</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="1678"/>
        <source>Problems connecting? Try enabling UPnP in the Network Settings</source>
        <translation>Проблемы подключения? Попробуйте включить UPnP в сетевых настройках.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2000"/>
        <source>Error: Bitmessage addresses start with BM-   Please check the recipient address %1</source>
        <translation>Ошибка: адреса Bitmessage начинаются с &quot;BM-&quot;. Пожалуйста, проверьте адрес получателя %1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2003"/>
        <source>Error: The recipient address %1 is not typed or copied correctly. Please check it.</source>
        <translation>Ошибка: адрес получателя %1 набран или скопирован неправильно. Пожалуйста, проверьте его.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2006"/>
        <source>Error: The recipient address %1 contains invalid characters. Please check it.</source>
        <translation>Ошибка: адрес получателя %1 содержит недопустимые символы. Пожалуйста, проверьте его.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2009"/>
        <source>Error: The version of the recipient address %1 is too high. Either you need to upgrade your Bitmessage software or your acquaintance is being clever.</source>
        <translation>Ошибка: версия адреса получателя %1 слишком высокая. Либо вам нужно обновить программу Bitmessage, либо ваш знакомый - умник.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2012"/>
        <source>Error: Some data encoded in the recipient address %1 is too short. There might be something wrong with the software of your acquaintance.</source>
        <translation>Ошибка: часть данных, закодированных в адресе получателя %1 слишком короткая. Видимо, что-то не так с программой, используемой вашим знакомым.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2015"/>
        <source>Error: Some data encoded in the recipient address %1 is too long. There might be something wrong with the software of your acquaintance.</source>
        <translation>Ошибка: часть данных, закодированных в адресе получателя %1 слишком длинная. Видимо, что-то не так с программой, используемой вашим знакомым.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2018"/>
        <source>Error: Some data encoded in the recipient address %1 is malformed. There might be something wrong with the software of your acquaintance.</source>
        <translation>Ошибка: часть данных, закодированных в адресе получателя %1 сформирована неправильно. Видимо, что-то не так с программой, используемой вашим знакомым.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2021"/>
        <source>Error: Something is wrong with the recipient address %1.</source>
        <translation>Ошибка: что-то не так с адресом получателя %1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2759"/>
        <source>Synchronisation pending</source>
        <translation>Ожидается синхронизация</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/__init__.py" line="2759"/>
        <source>Bitmessage hasn&apos;t synchronised with the network, %n object(s) to be downloaded. If you quit now, it may cause delivery delays. Wait until the synchronisation finishes?</source>
        <translation><numerusform>Bitmessage не синхронизирован с сетью, незагруженных объектов: %n. Выход сейчас может привести к задержкам доставки. Подождать завершения синхронизации?</numerusform><numerusform>Bitmessage не синхронизирован с сетью, незагруженных объектов: %n. Выход сейчас может привести к задержкам доставки. Подождать завершения синхронизации?</numerusform><numerusform>Bitmessage не синхронизирован с сетью, незагруженных объектов: %n. Выход сейчас может привести к задержкам доставки. Подождать завершения синхронизации?</numerusform><numerusform>Bitmessage не синхронизирован с сетью, незагруженных объектов: %n. Выход сейчас может привести к задержкам доставки. Подождать завершения синхронизации?</numerusform></translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2770"/>
        <source>Not connected</source>
        <translation>Не подключено</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2770"/>
        <source>Bitmessage isn&apos;t connected to the network. If you quit now, it may cause delivery delays. Wait until connected and the synchronisation finishes?</source>
        <translation>Bitmessage не подключен к сети. Выход сейчас может привести к задержкам доставки. Подождать подключения и завершения синхронизации?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2785"/>
        <source>Waiting for network connection...</source>
        <translation>Ожидание сетевого подключения...</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/__init__.py" line="2793"/>
        <source>Waiting for finishing synchronisation...</source>
        <translation>Ожидание окончания синхронизации...</translation>
    </message>
</context>
<context>
    <name>MessageView</name>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="67"/>
        <source>Follow external link</source>
        <translation>Перейти по внешней ссылке</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="67"/>
        <source>The link &quot;%1&quot; will open in a browser. It may be a security risk, it could de-anonymise you or download malicious data. Are you sure?</source>
        <translation>Ссылка &quot;%1&quot; откроется в браузере. Это может быть угрозой безопасности, например деанонимизировать вас или привести к скачиванию вредоносных данных. Вы уверены?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="112"/>
        <source>HTML detected, click here to display</source>
        <translation>Обнаружен HTML, нажмите здесь чтоб отобразить</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/messageview.py" line="121"/>
        <source>Click here to disable HTML</source>
        <translation>Нажмите здесь для отключения </translation>
    </message>
</context>
<context>
    <name>MsgDecode</name>
    <message>
        <location filename="../helper_msgcoding.py" line="61"/>
        <source>The message has an unknown encoding.
Perhaps you should upgrade Bitmessage.</source>
        <translation>Сообщение в неизвестной кодировке.
Возможно, вам следует обновить Bitmessage.</translation>
    </message>
    <message>
        <location filename="../helper_msgcoding.py" line="62"/>
        <source>Unknown encoding</source>
        <translation>Неизвестная кодировка</translation>
    </message>
</context>
<context>
    <name>NewAddressDialog</name>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="173"/>
        <source>Create new Address</source>
        <translation>Создать новый адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="174"/>
        <source>Here you may generate as many addresses as you like. Indeed, creating and abandoning addresses is encouraged. You may generate addresses by using either random numbers or by using a passphrase. If you use a passphrase, the address is called a &quot;deterministic&quot; address.
The &apos;Random Number&apos; option is selected by default but deterministic addresses have several pros and cons:</source>
        <translation>Здесь Вы сможете сгенерировать столько адресов сколько хотите. На самом деле, создание и выкидывание адресов даже поощряется. Вы можете сгенерировать адреса используя либо генератор случайных чисел, либо придумав секретную фразу. Если Вы используете секретную фразу, то адреса будут называться &quot;детерминистическими&quot;. Генератор случайных чисел выбран по умолчанию, однако детерминистические адреса имеют следующие плюсы и минусы по сравнению с ними:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="176"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Pros:&lt;br/&gt;&lt;/span&gt;You can recreate your addresses on any computer from memory. &lt;br/&gt;You need-not worry about backing up your keys.dat file as long as you can remember your passphrase. &lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Cons:&lt;br/&gt;&lt;/span&gt;You must remember (or write down) your passphrase if you expect to be able to recreate your keys if they are lost. &lt;br/&gt;You must remember the address version number and the stream number along with your passphrase. &lt;br/&gt;If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Плюсы:&lt;br/&gt;&lt;/span&gt;Вы сможете восстановить адрес по памяти на любом компьютере&lt;br/&gt;Вам не нужно беспокоиться о сохранении файла  keys.dat, если Вы запомнили секретную фразу&lt;br/&gt;&lt;span style=&quot; font-weight:600;&quot;&gt;Минусы:&lt;br/&gt;&lt;/span&gt;Вы должны запомнить (или записать) секретную фразу, если Вы хотите когда-либо восстановить Ваш адрес на другом компьютере &lt;br/&gt;Вы должны также запомнить версию адреса и номер потока вместе с секретной фразой&lt;br/&gt;Если Вы выберите слишком короткую секретную фразу, кто-нибудь в интернете сможет подобрать ключ и, как следствие, читать и отправлять от Вашего имени сообщения.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="177"/>
        <source>Use a random number generator to make an address</source>
        <translation>Использовать генератор случайных чисел для создания адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="178"/>
        <source>Use a passphrase to make addresses</source>
        <translation>Использовать секретную фразу для создания адресов</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="179"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Потратить несколько лишних минут, чтобы сделать адрес(а) короче на 1 или 2 символа</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="180"/>
        <source>Make deterministic addresses</source>
        <translation>Создать детерминистический адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="181"/>
        <source>Address version number: 4</source>
        <translation>Номер версии адреса: 4</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="182"/>
        <source>In addition to your passphrase, you must remember these numbers:</source>
        <translation>В дополнение к секретной фразе, Вам необходимо запомнить эти числа:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="183"/>
        <source>Passphrase</source>
        <translation>Придумайте секретную фразу</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="184"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Кол-во адресов, которые Вы хотите получить из секретной фразы:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="185"/>
        <source>Stream number: 1</source>
        <translation>Номер потока: 1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="186"/>
        <source>Retype passphrase</source>
        <translation>Повторите секретную фразу</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="187"/>
        <source>Randomly generate address</source>
        <translation>Сгенерировать случайный адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="188"/>
        <source>Label (not shown to anyone except you)</source>
        <translation>Имя (не показывается никому кроме Вас)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="189"/>
        <source>Use the most available stream</source>
        <translation>Использовать наиболее доступный поток</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="190"/>
        <source> (best if this is the first of many addresses you will create)</source>
        <translation> (выберите этот вариант если это лишь первый из многих адресов, которые Вы планируете создать)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="191"/>
        <source>Use the same stream as an existing address</source>
        <translation>Использовать тот же поток, что и указанный существующий адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newaddressdialog.py" line="192"/>
        <source>(saves you some bandwidth and processing power)</source>
        <translation>(немного сэкономит Вам пропускную способность сети и вычислительную мощь)</translation>
    </message>
</context>
<context>
    <name>NewSubscriptionDialog</name>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="65"/>
        <source>Add new entry</source>
        <translation>Добавить новую запись</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="66"/>
        <source>Label</source>
        <translation>Имя</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="67"/>
        <source>Address</source>
        <translation>Адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newsubscriptiondialog.py" line="68"/>
        <source>Enter an address above.</source>
        <translation>Введите адрес выше.</translation>
    </message>
</context>
<context>
    <name>SpecialAddressBehaviorDialog</name>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="59"/>
        <source>Special Address Behavior</source>
        <translation>Особое поведение адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="60"/>
        <source>Behave as a normal address</source>
        <translation>Вести себя как обычный адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="61"/>
        <source>Behave as a pseudo-mailing-list address</source>
        <translation>Вести себя как адрес псевдо-рассылки</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="62"/>
        <source>Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).</source>
        <translation>Почта, полученная на адрес псевдо-рассылки, будет автоматически разослана всем подписчикам (и поэтому будет доступна общей публике).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/specialaddressbehavior.py" line="63"/>
        <source>Name of the pseudo-mailing-list:</source>
        <translation>Имя псевдо-рассылки:</translation>
    </message>
</context>
<context>
    <name>aboutDialog</name>
    <message>
        <location filename="../bitmessageqt/about.py" line="68"/>
        <source>About</source>
        <translation>О программе</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="69"/>
        <source>PyBitmessage</source>
        <translation>PyBitmessage</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>version ?</source>
        <translation>версия ?</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="72"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Distributed under the MIT/X11 software license; see &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Программа распространяется в соответствии с лицензией MIT/X11; см. &lt;a href=&quot;http://www.opensource.org/licenses/mit-license.php&quot;&gt;&lt;span style=&quot; text-decoration: underline; color:#0000ff;&quot;&gt;http://www.opensource.org/licenses/mit-license.php&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="73"/>
        <source>This is Beta software.</source>
        <translation>Это бета версия программы.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="70"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright Â© 2012-2016 Jonathan Warren&lt;br/&gt;Copyright Â© 2013-2016 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/about.py" line="71"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Copyright &amp;copy; 2012-2016 Jonathan Warren&lt;br/&gt;Copyright &amp;copy; 2013-2016 The Bitmessage Developers&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Авторское право: &amp;copy; 2012-2016 Джонатан Уоррен&lt;br/&gt;Авторское право: &amp;copy; 2013-2016 Разработчики Bitmessage&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
</context>
<context>
    <name>blacklist</name>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="17"/>
        <source>Use a Blacklist (Allow all incoming messages except those on the Blacklist)</source>
        <translation>Использовать чёрный список (разрешить все входящие сообщения, кроме указанных в чёрном списке)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="27"/>
        <source>Use a Whitelist (Block all incoming messages except those on the Whitelist)</source>
        <translation>Использовать белый список (блокировать все входящие сообщения, кроме указанных в белом списке)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="34"/>
        <source>Add new entry</source>
        <translation>Добавить новую запись</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="85"/>
        <source>Name or Label</source>
        <translation>Имя</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.ui" line="90"/>
        <source>Address</source>
        <translation>Адрес</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="150"/>
        <source>Blacklist</source>
        <translation>Чёрный список</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/blacklist.py" line="152"/>
        <source>Whitelist</source>
        <translation>Белый список</translation>
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
        <translation>Bitmessage не будет соединяться ни с кем, пока Вы это не разрешите.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="58"/>
        <source>Connect now</source>
        <translation>Соединиться прямо сейчас</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/connect.py" line="59"/>
        <source>Let me configure special network settings first</source>
        <translation>Я хочу сперва настроить сетевые настройки</translation>
    </message>
</context>
<context>
    <name>helpDialog</name>
    <message>
        <location filename="../bitmessageqt/help.py" line="45"/>
        <source>Help</source>
        <translation>Помощь</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.py" line="46"/>
        <source>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</source>
        <translation>&lt;a href=&quot;https://bitmessage.org/wiki/PyBitmessage_Help&quot;&gt;https://bitmessage.org/wiki/PyBitmessage_Help&lt;/a&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/help.py" line="47"/>
        <source>As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:</source>
        <translation>Bitmessage - общественный проект. Вы можете найти подсказки и советы на Wiki-страничке Bitmessage:</translation>
    </message>
</context>
<context>
    <name>iconGlossaryDialog</name>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="82"/>
        <source>Icon Glossary</source>
        <translation>Описание значков</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="83"/>
        <source>You have no connections with other peers. </source>
        <translation>Нет соединения с другими участниками сети.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="84"/>
        <source>You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn&apos;t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.</source>
        <translation>На текущий момент Вы установили по-крайней мере одно исходящее соединение, но пока ни одного входящего. Ваш файрвол или маршрутизатор скорее всего не настроен на переброс входящих TCP соединений к Вашему компьютеру. Bitmessage будет прекрасно работать и без этого, но Вы могли бы помочь сети если бы разрешили и входящие соединения тоже. Это помогло бы Вам стать более важным узлом сети.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="85"/>
        <source>You are using TCP port ?. (This can be changed in the settings).</source>
        <translation>Вы используете TCP порт ?. (Его можно поменять в настройках).</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/iconglossary.py" line="86"/>
        <source>You do have connections with other peers and your firewall is correctly configured.</source>
        <translation>Вы установили соединение с другими участниками сети и ваш файрвол настроен правильно.</translation>
    </message>
</context>
<context>
    <name>networkstatus</name>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="39"/>
        <source>Total connections:</source>
        <translation>Всего соединений: </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="143"/>
        <source>Since startup:</source>
        <translation>С начала работы: </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="159"/>
        <source>Processed 0 person-to-person messages.</source>
        <translation>Обработано 0 сообщений.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="188"/>
        <source>Processed 0 public keys.</source>
        <translation>Обработано 0 открытых ключей.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="175"/>
        <source>Processed 0 broadcasts.</source>
        <translation>Обработано 0 рассылок.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="240"/>
        <source>Inventory lookups per second: 0</source>
        <translation>Поисков в каталоге в секунду: 0</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="201"/>
        <source>Objects to be synced:</source>
        <translation>Несинхронизированные объекты: </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="111"/>
        <source>Stream #</source>
        <translation>№ потока</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="116"/>
        <source>Connections</source>
        <translation>Соединений</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="132"/>
        <source>Since startup on %1</source>
        <translation>С начала работы в %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="70"/>
        <source>Down: %1/s  Total: %2</source>
        <translation>Загрузка: %1/s Всего: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="72"/>
        <source>Up: %1/s  Total: %2</source>
        <translation>Отправка: %1/s Всего: %2</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="115"/>
        <source>Total Connections: %1</source>
        <translation>Всего соединений: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.py" line="124"/>
        <source>Inventory lookups per second: %1</source>
        <translation>Поисков в каталоге в секунду: %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="214"/>
        <source>Up: 0 kB/s</source>
        <translation>Отправка: 0 кБ/с</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/networkstatus.ui" line="227"/>
        <source>Down: 0 kB/s</source>
        <translation>Загрузка: 0 кБ/с</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/bitmessageui.py" line="728"/>
        <source>Network Status</source>
        <translation>Состояние сети</translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="37"/>
        <source>byte(s)</source>
        <translation><numerusform>байт</numerusform><numerusform>байт</numerusform><numerusform>байт</numerusform><numerusform>байт</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="48"/>
        <source>Object(s) to be synced: %n</source>
        <translation><numerusform>Несинхронизированные объекты: %n</numerusform><numerusform>Несинхронизированные объекты: %n</numerusform><numerusform>Несинхронизированные объекты: %n</numerusform><numerusform>Несинхронизированные объекты: %n</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="52"/>
        <source>Processed %n person-to-person message(s).</source>
        <translation><numerusform>Обработано %n сообщение.</numerusform><numerusform>Обработано %n сообщений.</numerusform><numerusform>Обработано %n сообщений.</numerusform><numerusform>Обработано %n сообщений.</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="57"/>
        <source>Processed %n broadcast message(s).</source>
        <translation><numerusform>Обработана %n рассылка.</numerusform><numerusform>Обработано %n рассылок.</numerusform><numerusform>Обработано %n рассылок.</numerusform><numerusform>Обработано %n рассылок.</numerusform></translation>
    </message>
    <message numerus="yes">
        <location filename="../bitmessageqt/networkstatus.py" line="62"/>
        <source>Processed %n public key(s).</source>
        <translation><numerusform>Обработан %n открытый ключ.</numerusform><numerusform>Обработано %n открытых ключей.</numerusform><numerusform>Обработано %n открытых ключей.</numerusform><numerusform>Обработано %n открытых ключей.</numerusform></translation>
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
        <translation>Создать или подключить чан</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="41"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a message to the chan address.&lt;/p&gt;&lt;p&gt;Chans are experimental and completely unmoderatable.&lt;/p&gt;&lt;p&gt;Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly, then the chan will be secure and private. However if you and someone else both create a chan with the same chan name, the same chan will be shared.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Чан получается, когда группа людей использует общие ключи дешифрования. Ключи и адрес bitmessage, используемые чаном, генерируются из понятного слова или фразы (имя чана). Для отправки сообщения всем пользователям чана, нужно отправить его на адрес чана.&lt;/p&gt;&lt;p&gt;Чаны это экспериментальная  абсолютно немодерируемая среда.&lt;/p&gt;&lt;p&gt;Введите имя вашего чана. Если вы выберете достаточно сложное имя чана (как надежный и уникальный пароль) и никто из ваших друзей не обнародует его, чан будет безопасным и приватным. Однако, если кто-то создаст чан с таким-же именем, как ваш, то вы будете использовать общий чан.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="56"/>
        <source>Chan passhphrase/name:</source>
        <translation>Пароль/имя чана:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="63"/>
        <source>Optional, for advanced usage</source>
        <translation>Необязательно, для продвинутых пользователей</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="76"/>
        <source>Chan address</source>
        <translation>Адрес чана</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.ui" line="101"/>
        <source>Please input chan name/passphrase:</source>
        <translation>Пожалуйста, введите имя/пароль чана:</translation>
    </message>
</context>
<context>
    <name>newchandialog</name>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="40"/>
        <source>Successfully created / joined chan %1</source>
        <translation>Успешно создан / подключен чан %1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="44"/>
        <source>Chan creation / joining failed</source>
        <translation>Не удалось создать / подключить чан</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/newchandialog.py" line="50"/>
        <source>Chan creation / joining cancelled</source>
        <translation>Создание / подключение чана отменено</translation>
    </message>
</context>
<context>
    <name>proofofwork</name>
    <message>
        <location filename="../proofofwork.py" line="161"/>
        <source>C PoW module built successfully.</source>
        <translation>Модуль C для PoW успешно собран.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="163"/>
        <source>Failed to build C PoW module. Please build it manually.</source>
        <translation>Не удалось собрать модуль C для PoW. Пожалуйста, соберите его вручную.</translation>
    </message>
    <message>
        <location filename="../proofofwork.py" line="165"/>
        <source>C PoW module unavailable. Please build it.</source>
        <translation>Модуль C для PoW недоступен. Пожалуйста, соберите его.</translation>
    </message>
</context>
<context>
    <name>qrcodeDialog</name>
    <message>
        <location filename="../plugins/qrcodeui.py" line="67"/>
        <source>QR-code</source>
        <translation>QR-код</translation>
    </message>
</context>
<context>
    <name>regenerateAddressesDialog</name>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="114"/>
        <source>Regenerate Existing Addresses</source>
        <translation>Сгенерировать заново существующие адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="115"/>
        <source>Regenerate existing addresses</source>
        <translation>Сгенерировать заново существующие адреса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="116"/>
        <source>Passphrase</source>
        <translation>Секретная фраза</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="117"/>
        <source>Number of addresses to make based on your passphrase:</source>
        <translation>Кол-во адресов, которые Вы хотите получить из Вашей секретной фразы:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="118"/>
        <source>Address version number:</source>
        <translation>Номер версии адреса: </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="119"/>
        <source>Stream number:</source>
        <translation>Номер потока:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="120"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="121"/>
        <source>Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter</source>
        <translation>Потратить несколько лишних минут, чтобы сделать адрес(а) короче на 1 или 2 символа</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="122"/>
        <source>You must check (or not check) this box just like you did (or didn&apos;t) when you made your addresses the first time.</source>
        <translation>Вы должны отметить эту галочку (или не отмечать) точно так же, как Вы сделали (или не сделали) в самый первый раз, когда создавали Ваши адреса.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/regenerateaddresses.py" line="123"/>
        <source>If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.</source>
        <translation>Если Вы ранее создавали детерминистические адреса, но случайно потеряли их, Вы можете их восстановить здесь. Если же Вы использовали генератор случайных чисел чтобы создать Ваши адреса, то Вы не сможете их здесь восстановить.</translation>
    </message>
</context>
<context>
    <name>settingsDialog</name>
    <message>
        <location filename="../bitmessageqt/settings.py" line="453"/>
        <source>Settings</source>
        <translation>Настройки</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="454"/>
        <source>Start Bitmessage on user login</source>
        <translation>Запускать Bitmessage при входе в систему</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="455"/>
        <source>Tray</source>
        <translation>Трей</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="456"/>
        <source>Start Bitmessage in the tray (don&apos;t show main window)</source>
        <translation>Запускать Bitmessage в свернутом виде (не показывать главное окно)</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="457"/>
        <source>Minimize to tray</source>
        <translation>Сворачивать в трей</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="458"/>
        <source>Close to tray</source>
        <translation>Закрывать в трей</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="460"/>
        <source>Show notification when message received</source>
        <translation>Показывать уведомления при получении новых сообщений</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="461"/>
        <source>Run in Portable Mode</source>
        <translation>Запустить в переносном режиме</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="462"/>
        <source>In Portable Mode, messages and config files are stored in the same directory as the program rather than the normal application-data folder. This makes it convenient to run Bitmessage from a USB thumb drive.</source>
        <translation>В переносном режиме, все сообщения и конфигурационные файлы сохраняются в той же самой папке что и сама программа. Это делает более удобным использование Bitmessage с USB-флэшки.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="463"/>
        <source>Willingly include unencrypted destination address when sending to a mobile device</source>
        <translation>Специально прикреплять незашифрованный адрес получателя, когда посылаем на мобильное устройство</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="464"/>
        <source>Use Identicons</source>
        <translation>Включить иконки адресов</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="465"/>
        <source>Reply below Quote</source>
        <translation>Отвечать после цитаты</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="466"/>
        <source>Interface Language</source>
        <translation>Язык интерфейса</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="467"/>
        <source>System Settings</source>
        <comment>system</comment>
        <translation>Язык по умолчанию</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="468"/>
        <source>User Interface</source>
        <translation>Пользовательские</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="469"/>
        <source>Listening port</source>
        <translation>Порт прослушивания</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="470"/>
        <source>Listen for connections on port:</source>
        <translation>Прослушивать соединения на порту:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="471"/>
        <source>UPnP:</source>
        <translation>UPnP:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="472"/>
        <source>Bandwidth limit</source>
        <translation>Ограничение пропускной способности</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Maximum download rate (kB/s): [0: unlimited]</source>
        <translation>Максимальная скорость загрузки (кБ/с): [0: не ограничено]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="474"/>
        <source>Maximum upload rate (kB/s): [0: unlimited]</source>
        <translation>Максимальная скорость отдачи (кБ/с): [0: не ограничено]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="476"/>
        <source>Proxy server / Tor</source>
        <translation>Прокси сервер / Tor</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="477"/>
        <source>Type:</source>
        <translation>Тип:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="478"/>
        <source>Server hostname:</source>
        <translation>Адрес сервера:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="501"/>
        <source>Port:</source>
        <translation>Порт:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="480"/>
        <source>Authentication</source>
        <translation>Авторизация</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="502"/>
        <source>Username:</source>
        <translation>Имя пользователя:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="482"/>
        <source>Pass:</source>
        <translation>Пароль:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="483"/>
        <source>Listen for incoming connections when using proxy</source>
        <translation>Прослушивать входящие соединения если используется прокси</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="484"/>
        <source>none</source>
        <translation>отсутствует</translation>
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
        <translation>Сетевые настройки</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="488"/>
        <source>Total difficulty:</source>
        <translation>Общая сложность:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="489"/>
        <source>The &apos;Total difficulty&apos; affects the absolute amount of work the sender must complete. Doubling this value doubles the amount of work.</source>
        <translation>&quot;Общая сложность&quot; влияет на абсолютное количество вычислений, которые отправитель должен провести, чтобы отправить сообщение. Увеличив это число в два раза, вы увеличите в два раза объем требуемых вычислений.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="490"/>
        <source>Small message difficulty:</source>
        <translation>Сложность для маленьких сообщений:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="491"/>
        <source>When someone sends you a message, their computer must first complete some work. The difficulty of this work, by default, is 1. You may raise this default for new addresses you create by changing the values here. Any new addresses you create will require senders to meet the higher difficulty. There is one exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically notify them when you next send a message that they need only complete the minimum amount of work: difficulty 1. </source>
        <translation>Когда кто-либо отправляет Вам сообщение, его компьютер должен сперва решить определённую вычислительную задачу. Сложность этой задачи по умолчанию равна 1. Вы можете повысить эту сложность для новых адресов, которые Вы создадите, здесь. Таким образом, любые новые адреса, которые Вы создадите, могут требовать от отправителей сложность большую чем 1. Однако, есть одно исключение: если Вы специально добавите Вашего собеседника в адресную книгу, то Bitmessage автоматически уведомит его о том, что для него минимальная сложность будет составлять всегда всего лишь 1.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="492"/>
        <source>The &apos;Small message difficulty&apos; mostly only affects the difficulty of sending small messages. Doubling this value makes it almost twice as difficult to send a small message but doesn&apos;t really affect large messages.</source>
        <translation>&quot;Сложность для маленьких сообщений&quot; влияет исключительно на небольшие сообщения. Увеличив это число в два раза, вы сделаете отправку маленьких сообщений в два раза сложнее, в то время как сложность отправки больших сообщений не изменится.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="493"/>
        <source>Demanded difficulty</source>
        <translation>Требуемая сложность</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="494"/>
        <source>Here you may set the maximum amount of work you are willing to do to send a message to another person. Setting these values to 0 means that any value is acceptable.</source>
        <translation>Здесь Вы можете установить максимальную вычислительную работу, которую Вы согласны проделать, чтобы отправить сообщение другому пользователю. Ноль означает, что любое значение допустимо.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="495"/>
        <source>Maximum acceptable total difficulty:</source>
        <translation>Максимально допустимая общая сложность:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="496"/>
        <source>Maximum acceptable small message difficulty:</source>
        <translation>Максимально допустимая сложность для маленький сообщений:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="497"/>
        <source>Max acceptable difficulty</source>
        <translation>Макс допустимая сложность</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="473"/>
        <source>Hardware GPU acceleration (OpenCL)</source>
        <translation type="unfinished"/>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="499"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage can utilize a different Bitcoin-based program called Namecoin to make addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage address, you can simply tell him to send a message to &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Getting your own Bitmessage address into Namecoin is still rather difficult).&lt;/p&gt;&lt;p&gt;Bitmessage can use either namecoind directly or a running nmcontrol instance.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;Bitmessage умеет пользоваться программой Namecoin для того, чтобы сделать адреса более дружественными для пользователей. Например, вместо того, чтобы диктовать Вашему другу длинный и нудный адрес Bitmessage, Вы можете попросить его отправить сообщение на адрес вида &lt;span style=&quot; font-style:italic;&quot;&gt;test. &lt;/span&gt;&lt;/p&gt;&lt;p&gt;(Перенести Ваш Bitmessage адрес в Namecoin по-прежнему пока довольно сложно).&lt;/p&gt;&lt;p&gt;Bitmessage может использовать либо прямо namecoind, либо уже запущенную программу nmcontrol.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="500"/>
        <source>Host:</source>
        <translation>Адрес:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="503"/>
        <source>Password:</source>
        <translation>Пароль:</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="504"/>
        <source>Test</source>
        <translation>Проверить</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="505"/>
        <source>Connect to:</source>
        <translation>Подсоединиться к:</translation>
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
        <translation>Интеграция с Namecoin</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="509"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;By default, if you send a message to someone and he is offline for more than two days, Bitmessage will send the message again after an additional two days. This will be continued with exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain number of days or months.&lt;/p&gt;&lt;p&gt;Leave these input fields blank for the default behavior. &lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;По умолчанию, когда вы отправляете сообщение кому-либо, и адресат находится оффлайн несколько дней, ваш Bitmessage перепосылает сообщение. Это будет продолжаться с увеличивающимся по экспоненте интервалом; сообщение будет переотправляться, например, через 5, 10, 20 дней, пока адресат их запрашивает. Здесь вы можете изменить это поведение, заставив Bitmessage прекращать переотправку по прошествии указанного количества дней или месяцев.&lt;/p&gt;&lt;p&gt;Оставьте поля пустыми, чтобы вернуться к поведению по умолчанию.&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="510"/>
        <source>Give up after</source>
        <translation>Прекратить через </translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="511"/>
        <source>and</source>
        <translation>и</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="512"/>
        <source>days</source>
        <translation>дней</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="513"/>
        <source>months.</source>
        <translation>месяцев.</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="514"/>
        <source>Resends Expire</source>
        <translation>Окончание попыток отправки</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="459"/>
        <source>Hide connection notifications</source>
        <translation>Спрятать уведомления о подключениях</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="475"/>
        <source>Maximum outbound connections: [0: none]</source>
        <translation>Максимальное число исходящих подключений: [0: неограничено]</translation>
    </message>
    <message>
        <location filename="../bitmessageqt/settings.py" line="498"/>
        <source>Hardware GPU acceleration (OpenCL):</source>
        <translation>Аппаратное ускорение GPU</translation>
    </message>
</context>
</TS>