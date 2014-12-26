#!/bin/bash
#Bitmessage/Mixmaster Tails Installer - 
#Installs Bitmessage on a persistent tails partition and, if necessary, installs mixmaster.
#Also configures Bitmessage so that message recipients whose address labels contain <> enclosed  
#email addresses are automatically sent anonymous notifications through mixmaster which say:
#"someone is trying to communicate with you on a safer channel" (subj: "spidey sense")
#Instructions: Boot the Tails operating system and enable persistence, then reboot, run this script, and reboot again.
#Warning: Do not run this script if you already have Bitmessage installed in ~/Persistent/PyBitmessage.
#Warning: We won't overwrite an existing keys.dat, but remember this script is not for reinstallation/upgrading/overwriting!


echo "Bitmessage/Mixmaster Tails Installer - "
echo "Installs Bitmessage on a persistent tails partition and, if necessary, installs mixmaster."
echo "Also configures Bitmessage so that message recipients whose address labels contain <> enclosed " 
echo "email addresses are automatically sent anonymous notifications through mixmaster which say:"
echo '"someone is trying to communicate with you on a safer channel" (subj: "spidey sense")' 
echo 
echo "#Instructions: Boot the Tails operating system and enable persistence, then reboot, run this script, and reboot again."
echo "#Warning: Do not run this script if you already have Bitmessage installed in ~/Persistent/PyBitmessage."
echo "#Warning: We won't overwrite an existing keys.dat, but remember this script is not for reinstallation/upgrading/overwriting!"
echo 
read -n 1 -p "Press any key to continue..."
echo

cd /live/persistence/TailsData_unlocked/ || exit

echo
echo "Checking/enabling Dotfiles and, if necessary, "
echo "checking/enabling APT Lists and APT Packages and installing mixmaster"
echo
sudo sh -c '
mkdir -p ./dotfiles/
chmod 700 ./dotfiles/
chown amnesia:amnesia ./dotfiles/
grep "/home/amnesia	source=dotfiles,link" ./persistence.conf >/dev/null 2>&1 || ( echo "/home/amnesia	source=dotfiles,link" >> ./persistence.conf; );
command -v mixmaster >/dev/null 2>&1 && ( echo "Mixmaster is already installed and we assume it works."; echo; );
command -v mixmaster >/dev/null 2>&1 || ( 
echo; echo "Installing mixmaster"; echo; 
grep mixmaster ./live-additional-software.conf >/dev/null 2>&1 || ( echo "mixmaster" >> ./live-additional-software.conf ); 
grep "/var/lib/apt/lists	source=apt/lists" ./persistence.conf >/dev/null 2>&1 && ( apt-get -y update; );
grep "/var/lib/apt/lists	source=apt/lists" ./persistence.conf >/dev/null 2>&1 || ( echo "/var/lib/apt/lists	source=apt/lists" >> ./persistence.conf; ); 
grep "/var/cache/apt/archives	source=apt/cache" ./persistence.conf >/dev/null 2>&1 && ( apt-get -y install mixmaster; );
grep "/var/cache/apt/archives	source=apt/cache" ./persistence.conf >/dev/null 2>&1 || ( echo "/var/cache/apt/archives	source=apt/cache" >> ./persistence.conf; );  
rm -r /home/amnesia/.Mix/ >/dev/null 2>&1
);
';

echo
echo "Installing Bitmessage"
echo
git clone https://github.com/p2pmessage/PyBitmessage /home/amnesia/Persistent/PyBitmessage/
if [ -f /home/amnesia/Persistent/PyBitmessage/keys.dat ]; then exit; fi;
cat <<EOT >> /home/amnesia/Persistent/PyBitmessage/keys.dat
[bitmessagesettings]
settingsversion = 10
port = 8444
timeformat = %%a, %%d %%b %%Y  %%I:%%M %%p
blackwhitelist = black
startonlogon = False
minimizetotray = False
showtraynotifications = True
startintray = False
socksproxytype = SOCKS5
sockshostname = localhost
socksport = 9150
socksauthentication = True
sockslisten = False
socksusername = bitmessage
sockspassword = bitmessage
keysencrypted = false
messagesencrypted = false
defaultnoncetrialsperbyte = 1000
defaultpayloadlengthextrabytes = 1000
minimizeonclose = false
maxacceptablenoncetrialsperbyte = 0
maxacceptablepayloadlengthextrabytes = 0
userlocale = system
useidenticons = True
identiconsuffix = PV7e9irDHhsy
replybelow = False
stopresendingafterxdays = 
stopresendingafterxmonths = 
namecoinrpctype = namecoind
namecoinrpchost = localhost
namecoinrpcuser = 
namecoinrpcpassword = 
namecoinrpcport = 8336
sendoutgoingconnections = True
maxdownloadrate = 0
maxuploadrate = 0
willinglysendtomobile = False
EOT

mkdir -p /live/persistence/TailsData_unlocked/dotfiles/.config/
cd /live/persistence/TailsData_unlocked/dotfiles/.config/

echo
echo "Creating file to autostart Bitmessage with Tor"
echo
mkdir -p ./autostart/
cat <<EOT > ./autostart/bitmessage_autostart.desktop
[Desktop Entry]
Name=Bitmessage
Type=Application
Terminal=false
Exec=bash -c "until sudo -n -u debian-tor /usr/local/sbin/tor-has-bootstrapped ; do sleep 5 ; done ; cd /home/amnesia/Persistent/PyBitmessage/ ; mixmaster-update & ./src/bitmessagemain.py"
Icon=/home/amnesia/Persistent/PyBitmessage/desktop/icon24.png
Comment[en_US.UTF-8]=Anonymous P2P Messenger
EOT
chmod 700 ./autostart/bitmessage_autostart.desktop

echo
echo "Creating file to replace Claws Mail with Bitmessage in top panel"
echo;
mkdir -p ./gnome-panel/
cat <<EOT > ./gnome-panel/bitmessage.desktop
[Desktop Entry]
Name=Bitmessage
Type=Application
Terminal=false
Exec=bash -c "cd /home/amnesia/Persistent/PyBitmessage/ ; mixmaster-update & ./src/bitmessagemain.py"
Icon=/home/amnesia/Persistent/PyBitmessage/desktop/icon24.png
Comment[en_US.UTF-8]=Anonymous P2P Messenger
EOT
chmod 700 ./gnome-panel/bitmessage.desktop
cp /home/amnesia/.config/gnome-panel/panel-default-layout.layout ./gnome-panel/
sed -i "s|\[Object claws-launcher\]|\[Object bitmessage-launcher\]|g" ./gnome-panel/panel-default-layout.layout
sed -i "s|@instance-config/location='/usr/share/applications/claws-mail\.desktop'|@instance-config/location='/live/persistence/TailsData_unlocked/dotfiles/\.config/gnome-panel/bitmessage\.desktop'|g" ./gnome-panel/panel-default-layout.layout

echo
echo "Installing persistent mixmaster config files for tails user, if necessary"
echo;
#To configure mixmaster as a Tails user create the directory /home/amnesia/.Mix/
mkdir /home/amnesia/.Mix/ || exit
#and populate it with a file called 
#"mix.cfg" that contains the line "SMTPRELAY	gbhpq7eihle4btsn.onion" and the location of mix node files
cat <<EOT > /home/amnesia/.Mix/mix.cfg
SMTPRELAY	gbhpq7eihle4btsn.onion
PGPREMPUBASC	/home/amnesia/.Mix/pubring.asc
PUBRING		/home/amnesia/.Mix/pubring.mix
TYPE1LIST	/home/amnesia/.Mix/rlist.txt
TYPE2REL	/home/amnesia/.Mix/mlist.txt
TYPE2LIST	/home/amnesia/.Mix/type2.list 
EOT
#and also with a file called
#"update.conf" that contains the lines "SOURCE	noreply" and "DESTINATION /home/amnesia/.Mix/"
cat <<EOT > /home/amnesia/.Mix/update.conf
SOURCE	noreply
DESTINATION	/home/amnesia/.Mix/
EOT
# and copy these files to make them persistent.
cp -r /home/amnesia/.Mix/ /live/persistence/TailsData_unlocked/dotfiles/.Mix/

read -n 1 -p "Please reboot to finish installation..."

