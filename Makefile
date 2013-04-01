APP=pybitmessage
VERSION=0.2.7

all:
 
debug:

source:
	tar -cvzf ../$(APP)_$(VERSION).orig.tar.gz ../$(APP)-$(VERSION) --exclude=.git

install:
	mkdir -m 755 -p /usr/share/applications
	mkdir -m 755 -p /usr/share/applications/$(APP)
	mkdir -m 755 -p /usr/share/applications/$(APP)/images
	mkdir -m 755 -p /usr/share/applications/$(APP)/pyelliptic
	mkdir -m 755 -p /usr/share/applications/$(APP)/socks
	mkdir -m 755 -p /usr/share/pixmaps
	mkdir -m 755 -p /usr/share/icons
	mkdir -m 755 -p /usr/share/icons/hicolor
	mkdir -m 755 -p /usr/share/icons/hicolor/scalable
	mkdir -m 755 -p /usr/share/icons/hicolor/scalable/apps
	mkdir -m 755 -p /usr/share/icons/hicolor/24x24
	mkdir -m 755 -p /usr/share/icons/hicolor/24x24/apps

	install -m 644 src/*.ui /usr/share/applications/$(APP)
	install -m 644 src/*.py /usr/share/applications/$(APP)
	install -m 644 src/*.qrc /usr/share/applications/$(APP)

	install -m 644 src/images/*.png /usr/share/applications/$(APP)/images
	install -m 644 src/images/*.ico /usr/share/applications/$(APP)/images
	install -m 644 src/pyelliptic/* /usr/share/applications/$(APP)/pyelliptic
	install -m 644 src/socks/* /usr/share/applications/$(APP)/socks
	install -m 755 debian/pybm /usr/bin

	install -m 644 desktop/$(APP).desktop /usr/share/applications/$(APP)/$(APP).desktop
	install -m 644 src/images/can-icon-24px.png /usr/share/icons/hicolor/24x24/apps/$(APP).png
	install -m 644 desktop/can-icon.svg /usr/share/icons/hicolor/scalable/apps/$(APP).svg
	install -m 644 desktop/can-icon.svg /usr/share/pixmaps/$(APP).svg

clean:
	rm -rf debian/$(APP)
	rm -f ../$(APP)_*.deb ../$(APP)_*.asc ../$(APP)_*.dsc ../$(APP)*.changes
	rm -f *.sh~ src/*.pyc src/socks/*.pyc src/pyelliptic/*.pyc
	rm -f *.deb \#* \.#* debian/*.log debian/*.substvars
	rm -f Makefile~
