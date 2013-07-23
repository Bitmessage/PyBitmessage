APP=pybitmessage
VERSION=0.3.4
RELEASE=1
ARCH_TYPE=`uname -m`

all:
debug:
source:
	tar -cvzf ../${APP}_${VERSION}.orig.tar.gz ../${APP}-${VERSION} --exclude-vcs
install:
	mkdir -p ${DESTDIR}/usr
	mkdir -p ${DESTDIR}/usr/bin
	mkdir -m 755 -p ${DESTDIR}/usr/share
	mkdir -m 755 -p ${DESTDIR}/usr/share/man
	mkdir -m 755 -p ${DESTDIR}/usr/share/man/man1
	install -m 644 man/${APP}.1.gz ${DESTDIR}/usr/share/man/man1
	mkdir -m 755 -p ${DESTDIR}/usr/share/${APP}
	mkdir -m 755 -p ${DESTDIR}/usr/share/applications
	mkdir -m 755 -p ${DESTDIR}/usr/share/pixmaps
	mkdir -m 755 -p ${DESTDIR}/usr/share/icons
	mkdir -m 755 -p ${DESTDIR}/usr/share/icons/hicolor
	mkdir -m 755 -p ${DESTDIR}/usr/share/icons/hicolor/scalable
	mkdir -m 755 -p ${DESTDIR}/usr/share/icons/hicolor/scalable/apps
	mkdir -m 755 -p ${DESTDIR}/usr/share/icons/hicolor/24x24
	mkdir -m 755 -p ${DESTDIR}/usr/share/icons/hicolor/24x24/apps
	install -m 644 desktop/${APP}.desktop ${DESTDIR}/usr/share/applications/${APP}.desktop
	install -m 644 desktop/icon24.png ${DESTDIR}/usr/share/icons/hicolor/24x24/apps/${APP}.png
	cp -rf src/* ${DESTDIR}/usr/share/${APP}
	echo '#!/bin/sh' > ${DESTDIR}/usr/bin/${APP}
	echo 'cd /usr/share/pybitmessage' >> ${DESTDIR}/usr/bin/${APP}
	echo 'LD_LIBRARY_PATH="/opt/openssl-compat-bitcoin/lib/" exec python2 bitmessagemain.py' >> ${DESTDIR}/usr/bin/${APP}
	chmod +x ${DESTDIR}/usr/bin/${APP}
uninstall:
	rm -f /usr/share/man/man1/${APP}.1.gz
	rm -rf /usr/share/${APP}
	rm -f /usr/bin/${APP}
	rm -f /usr/share/applications/${APP}.desktop
	rm -f /usr/share/icons/hicolor/scalable/apps/${APP}.svg
	rm -f /usr/share/pixmaps/${APP}.svg
clean:
	rm -f ${APP} \#* \.#* gnuplot* *.png debian/*.substvars debian/*.log
	rm -fr deb.* debian/${APP} rpmpackage/${ARCH_TYPE}
	rm -f ../${APP}*.deb ../${APP}*.changes ../${APP}*.asc ../${APP}*.dsc
	rm -f rpmpackage/*.src.rpm archpackage/*.gz archpackage/*.xz
	rm -f  puppypackage/*.gz puppypackage/*.pet slackpackage/*.txz
