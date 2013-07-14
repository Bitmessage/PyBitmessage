Name: pybitmessage
Version: 0.3.4
Release: 1%{?dist}
Summary: Send encrypted messages
License: MIT
URL: https://github.com/Bitmessage/PyBitmessage
Packager: Bob Mottram (4096 bits) <bob@robotics.uk.to>
Source0: http://yourdomainname.com/src/%{name}_%{version}.orig.tar.gz
Group: Office/Email

Requires: python, PyQt4, openssl-compat-bitcoin-libs


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
make install -B DESTDIR=%{buildroot}

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

* Tue May 6 2013 Bob Mottram (4096 bits) <bob@sluggish.dyndns.org> - 0.3.0-1
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
- Vacuum the messages.dat file once a month: will greatly reduce the file size
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

* Tue Apr 1 2013 Bob Mottram (4096 bits) <bob@sluggish.dyndns.org> - 0.2.7-1
- Added debian packaging
- Script to generate debian packages
- SVG icon for Gnome shell, etc
- Source moved int src directory for debian standards compatibility
- Trailing carriage return on COPYING LICENSE and README.md
