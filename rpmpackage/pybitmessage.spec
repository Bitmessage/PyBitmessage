Name: pybitmessage
Version: 0.6.0
Release: 1%{?dist}
Summary: Send encrypted messages
License: MIT
URL: https://github.com/Bitmessage/PyBitmessage
Packager: Bob Mottram (4096 bits) <bob@robotics.uk.to>
Source0: http://yourdomainname.com/src/%{name}_%{version}.orig.tar.gz
BuildArch: noarch
Group: Office/Email

Requires: python, PyQt4, openssl-compat-bitcoin-libs, gst123


%description
Bitmessage is a P2P communications protocol used to send encrypted messages
to another person or to many subscribers. It is decentralized and
trustless, meaning that you need-not inherently trust any entities like
root certificate authorities. It uses strong authentication which means
that the sender of a message cannot be spoofed, and it aims to hide
"non-content" data, like the sender and receiver of messages, from passive
eavesdroppers like those running warrantless wiretapping programs.

%prep
%setup -q

%build
%configure
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
mkdir -p %{buildroot}/etc
mkdir -p %{buildroot}/etc/%{name}
mkdir -p %{buildroot}/usr
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share
mkdir -p %{buildroot}/usr/share/man
mkdir -p %{buildroot}/usr/share/man/man1
mkdir -p %{buildroot}/usr/share/%{name}
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons
mkdir -p %{buildroot}/usr/share/icons/hicolor
mkdir -p %{buildroot}/usr/share/icons/hicolor/24x24
mkdir -p %{buildroot}/usr/share/icons/hicolor/24x24/apps

mkdir -p %{buildroot}/usr/share/pixmaps
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps
# Make install but to the RPM BUILDROOT directory
make install -B DESTDIR=%{buildroot} PREFIX=/usr

%files
%doc README.md LICENSE
%defattr(-,root,root,-)
%dir /usr/share/%{name}
%dir /usr/share/applications
%dir /usr/share/icons/hicolor
%dir /usr/share/icons/hicolor/24x24
%dir /usr/share/icons/hicolor/24x24/apps
%dir /usr/share/pixmaps
%dir /usr/share/icons/hicolor/scalable
%dir /usr/share/icons/hicolor/scalable/apps
/usr/share/%{name}/*
%{_bindir}/*
%{_mandir}/man1/*
%attr(644,root,root) /usr/share/applications/%{name}.desktop
%attr(644,root,root) /usr/share/icons/hicolor/24x24/apps/%{name}.png

%changelog
* Sun Nov 2 2014 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.4.4-1
- Added ability to limit network transfer rate
- Updated to Protocol Version 3
- Removed use of memoryview so that we can support python 2.7.3
- Make use of l10n for localizations

* Thu Mar 6 2014 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.4.3-1
- Support pyelliptic's updated HMAC algorithm. We'll remove support for the old method after an upgrade period.
- Improved version check
- Refactored decodeBase58 function
- Ignore duplicate messages
- Added bytes received/sent counts and rate on the network information tab
- Fix unicode handling in 'View HTML code as formatted text'
- Refactor handling of packet headers
- Use pointMult function instead of arithmetic.privtopub since it is faster
- Fixed issue where client wasn't waiting for a verack before continuing on with the conversation
- Fixed CPU hogging by implementing tab-based refresh improvements
- Added curses interface
- Added support for IPv6
- Added a 'trustedpeer' option to keys.dat
- Limit maximum object size to 20 MB
- Support email-like > quote characters and reply-below-quote
- Added Japanese and Dutch language files; updated Norwegian and Russian languages files

* Thu Mar 6 2014 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.4.2-1
- Exclude debian directory from orig.tar.gz
- Added Norwegian, Chinese, and Arabic translations
- sock.sendall function isn't atomic.
  Let sendDataThread be the only thread which sends data.
- Moved API code to api.py
- Populate comboBoxSendFrom when replying
- Added option to show recent broadcasts when subscribing
- Fixed issue: If Windows username contained an international character,
  Bitmessage wouldn't start
- Added some code for FreeBSD compatibility
- Moved responsibility for processing network objects
  to the new ObjectProcessorThread
- Refactored main QT module
  Moved popup menus initialization to separate methods
  Simplified inbox loading
  Moved magic strings to the model scope constants so they won't
  be created every time.
- Updated list of defaultKnownNodes
- Fixed issue: [Linux] When too many messages arrive too quickly,
  exception occurs: "Exceeded maximum number of notifications"
- Fixed issue: creating then deleting an Address in short time crashes
  class_singleWorker.py
- Refactored code which displays messages to improve code readability
- load "Sent To" label from subscriptions if available
- Removed code to add chans to our address book as it is no longer necessary
- Added identicons
- Modified addresses.decodeAddress so that API command decodeAddress
  works properly
- Added API commands createChan, joinChan, leaveChan, deleteAddress
- In pyelliptic, check the return value of RAND_bytes to make sure enough
  random data was generated
- Don't store messages in UI table (and thus in memory), pull from SQL
  inventory as needed
- Fix typos in API commands addSubscription and getInboxMessagesByAddress
- Add feature in settings menu to give up resending a message after a
  specified period of time

* Sun Sep 29 2013 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.4.1-1
- Fixed whitelist bug
- Fixed chan bug
  Added addressversion field to pubkeys table
  Sending messages to a chan no longer uses anything in the pubkeys table
  Sending messages to yourself is now fully supported
- Change _verifyAddress function to support v4 addresses

* Sat Sep 28 2013 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.4.0-1
- Raised default demanded difficulty from 1 to 2 for new addresses
- Added v4 addresses:
  pubkeys are now encrypted and tagged in the inventory
- Use locks when accessing dictionary inventory
- Refactored the way inv and addr messages are shared
- Give user feedback when disk is full
- Added chan true/false to listAddresses results
- When replying using chan address, send to whole chan not just sender
- Refactored of the way PyBitmessage looks for interesting new objects
  in large inv messages from peers
- Show inventory lookup rate on Network Status tab
- Added SqlBulkExecute class
  so we can update inventory with only one commit
- Updated Russian translations
- Move duplicated SQL code into helper
- Allow specification of alternate settings dir
  via BITMESSAGE_HOME environment variable
- Removed use of gevent. Removed class_bgWorker.py
- Added Sip and PyQt to includes in build_osx.py
- Show number of each message type processed
  in the API command clientStatus
- Use fast PoW
  unless we're explicitly a frozen (binary) version of the code
- Enable user-set localization in settings
- Fix Archlinux package creation
- Fallback to language only localization when region doesn't match
- Fixed brew install instructions
- Added German translation
- Made inbox and sent messages table panels read-only
- Allow inbox and sent preview panels to resize
- Count RE: as a reply header, just like Re: so we don't chain Re: RE:
- Fix for traceback on OSX
- Added backend ability to understand shorter addresses
- Convert 'API Error' to raise APIError()
- Added option in settings to allow sending to a mobile device
  (app not yet done)
- Added ability to start daemon mode when using Bitmessage as a module
- Improved the way client detects locale
- Added API commands:
  getInboxMessageIds, getSentMessageIds, listAddressBookEntries,
  trashSentMessageByAckData, addAddressBookEntry,
  deleteAddressBookEntry, listAddresses2, listSubscriptions
- Set a maximum frequency for playing sounds
- Show Invalid Method error in same format as other API errors
- Update status of separate broadcasts separately
  even if the sent data is identical
- Added Namecoin integration
- Internally distinguish peers by IP and port
- Inbox message retrieval API
  functions now also returns read status

* Mon Jul 29 2013 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.3.5-1
- Inbox message retrieval API functions now also returns read status
- Added right-click option to mark a message as unread
- Prompt user to connect at first startup
- Install into /usr/local by default
- Add a missing rm -f to the uninstall task.
- Use system text color for enabled addresses instead of black
- Added support for Chans
- Start storing msgid in sent table
- Optionally play sounds on connection/disconnection or when messages arrive
- Adding configuration option to listen for connections when using SOCKS
- Added packaging for multiple distros (Arch, Puppy, Slack, etc.)
- Added Russian translation
- Added search support in the UI
- Added 'make uninstall'
- To improve OSX support, use PKCS5_PBKDF2_HMAC_SHA1
  if PKCS5_PBKDF2_HMAC is unavailable
- Added better warnings for OSX users who are using old versions of Python
- Repaired debian packaging
- Altered Makefile to avoid needing to chase changes
- Added logger module
- Added bgWorker class for background tasks
- Added use of gevent module
- On not-Windows: Fix insecure keyfile permissions
- Fix 100% CPU usage issue

* Sun Jun 30 2013 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.3.4-1
- Switched addr, msg, broadcast, and getpubkey message types
  to 8 byte time. Last remaining type is pubkey.
- Added tooltips to show the full subject of messages
- Added Maximum Acceptable Difficulty fields in the settings
- Send out pubkey immediately after generating deterministic
  addresses rather than waiting for a request

* Sat Jun 29 2013 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.3.3-1
- Remove inbox item from GUI when using API command trashMessage
- Add missing trailing semicolons to pybitmessage.desktop
- Ensure $(DESTDIR)/usr/bin exists
- Update Makefile to correct sandbox violations when built
  via Portage (Gentoo)
- Fix message authentication bug

* Fri Jun 28 2013 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.3.211-1
- Removed multi-core proof of work
  as the multiprocessing module does not work well with
  pyinstaller's --onefile option.

* Mon Jun 03 2013 Bob Mottram (4096 bits) <bob@robotics.uk.to> - 0.3.2-1
- Bugfix: Remove remaining references to the old myapp.trayIcon
- Refactored message status-related code. API function getStatus
  now returns one of these strings: notfound, msgqueued,
  broadcastqueued, broadcastsent, doingpubkeypow, awaitingpubkey,
  doingmsgpow, msgsent, or ackreceived
- Moved proof of work to low-priority multi-threaded child
  processes
- Added menu option to delete all trashed messages
- Added inv flooding attack mitigation
- On Linux, when selecting Show Bitmessage, do not maximize
  automatically
- Store tray icons in bitmessage_icons_rc.py

* Sat May 25 2013 Jonathan Warren (4096 bits) <jonathan@bitmessage.org> - 0.3.1-1
- Added new API commands: getDeterministicAddress,
  addSubscription, deleteSubscription
- TCP Connection timeout for non-fully-established connections
  now 20 seconds
- Don't update the time we last communicated with a node unless
  the connection is fully established. This will allow us to
  forget about active but non-Bitmessage nodes which have made
  it into our knownNodes file.
- Prevent incoming connection flooding from crashing
  singleListener thread. Client will now only accept one
  connection per remote node IP
- Bugfix: Worker thread crashed when doing a POW to send out
  a v2 pubkey (bug introduced in 0.3.0)
- Wrap all sock.shutdown functions in error handlers
- Put all 'commit' commands within SQLLocks
- Bugfix: If address book label is blank, Bitmessage wouldn't
  show message (bug introduced in 0.3.0)
- Messaging menu item selects the oldest unread message
- Standardize on 'Quit' rather than 'Exit'
- [OSX] Try to seek homebrew installation of OpenSSL
- Prevent multiple instances of the application from running
- Show 'Connected' or 'Connection Lost' indicators
- Use only 9 half-open connections on Windows but 32 for
  everyone else
- Added appIndicator (a more functional tray icon) and Ubuntu
  Messaging Menu integration
- Changed Debian install directory and run script name based
  on Github issue #135

* Mon May 6 2013 Bob Mottram (4096 bits) <bob@sluggish.dyndns.org> - 0.3.0-1
- Added new API function: getStatus
- Added error-handling around all sock.sendall() functions
  in the receiveData thread so that if there is a problem
  sending data, the threads will close gracefully
- Abandoned and removed the connectionsCount data structure;
  use the connectedHostsList instead because it has proved to be
  more accurate than trying to maintain the connectionsCount
- Added daemon mode. All UI code moved into a module and many
  shared objects moved into shared.py
- Truncate display of very long messages to avoid freezing the UI
- Added encrypted broadcasts for v3 addresses or v2 addresses
  after 2013-05-28 10:00 UTC
- No longer self.sock.close() from within receiveDataThreads,
  let the sendDataThreads do it
- Swapped out the v2 announcements subscription address for a v3
  announcements subscription address
- Vacuum the messages.dat file once a month:
  will greatly reduce the file size
- Added a settings table in message.dat
- Implemented v3 addresses:
  pubkey messages must now include two var_ints: nonce_trials_per_byte
  and extra_bytes, and also be signed. When sending a message to a v3
  address, the sender must use these values in calculating its POW or
  else the message will not be accepted by the receiver.
- Display a privacy warning when selecting 'Send Broadcast from this address'
- Added gitignore file
- Added code in preparation for a switch from 32-bit time to 64-bit time.
  Nodes will now advertise themselves as using protocol version 2.
- Don't necessarily delete entries from the inventory after 2.5 days;
  leave pubkeys there for 28 days so that we don't process the same ones
  many times throughout a month. This was causing the 'pubkeys processed'
  indicator on the 'Network Status' tab to not accurately reflect the
  number of truly new addresses on the network.
- Use 32 threads for outgoing connections in order to connect quickly
- Fix typo when calling os.environ in the sys.platform=='darwin' case
- Allow the cancelling of a message which is in the process of being
  sent by trashing it then restarting Bitmessage
- Bug fix: can't delete address from address book

* Tue Apr 9 2013 Bob Mottram (4096 bits) <bob@sluggish.dyndns.org> - 0.2.8-1
- Fixed Ubuntu & OS X issue:
  Bitmessage wouldn't receive any objects from peers after restart.
- Inventory flush to disk when exiting program now vastly faster.
- Fixed address generation bug (kept Bitmessage from restarting).
- Improve deserialization of messages
  before processing (a 'best practice').
- Change to help Macs find OpenSSL the way Unix systems find it.
- Do not share or accept IPs which are in the private IP ranges.
- Added time-fuzzing
  to the embedded time in pubkey and getpubkey messages.
- Added a knownNodes lock
  to prevent an exception from sometimes occurring when saving
  the data-structure to disk.
- Show unread messages in bold
  and do not display new messages automatically.
- Support selecting multiple items
  in the inbox, sent box, and address book.
- Use delete key to trash Inbox or Sent messages.
- Display richtext(HTML) messages
  from senders in address book or subscriptions (although not
  pseudo-mailing-lists; use new right-click option).
- Trim spaces
  from the beginning and end of addresses when adding to
  address book, subscriptions, and blacklist.
- Improved the display of the time for foreign language users.

* Mon Apr 1 2013 Bob Mottram (4096 bits) <bob@sluggish.dyndns.org> - 0.2.7-1
- Added debian packaging
- Script to generate debian packages
- SVG icon for Gnome shell, etc
- Source moved int src directory for debian standards compatibility
- Trailing carriage return on COPYING LICENSE and README.md
