# $Header: $

EAPI=5

inherit git-2 python-r1

PYTHON_COMPAT=( python2_7 )
PYTHON_REQ_USE="sqlite"
REQUIRED_USE="${PYTHON_REQUIRED_USE}"
DESCRIPTION="Bitmessage is a P2P communications protocol used to send encrypted messages to another person or to many subscribers. It is decentralized and trustless, meaning that you need-not inherently trust any entities like root certificate authorities. It uses strong authentication which means that the sender of a message cannot be spoofed, and it aims to hide "non-content" data, like the sender and receiver of messages, from passive eavesdroppers like those running warrantless wiretapping programs."
HOMEPAGE="https://github.com/Bitmessage/PyBitmessage"
EGIT_REPO_URI="https://github.com/Bitmessage/PyBitmessage.git"
LICENSE="MIT"
SLOT="0"
KEYWORDS="x86"
DEPEND="dev-libs/popt
    ${PYTHON_DEPS}"
RDEPEND="${DEPEND}
    dev-libs/openssl
    dev-python/PyQt4[]"

src_configure() {
    econf --with-popt
}

src_compile() { :; }

src_install() {
    emake DESTDIR="${D}" PREFIX="/usr" install
    # Install README and (Debian) changelog
    dodoc README.md debian/changelog
}
