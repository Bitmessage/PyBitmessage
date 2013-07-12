# $Header: $

EAPI=4

DESCRIPTION="Bitmessage is a P2P communications protocol used to send encrypted messages to another person or to many subscribers. It is decentralized and trustless, meaning that you need-not inherently trust any entities like root certificate authorities. It uses strong authentication which means that the sender of a message cannot be spoofed, and it aims to hide "non-content" data, like the sender and receiver of messages, from passive eavesdroppers like those running warrantless wiretapping programs."
HOMEPAGE="https://github.com/Bitmessage/PyBitmessage"
SRC_URI="${PN}/${P}.tar.gz"
LICENSE="MIT"
SLOT="0"
KEYWORDS="x86"
RDEPEND="dev-libs/popt"
DEPEND="${RDEPEND}"

src_configure() {
    econf --with-popt
}

src_install() {
    emake DESTDIR="${D}" install
    # Install README and (Debian) changelog
    dodoc README.md debian/changelog
}
