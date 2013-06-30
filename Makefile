APP=pybitmessage
VERSION=0.3.4
DEST_SHARE=${DESTDIR}/usr/share
DEST_APP=${DEST_SHARE}/${APP}

all:
 
debug:

source:
	tar -cvzf ../${APP}_${VERSION}.orig.tar.gz ../${APP}-${VERSION} --exclude-vcs

install:
	mkdir -m 755 -p ${DESTDIR}/usr/bin
	mkdir -m 755 -p ${DEST_APP}
	mkdir -m 755 -p ${DEST_SHARE}/applications
	mkdir -m 755 -p ${DEST_APP}/images
	mkdir -m 755 -p ${DEST_APP}/pyelliptic
	mkdir -m 755 -p ${DEST_APP}/socks
	mkdir -m 755 -p ${DEST_APP}/bitmessageqt
	mkdir -m 755 -p ${DEST_APP}/translations
	mkdir -m 755 -p ${DEST_SHARE}/pixmaps
	mkdir -m 755 -p ${DEST_SHARE}/icons
	mkdir -m 755 -p ${DEST_SHARE}/icons/hicolor
	mkdir -m 755 -p ${DEST_SHARE}/icons/hicolor/scalable
	mkdir -m 755 -p ${DEST_SHARE}/icons/hicolor/scalable/apps
	mkdir -m 755 -p ${DEST_SHARE}/icons/hicolor/24x24
	mkdir -m 755 -p ${DEST_SHARE}/icons/hicolor/24x24/apps

	cp -r src/* ${DEST_APP}
	install -m 755 debian/pybm ${DESTDIR}/usr/bin/${APP}

	install -m 644 desktop/${APP}.desktop ${DEST_SHARE}/applications/${APP}.desktop
	install -m 644 src/images/can-icon-24px.png ${DEST_SHARE}/icons/hicolor/24x24/apps/${APP}.png
	install -m 644 desktop/can-icon.svg ${DEST_SHARE}/icons/hicolor/scalable/apps/${APP}.svg
	install -m 644 desktop/can-icon.svg ${DEST_SHARE}/pixmaps/${APP}.svg

clean:
	rm -rf debian/${APP}
	rm -f ../${APP}_*.deb ../${APP}_*.asc ../${APP}_*.dsc ../${APP}*.changes
	rm -f *.sh~ src/*.pyc src/socks/*.pyc src/pyelliptic/*.pyc
	rm -f *.deb \#* \.#* debian/*.log debian/*.substvars
	rm -f Makefile~
