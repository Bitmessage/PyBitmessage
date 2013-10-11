APP=pybitmessage
VERSION=0.4.1
RELEASE=1
ARCH_TYPE=`uname -m`
PREFIX?=/usr/local

all:
debug:
source:
	tar -cvf ../${APP}_${VERSION}.orig.tar ../${APP}-${VERSION} --exclude-vcs
	gzip -f9n ../${APP}_${VERSION}.orig.tar
install:
	mkdir -p ${DESTDIR}/usr
	mkdir -p ${DESTDIR}${PREFIX}
	mkdir -p ${DESTDIR}${PREFIX}/bin
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/man
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/man/man1
	install -m 644 man/${APP}.1.gz ${DESTDIR}${PREFIX}/share/man/man1
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/${APP}
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/applications
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/pixmaps
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/icons
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/icons/hicolor
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/icons/hicolor/scalable
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/icons/hicolor/scalable/apps
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/icons/hicolor/24x24
	mkdir -m 755 -p ${DESTDIR}${PREFIX}/share/icons/hicolor/24x24/apps
	install -m 644 desktop/${APP}.desktop ${DESTDIR}${PREFIX}/share/applications/${APP}.desktop
	install -m 644 desktop/icon24.png ${DESTDIR}${PREFIX}/share/icons/hicolor/24x24/apps/${APP}.png
	cp -rf src/* ${DESTDIR}${PREFIX}/share/${APP}
	echo '#!/bin/sh' > ${DESTDIR}${PREFIX}/bin/${APP}
	echo 'if [ -d /usr/local/share/${APP} ]; then' >> ${DESTDIR}${PREFIX}/bin/${APP}
	echo '  cd /usr/local/share/${APP}' >> ${DESTDIR}${PREFIX}/bin/${APP}
	echo 'else' >> ${DESTDIR}${PREFIX}/bin/${APP}
	echo '  cd /usr/share/pybitmessage' >> ${DESTDIR}${PREFIX}/bin/${APP}
	echo 'fi' >> ${DESTDIR}${PREFIX}/bin/${APP}
	echo 'LD_LIBRARY_PATH="/opt/openssl-compat-bitcoin/lib/" exec python2 bitmessagemain.py' >> ${DESTDIR}${PREFIX}/bin/${APP}
	chmod +x ${DESTDIR}${PREFIX}/bin/${APP}
uninstall:
	rm -f ${PREFIX}/share/man/man1/${APP}.1.gz
	rm -rf ${PREFIX}/share/${APP}
	rm -f ${PREFIX}/bin/${APP}
	rm -f ${PREFIX}/share/applications/${APP}.desktop
	rm -f ${PREFIX}/share/icons/hicolor/scalable/apps/${APP}.svg
	rm -f ${PREFIX}/share/pixmaps/${APP}.svg
clean:
	rm -f ${APP} \#* \.#* gnuplot* *.png debian/*.substvars debian/*.log
	rm -fr deb.* debian/${APP} rpmpackage/${ARCH_TYPE}
	rm -f ../${APP}*.deb ../${APP}*.changes ../${APP}*.asc ../${APP}*.dsc
	rm -f rpmpackage/*.src.rpm archpackage/*.gz archpackage/*.xz
	rm -f puppypackage/*.gz puppypackage/*.pet slackpackage/*.txz
